# -*- coding: utf-8 -*-
"""Shared machinery for the no-regression wave (card t_0c40c7b1).

Three things live here, and nothing else does:

  1. the RECORDED SET   -- 28 volumes x 721 clusters, read from the frozen recordings (I1/I2);
  2. the RULERS         -- R_fam (family + four grades) and R_cl (Cell Ontology relations),
                           frozen in PREREG_NOREGRESSION_20261022.md section 3.3;
  3. the REPLAY ENGINE  -- run query_marker over the recorded set under a declared overlay.

Everything is read-only. The engine never writes to the repository, never activates anything, and
never touches the network. A "change" is an overlay applied inside this process only.
"""
import copy
import csv
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict

REPO = "/home/ubuntu/EYEKB_REPO"
OSS = "/mnt/D/EyeKB/plans/oss_check_20261019"
REPORTS = os.path.join(OSS, "dl", "results")
LEDGER = os.path.join(OSS, "ledger_v1", "ledger_cluster_level.tsv")
FAMILY_CROSSWALK = os.path.join(OSS, "kb_family_crosswalk_v2.json")
CROSSWALK = os.path.join(REPO, "kb", "baselines", "_tissue_class_crosswalk_v1.json")
CL_MAP = os.path.join(REPO, "kb", "markers", "markers_cl_alignment_v2_unified.json")
CL_OBO = os.path.join(REPO, "kb", "ontology", "cl", "releases", "2026-06-08", "cl-base.obo")
ANTSEG = os.path.join(REPO, "kb", "markers", "markers_v10_antseg_increment.json")

# every switch the replay engine knows about; cleared before each arm so arms cannot leak into
# each other (the same hygiene the previous waves used)
SWITCHES = ("EYEKB_TISSUE_SCOPE", "EYEKB_ACT_V6", "EYEKB_ACT_K9", "EYEKB_ACT_ANTSEG",
            "EYEKB_KB_ANTIUNION", "EYEKB_STATE_GUARD", "EYEKB_S0_ENFORCE",
            "EYEKB_FALLBACK_WIDEN", "EYEKB_FALLBACK_WIDEN_DENY_TISSUES")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- 1. the recorded set
def load_set():
    """The recorded (volume, cluster) set with truth, genes, declared tissue and cell count."""
    truth = {}
    with open(LEDGER, encoding="utf-8", errors="replace") as f:
        cols = f.readline().rstrip("\r\n").split("\t")
        ix = {c: i for i, c in enumerate(cols)}
        for line in f:
            p = line.rstrip("\r\n").split("\t")
            if len(p) < len(cols):
                continue
            truth[(p[ix["ds"]], str(p[ix["cluster"]]))] = {
                "ref_cell_type": p[ix["ref_cell_type"]], "ref_family": p[ix["ref_family"]],
                "n_cells": int(float(p[ix["n_cells"]] or 0)),
                "recorded_pred_top1": p[ix["pred_top1"]], "recorded_pred_family": p[ix["pred_family"]],
                "recorded_grade": p[ix["grade"]], "recorded_verdict": p[ix["verdict"]],
                "recorded_has_cand": p[ix["has_cand"]] == "True",
                "recorded_fam_eq_raw": p[ix["fam_eq_raw"]] == "True"}
    out = []
    for vol in sorted(os.listdir(REPORTS)):
        p = os.path.join(REPORTS, vol, "annotation_evidence_report.json")
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        inp = d.get("inputs") or {}
        tissue = (inp.get("tissue") or "").strip().lower() or None
        species = (inp.get("species") or "").strip().lower() or None
        for c in d.get("clusters", []):
            g = c.get("top_genes") or []
            t = truth.get((vol, str(c.get("cluster"))))
            if g and t:
                out.append({"vol": vol, "cluster": str(c.get("cluster")),
                            "genes": [str(x) for x in g], "tissue": tissue, "species": species,
                            "ref_cell_type": t["ref_cell_type"], "ref_family": t["ref_family"],
                            "n_cells": t["n_cells"], "truth": t})
    return out


# ---------------------------------------------------------------- 2. the rulers
class Rulers(object):
    """R_fam and R_cl, built once and applied identically to every arm."""

    def __init__(self, calls=None):
        self.clmap = json.load(open(CL_MAP))["labels"]
        self.crosswalk = json.load(open(FAMILY_CROSSWALK))
        # (a) label -> family from the recording itself (measured)
        self.from_recording = {}
        for c in (calls or []):
            lbl = (c["truth"]["recorded_pred_top1"] or "").strip()
            if lbl:
                self.from_recording.setdefault(base_label(lbl).casefold(),
                                               c["truth"]["recorded_pred_family"])
        # (b) label -> family from the frozen crosswalk, only where exactly one family claims it
        claims = defaultdict(list)
        for fam, rec in (self.crosswalk.get("families") or {}).items():
            for e in (rec.get("entries") or []):
                claims[str(e).strip().casefold()].append(fam)
        self.from_crosswalk = {k: v[0] for k, v in claims.items() if len(v) == 1}
        # (c) Cell Ontology
        self.terms = self._load_obo()
        self.label_cl = {}
        for lbl, rec in self.clmap.items():
            cid = rec.get("cl_id")
            if cid:
                self.label_cl[base_label(lbl).casefold()] = cid
        # truth side: the CL term's own label, exact (casefolded) match only
        self.cllabel_cl = {}
        for cid, t in self.terms.items():
            nm = (t.get("name") or "").strip().casefold()
            if nm:
                self.cllabel_cl.setdefault(nm, cid)
        self._anc = {}

    # -- family ruler -------------------------------------------------------
    def fam_of(self, label):
        if not label:
            return None
        k = base_label(label).casefold()
        if k in self.from_recording:
            return self.from_recording[k]
        if k in self.from_crosswalk:
            return self.from_crosswalk[k]
        return "other"

    def ruler_selfcheck(self, calls):
        """Agreement between this ruler and the recording's own pred_family column."""
        agree = diff = 0
        examples = []
        for c in calls:
            lbl = (c["truth"]["recorded_pred_top1"] or "").strip()
            if not lbl:
                continue
            got = self.fam_of(lbl)
            rec = c["truth"]["recorded_pred_family"]
            if got == rec:
                agree += 1
            else:
                diff += 1
                if len(examples) < 10:
                    examples.append({"label": lbl, "ruler": got, "recorded": rec})
        return {"agree": agree, "differ": diff, "examples": examples}

    # -- ontology ruler -----------------------------------------------------
    def _load_obo(self):
        terms = {}
        cur = None
        with open(CL_OBO, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.rstrip("\n")
                if line == "[Term]":
                    cur = {}
                    continue
                if line.startswith("[") and line.endswith("]"):
                    cur = None
                    continue
                if cur is None or ":" not in line:
                    continue
                k, v = line.split(":", 1)
                v = v.strip()
                if k == "id":
                    cur["id"] = v
                    terms[v] = cur
                elif k == "name":
                    cur["name"] = v
                elif k == "is_obsolete":
                    cur["obsolete"] = (v == "true")
                elif k == "is_a":
                    cur.setdefault("is_a", []).append(v.split("!")[0].strip())
        return {k: v for k, v in terms.items() if not v.get("obsolete")}

    def anc(self, cid):
        if cid in self._anc:
            return self._anc[cid]
        seen = set()
        stack = [cid]
        while stack:
            x = stack.pop()
            t = self.terms.get(x)
            if not t:
                continue
            for p in (t.get("is_a") or []):
                if p not in seen:
                    seen.add(p)
                    stack.append(p)
        self._anc[cid] = seen
        return seen

    def cl_of_pred(self, label):
        if not label:
            return None
        return self.label_cl.get(base_label(label).casefold())

    def cl_of_truth(self, ref_label):
        if not ref_label:
            return None
        k = str(ref_label).strip().casefold()
        return self.cllabel_cl.get(k)

    def related(self, pred_label, ref_label):
        """Same cell under another name, or a coarser/finer ontology term."""
        a = self.cl_of_pred(pred_label)
        b = self.cl_of_truth(ref_label)
        if not a or not b:
            return False
        if a == b:
            return True
        return (a in self.anc(b)) or (b in self.anc(a))

    def cl_grade(self, pred_label, ref_label):
        a = self.cl_of_pred(pred_label) if pred_label else None
        b = self.cl_of_truth(ref_label)
        if not pred_label:
            return "abstain"
        if not a:
            return "unmappable_pred"
        if not b:
            return "unmappable_truth"
        if a == b:
            return "same_cl"
        if a in self.anc(b):
            return "kb_coarser"
        if b in self.anc(a):
            return "kb_finer"
        return "truly_inconsistent"

    # -- the four grades ----------------------------------------------------
    def grade(self, pred_label, ref_family, ref_cell_type):
        if not pred_label:
            return "mixed"
        if self.fam_of(pred_label) == ref_family:
            return "consistent"
        if self.related(pred_label, ref_cell_type):
            return "related"
        return "inconsistent"


def base_label(label):
    return str(label).split("::")[-1].strip()


# ---------------------------------------------------------------- 3. the replay engine
def clear_switches():
    for s in SWITCHES:
        os.environ.pop(s, None)


def fresh_core(overlay_env=None, inject=None):
    """Import eyekb_core with a clean switch state, optionally merging a library into `all`."""
    clear_switches()
    for k, v in (overlay_env or {}).items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    for m in [k for k in list(sys.modules) if k == "eyekb_core" or k.startswith("eyekb_core.")]:
        del sys.modules[m]
    if os.path.join(REPO, "mcp_server") not in sys.path:
        sys.path.insert(0, os.path.join(REPO, "mcp_server"))
    import eyekb_core as core
    if inject:
        orig = core._load_marker_dbs

        def patched(library="all", _o=orig, _inj=tuple(inject)):
            dbs = _o(library)
            if (library or "all").strip().lower() == "all":
                dbs = list(dbs)
                for lib in _inj:
                    dbs = dbs + list(_o(lib))
            return dbs
        core._load_marker_dbs = patched
    return core


def withdraw_rows(core, pairs):
    """Measurement-only withdrawal of exclusion rows, applied to the loaded crosswalk."""
    doc = core._tissue_crosswalk()
    for tissue, cls in pairs:
        rec = (doc.get("tissues") or {}).get(tissue)
        if not rec:
            continue
        rec["excluded_classes"] = [c for c in rec.get("excluded_classes") or []
                                   if c != cls]


def replay(calls, overlay_env=None, inject=None, withdraw=None, use_own_tissue=True,
           label=""):
    """Run the recorded set under one declared overlay. Returns {key: reading}."""
    core = fresh_core(overlay_env, inject)
    if withdraw:
        withdraw_rows(core, withdraw)
    out = {}
    for c in calls:
        kw = {"genes": list(c["genes"]), "library": "all"}
        if c["species"] in ("human", "mouse"):
            kw.update({"species": c["species"], "volume_species": c["species"],
                       "volume_id": "noregr_%s" % (label or "arm")})
        kw["tissue"] = (c["tissue"] if use_own_tissue else None)
        r = core.query_marker(**kw)
        rank = r.get("celltype_ranking") or []
        top = rank[0]["cell_type"] if rank else None
        ts = r.get("tissue_scope") or {}
        out[(c["vol"], c["cluster"])] = {
            "top": top,
            "n_shared": rank[0].get("n_shared") if rank else None,
            "shared_genes": (rank[0].get("shared_genes") if rank else None),
            "library": (str(rank[0].get("library") or "").split("/")[-1] if rank else None),
            "n_ranked": len(rank),
            "top3": [(x.get("cell_type"), x.get("n_shared"),
                      str(x.get("library") or "").split("/")[-1]) for x in rank[:3]],
            "scope_status": ts.get("status"),
            "scope_n_before": ts.get("n_before"),
            "scope_n_after": ts.get("n_after"),
            "excluded": [x.get("cell_type") for x in
                         (r.get("tissue_excluded_candidates") or [])]
            if isinstance(r.get("tissue_excluded_candidates"), list) else [],
        }
    return out


# ---------------------------------------------------------------- 4. grading + reporting
GRADES = ("consistent", "related", "inconsistent", "mixed")


def grade_arm(calls, arm, rulers):
    per = {}
    for c in calls:
        k = (c["vol"], c["cluster"])
        r = arm[k]
        top = r["top"]
        per[k] = {"grade": rulers.grade(top, c["ref_family"], c["ref_cell_type"]),
                  "cl": rulers.cl_grade(top, c["ref_cell_type"]),
                  "top": top, "n_shared": r.get("n_shared"), "n_ranked": r.get("n_ranked"),
                  "library": r.get("library"), "excluded": r.get("excluded") or [],
                  "scope_status": r.get("scope_status"),
                  "scope_n_before": r.get("scope_n_before"),
                  "scope_n_after": r.get("scope_n_after"),
                  "n_cells": c["n_cells"], "ref_family": c["ref_family"],
                  "ref_cell_type": c["ref_cell_type"], "vol": c["vol"],
                  "cluster": c["cluster"], "tissue": c["tissue"]}
    return per


def shares(rows):
    tot = sum(r["n_cells"] for r in rows) or 1
    c = Counter(r["grade"] for r in rows)
    cells = Counter()
    for r in rows:
        cells[r["grade"]] += r["n_cells"]
    return {"n_clusters": len(rows), "n_cells": tot,
            "share_pct": {g: round(100.0 * cells.get(g, 0) / tot, 3) for g in GRADES},
            "clusters": {g: c.get(g, 0) for g in GRADES},
            "cells": {g: cells.get(g, 0) for g in GRADES}}


def by_dataset(calls, graded):
    ds = defaultdict(list)
    for c in calls:
        ds[c["vol"]].append(graded[(c["vol"], c["cluster"])])
    return {v: shares(rows) for v, rows in ds.items()}


def transition_matrix(calls, before, after):
    m = Counter()
    moved_cells = Counter()
    for c in calls:
        k = (c["vol"], c["cluster"])
        b, a = before[k]["grade"], after[k]["grade"]
        m[(b, a)] += 1
        if b != a:
            moved_cells[(b, a)] += c["n_cells"]
    return {"clusters": {"%s->%s" % k: v for k, v in sorted(m.items())},
            "cells": {"%s->%s" % k: v for k, v in sorted(moved_cells.items())}}


def rank_deltas(calls, before, after):
    rows = []
    for c in calls:
        k = (c["vol"], c["cluster"])
        b, a = before[k], after[k]
        if (b["top"], b["n_shared"], b["n_ranked"]) != (a["top"], a["n_shared"], a["n_ranked"]):
            rows.append({"vol": c["vol"], "cluster": c["cluster"], "n_cells": c["n_cells"],
                         "tissue": c["tissue"], "ref_cell_type": c["ref_cell_type"],
                         "ref_family": c["ref_family"],
                         "before_top": b["top"], "before_n_shared": b["n_shared"],
                         "before_n_ranked": b["n_ranked"], "before_grade": b["grade"],
                         "after_top": a["top"], "after_n_shared": a["n_shared"],
                         "after_n_ranked": a["n_ranked"], "after_grade": a["grade"],
                         "before_cl": b["cl"], "after_cl": a["cl"]})
    rows.sort(key=lambda r: -r["n_cells"])
    return rows


# ---------------------------------------------------------------- 5. the acceptance rule
def judge(by_ds_before, by_ds_after, attributions, moved_cells):
    """THE MACHINE GATE (PREREG section 4, G6).

    A change may not be reported complete while any dataset's cell-weighted `consistent` share has
    fallen, unless the drop is attributed -- in the artefact -- to a named cluster, a named cause
    and a named row/panel.

    attributions: {"<dataset>": {"cluster": "...", "cause": "...", "row_or_panel": "..."}}
    Returns (verdict, detail). verdict in {PASS, PASS_ATTRIBUTED, FAIL}.
    """
    falls, ok = {}, {}
    for ds, b in sorted(by_ds_before.items()):
        a = by_ds_after.get(ds)
        if a is None:
            falls[ds] = {"reason": "dataset missing from the after arm"}
            continue
        d = round(a["share_pct"]["consistent"] - b["share_pct"]["consistent"], 3)
        if d < 0:
            att = attributions.get(ds) or {}
            missing = [f for f in ("cluster", "cause", "row_or_panel") if not att.get(f)]
            falls[ds] = {"delta_pp": d, "before_pct": b["share_pct"]["consistent"],
                         "after_pct": a["share_pct"]["consistent"],
                         "attribution": att, "unattributed": missing,
                         "cells_lost": {k: v for k, v in moved_cells.items()
                                        if k.endswith("->mixed") or k.endswith("->inconsistent")}}
        else:
            ok[ds] = d
    if not falls:
        return "PASS", {"datasets_checked": len(ok), "drops": {},
                        "worst_delta_pp": min(ok.values()) if ok else None}
    unattributed = {d: v for d, v in falls.items() if v.get("unattributed")}
    if unattributed:
        return "FAIL", {"datasets_checked": len(ok), "drops": falls,
                        "unattributed_drops": sorted(unattributed),
                        "rule": "any dataset's consistent share may not fall without a named "
                                "cluster + named cause + named row/panel recorded in the artefact"}
    return "PASS_ATTRIBUTED", {"datasets_checked": len(ok), "drops": falls}


def save_json(path, doc):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, default=str)
    return path
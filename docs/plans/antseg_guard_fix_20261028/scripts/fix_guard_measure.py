#!/usr/bin/env python
"""Increment-admission guard (incumbent margin): pre-fix vs post-fix readings.

Preregistration: PREREG_ANTSEG_GUARD_FIX_20261028.md (criteria B1/B2/A1/A2 implemented here).

    python fix_guard_measure.py --capture   # take the pre-fix reading (run this on the pre-fix bytes)
    python fix_guard_measure.py --verify    # three states x two semantics, then B1/B2/A1/A2

How the merged states are built: a library is appended to the `all` route **inside a child process
only**, by wrapping `_load_marker_dbs`. No environment switch and no product code path is added, so
the only difference between a shipped and a merged state is the library's own entries.

Why child processes: which bytes answer a query is a property of the process, not of the import
order inside one run.

Why two semantics: the fix changes one predicate (`_production_lib_basenames`). The pre-fix meaning
of that predicate — "every registered library is an incumbent" — is reproduced in the child by
replacing it, which lets the pre/post comparison run on one copy of the code. The pre-fix reading is
also captured against the real pre-fix bytes, and the two are required to agree byte for byte
before any A-reading is trusted ("self-proof 0" below).

Corpus: the 25 volumes / 764 clusters used by the independent-validation wave, with tissue and
species taken from the same volume metadata the main table uses (`prep/`, `JUDGE_SCORE_*.json`).
"""
import argparse
import csv
import gzip
import hashlib
import json
import os
import subprocess
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
CORPUS_DIR = os.environ.get("CORPUS_DIR", "/home/ubuntu/eyekb_indep_validation_20261022")
CORE = os.environ.get("CORE_DIR", "/home/ubuntu/EYEKB_REPO/mcp_server")
PY = os.environ.get("PY", "/home/ubuntu/.conda/envs/scrnaseq/bin/python")
LENSIRIS_VOLS = ("CX13_lens", "CX13_iris")

CHILD = r'''
import hashlib, json, os, sys
sys.path.insert(0, os.environ["CORE_DIR"])
import eyekb_core as core

MERGE = os.environ.get("MERGE", "0")   # 0 = shipped route; 1 = library merged, no scope guard;
                                       # 2 = library merged with its own declared-scope guard
SEM = os.environ.get("SEM", "new")     # new = post-fix meaning; old = pre-fix meaning (emulated)

# --- pre-fix vs post-fix meaning: the only difference is who counts as an incumbent
if SEM == "old":
    core._production_lib_basenames = lambda: frozenset(p.name for p in core.MARKER_LIBS.values())

if MERGE in ("1", "2"):
    _orig = core._load_marker_dbs
    def _patched(library="all"):
        dbs = _orig(library)
        if (library or "all").strip().lower() == "all":
            name = "lensiris_v11"
            p = core.MARKER_LIBS[name]
            if p.is_file() and not any(n == name for n, _, _ in dbs):
                with open(p, encoding="utf-8") as f:
                    dbs = dbs + [(name, str(p), json.load(f))]
        return dbs
    core._load_marker_dbs = _patched

EMUL = {}
if MERGE == "2":
    _real_guard = core._antseg_guard_split
    with open(core.MARKER_LIBS["lensiris_v11"], encoding="utf-8") as f:
        _V11_SCOPE = tuple(str(x).strip().casefold() for x in json.load(f)["scope_tissues"])

    def _guard_twice(rank_full, owner_map, tissue, scope_tissues, is_state_entry):
        """Apply the same admission policy to the merged library as to the antseg increment."""
        kept, dem, st = _real_guard(rank_full, owner_map, tissue, scope_tissues, is_state_entry)
        old = core.ANTSEG_LIB_BASENAME
        core.ANTSEG_LIB_BASENAME = "markers_v11_lensiris_increment.json"
        try:
            kept2, dem2, st2 = _real_guard(kept, owner_map, tissue, _V11_SCOPE, is_state_entry)
        finally:
            core.ANTSEG_LIB_BASENAME = old
        _key = "pass2_%s" % (st2.get("status") if st2 else "not_applied")
        EMUL[_key] = EMUL.get(_key, 0) + 1
        return kept2, dem + dem2, st
    core._antseg_guard_split = _guard_twice

jobs = json.load(sys.stdin)
out = {"corpus": {}, "libs": {},
       "loaded_default": [n for n, _, _ in core._load_marker_dbs("all")]}


def md5(r):
    return hashlib.md5(json.dumps(r, ensure_ascii=False, default=str).encode()).hexdigest()


for k, v in jobs["corpus"].items():
    try:
        r = core.query_marker(genes=v["genes"], library="all", species=v["species"],
                              volume_species=v["species"], volume_id="guard_fix_probe",
                              tissue=v["tissue"])
        rk = r.get("celltype_ranking") or []
        out["corpus"][k] = {
            "top": rk[0]["cell_type"] if rk else None,
            "n_shared": (rk[0].get("n_shared") if rk else None),
            "rank": [[x.get("cell_type"), x.get("n_shared")] for x in rk],
            "md5": md5(r),
            "guard": (r.get("antseg_guard") or {}).get("status"),
            "guard_best_inc": (r.get("antseg_guard") or {}).get("best_incumbent_n_shared"),
            "demoted": [(d.get("cell_type"), d.get("n_shared"), d.get("reason"),
                         d.get("best_incumbent_n_shared"))
                        for d in (r.get("antseg_guard_demoted") or [])],
        }
    except Exception as e:
        out["corpus"][k] = {"err": "%s: %s" % (type(e).__name__, e)}

out["emul_status"] = EMUL
out["errs"] = sum(1 for v in out["corpus"].values() if "err" in v)
out["err_samples"] = [v["err"] for v in list(out["corpus"].values()) if "err" in v][:3]

# criterion B2: each library named explicitly (the guard does not run on that path; this proves the
# fix did not spill into explicit routes)
for lib, jobs_ in jobs["libs"].items():
    rec = {}
    for k, gen in jobs_.items():
        try:
            r = core.query_marker(genes=gen, library=lib, volume_id="guard_fix_probe",
                                  tissue="retina", species="human")
            rec[k] = md5(r)
        except Exception as e:
            rec[k] = "ERR:%s: %s" % (type(e).__name__, e)
    out["libs"][lib] = rec

print(json.dumps(out))
'''


def load_volmeta():
    """volume -> (tissue, species), from the same files the main table scores against."""
    m = {}
    for f in ("JUDGE_SCORE_judge_prod_think.json", "JUDGE_SCORE_judge_fair_think.json"):
        p = os.path.join(CORPUS_DIR, f)
        if not os.path.exists(p):
            continue
        for v in json.load(open(p))["volumes"]:
            m.setdefault(v["volume"], {"tissue": v.get("tissue"), "species": v.get("species")})
    return m


VOLMETA = load_volmeta()


def build_jobs():
    corpus = {}
    prep = os.path.join(CORPUS_DIR, "prep")
    for vol in sorted(os.listdir(prep)):
        pdir = os.path.join(prep, vol)
        if not os.path.isdir(pdir):
            continue
        # tissue/species come from the main-table volume metadata, never from prep_meta (those two
        # fields are empty there and tissue="" makes the tissue-scope filter demote every
        # increment candidate, which silently re-labels the whole run).
        vm = VOLMETA.get(vol, {})
        tissue = vm.get("tissue") or ""
        species = vm.get("species") or "human"
        by = {}
        with open(os.path.join(pdir, "cluster_markers.csv"), newline="") as f:
            for row in csv.DictReader(f):
                by.setdefault(str(row["cluster"]), []).append((int(row["rank"]), row["gene"]))
        for cl, lst in by.items():
            corpus["%s|%s" % (vol, cl)] = {"genes": [g for _, g in sorted(lst)][:30],
                                           "tissue": tissue, "species": species}
    probe = {k: v["genes"] for k, v in corpus.items()
             if k.split("|")[0] in ("CX13_lens", "CX13_iris", "CX13_central_cornea")}
    probe = dict(sorted(probe.items())[:9])
    libs = {lib: dict(probe) for lib in
            ("all", "retina", "membrane", "retina_interneuron", "retina_v6", "face_v6",
             "k9_ocs", "retina_v7", "retina_dev", "antseg_v10", "lensiris_v11",
             "holefill_v12", "onfibro_v13", "subtype_v14", "cl56_v15")}
    return {"corpus": corpus, "libs": libs}


def run(jobs, merge, sem):
    env = dict(os.environ, CORE_DIR=CORE, MERGE=str(merge), SEM=sem)
    p = subprocess.run([PY, "-c", CHILD], input=json.dumps(jobs),
                       capture_output=True, text=True, env=env)
    if p.returncode != 0:
        raise SystemExit("child failed (merge=%s sem=%s):\n%s" % (merge, sem, p.stderr[-3000:]))
    return json.loads(p.stdout)


def correctness(res):
    """Per-cluster top-1 verdict under the same scoring rule the main table uses.

    The guard's failure mode is a wrongly demoted candidate, so both directions matter: an answer
    that was right and became wrong is a loss, the reverse is a gain.
    """
    sys.path.insert(0, CORPUS_DIR)
    import score_corpus as S
    import score_judge as SJ
    cw = S.load_cw()
    verdict = {}
    for vol in sorted({k.split("|", 1)[0] for k in res["corpus"]}):
        pdir = os.path.join(CORPUS_DIR, "prep", vol)
        hp, tp = os.path.join(pdir, "processed.h5ad"), os.path.join(pdir, "truth.tsv")
        if not (os.path.exists(hp) and os.path.exists(tp)):
            continue
        truth, _ = S.cluster_truth_from_h5ad(hp, S.read_cell_truth(tp))
        tctx = S.TISSUE_CTX.get(vol)
        for key, r in res["corpus"].items():
            v, cl = key.split("|", 1)
            if v != vol:
                continue
            cnt = truth.get(cl)
            if not cnt:
                continue
            author = max(cnt.items(), key=lambda x: x[1])[0]
            top = r.get("top")
            if not top:
                verdict[key] = ("none", author, None)
                continue
            fam = SJ.fold_answer(top, tctx)
            s = S.score_one_label(author, fam, [fam] if fam else [], cw, tctx)
            verdict[key] = ("skip" if not s["usable"] else ("ok" if s["ok1"] else "wrong"),
                            author, top)
    return verdict


def summarise(tag, base, arm):
    v_base, v_arm = correctness(base), correctness(arm)
    print("\n== %s · criterion A (lens + iris) ==" % tag)
    per = {}
    for vol in LENSIRIS_VOLS:
        keys = [k for k in v_base if k.startswith(vol + "|")]
        o = sum(1 for k in keys if v_base[k][0] == "ok")
        n = sum(1 for k in keys if v_arm[k][0] == "ok")
        gain = [k for k in keys if v_base[k][0] != "ok" and v_arm[k][0] == "ok"]
        loss = [k for k in keys if v_base[k][0] == "ok" and v_arm[k][0] != "ok"]
        per[vol] = dict(clusters=len(keys), off_ok=o, on_ok=n, gain=len(gain), loss=len(loss),
                        gain_keys=gain, loss_keys=loss)
        print("  %-12s %2d clusters | base right %2d (%5.1f%%) | arm right %2d (%5.1f%%) | "
              "gained %d | lost %d"
              % (vol, len(keys), o, 100.0 * o / len(keys), n, 100.0 * n / len(keys),
                 len(gain), len(loss)))
    net = sum(x["on_ok"] - x["off_ok"] for x in per.values())
    print("  net %+d clusters (criterion A2 asks for >= +4)" % net)

    others = [k for k in v_base if not k.startswith(tuple(v + "|" for v in LENSIRIS_VOLS))]
    lost = [k for k in others if v_base[k][0] == "ok" and v_arm[k][0] != "ok"]
    gained = [k for k in others if v_base[k][0] != "ok" and v_arm[k][0] == "ok"]
    byvol = {}
    for k in lost:
        byvol[k.split("|")[0]] = byvol.get(k.split("|")[0], 0) + 1
    print("\n== %s · criterion A1 (answers outside the merged library's tissues) ==" % tag)
    print("  %d scoreable clusters: lost %d, gained %d" % (len(others), len(lost), len(gained)))
    if lost:
        print("  losses by volume:", byvol)
        for k in lost[:10]:
            print("   lost %-34s author=%-28s base=%r arm=%r"
                  % (k, v_base[k][1], v_base[k][2], v_arm[k][2]))
    for k in gained[:6]:
        print("   gained %-34s author=%-28s arm=%r" % (k, v_base[k][1], v_arm[k][2]))

    oth2 = [k for k in base["corpus"]
            if not k.startswith(tuple(v + "|" for v in LENSIRIS_VOLS))]
    ch_top = [k for k in oth2 if base["corpus"][k].get("top") != arm["corpus"][k].get("top")]
    ch_rank = [k for k in oth2 if base["corpus"][k].get("rank") != arm["corpus"][k].get("rank")]
    print("  %d clusters (ranking layer): top-1 moved %d, ranking sequence moved %d"
          % (len(oth2), len(ch_top), len(ch_rank)))
    cornea_keys = [k for k in lost
                   if k.split("|")[0] in ("CX13_central_cornea", "PRE_GSE199013")]
    print("  criterion A1 requires cornea losses = 0; measured %d" % len(cornea_keys))
    print("\n== %s · criterion A3 (where the gained answers landed) ==" % tag)
    for vol in LENSIRIS_VOLS:
        for k in per[vol]["gain_keys"]:
            print("   %-26s author=%-26s arm top-1=%r" % (k, v_arm[k][1], v_arm[k][2]))
    return dict(net=net, per=per, others=len(others), lost=len(lost), gained=len(gained),
                lost_by_vol=byvol, ch_top=len(ch_top), ch_rank=len(ch_rank),
                cornea_lost=len(cornea_keys), lost_keys=lost, gained_keys=gained,
                ch_top_keys=ch_top)


def capture_path():
    """Where the pre-fix capture lives: next to the script, or in ../out/ (the readings folder)."""
    for p in (os.path.join(OUT, "GUARD_FIX_CAPTURE.json"),
              os.path.join(OUT, "GUARD_FIX_CAPTURE.json.gz"),
              os.path.join(OUT, "..", "out", "GUARD_FIX_CAPTURE.json"),
              os.path.join(OUT, "..", "out", "GUARD_FIX_CAPTURE.json.gz")):
        if os.path.exists(p):
            return os.path.abspath(p)
    raise SystemExit("no pre-fix capture found; run --capture on the pre-fix bytes first "
                     "(it writes GUARD_FIX_CAPTURE.json next to this script)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", action="store_true")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    if not (a.capture or a.verify):
        raise SystemExit("need --capture or --verify")

    jobs = build_jobs()
    print("corpus %d clusters / %d libraries x %d probes"
          % (len(jobs["corpus"]), len(jobs["libs"]), len(next(iter(jobs["libs"].values())))))

    if a.capture:
        off = run(jobs, 0, "old")
        on = run(jobs, 1, "old")
        json.dump({"OFF": off, "ON": on},
                  open(os.path.join(OUT, "GUARD_FIX_CAPTURE.json"), "w"),
                  indent=1, ensure_ascii=False)
        print("wrote GUARD_FIX_CAPTURE.json (shipped + merged, pre-fix bytes)")
        return

    arms = {}
    for merge in (0, 1, 2):
        for sem in ("old", "new"):
            arms[(merge, sem)] = run(jobs, merge, sem)
            _a = arms[(merge, sem)]
            print("  arm merge=%d sem=%-3s done | errors %d | %s"
                  % (merge, sem, _a.get("errs", -1), _a.get("err_samples") or ""))
            if _a.get("errs"):
                raise SystemExit("arm merge=%d sem=%s has %d failing clusters -- readings unusable"
                                 % (merge, sem, _a["errs"], _a["err_samples"]))
    print("shipped route loads:", arms[(0, "new")]["loaded_default"])

    ship_old, ship_new = arms[(0, "old")], arms[(0, "new")]
    _cp = capture_path()
    cap = json.load(gzip.open(_cp, "rt", encoding="utf-8") if _cp.endswith(".gz")
                    else open(_cp, encoding="utf-8"))

    # --- self-proof: the emulated pre-fix meaning must equal the real pre-fix bytes
    print("\n== self-proof 0: emulated pre-fix meaning == real pre-fix bytes ==")
    k0 = sorted(set(cap["OFF"]["corpus"]) & set(ship_old["corpus"]))
    s0 = sum(1 for k in k0 if cap["OFF"]["corpus"][k].get("md5") == ship_old["corpus"][k].get("md5"))
    k1 = sorted(set(cap["ON"]["corpus"]) & set(arms[(1, "old")]["corpus"]))
    s1 = sum(1 for k in k1
             if cap["ON"]["corpus"][k].get("md5") == arms[(1, "old")]["corpus"][k].get("md5"))
    print("  shipped route %d clusters, md5 identical %d" % (len(k0), s0))
    print("  merged state  %d clusters, md5 identical %d" % (len(k1), s1))
    emul_ok = (s0 == len(k0) == s1 == len(k1))

    print("\n== criterion B1 (shipped route: real pre-fix bytes vs post-fix bytes) ==")
    keys = k0
    same_md5 = [k for k in keys
                if cap["OFF"]["corpus"][k].get("md5") == ship_new["corpus"][k].get("md5")]
    same_rank = [k for k in keys
                 if cap["OFF"]["corpus"][k].get("rank") == ship_new["corpus"][k].get("rank")]
    print("  %d clusters: full-response md5 identical %d, ranking sequence identical %d"
          % (len(keys), len(same_md5), len(same_rank)))
    for k in [k for k in keys if k not in set(same_md5)][:8]:
        print("   md5 differs:", k, cap["OFF"]["corpus"][k].get("rank", [])[:3], "->",
              ship_new["corpus"][k].get("rank", [])[:3])

    print("\n== criterion B2 (15 libraries named explicitly: pre-fix vs post-fix) ==")
    b2 = {}
    for lib in sorted(cap["OFF"]["libs"]):
        c, n = cap["OFF"]["libs"][lib], ship_new["libs"].get(lib, {})
        same = sum(1 for k in c if c[k] == n.get(k))
        b2[lib] = [same, len(c)]
        print("  %-20s %d/%d %s" % (lib, same, len(c), "OK" if same == len(c) else "DIFF"))

    # --- A group: for each merged state, (i) the fix's own effect, (ii) the pre-registered reading
    print("\n######## M1a = library merged without its own scope guard: the fix's own effect ########")
    M1_fix = summarise("M1 pre-fix -> post-fix", arms[(1, "old")], arms[(1, "new")])
    print("\n######## M1b = merged (post-fix) vs shipped route: the pre-registered A reading ########")
    M1_abs = summarise("M1 post-fix vs shipped", ship_new, arms[(1, "new")])
    print("\n######## M2a = merged with its declared scope honoured: the fix's own effect ########")
    M2_fix = summarise("M2 pre-fix -> post-fix", arms[(2, "old")], arms[(2, "new")])
    print("\n######## M2b = merged with scope (post-fix) vs shipped route: pre-registered A ########")
    M2_abs = summarise("M2 post-fix vs shipped", ship_new, arms[(2, "new")])

    verdict = dict(
        emulation=emul_ok,
        B1=len(same_md5) == len(keys) and len(same_rank) == len(keys),
        B2=all(v[0] == v[1] for v in b2.values()),
        A1=M1_abs["cornea_lost"] == 0,
        A2=M1_abs["net"] >= 4,
    )
    print("\n== criteria (pre-registered wording) ==")
    for k, v in verdict.items():
        print("  %-10s %s" % (k, "PASS" if v else "FAIL"))

    rec = dict(loaded_default=arms[(0, "new")]["loaded_default"], verdict=verdict,
               B1=dict(clusters=len(keys), same_md5=len(same_md5), same_rank=len(same_rank)),
               B2=b2, M1_fix=M1_fix, M1_abs=M1_abs, M2_fix=M2_fix, M2_abs=M2_abs)
    outdir = os.path.join(OUT, "..", "out")
    outdir = outdir if os.path.isdir(outdir) else OUT
    json.dump(rec, open(os.path.join(outdir, "GUARD_FIX_VERIFY.json"), "w"),
              indent=1, ensure_ascii=False)
    print("wrote GUARD_FIX_VERIFY.json")


if __name__ == "__main__":
    main()
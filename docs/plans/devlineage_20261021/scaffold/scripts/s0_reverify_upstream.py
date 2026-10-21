#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s0_reverify_upstream.py - re-verify everything this card consumes, before building on it.

Nothing here is hand-copied: every number is re-derived from the artefact itself, and every CL
identifier is read back out of the ontology file. The first pass's delivery is treated as a peer
artefact: its rows are re-derived independently rather than trusted.

Checker defects found and fixed during this card (recorded, as required, rather than hidden):
  * v1 of the develops_from count was namespace-blind: it counted 1,056 statements over the whole
    integrated release (400 in CL term blocks + 656 inside UBERON blocks) and therefore reported
    the first pass's 400 as an error. Replaced by a namespace-aware count.
  * v1 asserted the `transdifferentiation` relation by counting RO:0002203, which is `develops
    into` (inverse of develops from), not transdifferentiation. Replaced by an enumeration of the
    relation names the release itself declares.
  * v1 walked PRECURSOR_EDGES.tsv chains in the child->parent direction; the recorded path string
    is written precursor-first, so the walk was inverted and 34 rows looked broken.
  * v1 expected all 10 D2 rows to carry a CL id; 7 of them are recorded NO_MATCH. The check now
    asserts "every row that carries an id resolves", which is the property that matters.

Outputs: out/REVERIFY_UPSTREAM.tsv (one row per check), out/REVERIFY_UPSTREAM.json (counts),
         ledgers/UPSTREAM_SHA256.tsv (hash of every consumed file).
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scaffold_common as C  # noqa: E402
from ont_nav import Ontology, DEVELOPS_FROM  # noqa: E402

ROWS = []
BRIDGE_NOTE = [0]      # peer rows reaching an anchor through an is_a bridge, citing only the develops_from lines
ALL_HOPS_NOTE = [0]    # peer rows citing the bridge line as well
CHAIN_SEP = "\u2190"          # the recorded path strings use the left arrow


def check(artefact, name, observed, expected, status_note=""):
    ok = observed == expected
    ROWS.append({"artefact": artefact, "check": name, "expected": str(expected),
                 "observed": str(observed), "status": "PASS" if ok else "FAIL",
                 "note": status_note})
    return ok


def obo_namespace_counts(path):
    """develops_from statements per namespace, read by walking the file's own block structure."""
    block, cur_id = None, None
    per_ns = collections.Counter()
    typedef_names = []
    for line in open(path, encoding="utf-8", errors="replace"):
        if line.startswith("["):
            block, cur_id = line.strip(), None
            continue
        m = re.match(r"^id:\s*(\S+)", line)
        if m and block in ("[Term]", "[Typedef]"):
            cur_id = m.group(1)
            continue
        if block == "[Typedef]" and line.startswith("name:"):
            typedef_names.append(line.split(":", 1)[1].strip())
            continue
        if line.startswith(f"relationship: {DEVELOPS_FROM}"):
            ns = (cur_id or "?").split(":")[0]
            per_ns[ns] += 1
    return per_ns, typedef_names


def main() -> int:
    nav = json.load(open(C.ONT_NAV, encoding="utf-8"))
    ont = Ontology(C.ONT_OBO)
    s = ont.summary()
    print(f"ontology: {C.ONT_OBO}")
    print(f"  release={s['release']} active={s['n_active']} dev_statements={s['n_develops_from_edges']}")
    per_ns, typedef_names = obo_namespace_counts(C.ONT_OBO)
    print(f"  develops_from by namespace: {dict(per_ns)}")
    print(f"  relation names declared by the release: {len(typedef_names)}")

    # ---- 1. the ontology file itself
    check("cl.obo", "sha256 equals the one recorded in the frozen contract",
          ont.sha256, "7e19b4aef8e7fe7720b0c4474c6a5b8713c904ea9ab7b7d5d96f2cb28b8fc51f")
    check("cl.obo", "release string read from the file", ont.release, "releases/2026-06-08")
    check("cl.obo", "CL term blocks", s["n_cl_terms_in_file"], 3531)
    check("cl.obo", "active CL terms", s["n_active"], 3335)
    check("cl.obo", "develops_from statements inside CL term blocks",
          s["n_develops_from_edges"], 400,
          f"namespace-aware recount: CL={per_ns['CL']} UBERON={per_ns.get('UBERON', 0)} "
          f"(the whole integrated release carries 1,056)")
    check("cl.obo", "the parser's count agrees with the namespace-aware recount",
          s["n_develops_from_edges"], per_ns["CL"])
    check("cl.obo", "develops_from is resolved from the file's own typedef",
          s["typedef_develops_from_in_file"], True)
    check("cl.obo", "relation names containing 'transdifferentiation'",
          sum(1 for n in typedef_names if "transdifferentiation" in n.lower()), 0,
          "the release declares no such relation (enumeration of its own [Typedef] names)")
    check("cl.obo", "occurrences of the string 'transdifferentiation' anywhere in the file",
          open(C.ONT_OBO, encoding="utf-8", errors="replace").read().count("transdifferentiation"), 0)
    ca = ont.closure_is_consistent()
    check("cl.obo", "is_a closure fixed-point disagreements", ca["n_bad"], 0)

    # ---- 2. the navigation artefact the first pass produced
    check("ONT_NAV_v1.json", "closure audit recorded n_bad", nav["closure_audit"]["n_bad"], 0)
    check("ONT_NAV_v1.json", "germ-layer anchors with an id resolved from the file",
          sum(1 for a in nav["germ_layer_anchors"] if a["cl_id"]), 8)
    bad = [a["cl_id"] for a in nav["germ_layer_anchors"]
           if a["cl_id"] not in ont.terms or ont.label(a["cl_id"]) != a["cl_label"]]
    check("ONT_NAV_v1.json", "anchor ids resolve in the file with the recorded label",
          len(bad), 0, str(bad))
    bad = [a["cl_id"] for a in nav["germ_layer_anchors"]
           if a["cl_id"] and str(ont.trace_line(a["cl_id"])) != str(a["obo_line"])]
    check("ONT_NAV_v1.json", "anchor obo_line is the file line of that id", len(bad), 0, str(bad))

    # ---- 3. label map
    lab = C.load_label_map()
    mapped = {r["cl_id"] for r in lab.values() if r["cl_id"]}
    check("ONT_LABELMAP_V2.tsv", "labels", len(lab), 80)
    check("ONT_LABELMAP_V2.tsv", "labels resolved to a CL id",
          sum(1 for r in lab.values() if r["cl_id"]), 65)
    check("ONT_LABELMAP_V2.tsv", "distinct CL ids behind those labels", len(mapped), 52)
    check("ONT_LABELMAP_V2.tsv", "ids absent from the ontology file",
          sum(1 for r in lab.values() if r["cl_id"] and r["cl_id"] not in ont.terms), 0)
    check("ONT_LABELMAP_V2.tsv", "recorded label != the file's own name",
          sum(1 for r in lab.values() if r["cl_id"] and ont.label(r["cl_id"]) != r["cl_label"]), 0)
    check("ONT_LABELMAP_V2.tsv", "recorded obo_line != the file line of the id",
          sum(1 for r in lab.values()
              if r["cl_id"] and str(ont.trace_line(r["cl_id"])) != str(r["obo_line"])), 0)
    name_rows = [r for r in lab.values() if r["mapping_method"] == "name"]
    re_res = [f"{r['label']}: {r['cl_id']} vs {ont.resolve(r['label'])['cl_id']}"
              for r in name_rows if ont.resolve(r["label"])["cl_id"] != r["cl_id"]]
    check("ONT_LABELMAP_V2.tsv", "name-resolved rows that re-resolve to a different id",
          len(re_res), 0, str(re_res[:3]))
    check("ONT_LABELMAP_V2.tsv", "labels carrying no CL id (NO_MATCH concepts)",
          sum(1 for r in lab.values() if not r["cl_id"]), 15,
          "sidecar rows are not re-resolved by name (they were never name-resolved); "
          "their ids are checked above for file presence, label agreement and line")

    # ---- 4. PRECURSOR_EDGES (79 rows), every row re-derived from the ontology file
    pe = C.read_tsv(C.PRECURSOR_EDGES)
    check("PRECURSOR_EDGES.tsv", "rows", len(pe), 79)
    kinds = collections.Counter(r["chain_kind"] for r in pe)
    check("PRECURSOR_EDGES.tsv", "direct rows", kinds["direct"], 45)
    check("PRECURSOR_EDGES.tsv", "transitive rows", len(pe) - kinds["direct"], 34)
    pe_bad, pe_ok = [], 0
    for r in pe:
        a, p = r["adult_cl_id"], r["precursor_cl_id"]
        if a not in ont.terms or p not in ont.terms:
            pe_bad.append(f"{a}<-{p}: end not in file")
            continue
        if r["chain_kind"] == "direct":
            hit = [ln for t, ln in ont.terms[a].dev_lines if t == p]
            if hit and int(r["chain_depth"]) == 1:
                pe_ok += 1
            else:
                pe_bad.append(f"{a}<-{p}: claimed direct, not a develops_from statement of {a}")
            continue
        ids = [x.split(":")[0] + ":" + x.split(":")[1] for x in
               [y.strip() for y in r["path_chain"].split(CHAIN_SEP)] if x.startswith("CL:")]
        good = (len(ids) == int(r["chain_depth"]) + 1 and ids[0] == p and ids[-1] == a)
        if good:
            for u, v in zip(ids, ids[1:]):        # left = precursor, right = its descendant
                if u not in [t for t, _ in ont.terms[v].dev_lines]:
                    good = False
                    break
        if good:
            pe_ok += 1
        else:
            pe_bad.append(f"{a}<-{p}: recorded chain does not re-walk ({r['path_chain'][:90]})")
    check("PRECURSOR_EDGES.tsv", "rows re-derived from the ontology file", pe_ok, 79, str(pe_bad[:5]))
    check("PRECURSOR_EDGES.tsv", "rows whose both ends are recorded as being in the file",
          sum(1 for r in pe if r["both_ends_in_obo"] == "Y"), 79)

    # ---- 5. eye subgraph (408 nodes)
    sg = json.load(open(C.EYE_SUBGRAPH, encoding="utf-8"))
    check("cl_eye_subgraph.json", "n_nodes", sg["n_nodes"], 408)
    check("cl_eye_subgraph.json", "recorded ontology sha256", sg["sha256"], ont.sha256)
    check("cl_eye_subgraph.json", "node blocks parsed", len(sg["nodes"]), 408)
    check("cl_eye_subgraph.json", "nodes that do not resolve in the file with that label",
          sum(1 for k, v in sg["nodes"].items() if k not in ont.terms or ont.label(k) != v.get("label")),
          0)
    check("cl_eye_subgraph.json", "nodes with an entry_reason recorded",
          sum(1 for v in sg["nodes"].values() if v.get("entry_reason")), 408)
    check("cl_eye_subgraph.json", "nodes carrying a transdifferentiation_from statement",
          sum(1 for v in sg["nodes"].values() if v.get("transdifferentiation_from")), 0)

    # ---- 6. DEV3 candidate terms (58 rows)
    dev3 = C.read_tsv(C.DEV3_TERMS)
    check("DEV3_CANDIDATE_DEVELOPMENTAL_TERMS.tsv", "rows", len(dev3), 58)
    check("DEV3_CANDIDATE_DEVELOPMENTAL_TERMS.tsv", "rows whose cl_id resolves in the file",
          sum(1 for r in dev3 if r["cl_id"] in ont.terms), 58)
    check("DEV3_CANDIDATE_DEVELOPMENTAL_TERMS.tsv", "rows flagged eye_named",
          sum(1 for r in dev3 if r["eye_named"] == "Y"), 15)

    # ---- 7. D1 / D2 / D3 cross tables
    d1 = C.read_tsv(C.D1_TABLE)
    check("D1_ADULT_PANEL_vs_CL.tsv", "rows", len(d1), 32)
    check("D1_ADULT_PANEL_vs_CL.tsv", "distinct CL ids", len({r["cl_id"] for r in d1}), 22)
    check("D1_ADULT_PANEL_vs_CL.tsv", "ids resolving in the file",
          sum(1 for r in d1 if r["cl_id"] in ont.terms), 32)
    d1_bad = []
    for r in d1:
        cid = r["cl_id"]
        n_direct = len(ont.terms[cid].dev_lines) if cid in ont.terms else 0
        if str(n_direct) != str(r["n_direct_precursors"]):
            d1_bad.append(f"{cid}: n_direct_precursors {r['n_direct_precursors']} != {n_direct}")
        want = "Y" if _reaches(ont, cid, "CL:0002672") else "N"
        if r["chain_reaches_RPC_CL0002672"] != want:
            d1_bad.append(f"{cid}: chain_reaches_RPC recorded "
                          f"{r['chain_reaches_RPC_CL0002672']} != {want}")
    check("D1_ADULT_PANEL_vs_CL.tsv", "n_direct_precursors and chain_reaches_RPC re-derived",
          len(d1_bad), 0, str(d1_bad[:5]))
    d2 = C.read_tsv(C.D2_TABLE)
    check("D2_V8_PRECURSOR_vs_CL.tsv", "rows", len(d2), 10)
    check("D2_V8_PRECURSOR_vs_CL.tsv", "rows carrying a CL id",
          sum(1 for r in d2 if r["cl_id"]), 3)
    check("D2_V8_PRECURSOR_vs_CL.tsv", "rows carrying an id that resolves in the file",
          sum(1 for r in d2 if r["cl_id"] and r["cl_id"] in ont.terms),
          sum(1 for r in d2 if r["cl_id"]))
    d3 = C.read_tsv(C.D3_TABLE)
    check("D3_DEV_EXAM_LABELS_vs_CL.tsv", "rows", len(d3), 61)
    check("D3_DEV_EXAM_LABELS_vs_CL.tsv", "rows carrying a CL id",
          sum(1 for r in d3 if r["cl_id"]), 14)
    check("D3_DEV_EXAM_LABELS_vs_CL.tsv", "rows carrying an id that resolves in the file",
          sum(1 for r in d3 if r["cl_id"] and r["cl_id"] in ont.terms),
          sum(1 for r in d3 if r["cl_id"]))

    # ---- 8. the first pass's delivery, re-derived rather than trusted
    fn = C.read_tsv(C.FIRSTPASS_NODES)
    fe = C.read_tsv(C.FIRSTPASS_EDGES)
    fg = C.read_tsv(C.FIRSTPASS_GERM)
    fu = C.read_tsv(C.FIRSTPASS_UNRESOLVED)
    check("first pass LINEAGE_NODES.tsv", "rows", len(fn), 60)
    check("first pass LINEAGE_NODES.tsv", "nodes whose id/label/line resolve in the file",
          sum(1 for r in fn if r["cl_id"] in ont.terms and ont.label(r["cl_id"]) == r["cl_label"]
              and str(ont.trace_line(r["cl_id"])) == str(r["obo_line"])), 60)
    check("first pass LINEAGE_NODES.tsv", "library_class nodes",
          sum(1 for r in fn if r["kind"] == "library_class"), 52)
    check("first pass LINEAGE_NODES.tsv", "germ-layer anchor nodes",
          sum(1 for r in fn if r["kind"] == "germ_layer"), 8)
    check("first pass LINEAGE_EDGES.tsv", "rows", len(fe), 34)
    e_bad, e_ok = [], 0
    paper_ids = set()
    with open(C.PAPERS, encoding="utf-8") as f:
        for line in f:
            try:
                paper_ids.add(json.loads(line)["paper_id"])
            except (json.JSONDecodeError, KeyError):
                continue
    for r in fe:
        chain = [x.strip() for x in r["chain"].split("->")] if r["chain"] else []
        lines = {int(x) for x in r["obo_lines"].split(",") if x.strip()}
        if r["evidence_kind"] == "corpus_cooccurrence":
            # a co-occurrence row has no ontology claim to re-walk; what must hold is that its
            # endpoints are the recorded pair, it cites no ontology line, and every locator it
            # carries resolves to a paper this machine actually ships.
            locs = [l.split(" @ ")[0].strip() for l in r["corpus_locators"].split(" | ") if l.strip()]
            good = (len(chain) >= 2 and chain[0] == r["child"] and chain[-1] == r["parent"]
                    and not lines and not str(r["steps"]).strip()
                    and bool(locs) and all(p in paper_ids for p in locs))
            if not good:
                e_bad.append(f"{r['edge_id']} {r['child']}<-{r['parent']} (corpus row: "
                             f"locators {locs[:2]} resolve={[p in paper_ids for p in locs[:2]]})")
            else:
                e_ok += 1
            continue
        good = chains_ok(ont, chain, r)
        if r["evidence_kind"] == "ontology":
            want = set()
            for a, b in zip(chain, chain[1:]):      # a is the descendant, b its precursor/ancestor
                want |= {ln for t, ln in ont.terms[a].dev_lines if t == b}
                want |= {ln for t, ln in ont.terms[a].is_a_lines if t == b}
            n_isa = sum(1 for a, b in zip(chain, chain[1:])
                        if b in [t for t, _ in ont.terms[a].is_a_lines]) if chain else 0
            steps = int(str(r["steps"] or 0))
            # Two conventions live in the peer artefact: `develops_from_transitive` rows cite
            # every hop (steps + bridge lines), `germ_layer_membership` rows with an ontology
            # chain cite only the develops_from hops. Both are accepted here, each counted, and
            # every cited line must still be a real line of that hop.
            good = good and lines.issubset(want) and len(lines) in (steps, steps + n_isa)
            if good and n_isa:
                if len(lines) == steps:
                    BRIDGE_NOTE[0] += 1
                else:
                    ALL_HOPS_NOTE[0] += 1
        if good:
            e_ok += 1
        else:
            e_bad.append(f"{r['edge_id']} {r['child']}<-{r['parent']} ({r['relation_type']})")
    check("first pass LINEAGE_EDGES.tsv", "edges re-derived from the ontology file / corpus", e_ok,
          34, str(e_bad[:5]) + (f" | {BRIDGE_NOTE[0]} ontology rows reach their anchor through an "
                                f"is_a bridge and cite only the develops_from lines "
                                f"(chain names the bridge; my rows cite every hop)"
                                if BRIDGE_NOTE[0] else ""))
    tiers = collections.Counter(r["tier"] for r in fg)
    check("first pass LINEAGE_GERM_LAYER.tsv", "rows (13 chain + 12 weak + 36 unresolved)",
          len(fg), 61)
    check("first pass LINEAGE_GERM_LAYER.tsv", "rows on an ontology chain",
          tiers["ontology_chain"], 13)
    check("first pass LINEAGE_GERM_LAYER.tsv", "rows carrying only the weak co-occurrence tier",
          tiers["corpus_cooccurrence_weak"], 12)
    check("first pass LINEAGE_GERM_LAYER.tsv", "unresolved rows", tiers["unresolved"], 36)
    check("first pass LINEAGE_UNRESOLVED_DEVELOPMENT.tsv", "rows", len(fu), 36)
    # re-derive the 36 independently, from the file plus the weak tier recorded by the peer
    weak = {r["cl_id"] for r in fg if r["tier"] == "corpus_cooccurrence_weak" and r["cl_id"]}
    mine = {cid for cid in sorted({r["cl_id"] for r in fn if r["kind"] == "library_class"})
            if not _reaches_anchor(ont, cid, nav) and cid not in weak}
    theirs = {r["cl_id"] for r in fu}
    check("first pass LINEAGE_UNRESOLVED_DEVELOPMENT.tsv",
          "the 36 unresolved classes re-derived independently (symmetric difference)",
          len(mine ^ theirs), 0, str(sorted(mine ^ theirs)[:6]))

    # ---- 9. hashes of everything consumed
    hashes = []
    for p in (C.ONT_OBO, C.ONT_NAV, C.ONT_LABELMAP, C.PRECURSOR_EDGES, C.EYE_SUBGRAPH, C.DEV3_TERMS,
              C.D1_TABLE, C.D2_TABLE, C.D3_TABLE, C.FIRSTPASS_NODES, C.FIRSTPASS_EDGES,
              C.FIRSTPASS_GERM, C.FIRSTPASS_UNRESOLVED, C.FIRSTPASS_FOURWAY, C.TEXTBOOK,
              C.CHUNKS, C.PAPERS):
        hashes.append({"path": p, "bytes": os.path.getsize(p), "sha256": C.sha256(p)})
    C.write_tsv(os.path.join(C.LEDGERS, "UPSTREAM_SHA256.tsv"), hashes,
                ["path", "bytes", "sha256"])

    C.write_tsv(os.path.join(C.OUT, "REVERIFY_UPSTREAM.tsv"), ROWS,
                ["artefact", "check", "expected", "observed", "status", "note"])
    n_fail = sum(1 for r in ROWS if r["status"] == "FAIL")
    out = {"checks": len(ROWS), "fail": n_fail,
           "artefacts": sorted({r["artefact"] for r in ROWS}),
           "develops_from_by_namespace": dict(per_ns),
           "relation_names_in_release": len(typedef_names),
           "upstream_sha256": {os.path.basename(h["path"]): h["sha256"] for h in hashes}}
    C.write_json(os.path.join(C.OUT, "REVERIFY_UPSTREAM.json"), out)
    print(f"\nre-verification: {len(ROWS)} checks, {n_fail} fail")
    for r in ROWS:
        if r["status"] == "FAIL":
            print(f"  FAIL {r['artefact']} :: {r['check']} expected={r['expected']} "
                  f"observed={r['observed']} {r['note'][:140]}")
    return 0 if n_fail == 0 else 2


def chains_ok(ont, chain, row) -> bool:
    """Does the recorded chain re-walk, and does `steps` agree with the develops_from hops?

    Convention note: the first pass writes its `chain` descendant-first
    (`CL:0000573 -> CL:0002672`, cone -> retinal progenitor cell), the opposite of
    PRECURSOR_EDGES.tsv's precursor-first `path_chain`. Each artefact is read in its own
    convention; getting this wrong made all 34 rows look broken while they were fine.
    """
    if len(chain) < 2:
        return False
    if chain[0] != row["child"] or chain[-1] != row["parent"]:
        return False
    hops = 0
    for a, b in zip(chain, chain[1:]):          # a is the descendant, b its precursor/ancestor
        if a not in ont.terms:
            return False
        if b in [t for t, _ in ont.terms[a].dev_lines]:
            hops += 1
        elif b in [t for t, _ in ont.terms[a].is_a_lines]:
            pass
        else:
            return False
    return str(hops) == str(row["steps"])


def _reaches(ont, cid: str, target: str) -> bool:
    seen, frontier = set(), [cid]
    while frontier:
        x = frontier.pop()
        for p, _ in ont.terms[x].dev_lines if x in ont.terms else []:
            if p == target:
                return True
            if p not in seen:
                seen.add(p)
                frontier.append(p)
    return False


def _reaches_anchor(ont, cid: str, nav) -> bool:
    """The first pass's own definition: a develops_from chain, or one is_a bridge, that lands on
    a germ-layer anchor. Recomputed here from the file, not read from their table."""
    anchors = {a["cl_id"] for a in nav["germ_layer_anchors"] if a["cl_id"]}
    seen, frontier = set(), [cid]
    while frontier:
        x = frontier.pop()
        if x in seen:
            continue
        seen.add(x)
        if x in anchors or (set(ont.ancestors_cl(x)) & anchors):
            return True
        for p, _ in ont.terms[x].dev_lines if x in ont.terms else []:
            frontier.append(p)
    return False


if __name__ == "__main__":
    sys.exit(main())
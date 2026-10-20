#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wiring + boundary tests for the increment eligibility guard (SOL items C and D).

C — candidate-processing order invariants:
  C1  an increment candidate and a production candidate share one CL id; the increment fails the
      guard; the production candidate must still be answerable afterwards
  C2  same shape, increment fails for being out of declared tissue scope
  C3  a state_program entry with the highest n_shared must NOT raise the admission bar
  C4  call-order assertion on the live query path: the guard runs before the CL-key merge

D — declaration, ownership and boundary behaviour:
  D1  release file declares scope_tissues; the loaded db exposes it
  D2  class ownership is complete and single-valued (basename per class)
  D3  in-scope tissue admits the increment class
  D4  out-of-scope tissue demotes it
  D5  absent tissue demotes it (fail closed through the scope check)
  D6  missing/empty declaration demotes everything (fail closed, reported)
  D7  tissue string normalisation: case, spaces, partial forms
  D8  admission arithmetic: 0/1/2 incumbents vs 1..4 shared genes
  D9  a production single-gene candidate is not filtered by this rule
  D10 explicit library="antseg_v10" is never touched by the guard

Run:  python3 tests/antseg_guard_wiring_check.py <repo-root>
Exit code 0 = all assertions passed.
"""
import json
import os
import sys
from pathlib import Path

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/EYEKB_REPO"
sys.path.insert(0, os.path.join(ROOT, "mcp_server"))
for k in [k for k in os.environ if k.startswith("EYEKB_")]:
    del os.environ[k]
os.environ.pop("EYEKB_ACT_ANTSEG", None)
os.environ["EYEKB_ACT_ANTSEG"] = "1"          # increment loaded; guard is not optional any more

import eyekb_core as core  # noqa: E402

ANTSEG = core.ANTSEG_LIB_BASENAME
RETINA = "markers_v4.1_clean.json"
INC_CLASS = "lens epithelial cell"
PROD_CLASS = "Corneal Endothelium"

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(f"{'PASS' if cond else 'FAIL'}  {name}" + (f"  |  {detail}" if detail else ""))


def R(ct, ns, lib):
    return {"cell_type": ct, "n_shared": ns, "shared_genes": ["G%d" % i for i in range(ns)],
            "library": f"/kb/markers/{lib}"}


def owner_of(**pairs):
    return {k: f"/kb/markers/{v}" for k, v in pairs.items()}


NO_STATE = lambda e: False  # noqa: E731


# ----------------------------------------------------------------- C1/C2: CL collision
def c1_c2():
    # One CL id covers both the increment class and a production class ("lens-epithelial").
    labelmap = {INC_CLASS: {"cl_id": "CL:0000001", "cl_label": "epithelial cell"},
                PROD_CLASS: {"cl_id": "CL:0000001", "cl_label": "epithelial cell"}}
    ranks = [R(INC_CLASS, 3, ANTSEG), R(PROD_CLASS, 2, RETINA), R("Rod", 5, RETINA)]
    owner = owner_of(**{INC_CLASS: ANTSEG, PROD_CLASS: RETINA, "Rod": RETINA})

    # --- shipped order: guard first, then CL merge
    kept, dem, st = core._antseg_guard_split(ranks, owner, "lens", ("lens",), NO_STATE)
    kept2, _cldem, _att = core._cl_dedup_split(kept, labelmap)
    names = [r["cell_type"] for r in kept2]
    check("C1 guard-then-merge: failing increment does not delete the production class",
          PROD_CLASS in names and INC_CLASS not in names,
          f"final ranking={names}; demoted={[d['cell_type'] for d in dem]}")
    check("C1 the increment was demoted for the margin, not for scope",
          dem and dem[0]["reason"] == "below_increment_eligibility",
          f"reason={dem[0]['reason'] if dem else None} n_shared={dem[0]['n_shared'] if dem else None} "
          f"needed={dem[0].get('needs_n_shared') if dem else None}")

    # --- the order that was rejected: CL merge first would have deleted the production class
    merged, _d, _a = core._cl_dedup_split(ranks, labelmap)
    merged_names = [r["cell_type"] for r in merged]
    after_guard, _d2, _s2 = core._antseg_guard_split(merged, owner, "lens", ("lens",), NO_STATE)
    names_old = [r["cell_type"] for r in after_guard]
    check("C2 counter-example reproduces the unrecoverable loss under the OLD order",
          PROD_CLASS not in merged_names and PROD_CLASS not in names_old,
          f"merge-first kept={merged_names} -> after guard={names_old}")

    # --- C2b: out-of-scope increment, same CL, production must survive
    kept_o, dem_o, st_o = core._antseg_guard_split(ranks, owner, "retina", ("lens",), NO_STATE)
    kept_o2, _c, _a = core._cl_dedup_split(kept_o, labelmap)
    names_o = [r["cell_type"] for r in kept_o2]
    check("C2 out-of-scope increment also leaves the production class answerable",
          PROD_CLASS in names_o and INC_CLASS not in names_o,
          f"status={st_o['status']} final={names_o}")


# ----------------------------------------------------------------- C3: state must not raise the bar
def c3():
    km = core._x4b_state_map()
    if km is None:
        check("C3 concept-kind map available", False, "state sidecar not loaded")
        return
    state_entry = R("Proliferating", 9, "markers_membrane_v1.json")
    is_state = lambda e: core._x4b_state_kind(e, km) == "state_program"  # noqa: E731
    check("C3 fixture: the state entry really is concept_kind=state_program", is_state(state_entry),
          str(core._x4b_state_kind(state_entry, km)))

    ranks = [state_entry, R(INC_CLASS, 4, ANTSEG), R("Fibroblast", 2, "markers_membrane_v1.json")]
    owner = owner_of(**{INC_CLASS: ANTSEG, "Proliferating": "markers_membrane_v1.json",
                        "Fibroblast": "markers_membrane_v1.json"})
    kept, dem, st = core._antseg_guard_split(ranks, owner, "lens", ("lens",), is_state)
    kept_names = [r["cell_type"] for r in kept]
    check("C3 state entry does not raise the bar (4 shared genes admitted against incumbent 2)",
          INC_CLASS in kept_names and st["best_incumbent_n_shared"] == 2,
          f"best_incumbent={st['best_incumbent_n_shared']} kept={kept_names}")

    kept_ns, _d, st_ns = core._antseg_guard_split(ranks, owner, "lens", ("lens",), NO_STATE)
    check("C3 counter-example: counting the state entry WOULD have raised the bar",
          INC_CLASS not in [r["cell_type"] for r in kept_ns],
          f"best_incumbent={st_ns['best_incumbent_n_shared']}")


# ----------------------------------------------------------------- C4: live call order
def c4():
    order = []
    real_guard = core._antseg_guard_split
    real_cl = core._cl_dedup_split

    def spy_guard(*a, **k):
        order.append("guard")
        return real_guard(*a, **k)

    def spy_cl(*a, **k):
        order.append("cl_merge")
        return real_cl(*a, **k)

    core._antseg_guard_split = spy_guard
    core._cl_dedup_split = spy_cl
    os.environ["EYEKB_CL_KEY"] = "1"          # force the merge to be active so order is observable
    try:
        core.query_marker(genes=["PAX6", "CRYBB2", "CRYAB", "BFSP2", "CDH2", "PROX1", "MALAT1"],
                          library="all", species="human", tissue="lens")
    finally:
        core._antseg_guard_split = real_guard
        core._cl_dedup_split = real_cl
        os.environ.pop("EYEKB_CL_KEY", None)
    check("C4 live path calls the guard before the CL merge",
          order[:2] == ["guard", "cl_merge"], f"call order={order}")


# ----------------------------------------------------------------- D: declaration / ownership
def d():
    f = Path(ROOT) / "kb" / "markers" / "markers_v10_antseg_increment.json"
    d0 = json.loads(f.read_text(encoding="utf-8"))
    check("D1 release file declares scope_tissues", isinstance(d0.get("scope_tissues"), list)
          and len(d0["scope_tissues"]) > 0, f"{d0.get('scope_tissues')}")

    dbs = core._load_marker_dbs("all")
    loaded = [(Path(p).name, db) for _n, p, db in dbs if Path(p).name == ANTSEG]
    check("D1 the loaded db exposes the declaration", bool(loaded)
          and isinstance(loaded[0][1].get("scope_tissues"), list),
          f"loaded={[n for n, _ in loaded]}")

    # ownership: the guard classifies a candidate by the basename of its owning file, so what has
    # to hold is (a) no increment class shares a name with a production class, (b) every class on
    # the merged surface has exactly one owner, (c) production name clashes are disambiguated by an
    # explicit "library::" alias instead of silently overwriting one another.
    inc_classes = set(loaded[0][1].get("markers") or {}) if loaded else set()
    merged = core.query_marker(library="all", species="human")["cell_types"]
    owner = {}
    for n, p, db in dbs:
        for ct in (db.get("markers") or {}):
            owner.setdefault(ct, []).append(Path(p).name)
    prod_names = {ct for ct, libs in owner.items() if ANTSEG not in libs}
    collide = sorted(inc_classes & prod_names)
    check("D2a no increment class name collides with a production class name", not collide,
          f"increment={len(inc_classes)} collisions={collide}")

    # The merged surface renames a later library's clashing class to "shortlib::class" and leaves
    # the first library with the bare name, so every surface key must resolve to exactly one file
    # under that rule (this is the ownership the guard's basename test relies on).
    by_short = {n: (Path(p).name, db) for n, p, db in dbs}

    def resolve(ct):
        if "::" in ct:
            pre, name = ct.split("::", 1)
            hit = by_short.get(pre)
            return (hit[0], name) if hit and name in (hit[1].get("markers") or {}) else (None, None)
        for _n, p, db in dbs:
            if ct in (db.get("markers") or {}):
                return (Path(p).name, ct)          # first library wins the bare name
        return (None, None)

    unresolved = [ct for ct in merged if resolve(ct)[0] is None]
    check("D2b every class on the merged surface resolves to exactly one owning file",
          not unresolved, f"surface={len(merged)} unresolved={unresolved[:5]} "
                          f"(count={len(unresolved)})")

    conflicts = core.query_marker(genes=["RHO"], library="all",
                                  species="human")["provenance"].get("conflicts") or []
    aliased = [c for ct in merged if "::" in ct for c in conflicts if c.get("alias") == ct]
    check("D2c every production name clash is disambiguated by an explicit alias",
          len(aliased) == len([ct for ct in merged if "::" in ct])
          and all(c.get("kept") and c.get("alias") for c in conflicts),
          f"conflict_rows={len(conflicts)} aliased_keys={len([ct for ct in merged if '::' in ct])}")

    # D3-D5 through the live route
    lens_genes = ["PAX6", "CRYBB2", "CRYAB", "BFSP2", "CDH2", "PROX1", "MALAT1"]
    r = core.query_marker(genes=lens_genes, library="all", species="human", tissue="lens")
    inc_tops = [c["cell_type"] for c in (r.get("celltype_ranking") or [])]
    check("D3 in-scope tissue admits the increment class",
          r["antseg_guard"]["status"] == "in_scope"
          and any("lens" in c.lower() for c in inc_tops),
          f"status={r['antseg_guard']['status']} top3={inc_tops[:3]}")

    r = core.query_marker(genes=lens_genes, library="all", species="human", tissue="retina")
    lens_visible = any("lens" in c["cell_type"].lower()
                       for c in (r.get("celltype_ranking") or []))
    st = (r.get("antseg_guard") or {}).get("status")
    check("D4 out-of-scope tissue leaves no increment candidate answerable",
          not lens_visible and st in {"out_of_scope", None},
          f"status={st} (None = removed by an earlier filter) lens_visible={lens_visible}")

    r = core.query_marker(genes=lens_genes, library="all", species="human")
    lens_visible = any("lens" in c["cell_type"].lower()
                       for c in (r.get("celltype_ranking") or []))
    st = (r.get("antseg_guard") or {}).get("status")
    check("D5 absent tissue leaves no increment candidate answerable (fail closed)",
          not lens_visible and st in {"out_of_scope", None}
          and (r.get("antseg_guard") or {}).get("tissue") is None,
          f"status={st} lens_visible={lens_visible}")

    real_scope = core._antseg_scope_tissues
    core._antseg_scope_tissues = lambda dbs: ()
    try:
        r = core.query_marker(genes=lens_genes, library="all", species="human", tissue="lens")
        st = r["antseg_guard"]["status"]
        demoted = r.get("antseg_guard_demoted") or []
        no_inc = not any("lens" in c["cell_type"].lower()
                         for c in (r.get("celltype_ranking") or []))
        check("D6 missing declaration fails closed and is reported",
              st == "no_declared_scope" and no_inc and all(
                  d["reason"] == "no_declared_scope" for d in demoted),
              f"status={st} demoted={len(demoted)}")
    finally:
        core._antseg_scope_tissues = real_scope

    for label, tis in [("case", "LENS"), ("spaces", "Ciliary Body"),
                       ("underscore", "trabecular_meshwork"), ("partial", "ocular surface")]:
        rr = core.query_marker(genes=lens_genes, library="all", species="human", tissue=tis)
        st = (rr.get("antseg_guard") or {}).get("status")
        check(f"D7 normalisation [{label}] tissue={tis!r} normalises to an in-scope string",
              st == "in_scope", f"status={st}")

    # D8 admission arithmetic, synthetic
    def admit(best_inc, inc_ns):
        ranks = [R(INC_CLASS, inc_ns, ANTSEG)] + [R(f"Prod{i}", best_inc, RETINA)
                                                  for i in range(1 if best_inc else 0)]
        owner = owner_of(**{INC_CLASS: ANTSEG, **{f"Prod{i}": RETINA for i in
                                                 range(1 if best_inc else 0)}})
        kept, _dm, _st = core._antseg_guard_split(ranks, owner, "lens", ("lens",), NO_STATE)
        return INC_CLASS in [x["cell_type"] for x in kept]

    grid = [((0, 1), False), ((0, 2), True),
            ((1, 2), False), ((1, 3), True),
            ((2, 3), False), ((2, 4), True)]
    ok = all(admit(b, i) is exp for (b, i), exp in grid)
    check("D8 admission arithmetic (incumbent 0/1/2 vs shared 1..4)", ok,
          " ".join(f"best={b},inc={i}:{'admit' if admit(b, i) else 'reject'}" for (b, i), _ in grid))

    # D9 production single-gene candidate untouched
    ranks = [R(INC_CLASS, 3, ANTSEG), R("Fibroblast", 1, "markers_membrane_v1.json")]
    owner = owner_of(**{INC_CLASS: ANTSEG, "Fibroblast": "markers_membrane_v1.json"})
    kept, _dm, _st = core._antseg_guard_split(ranks, owner, "lens", ("lens",), NO_STATE)
    check("D9 production single-gene candidate is not filtered",
          "Fibroblast" in [x["cell_type"] for x in kept],
          f"kept={[x['cell_type'] for x in kept]}")

    # D10 explicit route untouched
    r_exp = core.query_marker(genes=lens_genes, library="antseg_v10", species="human")
    tops = [c["cell_type"] for c in (r_exp.get("celltype_ranking") or [])]
    check("D10 explicit library=antseg_v10 is never guarded",
          "antseg_guard" not in r_exp and any("lens" in t.lower() for t in tops),
          f"top3={tops[:3]}")


if __name__ == "__main__":
    print(f"module under test: {core.__file__}\n")
    c1_c2()
    c3()
    c4()
    d()
    bad = [n for n, ok, _ in results if not ok]
    print(f"\n=== {len(results) - len(bad)}/{len(results)} assertions passed ===")
    if bad:
        print("FAILED: " + "; ".join(bad))
    sys.exit(0 if not bad else 1)

# Increment-admission guard: the incumbent margin counted sibling increments' entries

**Status:** fixed and measured; the shipped default route is byte-identical before and after.
**Date:** 2026-10-28
**Scope:** `mcp_server/eyekb_core.py` (one predicate + its definition), `tests/antseg_guard_wiring_check.py`
(five new assertions), one registry row re-taken (`docs/W3_PIPELINE_REGISTRY.tsv` L1-11M).
**Preregistration:** `docs/plans/antseg_guard_fix_20261028/PREREG_ANTSEG_GUARD_FIX_20261028.md`
(written before any post-fix reading was taken; the criteria were not amended afterwards).

---

## 1. What was wrong

The anterior-segment increment (`antseg_v10`) is admitted onto the default route through a
three-condition policy: at least two shared genes, a declared tissue scope, and a margin of two
genes over the best incumbent. The third condition needs to know what "the incumbent" is, and it
answered that question with

```
best_inc = max(n_shared for candidates whose owning file is NOT the antseg file)
```

which is not the same thing. Any **other** increment library loaded on the same route also
satisfied "not the antseg file", so its entries were counted as incumbents and raised the bar for
antseg's own candidates.

Consequence, measured: with `lensiris_v11` loaded alongside the default route (this is what
merging that library into `all` looks like), the bar on the cornea moved from 2 to 3 shared genes
and antseg candidates that were legitimately eligible at `n_shared = 2` were demoted. The 2026-10-28
merge experiment recorded the signature — five top-1 answers changed, twenty ranking sequences
changed — and attributed it to the new library. It was not the new library: it was this predicate.

## 2. What changed

Incumbents are now the libraries the **shipped** `all` route loads. That set is derived from the
existing activation whitelists rather than restated, so activating a future increment edits one
whitelist and the incumbent set follows:

```python
def _production_lib_basenames():
    names = ["retina", "membrane", "retina_interneuron"]
    for wl in (V6_DEFAULT_LIBS, K9_DEFAULT_LIBS, ANTSEG_DEFAULT_LIBS,
               ONFIBRO_DEFAULT_LIBS, SUBTYPE_DEFAULT_LIBS, CL56_DEFAULT_LIBS):
        names.extend(wl)
    return frozenset(Path(MARKER_LIBS[n]).name for n in names if n in MARKER_LIBS)
```

Nothing else moved: no threshold changed (`ANTSEG_MIN_SHARED` stays 2, `ANTSEG_MARGIN` stays 2), no
whitelist changed, `_antseg_is_increment` (a different question — "is this candidate owned by the
antseg file", used by the scope demotion) is untouched, and no new library was activated.

## 3. Pre-registered criteria and readings

| Criterion | Requirement | Reading | Verdict |
|---|---|---|---|
| B1 shipped-route identity | 764 corpus clusters byte-identical (full response md5 **and** ranking sequence) | 764/764 and 764/764 | **PASS** |
| B2 explicit-route identity | 15 libraries × 9 gene probes unchanged | 135/135 | **PASS** |
| B3 unit regression | the guard's own assertions, including a sibling-increment case | 30/30 (5 new) | **PASS** |
| A1 defect gone | cornea top-1 losses with two increments loaded = 0 | 1 before → **0** after | **PASS** |
| A2 merge net gain | lens + iris cluster net ≥ +4 with the library merged | **+5** (lens 6→10, iris 5→6) | **PASS** |
| self-proof | the in-script "before" semantics reproduce the real pre-fix code | 764/764 + 764/764 | **PASS** |

The self-proof matters: the before/after comparison is run inside one process by swapping only the
predicate, so the claim "this is what the old code did" is not taken on trust — it is checked
against a capture taken by the pre-fix bytes.

## 4. What the fix does to the merge picture (and what it does not)

Two merged states were measured, because a library can be merged with or without honouring the
scope it declares in its own file.

**M1 — `lensiris_v11` merged with no scope guard of its own.** Isolated effect of the fix:

- lens 11 → 10, iris 7 → 6 correct (two correct answers from the merged library are displaced by
  antseg candidates that the old predicate had wrongly barred), ciliary epithelium +1;
- five top-1 answers and twenty ranking sequences move — **the exact signature the merge experiment
  recorded on 2026-10-28**, which is what identifies the two readings as the same event.

Against the shipped route the merged state scores +5 (lens 6→10, iris 5→6) but loses 8 answers in
retina volumes, because that library's entries are unguarded outside lens/iris. This state is not a
proposal; it is the state the defect was found in.

**M2 — merged with its own declared scope honoured** (the same policy applied to it as to antseg):

- against the shipped route: lens 6 → 8, iris unchanged, **zero top-1 changes and zero ranking
  changes across all 716 clusters outside lens/iris** — the merge cannot hurt any other volume;
- net +2, which is below the pre-registered bar of +4 that governs merging a library into `all`.

So the honest summary is: the fix removes the interference, and a properly scoped merge of that
library would be harmless — but it is still worth only +2 clusters, short of the bar. The library
stays registered default-off; the fix does not change that decision.

## 5. Reach of the fix

The shipped route can never hit the defect: `library="all"` loads only libraries that are themselves
incumbents, so the old and the new predicate return the same incumbent value there. That is why B1
is byte-identical rather than merely close, and why the defect could survive unnoticed since
2026-10-20.

The delivery tree under `/mnt/D` (runtime entry) does not carry this fix, deliberately: its
`MARKER_LIBS` has no staging increment beyond `antseg_v10`, and the guard only runs on the `all`
route, so the defect is structurally unreachable there. Copying the predicate into that tree would
create a second, divergent copy for no behavioural change; it will travel with the next whole-tree
sync.

## 6. Reproduce

```
python docs/plans/antseg_guard_fix_20261028/scripts/fix_guard_measure.py --capture   # pre-fix bytes
#   (apply the predicate change)
python docs/plans/antseg_guard_fix_20261028/scripts/fix_guard_measure.py --verify    # 3 states x 2 semantics
python tests/antseg_guard_wiring_check.py .                                          # 30/30
```

Readings: `docs/plans/antseg_guard_fix_20261028/out/GUARD_FIX_VERIFY.json`.
Gate chain at this commit: `tests/run_gates.sh` — G6–G13 pass; G3 (41-query retrieval anchor) and
G4 (pipeline byte anchors, 2/3) are red **before and after** this change, unchanged by it.
# PRE-REGISTRATION ANNEX A — AMENDMENTS, SECOND SET (written 2026-10-22 11:0x CST)

Thresholds in `PREREG_SUBDIVISION_READINESS_20261022.md §2` stand unchanged. What follows fixes two more
**operations**, each because the first operationalisation was measured to be non-discriminating. Both were written
after a first readiness pass existed; that pass is preserved at `out/firstpass/` and its defect is stated here.

## A7-b The state reference must discriminate (supersedes A7's set-membership test)

**What was observed first**: A7's reference as a *set* (3,880 disease-arm + 3,730 treatment-arm + 2,671 cell-cycle-arm
genes, union 5,396) saturated: `state_fraction_union` came out at **1.0000 for 26 of the 26 strongest candidate
pairs**. A set that contains every discriminating gene cannot answer "does this distinction depend on a state
programme".

**Amendment**: the state test becomes a **ratio**, not a membership. One pass over the discovery corpus records, for
every gene symbol, the number of chunks mentioning it and how many of those chunks are state-context chunks
(cell-cycle arm ∪ disease arm ∪ treatment arm — counted as a **union**, not a sum, so no ratio can exceed 1). A gene
is `state_dependent` iff at least **R = 0.75** of its mentioning chunks are state-context and it is mentioned at
least 3 times. `state_fraction` = |discriminating genes that are state_dependent| / |discriminating genes|; the
pre-registered `T-STATE` (< 0.50) is applied to this fraction unchanged.

Calibration evidence (`out/O_state_ratio.json`, ratios): MKI67 1.00, TOP2A 1.00, CCNB1 0.78 ‖ RBPMS 0.48, RHO 0.52,
BEST1 0.57, RPE65 0.59, GFAP 0.63, GRM6 0.35, OPN1SW 0.27, POU4F1 0.24. The 0.75 cutoff separates the cycling
programme from identity genes; the cutoffs 0.50 / 0.90 are written to the artefact so the sensitivity is readable.

## A11-b A progenitor parent's descendants are a lineage relation, not a subtype question

**What was observed first**: `progenitor cell` (CL:0011026, adult axis by its library declarations) returns
`monocyte`, `hematopoietic stem cell`, `myoblast`, `neuroblast` among its direct closure members — real ontology
edges, but the relation is lineage, not subtype. The ruling puts developmental/lineage reasoning in block B and
forbids it standing in for cell-type evidence.

**Amendment**: a parent whose own preferred name or CL synonym matches the pre-registered progenitor vocabulary
(`progenitor`, `precursor`, `blast`, `stem cell`, `transit amplifying`) is treated as a **developmental-axis
parent** (scope class `developmental_axis`), like the fetal-stage parents already are. Its children are listed with
their own tally and are never read as adult subdivisions.

## A12 Two tier-order fixes (no threshold involved)

**What was observed first**: 136 pairs came out `spectrum_only` purely because they had **no** positive genes at all —
that is thin evidence, not a continuum. And 26 pairs were being labelled `state_programme_only` by the saturated
test of A7 above.

**Amendment**:
1. a pair with fewer than 2 positive genes is `needs_deeper_panel_genes` (T2) **before** any continuum reading;
2. `spectrum_only` (T3) applies only when the child has ≥ 2 positive genes and **none** of them discriminate it from
   **any** sibling, i.e. it can never separate — a continuum, not a thin panel;
3. `no_target_context_occurrence` is reported split into `never_mentioned` (the name occurs in no chunk at all) and
   `outside_declared_context` (it occurs, but not under the declared species/tissue context), so the two are not
   conflated;
4. the nearest sibling is the sibling with the largest positive-set overlap; ties break on the smaller `is_a` graph
   distance to the parent, then alphabetically.

The first readiness pass is kept under `out/firstpass/` unmodified, and the wave REPORT states that pass 1 was
superseded by this annex and why.
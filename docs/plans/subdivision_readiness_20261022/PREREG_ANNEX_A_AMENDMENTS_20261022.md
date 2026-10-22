# PRE-REGISTRATION ANNEX A — AMENDMENTS (written 2026-10-22 10:4x CST, before any readiness table existed)

These amendments fix **operations**, not thresholds. Every threshold in `PREREG_SUBDIVISION_READINESS_20261022.md §2`
stands exactly as written. Each amendment names what was observed on disk before it was made, so the record shows
what the operation was chosen against.

## A4-b Occurrence test accepts a regular plural (marking `A4` superseded on this point)

**What was observed first**: with the singular-only word boundary of A4, the discovery corpus returned **1,277 chunks
matching a preferred name and 5,208 matching a synonym**, and 123 (parent, child) pairs with any occurrence.
A plural-sensitivity probe over the 78 names that had occurred showed **40 of them gain chunks when a regular plural
is accepted**, some substantially (monocyte +1,904; keratocyte +762; corneal endothelial cell +469; rod bipolar cell
+275; retinal astrocyte +190). A singular-only reading therefore measures nomenclature, not evidence.

**Amendment**: a chunk matches a candidate name when the text contains the name with an optional regular plural
suffix (`s` / `es`) inside word boundaries. Both channels (preferred name / synonym) remain reported separately.

## A3-b Target tissue context: the shipped crosswalk first, library declarations second

**What was observed first**: deriving the tissue context from the library files' own scope text gave uneven results
(two libraries yielded no tissue token at all, one yielded only `RPE`), which would have made the occurrence test a
function of prose rather than of a declaration.

**Amendment**: the parent's tissue set is now taken, in order, from
(1) `kb/baselines/_tissue_class_crosswalk_v1.json` (the shipped, PI-authorized class→tissue table; covers 26 of the 76
labels), else (2) the union of its libraries' declared tissues. The source used is recorded per parent. A parent with
neither source is flagged `tissue_scope_undeclared` and its occurrence test is run on species context alone, with the
flag carried into the row — **a declaration gap is never reported as a biological negative**.

## A11 Scope classes: which (parent, child) pairs are a subtype question at all

**What was observed first**: the raw `is_a` closure contains statements that are real ontology edges but are not
subtype questions for this dictionary. Verified by path: `monocyte is_a progenitor cell CL:0011026` (a **direct** edge),
`corneal endothelial cell is_a endothelial cell` (direct), `keratocyte is_a fibroblast` (via neural-crest-derived
fibroblast). `corneal endothelial cell` and `keratocyte` are **themselves shipped dictionary classes**.

**Amendment**: before tiers are assigned, each (parent, child) pair is placed in a scope class. The ruling fixes the
axes (stage / system / cell type are separate; developmental relations are block B, not the adult candidate ranking),
so:

| scope class | condition | consequence |
|---|---|---|
| `in_scope_adult_celltype` | none of the below | eligible for T1/T1k/T2/T3 |
| `already_shipped_as_own_class` | the child's CL id or preferred name is already one of the 76 shipped labels | not a subdivision of this parent; listed, excluded from the tier tally |
| `developmental_axis` | the parent's declared stage is `fetal_developing` | graded on the developmental axis; listed with its own tally, never read as an adult subdivision (ruling: 发育阶段…分轴) |
| `system_axis_organoid_or_ipsc` | the parent's declared system is `organoid_or_ipsc` | graded on the system axis; listed with its own tally |

Biological note carried into the report: `already_shipped_as_own_class` means the term is a **sibling dictionary
entry** that happens to sit inside this parent's ontology closure — the audit names it rather than silently dropping it,
because that is exactly the "same ancestor ≠ same class" trap the ruling warns about.

No threshold moved. The tier rules of §3 are applied unchanged to the eligible pairs.
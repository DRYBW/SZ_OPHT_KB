# CL label-map overlap decision, 2026-10-20

Two of the sixteen anterior-segment labels added to the unified CL label map share a Cell Ontology term with a label that was already registered. The earlier attempt to extend the map stopped on exactly this point, because a rule in the pre-registered criteria said that a shared term has to be adjudicated before the map can grow. This file records the adjudication so the reasoning survives the commit.

The ruling was given by the project owner on 2026-10-20 after the trade-off was put to him in plain terms. It is a decision record, not a validation result: the mapping change is gated separately by the default-off switch described below.

## **CL:0000132** corneal endothelial cell, merged

The production label `Corneal Endothelium` and the new label `corneal endothelial cell` describe the same ontology term at the same level of granularity. Two labels on one term split a single cell type into two votes, and each of them carries a thinner share of the same marker panel: a query that hits the term is answered twice with half the evidence each time.

The new label is therefore mapped to **CL:0000132** and **collapses into the production entry under the CL key**. Evidence that the merge works end to end: with `EYEKB_CL_KEY=1` and a corneal panel, the response keeps one row for the term and reports `Corneal Endothelium` in `cl_duplicate_demoted`, with `merged_into` pointing at the surviving label.

## **CL:1000432** conjunctival epithelial cell, kept separate

The three production labels are layer descriptors, basal, superficial and suprabasal. The new label is their parent. Mapping a parent onto the same key would delete the layer granularity, and under the exact-CL scoring convention that this project uses, answering a subtype where the truth is the parent is filed as finer-than-truth and does not count as an error, whereas the reverse collapse does.

The new label is therefore **kept as a separate candidate** with `status: kept_separate` and **no CL key**. It stays visible in responses, it never merges into the layer labels, and it is never used as a scoring key. The residual cost is that this one candidate carries no ontology id in the response; that is the price of keeping the granularity and it is recorded rather than hidden.

## Why one rule still covers both cases

One CL term, one scoring key, is the invariant the map is built on. It applies whenever two labels sit at the same level, which is the corneal case. It does not apply across a parent and its children, which is the conjunctival case, because there the invariant would destroy information rather than remove duplication. The decision rule is therefore stated as **merge at equal level, keep separate across levels**.

## What this change cannot move

The label map is read only when `EYEKB_CL_KEY` is enabled, and that switch is registered as default off. With the shipped environment, all 721 real pipeline queries of the 28-volume evaluation set were re-run before and after the edit: every per-query response is byte-identical, the aggregate is **5,219,369 bytes** in both runs, and an audit hook counted zero opens of the label-map file during the run. The default route therefore cannot be affected by the content of this file, whatever it says.

Under `EYEKB_CL_KEY=1` the map loads 76 labels, 61 of them with an ontology id, 14 documented as having no matching term, and one kept separate as described above.

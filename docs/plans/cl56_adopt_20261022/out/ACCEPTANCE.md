# Acceptance rule — result

Rule: `PREREG_ADOPT_CL56_20261022.md` §5. Verdict: **NO-GO**

- **(a) no dataset's cell-weighted consistent share may fall** → **FAIL**
- **(b) the aggregate cell-weighted inconsistent share must not rise** → **FAIL**
- **(c) every move attributable cluster by cluster, zero unexplained** → **PASS**
- **(d) the finer name must be the author's own label for those clusters** → **PASS**
- **(e) the kill switch restores the pre-flip default byte-for-byte** → **PASS**

Failed clauses: a, b

- E1 held=True — the scope list is a small subset of the 25: 3 of 25 adopted (14 clusters / 39005 cells); 22 pending with reasons
- E2 held=False — the named mechanism is narrow: gain at the ontology reading and at abstention, not a broad takeover: whole recording: same_cl 244 -> 220, truly_inconsistent 176 -> 241, abstain 165 -> 120; scope subset: {'kb_coarser': 12, 'abstain': 2} -> {'kb_coarser': 10, 'same_cl': 3, 'abstain': 1}
- E3 held=True — a renamed cluster can move consistent -> related under the frozen family ruler: consistent->related 11722 cells; consistent->inconsistent 66646 cells (the family ruler maps an adopted finer name to no family)
- E4 held=False — the named risk is clause (b) via unmappable names: unmappable_pred 15 -> 15 clusters: the label-map rows added in this card resolve, so the predecessor's `unmappable_pred` failure mode did not recur; the harm came from over-application instead
- E5 held=True — a NO-GO with numbers is a valid outcome: NO-GO

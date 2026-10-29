# Amendment 1: what the G4 anchor consequence is, and what it is not

Written before the G4 runs, so the criteria are still fixed ahead of the numbers.

## Added criteria

| id | criterion | fail action |
|---|---|---|
| **C8** | on the G4 fixture: the rollback state (`EYEKB_L2_BUDGET=0`) reproduces the pre-change anchors byte for byte, and the post-change anchors are deterministic across two runs. The anchors this change moves are recorded by name | stop, do not commit |
| **C9** | the module's registry row (`docs/W3_PIPELINE_REGISTRY.tsv`, `L2-11`) and a change-control instance row both carry the new sha256, the new default, and the fact that the flip was approved by the project owner | stop |

## Why C8 does not re-anchor G4

The precedent for a default-route change (`activate_onfibro_20261022`) re-anchored G4 inside its
own card, and legitimately so: its causal control reproduced the previous anchors with the switch
off, which proves the movement came from the change and not from the machine.

That control is not available here. G4 already reports 2/3 against its frozen expectation before
this card touches anything (`annotation_evidence_report.md__normalized` mismatch, recorded since
the earlier re-anchor rounds). If this card wrote a new expectation now, it would absorb that
unexplained drift and make a red gate look green — which is exactly the move the change-control
rule forbids.

So this card measures and publishes the differential, and leaves re-anchoring to a card whose
job is to explain the pre-existing 2/3 first. Whoever picks it up gets the numbers ready-made in
`out/G4_DIFFERENTIAL.json`.

## Consequence to state plainly

The default change does change shipped output: the evidence report and the decision template
carry 30 query genes per cluster instead of 10, so both anchors move by design. Anyone comparing
old runs to new ones will see that difference and should read it as the change, not as drift.
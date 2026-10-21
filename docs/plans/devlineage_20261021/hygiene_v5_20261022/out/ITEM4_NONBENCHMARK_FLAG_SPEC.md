# A non-benchmark flag: what it would have to assert

Decision-ready finding from the lineage-hygiene wave (item 4). Nothing was activated and
no panel body was changed.

## Measured

| panel | genes | A refused (no independent basis) | B admitted with evaluation-only panel basis | declared selection basis |
|---|---|---|---|---|
| markers_v9_dev_retina.json | 149 | 67 | 0 | developmental_panel_data_plus_literature (data track = the dev-exam substrate) |
| markers_k9_ocs_increment.json | 20 | 0 | 0 | in_house_atlas_eval_volume (D002 ocular surface) + canonical consensus |
| markers_membrane_v1.json | 199 | 0 | 0 | in_house_atlas_non_eval (GSE165784) + canonical consensus |
| markers_v10_antseg_increment.json | 277 | 0 | 0 | in_house_atlas_eval_volume (per-entry dev_volume) + corpus harvest |
| markers_v11_lensiris_increment.json | 80 | 0 | 0 | in_house_atlas_eval_volume (per-entry dev_volume) + corpus harvest |
| markers_v4.1_clean.json | 43 | 0 | 0 | curated_panel_pre_2026 (literature + canonical consensus) |
| markers_v5_retina_interneuron.json | 156 | 0 | 0 | in_house_atlas_eval_volume (HRCA D001 pairwise-DE gate) |
| markers_v6_face_increment.json | 18 | 0 | 0 | in_house_atlas_eval_volume (D002 ocular surface) + canonical consensus |
| markers_v6_lacrimal_increment.json | 7 | 0 | 0 | in_house_atlas_non_eval (GSE164403 human lacrimal gland) |
| markers_v6_retina_repair.json | 141 | 0 | 0 | in_house_atlas_eval_volume (HRCA D001 / KB7 repair disposition) |
| markers_v7_panel_increment.json | 89 | 0 | 0 | in_house_atlas_eval_volume (retina facet increment on D001-derived entries) |
| markers_v8_dev_retina.json | 28 | 0 | 0 | developmental_panel_data_plus_literature (data track = the dev-exam substrate) |

Totals across the consumed panels: A = 67 gene-panel rows, B = 0.

`markers_v12_holefill_increment.json` (present only in the git tree): 17 entries / 204 genes; its own scope names the measured coverage holes of the 28-volume / 721-cluster run — yes.

## Why a file-level bit is not enough

- the same panel file mixes the three readings: measured per panel in ITEM4_EVAL_BASIS_BY_PANEL.tsv (columns A, B, C sum to the panel's gene count)
- a panel whose declared selection basis is an evaluation volume still carries genes whose own entry names an independent source (reading C), so flagging the file would condemn them
- a panel whose declared basis is independent can still carry an entry whose only provenance is an evaluation volume (reading B), so not flagging the file would exonerate them

## What the flag must assert

- granularity: per entry (label) inside a panel file, and per gene inside that entry — not per file
- a basis class drawn from a closed vocabulary: independent_literature | independent_in_house_atlas_non_benchmark | evaluation_volume | evaluation_report_holes | unstated
- when the basis class is evaluation_volume or evaluation_report_holes: the entry must carry an independent anchor (a PMID or a corpus row) for every gene it wants to be usable for a lineage/marker claim, named per gene — the flag says 'this candidate list leaned on the benchmark', not 'this gene is unusable'
- the name of the evaluation artefact it leaned on (volume id / report id), so a reader can re-derive the exclusion list instead of trusting the bit
- an explicit statement of what the flag does NOT claim: it does not assert that the gene is wrong, and it does not authorise changing a shipped panel body

## Where it must be enforced

- at the consuming layer (the marker layer's admission test), not by editing the shipped panels: the contract's red line forbids deriving a marker from the evaluation volumes' own queries, and a rewrite of kb/ is an activation by another name

## Machine check

- for every assertion in a lineage artefact: if the source entry's basis class is evaluation_volume or evaluation_report_holes, the assertion must carry an anchor that is not derived from that volume; the marker layer already implements exactly this for reading A (the four-condition corpus test), and reading B is what is not yet checkable

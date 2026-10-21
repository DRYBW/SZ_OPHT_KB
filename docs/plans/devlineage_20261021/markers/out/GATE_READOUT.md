# Gate readout — marker layer

verdict: **PASS**  (13 checks, 0 failed)

| check | name | status | n_offenders | detail |
|---|---|---|---|---|
| G1 | KEY_RESOLVES | PASS | 0 | assertions=1053 node keys=70 edge keys=34 unresolved=0 |
| G2 | ANCHOR_RESOLVES | PASS | 0 | anchors=1053 by kind={'link_registry_gene_verified': 313, 'corpus_gene_row': 730, 'panel_provenance_stated': 6, 'panel_entry_basis_unstated': 4} corpus rows re-read=378 ok=378 bad=0 |
| G3 | VOCAB | PASS | 0 | fields checked over 1053 assertions + 34 edges; rows with an out-of-vocabulary value=0 |
| G4 | NO_NUMERIC | PASS | 0 | assertions with effect_value=0 (all qualitative by design); offenders=0 |
| G5 | RNA_PROTEIN_SPLIT | PASS | 0 | assays={'literature_RNA': 1025, 'literature_protein': 23, 'scRNA': 1, 'unspecified': 4}; (node, gene) pairs carrying both an RNA and a protein row (kept as separate rows, never merged)=0 |
| G6 | SPECIES_STAGE | PASS | 0 | node rows carry their node's species and stage; edge rows name source and target group and disclose stage_crossing; offenders=0 |
| G7 | NO_EVAL_INPUT | PASS | 0 | 60 forbidden tokens over 10 data artefacts; hits=0 |
| G8 | GAP_COVERAGE | PASS | 0 | gap rows=226 reasons=12/16 declared; zero-evidence nodes=11; edges covered=61/34 |
| G9 | NO_OFF_WITHOUT_DETECTION | PASS | 0 | off/down assertions=0; loss-side genes recorded as a gap instead=92 |
| G10 | REBUILD_REPLAY | PASS | 0 | chain rebuilt into a scratch dir: m0_corpus_gene_index.py rc=0; m1_nodes.py rc=0; m2_node_markers.py rc=0; m3_edge_assertions.py rc=0; m4_gap_register.py rc=0; artefacts compared=12 differing=0 |
| G11 | NO_FABRICATED_GENE | PASS | 0 | gene symbols in assertions=695; unresolvable to the corpus index or a shipped panel=0 |
| G12 | GOLDEN721 | PASS | 0 | recorded production queries replayed in 6.1s: n=721 identical=721 differ=0 (recorded baseline differ=0) |
| G13 | KB_UNTOUCHED | PASS | 0 | kb/ files walked; newest mtime=2026-10-21 23:22; files written during this card=0 |

Rebuild replay: build ok; artefacts compared=12, differing=0.

Recorded query set: rc=0 in 6.1s; now {'off': {'n': 721, 'identical': 721, 'differ': 0, 'examples': []}, 'on': {'n': 721, 'identical': 721, 'differ': 0, 'n_with_demoted': 19, 'examples': []}}; recorded {'off': {'n': 721, 'identical': 721, 'differ': 0, 'examples': []}, 'on': {'n': 721, 'identical': 721, 'differ': 0, 'n_with_demoted': 19, 'examples': []}}.

# Gate readout — wave-5 lineage hygiene

verdict: **PASS** (12 checks, 0 failed)

| check | name | status | n_offenders | detail |
|---|---|---|---|---|
| G1 | UPSTREAM_TABLE_HONEST | PASS | 0 | rows=100; rows contradicting their own direction=0; the builder computes the value (True); upstream gate B verdict=PASS (0 failed) |
| G2 | STRICT_GRADING_MATCHES_SUPERSEDING_ARTEFACT | PASS | 0 | gain rows=10; agreement with MARKER_CHANGE_EDGES.tsv=10; disagreements=0; gene sets identical=True |
| G3 | ONE_RECONCILED_TABLE | PASS | 0 | reconciled rows=100; both gradings carried=True; the loss side's refusal reason is recorded (detection_conditions_insufficient) |
| G4 | REPOINT_ACCOUNTS_FOR_EVERY_SOURCE_ROW | PASS | 0 | scaffold rows in=103/103 nodes, 51/51 edges; adapter rows=103/51; builders rc=[0, 0, 0, 0]; endpoints unresolved=0; assertions unresolved=0 |
| G5 | GRADE_CONFLICT_SURFACED_AND_SOURCE_GOVERNS | PASS | 0 | edges=51; builder/source agreement=0; conflicts=51 (all surfaced); reconciled rows where the source grade governs=51/51 |
| G6 | KB_LEDGER_COMPLETE_AND_NO_KB_WRITE | PASS | 0 | files ledgered=20; data tree unchanged=True; git tree unchanged=True; every shared file either byte-identical or n/a=True; sync script dry-run by default=True |
| G7 | EVAL_BASIS_FINDING_RECONCILES | PASS | 0 | per-panel A total=67; distinct eval-only genes=67; per-gene rows=75 (one row per label the gene sits in); summary A=67; activation=none; panel bodies changed=0 |
| G8 | NO_NETWORK | PASS | 0 | audit-hook receipts=102 (proves the hook was installed); network events=0 |
| G9 | DEFAULT_BEHAVIOUR_IDENTICAL | PASS | 0 | recorded production queries replayed in 5.8s: n=721 identical=721 differ=0 (recorded n=721) |
| G10 | WHAT_THIS_CARD_TOUCHED_OUTSIDE_ITS_WAVE | PASS | 0 | the repository working tree is clean |
| G11 | MANIFEST_VERIFIES | PASS | 0 | manifest entries=74, verified=74, failing=0 |
| G12 | CLEAN_CLONE_GREEN | PASS | 0 | clean-clone check: {"commit": "c321667af0028959748503b791398218c3a03f5a", "clone_root": "(temporary clone of the repository, removed after the run)", "gate_rc": 0, "gate_verdict": "PASS", "gate_failed": "[]", "files_differing_from_author_tree": 0} |

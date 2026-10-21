# V3 stage axis — machine gate readout

items: 12   PASS: 12   FAIL: 0

| item | verdict | title | measured |
|---|---|---|---|
| G1 | PASS | every stage literal is in the declared four-level axis {fetal,adult,developing,unknown} | `{"offending_rows": 0, "rows_checked": 354, "examples": []}` |
| G2 | PASS | no row silently assigned to adult; every non-adult row carries a disclosure row | `{"non_adult_rows": 222, "undisclosed": 0, "adult_rows_with_non_adult_source_literal": 0}` |
| G3 | PASS | no assertion mixes two stages in one row | `{"rows_with_more_than_one_stage_token": 0}` |
| G4 | PASS | no cross-species stitching in any published table; every cross-species candidate rejected | `{"species_values_in_tables": ["human"], "non_human_rows": 0, "cross_species_candidates_real": 1, "cross_species_candidates_fixture": 1, "real_rejected": 1}` |
| G5 | PASS | no numeric effect value without a traceable extraction record | `{"rows_with_effect_value": 0, "claim_types": ["qualitative"]}` |
| G6 | PASS | developmental entries appear in no adult query path | `{"retina_dev_in_a_DEFAULT_LIBS_whitelist": false, "libraries_seen_in_adult_default_rankings": ["markers_membrane_v1.json", "markers_v4.1_clean.json", "markers_v5_retina_interneuron.json", "markers_v6_retina_repair.json"]}` |
| G7 | PASS | `off` is never produced from absence of mention | `{"off_rows_in_tables": 0, "off_candidates_generated": 218, "of_which_rejected": 218}` |
| G8 | PASS | every admitted change carries an anchor and a contract grade | `{"admitted_rows": 0, "invalid_admitted_rows": 0, "note": "an empty admitted set passes; the count is reported so an empty set can never be read as a filled one"}` |
| G9 | PASS | the recognition probe stores the real service output, the exact commands, and replays byte-identically | `{"n_calls_pass1": 104, "n_differing_responses": 0, "verdict_table_identical": true, "server": "/home/ubuntu/EYEKB_REPO/mcp_server/server.py", "interpreter": "/home/ubuntu/training-venv/bin/python3", "transport": "MCP stdio (mcp SDK client -> shipped server.py subprocess)"}` |
| G10 | PASS | default behaviour unchanged by this card: no shipped byte differs from the committed release, and this card's own recorded query set replays with difference count 0 | `{"git_diff_rc": 0, "git_diff_lines": 0, "untracked_paths_outside_this_card": [], "replay_difference_count_own_query_set": 0, "own_query_set_size": 104}` |
| G11 | PASS | zero download, zero network: no client code in this card's scripts, and no outbound socket event in the instrumented run | `{"network_client_code_hits": [], "audit_control_lines": 4, "audit_event_lines_total": 5, "audit_outbound_event_lines": 0, "note": "socket.__new__ / socket.gethostname are local-only object construction and the hostname field of the service's own call-trace record; they are counted separately and not treated as network use"}` |
| G12 | PASS | repository-facing text of this card's deliverables is English only | `{"files_with_cjk_characters": {}}` |

## Service-behaviour observations (recorded, not scored)

- verdict counts: `{"needs_information_this_interface_cannot_observe": 4, "observable_now": 11}`
- silent adult assignment on a fetal window: `['cone', 'hc', 'progenitor_nrpc_late', 'progenitor_rpc_late', 'rgc', 'rod']`
- `state_annotations` hits on the default route: `[]`, entries returned under that key anywhere in the probe: `['Endo_Patho', 'Mac_DAM_LAM', 'Proliferating', 'Retinal_Proliferating', 'TAC_proliferating']`
- boundary cells: `{"rows": 61, "by_stage": {"fetal": 15, "developing": 15, "unknown": 15, "adult": 16}, "observable_by_stage": {"fetal": 11, "developing": 0, "adult": 10, "unknown": 0}, "by_reason": {"observable_via_shipped_path": 11, "no_assertion_in_corpus": 31, "observable_via_named_ranking": 9, "no_adult_counterpart_in_vocabulary": 6, "observable_via_named_ranking_fetal_side_absent": 1, "no_precursor_entry_in_corpus": 3}, "unobservable_cells": 40}`
- change candidates: `{"n_candidates_real": 287, "n_rejected_real": 287, "n_admitted_real": 0, "n_candidates_fixture": 6, "n_rejected_fixture": 6, "n_admitted_fixture": 0, "primary_rule_counts_real": {"R2": 40, "R3": 247}, "rules_never_fired_real": ["R1", "R5", "R9", "R11"], "by_family": {"cross_entry_composition_differ": 5, "cross_source_snapshot_differ": 239, "cross_species_stitch": 1, "derived_keyword_stage": 40, "multistep_propagation": 2}}`

## External findings (measured here, not caused by this card)

### repo_recorded_query_set_does_not_reproduce_at_HEAD
- measured: tests/probe_tool_panel_identity.py --baseline tests/fixtures/tool_panel_baseline.json -> legacy_panel and full_panel digests moved; 5 of 12 calls differ
- cause: get_kb_page{kind:index} and get_kb_page{kind:topic,name:vascular}: the panel spells the argument `kind`, the tracked tool signature is `scope` at HEAD and also at the commit that last touched the fixture (a400315) -> argument validation error, i.e. the panel does not match any tracked build of the server on this machine; get_tissue_composition{detail:true}: the panel passes a boolean, the tracked signature is `detail: str` -> validation error; search_literature{query:...} without cell_type: the tracked signature requires cell_type -> validation error; explain_annotation{cell_type:'Mueller cell'}: no validation error; a content difference the fixture cannot attribute because it stores digests only
- attribution: pre-existing; not caused by this card (git diff HEAD over mcp_server/kb/tests/scripts is empty and the only untracked path is this card's own directory)

### unrecognised_stage_literal_returns_the_adult_baseline
- measured: get_tissue_composition(species=human, tissue=retina, development_stage='organoid') returns a response byte-identical to development_stage='adult' (same md5), with no flag; the shipped tool docstring names 'organoid -> unknown+flag'
- cause: the query path maps only fetal/developing/postnatal/unknown; an unrecognised literal falls through to the adult main file
- attribution: external observation about the shipped surface; the card's own tables never pass an unrecognised literal

### fetal_window_recognised_but_named_as_an_adult_class
- measured: 6 of the probed lineages return an adult class as the top-1 named candidate for a fetal-state window: ['cone', 'hc', 'progenitor_nrpc_late', 'progenitor_rpc_late', 'rgc', 'rod']
- cause: the developmental panel is not on the default route; the adult libraries still score the fetal window and name the nearest adult class
- attribution: external observation; the card records it per lineage and does not silence it

### cell_cycle_entries_are_moved_out_of_the_named_ranking_by_design
- measured: Retinal_Proliferating and TAC_proliferating are annotated concept_kind=state_program in the shipped sidecar, so their identity comes back under the additive `state_annotations` key (measured: n_shared=10 for Retinal_Proliferating on both routes)
- cause: deliberate shipped behaviour (concept-kind stratification), not a defect
- attribution: recorded so a reader does not read an empty ranking as a missing answer

### superseded_v8_developmental_panel_exists_only_on_the_data_mount
- measured: kb/markers/markers_v8_dev_retina.json is present at /mnt/D/EyeKB/kb/markers/ (sha256 recorded in ROBUSTNESS_RESULTS.json) but not in the repository
- cause: the repository keeps only the active v9 panel
- attribution: the robustness pass uses the v8 gene lists (its own ban list permits word-level reference) and records the path and sha, so the step is reproducible only where that file exists

## The composition tool's stage literals

| literal | mode / entry | organism_stage | bytes | identical to the adult response |
|---|---|---|---|---|
| `` | baseline_human_retina | adult | 91392 | Y |
| `adult` | baseline_human_retina | adult | 91392 | Y |
| `developing` | fetal_development_concept |  | 7266 | N |
| `fetal` | fetal_development_concept |  | 7261 | N |
| `organoid` | baseline_human_retina | adult | 91392 | Y |
| `postnatal` | fetal_development_concept |  | 7266 | N |
| `unknown` | no_unknown_stage_entry |  | 319 | N |

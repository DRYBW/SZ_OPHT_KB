# V3 — the developmental stage axis, and whether marker change is recognisable

Card `t_aa1b7f12` (workstream V3 of the frozen developmental-lineage contract). Deliverable root: `docs/plans/devlineage_20261021/stages/` in the shipped repository (`/home/ubuntu/EYEKB_REPO`), mirrored to the path the card names on the data mount (`/mnt/D/EyeKB/plans/devlineage_20261021/stages/`).

This card owns three things: the stage axis (which markers a lineage carries at which stage), the recognition test (can the shipped interface tell those stages apart, measured rather than asserted), and the rule that a marker change is a per-edge per-stage assertion with an anchor and a grade — never an inference from two snapshots taken elsewhere.

## 1. Which service answered

- transport: **MCP stdio** — the shipped `mcp_server/server.py` started as a subprocess by the MCP SDK client; interpreter `/home/ubuntu/training-venv/bin/python3` (the one on this machine that can import `mcp.server.MCPServer`; the bare system interpreter cannot, measured).
- the shipped server's own identity tool answered: release_id `8d80da1b38c8`, protocol generation `KB1v2-0.14-kb11a-reasonjoin`, `3420` files covered (`every file of the tree (HEAD, or the staged tree with --source index)`). `python3 scripts/release_identity.py --check` at HEAD returns rc=0 (IDENTITY MATCH), so the identity names the bytes that answered.
- the probe tagged its own traffic with `EYEKB_MCP_TRACE_TAG=devlineage-v3-stage-probe` so the service's call-trace layer can exclude self-test traffic.
- two kernel copies exist on this machine; §0 of `PREREG_STAGE_CHANGE_v1.md` records the sha256 of both and decides, before probing, that the **repository** copy is the shipped service (committed, carries the release identity, and is a strict superset of the data-mount copy).

## 2. Stage-resolved marker sets (task 1)

- nodes: **24** (14 developmental entries + 10 adult classes); marker assertions: **269** (222 at `fetal`, 47 at `adult`, 0 at `developing`, 0 at `unknown`).
- every stage literal is one of the contract's four; the source literal is kept in its own column (`source_stage_literal`). Identifier rule respected: 13 nodes carry a Cell Ontology id read from the release file, 11 are recorded `NO_MATCH` with the mandatory in-house prefix.
- node-key injectivity audit: `{"dl:CL:0002672|sp=human|ts=retina|st=fetal|es=in_vivo": 2}` — `RPC_early` and `RPC_late` are two entries that share one CL term and differ only by the label map's temporal qualifier, so the contract's node key is not injective there. Both rows are kept and distinguished by `node_instance_id`; the collision is reported, not patched away.
- the grade counts: `{"identity_conversion_not_direct": 269}`. `direct_lineage_support` and `trajectory_only` carry **0 rows**: no source in this corpus asserts a lineage relation *with* a gene (`direct_lineage_support`), and none is a pseudotime-only association, so both values are unused here rather than stretched to fit.
- the adult class **Microglia** is claimed by no developmental entry in this corpus (recorded as a boundary cell, not silently dropped).

Per-lineage coverage, i.e. the "where a lineage has markers only for one stage, say so" answer:

| lineage | fetal entry | adult counterpart(s) | fetal markers | adult markers | finding |
|---|---|---|---|---|---|
| rod | Rod_precursor | Rod | 25 | 5 | both stages carry markers |
| cone | Cone_precursor | Cone | 25 | 5 | both stages carry markers |
| bc | BC_precursor | BC | 0 | 5 | adult-stage markers only (no fetal-stage marker asserted for this lineage in the corpus) |
| ac | AC_precursor | AC | 18 | 5 | both stages carry markers |
| hc | HC_precursor | HC | 25 | 5 | both stages carry markers |
| rgc | RGC_precursor | RGC | 17 | 5 | both stages carry markers |
| glia | glia_precursor | MG;Astrocyte | 0 | 10 | adult-stage markers only (no fetal-stage marker asserted for this lineage in the corpus) |
| rpe | RPE_fetal | RPE | 0 | 6 | adult-stage markers only (no fetal-stage marker asserted for this lineage in the corpus) |
| progenitor_rpc_early | RPC_early | - | 25 | 0 | fetal-stage markers only, no adult counterpart class in the 10-class adult vocabulary |
| progenitor_rpc_late | RPC_late | - | 25 | 0 | fetal-stage markers only, no adult counterpart class in the 10-class adult vocabulary |
| progenitor_nrpc_early | NRPC_early | - | 25 | 0 | fetal-stage markers only, no adult counterpart class in the 10-class adult vocabulary |
| progenitor_nrpc_late | NRPC_late | - | 25 | 0 | fetal-stage markers only, no adult counterpart class in the 10-class adult vocabulary |
| progenitor_tac | TAC_proliferating | - | 2 | 0 | fetal-stage markers only, no adult counterpart class in the 10-class adult vocabulary |
| progenitor_cycling_state | Retinal_Proliferating | - | 10 | 0 | fetal-stage markers only, no adult counterpart class in the 10-class adult vocabulary |
| _(the 0 `developing` and 0 `unknown` cells)_ | — | — | 0 | 0 | no per-gene marker evidence exists in this corpus for those stages; recorded, not filled |

## 3. The recognition probe (task 2) — built, run, and measured

The input a caller would actually supply is the top-K gene window of the lineage's stage-resolved set (K ∈ {10, 25}, frozen in the prereg before running; a set shorter than K is supplied whole and the shortfall is recorded). Each window is sent twice: on the default route a caller gets with no extra knowledge, and on the explicit developmental route. 104 calls in 2.74 s wall, with 0 error responses out of 104.

| lineage | verdict | reason code | fetal window top-1 (default route) | adult window top-1 | off_domain advisory on fetal | rankings identical | silent adult assignment |
|---|---|---|---|---|---|---|---|
| ac | **observable_now** | shipped_off_domain_advisory_fires_on_fetal_input | pDC (1) | AC (5) | Y | N | N |
| bc | **needs_information_this_interface_cannot_observe** | no_discriminating_gene_in_any_loaded_library_and_no_stage_channel | (empty) (-) | BC (5) | N | N | N |
| cone | **observable_now** | shipped_off_domain_advisory_fires_on_fetal_input | BC (1) | Cone (5) | Y | N | Y |
| glia | **needs_information_this_interface_cannot_observe** | no_discriminating_gene_in_any_loaded_library_and_no_stage_channel | (empty) (-) | MG (5) | N | N | N |
| hc | **observable_now** | shipped_off_domain_advisory_fires_on_fetal_input | retina_interneuron::HC (5) | HC (5) | Y | N | Y |
| progenitor_cycling_state | **observable_now** | shipped_off_domain_advisory_fires_on_fetal_input | (empty) (-) | (empty) (-) | Y | NA | N |
| progenitor_nrpc_early | **observable_now** | shipped_off_domain_advisory_fires_on_fetal_input | pDC (1) | (empty) (-) | Y | NA | N |
| progenitor_nrpc_late | **observable_now** | shipped_off_domain_advisory_fires_on_fetal_input | BC (1) | (empty) (-) | Y | NA | Y |
| progenitor_rpc_early | **observable_now** | shipped_off_domain_advisory_fires_on_fetal_input | pDC (1) | (empty) (-) | Y | NA | N |
| progenitor_rpc_late | **observable_now** | shipped_off_domain_advisory_fires_on_fetal_input | MG (1) | (empty) (-) | Y | NA | Y |
| progenitor_tac | **observable_now** | shipped_off_domain_advisory_fires_on_fetal_input | Schwann (1) | (empty) (-) | Y | NA | N |
| rgc | **observable_now** | shipped_off_domain_advisory_fires_on_fetal_input | HC (2) | RGC (5) | Y | N | Y |
| rod | **observable_now** | shipped_off_domain_advisory_fires_on_fetal_input | Rod (2) | Rod (5) | Y | N | Y |
| rpe | **needs_information_this_interface_cannot_observe** | no_discriminating_gene_in_any_loaded_library_and_no_stage_channel | (empty) (-) | RPE (6) | N | N | N |
| adult_only::Microglia | **needs_information_this_interface_cannot_observe** | no_precursor_entry_in_corpus | (empty) (-) | Micro (1) | N | NA | NA |

Verdict counts: `{"needs_information_this_interface_cannot_observe": 4, "observable_now": 11}`. The four verdicts the brief names are used exactly as frozen; the boundary register (task 4) carries the per-cell version.

**How the answer comes back.** Three shipped paths carry the stage signal, and the register names which one answered:

- the `off_domain` advisory on the default route (`possible_dev_fetal_content`) — 11 fetal cells;
- the named ranking on the default route, for the adult side — 10 adult cells;
- the additive `state_annotations` key, which is where the shipped concept-kind stratification puts the two cell-cycle entries (`Retinal_Proliferating`, `TAC_proliferating`); their identity does come back, under that key, with n_shared=10 for the 10-gene window — an empty named ranking there is **not** a missing answer.

**The limitation of this probe, disclosed rather than hidden.** The fetal window is drawn from the same file the `off_domain` advisory reads, so the advisory fires whenever that window is supplied: it answers "this window looks like the developmental panel", which is weaker than "an independent fetal sample would be recognised". A second pass therefore re-asks the same question with windows that are not the panel's final list:

| window source | windows | advisory fired | dev_best >= 1 | dev_best >= 2 |
|---|---|---|---|---|
| v9 panel (narrower) | 10 | 10 | 10 | 10 |
| genes this build removed as mature markers | 8 | 0 | 0 | 0 |
| v8 panel build | 4 | 2 | 4 | 3 |

The middle row is the important one: the genes the panel build itself **removed** as mature markers (8 windows) carry **no** developmental signal at all, so the advisory is not a generic detergent that fires on anything fetal-looking. The third row is the empirical instance of the "wider query window" verdict: a window drawn from the superseded v8 build returns `dev_best=1` with the advisory silent (`RPC_late`, 7 genes) where the v9 windows return `dev_best>=5`. Recognition is therefore **window-composition sensitive**, and the verdicts above are the frozen-rule readings of the primary windows — the supplementary pass was not used to revise them.

The composition surface — the only shipped tool that accepts a stage literal at all — answers:

| literal | mode / entry | organism_stage | bytes | identical to the adult response |
|---|---|---|---|---|
| `` | baseline_human_retina | adult | 91392 | Y |
| `adult` | baseline_human_retina | adult | 91392 | Y |
| `developing` | fetal_development_concept |  | 7266 | N |
| `fetal` | fetal_development_concept |  | 7261 | N |
| `organoid` | baseline_human_retina | adult | 91392 | Y |
| `postnatal` | fetal_development_concept |  | 7266 | N |
| `unknown` | no_unknown_stage_entry |  | 319 | N |

## 4. Change legitimacy (task 3)

Rules R1–R11 are frozen in the prereg and implemented as code in `scripts/04_change_legitimacy_check.py`; the crossing is reported per rule in `out/RULE_REGISTRY.tsv`. Candidates were generated from the materials that actually tempt a reader, not from invented examples:

| family | candidates | what it tempts |
|---|---|---|
| cross_source_snapshot_differ | 239 | "this gene is off in adult" / "on in adult", inferred from the fetal panel list vs the adult atlas list (two studies) |
| derived_keyword_stage | 40 | treating the `PRECURSOR_EDGES.tsv` derived keyword stage column as a stage fact |
| cross_entry_composition_differ | 5 | reading a lineage's growth across stage from two label histograms that use different vocabularies and different studies |
| multistep_propagation | 2 | propagating a direction along a chain deeper than one step |
| cross_species_stitch | 1 | a human stage on one side and a mouse-labelled evidence node on the other (structured `species: mouse` fields only, 3 such genes exist in the shipped libraries) |

Result: **287 real candidates generated, 287 rejected, 0 admitted**; 6 rule-firing fixtures, 6 rejected (counted separately). Primary rejection reasons: `{"R2": 40, "R3": 247}`. Rules with no real candidate in this corpus (`R1, R5, R9, R11`) are exercised by labelled fixtures so the code path is proven rather than assumed.

An empty admitted set is the honest result here and matches the contract's own rule: a stage with no available dynamics is recorded as unavailable, which is strictly better than a speculative paragraph. The tempting raw material is not thrown away — it is in `out/CANDIDATE_CHANGES.tsv` with the rule each row broke.

## 5. Observability boundary register (task 4)

61 cells (lineage × stage). Observable through the shipped interface: `{"fetal": 11, "developing": 0, "adult": 10, "unknown": 0}`. Not observable: **40** cells, by reason: `{"observable_via_shipped_path": 11, "no_assertion_in_corpus": 31, "observable_via_named_ranking": 9, "no_adult_counterpart_in_vocabulary": 6, "observable_via_named_ranking_fetal_side_absent": 1, "no_precursor_entry_in_corpus": 3}`.

The four reasons, in plain words:

- `no_assertion_in_corpus` — the corpus simply carries no per-gene marker set for that stage (all 15 `developing` and all 15 `unknown` cells, plus the three lineages whose developmental entry has no genes: BC, glia, RPE).
- `no_precursor_entry_in_corpus` — an adult class no developmental entry claims (Microglia).
- `no_adult_counterpart_in_vocabulary` — the six progenitor/cycling entries: their own record forbids mapping a developmental concept onto an adult class, so they have no adult side.
- `no_assertion_in_corpus` again for the fetal side of the three gene-less entries — the honest form of "this lineage is not observable today".

## 6. The machine gate (task 5)

**12 items: 12 PASS / 0 FAIL.** Full readout with the measured value behind each item: `out/GATE_READOUT.md` and `out/GATE_READOUT.json`.

| item | verdict | what it asserts |
|---|---|---|
| G1 | PASS | every stage literal is in the declared four-level axis {fetal,adult,developing,unknown} |
| G2 | PASS | no row silently assigned to adult; every non-adult row carries a disclosure row |
| G3 | PASS | no assertion mixes two stages in one row |
| G4 | PASS | no cross-species stitching in any published table; every cross-species candidate rejected |
| G5 | PASS | no numeric effect value without a traceable extraction record |
| G6 | PASS | developmental entries appear in no adult query path |
| G7 | PASS | `off` is never produced from absence of mention |
| G8 | PASS | every admitted change carries an anchor and a contract grade |
| G9 | PASS | the recognition probe stores the real service output, the exact commands, and replays byte-identically |
| G10 | PASS | default behaviour unchanged by this card: no shipped byte differs from the committed release, and this card's own recorded query set replays with difference count 0 |
| G11 | PASS | zero download, zero network: no client code in this card's scripts, and no outbound socket event in the instrumented run |
| G12 | PASS | repository-facing text of this card's deliverables is English only |

## 7. External findings (measured here, not caused by this card)

**repo_recorded_query_set_does_not_reproduce_at_HEAD** — tests/probe_tool_panel_identity.py --baseline tests/fixtures/tool_panel_baseline.json -> legacy_panel and full_panel digests moved; 5 of 12 calls differ  
_cause_: get_kb_page{kind:index} and get_kb_page{kind:topic,name:vascular}: the panel spells the argument `kind`, the tracked tool signature is `scope` at HEAD and also at the commit that last touched the fixture (a400315) -> argument validation error, i.e. the panel does not match any tracked build of the server on this machine; get_tissue_composition{detail:true}: the panel passes a boolean, the tracked signature is `detail: str` -> validation error; search_literature{query:...} without cell_type: the tracked signature requires cell_type -> validation error; explain_annotation{cell_type:'Mueller cell'}: no validation error; a content difference the fixture cannot attribute because it stores digests only  
_attribution_: pre-existing; not caused by this card (git diff HEAD over mcp_server/kb/tests/scripts is empty and the only untracked path is this card's own directory)

**unrecognised_stage_literal_returns_the_adult_baseline** — get_tissue_composition(species=human, tissue=retina, development_stage='organoid') returns a response byte-identical to development_stage='adult' (same md5), with no flag; the shipped tool docstring names 'organoid -> unknown+flag'  
_cause_: the query path maps only fetal/developing/postnatal/unknown; an unrecognised literal falls through to the adult main file  
_attribution_: external observation about the shipped surface; the card's own tables never pass an unrecognised literal

**fetal_window_recognised_but_named_as_an_adult_class** — 6 of the probed lineages return an adult class as the top-1 named candidate for a fetal-state window: ['cone', 'hc', 'progenitor_nrpc_late', 'progenitor_rpc_late', 'rgc', 'rod']  
_cause_: the developmental panel is not on the default route; the adult libraries still score the fetal window and name the nearest adult class  
_attribution_: external observation; the card records it per lineage and does not silence it

**cell_cycle_entries_are_moved_out_of_the_named_ranking_by_design** — Retinal_Proliferating and TAC_proliferating are annotated concept_kind=state_program in the shipped sidecar, so their identity comes back under the additive `state_annotations` key (measured: n_shared=10 for Retinal_Proliferating on both routes)  
_cause_: deliberate shipped behaviour (concept-kind stratification), not a defect  
_attribution_: recorded so a reader does not read an empty ranking as a missing answer

**superseded_v8_developmental_panel_exists_only_on_the_data_mount** — kb/markers/markers_v8_dev_retina.json is present at /mnt/D/EyeKB/kb/markers/ (sha256 recorded in ROBUSTNESS_RESULTS.json) but not in the repository  
_cause_: the repository keeps only the active v9 panel  
_attribution_: the robustness pass uses the v8 gene lists (its own ban list permits word-level reference) and records the path and sha, so the step is reproducible only where that file exists

## 8. What could not be closed

- **No legitimate marker change exists in this corpus.** 0 admitted rows out of 287 candidates. Producing a change register would have required either one source that observed both stages under one species/assay/condition, or a Stage-2 experiment; neither is available here, and the card is forbidden to train a predictor.
- **The `developing` and `unknown` stage cells carry no per-gene evidence** (the KB3 postnatal layer has published-label percentages only). They are registered as unobservable, not filled.
- **Three lineages have no fetal-stage markers at all in the corpus**: BC, glia (Müller/astro), RPE. Their developmental entries exist but are empty in the shipped panel.
- **The recognition measured here is window-composition sensitive** and, for the fetal side, partial: the default route names an adult class for a fetal window in 6 lineages, and only the advisory (or the explicit developmental route) says "developmental".
- **The repository's own recorded query-set panel does not reproduce at HEAD** (5 of 12 calls differ; classified in §7). This card did not cause it and did not attempt to repair it — repairing a fixture that belongs to another card's scope would be a silent cross-card write.
- The superseded v8 developmental panel exists only on the data mount, so the robustness pass is reproducible only where that file exists (path and sha256 recorded).

## 9. Inherited honesty notes (repeated wherever the artefacts are relied on)

- The `*_stage` columns of `plans/devline_ont_20261002/out/PRECURSOR_EDGES.tsv` are a **derived keyword rule**, not a native ontology attribute. Nothing in this deliverable promotes that column into the contract's `stage` field (rule R2 rejects exactly that, 40 times).
- The developmental panel is built from published labels and literature, not from a model we trained. A gene the build filtered out as a mature marker was **not** observed to be off in fetal tissue; that contrast is registered as raw material, not as a change.
- "Not mentioned" is never `off` (R10; 218 candidates rejected for exactly that).
- No marker direction is propagated along a multi-step lineage (R7). No cross-species or cross-stage cross-sections are stitched (R3/R4/R5/R6). Ageing appears nowhere: it is a third, orthogonal axis.
- Fetal is not adult even in the same tissue, and the two are never each other's reference; the developmental panel appears in no adult query path (gate G6).

## 10. Exact commands

```
cd /home/ubuntu/EYEKB_REPO/docs/plans/devlineage_20261021/stages
python3 scripts/01_stage_resolved_markers.py                       # stage-resolved tables
/home/ubuntu/training-venv/bin/python3 scripts/02_probe_recognition.py --pass 1   # probe, run 1
/home/ubuntu/training-venv/bin/python3 scripts/02_probe_recognition.py --pass 2   # probe, replay
/home/ubuntu/training-venv/bin/python3 scripts/03_robustness_probe.py# non-circular windows
python3 scripts/04_change_legitimacy_check.py                      # change rules + ledger
python3 scripts/05_boundary_register.py                            # boundary register
bash  scripts/07_net_audit.sh                                      # run-time network audit
python3 scripts/06_gate.py                                         # gate + readout
python3 scripts/08_report.py                                       # this report
python3 scripts/09_manifest.py                                     # MANIFEST.sha256
# the shipped service's own identity check, from the repository root
cd /home/ubuntu/EYEKB_REPO && python3 scripts/release_identity.py --check
# the repository's recorded query-set panel (run, for the record, with the SDK interpreter)
cd /home/ubuntu/EYEKB_REPO && /home/ubuntu/training-venv/bin/python3 tests/probe_tool_panel_identity.py --baseline tests/fixtures/tool_panel_baseline.json
```

## 11. Artefacts

| file | what it is |
|---|---|
| `out/ANCHORS.tsv` | every anchor with file + sha256 |
| `out/CANDIDATE_CHANGES.tsv` | 287 real + 6 fixture change candidates |
| `out/CHANGE_ADMITTED.tsv` | the admitted set (header only: the set is empty, reported as such) |
| `out/CHANGE_REJECTION_LEDGER.tsv` | every rejected candidate with the rules it broke |
| `out/NODE_KEYS.tsv` | 24 nodes with contract keys, CL match status and collisions |
| `out/OBSERVABILITY_BOUNDARY_REGISTER.tsv` | 61 lineage × stage cells with reasons and measurements |
| `out/PROBE_PLAN.json` | the frozen inputs, windows and the call list |
| `out/PROBE_RESULTS.json` | the real service output for all calls (pass 2) |
| `out/ROBUSTNESS_WINDOWS.tsv` | the non-circular window measurements |
| `out/RULE_REGISTRY.tsv` | rules R1–R11 with how often each rejected |
| `out/STAGE_COVERAGE.tsv` | per-lineage × stage marker counts and the one-stage-only findings |
| `out/STAGE_DISCLOSURE.tsv` | row-by-row disclosure of every non-adult value |
| `out/STAGE_LITERAL_SURFACE.tsv` | what the composition tool answers per stage literal |
| `out/STAGE_RESOLVED_MARKERS.tsv` | 269 marker assertions, one row per gene per node per stage |
| `out/VERDICTS.tsv` | one observability verdict per lineage with its measurements |

## 12. Two probe defects found and fixed during the run (disclosed, not hidden)

- **One adult counterpart was silently dropped.** A lineage can claim two adult classes (the glia entry claims MG and Astrocyte). Call ids keyed only by (lineage, side) collided, so the second counterpart's window was never sent. Found by reading the stored output and noticing one id where two were expected; fixed by putting the class into the call id. The pre-fix artefacts are kept verbatim in `out/prefix_artifacts/`.
- **The silent-adult-assignment flag ignored cross-library aliases**, so an answer such as `retina_interneuron::HC` counted as "not the adult class" when it is the same class from another library. The comparison now strips the `lib::` prefix. Both are secondary-flag corrections; no verdict rule was changed, and the frozen verdict rules were not re-tuned after seeing results.

## 13. Reproduce

```
# inputs, by hash
#   kb/baselines/fetal_development_transitions.json  2334d11ba169c034b75613d24b6b3ce38ee4b39efa2d37fdd917ff7249ad3300
#   kb/baselines/retina.json  25ffa795328589f24f554cd606ecdeb7c65f242af8d56c68c67f63a3a4d15619
#   kb/baselines/retina__fetal_developing.json  7fd8c3645247cbd88eecfad1ff13d3139db3df02eb4423ea4daf85bf0958377c
#   kb/markers/markers_v9_dev_retina.json  0b60cd127fc39482eca07d377bb80fcf15def02278a091ec7089ca29b983a775
# shipped service files probed
#   mcp_server/eyekb_core.py   5068a4a27b645d4ca16bc6c90ba6fb8bed8b02761fd056f5e7ec7de64d9063be
#   mcp_server/server.py        d127854bfeb08a65fcc3f513b006576cc17a7cb34e871e86cd7d1b8915bdf855
#   kb/markers/markers_v9_dev_retina.json  0b60cd127fc39482eca07d377bb80fcf15def02278a091ec7089ca29b983a775
#   kb/baselines/retina.json    25ffa795328589f24f554cd606ecdeb7c65f242af8d56c68c67f63a3a4d15619
```

Repository HEAD at the time of writing: `1cd3cf18b294a3e9dbfb52629d4bd72241092829` (this card's own commit is reported in the completion handoff; nothing was pushed).


# pipeline/ — batch annotation evidence entry point

Wires Phases A (steps 1–3) and B (steps 4–7) of the root README's **Standard workflow** onto your own dataset: **feed in one single-cell dataset, get per-cluster evidence reports plus a pending human-decision list.** This closes the last "open means usable" gap — the five-tool evidence server, the nine-step SOP, and example scripts were already in the repository, but the entry script that runs the five tools over your data cluster by cluster was not.

## Running it

```bash
# Format 1: .h5ad (X = raw counts; obs must let samples be distinguished)
python pipeline/run_pipeline.py --input data.h5ad --species human --tissue retina \
    --group-col treatment --out results/run1

# Format 2: a 10X triplet directory (the directory itself = one sample; a parent
# directory containing several triplet subdirectories = multi-sample)
python pipeline/run_pipeline.py --input 10x_dir/ --species human --tissue retina \
    --sample-group "S1=control;S2=case" --out results/run2

# Format 3: no species/tissue given — the S0 pre-check determines and backfills them (default behavior)
python pipeline/run_pipeline.py --input data.h5ad --out results/run4

# Input carries Ensembl IDs without a symbol column:
python pipeline/run_pipeline.py --input data.h5ad --species human --tissue retina \
    --ensg-map ensg2symbol.tsv --out results/run3
```

Key parameters: `--species` (`human|mouse|auto`, default `auto`) and `--tissue` (any tissue known to the dictionary — `--list-tissues` prints the list, e.g. `retina`, `fibrovascular_membrane`, `ocular_surface`…, default `auto`); with `auto`, the S0 gate decides, and an explicit value counts as a human override recorded as `s0_overridden_by_user` in the report. Group information via `--group-col` / `--sample-group` is what activates the disease-prior comparison. Full input requirements: root README, *Inputs and outputs*.

## S0 sample pre-check gate (enabled by default; shadow semantics in the current phase — never blocks)

Before Phase A, S0 runs first: three evidence channels (gene-ID composition, symbol-convention × marker cross-hits, composition scoring) automatically determine species × tissue, and six hard checks (species contradiction, insufficient tissue-score margin, out-of-domain, insufficient depth, suspected fetal material, etc.) each record an abstain on hit. **Phase 1 = shadow: abstention does not block the run** — the pipeline writes `s0_gate_report.json` + `REPORT_ABSTAIN.md` (record artifacts) and proceeds. Blocking enforcement belongs to a later phase, switched on via `EYEKB_S0_ENFORCE=1` (then abstain stops the run, fail-closed). Abstention is a legitimate reading, same principle as per-cluster abstention.

After the gate passes, structured known-claims consumption is triggered (`pipeline/pitfalls/`, see its README): the **risk flags** of entries applicable to the coordinate render into the evidence-report header (structured table only, no free text) and into the two columns `pitfall_risk_flags` / `pitfall_review_required` of `decisions_template.csv` (human decision reference; **no automatic rewriting of grades or ballots** — automatic relabeling/downgrade changes are permanently 0; entries with `answer_dependency` ≠ none open only after independent reading). Global fallback: environment variable `EYEKB_S0_GATE=0` restores the pre-wiring manual-parameter behavior (then `--species/--tissue` become required and no S0/flag artifacts are produced; used for baseline comparisons without the gate). Threshold overrides: `--s0-thr <json>`.

## Outputs (all under `--out`)

| File | Contents |
|---|---|
| `stage_a/processed.h5ad` | Matrix after QC filtering, normalization, batch correction (Harmony when ≥2 samples), doublet marking, Leiden clustering |
| `stage_a/figures/` | QC figures: mitochondrial fraction, gene detection, doublet scores, UMAP before/after correction |
| `stage_a/cluster_markers.csv` | Per-cluster Wilcoxon top-30 genes |
| `annotation_evidence_report.json` / `.md` | Five fields per cluster: top genes / `query_marker` candidates and scores / `get_tissue_composition` comparison (out-of-range flags) / `get_disease_prior` check (only with group labels) / `search_literature` passages + PMIDs; plus a mechanical confidence grade |
| `decisions_template.csv` | One row per cluster; the `decision` (accept/modify/abstain) and `proposed_label` columns are **left empty for the researcher to fill** |
| `mcp_calls.jsonl` | Audit trail of every evidence-service call (tool, arguments, success/failure, duration) |
| `s0_gate_report.json` | (When the S0 gate is on) full three-channel readings, gate rationale, override trail |
| `REPORT_ABSTAIN.md` | (Only on abstention) the stop-and-escalate record; at this point Phases A/B have not executed |
| `pitfalls_attention.json` / `pitfall_override_audit.jsonl` | (When the S0 gate is on) machine-readable attention list for the coordinate + per-entry audit of override suggestions |

## Three disciplines

1. **Zero-LLM by default.** The five tools are local deterministic retrieval: they emit evidence, not conclusions. The `--llm-assist` switch only calls a user-provided channel (read from the `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL` environment variables), is off by default, and even when enabled produces only a reference narrative without changing any cluster's grade. The repository ships no real keys or URLs.
2. **Abstention is a legal output.** The confidence grades in the report (`evidence_consistent` / `mixed_or_insufficient` / `needs_review`) are **pre-registered mechanical QC flags** — every triggering rule (`no_named_marker_candidates`, `composition_outside_baseline_range`, etc.) is written into the report and checkable cluster by cluster; they are not annotation conclusions, and the script never writes `needs_review` clusters as definite labels. The decision columns of `decisions_template.csv` are always filled by a human.
3. **No automatic scoring.** Consistent with the service-level red line in `mcp_server/`: evidence must never be converted into module scores / label weights / candidate-ranking scores / composite QC scores.

## Cross-species note (governed server-side; the pipeline does not bypass it)

The B5 cross-species governance of `query_marker` clears the named ranking for mouse-gene inputs (`no_named_ranking_for="mouse_input"`; candidates move to `unranked_candidates`). Those clusters are machine-flagged as `needs_review` / `mixed_or_insufficient` and the unranked candidates are presented as they are, for the researcher to read — this is by design, not a bug.

## Dependencies

`requirements.txt` pins the versions actually tested with this directory (Python ≥ 3.11, CPU is enough). Obtaining the vector model for literature retrieval and the fallback rules are as in the root README's *5-minute quickstart*; without a model, `search_literature` runs in lexical mode and reports the degradation explicitly; the other four tools are unaffected.

## Known boundaries

- Phase A default thresholds (min_genes=200, MT ≤ 20%, expected doublet rate 0.06, resolution 1.0) follow the tested workflow in this repository; all have command-line switches; there is no automatic tuning.
- The 10X triplet format carries no group information; supply it explicitly with `--sample-group "sample_dir_name=group;…"`.
- The disease-prior comparison is an evidence excerpt: the report presents the prior entries' textual mentions of the cluster's candidate cell types and the group-level proportions, without automatic "consistent/inconsistent" verdicts.

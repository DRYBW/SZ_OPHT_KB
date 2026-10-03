# KB2 RUN3 full-scale round record (2026-09-24, census of the 246-cluster main volume)

## Trigger chain
PI: "What is RUN3's direction?" → "You finished the whole exam already? No need to download anything further — just use the data we already have; go." —
This confirmed: ① before expanding the evaluation, take stock of the untested portion of the locally frozen data (result: only 45 of 305 clusters had ever been tested); ② zero downloads.

## Census numbers (kb2_roster_v3full.py)
Member × clusters with >=100 cells / anchors among them: Q1 16/5, Q2 27/5, Q3 16/5, Q4 40/5, Q5b 47/5, Q6 33/5, Q7 59/5, Q8 35/5, Q9 17/4; total 290/44 (246 new main-volume clusters).
Note: Q9 harmonized leiden_A has 21 clusters in total, 17 with >=100 cells — consistent with the "17 clusters" basis in the RUN1 report (17 is exactly the >=100-cell basis).

## Design artifact (frozen before execution)
RUN3_DESIGN_prereg.md: criteria — M1 agreement rate + kappa (baseline RUN2 28/45, 0.539) / M2 per-member ground-truth hits (baseline A26 B24 per 30) / M3 abstention-rate distribution (no passing line set) / M4 new disagreement hotspots → KB-gap candidates (report only; self-repair forbidden) / M5 anchor set — 44-cluster cross-surface flip rate. Stopping rules: a qwen batch failing 3 times is recorded as missing, never fabricated; if the surface sha changes mid-run = stop reading and refreeze.

## Model-channel selection (smoke-test criterion = non-empty content)
- A = qwen3.8-max @ LLM_CHANNEL LLM_CHANNEL.cn-beijing.LLM_CHANNEL/compatible-mode/v1 (key extracted via re.search from the `"name: LLM_CHANNEL"` section of the AGENT_ROLE config — MUST NOT appear on the command line)
- B = glm-5.1 (same channel). Eliminated: Agents-A1 (discovery-api site — the key in config is a redacted placeholder, unusable), deepseek-v4-pro (returns 200 but content='', reasoning consumed all max_tokens)
- Scale deviation written into the prereg: the runner script's card, with a ~2h capacity of about 45 rows, cannot carry 290 — so B switched from a session card to a cross-vendor runner; A=Qwen family, B=GLM family to preserve independence

## Script assets (reusable)
- scripts/kb2_roster_v3full.py: roster (Q1-Q8: clustering TSV leiden value_counts>=100; Q9: backed read of leiden_A)
- scripts/kb2_digest_full_v3.py: same mean-diff top25@HVG4000 as digest2, input swapped to the full roster, dual columns top_genes+top_genes_sym emitted directly; serial per-member del+gc for memory control (Q4 85K dense is the bulk; peak <30G). Pitfall: take n_cells directly from ncmap[c]; never write a len(c) fallback (string length is wrong)
- scripts/kb2_mcp_v2.py v2.2: env KB2_GENES selects input, KB2_FACE_TAG selects output; reuses the entire RUN2 collection chain with zero modification
- annotation/run_annotator_run3.py <model> <stem>: generic reading runner (5 clusters/batch, <=3 retries, .run3_{stem}_done.json breakpoint, empty content falls back to reasoning_content, META records the face sha16) — A and B each run as independent processes
- scripts/kb2_bscore_v4.py: v3 with the run2_→run3_ output prefix (the scorer is copied and re-prefixed each round; overwriting the previous round's artifacts is forbidden)

## Pipeline orchestration
digest (~8min) -> MCP collection (290 × ~3.5 calls) -> SLIM_v3full freeze sha -> A/B parallel blinded reading (58 batches each × 20-60s) -> bscore v4 -> disagreement table + anchor-set flips -> WIKI completion. Background chaining + notify; the two sides' breakpoint files are naturally isolated by stem.

## Results (to be appended when the round finishes)
- M1-M5 readings:
- New lexicon-gap candidate list:
- Lessons backfilled:

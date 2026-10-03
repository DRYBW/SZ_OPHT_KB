# KB2 RUN-series ledger and channel details (2026-09-24)

## LLM_CHANNEL (LLM_CHANNEL) channel
- base_url: `https://LLM_CHANNEL.cn-beijing.LLM_CHANNEL/compatible-mode/v1` (OpenAI-compatible)
- Usable key: the api_key of the `name: LLM_CHANNEL` entry in the AGENT_ROLE profile config.yaml (sk-sp- prefix, stored in full, usable); the key of the `name: LLM_CHANNEL` entry (LLM_CHANNEL) is **stored redacted** in the config ("sk-b21...12c2") and is unusable by scripts
- The model list can be checked live via GET /v1/models: includes qwen3.8-max / qwen3.8-flash / glm-5.1 / kimi-k2.6 / deepseek-v4-pro, etc.
- **Pitfall: align the model name the PI uses with the channel first.** Instance: "qwen3.8MAX" was understood as the local LOCAL_LLM's Qwen3.8-27B-NVFP4 (:PORT), while it actually meant **LLM_CHANNEL's qwen3.8-max** ("if you don't know, ask the other agents and you'll find out" — scanning provider/model in each profile config gives the answer)
- qwen3.8-max enables the chain of thought by default: batch tasks MUST carry `enable_thinking:false`, otherwise large-output requests hit read timeouts (>540s)
- Responses carry reasoning_content; do not pick models whose content comes back empty (e.g., the deepseek-v4-pro smoke test)

## Reading-surface / artifact file lineage (/mnt/D/EyeKB/plans/evalset/)
```
digest/genes_part.json                 # 45-cluster r2 fixed surface (before the dual-column schema)
digest/EV_DIGEST_SLIM{,_v2,_v3,_v3full}.jsonl   # per-round reading evidence cards (all shas in the ledger)
digest/ERRATA_SOURCE_FIX_SHA_LOG.txt   # unified sha ledger (surfaces/readings/merges appended per round)
digest/exam_roster_v3full.json         # RUN3 full roster (≥100 cells, 290 clusters)
annotation/ANN_{A,B}*.jsonl            # per-round per-slot reading artifacts (slot filenames stay scorer-compatible; human/model changes go in README/META, not filenames)
annotation/ANN_A_pi_VERBATIM_Q9.md     # PI human reading as-is + transcription mapping (slot-provenance pattern)
annotation/.qwen_*_done.json           # runner breakpoint files
scoring/{,run2_,run3_}object_B_summary.json / *_table.tsv / disagreement_table.tsv
scripts/kb2_digest2.py / kb2_mcp_v2.py / kb2_slim_v2.py / kb2_bscore_v{2,3,4}.py
EVAL_RUN*_COMPLETED_*.md               # per-round deliverables (RUN3_DESIGN_prereg.md carries the scale-deviation declaration)
```

## Script essentials
- `annotation/run_annotator_run3.py <model> <stem>`: generic LLM blinded-reading runner (5/batch, 3 retries, resume from breakpoint; A/B independent processes, mutually invisible). Qwen-family models automatically carry enable_thinking=false; empty content falls back to reasoning_content
- `scripts/kb2_mcp_v2.py`: evidence-surface collector, env `KB2_GENES` (input genes_part name) + `KB2_FACE_TAG` (output `EV_DIGEST_{TAG}.jsonl`, default v3 to keep frozen surfaces from being overwritten); **v2.2 dual-column schema** (top_genes original IDs + top_genes_sym side column)
- `scripts/kb2_bscore_v4.py A_file B_file`: round-prefixed outputs (the convention is to copy v3 and change to the run3_ prefix — one copy per round with a new prefix; never modify shared files)
- Hotspot method, one-liner: `t[(t.ident_equal)&(t.matchA==False)&(t.matchB==False)&(t.truth_frac>=0.7)]` → aggregate by truth to inspect class concentration

## Human PI reading package, MSG_PLATFORM distribution format (validated on the RUN1 Q9 batch)
- Each batch = one member's 5 clusters; card face: cluster_id + cell count / top 20 genes / KB hits
- Stated up front: the grade table (A = use with caution / B = strong transcriptomic signal + alternatives excludable / C = doubtful), "insufficient evidence is a legitimate answer", plain-language replies suffice ("Q9::0 = inflammatory macrophage, C")
- The project maintainer transcribes to JSONL (why compressed to ≤40 characters; the original wording goes into the VERBATIM artifact); **PI readings go to an independent LLM review before the PI's final ruling is returned** — the QA loop fixed in this round

## RUN3 key numbers (comparison anchors for the next round)
Agreement 63.8% / kappa 0.622 / ground-truth zone A 60% B 70% / Q5b hardest (0.42/0.47) / hotspots 23 = BC11+AC6+HC2 / anchor-set flips 8/40
Repairs in flight: t_c12cb349 (KB5 interneuron panel, acceptance = hotspot offline self-check ≥15/23), t_89d02fde (Q2::18 truth-mapping audit)

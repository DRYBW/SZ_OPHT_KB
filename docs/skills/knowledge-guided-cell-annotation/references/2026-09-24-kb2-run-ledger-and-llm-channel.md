# KB2 RUN 系列台账与通道细节（2026-09-24）

## LLM_CHANNEL（LLM_CHANNEL）通道
- base_url: `https://LLM_CHANNEL.cn-beijing.LLM_CHANNEL/compatible-mode/v1`（OpenAI 兼容）
- 可用 key：AGENT_ROLE profile config.yaml 里 `name: LLM_CHANNEL` 条目的 api_key（sk-sp- 前缀，全文存储可用）；`name: LLM_CHANNEL` 条目（LLM_CHANNEL）的 key 在 config 里**脱敏存储**（"sk-b21...12c2"），脚本不可用
- 模型清单可 GET /v1/models 实查：含 qwen3.8-max / qwen3.8-flash / glm-5.1 / kimi-k2.6 / deepseek-v4-pro 等
- **坑：PI 口中的模型名先对齐通道**。实例：说"qwen3.8MAX"被理解成本地 LOCAL_LLM 的 Qwen3.8-27B-NVFP4（:PORT），实际指**LLM_CHANNEL的 qwen3.8-max**（"你不知道的话问下其他的agent就知道了"——扫各 profile config 的 provider/model 即得）
- qwen3.8-max 默认开思维链：批量任务必带 `enable_thinking:false`，否则大输出请求读超时（>540s）
- 返回体含 reasoning_content；content 为空的模型（如 deepseek-v4-pro smoke）不要选

## 判读面/产物文件谱系（/mnt/D/EyeKB/plans/evalset/）
```
digest/genes_part.json                 # 45 簇 r2 修复面（双列前）
digest/EV_DIGEST_SLIM{,_v2,_v3,_v3full}.jsonl   # 各轮判读证据卡（sha 全入账）
digest/ERRATA_SOURCE_FIX_SHA_LOG.txt   # 统一 sha 台账（面/判读件/合并件按轮追加）
digest/exam_roster_v3full.json         # RUN3 全量名册（≥100细胞 290 簇）
annotation/ANN_{A,B}*.jsonl            # 各轮各槽位判读件（槽位文件名保评分器兼容，人/模型变更写 README/META 不写文件名）
annotation/ANN_A_pi_VERBATIM_Q9.md     # PI 人类判读原话+转录映射（槽位溯源范式）
annotation/.qwen_*_done.json           # runner 断点文件
scoring/{,run2_,run3_}object_B_summary.json / *_table.tsv / disagreement_table.tsv
scripts/kb2_digest2.py / kb2_mcp_v2.py / kb2_slim_v2.py / kb2_bscore_v{2,3,4}.py
EVAL_RUN*_COMPLETED_*.md               # 各轮收口件（RUN3_DESIGN_prereg.md 含规模偏差声明）
```

## 脚本要点
- `annotation/run_annotator_run3.py <model> <stem>`：通用 LLM 盲判 runner（5/批、重试3、断点续跑、A/B 独立进程互不可见）。qwen 系自动带 enable_thinking=false；content 空回退取 reasoning_content
- `scripts/kb2_mcp_v2.py`：证据面采集器，env `KB2_GENES`（输入 genes_part 名）+ `KB2_FACE_TAG`（输出 EV_DIGEST_{TAG}.jsonl，默认 v3 防覆盖冻结面）；**v2.2 双列 schema**（top_genes 原 ID + top_genes_sym 旁列）
- `scripts/kb2_bscore_v4.py A_file B_file`：轮次前缀输出（复制 v3 改 run3_ 前缀=惯例，每轮复制一份改前缀，勿改共用件）
- 热点法一行版：`t[(t.ident_equal)&(t.matchA==False)&(t.matchB==False)&(t.truth_frac>=0.7)]` → 按 truth 聚合看类别集中度

## 人类 PI 判读包 MSG_PLATFORM 分发格式（RUN1 Q9 批实证）
- 每批=一成员 5 簇；卡面：cluster_id+细胞数 / top 基因 20 个 / KB 命中
- 明示：等级表（A 慎用/B 转录强+可排除/C 存疑）、"证据不足合法"、大白话回复即可（"Q9::0 = 炎性巨噬，C"）
- 协调者转录 JSONL（why ≤40 字压缩，原话进 VERBATIM 件）；**PI 判读后送独立 LLM 评审再回呈裁定**是本轮定型的 QA 环

## RUN3 关键数字（供下轮对比锚）
一致 63.8% / kappa 0.622 / 真值区 A 60% B 70% / Q5b 最难(0.42/0.47) / 热点 23=BC11+AC6+HC2 / 锚卷翻转 8/40
在途修复：t_c12cb349（KB5 中间神经元面板，验收=热点离线自检≥15/23）、t_89d02fde（Q2::18 truth 映射审计）

# 脱敏双扫描报告 — 2026-09-27 REPOSYNC

范围：docs/wiki（14 件）+ docs/skills（两套 skill 镜像 + protocols 3 件）+ docs/plans（判读层 1439 件）+ mcp_server（4 件代码）。
规则三元组 = project-github-export 现行清单同源（R01–R16 编号见下表），本轮新增面：二手渠道商端点串、第三方作者邮箱、本地代理端口、内部 agent 角色名。
**本报告不复现任何渠道商名/裁决商名/端点串**——规则名一律以代号+语义描述，全量映射留在本地脱敏器脚本与 git commit message（仓外）。

## 规则代号表（命中数）

| 代号 | 语义 | 标签 | 命中 |
|---|---|---|---|
| R01 | 自家 DR 样本编号 | OWN_MOUSE_DR_DATASET | 2 |
| R02 | IM 会话 ID 前缀形态 | CONTACT_ID | 0 |
| R03 | 工作机主机名 | HOST | 0 |
| R04 | 渠道商 A（中文俗称）及端点/裸别名（token-plan 类字样） | LLM_CHANNEL | 44 |
| R05 | 渠道商 B（.fan/.fun 双域名系） | LLM_CHANNEL | 2 |
| R06 | 渠道商 C（俗称+数字端点） | LLM_CHANNEL | 14 |
| R07 | 渠道商 D（intern 域） | LLM_CHANNEL | 2 |
| R08 | 外部裁决 LLM 别名（含裁决商 A$_ 前缀文件名；词边界防误伤 astrocyte 类子串） | REVIEWER_LLM | 353 |
| R09 | IM 平台名（企微系） | MSG_PLATFORM | 7 |
| R10 | 密钥形态兜底（sk-/github_pat_/gh*_/PRIVATE KEY） | REDACTED_SECRET | **0** |
| R11 | 本地 LLM 栈名 | LOCAL_LLM | 1 |
| R12 | 内部 agent 角色/profile 名 | AGENT_ROLE | 29 |
| R13 | 第三方联系邮箱（论文通讯作者，API 缓存内） | CONTACT_EMAIL | 259 |
| R14 | 内部服务端口（仅散文类生效） | PORT | 1 |
| R15 | 本地代理端口（仅散文类生效；tsv/json/jsonl 数值证据面不触碰，防破坏可复算数字） | PORT | 4 |
| R16 | 会话标识形态（session/conversation/chat/trace id） | SESSION_ID | **0** |

## 文件名扫描（改名 21 件 + 1 目录）

- knowledge-guided skill 引用件 1 份：文件名含渠道商 A 字样 → `<…>-llm-channel.md`（与 09-25 首导出仓内同名件对齐，内容刷新至 09-26 版）
- kb9_ocs_20260927 五轮送审件 17 份（PROMPT/REPLY/send.log）：文件名裁决商前缀 → `REVIEWER_LLM_*`；正文引用同步替换，改名后引用与文件名逐一对应
- kb9 脚本原名含 R08 词干 → `REVIEWER_LLM_xhigh.py`；out/recheck 留痕件 6 份同规则
- 目录 `docs/plans/sync_<profile名>_scSOP_20260927` → `sync_scSOP_20260927`（profile 名不落目录面）

## 零命中兜底（红线复查）

- 密钥形态（R10）：**0**；IM chat_id（R02）：**0**；主机名（R03）：**0**；会话标识（R16）：**0**（票档 toolcalls 实测仅 ts+tool+args+结果摘要，无会话字段）
- 患者/DR 衍生数据：镜像面内 0 个 csv/percell/patient 文件；>5MB 大表与 raw 缓存目录整体未入镜像（体积与再生产方式见主 README 附录）
- PI 原话：directive/简报中 PI 引语按原话保留（脱敏仅替换账号/渠道/邮箱形态，未删语句）

## 幂等验证

替换后二次全规则扫描：0 命中、0 改名（各标签不与任何规则模式再匹配）。

## 冻结哈希锚例外登记（重要）

- `docs/plans/btest_20260927/BTEST_PREREG_v1.0.md` 有 2 行经 R04/R12 脱敏（卡归属与通道字样）。
- 其 sidecar `BTEST_PREREG_v1.0.md.sha256` **保持原样未重写**：其中哈希锚定的是线上原件（`/mnt/D/EyeKB/plans/...`，已实证 sha256 相符）。预注册锚不可被镜像方改写。
- 因此在本镜像内执行 `sha256sum -c` 对该件**预期 FAIL**——这是脱敏差异，不是篡改。原件完整性以线上盘/证据包为准。

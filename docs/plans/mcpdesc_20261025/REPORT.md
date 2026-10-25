# MCPDESC 20261025 — 说明串与随件语料口径对齐（卡 t_2a047be0）

口径令执行：与同类/已发表文章相同的统一标准（本卡为工程对齐卡，判据全部「机器可查」，无统计口径面）。
闸 0（可辨识性）：不适用（无统计终点）；闸 0b（引数溯源）：全文数字均给出复算命令。

## 0. 结论

服务描述串已从「写死发射代数字」改为「import 时现读随件语料 build 记录」，并落机器门 G11（六检查、rc 0/2/3、双向证明）。一字节破坏即可让门挂（A1/A2），恢复后字节恒等、门复绿；无语料影子根行为 = INCONCLUSIVE 且 fallback 仍被 pointer 钉住。一键链 9 门全绿（G3 dense 41/41 … G11 6/6）。

## 1. 溯源登记（交付 1：旧数字来自哪）

2,713 papers / 174,616 passages = `rag_dbs.v2.0_2026-09` 块的登记值（kb/literature_db/EYEKB_DB_POINTER.yaml：
该块明载 `chunks: 174616` / `unique_papers: 2713`），即 v2.0_2026-09 语料的真实规模；
该块 role 注释明确「served as the search_literature built-in corpus before 2026-10-01, now handed over to v2.4.2」。
2026-10-01 内置语料切换 v2.4.2（switch 卡 t_b94d0999；pointer v2.4.2_2026-09 块 role: default，
unique_papers 3869 / chunks 242928；随件 build_stats.json 同值）。说明串是发射代残留，未随切换更新。
D 侧运行时入口同源残留另行登记（见 §6）。

复算：`grep -n "174616\|2713" kb/literature_db/EYEKB_DB_POINTER.yaml`（v2.0 块）；
`python3 -c` 读 `literature_db/v2.4.2_2026-09_slim/build_stats.json` 键 n_papers/n_chunks（或 `python3 mcp_server/corpus_stats.py` 不可用时的等价读取）。

## 2. 说明串改前/改后逐字对照（交付 2）

改前（server.py:104，PRE sha 040d99baf3956b210a0324c6db3b571fd8cac1a8ba8b086a0a144e4886dcf052）：

    description=("Ophthalmic knowledge base for cell-type annotation. (1) Literature retrieval over a "
                 "bundled corpus of 2,713 papers / 174,616 passages covering the whole eye; each result "

改后（现值，sha 23549a2dd6faad27dbf75fbae44ab2cd4e5c7de879747d48ee9aa0998dc72740）：

    description=("Ophthalmic knowledge base for cell-type annotation. (1) Literature retrieval over a "
                 f"bundled corpus of {corpus_stats.BUNDLED_CORPUS_LINE} covering the whole eye; each result "

渲染结果（training-venv 真实 import，HAS_OLD=False）：`...a bundled corpus of 3,869 papers / 242,928 passages covering the whole eye; each result carries PMID, ...`。

同文件同性质残留一并对齐：search_literature 工具 docstring 的 `db: empty = the bundled v2.0_2026-09 corpus` 改为
实际解析链描述（EYEKB_DB_DIR → pointer role:default → bundled v2.4.2_2026-09_slim）。

现读来源与键名（写死退路的注明，交付 2 要求）：mcp_server/corpus_stats.py，
`BUILD_STATS_REL = literature_db/v2.4.2_2026-09_slim/build_stats.json`，键 `n_papers` / `n_chunks`；
fallback 常量 `FALLBACK_PAPERS = 3869` / `FALLBACK_CHUNKS = 242928`（来源文件 + 键名 + pointer 等值注册在模块注释内）。
fallback 仅在语料文件未解包（fresh clone，G2 Release 资产）时生效。

## 3. 机器门（交付 3）：tests/gate_mcpdesc_corpus.py = G11

六检查（全 fail-closed；rc：0=PASS / 2=FAIL / 3=INCONCLUSIVE）：
G11-C01 STATS-SOURCE；C02 RENDER-NO-HARDCODE（描述子句禁内 baked 数字 + 旧代数字不得回归 server.py）；
C03 RENDER-MATCH（渲染值 == 随件 build_stats.json）；C04 FALLBACK-IDENTITY（fallback == pointer v2.4.2 登记值，
role: default 必须仍是 v2.4.2 块）；C05 POINTER-AGREE（随件 build 记录 == pointer 登记值）；C06 SELF-TEST（植桩形状必被自身比较器抓到）。
已入一键链 tests/run_gates.sh（C07 登记 = docs/GATE_INVENTORY_G5G6.tsv G11 行，sha 90e1a5820ab7…）；
契约条目 = docs/VERIFY_CONTRACT.md §5.6；所有权台账行 = docs/W3_PIPELINE_REGISTRY.tsv L6-48（门）+ L1-33（模块）。

## 4. 反向控制（交付 4）：错→挂 / 对→绿 双向证明（真实树）

| # | 动作 | 证据（out/） | rc |
|---|------|--------------|----|
| A1 | 说明子句硬编码错一位（3,859 / 242,918，合法语法字面） | G11_SABOTAGE_A1.json，C02 点名子句 | 2 |
| A1× | 恢复（/tmp/mcpdemo_bak 字节副本回写，sha256sum 相等） | G11_GREEN_AFTER_A1.json | 0 |
| A2 | fallback 错一位（FALLBACK_PAPERS=3860） | G11_SABOTAGE_A2.json，C04 点名失配对 | 2 |
| A2× | 恢复（5de5e966d9ac… 字节恒等） | G11_GREEN_AFTER_A2.json | 0 |
| A3 | 影子根（无语料资产，纯 copy 不 move） | G11_SHADOW_INCONCLUSIVE.json：C01/C03/C05=INCONCLUSIVE、C04 仍 PASS | 3 |

破坏前源件 sha 备案：server.py=23549a2dd6fa…，corpus_stats.py=5de5e966d9ac…（out/POST_IMPL_SHAS.txt）。

## 5. 链与注册面读数

- 一键链（最终轮，EYEKB_G3_PY=/home/ubuntu/.conda/envs/pipeline_env/bin/python）logs/run_gates_after2.log：
  G3 41/41 dense PASS、G4 3/3、G5 8/8、G6 21 检查 PASS、G7 6/6、G8、G9、G10、G11 6/6 —— **CHAIN PASS rc=0**。
  （首轮 run_gates_after.log 的 G3=INCONCLUSIVE / G7=FAIL 为解释器前提所致的非结果，非本卡削弱；G6 首轮 3 项 = 本卡实例行措辞，
  按 R5/R6/R7 判据修正后 PASS，全程无既有判据改动。）
- 注册面：GATE_INVENTORY 更新（G11 行新增 + G2 行 sha 重取）；REGISTRY 更新（L6-01 sha/bytes/mtime 重取 + L1-33、L6-48 新行）；
  G5 复算 rc=0（143 行/11 门；SHA-MATCH 0 失配）。
- release identity：staged tree 同 commit 重取（python3 scripts/release_identity.py --take --source index；--check rc=0 复算见 §7）。
- 工具面板身份对拍（预期变化面披露）：PANEL_PRE.json vs PANEL_POST.json —— 12 调用中 11 逐字节恒等；
  唯 1 变动（get_kb_page scope=index）归因并发卡 t_44d29ac9（CORPUSONE，pi-chief）commit 2335beb（10:51:00）对
  kb/vk_literature_index/INDEX.md 的对齐（`git show --stat 2335beb`：3 文件 7 插入，与本病卡文件集零重叠）。

## 6. 禁静默丢弃登记（未修项与原因分类）

1. D 侧运行时入口 /mnt/D/EyeKB/mcp_server/server.py 同样携带旧代数字（其 description 为另一代文本："v2.0 whole-eye-bank
   174,616 chunks / 2,713 papers"）。分类=交付权威在仓侧（MIRROR_AUTHORITY_RECORD / USER_DIRECTIVE_20261012 §D1），
   运行时副本随下一次 mcp_server 镜像同步承接本修正；本卡不动 D 侧运行时（红线：冻结件不回改 + 运行面归另有通道）。
2. 面板基线 tests/fixtures/tool_panel_baseline.json 维持 t_c19cd667 的 RED-by-design 状态（本卡不重录；
   与 §5.5 的遗留条款一致——该器件本就按记录保持 RED）。
3. run_gates.sh 头注释「G3 -> G4 -> G5 -> G6」文字滞后于实际 9 门（既有文本，非本卡判据件；未改，避免与本波无关的字节扩散）。

## 7. 协调者复算入口（逐节点）

    cd /home/ubuntu/EYEKB_REPO
    python3 tests/gate_mcpdesc_corpus.py                                   # expect rc=0, 6/6 PASS
    bash tests/run_gates.sh                                                # EYEKB_G3_PY 未设时 G3=rc3（见 §5）；带解释器：
    EYEKB_G3_PY=/home/ubuntu/.conda/envs/pipeline_env/bin/python bash tests/run_gates.sh   # expect CHAIN PASS
    python3 scripts/release_identity.py --check                           # expect rc=0
    sha256sum -c docs/plans/mcpdesc_20261025/out/POST_IMPL_SHAS.txt       # 改定字节仍恒等
    git show --stat HEAD                                                   # 本波逐文件清单

## 8. 改动清单

新增：mcp_server/corpus_stats.py；tests/gate_mcpdesc_corpus.py；本证据目录 docs/plans/mcpdesc_20261025/。
就地修订：mcp_server/server.py（description 子句 + docstring + import）、tests/run_gates.sh（挂 G11）、
docs/VERIFY_CONTRACT.md（§5.6）、docs/GATE_INVENTORY_G5G6.tsv（G11 + G2 sha 重取）、
docs/W3_PIPELINE_REGISTRY.tsv（L6-01 重取 + L1-33 + L6-48）、docs/CHANGE_CONTROL_G6_INSTANCE.tsv
（CHG-20261025-MCPDESC-ALIGN 行）、docs/RELEASE_IDENTITY.json（staged tree 重取）。
红线执行：零下载、零 GPU、零 move（影子根全 copy）、冻结件零回改、本地 commit 不 push（推由协调者统一执行）。

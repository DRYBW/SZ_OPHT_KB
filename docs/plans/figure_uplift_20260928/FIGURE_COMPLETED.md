# FIGURE_COMPLETED — SZ_OPHT_KB 仓面图片升级（t_00a3ed6b，2026-09-28）

PI 原话："github 里面那个图也太丑了……你至少放一个我们项目跑的好看的图吧"。
执行按协调者建议案：②髓系亚群图上封面、③compartment+doublet 质检图并列、①旧 v1 图转 legacy 留痕。

## 变更清单

| 项 | 仓内路径 | 来源（只读，copy 不 move） |
|---|---|---|
| 新增封面图 | `figures/umap_myeloid_sub.png` | `/mnt/D/EyeKB/plans/demo_gse165784/proc/v2/figs_v2/umapmyeloid_sub.png`（v2_o2_myeloid 脚本 L146 产物，髓系亚群 UMAP：Microglia/Macrophage/Mono/DAM-LAM） |
| 新增质检图 | `figures/umap_compartment_doublet.png` | 同目录同名（v2_o1o3_harmony_scrublet 脚本 L206 产物，compartment + doublet 打标） |
| v1 转 legacy | `figures/v1_legacy/umap_cluster.png`、`figures/v1_legacy/umap_sample.png` | 仓内 `git mv`（字节不变，留痕；README 不再引用） |
| 来源脚本收录 | `docs/plans/figure_uplift_20260928/scripts/v2_o1o3_harmony_scrublet_20260923.py`、`v2_o2_myeloid_20260923.py` | demo 目录原件逐字节 copy；未入顶层 `scripts/`（该面 = 线上 `scripts/` 字节镜像口径，混入会破坏对账表），改随 plans 层 |
| README | 四层体系地图节顶部新增"体系跑出来长什么样（demo 真产物）"小节：②封面 + ③并列 + 两行图注（含 demo 性质=WIKI 口径、禁疗效/临床结论声明） | — |
| sha 台账 | `docs/recon/RECON_figures_20260928.tsv` | 6 行（2 图 + 2 脚本 + 2 legacy 位移件），源↔仓 sha256 全 MATCH/MOVED-UNCHANGED |

## 五门结果（全 PASS 后 push）

- **F1 png 完整性**：PIL open+load 4 件全过（685×431 / 1239×431 / 694×431 / 1290×431，bytes 均 >0）；sha 台账如上入 `docs/recon/`。**PASS**
- **F2 MCP 回归零行为漂移**：staging 副本（基线 b85c006）与修改后副本分别起真 stdio MCP，沿用 `tests/probe_repo_mcp.py` + `probe_repo_mcp2.py`（副本仅改 SRV 路径行，断言集逐字一致）；PRE vs POST diff=空 → probe1/probe2 双 ZERO-DRIFT；`diff -rq` 实证 `mcp_server/` 与 `kb/` 相对收卡基线**字节零变动**（本卡承诺不动两面）。**PASS**
- **F3 README 图片路径实证**：`![..](..)` 提取 2 条 → `figures/umap_myeloid_sub.png`、`figures/umap_compartment_doublet.png` 均 EXISTS。**PASS**
- **F4 脱敏复扫 0 命中**：v3 引擎 `--scan`（docs/wiki·skills·plans + mcp_server 面，含新收 2 脚本）= 文件名改名 0 / 规则命中 0 / 命中文件 0；补充面：figures+新目录文件名 FN_PAT 复扫 0；两 PNG 二进制 strings 无 `/home/`、`/mnt/`、主机名残留（元数据仅 Matplotlib Software 块）；README 新增行 16 类规则 grep 0。**PASS**
- **F5 git 分层**：基线 main=`b85c006`；三个 commit 分层 = ①figures 层（两图入仓 + v1→legacy + 两脚本 + sha 台账）②README 层 ③收尾件层（本文档）。**PASS**

## 改判指引（PI 可随时换图）

候选池 = `/mnt/D/EyeKB/plans/demo_gse165784/proc/v2/figs_v2/`（demo v2 真产物 11 张）：
- ④分样本备选：`umap_sampleA/B.png`、`umapmyeloid_sample.png`（本轮未入仓）
- marker 签名备选：`umapmyeloid_sig_{Microglia,Mac_DAM_LAM,Mac_Tissue,Mono_Classical,APC_MHCII_high}.png`
- 整合前后双轨：`umap_track{A,B}.png`

改判操作（单文件替换即可）：从 figs_v2 拷新图 → `figures/`（沿用英文语义文件名）→ 改 README 对应 `![](...)` 行 → 重跑 F1（PIL+sha 台账追加行）与 F3（路径实证）→ 分层 commit + push。图注事实描述需随图更换（数据集 GSE165784 / demo v2 定性句不动）。

## 大文件与镜像口径

两图 192KB/222KB（<500KB 无碍，照旧规则）；线上 `/mnt/D/EyeKB` 全程只读零写入；Release 资产面无涉。

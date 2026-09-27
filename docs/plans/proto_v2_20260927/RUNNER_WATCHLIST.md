# RUNNER_WATCHLIST — 投票实现 runner 落点盘点（PROTO 卡 t_03808fff，只列不改）

- 性质：**盘点件**。本卡零脚本改动、零生产写；下一波各 run 的 warmup 卡**照单分叉**（v2=C2b run 需替换计票函数；v1=C4 run 原样沿用）。
- 票规定义指针：v2=/mnt/D/OcularKB/WIKI/PROTOCOL_VOTING_v2_C2b.md；v1=C4 现行=下表各 `consensus()` 逐字。
- 盘点日期：2026-09-27；sha256 为本日实测。
- 结构事实：六个三席裁决脚本的 `consensus()` 体**逐字同构**（Counter 多数制），差异仅在 `ballot()` 的 grade∈{A,B} 过滤与 UNDET/COARSE 弃规——这正是 C2b 的两个改动点。

## 1. 三席现行 runner（v2 生效需分叉的对象）

| # | 面 | 脚本（绝对路径） | sha256 | 计票函数落点 | norm_identity 来源 |
|---|---|---|---|---|---|
| R1 | RUN4-r | /mnt/D/EyeKB/plans/evalset/scripts/run4r_verdict.py | 7c32e0c60d596c2e…b224bc (完整见§4) | `ballot()` L22-27；`consensus()` L29-39；票规措辞另见文件头 docstring L6 + RUN4R_PREREG.md (sha dfa4a6c9…) | exec-head 复用 kb2_bscore_v4_truthfix_t_2ae2610d.py L93 |
| R2 | RUN5 | /mnt/D/EyeKB/plans/evalset/scripts/run5_verdict.py | 234c592fbefcece2…456201 | `norm_identity()` L78-（内联）；`ballot()` L89-97；`consensus()` L100- | 内联 |
| R3 | RUN6-B | /mnt/D/EyeKB/plans/run6b_20260926/scripts/run6b_verdict.py | 69ecca818abc0661…3229e7 | `norm_identity()` L75-（内联）；`ballot()` L86-94；`consensus()` L97- | 内联 |
| R4 | RUN7-RG | /mnt/D/EyeKB/plans/run7rg_20260926/scripts/run7rg_verdict.py | cd3577ff4bb359e3…1e121b | `ballot()` L31-36；`consensus()` L38-49 | exec-head 复用 kb2_bscore_v4_truthfix_t_2ae2610d.py L93 |
| R5 | FACEV21 | /mnt/D/EyeKB/plans/face_v21_20260926/scripts/facev21_verdict.py | 4a467fee05676ded…dfe48 | `ballot()` L37-42；`consensus()` L44- | exec-head 复用 kb2_bscore_v4_truthfix_t_2ae2610d.py L93（头注 L4 自述"与 run7rg 同源"） |
| R6 | KB9 | /mnt/D/EyeKB/plans/kb9_ocs_20260927/scripts/k8_verdict.py | 41cb11b13ea83df8…452b8f | `norm_identity()` L73-81（内联）；`ballot()` L83-91；`consensus()` L94-104 | 内联 |

三席 runner 共用口径（= v1=C4）：定名票 grade∈{A,B} 且非 UNDET/COARSE 才计票；`Counter` 多数制，≥2 席同名定名；无票=abstain3、三票各异=split3、单有效票=tie。

## 2. 历史/参考落点（**不在分叉范围**）

| # | 面/用途 | 脚本 | sha256 | 说明 |
|---|---|---|---|---|
| H1 | RUN4（2 席历史面） | /mnt/D/EyeKB/plans/evalset/scripts/run4_verdict.py | 90c97a88f2f6f609…8b24 | 无 `consensus()`；R1 严格=双判 match 且 grade∈{A,B}（C 弃权级不算修复）。历史冻结件 |
| H2 | 真值归一上游 | /mnt/D/EyeKB/plans/evalset/scripts/kb2_bscore_v4_truthfix_t_2ae2610d.py | d1833425c746330a…c0e990 | `norm_identity()` L93；R1/R4/R5 exec-head 的共享头——若 crosswalk 归一（决策件 §4.3）落地，动这里=同时动三个 runner，**须单独立卡** |
| H3 | C2b 参考实现 | /mnt/D/EyeKB/plans/tiep_20260927/scripts/t1_revote.py | d321e793144e2795…32495 | `c4_consensus()` L48（C4 逐字复刻，已对账）；`parse_ballot()` L35-47（kind/label/coarse 三态解析）；`rule_c2(bs, count_coarse)` L86（C2a/C2b 合一，count_coarse=True=C2b）。**分叉时的语义基准，勿动原件** |

## 3. 分叉指引（供下一波 warmup 卡；本卡不执行）

- v2 run 分叉=两处最小改动（对照 §1 各表行号）：① `ballot()` 去掉 grade∈{A,B} 过滤（grade C 定名票入数）；② COARSE 票按 `coarse:` 后标签入 Counter（H3 `parse_ballot`/`rule_c2` 为等价性基准）。
- 分叉后**必须**跑 H3 `c4_consensus` 对旧面回归：v2 改动不得改变任何既有"已定名且正确"结论（OVERTURN=0 性质）；新增定名簇自动进 P2 污染检查。
- KB9 面警示：票面 8/33 簇沿用 RUN5 存档票（TIEP §5.3）——分叉重算时混合票面继承 RUN5 grade 习惯，报告须标注。
- 平票残余=S1 破平禁用：分叉实现**不得**引入 n_shared_decon/S1 破平或单票确认（决策件 §1.4）。
- 每 run 预注册必写票规版本行（决策件 §2.2）：`票规版本: v1=C4` 或 `v2=C2b`。

## 4. sha256 全值

```
7c32e0c60d596c2ec99798e45744fb32b80d29e9cbef5d53fd877610bfb224bc  evalset/scripts/run4r_verdict.py
234c592fbefcece241ca9801272acafa52524de9c7fe83524e88f6ab7c456201  evalset/scripts/run5_verdict.py
69ecca818abc0661d70014ae83f3a5034b3f9dc0eb2b37ec25ec0fc9692329e7  run6b_20260926/scripts/run6b_verdict.py
cd3577ff4bb359e31288ca17f613dad6956999515def157b6634896dda1e121b  run7rg_20260926/scripts/run7rg_verdict.py
4a467fee05676ded888da5f2a61a1a0532a4e96ee7a82f2ab94dc51aa61dfe48  face_v21_20260926/scripts/facev21_verdict.py
41cb11b13ea83df839e83c67e5a11e24da965a396898ac16c42ac94542452b8f  kb9_ocs_20260927/scripts/k8_verdict.py
90c97a88f2f6f609eceab450f976843c939a889adc85f6e5dbfc3f7d20aa8b24  evalset/scripts/run4_verdict.py
d1833425c746330ac5c66e8367ef9e9046f0645e2149fb9e76786b5192c0e990  evalset/scripts/kb2_bscore_v4_truthfix_t_2ae2610d.py
d321e793144e2795d0270addcfbc851c430b46501cefc35ebaaeb960ec932495  tiep_20260927/scripts/t1_revote.py
dfa4a6c9af71b8e40b6dd85a20412c7e4bfd1c56fd9679aae3e81fad1c68c0b1  evalset/RUN4R_PREREG.md
```
（相对路径基准=/mnt/D/EyeKB/plans/）

## 5. 已知边界（盘点未覆盖项，如实声明）

- btest（D9）runner 尚未落盘（plans/btest_20260927/ 现仅 BRIEF_BTEST.md，PREREG 待预注册）——其 C4 主读+C2b 并列计票函数由该卡 warmup 自带，按 §3 指引落双计票即合规。
- OcularKB 侧 `p2_step5_verdict.py`、`M31_T120_w8_equiv_verdict.py`、`gate_reverdict_v1_2_20260916.py` 名字含 verdict 但**非判读票计票**（M3 模型/门控裁决），不入分叉范围。

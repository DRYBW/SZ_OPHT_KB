# D8 疗效重考双系列实录（2026-09-25 夜，RUN6-B 眼表 + RUN7-RG 视网膜 22 靶）

## RUN7-RG（t_09ca801c，plans/run7rg_20260926/）
- 预注册：RUN7RG_PREREG.md sha `2cab65e2…`（sha 落纸先于构建；只读输入 11 件起跑前后两轮 sha 复核未变）
- 面：45 簇（22 靶=RUN4-r 原靶一字不改 + 23 对照=RUN3 双判对簇），v6 词条+FACE_V2 证据面（2B 优先占位窗+3A 旗）；三席=qwen3.8-max/glm-5.1/deepseek-v3.2 温度 0.2 全部重跑
- 结果：**R1=17/22 PASS**（基线 15/22，+2：Q4::15、Q5b::13——恰为 RUN4-r 三票分裂残余，归因预言第二次验证；丢失 0）；**R2=4/23 FAIL**（≤1 门破）：Q5b::2 被 3A 描述旗引发降级弃权 / Q7::52、Q7::58 被 v6 跨物种 ranking 噪声带偏 AC / Q4::23 v6 RPE 词条命中引入新谱系冲突集体弃权
- Q2::22 反向验证落冻结矩阵分支 `repair_ineffective_for_cluster`：主跑无共识（三席 1 定名票），删词条+hint 后反而 2/3 票回 MG——误导源在基因集先验（GLUL/VIM/CLU 歧义共表达），非仅词条
- **MCP 激活切换建议=阴性**；face v2.1 三修补点（新预注册待 PI）：(a) 3A 旗加"禁用作降级依据"指令行或撤旗 (b) Q7 跨物种簇撤 v6 ranking 或加 ortholog 回证 (c) RPE×BC 冲突簇 resolution 判序细化；预期保 +2 增益
- 防移动球门：本文档不追加协议再测；与 RUN4-r PASS 并列归档逐簇归因回 PI

## RUN6-B（t_6951c807，plans/run6b_20260926/）
- 框架：Q6_VOCAB2_TRUTH_HIERARCHY_PREREG_v1.0（sha 800d5db1…零触碰）+执行配置冻结 RUN6B_FACE_SPEC.md（sha c9fbda97…）+新面 sha 206badfa…（FACE_V2 切片+v6 眼表词条命中层，生产 MCP stdio query_marker library=face_v6 实况 47 次调用留日志）
- 三席同 RUN5 同温同 prompt（禁换人换模型），33/33×3 零缺失
- 结果：**P1=22/33**（基线 21/33，Δ+1：词条补位翻正 4、C 席词表外跟票+粒度歧义翻丢 3）；**P2=1/33 擦线 PASS**——违例仍是 Q6::24，mural 软提示三席全见仍未拦 SMC 接管
- 软提示真实流量首测（只报不裁）：mural 触发 8/33（全间质/壁细胞簇）；rod_bc 0/33（face_v6 无 Rod/BC 结构性，如实报禁调阈值）；note 可见票改判 10/24 与无 note 对照区间噪声同级；引用率 23/24（含粒度注记通道混淆 caveat）；簇×席全量矩阵 99 行=softflag_followup_table.tsv
- 副产品：v6 眼表面 ranking 空率 19/33 vs RUN5 老 43 类面 9/33（空=不给误导先验但带宽窄），影响已在 P1 迁移记账

## 状态与待决定
- 激活保持阴性=现行口径；等 PI：①face v2.1 拆弹重考放行 ②软提示升硬（强制复核步骤/并入投票）还是止步写进 M1 讨论节 ③基因先验歧义开新线 or 记账
- directive 落 USER_DIRECTIVE_20260925_eyekb_downstream_batch.md 追加四（D8）；INDEX 09-25 深夜条有当日 21 卡总账

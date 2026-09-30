# BRIEF_KB9ACT — 案 A k9_ocs overlay 激活切换（PI 2026-09-30 放行 OB-5）

## 放行依据（逐字继承，禁扩权）
- PI 原话（2026-09-30，WeCom）："按照我们现有的数据，能够全部激活的就激活……验证之后确实可以的那就可以直接上传"
- 证据基座：docs/plans/obligrun_20260928/VERDICT_OBLIGRUN_v2.md = READY（OB-1..4 全清、P1 26/33≥24、P2 strict 0/33）+ out/ACTIVATION_READINESS.md 建议票
- **范围锁定**：仅案 A（k9_ocs 规则 overlay + 增量词条由 OFF 转生效）。v2.4/v2.4.1 RAG 默认切换**明确不在本卡**（门③ FAIL 在册）；face/v6 已激活勿动；泪腺维持禁活。

## 动作（生产盘 /mnt/D/EyeKB 侧）
1. 激活前 sha 台账：kb/markers 两件 overlay（_k9_ocs_rules_overlay_v1.json / markers_k9_ocs_increment.json）+ server/core 相关件 + 现役响应基线（选定 8 个探针查询的 ON/OFF 双态响应存 pre/）
2. 按 overlay 文件内 activation 开关条款执行切换（机制=装条时预置的开关，env/配置级可回退=A5 纪律；禁改规则内容本身）
3. ON 态验证探针（自建断言不复用装条卡）：①案 A 词条参与 query_marker ranking（目标细胞类上位）②非案 A 簇响应与 OFF 基线逐字节全等（外溢=0，抽 22 视网膜簇回归集）③黄金 41 逐位（tests/verify_repro.py 同口径）④泪腺查询维持硬禁不变
4. A5 回退件：切回 OFF 后与 pre/OFF 基线机读全等（回退演练必做一遍，留 on→off→on 或 off→on→off→on 序列日志）
5. 跟票观察登记：仿眼表 v6 条款——激活后一周采样窗口，异常即回退；把采样口径写进 plans/kb9_act_20260930/OBSERVE_NOTE.md
6. 措辞纪律：对外口径=工程验收达标激活，**禁写独立验证/疗效提升**；READINESS 四条限制（开发集同源/C2b 语义跃迁/chen_* source 未解析/下游登记）原样进激活记录
7. 产物落 /mnt/D/EyeKB/plans/kb9_act_20260930/：ACTIVATION_RECORD.md（含前后 sha 台账+探针输出+回退演练日志）；完成落卡

## 领地
可写：kb/markers overlay 开关态、logs、plans/kb9_act_20260930/
禁写：kb/composition（COMPV1X 卡领地）、mcp_server 代码、evalset 冻结面、RAG 目录
禁 push（仓侧同步由协调者在复核后走 REPOSYNC）。完成或遇阻必须落卡。

# OB-2 v2.1 机械重算附注（t_c145db7c run142，案A细则3）
- 输入面 kb9_face_v2.1.jsonl（sha 2c0649dc…）；行数=57（v1=57）。
- 硬断言 post_shield top3 == v2.1 面 kb_marker_ranking：33 簇全检，失败=0 例 []
- 31 未涉簇零变化对照 + 2 变化簇对照：delta=zero 57/57 行；非零漂移 0 行 []；v1 行缺失=0 []
- 说明：诊断表输入=簇 top10 基因×库 marker 集（ranking 臂），lit 字段不进入诊断计算；案 A 仅动 lit（2 行删除）且 ranking 逐字节不动 → 全表预期零漂移，实测一致则「零漂移断言」成立。
- 指定对照簇 Q6::8 / Q6::26（v2.1 重算）：
  Q6::8: T n_raw=1 n_shielded=0 n_remaining=1 rank 1→1 top3=True [n_remaining>0:Y|top3:Y] delta=zero
  Q6::26: Mac_DAM_LAM n_raw=2 n_shielded=0 n_remaining=2 rank 2→1 top3=True [n_remaining>0:Y|top3:Y] delta=zero
  Q6::26: Mono_Nonclassical n_raw=1 n_shielded=0 n_remaining=1 rank 3→2 top3=True [n_remaining>0:Y|top3:Y] delta=zero
  Q6::26: APC_MHCII_high n_raw=3 n_shielded=3 n_remaining=0 rank 1→ top3=False [n_remaining>0:N|top3:N] delta=zero
  Q6::26: cDC2 n_raw=1 n_shielded=1 n_remaining=0 rank 4→ top3=False [n_remaining>0:N|top3:N] delta=zero
- Q6::26 型掏空回退指认（v2.1）：
  Q6::6: Mac_DAM_LAM 掏空（raw_hits=['FTH1']）
  Q6::11: APC_MHCII_high 掏空（raw_hits=['CD74', 'HLA-DRB1']）
  Q6::11: pDC 掏空（raw_hits=['TCF4']）
  Q6::2: Mono_Classical 掏空（raw_hits=['S100A8', 'S100A9']）
  Q6::3: Mono_Classical 掏空（raw_hits=['S100A8', 'S100A9']）
  Q6::25: Mac_DAM_LAM 掏空（raw_hits=['APOE']）
  Q6::26: APC_MHCII_high 掏空（raw_hits=['CD74', 'HLA-DRA', 'HLA-DRB1']）
  Q6::26: cDC2 掏空（raw_hits=['HLA-DRA']）
  Q6::30: Mono_Classical 掏空（raw_hits=['S100A8', 'S100A9']）

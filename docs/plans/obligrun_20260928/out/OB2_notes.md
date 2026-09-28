# OB-2 附注（t_c145db7c，PREREG §6 OB-2）
- 硬断言 post_shield top3 == 票面 kb_marker_ranking：33 簇全检，失败=0 例 []
- 指定对照簇 Q6::8 / Q6::26 逐簇免疫候选行：
  Q6::8: T n_raw=1 n_shielded=0 n_remaining=1 rank 1→1 top3=True [n_remaining>0:Y|top3:Y]
  Q6::26: Mac_DAM_LAM n_raw=2 n_shielded=0 n_remaining=2 rank 2→1 top3=True [n_remaining>0:Y|top3:Y]
  Q6::26: Mono_Nonclassical n_raw=1 n_shielded=0 n_remaining=1 rank 3→2 top3=True [n_remaining>0:Y|top3:Y]
  Q6::26: APC_MHCII_high n_raw=3 n_shielded=3 n_remaining=0 rank 1→ top3=False [n_remaining>0:N|top3:N]
  Q6::26: cDC2 n_raw=1 n_shielded=1 n_remaining=0 rank 4→ top3=False [n_remaining>0:N|top3:N]
- Q6::26 型"证据被掏空"回退指认（n_shielded>0 且 n_remaining=0 的免疫头部）：
  Q6::6: Mac_DAM_LAM 掏空（raw_hits=['FTH1']）
  Q6::11: APC_MHCII_high 掏空（raw_hits=['CD74', 'HLA-DRB1']）
  Q6::11: pDC 掏空（raw_hits=['TCF4']）
  Q6::2: Mono_Classical 掏空（raw_hits=['S100A8', 'S100A9']）
  Q6::3: Mono_Classical 掏空（raw_hits=['S100A8', 'S100A9']）
  Q6::25: Mac_DAM_LAM 掏空（raw_hits=['APOE']）
  Q6::26: APC_MHCII_high 掏空（raw_hits=['CD74', 'HLA-DRA', 'HLA-DRB1']）
  Q6::26: cDC2 掏空（raw_hits=['HLA-DRA']）
  Q6::30: Mono_Classical 掏空（raw_hits=['S100A8', 'S100A9']）

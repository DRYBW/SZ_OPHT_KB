# T3 README 增量复跑实证 — REPOSYNC2
# 断言1: 版本注记含 09-28 改进波段
  段存在: True
# 断言2: v2.4/v2.4.1 描述零'已激活/已上线'（含 docs/wiki）
  违例: 0 命中
# 断言3: 附录A 新行仓内指针件逐件 ls 实证
  缺失: 0（全部存在）
# 断言4: 附录A 再生产命令可执行性（本卡收录面 py 全量 compile；外部输入件存在性=线上盘核验）
  新波 py 全量 compile: n=64 fail=0
  外部输入 /mnt/D/OcularKB/data/GSE164403/GSE164403_annotated.h5ad: 存在(附录A指称成立)
# 断言5: §五 新表行数与 README 宣称一致
  RECON: {'MATCH': 103, 'DESSENS-VERIFIED': 4, 'PRIOR_DESENS(c4a8f53 注释级脱敏, 协调者已批; 09-28 表逐字全等复核于本卡)': 1} total: 108 == 108: True
  INTAKE entries: 768 == 768: True
  INTAKE -c: OK

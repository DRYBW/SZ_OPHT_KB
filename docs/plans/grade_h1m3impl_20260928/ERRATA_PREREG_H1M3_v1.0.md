# ERRATA_PREREG_H1M3 v1.0（卡 t_e0f94d4f，2026-09-28 15:2x）

- 对象：/mnt/D/EyeKB/plans/grade_h1m3impl_20260928/PREREG_H1M3.md（sha 14fc3f8f0bb64b9f…，开算前冻结，原件**不回改**）
- 缺陷：§2 冻结预期表 RUN6A 行"named 23→23"为**手抄笔误**；锚件真值=**24→24**
  （grade_anchor/data/counterfactual_summary.json H1-M3 行 RUN6A：named_base=24, named_cf=24；
  本卡实测 out/g1_perarchive.tsv RUN6A 行=24->24 match=True，其余 8 档抄录全对）。
- 影响裁定：**门1 有效性零影响**——PREREG §2 白纸黑字定义"对照件=同目录 counterfactual_summary.json"，
  g1 脚本逐档比对对象即该冻结锚件（非手抄表），9/9 全字段一致+合计 24/7/0/0+22/24 全过；
  手抄表仅为人类可读快照，其单格笔误不改变开算前已冻结的判据。
- 处置：按"历史冻结件不回改、勘误增量落纸"惯例（errata-source-fix 纪律），本件为 v1.0 增量登记件；
  REPORT_H1M3 §5 已加引用行。禁后续任何轮以本笔误为由重开 G1。

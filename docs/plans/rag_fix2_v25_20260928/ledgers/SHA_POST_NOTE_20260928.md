# SHA_POST 复核 2026-09-28 (RAGFIX2 t_6848d3de) — 冻结面零改动证明
# 对 ledgers/SHA_PRE_inputs_20260928.txt 逐项 sha256sum -c: 8/9 OK
# 唯一预期差异 = EYEKB_DB_POINTER.yaml (本卡领地内设计变更, 两步):
#   step1 pointer_register2.py 纯追加 v2.4.1 块: assert post.startswith(pre) PASS
#     pre  sha256  = 12a4462eaf819ce535fce77ddcaaa324fdf08c72584ccbb4ebc550436a1270e0
#     after-append = 286663df6c5a837c4bf94f71d3f8cd80292c35df900b4d6e87af7da8e237c9f7
#   step2 本块内文字两处修正 (未触任何既有行): gate_status 文案补齐(7备选/CPNE5副产品注记+①②)
#     与 whitelist_ledger 行内冒号转"="(修 yaml.safe_load 解析); 修正后实测:
#     final sha256 = c7f2e0f7d583cfc56ce8bfb821b0517513e81316e416b55ecd0aa30d1f6e15c7
# v2.4.1 块之后无任何行; v2.0-v2.4 库四件/前卡增量 chunks/闭集/两 INERT 旁挂件: 零改动
# (PRE 全清单见 SHA_PRE_inputs_20260928.txt; -c 复核原始输出见 git-less 台账=本说明+SHA_DELIVERABLES)

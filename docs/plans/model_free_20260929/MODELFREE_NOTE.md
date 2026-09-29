# 零模型可选化（2026-09-29，PI："如果整个项目完全不需要模型就好了"）

## 改动
- stage3_retrieve.py：模型目录三级查找（EYEKB_MODEL_DIR env > 仓内 models/bge-large-en-v1.5 > 旧绝对路径），全无则检索自动降级纯词法 lexical_fallback（确定性 stable 排序、可复算、返回体带 retrieval_mode/degraded/note 三字段明标降级）。
- db 缺失时报人话错误+README 指引（原为裸 traceback）。
- dense 主路径（模型可得）代码逐行保留，sort 参数逐位不变。

## 验证（本机实测）
1. 黄金 41 题（模型在位）：REPRO PASS 41/41 top5 逐位全等 —— 锚零漂移。
2. 零模型模拟（EYEKB_MODEL_DIR=/nonexistent）：INFO 指引 + lexical_fallback 出结果，microglia/retina 查询 top3 均为小胶质细胞 scRNA 真相关文献（38409074/38585235/36088481）。
3. MCP 面：eyekb_core 透传同一 stage3 源，单实现两处生效；模型缺失时 4 个 kb 工具本就零模型，search_literature 走同一降级分支。

## 依赖面变化
- 零模型用户：只需 numpy/pandas/pyarrow（+mcp 可选）——无 torch、无 sentence-transformers、无 HF 下载。
- 官方同款 dense：仓内 models/ 放 bge-large-en-v1.5（Release 附件可选）或 env 指路径。

## 待 PI 拍板的更大方案（本卡未动）
"整仓永久去模型"（golden 41 重建词法版锚、历史 RUN 数字定性为 dense 口径旧档、删 st/torch 依赖与模型附件）——属球门层决定，须 PI 点名+历史裁决口径注记，不在本次可选化范围内。

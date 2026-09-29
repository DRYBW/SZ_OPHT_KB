# KB2 RUN3 全量轮实录（2026-09-24，主卷 246 簇普查）

## 触发链
PI："RUN3 方向？"→"你考卷都考完了？不用下了，用已有数据就可以了，去做吧"——
确认了：①扩评测先盘点本地冻结数据的未考部分（结果：305 簇里只考过 45）②零下载。

## 普查数字（kb2_roster_v3full.py）
成员×>=100细胞簇/其中锚：Q1 16/5、Q2 27/5、Q3 16/5、Q4 40/5、Q5b 47/5、Q6 33/5、Q7 59/5、Q8 35/5、Q9 17/4；合计 290/44（主卷 246 新簇）。
注：Q9 harmonized leiden_A 全量 21 簇，>=100 细胞 17——与 RUN1 报告"17 簇"口径吻合（17 即 >=100 口径）。

## 设计件（先于执行冻结）
RUN3_DESIGN_prereg.md：判据 M1 一致率+kappa（基线 RUN2 28/45、0.539）/ M2 真值逐成员命中（基线 A26 B24 每30）/ M3 弃权率分布（不设及格线）/ M4 新分歧热点→KB 缺口候选（只报告禁自修）/ M5 锚卷 44 簇跨面翻转率。stopping rules：qwen 批 3 败列缺失不伪造；面 sha 中途变=停判重冻。

## 模型通道选定（冒烟判据=content 非空）
- A = qwen3.8-max @ LLM_CHANNEL LLM_CHANNEL.cn-beijing.LLM_CHANNEL/compatible-mode/v1（key 从 AGENT_ROLE config "name: LLM_CHANNEL" 段 re.search 提取，禁进命令行）
- B = glm-5.1（同通道）。淘汰：Agents-A1（discovery-api 站 config 里 key 是脱敏占位不可用）、deepseek-v4-pro（200 但 content=''，reasoning 吃光 max_tokens）
- 规模偏差写进 prereg：执行脚本 卡 2h 容量约 45 行撑不了 290，B 从会话卡改跨厂商 runner；A=Qwen 系 B=GLM 系保独立性

## 脚本资产（可复用）
- scripts/kb2_roster_v3full.py：名册（Q1-Q8 clustering TSV leiden value_counts>=100；Q9 backed 读 leiden_A）
- scripts/kb2_digest_full_v3.py：digest2 同款 mean-diff top25@HVG4000，输入换全量 roster，双列 top_genes+top_genes_sym 直出；串行分成员 del+gc 控内存（Q4 85K dense 是大头，峰值 <30G）。坑：n_cells 用 ncmap[c] 直取，勿写 len(c) 兜底（字符串长度是错的）
- scripts/kb2_mcp_v2.py v2.2：env KB2_GENES 选输入、KB2_FACE_TAG 选输出，全量复用 RUN2 采集链零改动
- annotation/run_annotator_run3.py <model> <stem>：通用判读 runner（5 簇/批、<=3 重试、.run3_{stem}_done.json 断点、空 content 回退 reasoning_content、META 记 face sha16）——A/B 各跑独立进程
- scripts/kb2_bscore_v4.py：v3 的 run2_→run3_ 输出前缀版（评分器每轮复制改前缀，禁覆盖上一轮产物）

## 管道编排
digest(~8min) -> MCP 采集(290x~3.5 调用) -> SLIM_v3full 冻结 sha -> A/B 并行盲判（各 58 批 x20-60s）-> bscore v4 -> 分歧表+锚卷翻转 -> WIKI 完成。后台链式 + notify；双侧断点文件按 stem 天然隔离。

## 结果（待本轮跑完追加）
- M1-M5 读数：
- 新词表缺口候选清单：
- 教训回填：

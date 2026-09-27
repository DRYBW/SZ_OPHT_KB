# BRIEF_REPOSYNC — SZ_OPHT_KB 整仓对齐"可克隆运行四层系统"标准（PI 纠正定性 2026-09-27）

## 项目定性（PI 原话依据："缺skill和mcp啊，你还是没懂我们eyekb的项目是做什么的"）
本仓=EyeKB **MCP-RAG-Wiki-Skill 四层体系的完整镜像交付物**：任何人 clone 后配好依赖即可起 MCP 服务、查 KB、按 README 拉 Release 的 RAG 资产恢复语料、用 skills 复现判读与评测流程。不是文档备份，不是快照存档；"本地没改"≠"仓里最新"。

## 已实证缺口（协调者 09-27 盘上核对）
1. mcp_server/server.py=**KB1v2-0.3-kb7wire 旧版**（线上 0.4-actv6）；**calllog.py 整文件缺失**（留痕层）。
2. docs/skills 仅 2 个镜像（annotation-eval-ops / knowledge-guided-cell-annotation），且为 09-26 版；判读协议件 ANNOTATION_PROTOCOL 与票规 v2 决策件未镜像。
3. WIKI 镜像停在 09-26 晚 directive 两件——INDEX/当前状态/结论速查 09-26 深夜→09-27 全部条目、scoring_wave directive（含追加一/二）、红线追加节（操作定义）、PROTOCOL_VOTING_v2_C2b.md、AUDIT_SOP_v1.0 全缺。
4. 09-27 十五卡判读层（evidence_scoring/e2_decontam/e3_rescue/e2r/btest/tiep/pme×2/kb9×3/proto 的 VERDICT/PREREG/判读表）零镜像。
5. README 无"clone 后跑起来"路径（依赖、stdio 启动、EYEKB_ACT_V6 开关、client 注册示例、RAG 分卷合并+sha256 校验步骤）。

## 任务（staging 副本法，全程不触线上）
1. 建 staging 副本，按上述五块逐项同步最新版；kb/ 100 文件与 mcp 代码同步后**逐文件 sha256 对线上清单**（对账表进仓）。
2. plans 判读层收录口径：md/json/tsv 判读件全进；data/ 大表（>5MB 的 tsv/jsonl 面件、npz）不进仓、在 README 附录列"体积与再生产方式（脚本+输入 sha）"；票档 annotation/*.jsonl 进（判读可复算的最小充分集）。
3. **脱敏双扫描**（文件名+内容，规则三元组照 project-github-export skill 现行清单）：重点新增面——btest/kb9 票档与日志含LLM_CHANNEL/LLM_CHANNEL通道串与会话标识、directive 含 PI 原话（原话保留但不含账号信息）、calllog 含 pid/路径；命中一律按标签替换，扫描报告随 commit 留痕。
4. README 重写为"四层系统运行指南"：依赖（scrnaseq env anndata 0.13.2 注意点、pipeline_env 不兼容声明）、MCP stdio 注册样例、env 开关矩阵（EYEKB_ACT_V6/softflags 三态）、RAG v2.3 Release 分卷下载合并+sha256 核验命令、评测复算入口（各卡 scripts/ 链路指针）。
5. Release 资产（v2.3-rag-assets 六件）**不动**——RAG 语料侧核实线上自 09-25 打包后未变（各卡 sha 台账），若发现变动如实报告不擅自重传。
6. push 走 PORT 代理（配方见 skill）；commit 分层（代码/文档镜像/判读层/README）便于回滚。
7. 产出 REPOSYNC_NOTE.md：缺口→处置→对账表→脱敏命中统计→遗留（"下次结构变更后重同步检查项"清单，供未来收口卡继承）。

## 红线
- copy 不 move，线上 /mnt/D/EyeKB 与 /mnt/D/OcularKB 全只读；不传任何患者/DR 项目数据；密钥形态兜底扫描必跑；完成或遇阻必须落卡。
- 工作目录：/home/ubuntu/EYEKB_REPO（既有仓本地副本，先 fetch 核对远端状态再动）；staging 在其旁新建，勿原地改。

## 增补（PI 09-27 指令："你测试过再更新上传哈"）——push 前测试硬门
**顺序改为：staging 同步 → 仓副本自测全绿 → 测试报告进仓 → 才允许 push。任何一项不过，不 push，block 上报。**
1. **MCP 起服自测**：对 staging 副本（非线上）起真 stdio 服务，跑黄金回归子集+三态探针（ON/OFF/开关回退），断言与线上现行为一致；原始输出落 tests/mcp_selftest.log 进仓。
2. **README 步骤复跑**：按新 README 从零走一遍（含依赖安装说明的可用性与 RAG 分卷合并+sha256 校验命令），每步截图级留痕 tests/readme_walkthrough.log；文档步骤与实际行为不符即修文档再跑。
3. **评测脚本抽跑**：evals/ 至少 2 个回归脚本对 staging kb/ 副本实跑通过。
4. **RAG 资产一致性**：Release v2.3 六件本地重合并 → sha256 对账线上 EYEKB_RAG_v2.3.tar（只验不动 Release）。
5. tests/ 目录（脚本+两份 log）随仓 commit；REPOSYNC_NOTE.md 增加"测试门"节逐项 PASS/FAIL。
6. worker 自测全绿后落卡；**协调者将另行独立探针复测后方视为"已测试上传"**（PI 验收铁律，自报不作数）。

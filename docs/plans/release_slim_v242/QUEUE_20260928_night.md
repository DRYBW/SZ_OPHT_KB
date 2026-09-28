# 夜间任务队列（2026-09-28 落，防上下文压缩丢单——任何会话接手先读此件）

## A. 在跑（kanban pi-briefing 板，三卡，watcher proc 已挂）
- t_5d18900e SEURATPROBE：registry 标准集双轨探针；降级条款=装机>1GB 停卡报批 / 试点不达标 NO-GO 回落 scanpy 单轨。收口后报三数字。
- t_db0c8206 DISC_QANT：供体翻否杠杆+深度位移量化 → 勾选表+三档阈值（D-2/D-3 纪律落地）。
- t_fa03e1d7 DISC_COMP：EXPECTED_COMPOSITION_v0 组成先验面（D-1，默认 OFF）。
- 收卡验收铁律：读原件核数字+协调者自探针，不以 worker 自报代测试。

## B. RELEASE 瘦身线（PI 拍板 fp16 档=我推荐、PI 追问后确认语义；本地 fp32 原件冻结零触碰）
1. [进行中] 转换：chunks.parquet embedding 列 float32→float16（fixed_size_binary 2048B/行），产出 /home/ubuntu/RAG_SLIM_V242/literature_db/v2.4.2_2026-09_slim/；text(77MB)与全部元数据列原样保留（证据面展示依赖 text，不留=功能残缺）。体积目标 ≈555MB。
2. [待做] 服务侧适配（向后兼容双格式分支）：clients/ocularkb/rag/scripts/stage3_retrieve.py 的 np.stack 处加分支（bytes/memoryview → np.frombuffer float16 reshape(1024) astype float32）。只改仓副本，不碰 /mnt/D 生产文件（生产仍用 fp32 库）。
3. [待做] 三层质量验证（球门零移动）：①数值层=随机 2000 query 指纹对比 fp32 全库 vs slim 的 top1 一致率/Spearman；②黄金 41/41 off 态对 v2.4.2 fp32 基线逐字全等；③门②retina gate + 门③覆盖 87/92=94.6% 复算不回退。任何 top5 漂移=如实报，回退档再议。
4. [待做] 打包：tar（v2.4.2_2026-09_slim 目录）+ sha256 + split 192M 分卷（预计 3 卷+sha 件）；manifest/release note 写明"fp16 派生件+精度声明+原件不在仓（本地冻结在 /mnt/D/OcularKB/.../v2.4.2_2026-09，sha 台账见 pointer）"。
5. [待做] README 顶部"5 分钟跑通"卡片（PI 已批）：clone→pip 依赖→起 stdio 服→gh release download v2.4.2-rag-assets→拼接→sha256 -c→解包→指针 path 改一行→search_literature 通。数字用实测体积。
6. [待做] skills 镜像增量同步（攒了三轮：OBLIGRUN 节/RAG 三层验收法节/新 reference activation-obligation-run-20260928.md + 本地新改动）：cp→v4 脱敏引擎→T7 自家 token 扫描→commit。
7. [一次设备码全办] push（B5+B6 的 commit）→ 建 Release tag v2.4.2-rag-assets（draft→上传 6 件→publish）→ gh api 核 size/state=uploaded + release note sha + 下载最小件 cmp。设备码流走 project-github-export 技能铁律：curl 双通道、user_code 键名、轮询 background、TOKEN_OK 后勿 kill、一次性 token 落盘文件捞回法。
8. [验收] 新鲜拉取全链复跑一遍才算"下载了就能用"（README 卡片命令逐条实测，不是转述）。

## C. 等 PI 的（不开工，只等点名）
- k9_ocs 眼表 4 词条激活批否（义务 run READY 26/33 建议票在 ACTIVATION_READINESS.md）。
- int8/PQ 更激进的档位：不推荐不重提（fp16 已选）。

## D. 定时已在轨
- cron 10-03 09:00 A2 跟票周报；cron 10-05 09:30 B5 全大写误拒 T+7 复核（零误拒报平安，>0 报明细+建议 B4）。

## E. 常驻红线
- >1GB 下载需 PI 批准；敏感自家数据 token 扫描每 push 前跑（命中即剔）；不动其他窗在跑进程；重计算 systemd-run MemoryMax；GPU=qwen 独占勿碰。

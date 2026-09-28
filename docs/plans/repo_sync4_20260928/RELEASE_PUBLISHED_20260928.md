# Release 落地回执 — v2.4.2-rag-assets（2026-09-28）

## 事实链（服务端为准，非本地自报）
- push: `cf254ab..a0ad857 main -> main`（REPOSYNC4 三锁契约 commit，GitHub 服务端回执 PUSH_OK）
- Release: tag `v2.4.2-rag-assets`，id=398380962，draft=false（PATCH 回执含 "draft": false）
- 资产×3（API 回读 state=uploaded）：
  | 资产 | 字节 |
  |---|---|
  | EYEKB_RAG_v2.4.2_slim.tar.part_aa | 201,326,592 |
  | EYEKB_RAG_v2.4.2_slim.tar.part_ab | 196,917,248 |
  | EYEKB_RAG_v2.4.2_slim.tar.sha256 | 92 |
- 本地完整性：`cat part_* > tar; sha256sum -c` → OK；tar sha256 = `95a3359c35c2943415bd54a779c84692bab3b40ecd416be5b1fc3485f9c63bbb`（与 Release notes 登记一致）；两 part 之和=398,243,840=tar 本体 ✓

## 卫生
- OAuth token 用后即焚（脚本 line 93 os.remove，已确认文件不存在）；全程零打印密钥。
- 一次性 device_code 竞态教训：双启发布器会抢 token 兑换——重跑前必须先杀旧实例。

## 待办（下一授权窗顺路，非阻塞）
- T6 补跳：真·异机模拟 = fresh clone + 从 GitHub 下载 Release 资产 + 解包 + verify_repro 41/41（本地已验到拼接+哈希级；私有仓下载需再授权 30s）。
- 建议（供 PI 拍板）：为只读自动化配 fine-grained PAT（repo+downloads 只读）存 credential store，免逐次扫码。

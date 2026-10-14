# 仓内门清单（人读版，G5G6 卡新增；机器版=`GATE_INVENTORY_G5G6.tsv`）

> 与既有三锁 G1/G2/G3 并列；sha256 逐门实取（本文件由 `scripts/gen_g5g6_assets.py` 同源生成，禁手抄）。
> 判据/期望输出的权威源=`docs/VERIFY_CONTRACT.md`（既有四门）+ `docs/VERIFY_CONTRACT_G5G6.md`（新增两门）。

| 门 | 名称 | 入口命令 | 判据 | 期望输出 | 实取 sha256（前 16） |
|---|---|---|---|---|---|
| G1 | 环境锁（依赖钉版） | `pip install -r requirements.repro.txt` | 依赖按 requirements.repro.txt 钉版安装；模型固定 BAAI/bge-large-en-v1.5 | pip install 成功（无版本告警） | `8c0af43f9fa83281…` |
| G2 | 数据锁（唯一官方语料通道） | `下载 Release 资产 v2.4.2-rag-assets → sha256sum -c` | 只认 Release 预建语料资产；sha256sum -c 通过才允许解包 | sha256sum -c 逐行 OK | `02eec500f215052c…` |
| G3 | 检索验收（41 查询 top5 逐位） | `python3 tests/verify_repro.py --db-dir <corpus>` | 41 查询 top5 PMID 逐位一致（tests/REPRO_EXPECTED.json） | `REPRO PASS: 41/41`、rc=0 | `53ced2bf7815ae6b…` |
| G4 | 字节锚（三件锚 + 解释器钉死） | `python3 tests/verify_pipeline.py` | 三件锚逐字节一致（解释器钉 pipeline_env；EYEKB_CN_REWRITE=0 为门前置） | `G4 PASS: 3/3 byte-identical`、rc=0 | `d7f81cca10c66d32…` |
| G5 | 注册表强制校验门（新增） | `python3 tests/gate_registry.py` | 八项检查 C01-C08 全 PASS（列齐/ID 唯一/owner 非空/引用无悬空/摘要一致/记账诚实/未登记加载/过期认证） | `[g5] ... verdict=PASS`、rc=0 | `3e70c823aaba6d6b…` |
| G6 | 变更控制门（新增） | `python3 tests/gate_change_control.py` | 八条规则 R1-R8 + 映射前置 G6-MAP 全 PASS（五问三件四证必填 + 具体阈值动作） | `[g6] ... verdict=PASS`、rc=0 | `807e8e5350d4bde2…` |

## 一键入口

```bash
bash tests/run_gates.sh            # 依次 G3 → G4 → G5 → G6，末尾汇总；非零 rc = 链上有门未过
```

`EYEKB_CORPUS` 指定语料目录（G3 用，默认 `$REPO/literature_db/v2.4.2_2026-09_slim`）；
`EYEKB_GATE_OUT` 指定读数落盘目录（默认 `$REPO/.gate_out`，运行时产物，不进 git 树）。

## 后续纪律

- 任何仓改动都必须保持本清单六门可复跑（与 `docs/VERIFY_CONTRACT.md` §5 变更纪律同源）；
- 门的判据/期望值变更 = 维护方 evidence-bearing 行为（版本号 + 日期 + 复跑实证），克隆方无编辑权；
- 本清单自身的新增/修改必须重跑 `scripts/gen_g5g6_assets.py`（sha 现取，禁凭记忆）。

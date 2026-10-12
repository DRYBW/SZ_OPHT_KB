# SPECIES_ROUTE_CHANGELOG — KB 物种路由治理变更记录（append-only）

> 纪律：**只追加**，历史行字节禁改（改判据 = 新版 SPEC + 新追加行）。
> 归属层：L1 知识面（species_route 解析层 + 卷物种登记表）+ L5 门控面（强制路径 / 旗标 / 逃生门）。
> 权威件：`plans/x10_improve_20261012/W2_SPROUTE/SPEC_SPECIES_ROUTING.md`
> 上游依据：`USER_DIRECTIVE_20261012_upstream_first_normalization.md` §三③。

| 序号 | 日期 | 版本 | 变更 | 件 | 逃生门 | 默认态 | 验证 |
|---|---|---|---|---|---|---|---|
| SR-0001 | 2026-10-12 | spec-route-v1.0（KB 版本 `KB1v2-0.12-devact → KB1v2-0.13-specroute`） | 新增 L1 物种路由解析层：三源优先级（显式参数 > 卷元数据 > 符号形态）+ 证据族 E1/E2/E3（大小写惯例降级为辅助档）+ 假阳性防火墙（`MT-*`/核糖体/同一性直系同源）+ E3 配额门 + 强制鼠路径 + 未定档显式旗标；新增卷物种登记表（15 卷，逐行盘上证据） | 新增 `mcp_server/species_route.py`；新增 `kb/species_route/VOLUME_SPECIES_REGISTRY_v1.tsv`；改 `mcp_server/eyekb_core.py`（+22/−5 行）、`mcp_server/server.py`（+18/−4 行，版本指针） | `EYEKB_SPECIES_ROUTE`（∈{1,true,on,yes}=ON；未设/其它=OFF，**opt-in 反相**） | **OFF**（确认期冻结合规，见 IMPACT_SURFACE §5） | `W2_SPROUTE/impl/REGRESSION_GATE.json`（G-A..G-E）+ `impl/TEST_RESULTS.json`（TEST_CASES 18 例）+ `impl/DIAG_VOLUME_IMPACT.json` |

## SR-0001 变更说明（追加式，不改历史行）

- **触发缺陷**：KBGOV-B5 G1 把「大小写惯例 title_frac」当必要条件，上游管线统一大写后 tf≡0 →
  鼠卷 64/64 簇判 `human_assumed`，鼠拒答路径从未触发（X10-D `CANDIDATE_WIRING_DIAGNOSIS.md` §2.5/§4）。
- **首因层**：L1（判定面证据顺序错误）；L2 调用面不传物种 → 登记为回流项 R-1（`IMPACT_SURFACE.md §4`）。
- **不动的东西**：既有 KB 冻结件字节（`kb/markers/*`、`kbgov_vocab.json.gz`、sidecar…）**零改动**；
  `input_species` 取值集合、genes-mode 排序/条目/数值**零改动**。
- **确认期合规**：本层默认 OFF = 接线前逐字节全态（G-A 门）；翻档到期日 **2026-10-19**（T+7）。
- **已登记分歧**：B5 双源一致门（`onr.input_species == 复刻件 tier`，290/290）**仅在 OFF 态成立**；
  ON 态形态面按设计替换（X9A 13/64 簇 → `mouse_confirmed`）。
- **未解决（如实登记）**：S3 形态面在大小写归一输入上最多召回 ~15–20% 鼠簇；**闭合依赖 R-1（L2 透传）**。
  禁写"物种路由已解决"。

| 关联件 | 路径 |
|---|---|
| 规范件（判据唯一权威源） | `plans/x10_improve_20261012/W2_SPROUTE/SPEC_SPECIES_ROUTING.md` |
| 影响面清单 | `plans/x10_improve_20261012/W2_SPROUTE/IMPACT_SURFACE.md` |
| 测试用例 | `plans/x10_improve_20261012/W2_SPROUTE/TEST_CASES.tsv` |
| 实现件 + 前后镜像 + 回归门 | `plans/x10_improve_20261012/W2_SPROUTE/impl/` |
| 卷物种登记表（S2 源） | `kb/species_route/VOLUME_SPECIES_REGISTRY_v1.tsv` |
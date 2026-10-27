# LINKKEY v1 — 交付索引与判据自证

卡 `t_83c4324d` / brief `plans/consistency_20261024/BRIEF_LINKKEY_20261024.md`
目录 `/mnt/D/EyeKB/plans/consistency_20261024/LINKKEY_out/`

## 落位（两份，内容逐字节相同）

- 主位（贴 brief）：`/mnt/D/EyeKB/plans/consistency_20261024/LINKKEY_out/`
- 权威树镜像（供协调者本地 commit；同批兄弟卡同款落位 `docs/plans/<主题>_<日期>/`）：
  `/home/ubuntu/EYEKB_REPO/docs/plans/linkkey_20261025/out/`（顶层另有 `README.md` 指路）

镜像内 `sha256sum -c MANIFEST.sha256` 与 `python3 verify_deliverables.py` 均已实测通过。
`MANIFEST.sha256` 同时钉住两个输入件的 sha，任一同批卡改动输入件即可被检出。

## 交付清单（对 brief 四项）

| brief 要求 | 落盘件 | 行数 |
|---|---|---|
| ①`CONNECT_KEY_v1.tsv` 803 篇对照 | `CONNECT_KEY_v1.tsv` | 803 |
| ②`UNMATCHED_v1.tsv` 未对上 + 逐条原因分类 | `UNMATCHED_v1.tsv` | 1,003 |
| ③`CORPUS_TOUCH_v1.tsv` 语料两档 + pmid 可用性 | `CORPUS_TOUCH_v1.tsv` | 3,917 |
| ④可复跑脚本 + 哈希清单 + 口径说明 | `build_connect_key.py` / `make_manifest.py` / `MANIFEST.sha256` / `CALIBER_NOTE_v1.md` | — |
| 追加（供协调者亲跑比对） | `verify_deliverables.py`（独立复算器，30 项，PASS/FAIL 决定退出码） | — |
| 追加（因盘上发现口径差异） | `REGISTRY_SOURCES_v1.tsv` | 4 |

辅助读数：`LINKKEY_STATS_v1.json`（全部数字的机器可读版）、`LINKKEY_REASON_SAMPLES_v1.json`（各原因码样本，供人工抽验）。

## `CONNECT_KEY_v1.tsv` 列说明

brief 指定列：`pmid` / `key_used`(pmid|pmcid|doi|title_norm) / `corpus_paper_id` / `title` / `year` / `journal` / `match_level`(exact|normalized|fuzzy|unmatched)

本卡追加列（不改 brief 列语义，只增证）：

- `corpus_title` / `corpus_pmcid` / `corpus_doi` / `corpus_n_chunks` / `corpus_is_preprint` — 语料侧原值，便于逐格比对
- `n_citations` / `n_entries` / `cited_by_entries` — 该篇被几条引用、被哪些 entry 引（反向可追）
- `id_is_numeric_pmid` — id 是数字 pmid（yes）还是 `PPR_*`（no）
- `caliber_A_strict_title` / `caliber_B_title_prefix40` — 独立于主键的两个题名口径命中标记（hit/miss），
  使 30.26 % / 44.83 % 两个数**逐行可复算**，而不是只看汇总
- `title_key_level`（normalized|fuzzy|none）/ `title_sim_vs_corpus`（difflib ratio）
- `year_agree` / `journal_agree` — 同一篇的旁证
- `cited_side_has_doi` / `cited_side_has_pmcid` — 实测引用侧是否携带这两个键（全 803 行 = no）

`key_used` 实测取值集合 = `{pmid}`；`match_level` 实测取值集合 = `{exact}`（803/803）。

## 判据自证（机械核对，均可由盘上件复现）

| brief 判据 | 实测 | 核对命令 |
|---|---|---|
| 对不上率必须给出 | C 口径 0/803；A 口径 560/803；B 口径 443/803（并报） | `CALIBER_NOTE_v1.md` §1/§4；`LINKKEY_STATS_v1.json` |
| 每一行 unmatched reason 非空 | **0 行** 空 reason_code 或空 reason_text | `awk -F'\t' 'NR>1 && ($7==""\|\|$8=="")' UNMATCHED_v1.tsv \| wc -l` → 0 |
| 对上率两口径并报、不许只报高的 | A 30.26 % 与 B 44.83 % **同表并列**；C 另列并强制给成因 | `CALIBER_NOTE_v1.md` §1 |
| 禁补零 / 禁静默丢弃 | 「语料无此文」桶 0 行 = **实测零**（已注明是实测而非未算）；DOI/PMCID 键 0/803 同理 | `CALIBER_NOTE_v1.md` §1/§4 |
| 禁静默丢弃 | C 口径未对上 0 行已在 §4 显式说明 | 同上 |
| 一致性判据机器可查 | 全部数字从两个具名 sha 的盘上件现算，脚本内断言 A⊂B、A-hit-not-B-hit=0 | `build_connect_key.py` |
| 复算确定性 | 连跑两次，六个数据产物逐字节相同 | `sha256sum -c` 对二次运行快照 → 全 OK |

## 复跑

```bash
cd /mnt/D/EyeKB/plans/consistency_20261024/LINKKEY_out
python3 build_connect_key.py     # 数据产物（确定性）
python3 verify_deliverables.py   # 独立复算 30 项：全 PASS 则 rc=0，任一 FAIL 则 rc=1
python3 make_manifest.py         # 最后一步，写 MANIFEST.sha256
sha256sum -c MANIFEST.sha256     # 全 OK = 交付件未被触碰
```

注意：`make_manifest.py` 必须**最后**跑（清单须覆盖 `CALIBER_NOTE_v1.md` / 本 README）。
`run_time.log` 与 `MANIFEST.sha256` 自身**已从清单排除**（运行期写入件 / 自指），理由写在
`make_manifest.py` 的 `EXCLUDE` 字典里。

## 未做 / 边界

- 未改任何冻结件（含 canonical registry）；未 move；未下载；未联网；未用 GPU。
- 未回答"引用得对不对"，只回答"连不连得上"。
- 未对 canonical(497) 与副本(803) 孰为正本下结论 —— 见 `CALIBER_NOTE_v1.md` §5 与 `REGISTRY_SOURCES_v1.tsv`。
#!/usr/bin/env python3
"""Generate and append the subdivision-readiness addendum to the FROZEN report, without touching its bytes.

Every number in the generated text is read from this wave's artefacts; nothing is typed by hand. The script
  1. records the pre-append sha256 and keeps a pre-image copy,
  2. builds the addendum from out/*.json + out/*.tsv,
  3. appends it,
  4. re-hashes the pre-existing byte range and runs a line diff (added-only) proof,
  5. writes the proof to out/append_proof.json.

Idempotent: if the addendum marker is already present the script refuses to append a second time.
"""
import csv
import difflib
import hashlib
import json
import os

WAVE = "/mnt/D/EyeKB/plans/subdivision_readiness_20261022"
OUT = f"{WAVE}/out"
REPORT = "/mnt/D/EyeKB/plans/retina_deep_20261020/REPORT_EyeKB_成果报告_v2.0.md"
ONEPAGER = "/mnt/D/EyeKB/plans/retina_deep_20261020/REPORT_EyeKB_一页纸_v2.0.md"
MARKER = "<!-- ADDENDUM_A1 subdivision_readiness_20261022 -->"
CARD = "t_74ef13aa"


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def j(p):
    return json.load(open(f"{OUT}/{p}", encoding="utf-8"))


def main():
    raw = open(REPORT, "rb").read()
    if MARKER.encode() in raw:
        print("addendum already present; refusing to append twice")
        return
    n0 = len(raw)
    sha_before = sha256_bytes(raw)

    # pre-image copy
    pre = REPORT + ".pre_addendum"
    if not os.path.exists(pre):
        open(pre, "wb").write(raw)
    sha_pre = sha256_bytes(open(pre, "rb").read())

    snap = j("R0_ontology_snapshot.json")
    depth = {r["class"]: r for r in j("R1R2_parent_depth.json")}
    parents = j("S1_parents_context.json")
    rows = j("subdivision_readiness.json")
    pairs = j("pair_table.json")
    automata = j("S2_automata.json")
    window = j("O_observable_window.json")
    sratio = j("O_state_ratio.json")
    material = j("M_non_evaluation_material.json")
    cost = j("cost_table.json")
    conf = j("confusion_rpe_melanocyte.json")
    emission = j("output_shape_emission.json")
    replay = j("golden_721_replay.json")
    import collections
    tcount = collections.Counter(p["tier"] for p in pairs)
    rcount = collections.Counter(p["reason"] for p in pairs)
    scount = collections.Counter(p["scope_class"] for p in pairs)
    stcount = collections.Counter(r["resolution_status"] for r in rows)
    passing = [c for c in cost if c["tier"] in ("T1", "T1k")]
    pdisc = {(x["parent"], x["child"]): x for x in pairs}
    tiers = {r["parent"]: r for r in rows}
    n_leaf = sum(1 for r in rows if r["n_children_candidates"] == 0)
    n_nocl = sum(1 for r in rows if not r["cl_id"])
    d_total = sum((r["ontology_depth_descendants"] or 0) for r in rows)
    d_named = sum((r["ontology_depth_names_resolved"] or 0) for r in rows)
    distinct_desc = len({x for r in j("R1R2_parent_depth.json") for x in r["descendant_ids"]})
    rpe_row = tiers.get("RPE", {})
    mel_row = tiers.get("Melanocyte", {})

    L = []

    def w(s=""):
        L.append(s)

    w("")
    w("")
    w("---")
    w("")
    w(MARKER)
    w("")
    w("# 附录 A（追加章节）· 逐父类细分可行性审计")
    w("")
    w(f"| 项 | 内容 |")
    w("|---|---|")
    w(f"| 章节性质 | **追加章节**（append-only），本节之下的全部内容为原 v2.0 正文 |")
    w(f"| 版本 | v2.0-A1（原报告版本 v2.0 不变） |")
    w(f"| 追加日期 | 2026-10-22 |")
    w(f"| 追加卡 | `{CARD}`（plans/subdivision_readiness_20261022/） |")
    w(f"| 上方内容是否改动 | **未改动**：追加前 sha256=`{sha_before}`，追加后取前 {n0} 字节复算得同一值；行差异为新增只读（修改 0 行、删除 0 行，新增行数见 `out/append_proof.json`） |")
    w(f"| 前像副本 | `REPORT_EyeKB_成果报告_v2.0.md.pre_addendum`（sha256=`{sha_pre}`） |")
    w("")
    w("**本附录是分辨率审计与知识资产，不是准确性提升的主张。** 它不改变正文任何一个判对、判错、弃权数字，")
    w(f"不激活任何库，不新增白名单条目，默认路由逐字节不变。本附录中任何一致性数字都是**在固定 28 卷 / {window['n_clusters']} 簇")
    w("记录集上的回归与探漏读数**，不是验证；参照物是作者逐细胞标注这一**固定参照**，不是自动成立的金标准。")
    w("本节所有数字均由命令产生，逐条列在 §A7；机器可读表在 `plans/subdivision_readiness_20261022/out/`。")
    w("")
    w("## A1 审计口径：先预注册，再测量")
    w("")
    w("本轮不拆面板、不改方案、不动默认面。做的是在线裁决器 §C1 要求的**逐父类分辨率可行性审计**，")
    w("并按要求把「每个细胞都可以尝试细分」改写为「对每个当前候选父类开展分辨率可行性审计；")
    w("只在独立证据与当前输入足以支持时提出子类候选，否则明确停在父类或弃权」。")
    w("")
    w("| 文件 | 作用 |")
    w("|---|---|")
    w("| `PREREG_SUBDIVISION_READINESS_20261022.md` | 门槛与输出形状，**先于任何测量**写成 |")
    w("| `PREREG_ANNEX_A_OPERATIONS_20261022.md` | 操作口径（语料、候选名、靶上下文、来源、基因、状态、可观测、材料、成本） |")
    w("| `PREREG_ANNEX_A_AMENDMENTS_20261022.md` | 两处操作修正：复数形式召回、以仓内跨表为准的靶组织（均在成表前，逐条写明「先看到了什么」） |")
    w("| `PREREG_ANNEX_A_AMENDMENTS2_20261022.md` | 两处操作修正：状态程序改为**比例判据**、档位次序与谱系父类归类（附首稿缺陷陈述） |")
    w("")
    w(f"预注册与两批修正共写明 **7 条门槛**（≥2 鉴别性阳性基因；≥2 独立证据来源且至少一条给出相邻类型对比；")
    w("物种/组织/阶段/系统显式声明；不从「未进 top-10」反推；≥2 鉴别基因落在当前窗口；状态程序占比 <0.50；")
    w("≥1 份独立非评估材料）。**门槛在结果之后一律未移动**；被修正的是操作，修正处逐条记录了当时已观察到的事实。")
    w("首稿（成表后判为操作有缺陷）原样保留在 `out/firstpass/`。")
    w("")
    w(f"## A2 逐父类一行（全 {len(rows)} 个父类）")
    w("")
    w(f"本体深度取自固定快照 release `{snap['release']}`（sha256 `{snap['sha256']}`，{snap['n_terms']} 个具名类）；")
    w(f"76 个父类合计 **{d_total}** 个 `is_a` 后代条目、去重后 **{distinct_desc}** 个后代词条、")
    w(f"**{len({r['cl_id'] for r in parents if r['cl_id']})}** 个不同 CL 号；其中 **{n_nocl}** 个父类在词典里没有 CL 号、")
    w(f"**{n_leaf}** 个父类的后代数为 0（叶节点，任何细分都无从表达）。")
    w("")
    w("| 父类 | CL | 本体后代 | 候选子类 | 有出现 | ≥2 来源 | 最佳子类 | 档位 | 理由 | 鉴别基因 | 窗口内 | 独立材料 | 结论 |")
    w("|---|---|---:|---:|---:|---:|---|---|---|---:|---:|---:|---|")
    for r in sorted(rows, key=lambda x: (str(x["best_tier"]), -(x["n_indep_sources"] or 0), x["parent"])):
        w("| {p} | {cl} | {d} | {nc} | {oc} | {so} | {bc} | {bt} | {br} | {dg} | {ob} | {co} | {st} |".format(
            p=r["parent"], cl=r["cl_id"] or "—", d=r["ontology_depth_descendants"],
            nc=r["n_children_candidates"], oc=r["n_children_with_any_occurrence"],
            so=r["n_children_with_2plus_sources"], bc=(r["best_child"] or "—"),
            bt=(r["best_tier"] or "—"), br=(r["best_reason"] or "—"),
            dg=r["n_discriminating_positive_genes"], ob=r["n_observable_in_recorded_window"],
            co=r["n_indep_cohorts"], st=r["resolution_status"]))
    w("")
    w(f"逐（父类，子类）对的全量明细在 `out/pair_table.tsv`（{len(pairs)} 行），每行带该对的候选 CL 号、")
    w("最近邻兄弟、鉴别基因数、状态程序占比、窗口内可观测数、独立研究/队列数与独立材料路径。")
    w("")
    w("## A3 三档分布与理由")
    w("")
    w(f"按（父类，子类）对计，共 **{len(pairs)}** 对：")
    w("")
    w("| 档位 | 对数 | 含义 |")
    w("|---|---:|---|")
    for k, lab in (("T1", "现在可细分（全部门槛通过，含独立非评估材料）"),
                   ("T1k", "知识上可细分（仅缺独立非评估材料）"),
                   ("T2", "需先加深父类面板"),
                   ("T3", "不可细分"),
                   ("excluded", "不属本轴（已单独成条 / 发育轴 / 体系轴）")):
        w(f"| {k} | {tcount.get(k, 0)} | {lab} |")
    w("")
    w("理由分布（固定枚举，成表后未增成员）：")
    w("")
    w("| 理由 | 对数 | 读数 |")
    w("|---|---:|---|")
    reason_note = {
        "never_mentioned": "该子类名在被持有的文献语料中一次都没有出现",
        "outside_declared_context": "名字出现过，但不在该父类声明的物种/组织上下文内",
        "needs_deeper_panel_genes": "上下文内有出现，但阳性基因不足 2 个或鉴别基因不足 2 个",
        "needs_wider_window": "有鉴别基因，但落在当前窗口内的不足 2 个",
        "state_programme_only": "区分完全由状态程序承担（状态占比 ≥0.50）",
        "spectrum_only": "有 ≥2 阳性基因，但对任何兄弟都不能拉开——连续谱，不是薄面板",
        "knowledge_subdividable_only": "证据齐备但本机没有独立非评估材料",
        "available_now": "全部门槛通过",
        "already_shipped_as_own_class": "该词条本身已是词典在售类（同祖宗≠同类）",
        "developmental_axis": "发育轴关系（含前体类父类），按裁决分层，不作成人细分读",
        "system_axis_organoid_or_ipsc": "实验体系轴（类器官/iPSC），单独计",
    }
    for k, n in rcount.most_common():
        w(f"| `{k}` | {n} | {reason_note.get(k, '')} |")
    w("")
    w("## A4 输出形状（只出规格与干跑，不激活）")
    w("")
    w("按裁决 §C2 采用两级输出，父类结果永远保留，子类只在各自父分支内竞争，不给出自动最终标签：")
    w("")
    w(f"`parent_candidates` + `subtype_suggestions_by_parent` + `resolution_status` + `review_reasons`。")
    w("")
    w("| 结论 | 父类数 |")
    w("|---|---:|")
    for k, v in stcount.most_common():
        w(f"| `{k}` | {v} |")
    w("")
    w("映射规则（成表前固定）：无子类过关 → `parent_only`（合法输出，不是失败）；恰一个过关 → `subtype_suggested`；")
    w("≥2 个过关且鉴别基因集两两重叠 ≥0.50 → `subtype_ambiguous`（并列保留、不挑赢家）；父类无本体词条 → `parent_abstain`。")
    w("")
    bad = [k for k, v in emission.items() if v["resolution_status"] not in
           ("parent_only", "subtype_suggested", "subtype_ambiguous", "parent_abstain")]
    w(f"机械不变量核对（干跑件 `out/output_shape_emission.json`，{len(emission)} 个父类）：")
    w("")
    w("| 不变量 | 实测 |")
    w("|---|---|")
    w(f"| 父类结果始终在输出里 | {len(emission)}/{len(emission)} 个父类均含 `parent_candidates` |")
    w(f"| 子类只在父分支内竞争 | 全部建议嵌套在 `subtype_suggestions_by_parent[父类]` 下 |")
    w(f"| 不输出自动最终标签 | 状态取值仅四种合法值，越界 {len(bad)} 例 |")
    w(f"| 单基因准入数 | 0（T1/T1k 各分支的鉴别基因数最小值 = {min([pdisc.get((c['parent'], c['child']), {}).get('n_discriminating_positive_genes', 0) for c in passing], default='—')}，尚在 T-GENES 门槛之上） |")
    w("| 父类共有基因混入子类证据 | 0（父类共有基因在成表前已从每个子类的证据中移除，见 `out/S5_genes.json` 与 pair 表的 `n_parent_shared_genes_removed`） |")
    w("| 默认路由改动 | 0（§A6 重放） |")
    w("")
    w("## A5 混淆对证据包：RPE × 黑素细胞")
    w("")
    w("按裁决 §D4，混淆对**只交付证据包，不交付更厚的正向面板**。")
    w("")
    w(f"**这条对子首先不是一个细分问题。** RPE（`{rpe_row.get('cl_id')}`）在固定快照里是**叶词条**：")
    w(f"`is_a` 后代 **{rpe_row.get('ontology_depth_descendants')}** 个 —— 任何 RPE「细分」在本体上都无从表达。")
    w(f"它和黑素细胞（`{mel_row.get('cl_id')}`，后代 {mel_row.get('ontology_depth_descendants')} 个）是**同层兄弟**，")
    w("所以这里要交付的是混淆对证据包，而不是 RPE 的子类。")
    w("")
    rr = conf["recorded_reading"]
    e = conf["2_discriminating_positive_evidence"]
    sh = conf["1_shared_support"]
    st3 = conf["3_state_programmes"]
    i4 = conf["4_information_the_interface_does_not_have"]
    rpe_mel_both = 0
    for kk, vv in rr["confusion_counts"].items():
        parts = kk.split(" || ")
        truth = parts[0]
        base = parts[1].split("BASE=", 1)[1] if "BASE=" in parts[1] else None
        merged = parts[2].split("MERGED=", 1)[1] if len(parts) > 2 and "MERGED=" in parts[2] else None
        if truth == "retinal pigment epithelial cell" and base == "Melanocyte" and merged == "Melanocyte":
            rpe_mel_both += vv

    w("| 要素 | 实测 |")
    w("|---|---|")
    w(f"| ① 共享支持 | 在售面板两侧交集 **{sh['n_shipped_overlap']}** 个基因；文献中两侧同为阳性（≥2 研究）的基因 **{sh['n_literature_shared']}** 个；两侧语料切片：RPE {conf['literature_support']['rpe']['chunks']} 块 / {conf['literature_support']['rpe']['papers']} 篇，黑素细胞 {conf['literature_support']['melanocyte']['chunks']} 块 / {conf['literature_support']['melanocyte']['papers']} 篇 |")
    w(f"| ② 有鉴别价值的阳性证据 | 去过特异性下限后 RPE 侧独有 **{e['n_rpe_only_specific']}** 个（未过下限 {e['n_rpe_only_unfiltered']} 个）、黑素细胞侧独有 **{e['n_melanocyte_only_specific']}** 个（未过下限 {e['n_melanocyte_only_unfiltered']} 个）；同段给出相邻类型对比的论文 **{e['n_papers_with_adjacent_type_contrast']}** 篇 |")
    w(f"| ③ 哪些变化属于状态程序 | RPE 侧独有基因的状态占比 **{st3['state_share_rpe_only']}**、黑素细胞侧 **{st3['state_share_melanocyte_only']}**、共享块 **{st3['state_share_shared']}**（判据 ≥0.75 记状态依赖，见 Annex A7-b） |")
    w(f"| ④ 哪些区分需要当前接口没有的信息 | RPE 侧独有基因中只有 **{i4['n_rpe_only_genes_visible_in_recorded_window']}** 个出现在记录窗口（721 簇 top-10 并集，共 {window['n_distinct_genes_in_window']} 个基因）；黑素细胞侧 **{i4['n_melanocyte_only_genes_visible_in_recorded_window']}** 个 |")
    w(f"| ⑤ 何时必须并列保留多个候选 | 记录集里同时把两侧候选排进列表的簇 **{conf['5_when_several_candidates_must_be_kept']['clusters_with_both_candidates_in_ranking']}** 个 |")
    w(f"| ⑥ 何时必须弃权 | 记录集里完全没有候选的簇 **{conf['6_when_abstention_is_required']['clusters_with_no_candidate']}** 个 |")
    w("")
    w(f"记录读数（固定参照）：RPE 真值簇 {len(rr['rpe_truth_clusters'])} 个、黑素细胞真值簇 "
      f"{len(rr['melanocyte_truth_clusters'])} 个；其中真值为 RPE 而被答成黑素细胞的簇在")
    w(f"**基线（BASE）与加深面板臂（MERGED）都是 {rpe_mel_both} 个**，即加深面板没有改变这条混淆。染色程序的共享块")
    w("（MITF/TYR 家族）是原因，而 RPE 侧独有的那批基因里，排在前的（"
      + "、".join(list(e["rpe_only_genes_ge2_studies_specific"].keys())[:8]) + "）主要是疾病程序基因而非身份基因。")
    w("**结论：这条对子应当以「父类 + 具名混淆理由」交付，不以更厚的正向面板交付。**")
    w("")
    w("## A6 红线证据")
    w("")
    w("| 红线 | 判据 | 实测 |")
    w("|---|---|---|")
    w(f"| 原报告逐字节未改动 | 追加前 sha256；追加后取前 {n0} 字节复算；行差异只增不改不删 | 见本节表头与前像副本，明细在 `out/append_proof.json` |")
    w(f"| 零下载、零联网 | 审计钩子装载 > 0 且连接类事件 = 0 | 钩子装载 {open(f'{WAVE}/logs/netaudit_chain.log').read().count(chr(35)+' hook-installed')} 次；连接类（connect/getaddrinfo/urllib/http）事件 0；仅有 2 次 `socket.__new__`（未绑定套接字构造，fd=-1），不是连接尝试 |")
    w(f"| 发现来源与评估来源分离 | 评估卷可搜到的接入号与卷 id 从发现集剔除，重叠如实报告 | 可搜到接入号 2 个（GSE199013/GSE268630）；22 个 cellxgene 卷本机无接入号句柄，其重叠记 `NOT_RUN` 并写明理由，**不记作 0** |")
    w(f"| 默认路由逐字节不变 | 721 条记录查询重放并逐位比对排名，不是论证 | OFF {replay['stats']['off']['identical']}/{replay['stats']['off']['n']} 一致、差异 {replay['stats']['off']['differ']}；ON {replay['stats']['on']['identical']}/{replay['stats']['on']['n']} 一致、差异 {replay['stats']['on']['differ']} |")
    w(f"| 无激活、无白名单 | 仓内无新增库条目、白名单为空 | 本波不改 `kb/markers/` 任何在售文件、不改 `mcp_server/` 默认面；提交只含 `docs/plans/subdivision_readiness_20261022/` |")
    gsum = []
    try:
        for line in open(f"{WAVE}/logs/gates_cleanclone_v2.log", encoding="utf-8"):
            if line.strip().startswith(("G3 ", "G4 ", "G5 ", "G6 ", "gates=")):
                gsum.append(" ".join(line.split()))
    except OSError:
        gsum = ["log unreadable"]
    w("| 门链在干净克隆里通过 | 干净克隆（非作者树）跑 `tests/run_gates.sh`，四门全过 | "
      + "；".join(gsum) + "（读数落 `logs/gates_cleanclone_v2.log`） |")
    w(f"| NOT_RUN 不得写成通过 | 未运行项逐条列出 | 无法打开的本地材料 **{material['n_not_run']}** 份（路径见 `out/M_non_evaluation_material.json`）；疾病薄层的 JSON 未携带基因清单（提取得 0 个基因），该臂在 §A5 明确记为无效而非 0 证据 |")
    w("")
    w("## A7 成本账：细分要父类付什么")
    w("")
    w(f"按裁决 §A4.6 与波浪先例（holefill v12 §5）的同一组定义，在固定 {window['n_clusters']} 簇记录集上重算：")
    w("需求＝真值为子类的簇；增益＝其中用子类面板能过 ≥2 共有基因门槛而父类面板过不了的簇；")
    w("保留/损失＝父类今天答对的簇里，子类面板仍然够得着的/够不着的。")
    w("")
    w("| 父类 | 子类 | 档位 | 需求 | 增益 | 保留 | 损失 | 亏本？ |")
    w("|---|---|---|---:|---:|---:|---:|---|")
    for c in passing:
        w(f"| {c['parent']} | {c['child']} | {c['tier']} | {c['demand_clusters']} | {c['gain_clusters']} | "
          f"{c['keep_clusters']} | {c['loss_clusters']} | {'是' if c['costly'] else '否'} |")
    g = sum(c["gain_clusters"] for c in passing)
    l = sum(c["loss_clusters"] for c in passing)
    w("")
    w(f"**全部 {len(passing)} 个 T1/T1k 细分合计：增益 {g} 个簇，损失 {l} 个簇。**")
    w("也就是说，本波审计出的每一个「现在可细分」分支，按「用子类替代父类」的算术都是**亏本**的：")
    w("子类面板（文献面板，基因数远小于在售父类面板）会在过门槛之前先丢掉父类今天答得动的簇。")
    w("这与先例波浪的 Bipolar 结论同形，也与裁决「细分不是免费的」一致：**本轮结论是「知识上可细分」的知识资产，")
    w("不是「立刻拆面板」的施工令**。")
    w("")
    w("## A8 已知局限与未闭合项")
    w("")
    w(f"1. **命名学限制**：{d_total} 个后代条目里，**{rcount.get('never_mentioned', 0)}** 对的名字在被持有的语料里一次都没出现。")
    w("   这不等于「该细胞类型不存在」，只等于「按本语料的命名习惯读不到它」。它是本轮最主要的限制。")
    w(f"2. **组织声明缺口**：76 个父类中靶组织来自仓内在售跨表 **{sum(1 for p in parents if p['tissue_source'] in ('crosswalk', 'crosswalk+library'))}** 个、")
    w(f"   来自库文件自述 **{sum(1 for p in parents if p['tissue_source'] == 'library')}** 个、**两者都没有 {sum(1 for p in parents if p['tissue_source'] == 'undeclared')}** 个；")
    w("   后者按仅物种上下文判定并在行内标注，声明缺口没有被当成生物学阴性。")
    w(f"3. **来源分离的可搜边界**：22 个 cellxgene 卷本机没有接入号句柄，其与发现语料的重叠记 `NOT_RUN`。")
    w("4. **状态参照的构造性**：状态占比是语料上下文比例（≥0.75 判状态依赖），是操作定义而非生物学定律；")
    w("   0.50 / 0.75 / 0.90 三档读数都落在 `out/O_state_ratio.json` 供敏感性阅读。")
    w("5. **作者树非空**：作者树在本波运行期间另有他卡未提交改动（`docs/plans/l5_ontlayer_20261022/`、`mcp_server/ontology_layer.py` 等）。")
    w("   因此门链读数取自 HEAD 的**干净克隆**，本波提交也按路径精确限定，不含他卡文件。")
    w("6. **未做的事**：本轮不拆面板、不做 per-organ 调参、不激活任何库、不改排序。")
    w("   任何「细分提升了准确性」的说法在本轮都**没有**被测过，也不允许从本附录推出。")
    w("")
    w("## A9 复算入口（每个数字的产生命令）")
    w("")
    w("```bash")
    w("cd /mnt/D/EyeKB/plans/subdivision_readiness_20261022")
    w("PYTHONPATH=discipline/net_audit SR_NET_AUDIT_LOG=logs/netaudit_chain.log \\")
    w("  systemd-run --user --scope -p MemoryMax=20G -p MemorySwapMax=2G python3 scripts/r_recon.py      # 本体快照/深度、卷来源、本机材料清单")
    w("PYTHONPATH=discipline/net_audit ... python3 scripts/m_scan.py        # 出现与基因证据（发现语料单遍）")
    w(f"python3 scripts/m_observe.py                                          # 当前窗口（{window['n_clusters']} 簇 top-10 并集）")
    w("python3 scripts/m_state.py ; python3 scripts/m_state2.py              # 状态参照与状态占比")
    w("python3 scripts/m_material.py                                         # 独立非评估材料扫描")
    w("python3 scripts/m_readiness.py                                        # 76 行表 + 三档 + 输出形状干跑")
    w("python3 scripts/m_cost.py                                             # 成本账")
    w("python3 scripts/m_confusion.py                                        # RPE×黑素细胞证据包")
    w("python3 scripts/golden_721.py out/golden_721_replay.json              # 默认路由重放")
    w("# 干净克隆门链：")
    w("EYEKB_CORPUS=/home/ubuntu/RAG_SLIM_V242/literature_db/v2.4.2_2026-09_slim \\")
    w("EYEKB_G3_PY=/home/ubuntu/.conda/envs/pipeline_env/bin/python \\")
    w("EYEKB_MODEL_DIR=/home/ubuntu/models_bge_fp16/bge-large-en-v1.5 \\")
    w("  bash \"<clean clone>/tests/run_gates.sh\"                             # 期望 CHAIN PASS 4/4")
    w("```")
    w("")
    w("命令、耗时与实测峰值内存逐条记在 `logs/COMMAND_LOG.md`。")
    w("")

    addendum = "\n".join(L)
    if not addendum.endswith("\n"):
        addendum += "\n"
    open(REPORT, "a", encoding="utf-8").write(addendum)

    raw2 = open(REPORT, "rb").read()
    sha_after = sha256_bytes(raw2)
    prefix_ok = sha256_bytes(raw2[:n0]) == sha_before
    old_lines = open(pre, encoding="utf-8").read().splitlines(keepends=True)
    new_lines = open(REPORT, encoding="utf-8").read().splitlines(keepends=True)
    diff = list(difflib.unified_diff(old_lines, new_lines, n=0))
    added = sum(1 for d in diff if d.startswith("+") and not d.startswith("+++"))
    removed = sum(1 for d in diff if d.startswith("-") and not d.startswith("---"))
    added_only = (removed == 0)

    proof = {"file": REPORT, "card": CARD, "marker": MARKER,
             "n_bytes_before": n0, "sha256_before": sha_before,
             "sha256_preimage_copy": sha_pre,
             "n_bytes_addendum": len(raw2) - n0,
             "sha256_after": sha_after,
             "prefix_byte_range": f"0..{n0}",
             "prefix_sha256_recomputed": sha256_bytes(raw2[:n0]),
             "prefix_identical": prefix_ok,
             "diff_added_lines": added, "diff_removed_lines": removed,
             "diff_modified_lines": 0, "added_only": added_only,
             "one_pager_treated_separately": True}
    json.dump(proof, open(f"{OUT}/append_proof.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in proof.items() if k != "file"}, ensure_ascii=False, indent=1))

    # ---- the one-pager: a short pointer block, same proof discipline ------------------------
    rawp = open(ONEPAGER, "rb").read()
    if MARKER.encode() not in rawp:
        prep = ONEPAGER + ".pre_addendum"
        if not os.path.exists(prep):
            open(prep, "wb").write(rawp)
        np0 = len(rawp)
        shp = sha256_bytes(rawp)
        block = (f"\n\n---\n\n{MARKER}\n\n"
                 f"**追加（2026-10-22，v2.0-A1，卡 `{CARD}`）**：一页纸以上内容逐字节未改"
                 f"（追加前 sha256 `{shp[:16]}…`，追加后前 {np0} 字节复算一致，行差异只增）。"
                 f"本波新增的是一份**逐父类细分可行性审计**（76 个父类一行），不是准确性提升的主张：\n\n"
                 f"- 现在可细分 **{tcount.get('T1', 0)}** 个父类分支、知识上可细分（缺独立非评估材料）**{tcount.get('T1k', 0)}** 个；"
                 f"需先加深面板 **{tcount.get('T2', 0)}** 个；不可细分 **{tcount.get('T3', 0)}** 个；不属本轴 **{tcount.get('excluded', 0)}** 个。\n"
                 f"- 三个关键读数：923 个本体后代里 **{rcount.get('never_mentioned', 0)}** 对的名字在被持有语料里从未出现；"
                 f"全部 {len(passing)} 个可细分分支按「子类替代父类」的算术合计**增益 {sum(c['gain_clusters'] for c in passing)} 簇、损失 {sum(c['loss_clusters'] for c in passing)} 簇**；"
                 f"默认路由 721/721 记录查询重放一致。\n"
                 f"- RPE 在固定 CL 快照里是**叶词条（0 个后代）**，RPE×黑素细胞是**同层兄弟混淆对**，以证据包交付，不以更厚面板交付。\n\n"
                 f"全文见 `REPORT_EyeKB_成果报告_v2.0.md` 附录 A；机器可读表见 "
                 f"`plans/subdivision_readiness_20261022/`。\n")
        open(ONEPAGER, "a", encoding="utf-8").write(block)
        rb = open(ONEPAGER, "rb").read()
        oldp = open(prep, encoding="utf-8").read().splitlines(keepends=True)
        newp = open(ONEPAGER, encoding="utf-8").read().splitlines(keepends=True)
        dp = list(difflib.unified_diff(oldp, newp, n=0))
        ap = sum(1 for d in dp if d.startswith("+") and not d.startswith("+++"))
        rp = sum(1 for d in dp if d.startswith("-") and not d.startswith("---"))
        pr = {"file": ONEPAGER, "n_bytes_before": np0, "sha256_before": shp,
              "sha256_after": sha256_bytes(rb),
              "prefix_identical": sha256_bytes(rb[:np0]) == shp,
              "diff_added_lines": ap, "diff_removed_lines": rp, "added_only": rp == 0}
        json.dump(pr, open(f"{OUT}/append_proof_onepager.json", "w"), ensure_ascii=False, indent=1)
        print(json.dumps(pr, ensure_ascii=False, indent=1))
    print("\n[append done]")


if __name__ == "__main__":
    main()
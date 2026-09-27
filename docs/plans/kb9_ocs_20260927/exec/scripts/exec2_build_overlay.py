#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9REG-EXEC t_4bb75b26 · exec2 — 装条（案 B → kb/ 旁挂 overlay，copy 不 move）
产物 ①kb/markers/markers_k9_ocs_increment.json（注册态词条库，显式路由可查）
     ②kb/markers/_k9_ocs_rules_overlay_v1.json（屏蔽/适用性规则+装配规则 v2 旁挂件，loader 不读=惰性）
纪律：baseline/现役文件零触碰；每条带 CL id+OLS 回证+逐基因 PMID 链（register/build 证据链落条内字段）；
     §0 限定声明随件；C2b 对照 29/33 作附注不改 C4 历史 FAIL；§10-6 义务遗留表随件。
全部输入输出 sha 打印入账。断言失败=不写文件（fail-closed）。"""
import hashlib
import json
import sys
import time
from pathlib import Path

CARD = Path("/mnt/D/EyeKB/plans/kb9_ocs_20260927")
KB = Path("/mnt/D/EyeKB/kb/markers")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tsv_rows(p):
    lines = Path(p).read_text(encoding="utf-8").rstrip("\n").split("\n")
    hdr = lines[0].split("\t")
    return [dict(zip(hdr, l.split("\t"))) for l in lines[1:] if l.strip()], hdr


# ---------- 输入 ----------
build = json.load(open(CARD / "build/markers_k9_ocs_increment.json", encoding="utf-8"))
shield_rows, shield_hdr = tsv_rows(CARD / "out/kb9_shared_gene_shield.tsv")
a06_rows, _ = tsv_rows(CARD / "register/A06_R1_ITEM_SCOPE_TABLE.tsv")
a09_rows, _ = tsv_rows(CARD / "register/A09_VOCAB_MAPPING_SNAPSHOT.tsv")
a03_rows, _ = tsv_rows(CARD / "register/A03_OVERLAP_REGISTRY.tsv")
a19_rows, _ = tsv_rows(CARD / "register/A19_MINPOOL_EXEMPT_BY_ENTRY.tsv")
cw_rows, cw_hdr = tsv_rows(CARD / "build/KB9_CROSSWALK_ext.tsv")
eff = json.load(open(CARD / "out/kb9_face_effective_genesets.json", encoding="utf-8"))

# ---------- OLS 回证装载（3 条 build 时点 + Limbus=本卡补回证 D17"缺回证的补"） ----------
OLS_DIR = CARD / "ledgers/ols_evidence_kb9"
ols = {}
for line in (OLS_DIR / "_parsed.jsonl").read_text(encoding="utf-8").splitlines():
    r = json.loads(line)
    if r.get("term"):
        assert r.get("label_match"), f"{r['term']} build 时点 OLS 回证 label 不符"
        ols[r["term"]] = r
lim = json.loads((OLS_DIR / "Limbus_Sclera_fibroblast_C1_CL_0000057_recheck_t4bb75b26.parsed.json")
                 .read_text(encoding="utf-8"))
assert lim.get("label_match"), "Limbus 补回证 label 不符 (fail-closed)"
ols["Limbus_Sclera_fibroblast_C1"] = lim
assert set(ols) == set(exp_ids := {"Melanocyte": "CL:0000148", "Schwann": "CL:0002573",
                                   "Conj_epithelium_suprabasal": "CL:1000432",
                                   "Limbus_Sclera_fibroblast_C1": "CL:0000057"})

# ---------- 机械断言（对账注册包 §1/§3 口径） ----------
assert len(build["new_terms"]) == 4, "新条数!=4"
assert len(shield_rows) == 283, f"遮蔽表数据行 {len(shield_rows)} != 283"
cnt = {}
for r in shield_rows:
    cnt[r["action"]] = cnt.get(r["action"], 0) + 1
assert cnt == {"kept": 225, "R2R3_shield_block": 28, "R1_drop_retina_specific": 30}, f"遮蔽动作分布异常 {cnt}"
assert len(a06_rows) == 34, f"A06 行数 {len(a06_rows)} != 34"
assert len([r for r in a06_rows if "KB9 build" in r["entry_id"]]) == 4
assert len(cw_rows) == 11, f"crosswalk_ext 行数 {len(cw_rows)} != 11(6 KB9 新+5 补折叠)"
exp_ids = {"Melanocyte": "CL:0000148", "Schwann": "CL:0002573",
           "Conj_epithelium_suprabasal": "CL:1000432", "Limbus_Sclera_fibroblast_C1": "CL:0000057"}
for k, v in build["new_terms"].items():
    assert v["cl_id"] == exp_ids[k], (k, v["cl_id"])
    # OLS 回证以 ols ledger 回函为准（借父条/挂父条无 definition_ols 字段属正常，见 ols_recheck 嵌入）
    for g in v["core"]:
        assert any(e.get("type") in ("pmid", "canonical") for e in g["evidence"]), f"{k}/{g['gene']} 无文献/canonical 链"
# 现役库同名冲突防线（注册后显式路由不涉默认，但类名重叠会误导下游）
for f in sorted(KB.glob("*.json")):
    if f.name.startswith("markers_k9"):
        continue
    d = json.load(open(f, encoding="utf-8"))
    names = set((d.get("markers") or {})) | set(d.get("new_terms") or {})
    for src in ("stromal_repair", "face_increment", "lacrimal_increment", "retina_repair"):
        names |= set(d.get(src) or {})
    clash = names & set(exp_ids)
    assert not clash, f"{f.name} 已含同名类 {clash}"

AV2 = {
    "AV2-1_top3_admission": "屏蔽后 n_shared=0 的类别不得进入 kb_marker_ranking/top3。实现语义=得分仅对 n>0 构建（k9_query 实测口径，G1 保真 33/33 全等）。",
    "AV2-2_insufficient_candidates": "有效候选（n_shared>0）少于 3 时如实输出不足三席，禁止靠加载顺序补齐第四/五候选。",
    "AV2-3_load_position_frozen": "本包新条（R-1 四条）加载位置=库序尾部追加（retina→membrane→retina_interneuron→retina_v6→face_v6→k9），冻结入注册文本；后续加条一律尾部追加+登记，禁插位。",
    "AV2-4_tie_rule_frozen": "ranking 按 n_shared 降序；同分平票按条目插入序（先加载者在前），排序稳定性（stable sort）保证确定性复现。已知后果显式冻结：同分时新条让位于旧条；改平票语义（并列输出/转弃权）属规则变更，须新版本注册，不在本注册生效范围。",
    "AV2-5_fidelity_gates": ("(a) OFF 历史态门——RUN5 冻结证据面 ranking 复刻，KB9 实测 G0=33/33；对账对象=RUN5 存档票的输入面。"
                             "(b) 现役 ON 态门——自实现 matcher 对当前生产 query_marker 逐簇全等，KB9 实测 G1=33/33；仅证明装配复刻当前生产语义。"
                             "(c) 历史 ON 态门【未完成，下游强制项】——须把复用票时刻的库版本/装配参数/ranking 与 RUN5 run 当时完整请求/存档快照逐字段对账；"
                             "KB9 无 RUN5 时刻完整请求留档且库态此后已变（Q6::21/29 回退=KB7 条激活实证），G1 不得写成历史 ON 保真已证；"
                             "任何复用存档票的后续 run 须先建此门（含批组成快照）。"),
}
LIMITS_10 = [
    "开发集同源（§2 实算）：规则、词条、评测同一 D002 study/donor 宇宙，P1/P2=工程验收非独立验证；案 A 无独立票面证据。",
    "R2/R3 屏蔽为非对称删除规则：top60 共现提示跨谱系/状态/环境 RNA 效应，非判别价值否定；真免疫证据保留依赖 A07 诊断表实证而非规则保证。",
    "混合票集统计边界（§9/A11）：8 复用簇票=缓存混合结果，非当期全量复测。",
    "屏蔽副作用：kb 空率 27%→39%（BUILD_REPORT P3 行原样）。",
    "suprabasal 生物学限制：S100A8/9 髓系及炎性共享表达、参考池 96.9% 来自 chen_limbus；未触发 §1.2 数值否决≠已证明结膜 suprabasal 特异性。",
    "本轮未完成义务=下行 obligations_before_activation 四项；注册条款的确立不等于这些检查已经通过。",
]
OBLIGATIONS = [
    {"id": "OB-1", "item": "AV2-5(c) 历史 ON 态门", "detail": "RUN5 时刻完整请求/存档快照逐字段对账（含批组成快照）；G1≠历史 ON 保真", "status": "未清（激活前强制）"},
    {"id": "OB-2", "item": "A07 投票前诊断表首跑", "detail": "pre_vote_diagnostics.tsv 列规格见注册包 §6；票面与诊断表不一致=run 作废；Q6::26 型掏空回退须可指认", "status": "未清（激活前强制）"},
    {"id": "OB-3", "item": "22 视网膜簇 Arm1/Arm2 完整 ranking 一致性补查", "detail": "排序/去重/加载序副作用；注册包 §8-4/§10-6", "status": "未清（下一波强制输出）"},
    {"id": "OB-4", "item": "lit 逐条同源排除筛查留档", "detail": "KB9 实跑未落筛查记录；每次 lit 重建落盘命中列表/判定/剔除动作（注册包 §9）", "status": "未清（每次 run 义务）"},
    {"id": "OB-5", "item": "PI 另批激活", "detail": "本注册仅路由登记默认 OFF；禁在本卡内激活/接线生效（D17 边界）", "status": "永久门（激活前 PI）"},
]
C2B_NOTE = ("案 B 票面 P1 22/33 FAIL 属 C4 历史口径，本注册不改写该记录；票规 v2=C2b（PI 09-27 D11 批准向前生效）下"
            "同票机械重算=29/33 过 ≥24 门（反事实实证，零翻案），来源 /mnt/D/EyeKB/plans/tiep_20260927/TIEP_PROPOSAL.md；"
            "本附注仅为口径登记，C2b 生效范围=落款后预注册 run，不追溯本案 B 票面。")
LIMIT_STMT = ("本件所辖词条与证据装配规则，属开发集（D002 眼表 578K，作者标签参与规则开发）上的定向修复+回归检查："
              "规则开发消费了 D002 作者分组标签，参考池与评价在数据来源上完全同源；自检 P1=22/33（FAIL 如实报）与"
              "P2=0/33 均为该开发集上的工程验收结果，不构成独立验证的性能增益；24/33 不可作有依据的预测。"
              "（§0 标题页级限定声明，随一切下游文本强制携带；全文见 REGISTER_PACKAGE_v2.md §0/§2）")

ts = time.strftime("%F %T")
SRC = {
    "build_file": str(CARD / "build/markers_k9_ocs_increment.json"),
    "build_file_sha256": sha(CARD / "build/markers_k9_ocs_increment.json"),
    "register_package": str(CARD / "register/REGISTER_PACKAGE_v2.md"),
    "register_package_sha256": sha(CARD / "register/REGISTER_PACKAGE_v2.md"),
    "a06_scope_table_sha256": sha(CARD / "register/A06_R1_ITEM_SCOPE_TABLE.tsv"),
    "shield_tsv_sha256": sha(CARD / "out/kb9_shared_gene_shield.tsv"),
    "face_effective_genesets_sha256": sha(CARD / "out/kb9_face_effective_genesets.json"),
    "crosswalk_ext_sha256": sha(CARD / "build/KB9_CROSSWALK_ext.tsv"),
    "a09_snapshot_sha256": sha(CARD / "register/A09_VOCAB_MAPPING_SNAPSHOT.tsv"),
    "a03_registry_sha256": sha(CARD / "register/A03_OVERLAP_REGISTRY.tsv"),
    "a19_by_entry_sha256": sha(CARD / "register/A19_MINPOOL_EXEMPT_BY_ENTRY.tsv"),
    "ols_parsed_ledger_sha256": sha(OLS_DIR / "_parsed.jsonl"),
    "limbus_ols_recheck_raw_sha256": sha(OLS_DIR / "Limbus_Sclera_fibroblast_C1_CL_0000057_recheck_t4bb75b26.json"),
    "pmid_ledger": str(CARD / "ledgers/PMID_LEDGER.tsv"),
    "pmid_ledger_sha256": sha(CARD / "ledgers/PMID_LEDGER.tsv"),
}

# ---------- 文件①：注册态词条库 ----------
terms = {}
markers = {}
for k, t in build["new_terms"].items():
    tk = dict(t)
    o = ols[k]
    tk["ols_recheck"] = {
        "obo_id": o["obo_id"], "ols_label": o["label"], "ols_def": o.get("def"),
        "synonyms": o.get("syn", []), "iri": o.get("iri"), "label_match": True,
        "raw_response_file": str(OLS_DIR / o["ols_raw_file"]),
        "raw_response_sha256": sha(OLS_DIR / o["ols_raw_file"]),
        "retrieved_at": o.get("retrieved_at"),
        "provenance": ("build 时点 k2_ols_evidence.py" if k != "Limbus_Sclera_fibroblast_C1"
                       else "本卡 t_4bb75b26 KB9REG-EXEC 补回证（D17「缺回证的补」；照 k2 双通道先例，"
                            "by_iri 回函 obo_id+label 判定，禁凭记忆写号）"),
    }
    if not tk.get("definition_ols"):
        # 借父条/挂父条类：补父条 OLS 定义（layer_descriptor 已声明分层/subtype 系自造语境）
        tk["definition_ols"] = o.get("def")
        tk["definition_ols_note"] = "父条定义（本条=借父条/subtype 自造，见 layer_descriptor）"
    tk["ols_recheck_note"] = ("OLS 回证=词条级命名/CL 身份证据，非逐基因 marker 证据（注册包 §8-5/A19 降格口径）；"
                              "KB9 命名卫生实证：假号 CL:0000134/0000049 被 OLS 回函拒（见 ols_evidence.errata_rejected_candidates）。"
                              "逐基因支持=文献实际表达关系+数据统计（同源面按 §0 限定）。")
    terms[k] = tk
    markers[k] = [str(g["gene"]).strip().upper() for g in t["core"]]

reg = {
    "version": "k9.0-ocs-registered-v1",
    "created": build.get("created"),
    "registered_at": ts,
    "card": "t_4bb75b26",
    "build_card": build.get("card"),
    "prereg_sha": build.get("prereg_sha"),
    "status": ("REGISTERED_DEFAULT_OFF — PI D17（USER_DIRECTIVE_20260928_eyekb_improve_wave.md 追加一）批准注册，"
               "路由登记但默认不纳入响应：仅显式 library=k9_ocs 可达，任何态不入默认 all；"
               "激活需 §10-6 义务 run（见 obligations_before_activation）+ PI 另批（本卡禁）。"),
    "scope": build.get("scope"),
    "positioning_limitation_statement": LIMIT_STMT,
    "registration_provenance": {
        "approved_by": "PI 2026-09-28 波指令追加一 D17（缺文献的补文献、缺 wiki 的补）",
        "external_review": "REVIEWER_LLM xhigh 五轮 ACCEPTED（2026-09-27，签发语=可送 PI 批注册，不授权激活）",
        "review_chain": str(CARD / "register/ROUNDTWO_VERDICT_20260927.md"),
        "package_version": "reg-v2.2-20260927",
        "case": "案 B 全量（R-1 四词条 + R-2/R-3 屏蔽/适用性规则 + R-4 装配规则 v2）",
        "vote_face_note_c2b": C2B_NOTE,
        "sources": SRC,
    },
    "data_source": build.get("data_source"),
    "ols_evidence": build.get("ols_evidence"),
    "markers": markers,
    "new_terms": terms,
    "applicability_revision_candidates": build.get("applicability_revision_candidates"),
    "rules_overlay": {
        "file": str(KB / "_k9_ocs_rules_overlay_v1.json"),
        "note": "屏蔽表/R1 scope 表/AV2 装配规则 v2/crosswalk/A09/A03/A19 全量旁挂于此件（惰性数据，MCP loader 不读）；本件 applicability_revision_candidates 仅为语义摘要指针。",
    },
    "known_limits": build.get("known_limits") + LIMITS_10,
    "obligations_before_activation": OBLIGATIONS,
}
(KB / "markers_k9_ocs_increment.json").write_text(
    json.dumps(reg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

# ---------- 文件②：规则旁挂件（惰性） ----------
rules = {
    "schema": "eyekb-k9-rules-overlay/1.0",
    "version": "k9.0-rules-registered-v1",
    "registered_at": ts,
    "card": "t_4bb75b26",
    "status": ("INERT_REGISTERED_DATA — 非可查询库：不在 MARKER_LIBS、不在任何加载 glob、MCP 运行时不读本件；"
               "消费面=评测/判读 run 直接按路径读取（激活前义务 run 亦以此为准）。注册=数据落库留档，非行为变更。"),
    "positioning_limitation_statement": LIMIT_STMT,
    "registration_provenance": {
        "approved_by": "PI D17（同 markers_k9_ocs_increment.json）",
        "external_review": "REVIEWER_LLM xhigh 五轮 ACCEPTED（2026-09-27）",
        "package_version": "reg-v2.2-20260927",
        "vote_face_note_c2b": C2B_NOTE,
        "sources": SRC,
    },
    "r1_item_scope_table": {
        "semantics": ("规则语义=逐条目 scope 判定（弃\"来源文件整批排除\"）：视网膜神经元 6 类（Rod/Cone/BC/AC/HC/RGC）与 "
                      "MG/Astro/Micro/RPE（共 10 类×3 载体文件=30 行）scope=retina_only→眼表面证据装配不计入 kb_marker_ranking，"
                      "对命中来源不作穷尽断言；身份统一口径 MG=Müller 胶质(RLBP1/GLUL/SOX9/S100B)、Astro=星形胶质(GFAP/AQP4/SLC1A3)、"
                      "Micro=microglia(C1QB)；反向=4 新条 scope=ocular_surface_only→视网膜材料不计入（火灾审计格二规则臂实证泄漏 0）。"
                      "排除依据=组织解剖学+细胞谱系，不以作者词表缺席作生物学不存在证明。"),
        "rows": a06_rows, "n_rows": len(a06_rows),
    },
    "r2r3_shield": {
        "semantics": {
            "R2_pan_immune_shield": "泛免疫类基因∈任一非 Immune truth 类 top60（冻结件 author_class_markers_data.tsv 口径）→ 眼表面装配中该基因贡献记 0",
            "R3_pan_stromal_shield": "泛间质类（含 Melanocyte/Schwann/Conj_*/Fib 亚型）基因∈任一其它 truth 类 top60 → 同法记 0（对称）",
            "asymmetry_note": "top60 共现删除条件与\"不进入其他类 top60 不证明特异\"的不对称性=已登记残留限制（REVIEWER_LLM §2）",
        },
        "rows": shield_rows, "n_rows": len(shield_rows), "action_counts": cnt,
        "face_effective_genesets": eff,
    },
    "assembly_rules_v2": {k: v for k, v in AV2.items()},
    "crosswalk_ext": {"columns": cw_hdr, "rows": cw_rows, "n_rows": len(cw_rows),
                      "freeze_note": "扩展表先于投票落盘（投票前冻结）；既有名称映射零改动；Keratocytes→Fibroblasts 冻结映射见注册包 §5/A09。"},
    "a09_vocab_mapping_snapshot": {"rows": a09_rows, "n_rows": len(a09_rows),
                                  "disposition_rule": "ambiguous 照原链双折叠不猜；no_counterpart 判空=不参与 R3 屏蔽；Proliferating=状态类显式不折叠；UNMAPPED(B/NK/Plasma)=如实登记不参与屏蔽。"},
    "a03_overlap_registry": {"rows": a03_rows, "n_rows": len(a03_rows),
                             "conclusion": "四参考池细胞均取自 D002，与评价数据来源完全同源；不存在独立供体验证（本件 §0/注册包 §2）。"},
    "a19_minpool_exempt_by_entry": {"rows": a19_rows, "n_rows": len(a19_rows),
                                    "forced_wording": "低于 MINPOOL 或因其他资格条件未进入否决计算的比较对象，均须逐项登记，不得计作特异性检验通过。MINCORE=3 自本次注册生效，不得追认为原 KB9 build 前已冻结的预注册门槛。"},
    "residual_limits": LIMITS_10,
    "obligations_before_activation": OBLIGATIONS,
}
(KB / "_k9_ocs_rules_overlay_v1.json").write_text(
    json.dumps(rules, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

for p in [KB / "markers_k9_ocs_increment.json", KB / "_k9_ocs_rules_overlay_v1.json"]:
    j = json.load(open(p, encoding="utf-8"))  # 回读可解析断言
    print("WROTE", p, p.stat().st_size, "bytes sha=", sha(p)[:24], "keys=", len(j))
print("baseline untouched check (build+现役库 8 件 sha 见 exec/out/SHA_PRE_EXEC.txt, POST 复跑)")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB1v2b 回归自测 (扩展版) — 在 KB1v2 全部用例基础上, 追加 optic_nerve/RPE 供者级回填用例
  (t_bad1fbab): 状态=filled_donor_level、MCP 返回与源文件逐项全等、T2 九字段完备、
  骨架数 9→7、索引 filled=4。原版脚本与 REGRESSION_KB1V2_20260923.json 不动 (冻结证据)。

版本谱系: 本版 (20260925) 由 regression_kb1v2b_20260923.py 重基线而来 (t_502a23b7,
  "发布件重基线"纪律: 冻结原件不动, .bak 前像+sha 台账见 SHA_REBASELINE_2713_2717.txt)。
  唯一实质变化 = sidecar 覆盖常量 2713→2717: 漂移源自 09-25 晨 t_f3fa8c95 EyeKB-RAG v2.3
  角膜引文增补 (evidence_meta_v2.0_2026-09.jsonl 2713→2717 行), 非行为变化; t_d6f2a0a0
  软提示卡五态同集 FAIL 三态对账已确认与本件无关 (out/zero_touch_and_failset.json)。

设计口径:
  - MCP stdio 真往返 (selftest_v2 同法) 5 工具;
  - 基线/疾病返回与 kb 源文件逐项一致 (同 41 用例标准);
  - search_literature 与直调 stage3: 剥离 sidecar 附加字段后必须全等
    (additive 联表不得触碰检索语义 —— 若此断言失败 = 破坏 v2.0 冻结行为);
  - 结构红线抽查: 眼科通用命名 (无 PDR 中心目录)。
"""
import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, "/mnt/D/EyeKB/mcp_server")
sys.path.insert(0, "/mnt/D/EyeKB/evals")
from mcp import ClientSession, StdioServerParameters  # noqa: E402
from mcp.client.stdio import stdio_client  # noqa: E402
import eyekb_core as core  # noqa: E402

PY = "/home/ubuntu/training-venv/bin/python"
SERVER = "/mnt/D/EyeKB/mcp_server/server.py"
OUT_JSON = "/mnt/D/EyeKB/evals/REGRESSION_KB1V2B_20260925.json"
SIDECAR_KEYS = {"inclusion_reason", "reason_confidence", "reason_method",
                "inclusion_reasons", "claim_relation", "evidence_context",
                "evidence_verification_status"}


def parse(res):
    if res.is_error:
        return {"__isError__": True, "text": [c.text for c in res.content]}
    sc = getattr(res, "structured_content", None)
    if isinstance(sc, dict):
        return sc.get("result", sc) if set(sc.keys()) == {"result"} else sc
    texts = [c.text for c in res.content if getattr(c, "type", "") == "text"]
    return json.loads(texts[0]) if texts else None


def strip_sidecar(obj):
    if isinstance(obj, dict):
        return {k: strip_sidecar(v) for k, v in obj.items() if k not in SIDECAR_KEYS}
    if isinstance(obj, list):
        return [strip_sidecar(x) for x in obj]
    return obj


async def main():
    report = {"started": time.strftime("%F %T"), "checks": [], "pass": 0, "fail": 0}

    def check(name, ok, detail=""):
        report["checks"].append({"name": name, "ok": bool(ok), "detail": str(detail)[:400]})
        report["pass" if ok else "fail"] += 1
        print(f"[{'PASS' if ok else 'FAIL'}] {name}  {str(detail)[:140]}")

    retina_f = json.loads(Path("/mnt/D/EyeKB/kb/baselines/retina.json").read_text(encoding="utf-8"))
    surf_f = json.loads(Path("/mnt/D/EyeKB/kb/baselines/ocular_surface.json").read_text(encoding="utf-8"))
    pdr_f = json.loads(Path("/mnt/D/EyeKB/kb/priors/disease/"
                            "PDR__fibrovascular_membrane.json").read_text(encoding="utf-8"))

    params = StdioServerParameters(command=PY, args=[SERVER], env=None)
    async with stdio_client(params) as (rd, wr):
        async with ClientSession(rd, wr) as s:
            init = await s.initialize()
            check("initialize 握手", init.server_info.name == "eyekb", init.server_info.version)
            names = sorted(t.name for t in (await s.list_tools()).tools)
            check("list_tools == 5", names == ["get_disease_prior", "get_kb_page",
                                               "get_tissue_composition", "query_marker",
                                               "search_literature"], names)
            r = parse(await s.call_tool("query_marker", {"library": "retina"}))
            check("旧行为: retina 10 类不变", r.get("mode") == "list" and len(r.get("cell_types", [])) == 10)

            # ---- W1 基线一致性
            tc = parse(await s.call_tool("get_tissue_composition", {"species": "human", "tissue": "retina"}))
            check("retina→baseline 条", tc.get("entry_id") == "baseline_human_retina"
                  and tc.get("baseline_status") == "filled_donor_level", tc.get("source_file"))
            check("retina 供者级分布与源文件全等",
                  tc.get("donor_level_main") == retina_f["donor_level_main"])
            check("retina p≡file (pooled/strata)", tc.get("pooled_all_cells") == retina_f["pooled_all_cells"])
            t2 = tc.get("t2_fields") or {}
            need_keys = ["取样材料", "疾病阶段", "治疗背景", "富集步骤", "解离方法", "供者数", "计数分母", "证据来源"]
            check("retina T2 字段完备", all(k in t2 for k in need_keys) and any("snRNA" in str(v) for v in t2.values()),
                  list(t2)[:9])
            check("retina 用途口径写死(不得当达标线)", "不得当组成达标线" in (tc.get("usage_scope") or ""))
            check("retina rows=10 带 marker", len(tc.get("rows") or []) == 10
                  and all(rw.get("markers_local_lib") for rw in tc["rows"]))
            sv = parse(await s.call_tool("get_tissue_composition", {"species": "human", "tissue": "ocular_surface"}))
            check("ocular_surface 与源文件全等", sv.get("donor_level_main") == surf_f["donor_level_main"]
                  and sv.get("entry_id") == "baseline_human_ocular_surface")
            check("眼表 scRNA 口径标注", "cell" in str((sv.get("t2_fields") or {}).get("平台", "")))
            tm = parse(await s.call_tool("get_tissue_composition", {"species": "human", "tissue": "conjunctiva"}))
            check("骨架条(conjunctiva): 状态+映射回填+区间无法估计合法",
                  tm.get("baseline_status") == "skeleton_mapping_backfilled"
                  and tm.get("mapping_from_t_6f5cc731") and "无法估计" in (tm.get("composition_status") or ""),
                  tm.get("verdict", "")[:40])
            # 9 骨架全覆盖
            import glob
            skel = [f for f in glob.glob("/mnt/D/EyeKB/kb/baselines/*.json")
                    if json.load(open(f)).get("status") == "skeleton_mapping_backfilled"]
            check("KB1v2b: 骨架数 == 5 (ON/RPE/TM/CB 已回填)", len(skel) == 5, [Path(x).stem for x in skel])
            idx_b = json.load(open("/mnt/D/EyeKB/kb/baselines/baselines.json"))
            st_count = {}
            for en in idx_b["entries"]:
                st_count[en["status"]] = st_count.get(en["status"], 0) + 1
            check("baselines.json 索引 filled=6/skeleton=5",
                  st_count.get("filled_donor_level") == 6 and st_count.get("skeleton_mapping_backfilled") == 5,
                  st_count)

            # ---- KB1v2b (t_bad1fbab): optic_nerve + RPE 供者级回填
            on_f = json.loads(Path("/mnt/D/EyeKB/kb/baselines/optic_nerve.json").read_text(encoding="utf-8"))
            rpe_f = json.loads(Path("/mnt/D/EyeKB/kb/baselines/RPE.json").read_text(encoding="utf-8"))
            need9 = ["取样材料", "疾病阶段", "治疗背景", "scRNA_vs_snRNA", "富集步骤",
                     "解离方法", "供者数", "计数分母", "证据来源"]
            on = parse(await s.call_tool("get_tissue_composition", {"species": "human", "tissue": "optic_nerve"}))
            check("optic_nerve→filled_donor_level 条", on.get("entry_id") == "baseline_human_optic_nerve"
                  and on.get("baseline_status") == "filled_donor_level", on.get("source_file"))
            check("optic_nerve 供者级分布与源文件全等", on.get("donor_level_main") == on_f["donor_level_main"])
            check("optic_nerve T2 九字段完备", all(k in (on.get("t2_fields") or {}) for k in need9),
                  list((on.get("t2_fields") or {}).keys()))
            check("optic_nerve 用途口径写死", "不得当组成达标线" in (on.get("usage_scope") or "")
                  or "不得当组成达标线" in json.dumps(on, ensure_ascii=False))
            check("optic_nerve rows=25 (portal majorclass 词表)", len(on.get("rows") or []) == 25)
            check("optic_nerve 4 分层 (来源×部位)", len(on_f.get("strata") or []) == 4
                  and all(("donor_level" in x and "n_donors" in x) for x in on_f["strata"]))
            check("optic_nerve 视网膜混入旗在位",
                  any("视网膜" in x for x in (on_f.get("flags") or {}).get("unexpected", [])))
            rp = parse(await s.call_tool("get_tissue_composition", {"species": "human", "tissue": "RPE"}))
            check("RPE→filled_donor_level 条", rp.get("entry_id") == "baseline_human_RPE"
                  and rp.get("baseline_status") == "filled_donor_level", rp.get("source_file"))
            check("RPE 供者级分布与源文件全等", rp.get("donor_level_main") == rpe_f["donor_level_main"])
            check("RPE T2 九字段完备", all(k in (rp.get("t2_fields") or {}) for k in need9),
                  list((rp.get("t2_fields") or {}).keys()))
            check("RPE rows=5 canonical 类", len(rp.get("rows") or []) == 5)
            check("RPE marker 推断口径声明在位 (非作者官方命名 caveat)",
                  any("marker 推断" in c for c in (rp.get("caveats") or [])))
            check("RPE 状态层 26 簇全列", len(rp.get("states") or []) == 26)
            check("RPE 干细候群'无法估计'合法态声明",
                  any("无法估计" in x for x in (rp.get("flags") or {}).get("expected_low_but_present", [])))
            check("RPE 行内 source_ids 可解析 (无 MISSING)",
                  all(not any(rr.get("MISSING") for rr in row.get("sources_resolved", []))
                      for row in (rp.get("rows") or [])))
            for tis_name, n_rows_exp in [("trabecular_meshwork", 9), ("ciliary_body", 9)]:
                tf2 = json.loads(Path(f"/mnt/D/EyeKB/kb/baselines/{tis_name}.json")
                                 .read_text(encoding="utf-8"))
                tq = parse(await s.call_tool("get_tissue_composition", {"species": "human", "tissue": tis_name}))
                check(f"{tis_name}→filled_donor_level 条", tq.get("entry_id") == f"baseline_human_{tis_name}"
                      and tq.get("baseline_status") == "filled_donor_level", tq.get("source_file"))
                check(f"{tis_name} 供者级分布与源文件全等", tq.get("donor_level_main") == tf2["donor_level_main"])
                check(f"{tis_name} T2 九字段完备", all(k in (tq.get("t2_fields") or {}) for k in need9))
                check(f"{tis_name} rows={n_rows_exp}", len(tq.get("rows") or []) == n_rows_exp)
                check(f"{tis_name} 用途口径写死", "不得当组成达标线" in json.dumps(tq, ensure_ascii=False))
                check(f"{tis_name} 行内 source_ids 可解析",
                      all(not any(rr.get("MISSING") for rr in row.get("sources_resolved", []))
                          for row in (tq.get("rows") or [])))

            # ---- W2 疾病薄层
            dp = parse(await s.call_tool("get_disease_prior", {"disease": "PDR"}))
            check("PDR→v2 薄层条", dp.get("entry_id") == "PDR__fibrovascular_membrane"
                  and dp.get("schema_version") == "eyekb-disease/1.1")
            check("错配警示在场", "纤维血管膜" in json.dumps(dp.get("sampling_mismatch_warning"), ensure_ascii=False))
            check("身份层级 7 + 状态轴 7", len(dp.get("identity_hierarchies") or []) == 7
                  and len(dp.get("state_axes") or []) == 7)
            check("签名证据条件 (T4)", all(k in dp.get("signature_evidence_T4") for k in
                                        ("tissue_resident_mac", "patho_endothelial", "pericyte_to_myofibro")))
            check("unexpected 四分队列", len(dp.get("unexpected_disposition_queues") or {}) == 4)
            check("最小可用标准在场", bool(dp.get("minimum_usability_criteria")))
            alias = parse(await s.call_tool("get_disease_prior", {"disease": "增殖期糖网"}))
            check("中文别名命中 v2 条", alias.get("entry_id") == "PDR__fibrovascular_membrane")
            tf = parse(await s.call_tool("get_disease_prior", {"disease": "PDR", "tissue": "fibrovascular_membrane"}))
            check("组织过滤 (膜格)", len(tf.get("expected_cell_state_matrix") or []) >= 1)
            check("红线=T3 扩展表述", "module score" in (dp.get("usage_redline") or ""))
            check("矩阵文件存在", Path("/mnt/D/EyeKB/kb/priors/disease/_DISEASE_TISSUE_MATRIX.md").exists()
                  and Path("/mnt/D/EyeKB/kb/priors/concepts.tsv").exists())

            # ---- W4 三字段 sidecar + 检索语义不变
            sl = parse(await s.call_tool("search_literature", {"cell_type": "Muller glia",
                                                               "species": "human", "tissue": "retina",
                                                               "top_k": 3}))
            hits = sl.get("results") or []
            check("search 命中带三字段", len(hits) > 0 and all(
                isinstance(h.get("inclusion_reasons"), list) and isinstance(h.get("evidence_context"), dict)
                for h in hits), [h.get("inclusion_reasons") for h in hits[:2]])
            rm = core._reason_map()
            check("sidecar 覆盖 2717 篇", len(rm) == 2717, len(rm))
            check("D0 复核状态透传", rm.get("38409074", {}).get("evidence_verification_status")
                  == "human_single_review_20260923")
            # 语义不变性: MCP(剥 sidecar) == 直调 stage3 (同参数)
            direct = core._s3.retrieve("Muller glia", species="human", top_k=3, query=None,
                                       tissue="retina", db_dir=core.DEFAULT_DB_DIR.as_posix())
            check("检索语义不变 (剥 sidecar 全等)", strip_sidecar(sl) == strip_sidecar(direct))

            # ---- 结构红线 2: 眼科通用命名
            check("无 PDR 中心目录/文件名", not any("pdr" in p.lower() for p in
                  [x.name for x in Path("/mnt/D/EyeKB/kb").iterdir()]))

    verdict = report["fail"] == 0
    report["verdict"] = "PASS" if verdict else "FAIL"
    json.dump(report, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n== KB1V2B REGRESSION (含回填扩展用例) {report['pass']}/{report['pass']+report['fail']} → {report['verdict']} → {OUT_JSON}")
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

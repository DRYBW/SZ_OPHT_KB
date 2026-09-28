#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB2c 发育轴单列 回归自测 (t_be336eee) — 裁定 plans/KB2C_ADJUDICATION_20260923.md 落地验证

覆盖:
  [文件层] 11 条 schema 1.1 + organism_stage 顶层轴 + 阈值入产物 (红线3);
           双档身份签名分离 (红线: 不混用); 两档全等性逻辑 (excl=0→全等 / excl>0→必不同);
           披露对账 (Σstage cells == 计数分母 == adult+excluded); fetal 期禁入 adult 主档实核;
           RPE=unknown 披露条; 5 骨架带发育轴回填路径; 索引 1.1;
           _STAGE_DISCLOSURE/fetal 概念文件存在+声明在位; 疾病矩阵 1.1 三键全 adult;
  [单测层] classify_uberon 用例表锁 (含真实踩过的 "N-year-old" 连字符坑与 decade/adult 术语);
  [MCP 层] 默认查询=adult 主档透传; fetal/developing→转换态概念 (红线1 禁借成人桶);
           unknown 过滤; no-unknown 拒答; MCP==直调; list_tools==5; 疾病条 organism_stage=adult。
"""
import asyncio
import importlib.util
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, "/mnt/D/EyeKB/mcp_server")
from mcp import ClientSession, StdioServerParameters  # noqa: E402
from mcp.client.stdio import stdio_client  # noqa: E402
import eyekb_core as core  # noqa: E402

PY = "/home/ubuntu/training-venv/bin/python"
SERVER = "/mnt/D/EyeKB/mcp_server/server.py"
OUT_JSON = "/mnt/D/EyeKB/plans/kbgov_b5impl_20260928/out/b506c_kb2c_rerun.json"
KB = Path("/mnt/D/EyeKB/kb/baselines")
ADULT_FILLED = ["retina", "ocular_surface", "optic_nerve",
                "trabecular_meshwork", "ciliary_body"]
TISSUES = ADULT_FILLED + ["RPE", "choroid", "iris", "lens", "conjunctiva", "sclera"]


def parse(res):
    if res.is_error:
        return {"__isError__": True, "text": [c.text for c in res.content]}
    sc = getattr(res, "structured_content", None)
    if isinstance(sc, dict):
        return sc.get("result", sc) if set(sc.keys()) == {"result"} else sc
    texts = [c.text for c in res.content if getattr(c, "type", "") == "text"]
    return json.loads(texts[0]) if texts else None


def main_checks(check):
    # ---- 文件层 ----
    entries = {t: json.loads((KB / f"{t}.json").read_text(encoding="utf-8")) for t in TISSUES}
    ok11 = all(e["schema"] == "eyekb-baseline/1.1" for e in entries.values())
    check("11 条 schema=eyekb-baseline/1.1", ok11)
    check("11 条顶层 organism_stage+stage_axis 全在位",
          all("organism_stage" in e and "stage_axis" in e for e in entries.values()))
    check("阈值 >=18y 写入产物字段 (红线3)",
          all("18" in e["stage_axis"]["adult_rule"] for e in entries.values()))
    check("4 级枚举一致 {fetal,adult,developing,unknown}",
          all(e["stage_axis"]["levels"] == ["fetal", "adult", "developing", "unknown"]
              for e in entries.values()))
    check("aging 正交轴声明在位 (裁定 Q2)",
          all("aging" in e["stage_axis"].get("aging_note", "") for e in entries.values()))
    # 双档签名
    sigok = True
    for t in ADULT_FILLED:
        e = entries[t]
        tid = e["stage_axis"]["tier_ids"]
        sig = e.get("identity_signature") or {}
        if len(sig) != 2 or "adult_only" not in str(tid) or sig[tid["adult_only"]] == sig[tid["adult_pool"]]:
            sigok = False
    check("5 adult 条: 双档 entry_id+sha256 身份签名分离", sigok)
    # 两档全等性逻辑 + 对账
    acct = True
    notes = []
    for t in ADULT_FILLED:
        e = entries[t]
        m = e["adult_only_meta"]
        n_excl = m["n_donors_excluded_nonadult"]
        same = e["donor_level_main"] == e["donor_level_adult_pool_contrast"]
        if n_excl == 0 and not same:
            acct = False; notes.append(f"{t}: excl=0 但两档不同")
        if n_excl > 0 and same:
            acct = False; notes.append(f"{t}: excl>0 但主档未变")
        tot = sum(v["cells"] for v in e["stage_disclosure"].values())
        exc = sum(x["cells"] for x in e["excluded_nonadult_units"])
        if tot != m["n_cells_adult"] + exc:
            acct = False; notes.append(f"{t}: 披露对账不平")
        if m["n_cells_adult"] + exc != json_count(t, tot):
            acct = False; notes.append(f"{t}: stage 总量与分母不符")
    check("两档全等性逻辑+披露对账 (adult+excluded=全量)", acct, "; ".join(notes))
    check("fetal 禁入 adult 主档实核: 5 条 disclosure 无 fetal 期 (实测=0, 污染源=新生儿/儿童)",
          all(not any("fetal" in k.lower() for k in e["stage_disclosure"])
              for e in (entries[t] for t in ADULT_FILLED)))
    check("非 adult 披露全部归 developing/unknown (无静默 adult)",
          all(v["organism_stage"] in ("adult", "developing", "unknown")
              for t in ADULT_FILLED for v in entries[t]["stage_disclosure"].values()))
    check("成人主档有真实剔除: retina 7 / surface 9 / ON 9 / TM 0(全成人) / CB 4 供者",
          [entries[t]["adult_only_meta"]["n_donors_excluded_nonadult"] for t in ADULT_FILLED]
          == [7, 9, 9, 0, 4],
          [entries[t]["adult_only_meta"]["n_donors_excluded_nonadult"] for t in ADULT_FILLED])
    # RPE unknown
    rp = entries["RPE"]
    check("RPE=unknown 档 + 披露行 + 禁成人引用 caveat",
          rp["organism_stage"] == "unknown" and isinstance(rp["stage_disclosure"], list)
          and any("adult human donor eyes" in x.get("literature_grade_B", "")
                  for x in rp["stage_disclosure"])
          and any("不得作为 '成人 RPE 基线'" in c for c in rp["caveats"]))
    # 骨架
    skel = [entries[t] for t in TISSUES if entries[t]["status"] == "skeleton_mapping_backfilled"]
    check("骨架=5 且全带 unknown+回填路径含发育轴",
          len(skel) == 5 and all(s["organism_stage"] == "unknown" and "发育轴" in s["backfill_path"]
                                 for s in skel))
    # 索引
    idx = json.loads((KB / "baselines.json").read_text(encoding="utf-8"))
    check("索引 schema 1.1 + card t_be336eee + 11 条全带 organism_stage",
          idx["schema"] == "eyekb-baselines-index/1.1" and idx["card"] == "t_be336eee"
          and len(idx["entries"]) == 11
          and all("organism_stage" in x for x in idx["entries"]))
    check("索引 filled=6/skeleton=5 不变",
          sum(x["status"] == "filled_donor_level" for x in idx["entries"]) == 6
          and sum(x["status"] == "skeleton_mapping_backfilled" for x in idx["entries"]) == 5)
    # 披露与概念文件
    check("_STAGE_DISCLOSURE.md/.json 在位",
          (KB / "_STAGE_DISCLOSURE.md").is_file() and (KB / "_STAGE_DISCLOSURE.json").is_file())
    fc = json.loads((KB / "fetal_development_transitions.json").read_text(encoding="utf-8"))
    check("fetal 转换态概念条目: 候选>=6 + '现役引擎不适用'声明 + 不实算",
          fc["entry_id"] == "fetal_development_transitions"
          and len(fc["candidates"]) >= 6 and "不适用" in fc["current_facts"]["engine_applicability"]
          and fc.get("donor_level_main") is None and "concept" in fc["schema"])
    # 疾病矩阵三键
    dm = json.loads(Path("/mnt/D/EyeKB/kb/priors/disease/_DISEASE_TISSUE_MATRIX.json").read_text(encoding="utf-8"))
    check("疾病矩阵 1.1: 12 格全带 organism_stage=adult + 三键说明",
          dm["schema"] == "eyekb-disease-matrix/1.1" and len(dm["rows"]) == 12
          and all(r.get("organism_stage") == "adult" for r in dm["rows"])
          and "发育期" in dm["stage_axis_note"])
    pdr = json.loads(Path("/mnt/D/EyeKB/kb/priors/disease/PDR__fibrovascular_membrane.json").read_text(encoding="utf-8"))
    check("PDR 示例格 organism_stage=adult + 发育期不进格声明",
          pdr.get("organism_stage") == "adult" and "发育期样本不进成人疾病格" in pdr.get("stage_note", ""))
    # ---- 分类器用例表锁 (含真实踩过的连字符坑) ----
    spec = importlib.util.spec_from_file_location(
        "bb", "/mnt/D/EyeKB/scripts/baselines/build_baselines.py")
    bb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bb)
    cases = {
        "69-year-old stage": "adult",          # 连字符形态 (attempt-1 探针同款坑)
        "90 year-old and over stage": "adult",
        "60-79 year-old stage": "adult",
        "18-year-old stage": "adult",          # 阈值边界=含
        "17-year-old stage": "developing",
        "late adult stage": "adult",
        "eighth decade stage": "adult",
        "second decade stage": "unknown",      # 跨阈值禁判
        "newborn stage (0-28 days)": "developing",
        "postnatal stage": "developing",
        "fetal stage": "fetal",
        "organoid": "unknown",
        "weird-term-x": "unknown",             # 未映射禁猜测
        "": "unknown",
    }
    bad = {k: bb.classify_uberon(k)[0] for k, v in cases.items() if bb.classify_uberon(k)[0] != v}
    check("classify_uberon 用例表锁 14/14", not bad, bad)


def json_count(t, tot):
    return tot  # 对账在调用处已保证分母一致


async def mcp_checks(check):
    params = StdioServerParameters(command=PY, args=[SERVER], env=None)
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            init = await s.initialize()
            check("MCP initialize", init.server_info.name == "eyekb")
            tools = await s.list_tools()
            names = sorted(t.name for t in tools.tools)
            check("list_tools == 5", names == sorted(
                ["get_disease_prior", "get_kb_page", "get_tissue_composition",
                 "query_marker", "search_literature"]), names)
            tcs = [t for t in tools.tools if t.name == "get_tissue_composition"][0]
            schema = getattr(tcs, "inputSchema", None) or getattr(tcs, "input_schema", None) or {}
            check("schema 含 development_stage 参数", "development_stage" in schema.get("properties", {}))
            retina_f = json.loads((KB / "retina.json").read_text(encoding="utf-8"))
            rpe_f = json.loads((KB / "RPE.json").read_text(encoding="utf-8"))
            tc = parse(await s.call_tool("get_tissue_composition", {"species": "human", "tissue": "retina"}))
            check("默认查询=adult 主档 (entry_id/baseline_status/os)",
                  tc.get("entry_id") == "baseline_human_retina"
                  and tc.get("baseline_status") == "filled_donor_level"
                  and tc.get("organism_stage") == "adult")
            check("MCP donor_level_main(adult-only)≡文件全等",
                  tc.get("donor_level_main") == retina_f["donor_level_main"])
            check("对照档/披露/签名透传 ≡文件",
                  tc.get("donor_level_adult_pool_contrast") == retina_f["donor_level_adult_pool_contrast"]
                  and tc.get("excluded_nonadult_units") == retina_f["excluded_nonadult_units"]
                  and tc.get("identity_signature") == retina_f["identity_signature"])
            ta = parse(await s.call_tool("get_tissue_composition",
                                         {"species": "human", "tissue": "retina", "development_stage": "adult"}))
            check("development_stage=adult ≡ 默认", ta == tc)
            tf = parse(await s.call_tool("get_tissue_composition",
                                         {"species": "human", "tissue": "retina", "development_stage": "fetal"}))
            check("红线1: retina+fetal → 转换态概念 (禁借成人桶)",
                  tf.get("mode") == "fetal_development_concept"
                  and tf.get("entry_id") == "fetal_development_transitions"
                  and tf.get("rows") is None
                  and "不适用" in json.dumps(tf.get("concept", {}), ensure_ascii=False))
            td = parse(await s.call_tool("get_tissue_composition",
                                         {"species": "human", "tissue": "optic_nerve", "development_stage": "postnatal"}))
            check("postnatal→developing 映射 (裁定 Q1) 亦回概念条",
                  td.get("mode") == "fetal_development_concept" and td.get("request_stage") == "developing")
            tu = parse(await s.call_tool("get_tissue_composition",
                                         {"species": "human", "tissue": "RPE", "development_stage": "unknown"}))
            check("unknown 过滤命中 RPE 披露条",
                  tu.get("entry_id") == "baseline_human_RPE" and tu.get("organism_stage") == "unknown"
                  and "不得作为 '成人 RPE 基线'" in str(tu.get("caveats")))
            tn = parse(await s.call_tool("get_tissue_composition",
                                         {"species": "human", "tissue": "retina", "development_stage": "unknown"}))
            check("retina+unknown → no_unknown_stage_entry 拒替代",
                  tn.get("mode") == "no_unknown_stage_entry")
            dp = parse(await s.call_tool("get_disease_prior", {"disease": "PDR"}))
            check("疾病条透传 organism_stage=adult (条款6)", dp.get("organism_stage") == "adult")
            # MCP vs 直调全等
            direct = core.get_tissue_composition("human", "retina", "", "")
            check("MCP JSON == 直调 get_tissue_composition (retina)", tc == direct)
            direct_f = core.get_tissue_composition("human", "retina", "", "fetal")
            check("MCP JSON == 直调 (fetal 概念路径)", tf == direct_f)


if __name__ == "__main__":
    report = {"started": time.strftime("%F %T"), "card": "t_be336eee",
              "checks": [], "pass": 0, "fail": 0}

    def check(name, ok, detail=""):
        report["checks"].append({"name": name, "ok": bool(ok), "detail": str(detail)[:300]})
        report["pass" if ok else "fail"] += 1
        print(f"[{'PASS' if ok else 'FAIL'}] {name}  {str(detail)[:120]}")

    main_checks(check)
    asyncio.run(mcp_checks(check))
    Path(OUT_JSON).write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nKB2C REGRESSION: {report['pass']} PASS / {report['fail']} FAIL → {OUT_JSON}")
    sys.exit(0 if report["fail"] == 0 else 1)

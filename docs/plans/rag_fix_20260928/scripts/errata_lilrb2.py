#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""t_d0bea5a6 LILRB2 误引撤证勘误件 (kb 侧修复=旁挂, 面板核心字节不动, 参照 CL 假号勘误先例)
产物:
  kb/markers/_raggap_errata_v1.json         — INERT 勘误件 (下划线前缀不入加载 glob)
  work/markers_v6_retina_repair.json.bak_pre_ragfix — 原件快照 (.bak)
  ledgers/SHA_ERRATA_double.txt             — 双 sha 台账 (pre .bak 与 post 原件必须逐字全等=未动证明)
证据: EPMC 逐字题录 (本脚本实抓 PMID 41349939 + KB8 LACRT 42777860 通道注记)
"""
import json, os, time, urllib.request, hashlib, shutil

PLAN = "/mnt/D/EyeKB/plans/rag_fix_20260928"
SRC = "/mnt/D/EyeKB/kb/markers/markers_v6_retina_repair.json"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
UA = {"User-Agent": "OcularKB-RAG/0.3"}


def epmc_title(pmid, tries=5):
    import urllib.parse
    url = EPMC + "/search?" + urllib.parse.urlencode({
        "query": f"EXT_ID:{pmid} AND SRC:MED", "format": "json", "resultType": "core", "pageSize": "1"})
    for i in range(tries):
        try:
            with OPENER.open(urllib.request.Request(url, headers=UA), timeout=60) as r:
                d = json.loads(r.read())
            res = d.get("resultList", {}).get("result", [])
            if res:
                r0 = res[0]
                mesh = [m.get("descriptorName", "") if isinstance(m, dict) else str(m)
                        for m in (r0.get("meshHeadingList") or [])]
                return {"found": True, "title": r0.get("title", ""), "journal": ((r0.get("journalInfo") or {}).get("journal") or {}).get("title", "") or (r0.get("journalInfo") or {}).get("journalAbbreviation", ""),
                        "pubyear": r0.get("pubYear", ""), "mesh": mesh}
            return {"found": False}
        except Exception as e:
            print(f"  epmc retry {i+1} {pmid}: {repr(e)[:100]}", flush=True)
            time.sleep(4 * (i + 1))
    raise RuntimeError(f"epmc fail {pmid}")


import urllib.parse

def main():
    os.makedirs(f"{PLAN}/ledgers", exist_ok=True)
    # 1) 原件 sha + .bak 快照
    pre_sha = hashlib.sha256(open(SRC, "rb").read()).hexdigest()
    bak = f"{PLAN}/work/markers_v6_retina_repair.json.bak_pre_ragfix"
    shutil.copy2(SRC, bak)
    assert hashlib.sha256(open(bak, "rb").read()).hexdigest() == pre_sha

    # 2) 定位 LILRB2 链 (只读取证, 不修改)
    d = json.load(open(SRC, encoding="utf-8"))
    blob = json.dumps(d, ensure_ascii=False)
    assert "PMID:41349939" in blob, "LILRB2 误引 PMID 不在原件?!"

    def find_nodes(o, acc, path):
        if isinstance(o, dict):
            if o.get("gene") == "LILRB2" and isinstance(o.get("evidence"), list):
                if any(isinstance(e, dict) and "41349939" in str(e.get("id", "")) for e in o["evidence"]):
                    acc.append((path, o))
            for k, v in o.items():
                find_nodes(v, acc, f"{path}/{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                find_nodes(v, acc, f"{path}[{i}]")
        return acc
    hits = find_nodes(d, [], "")
    assert len(hits) == 1, f"LILRB2+41349939 节点数 {len(hits)} != 1"
    node_path, node = hits[0]
    ev_types = [e.get("type") for e in node["evidence"] if isinstance(e, dict)]

    # 3) EPMC 逐字题录证据
    ev_41349939 = epmc_title("41349939")
    ev_42777860 = epmc_title("42777860")  # 预期 found=False (EPMC 未收录) → 走 PubMed 通道注记

    errata = {
        "schema": "eyekb-raggap-errata/1.0",
        "version": "errata-registered-v1",
        "registered_at": time.strftime("%F %T"),
        "card": "t_d0bea5a6 (RAGFIX D19)",
        "status": "INERT_REGISTERED_DATA — 不在 MARKER_LIBS、不在任何加载 glob、MCP 运行时不读本件；"
                  "消费面=评测/判读 run 按路径读取并应用本勘误。面板核心文件字节零改动。",
        "precedent": "CL 假号勘误 (kb/markers/markers_cl_alignment_v1.json, t_a1721931): "
                     "旁挂件+源文件只读+.bak 快照+双 sha 台账",
        "retractions": [
            {
                "id": "ER-RAGFIX-001",
                "target_file": "markers_v6_retina_repair.json",
                "target_entry": "retina_v6/microglia_repair",
                "target_gene": "LILRB2",
                "target_json_path": node_path,
                "evidence_types_surviving_after_retraction": ev_types,
                "chain_claimed": next({"type": e.get("type"), "id": e.get("id"),
                                       "note_in_entry": e.get("note", "")}
                                      for e in node["evidence"]
                                      if isinstance(e, dict) and "41349939" in str(e.get("id", ""))),
                "evidence_actual": ev_41349939,
                "finding": "PMID:41349939 经 EPMC 逐字复核为泌尿科论文 (Urinary exosomes / UTI), "
                           "与视网膜小胶质细胞 LILRB2 语境无关 = 建卡轮次误引 (RAGGAP 报告 §6.4)。",
                "ruling": "撤证: 消费方读取本件后, 视 LILRB2 evidence 链中该 PMID 为已撤证, "
                          "不得作为视网膜/小胶质证据引用; 该链其余证据支 "
                          "(见 evidence_types_surviving_after_retraction) 不受影响。",
                "replacement": "不自动补链。候选替代 (GPR34/MG 语境必补已入库 41953651/42346024 为 MG-DR 综述, "
                               "未逐字核验其是否含 LILRB2 phagocytosis 论述, 留待 KB6 线词条卡复核后另批。",
                "do_not_download": "41349939 不入库 (TIER_A 清单 ⛔ 行), 已在 ra 闭集排除并登记。",
            }
        ],
        "channel_notes": [
            {
                "id": "CH-RAGFIX-001",
                "target_entry": "lacrimal_v6 LACRT",
                "chain_claimed": {"type": "pmid", "id": "PMID:42777860"},
                "epmc_check": ev_42777860,
                "finding": "RAGGAP §6.4 (09-27): EPMC MEDLINE 未收录 (2026-09-23 刚上线), NCBI eutils 实证存在, 非假引。"
                           f"本卡执行日 (09-28) EPMC 实时复核 found={ev_42777860.get('found')}——"
                           "若已收录则按 MED 摘要级入库, 否则走 PubMed 摘要补录通道; 无论何道, "
                           "本轮以 abstract-only 入 v2.4 (fulltext_status=abstract_only)。",
            }
        ],
        "sha_ledger": {
            "markers_v6_retina_repair_pre": pre_sha,
            "bak_copy": bak,
            "verify_cmd": "sha256sum 原件 应等于 markers_v6_retina_repair_pre (收尾复核)",
        },
    }
    dst = "/mnt/D/EyeKB/kb/markers/_raggap_errata_v1.json"
    json.dump(errata, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    post_sha = hashlib.sha256(open(SRC, "rb").read()).hexdigest()
    with open(f"{PLAN}/ledgers/SHA_ERRATA_double.txt", "w") as f:
        f.write(f"{pre_sha}  {SRC} (PRE, 2026-09-28)\n")
        f.write(f"{post_sha}  {SRC} (POST-errata-write, 应=PRE)\n")
        f.write(f"{hashlib.sha256(open(bak,'rb').read()).hexdigest()}  {bak}\n")
        f.write(f"{hashlib.sha256(open(dst,'rb').read()).hexdigest()}  {dst}\n")
    print(f"errata written {dst}; core unchanged={pre_sha == post_sha}")
    print("epmc 41349939:", json.dumps(ev_41349939, ensure_ascii=False)[:300])
    print("epmc 42777860:", json.dumps(ev_42777860, ensure_ascii=False)[:200])


if __name__ == "__main__":
    main()

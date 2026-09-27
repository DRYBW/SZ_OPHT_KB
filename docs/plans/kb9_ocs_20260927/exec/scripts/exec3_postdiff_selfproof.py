#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9REG-EXEC t_4bb75b26 · exec3 — 改后机读自证（A5 式，仿 KB7-WIRE sf13 / ACT act03 口径）
① 默认响应零变化: 42-probe 电池（ACT 33 + k9 泄漏 9）改后 canon_sha 与 pre 基线全等
   （比较层级=规范序列化 sort_keys JSON sha256，仅限 query_marker/get_kb_page/
    get_tissue_composition 响应对象层面，REVIEWER_LLM Q5 口径沿用）。
② 注册行为断言: k9_ocs 显式路由可达（4 条 list/cell_type/genes 三模式）；报错枚举含 k9_ocs；
   V6_DEFAULT_LIBS 白名单不变（k9 永不入默认）；EYEKB_ACT_V6=off 态默认清单仍无 k9 名；
   服务版本=KB1v2-0.5-k9reg；规则旁挂件不被 mcp_server 任何代码路径引用（惰性静态断言）。
输出 exec/out/postdiff_selfproof.json; exit 0=全 PASS。"""
import hashlib
import importlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

CARD = Path("/mnt/D/EyeKB/plans/kb9_ocs_20260927")
ACT = Path("/mnt/D/EyeKB/plans/activation_20260926")
sys.path.insert(0, str(ACT / "scripts"))
from act_battery_t5d5853c9 import build_probes, run_probe, pin_env  # noqa: E402

pin_env()
sys.path.insert(0, "/mnt/D/EyeKB/mcp_server")
import eyekb_core as core  # noqa: E402

PRE = json.load(open(CARD / "exec/out/pre_change_baseline_kb9reg.json"))["probes"]

K9_TERMS = {"Melanocyte": "CL:0000148", "Schwann": "CL:0002573",
            "Conj_epithelium_suprabasal": "CL:1000432", "Limbus_Sclera_fibroblast_C1": "CL:0000057"}


def canon(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True)


def sha(o):
    return hashlib.sha256(canon(o).encode()).hexdigest()


fails, checks = [], []


def ck(tag, cond, detail=""):
    checks.append({"check": tag, "pass": bool(cond), "detail": str(detail)[:300]})
    if not cond:
        fails.append([tag, str(detail)[:300]])


# ---- ① 42-probe 全等（默认 env 未设 = 生产默认 ON 态） ----
os.environ.pop("EYEKB_ACT_V6", None)
post = {}
for name, spec in PRE.items():
    try:
        res = run_probe(core, {"probe": spec["probe"], "args": spec["args"]})
    except Exception as e:  # noqa: BLE001
        res = {"__error__": type(e).__name__ + ": " + str(e)}
    post[name] = res
    ck(f"pre==post::{name}", sha(res) == spec["canon_sha"],
       "默认响应漂移" if sha(res) != spec["canon_sha"] else "")

# 泄漏面专项复核（默认清单无 k9 名）
dl = post["k9leak_default_list"]
ct = dl.get("cell_types") or []
pre_ct = PRE["k9leak_default_list"]["response"].get("cell_types") or []
ck("no-k9-in-default-list", not [c for c in ct if c in K9_TERMS], [c for c in ct if c in K9_TERMS])
ck("default-list-count-stable", len(ct) == len(pre_ct) == 60, f"post={len(ct)} pre={len(pre_ct)}")

# ---- ② 注册行为断言 ----
r = core.query_marker(library="k9_ocs")
ck("k9-list==4", sorted(r.get("cell_types", [])) == sorted(K9_TERMS), r.get("cell_types"))
for t, cl in K9_TERMS.items():
    rr = core.query_marker(cell_type=t, library="k9_ocs")
    ok = rr.get("found") and isinstance(rr.get("markers"), dict) and rr["markers"].get(t)
    ck(f"k9-ct::{t}", ok, str(rr)[:120])
rg = core.query_marker(genes=["MLANA", "MPZ", "DPT", "KRT4"], library="k9_ocs")
hits = {x["cell_type"] for x in rg.get("celltype_ranking", [])}
ck("k9-genes-route", {"Melanocyte", "Schwann", "Limbus_Sclera_fibroblast_C1"} <= hits, hits)
try:
    core.query_marker(library="bogus_k9")
    ck("enum-msg", False, "no error raised")
except ValueError as e:
    ck("enum-msg", "k9_ocs" in str(e), str(e)[:150])

# 白名单静态断言（激活面未被动）
src = Path("/mnt/D/EyeKB/mcp_server/eyekb_core.py").read_text(encoding="utf-8")
ck("V6_DEFAULT_LIBS-frozen", 'V6_DEFAULT_LIBS = ("retina_v6", "face_v6")' in src, "白名单未扩")
ck("k9-not-in-default-path", "k9" not in re.search(r"V6_DEFAULT_LIBS = \(.*?\)", src).group(0), "")
# 规则旁挂件惰性断言：mcp_server 无任何代码路径加载该件（仅允许注释/文档提及）
g = subprocess.run(["grep", "-rnE", r"(open|json\.load|Path)\s*\(?[^#\n]*_k9_ocs_rules_overlay",
                    "/mnt/D/EyeKB/mcp_server", "--include=*.py"], capture_output=True, text=True)
ck("rules-overlay-inert", g.stdout.strip() == "", f"rc={g.returncode} out={g.stdout[:200]}")
# 服务版本（源码级；stdio 级由 GOLDEN41 harness 真往返另证）
srv = Path("/mnt/D/EyeKB/mcp_server/server.py").read_text(encoding="utf-8")
ck("server-version-bump", 'version="KB1v2-0.5-k9reg"' in srv, "")

# EYEKB_ACT_V6=off 态泄漏反例（回退态同样禁入）
os.environ["EYEKB_ACT_V6"] = "off"
dl2 = core.query_marker()
ck("off-state-no-k9", not [c for c in dl2.get("cell_types", []) if c in K9_TERMS], len(dl2.get("cell_types", [])))
os.environ.pop("EYEKB_ACT_V6", None)

report = {
    "level": "规范序列化 (sort_keys JSON sha256); 对象字段级隐含其中; 仅限响应对象层面 (REVIEWER_LLM Q5 口径)",
    "n_probes": len(PRE), "n_checks": len(checks), "n_fails": len(fails),
    "verdict": "PASS" if not fails else "FAIL",
    "failures": fails, "checks": checks,
    "post_probe_shas": {k: sha(v) for k, v in post.items()},
}
(CARD / "exec/out/postdiff_selfproof.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: report[k] for k in ("level", "n_probes", "n_checks", "n_fails", "verdict")},
                 ensure_ascii=False))
if fails:
    print("FAILURES:", json.dumps(fails[:10], ensure_ascii=False))
sys.exit(0 if not fails else 1)

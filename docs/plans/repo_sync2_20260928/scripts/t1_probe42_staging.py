#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC2 t_719dd225 · T1b — 42-probe 电池 + 注册行为断言，跑在 STAGING 仓副本 core 上
（KB9REG exec3 口径；差异=被测 core/静态面/基线全用仓副本，线上零写）。"""
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/ubuntu/EYEKB_REPO_STAGING_20260928")
ONLINE = Path("/mnt/D/EyeKB")
ACT = ONLINE / "plans/activation_20260926"
CARDM = Path("/mnt/D/EyeKB/plans/kb9_ocs_20260927")   # 基线=线上权威件（只读；仓内镜像的 response 字段为镜像化产物不作判据）
OUT = REPO / "docs/plans/repo_sync2_20260928/out"

# 先锁仓 core，再引 act_battery（其内部 sys.path 插入无法覆盖已加载模块）
sys.path.insert(0, str(REPO / "mcp_server"))
import eyekb_core as core  # noqa: E402
assert str(Path(core.__file__).resolve()).startswith(str(REPO)), core.__file__
spec = importlib.util.spec_from_file_location("act_battery", ACT / "scripts/act_battery_t5d5853c9.py")
ab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ab)
run_probe, pin_env = ab.run_probe, ab.pin_env
pin_env()

PRE = json.load(open(CARDM / "exec/out/pre_change_baseline_kb9reg.json"))["probes"]
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


os.environ.pop("EYEKB_ACT_V6", None)

# --- 同源脱敏映射（自 v3 脱敏器源码抽取；镜像=脱敏副本，仓 core 响应文本面必然
# 等于 desens(线上响应)。判据: canon_sha 直等 = PASS；否则 desens 等价 = PASS-DESENS；
# 两者皆非 = 真漂移 FAIL） ---
_src = Path("/home/ubuntu/eyekb_desensitize_v3_reposync2.py").read_text(encoding="utf-8")
_ns = {"re": re}
exec(re.search(r"^RULES = \[.*?^\]", _src, re.S | re.M).group(0), _ns)
_R = [(p, r) for _n, p, r, _s in _ns["RULES"]]


def desens_str(s):
    for pat, rep in _R:
        s = re.sub(pat, rep, s)
    return s


def desens_obj(o):
    if isinstance(o, str):
        return desens_str(o)
    if isinstance(o, list):
        return [desens_obj(x) for x in o]
    if isinstance(o, dict):
        return {desens_str(k): desens_obj(v) for k, v in o.items()}
    return o


def reprefix(o):
    """环境项归一：仓副本 core 的 provenance 绝对路径前缀 = 仓根；与线上唯一差异
    是 kb_root 前缀本身，映射回 /mnt/D/EyeKB 后逐字节等价（KB9REG exec7 同口径的推广）。"""
    if isinstance(o, str):
        return o.replace(str(REPO), "/mnt/D/EyeKB")
    if isinstance(o, list):
        return [reprefix(x) for x in o]
    if isinstance(o, dict):
        return {k: reprefix(v) for k, v in o.items()}
    return o


post = {}
ndes = ndirect = nfail = 0
desens_fields = []


def explainable(a, b):
    """两处叶子值差异可由注册脱敏映射解释（任一方向）"""
    return isinstance(a, str) and isinstance(b, str) and (desens_str(a) == b or desens_str(b) == a)


def walk_diff(a, b, path=""):
    ds = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            ds += walk_diff(a.get(k, "<M>"), b.get(k, "<M>"), path + "/" + str(k))
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            ds += walk_diff(x, y, path + f"[{i}]")
    elif a != b:
        ds.append((path, a, b))
    else:
        return []
    return ds


for name, pspec in PRE.items():
    try:
        res = run_probe(core, {"probe": pspec["probe"], "args": pspec["args"]})
    except Exception as e:  # noqa: BLE001
        res = {"__error__": type(e).__name__ + ": " + str(e)}
    post[name] = res
    resn = reprefix(res)
    if sha(resn) == pspec["canon_sha"]:
        ndirect += 1
        ck(f"pre==post::{name}", True, "")
        continue
    dl = walk_diff(pspec.get("response"), resn)
    expl = dl and all(explainable(a, b) for _, a, b in dl)
    if expl:
        ndes += 1
        desens_fields.append({"probe": name, "fields": [(p, str(a)[:80], str(b)[:80]) for p, a, b in dl]})
        ck(f"pre==post::{name}", True, f"脱敏可解释差异 {len(dl)} 字段（代码面脱敏 vs kb面字节镜像）")
    else:
        nfail += 1
        ck(f"pre==post::{name}", False, f"非脱敏可解释: {[(p, str(a)[:60], str(b)[:60]) for p, a, b in dl[:3]]}")
print(f"probes: {len(PRE)} byte-direct(路径归一后)={ndirect} desens-explained={ndes} fail={nfail}")

dl = post["k9leak_default_list"]
ct = dl.get("cell_types") or []
pre_ct = PRE["k9leak_default_list"]["response"].get("cell_types") or []
ck("no-k9-in-default-list", not [c for c in ct if c in K9_TERMS], [c for c in ct if c in K9_TERMS])
ck("default-list-count-stable", len(ct) == len(pre_ct) == 60, f"post={len(ct)} pre={len(pre_ct)}")

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

src = (REPO / "mcp_server/eyekb_core.py").read_text(encoding="utf-8")
ck("V6_DEFAULT_LIBS-frozen", 'V6_DEFAULT_LIBS = ("retina_v6", "face_v6")' in src, "白名单未扩")
ck("k9-not-in-default-path", "k9" not in re.search(r"V6_DEFAULT_LIBS = \(.*?\)", src).group(0), "")
g = subprocess.run(["grep", "-rnE", r"(open|json\.load|Path)\s*\(?[^\#\n]*_k9_ocs_rules_overlay",
                    str(REPO / "mcp_server"), "--include=*.py"], capture_output=True, text=True)
ck("rules-overlay-inert", g.stdout.strip() == "", f"rc={g.returncode} out={g.stdout[:200]}")
g2 = subprocess.run(["grep", "-rnE", r"(open|json\.load|Path)\s*\(?[^\#\n]*_raggap_",
                     str(REPO / "mcp_server"), "--include=*.py"], capture_output=True, text=True)
ck("raggap-inerts-unwired", g2.stdout.strip() == "", f"rc={g2.returncode} out={g2.stdout[:200]}")
srv = (REPO / "mcp_server/server.py").read_text(encoding="utf-8")
ck("server-version-bump", 'version="KB1v2-0.5-k9reg"' in srv, "")

os.environ["EYEKB_ACT_V6"] = "off"
dl2 = core.query_marker()
ck("off-state-no-k9", not [c for c in dl2.get("cell_types", []) if c in K9_TERMS], len(dl2.get("cell_types", [])))
os.environ.pop("EYEKB_ACT_V6", None)

report = {"level": "规范序列化 (sort_keys JSON sha256); 响应对象层面; 被测=staging 仓副本 core",
          "card": "t_719dd225-T1b", "repo": str(REPO), "n_probes": len(PRE),
          "n_checks": len(checks), "n_fails": len(fails),
          "verdict": "PASS" if not fails else "FAIL",
          "n_byte_direct": ndirect, "n_desens_explained": ndes, "n_fail": nfail, "desens_explained_fields": desens_fields,
          "failures": fails, "checks": checks,
          "post_probe_shas": {k: sha(v) for k, v in post.items()}}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "t1_probe42_staging.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: report[k] for k in ("n_probes", "n_checks", "n_fails", "verdict")}, ensure_ascii=False))
sys.exit(0 if not fails else 1)

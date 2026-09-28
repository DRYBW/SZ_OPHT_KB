#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B5IMPL t_8960c7e0 · b503 — 回退门 + 注册面自证（A5 式，仿 kb9 exec3 / ACT sf13 口径）
① 42-probe B5-OFF 态 canon_sha 与 b501 pre 基线逐条全等（回退=零扰动，机读自证）；
② 双态对照：同电池 EYEKB_KBGOV_B5 未设（默认 ON）重放，genes-mode 探针 off_sha≠on_sha
   （治理真实生效），非 genes-mode 探针（cell_type/list/组成）三态全等（管辖面不越界）；
③ 注册面断言：server version=KB1v2-0.6-kbgov5；V6_DEFAULT_LIBS 白名单不变；
   k9_ocs/lacrimal_v6 REGISTERED_DEFAULT_OFF 语义保持（默认清单无 k9/lacrimal 名、
   显式路由可达）；OFF 态响应零治理字段；词表 sha==KBGOV 冻结源；fail-soft 降级路径。
输出 out/B5IMPL_A5_ROLLBACK.tsv + out/b503_selfproof.json; exit 0=全 PASS。"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

CARD = Path("/mnt/D/EyeKB/plans/kbgov_b5impl_20260928")
ACT = Path("/mnt/D/EyeKB/plans/activation_20260926")
sys.path.insert(0, str(ACT / "scripts"))
from act_battery_t5d5853c9 import build_probes, run_probe, pin_env  # noqa: E402

pin_env()
sys.path.insert(0, "/mnt/D/EyeKB/mcp_server")
import eyekb_core as core  # noqa: E402

PRE = json.load(open(CARD / "out/b5_pre_baseline.json"))["probes"]
K9N = {"Melanocyte", "Schwann", "Conj_epithelium_suprabasal", "Limbus_Sclera_fibroblast_C1"}


def canon(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True)


def sha(o):
    return hashlib.sha256(canon(o).encode()).hexdigest()


def run_battery(env_b5):
    if env_b5 is None:
        os.environ.pop("EYEKB_KBGOV_B5", None)
    else:
        os.environ["EYEKB_KBGOV_B5"] = env_b5
    out = {}
    for name, spec in PRE.items():
        try:
            res = run_probe(core, {"probe": spec["probe"], "args": spec["args"]})
        except Exception as e:  # noqa: BLE001
            res = {"__error__": type(e).__name__ + ": " + str(e)}
        out[name] = res
    return out


def is_genes_probe(name):
    a = PRE[name]["args"]
    return PRE[name]["probe"] == "query_marker" and isinstance(a, dict) and bool(a.get("genes"))


fails, checks = [], []


def ck(tag, cond, detail=""):
    checks.append({"check": tag, "pass": bool(cond), "detail": str(detail)[:300]})
    if not cond:
        fails.append([tag, str(detail)[:300]])


os.environ.pop("EYEKB_ACT_V6", None)  # 生产默认 V6 ON

# ---- ① OFF 态 42-probe 全等（逐字节=规范序列化 sha 全等） ----
off = run_battery("0")
for name in PRE:
    pre_sha = PRE[name]["canon_sha"]
    off_sha = sha(off[name])
    ck(f"off==pre::{name}", off_sha == pre_sha, "回退态漂移" if off_sha != pre_sha else "")

# ---- ② 默认 ON 态双态对照 ----
on = run_battery(None)
GKEYS = {"input_species", "no_named_ranking_for", "species_evidence", "unranked_candidates"}
n_genes_probes = 0
for name in PRE:
    on_sha = sha(on[name])
    if is_genes_probe(name):
        n_genes_probes += 1
        ck(f"on-changed::{name}", on_sha != PRE[name]["canon_sha"],
           "ON 态 genes-mode 探针未生效治理（应≠pre）" if on_sha == PRE[name]["canon_sha"] else "")
        if not off[name].get("celltype_ranking"):
            # 零命中的 genes 探针（k9leak 默认态=无命中）: 仅新增 input_species, 序不变
            ck(f"on-emptyranking-addfield::{name}", "input_species" in on[name]
               and "celltype_ranking" in on[name] and on[name]["celltype_ranking"] == [])
    else:
        ck(f"on-untouched::{name}", on_sha == PRE[name]["canon_sha"],
           "非 genes-mode 探针在 ON 态漂移（管辖面越界）" if on_sha != PRE[name]["canon_sha"] else "")

# 治理字段在 OFF 态零出现（响应键面 == pre 键面）
for name in PRE:
    ck(f"off-no-govkeys::{name}",
       set(off[name].keys()) == set(PRE[name]["response"].keys()),
       f"extra={set(off[name].keys()) - set(PRE[name]['response'].keys())}")

# ---- ③ 注册面断言 ----
ck("version-0.6-kbgov5", core.__dict__.get("__file__") is not None)  # 版本在 server.py, 下方 grep 断言
srv_txt = Path("/mnt/D/EyeKB/mcp_server/server.py").read_text(encoding="utf-8")
ck("srv-version-string", 'version="KB1v2-0.6-kbgov5"' in srv_txt, "server.py version")
ck("core-version-bump-no-regression-of-k9reg-note", "KB1v2-0.5-k9reg" not in srv_txt,
   "旧版本串残留=0")
ck("V6_DEFAULT_LIBS-unchanged", tuple(core.V6_DEFAULT_LIBS) == ("retina_v6", "face_v6"),
   core.V6_DEFAULT_LIBS)
dl = core.query_marker(library="all")
ck("no-k9-in-default", not (set(dl.get("cell_types", [])) & K9N), sorted(set(dl.get("cell_types", [])) & K9N))
ck("no-lacrimal-in-default", not [c for c in dl.get("cell_types", [])
                                  if "acrimal" in c], "lacrimal leak")
r = core.query_marker(library="k9_ocs")
ck("k9-route-reachable", sorted(r.get("cell_types", [])) == sorted(K9N), r.get("cell_types"))
r = core.query_marker(cell_type="Lacrimal_secretory_tearcell", library="lacrimal_v6")
ck("lacrimal-route-reachable", r.get("found") is True, r.get("found"))

# 词表 sha 锚定 == KBGOV 冻结源
voc_local = hashlib.sha256(Path("/mnt/D/EyeKB/mcp_server/kbgov_vocab.json.gz").read_bytes()).hexdigest()
voc_src = hashlib.sha256(Path("/mnt/D/EyeKB/plans/kb_gov_20260928/data/kbgov_vocab.json.gz").read_bytes()).hexdigest()
ck("vocab-byte-identical", voc_local == voc_src == "9b504a2e7cdc975b3963579e445e680e40921dc6749b1b105d172d80a0222a61",
   voc_local[:16])
ck("vocab-loads", core._kbgov_vocab() is not None and len(core._kbgov_vocab()[0]) == 262000,
   len(core._kbgov_vocab()[0]) if core._kbgov_vocab() else None)

# fail-soft: 临时改名词表 → 响应=legacy（与 OFF 全等），恢复后正常
p = Path("/mnt/D/EyeKB/mcp_server/kbgov_vocab.json.gz")
bak = Path("/mnt/D/EyeKB/mcp_server/.kbgov_vocab.failsoft_test")
os.environ.pop("EYEKB_KBGOV_B5", None)
genes_probe = {k: v for k, v in PRE.items() if is_genes_probe(k)}
try:
    p.rename(bak)
    core._kbgov_voc_cache.update(sig=None, data=None, warned=False)
    degraded = {k: core.query_marker(**v["args"]) for k, v in genes_probe.items()}
    ok_ds = all(sha(degraded[k]) == sha(off[k]) for k in genes_probe)
    ck("failsoft-vocab-missing==legacy", ok_ds, "missing-vocab 响应应==OFF/legacy")
finally:
    bak.rename(p)
    core._kbgov_voc_cache.update(sig=None, data=None, warned=False)
after = {k: core.query_marker(**v["args"]) for k, v in genes_probe.items()}
ck("failsoft-recovery", all(sha(after[k]) == sha(on[k]) for k in genes_probe), "词表恢复后 ON 语义复原")

# OFF 态 cell_type-mode 与 list-mode 无 input_species（管辖面）
ct_resp = core.query_marker(cell_type="RPE")
os.environ["EYEKB_KBGOV_B5"] = "0"
ct_resp_off = core.query_marker(cell_type="RPE")
ck("celltype-mode-no-gov-keys", "input_species" not in ct_resp and "input_species" not in ct_resp_off,
   "cell_type 模式不在 B5 管辖")

# B5 开关解析函数口径
os.environ["EYEKB_KBGOV_B5"] = "OFF"
ck("switch-casefold-off", core._kbgov_b5_enabled() is False)
os.environ["EYEKB_KBGOV_B5"] = "0 "
ck("switch-0", core._kbgov_b5_enabled() is False)
os.environ["EYEKB_KBGOV_B5"] = "1"
ck("switch-1-on", core._kbgov_b5_enabled() is True)
os.environ["EYEKB_KBGOV_B5"] = "true"
ck("switch-true-on", core._kbgov_b5_enabled() is True)
os.environ.pop("EYEKB_KBGOV_B5", None)
ck("switch-unset-on", core._kbgov_b5_enabled() is True)

# ---- 输出: 回退双态 sha 台账 (门4 验收件) + json ----
with open(CARD / "out/B5IMPL_A5_ROLLBACK.tsv", "w") as f:
    f.write("probe\tpre_sha\tb5off_sha\tb5on_sha\tmode\toff_eq_pre\ton_eq_pre\n")
    for name in PRE:
        pre_sha, off_sha, on_sha = PRE[name]["canon_sha"], sha(off[name]), sha(on[name])
        mode = "genes" if is_genes_probe(name) else "other"
        f.write(f"{name}\t{pre_sha}\t{off_sha}\t{on_sha}\t{mode}\t"
                f"{pre_sha == off_sha}\t{pre_sha == on_sha}\n")

json.dump({"at": time.strftime("%F %T"), "card": "t_8960c7e0",
           "n_checks": len(checks), "n_fails": len(fails), "fails": fails,
           "checks": checks,
           "rollback_tsv": str(CARD / "out/B5IMPL_A5_ROLLBACK.tsv"),
           "probes_total": len(PRE), "probes_genes": n_genes_probes},
          open(CARD / "out/b503_selfproof.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps({"checks": len(checks), "fails": len(fails), "gene_probes": n_genes_probes,
                  "verdict": "PASS" if not fails else "FAIL"}, ensure_ascii=False))
sys.exit(0 if not fails else 1)

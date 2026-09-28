#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B5IMPL t_8960c7e0 · b501 — 改码前基线捕获（A5 式验收的 pre 半边）
probe 电池 = ACT t_5d5853c9 共享电池 33 条 + KB9 泄漏反例 9 条 = 42 条（与
plans/kb9_ocs_20260927 exec1/exec3 同电池同口径，EYEKB_MCP_SOFTFLAGS=1 固定）。
本件在 B5 实装改码之前运行：捕获"现生产行为"（V6 默认 ON, B5 代码不存在）。
输出 out/b5_pre_baseline.json + ledgers/SHA_PRE_B5IMPL.txt。"""
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

CARD = Path("/mnt/D/EyeKB/plans/kbgov_b5impl_20260928")
ACT = Path("/mnt/D/EyeKB/plans/activation_20260926")
sys.path.insert(0, str(ACT / "scripts"))
from act_battery_t5d5853c9 import build_probes, run_probe, pin_env  # noqa: E402

pin_env()
# 生产默认态：EYEKB_ACT_V6 未设；B5 开关此时不存在，显式清掉防环境污染
os.environ.pop("EYEKB_ACT_V6", None)
os.environ.pop("EYEKB_KBGOV_B5", None)
sys.path.insert(0, "/mnt/D/EyeKB/mcp_server")
import eyekb_core as core  # noqa: E402

# KB9 泄漏 9 条（逐字继承 exec1_capture_pre_baseline.py 的 K9_LEAK）
K9_LEAK = {
    "k9leak_ct_Melanocyte": ("query_marker", {"cell_type": "Melanocyte"}),
    "k9leak_ct_Schwann": ("query_marker", {"cell_type": "Schwann"}),
    "k9leak_ct_suprabasal": ("query_marker", {"cell_type": "Conj_epithelium_suprabasal"}),
    "k9leak_ct_limbusC1": ("query_marker", {"cell_type": "Limbus_Sclera_fibroblast_C1"}),
    "k9leak_genes_mel_core": ("query_marker", {"genes": ["MLANA", "TYRP1", "PMEL", "DCT", "GPR143", "SLC24A5", "ABCB5", "GAPDHS"]}),
    "k9leak_genes_schw_core": ("query_marker", {"genes": ["MPZ", "SCN7A", "NRXN1"]}),
    "k9leak_genes_supra_core": ("query_marker", {"genes": ["KRT4", "S100A8", "S100A9"]}),
    "k9leak_genes_limC1_core": ("query_marker", {"genes": ["DPT", "LEPR", "LAMA2"]}),
    "k9leak_default_list": ("query_marker", {}),
}


def canon(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True)


def sha(o):
    return hashlib.sha256(canon(o).encode()).hexdigest()


probes = build_probes()
for k, (fn, args) in K9_LEAK.items():
    probes[k] = {"probe": fn, "args": args}

out = {}
for name, spec in probes.items():
    try:
        res = run_probe(core, spec)
    except Exception as e:  # noqa: BLE001
        res = {"__error__": type(e).__name__ + ": " + str(e)}
    out[name] = {"probe": spec["probe"], "args": spec["args"],
                 "response": res, "canon_sha": sha(res)}

# 与 KB9 现基线交叉核对（同电池同默认 env 下 pre==kb9 基线的 33 条共享探针）
KB9PRE = Path("/mnt/D/EyeKB/plans/kb9_ocs_20260927/exec/out/pre_change_baseline_kb9reg.json")
xcheck = {}
if KB9PRE.is_file():
    kb9 = json.load(open(KB9PRE))["probes"]
    shared = [k for k in out if k in kb9]
    drift = [k for k in shared if sha(out[k]["response"]) != kb9[k]["canon_sha"]]
    xcheck = {"shared_probes": len(shared), "drift_vs_kb9_pre": sorted(drift)}

json.dump({"captured_at": time.strftime("%F %T"), "card": "t_8960c7e0",
           "env": {"EYEKB_MCP_SOFTFLAGS": os.environ.get("EYEKB_MCP_SOFTFLAGS"),
                   "EYEKB_ACT_V6": "(unset)", "EYEKB_KBGOV_B5": "(absent=pre-B5 世界)"},
           "n_probes": len(out), "probes": out, "kb9_cross_check": xcheck},
          open(CARD / "out/b5_pre_baseline.json", "w"), ensure_ascii=False, indent=1)

# SHA_PRE 台账：mcp_server 全件 + KBGOV 冻结输入（词表/校准判据）
lines = []
for p in sorted(Path("/mnt/D/EyeKB/mcp_server").glob("*")):
    if p.is_file() and p.suffix == ".py":
        lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p}")
for rel in ("data/kbgov_vocab.json.gz", "data/kbgov_g1_calibration.json",
            "out/kbgov_gates_final.json", "out/kbgov_lesion_verdicts.tsv",
            "out/kbgov_regression_shift.tsv", "out/kbgov_mouse_side.tsv",
            "out/kbgov_ab_metrics.json", "data/kbgov_g1_signals_290.json",
            "data/kbgov_ab_lesion.tsv"):
    p = Path("/mnt/D/EyeKB/plans/kb_gov_20260928") / rel
    lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p}")
(CARD / "ledgers/SHA_PRE_B5IMPL.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

print(json.dumps({"n_probes": len(out), "kb9_cross_check": xcheck,
                  "written": ["out/b5_pre_baseline.json", "ledgers/SHA_PRE_B5IMPL.txt"],
                  "at": time.strftime("%F %T")}, ensure_ascii=False))
sys.exit(0 if not xcheck.get("drift_vs_kb9_pre") else 3)

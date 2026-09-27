#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9REG-EXEC t_4bb75b26 · exec1 — 改码前基线捕获（A5 式验收的 pre 半边）
probe 电池 = ACT t_5d5853c9 共享电池 33 条（sf18+act15，args 逐字继承，判据零改动）
+ KB9 泄漏反例探针（4 新条类名直查 / k9 core 基因反查 / 默认全清单构成断言）。
EYEKB_MCP_SOFTFLAGS=1 固定（与 ACT 电池同口径，消除软提示态漂移）。
输出 exec/out/pre_change_baseline_kb9reg.json"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

CARD = Path("/mnt/D/EyeKB/plans/kb9_ocs_20260927")
ACT = Path("/mnt/D/EyeKB/plans/activation_20260926")
sys.path.insert(0, str(ACT / "scripts"))
from act_battery_t5d5853c9 import build_probes, run_probe, pin_env  # noqa: E402

pin_env()
sys.path.insert(0, "/mnt/D/EyeKB/mcp_server")
import eyekb_core as core  # noqa: E402

K9_LEAK = {
    # 新条类名直查（默认态：注册前后都应 found=false / 无该类 —— k9 永不入默认）
    "k9leak_ct_Melanocyte": ("query_marker", {"cell_type": "Melanocyte"}),
    "k9leak_ct_Schwann": ("query_marker", {"cell_type": "Schwann"}),
    "k9leak_ct_suprabasal": ("query_marker", {"cell_type": "Conj_epithelium_suprabasal"}),
    "k9leak_ct_limbusC1": ("query_marker", {"cell_type": "Limbus_Sclera_fibroblast_C1"}),
    # k9 core 基因默认态反查（注册前=无 k9 行；注册后仍=无 k9 行 = 默认零扰动）
    "k9leak_genes_mel_core": ("query_marker", {"genes": ["MLANA", "TYRP1", "PMEL", "DCT", "GPR143", "SLC24A5", "ABCB5", "GAPDHS"]}),
    "k9leak_genes_schw_core": ("query_marker", {"genes": ["MPZ", "SCN7A", "NRXN1"]}),
    "k9leak_genes_supra_core": ("query_marker", {"genes": ["KRT4", "S100A8", "S100A9"]}),
    "k9leak_genes_limC1_core": ("query_marker", {"genes": ["DPT", "LEPR", "LAMA2"]}),
    # 默认全清单（list 模式，类名全集——前后必须一字不差）
    "k9leak_default_list": ("query_marker", {}),
}


def canon(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True)


def sha(o):
    return hashlib.sha256(canon(o).encode()).hexdigest()


fails = []
probes = build_probes()
for k, (fn, args) in K9_LEAK.items():
    probes[k] = {"probe": "query_marker", "args": args}

out = {}
for name, spec in probes.items():
    try:
        res = run_probe(core, spec)
        out[name] = res
    except Exception as e:  # noqa: BLE001
        out[name] = {"__error__": type(e).__name__ + ": " + str(e)}

# 记录默认清单类名集与 k9 名命中情况（前后对照用）
dl = out.get("k9leak_default_list", {})
ct_list = dl.get("cell_types") if isinstance(dl, dict) else None
summary = {
    "date": time.strftime("%F %T"),
    "task": "KB9REG-EXEC t_4bb75b26 pre-change baseline",
    "n_probes": len(probes),
    "battery_source": "activation_20260926/scripts/act_battery_t5d5853c9.py (33) + k9 leak (9)",
    "env": {"EYEKB_MCP_SOFTFLAGS": os.environ.get("EYEKB_MCP_SOFTFLAGS"),
            "EYEKB_ACT_V6": os.environ.get("EYEKB_ACT_V6", "(unset=ON 生产默认)")},
    "default_all_n_celltypes": len(ct_list) if ct_list else None,
    "default_all_has_k9_names": sorted([c for c in (ct_list or []) if any(
        s in c for s in ("Melanocyte", "Schwann", "Suprabasal", "suprabasal", "Limbus_Sclera"))]),
    "probes": {k: {"probe": v["probe"], "args": v["args"],
                   "canon_sha": sha(out[k]), "response": out[k]} for k, v in probes.items()},
}
(CARD / "exec/out").mkdir(parents=True, exist_ok=True)
(CARD / "exec/out/pre_change_baseline_kb9reg.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"PRE baseline captured: {summary['n_probes']} probes; "
      f"default all classes={summary['default_all_n_celltypes']}; "
      f"k9 names in default={summary['default_all_has_k9_names']}")

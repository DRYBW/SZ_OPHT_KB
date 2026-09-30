#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/test_s0_gate.py — S0 + claim 契约黄金回归（WIRE-P1 REV-1=astra 定盘版）。

判据（全部本地、零联网、零 LLM）：
  T1 人视网膜真实切片（仓内 fixture）→ S0 不弃权，species=human，top1=human_retina。
  T2 混染扰动 → 弃权（species_mixed_id_prefixes）。
  T3 空面板扰动 → 弃权（empty_or_zero_counts）。
  T4 防火墙源码断言（ast 级）：判读面模块不 import/引用 pitfalls/known_issues。
  T5 契约一致性：build_claims.py --check（脚本↔pages 互证）+ INDEX 链接 100% 解析
     + 全 claim 带 scope/evidence_source_type/owner/status/visibility/blind_safe/
     answer_dependency + 唯一 Home + 无 GLOBAL 残留（五支树）。
  T6 shadow 语义：consume 不产生任何 cap/override 旗标字样（禁自动改标断言），
     非盲评安全条在预标注渲染中无自由文本。
用法: python tests/test_s0_gate.py （exit 0=PASS；无 pytest 依赖）
"""
import gzip
import importlib
import json
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))


def main():
    fails = []
    s0 = importlib.import_module("s0_check")
    ctx = s0._ctx()

    def probe_csv(text, name):
        fd, p = tempfile.mkstemp(suffix=".csv", prefix=name)
        os.write(fd, text.encode()); os.close(fd)
        try:
            return s0.probe(p, name, ctx['assets'], ctx['mk'], ctx['panels'],
                            ctx['human_panel'])
        finally:
            os.unlink(p)

    fx = gzip.open(ROOT / "tests/fixtures/s0_human_retina_pb_top8000.csv.gz", "rt").read()
    f1 = probe_csv(fx, "t1")["final"]
    ok1 = (not f1["abstain"]) and f1["species_call"] == "human" and f1["tissue_top1"] == "human_retina"
    print("T1", "PASS" if ok1 else f"FAIL {f1}")
    fails += [] if ok1 else ["T1"]

    lines = fx.splitlines(True)
    rng = random.Random(20260930)
    idxset = set(rng.sample(range(1, len(lines)), k=int(0.2 * (len(lines) - 1))))
    mixed = [lines[0]]
    for i, ln in enumerate(lines[1:], 1):
        parts = ln.rstrip("\n").split(",")
        if i in idxset and parts[0].startswith("ENSG"):
            parts[0] = "ENSMUSG" + parts[0][4:]  # ENSG 前缀 4 字符，数字 11 位=RE_M 合法形态
        mixed.append(",".join(parts) + "\n")
    f2 = probe_csv("".join(mixed), "t2")["final"]
    ok2 = f2["abstain"] and any("species_mixed" in g for g in f2["gate_reasons"])
    print("T2", "PASS" if ok2 else f"FAIL {f2['gate_reasons']}")
    fails += [] if ok2 else ["T2"]

    f3 = probe_csv(open(ROOT / "tests/fixtures/s0_empty_pb.csv").read(), "t3")["final"]
    ok3 = f3["abstain"] and "empty_or_zero_counts" in f3["gate_reasons"]
    print("T3", "PASS" if ok3 else f"FAIL {f3['gate_reasons']}")
    fails += [] if ok3 else ["T3"]

    import ast
    bad = []
    for fn in ("s0_check.py", "stage_b_evidence.py", "stage_a_processing.py", "llm_assist.py"):
        tree = ast.parse((ROOT / "pipeline" / fn).read_text(encoding="utf-8"))
        doc_ids = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                body = getattr(node, "body", [])
                if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                        and isinstance(body[0].value.value, str):
                    doc_ids.add(id(body[0].value))
            if isinstance(node, ast.Import):
                mods = [n.name for n in node.names]
            elif isinstance(node, ast.ImportFrom):
                mods = [node.module or ""]
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                if id(node) in doc_ids:
                    continue
                if any(k in node.value for k in ("pitfalls/", "known_issues", "pages/cells",
                                                 "pages/patterns", "shadow_attention")):
                    bad.append((fn, node.value[:40]))
                continue
            else:
                continue
            for m in mods:
                if any(k in m for k in ("pitfall", "consume", "known_issue")):
                    bad.append((fn, m))
    ok4 = not bad
    print("T4", "PASS" if ok4 else f"FAIL {bad}")
    fails += [] if ok4 else ["T4"]

    r = subprocess.run([sys.executable, str(ROOT / "pipeline/pitfalls/build_claims.py"),
                        "--check"], capture_output=True, text=True)
    # 链接 100% + 字段完整（validate 已在 --check 内跑；此处再核 INDEX）
    idx = json.loads((ROOT / "pipeline/pitfalls/pages/INDEX.json").read_text(encoding="utf-8"))
    ids = set(idx["claim_ids"])
    dangling, missing_fields = [], []
    for p in (ROOT / "pipeline/pitfalls/pages").rglob("*.json"):
        if p.name in ("INDEX.json", "EXCLUSIONS.json"):
            continue
        pg = json.loads(p.read_text(encoding="utf-8"))
        for pt in pg.get("pointers") or []:
            if pt["ref_id"] not in ids:
                dangling.append((p.name, pt["ref_id"]))
        for e in pg.get("entries") or []:
            for k in ("scope", "evidence_source_type", "owner", "status", "visibility",
                      "blind_safe", "answer_dependency", "failure_mode",
                      "observable_signature", "source_check", "risk_level"):
                if k not in e:
                    missing_fields.append((e.get("claim_id"), k))
    ok5 = r.returncode == 0 and not dangling and not missing_fields
    print("T5", "PASS" if ok5 else f"FAIL check_rc={r.returncode} dangling={dangling[:3]} missing={missing_fields[:3]}")
    fails += [] if ok5 else ["T5"]

    # T6 shadow 语义：渲染中非盲评安全条无自由文本；不出现 cap/override 字样
    sys.path.insert(0, str(ROOT / "pipeline/pitfalls"))
    consume = importlib.import_module("consume")
    lns, machine, claims, dang = consume.attention_section("human", "fibrovascular_membrane",
                                                           {"source": "s0"})
    body = "\n".join(lns)
    red_claims = [c for c in claims if not c.get("blind_safe", True)]
    leak = [c["claim_id"] for c in red_claims if c["failure_mode"] in body or c["mitigation"] in body]
    banned = [w for w in ("PITFALL_OVERRIDE", "suggested_grade_cap", "C-TENTATIVE") if w in body]
    # 类锚命中旗标也必须是 REVIEW:（非 override/非降级）
    fl, audit = consume.cluster_flags(claims, ["Mac_DAM_LAM", "Endothelial cell"])
    badflags = [x for x in fl if not x.startswith("REVIEW:")]
    ok6 = (not leak) and (not banned) and (not badflags) and all(
        a["action"] == "risk_flag_only(no_auto_override)" for a in audit)
    print("T6", "PASS" if ok6 else f"FAIL leak={leak} banned={banned} badflags={badflags}")
    fails += [] if ok6 else ["T6"]

    print("GATE", "ALL PASS" if not fails else f"FAILED: {fails}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())

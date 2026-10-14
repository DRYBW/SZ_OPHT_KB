#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/gate_g5g6_negative.py — G5/G6 负例电池（对真件做最小突变 → 断言被拒且报目标检查码）

契约（沿用 W3_NORM/R1 `tests/run_negative_tests.py` 的负例口径）：
  · 正控：未突变的真件副本 ⇒ 必须 rc=0（否则门本身不可信）；
  · 负例：每一类必须 rc≠0，且**命中预期的目标检查码**（禁只报「整体 FAIL」）；
  · 额外失败（目标码之外）如实记录为 unexpected_extra_failures，不隐藏也不据此判失败。

突变只作用于 fixtures 下的**副本**：仓内真件（台账 / 门清单 / 实例 / 人读清单 / 入口）零改动。

G5 用例：P0 正控 / N1 缺件(C04) / N2 摘要漂移(C05) / N3 未登记加载(C07) / N4 过期认证(C08) / N5 记账过期(C06)
G6 用例：P0 正控 / N1 必填缺项(R1) / N2 无锚证据(R2) / N3 只报增益(R5) / N4 无 sha(R6) /
         N5 逃生门缺开关(R7) / N6 默认 ON 未登记门前置(R8) / N7 无阈值动作(R2-CONCRETE) / N8 清单↔规则映射缺行(MAP)

用法：python3 tests/gate_g5g6_negative.py [--out DIR] [--json OUT.json]
退出码：0=全部符合预期；1=有不合预期项。
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures"


def sh(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(p: Path, txt: str) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(txt, encoding="utf-8")
    return p


def mutate(src: Path, dst: Path, old: str, new: str) -> Path:
    t = sh(src)
    n = t.count(old)
    assert n == 1, f"mutation target not unique in {src.name}: {n} matches for {old[:40]!r}"
    return write(dst, t.replace(old, new))


def run_gate(script: Path, args: list, cwd: Path = ROOT) -> tuple:
    """返回 (rc, failing_codes, stdout_tail)"""
    cmd = [sys.executable, str(script)] + args
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd))
    codes = []
    for a in args:
        if a.startswith("--json="):
            jp = Path(a.split("=", 1)[1])
            if jp.exists():
                try:
                    codes = [c["code"] for c in json.loads(jp.read_text(encoding="utf-8"))["checks"]
                             if c["status"] == "FAIL"]
                except Exception:                                  # noqa: BLE001
                    codes = ["<json-unreadable>"]
    return r.returncode, codes, (r.stdout + r.stderr)[-600:]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(FIX))
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    fixtures = Path(a.out)

    reg = ROOT / "docs" / "W3_PIPELINE_REGISTRY.tsv"
    inv = ROOT / "docs" / "GATE_INVENTORY_G5G6.tsv"
    led = ROOT / "tests" / "fixtures" / "g5" / "snapshot_drift_ledger.tsv"
    ent = ROOT / "tests" / "run_gates.sh"
    inst = ROOT / "docs" / "CHANGE_CONTROL_G6_INSTANCE.tsv"
    tmpl = ROOT / "docs" / "CHANGE_CONTROL_G6_TEMPLATE.tsv"
    chk = ROOT / "docs" / "W3_CHANGE_CONTROL_CHECKLIST.md"
    g5 = ROOT / "tests" / "gate_registry.py"
    g6 = ROOT / "tests" / "gate_change_control.py"
    missing = [str(p) for p in (reg, inv, led, ent, inst, tmpl, chk, g5, g6) if not p.exists()]
    if missing:
        print(json.dumps({"verdict": "FAIL", "error": f"inputs missing: {missing}"}, ensure_ascii=False))
        return 1

    g5m = fixtures / "g5" / "mutants"
    g6m = fixtures / "g6" / "mutants"
    tmp = fixtures / "_tmp"
    for d in (g5m, g6m, tmp):
        d.mkdir(parents=True, exist_ok=True)

    # ---------- 真件副本（正控 + 负例母本） ----------
    reg0 = write(g5m / "registry_copy.tsv", sh(reg))
    inv0 = write(g5m / "gate_inventory_copy.tsv", sh(inv))
    led0 = write(g5m / "snapshot_drift_ledger_copy.tsv", sh(led))
    ent0 = write(g5m / "run_gates_copy.sh", sh(ent))
    inst0 = write(g6m / "instance_copy.tsv", sh(inst))
    tmpl0 = write(g6m / "template_copy.tsv", sh(tmpl))
    chk0 = write(g6m / "checklist_copy.md", sh(chk))

    def jout(tag: str) -> str:
        return f"--json={tmp / (tag + '.json')}"

    cases = []

    def add(gate: str, cid: str, mutation: str, expected: list, rc: int, codes: list, tail: str) -> None:
        ok = (rc == 0 and not codes) if not expected else (rc != 0 and any(c in codes for c in expected))
        extra = [c for c in codes if c not in expected]
        cases.append({"gate": gate, "id": cid, "mutation": mutation,
                      "expected_codes": expected or ["<none: positive control>"],
                      "rc": rc, "failing_codes": codes, "unexpected_extra_failures": extra,
                      "verdict": "PASS(符合预期)" if ok else "FAIL(不合预期)", "ok": ok,
                      "stdout_tail": tail if not ok else ""})

    # G5 用例用的最小突变一律按「行×列」定位（不靠全文替换）：先解析真件副本，改一格，再写回。
    def tsv_rows(txt: str) -> tuple:
        lines = [ln for ln in txt.splitlines() if ln and not ln.startswith("#")]
        hdr = lines[0].split("\t")
        return hdr, [ln.split("\t") for ln in lines[1:]]

    def tsv_write(path: Path, hdr: list, body: list) -> Path:
        return write(path, "\n".join(["\t".join(hdr)] + ["\t".join(r) for r in body]) + "\n")

    def cell_edit(txt: str, idcol: str, rid: str, col: str, value: str, path: Path) -> Path:
        hdr, body = tsv_rows(txt)
        ci, ri = hdr.index(col), hdr.index(idcol)
        hit = 0
        for r in body:
            if r[ri] == rid:
                r[ci] = value
                hit += 1
        assert hit == 1, f"cell_edit target not unique: {rid}.{col} -> {hit}"
        return tsv_write(path, hdr, body)

    # ================= G5 =================
    rc, codes, tail = run_gate(g5, ["--registry", str(reg0), "--gate-inventory", str(inv0),
                                    "--drift-ledger", str(led0), "--entry", str(ent0), jout("g5_p0")])
    add("G5", "P0_POSITIVE_CONTROL", "正控：真件未突变副本", [], rc, codes, tail)

    regN1 = cell_edit(sh(reg0), "件ID", "L6-04", "路径", "/tmp/NO_SUCH_GATE_FILE_G5.py",
                      g5m / "N1_missing_file_registry.tsv")
    rc, codes, tail = run_gate(g5, ["--registry", str(regN1), "--gate-inventory", str(inv0),
                                    "--drift-ledger", str(led0), "--entry", str(ent0), jout("g5_n1")])
    add("G5", "N1_MISSING_FILE", "台账 L6-04 路径 → 不存在路径（缺件）", ["G5-C04"], rc, codes, tail)

    regN2 = cell_edit(sh(reg0), "件ID", "L6-04", "sha256", "0" * 64,
                      g5m / "N2_sha_drift_registry.tsv")
    rc, codes, tail = run_gate(g5, ["--registry", str(regN2), "--gate-inventory", str(inv0),
                                    "--drift-ledger", str(led0), "--entry", str(ent0), jout("g5_n2")])
    add("G5", "N2_SHA_DRIFT", "台账 L6-04 sha256 → 全 0（摘要漂移，且不在漂移记账内）", ["G5-C05"], rc, codes, tail)

    entN3 = mutate(ent0, g5m / "N3_unregistered_entry.sh",
                   'run_gate "G6 gate_change_control (eight machine rules)" \\\n  python3 tests/gate_change_control.py',
                   'run_gate "G6 gate_change_control (eight machine rules)" \\\n  python3 tests/gate_change_control.py\nrun_gate "probe" \\\n  python3 tests/gate_unregistered_probe.py')
    rc, codes, tail = run_gate(g5, ["--registry", str(reg0), "--gate-inventory", str(inv0),
                                    "--drift-ledger", str(led0), "--entry", str(entN3), jout("g5_n3")])
    add("G5", "N3_UNREG_LOAD", "入口新增一行调用未登记脚本（未登记加载）", ["G5-C07"], rc, codes, tail)

    regN4 = cell_edit(sh(reg0), "件ID", "L1-22", "备注",
                      "到期日条款：到期（2026-10-01）须由 PI 决定翻档或延长（原声明 2026-10-19）",
                      g5m / "N4_expired_cert_registry.tsv")
    rc, codes, tail = run_gate(g5, ["--registry", str(regN4), "--gate-inventory", str(inv0),
                                    "--drift-ledger", str(led0), "--entry", str(ent0), jout("g5_n4")])
    add("G5", "N4_CERT_EXPIRED", "台账 L1-22 声明的到期日 2026-10-19 → 2026-10-01（早于 as_of）",
        ["G5-C08"], rc, codes, tail)

    regN6 = cell_edit(sh(reg0), "件ID", "L0-06", "变更口", "TBD",
                      g5m / "N6_owner_placeholder_registry.tsv")
    rc, codes, tail = run_gate(g5, ["--registry", str(regN6), "--gate-inventory", str(inv0),
                                    "--drift-ledger", str(led0), "--entry", str(ent0), jout("g5_n6")])
    add("G5", "N6_OWNER_PLACEHOLDER", "台账 L0-06 变更口 → TBD（owner 占位）", ["G5-C03"], rc, codes, tail)

    # N5：把某条记账行「重新指向一个未漂移的件」（该件现取 sha == 登记 sha）⇒ 该免检条已无存在理由。
    # 这是可构造的过期形态：C06 必须判 stale dispensation；同时 C05 会因原漂移件失去记账而额外失败（如实记录）。
    led_rows = [ln.split("\t") for ln in sh(led0).splitlines() if ln and not ln.startswith("#")]
    lh, lrows = led_rows[0], led_rows[1:]
    rhdr, rbody = tsv_rows(sh(reg0))
    stable = next(r for r in rbody if r[rhdr.index("件ID")] == "L6-04")
    lrows2 = []
    for r in lrows:
        r = list(r)
        if r[lh.index("件ID")] == "L6-13":
            r[lh.index("件ID")] = "L6-04"                      # 指向未漂移件
            r[lh.index("registered_sha256")] = stable[rhdr.index("sha256")]
            r[lh.index("observed_sha256")] = stable[rhdr.index("sha256")]
            r[lh.index("cause")] = "TEST_STALE_DISPENSATION"
        lrows2.append(r)
    ledN5 = write(g5m / "N5_stale_ledger.tsv", "\n".join(["\t".join(lh)] + ["\t".join(r) for r in lrows2]) + "\n")
    rc, codes, tail = run_gate(g5, ["--registry", str(reg0), "--gate-inventory", str(inv0),
                                    "--drift-ledger", str(ledN5), "--entry", str(ent0), jout("g5_n5")])
    add("G5", "N5_LEDGER_STALE", "记账行重新指向「未漂移」的件（免检条已无存在理由 ⇒ C06 判 stale）",
        ["G5-C06"], rc, codes, tail)

    # ================= G6 =================
    rc, codes, tail = run_gate(g6, ["--instance", str(inst0), "--template", str(tmpl0),
                                    "--checklist", str(chk0), jout("g6_p0")])
    add("G6", "P0_POSITIVE_CONTROL", "正控：真件未突变副本", [], rc, codes, tail)

    row = [ln for ln in sh(inst0).splitlines() if ln and not ln.startswith("#")]
    hdr, body = row[0].split("\t"), [ln.split("\t") for ln in row[1:]]
    idx = {c: i for i, c in enumerate(hdr)}
    b2 = [list(r) for r in body]
    b2[0][idx["E4"]] = ""
    iN1 = write(g6m / "N1_required_instance.tsv", "\n".join(["\t".join(hdr)] + ["\t".join(r) for r in b2]) + "\n")
    rc, codes, tail = run_gate(g6, ["--instance", str(iN1), "--template", str(tmpl0),
                                    "--checklist", str(chk0), jout("g6_n1")])
    add("G6", "N1_REQUIRED_EMPTY", "E4 置空（必填缺项）", ["G6-R1"], rc, codes, tail)

    def edit(body_rows, cell, value, ev=None):
        b = [list(r) for r in body_rows]
        b[0][idx[cell]] = value
        if ev is not None:
            b[0][idx[cell + "_evidence"]] = ev
        return b

    def emit(tag, b):
        p = write(g6m / tag, "\n".join(["\t".join(hdr)] + ["\t".join(r) for r in b]) + "\n")
        return run_gate(g6, ["--instance", str(p), "--template", str(tmpl0),
                             "--checklist", str(chk0), jout(tag.replace(".tsv", ""))])

    rc, codes, tail = emit("N2_no_anchor_instance.tsv", edit(body, "Q2", "拟修层 = 首因层", "见报告"))
    add("G6", "N2_EVIDENCE_NO_ANCHOR", "Q2_evidence → 「见报告」（无可核验锚）", ["G6-R2"], rc, codes, tail)

    cur_q3 = body[0][idx["Q3"]]
    rc, codes, tail = emit("N3_gains_only_instance.tsv",
                           edit(body, "Q3", cur_q3.replace("回退", "增益").replace("负向", "正向")
                                .replace("不单调", "单调").replace("退步", "进步")))
    add("G6", "N3_ROLLBACK_TERM_REMOVED", "Q3 删除回退/负向词（只报增益）", ["G6-R5"], rc, codes, tail)

    bN4 = [list(r) for r in body]
    bN4[0][idx["Q4"]] = "判据预注册：G5 八项检查 + G6 八条规则，开封前冻结。"
    bN4[0][idx["Q4_evidence"]] = "判据节见 /home/ubuntu/EYEKB_REPO/docs/VERIFY_CONTRACT_G5G6.md（已落盘）"
    rc, codes, tail = emit("N4_no_sha_instance.tsv", bN4)
    add("G6", "N4_PREREG_NO_SHA", "Q4/Q4_evidence 去 sha 锚", ["G6-R6"], rc, codes, tail)

    bN5 = [list(r) for r in body]
    bN5[0][idx["Q5"]] = "逃生门：零接线新增门，既有门逃生门沿用未动；关断后与接线前恒等。"
    bN5[0][idx["Q5_evidence"]] = "见 /home/ubuntu/EYEKB_REPO/docs/GATE_INVENTORY_G5G6.tsv（门清单）"
    rc, codes, tail = emit("N5_no_switch_instance.tsv", bN5)
    add("G6", "N5_ESCAPE_NO_SWITCH", "Q5 去开关名（EYEKB_*）", ["G6-R7"], rc, codes, tail)

    bN6 = [list(r) for r in body]
    bN6[0][idx["M3"]] = bN6[0][idx["M3"]] + " 本次含默认 ON 行为变更（EYEKB_CN_REWRITE 语义）。"
    bN6[0][idx["M3_evidence"]] = bN6[0][idx["M3_evidence"]] + " 见 tests/G4_EXPECTED.json rc=0"
    rc, codes, tail = emit("N6_default_on_instance.tsv", bN6)
    add("G6", "N6_PRECOND_UNREGISTERED", "M3 声明默认 ON 行为变更但未登记门前置（VERIFY_CONTRACT）",
        ["G6-R8"], rc, codes, tail)

    bN7 = [list(r) for r in body]
    bN7[0][idx["M3"]] = "回归门：跑了，通过。"
    bN7[0][idx["M3_evidence"]] = "见 /home/ubuntu/EYEKB_REPO/docs/W3_CHANGE_CONTROL_CHECKLIST.md（人读清单）"
    rc, codes, tail = emit("N7_no_threshold_instance.tsv", bN7)
    add("G6", "N7_NO_THRESHOLD_ACTION", "M3 只写「跑了，通过」——无命令/无期望读数（只做格式检查的反面）",
        ["G6-R2-CONCRETE"], rc, codes, tail)

    chk_lines = sh(chk0).splitlines(True)
    drop = [i for i, ln in enumerate(chk_lines) if ln.startswith("| 14 |")]
    assert len(drop) == 1, f"checklist row 14 not uniquely located: {drop}"
    chkN8 = write(g6m / "N8_map_checklist.md", "".join(chk_lines[:drop[0]] + chk_lines[drop[0] + 1:]))
    rc, codes, tail = run_gate(g6, ["--instance", str(inst0), "--template", str(tmpl0),
                                    "--checklist", str(chkN8), jout("g6_n8")])
    add("G6", "N8_CHECKLIST_MAP_GAP", "人读清单 §五 删除第 14 行（规则↔清单映射缺口）", ["G6-MAP"], rc, codes, tail)

    n_ok = sum(1 for c in cases if c["ok"])
    res = {"card": "t_9dce4923 (G5G6 repo gates)", "harness": str(Path(__file__).resolve()),
           "method": "对真件做最小突变（只作用于 fixtures 副本，仓内真件零改动）→ 跑门 → 断言 rc≠0 且命中目标检查码",
           "contract": "正控必须通过（否则门本身不可信）；每个负例必须被拒且报目标检查码；额外失败如实记录",
           "n_cases": len(cases), "n_ok": n_ok, "all_as_expected": n_ok == len(cases),
           "fixtures_dir": str(fixtures), "results": cases,
           "by_gate": {g: {"n": sum(1 for c in cases if c["gate"] == g),
                           "ok": sum(1 for c in cases if c["gate"] == g and c["ok"])}
                       for g in ("G5", "G6")}}
    if a.json:
        Path(a.json).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for c in cases:
        print(f"  [{'OK ' if c['ok'] else 'BAD'}] {c['gate']} {c['id']:<26} rc={c['rc']} "
              f"codes={c['failing_codes']} expect={c['expected_codes']}")
    print(f"G5G6 negative battery: {n_ok}/{len(cases)} as expected -> "
          f"{'PASS' if n_ok == len(cases) else 'FAIL'}")
    return 0 if n_ok == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
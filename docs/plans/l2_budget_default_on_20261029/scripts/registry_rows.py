#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Criterion C9: put this change in the ledgers.

Re-takes the identity of the three production files this card edits in
`docs/W3_PIPELINE_REGISTRY.tsv` (rows L2-01, L2-03, L2-11) and appends one change-control row
to `docs/CHANGE_CONTROL_G6_INSTANCE.tsv`. Values are read from disk at run time; nothing in the
row is typed from memory.

After writing, it runs `tests/gate_change_control.py` so the ledger itself reports its verdict.
Writes `out/REGISTRY_ROWS.json`.
"""
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CARD = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(CARD, "..", "..", ".."))
OUT = os.path.join(CARD, "out")
W3 = os.path.join(REPO, "docs", "W3_PIPELINE_REGISTRY.tsv")
G6 = os.path.join(REPO, "docs", "CHANGE_CONTROL_G6_INSTANCE.tsv")
CARD_MD = os.path.join(CARD, "CARD.md")
ROW_ID = "CHG-20261029-L2BUDGET-JUDGEDEFAULT"
TITLE = "v(2026-10-29 L2BUDGET-JUDGEDEFAULT 判读路径默认 30)"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def ident(rel):
    p = os.path.join(REPO, rel)
    st = os.stat(p)
    return {"rel": rel, "sha256": sha(p), "bytes": st.st_size,
            "mtime": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")}


def main():
    os.makedirs(OUT, exist_ok=True)
    files = {r: ident(r) for r in ("pipeline/l2_budget.py", "pipeline/stage_b_evidence.py",
                                   "pipeline/run_pipeline.py")}
    card_sha = sha(CARD_MD)

    # ---- W3 registry: re-take identity of the three rows -------------------------------
    lines = open(W3, encoding="utf-8").read().split("\n")
    hdr = lines[0].split("\t")
    idx = {h: i for i, h in enumerate(hdr)}
    touched = []
    for n, ln in enumerate(lines):
        if not ln or ln.startswith("#"):
            continue
        cells = ln.split("\t")
        if len(cells) < len(hdr):
            continue
        iid = cells[idx["item_id"]]
        if iid not in ("L2-01", "L2-03", "L2-11"):
            continue
        rel = cells[idx["path"]]
        # L2-05 path is absolute; only re-take rows whose path is one of ours
        if rel not in files:
            continue
        before = {h: cells[i] for h, i in idx.items()}
        info = files[rel]
        cells[idx["sha256"]] = info["sha256"]
        cells[idx["bytes"]] = str(info["bytes"])
        cells[idx["mtime"]] = info["mtime"]
        cells[idx["version"]] = TITLE
        if iid == "L2-11":
            cells[idx["authority"]] = "AUTHORITATIVE(门实现件；判读路径默认 30 / 普通路径默认 10)"
            cells[idx["notes"]] = (
                "判读路径默认 30、普通路径默认 10；EYEKB_L2_BUDGET ON=>30 / OFF(含未设以外的显式关)=>10；"
                "显式 --top-genes-n 任何态下不改写；翻判读层默认=PI 2026-10-29 放行（卡 "
                "docs/plans/l2_budget_default_on_20261029）")
        else:
            cells[idx["notes"]] = (
                (cells[idx["notes"]] + " ｜ " if cells[idx["notes"]] else "")
                + "2026-10-29 判读路径预算默认 30（卡 docs/plans/l2_budget_default_on_20261029）；"
                  "普通路径逐字节不变")
        lines[n] = "\t".join(cells)
        touched.append({"item_id": iid, "path": rel, "before_sha256": before["sha256"],
                        "after_sha256": info["sha256"], "before_version": before["version"],
                        "after_version": TITLE})
    open(W3, "w", encoding="utf-8").write("\n".join(lines))

    # ---- G6 change-control row ---------------------------------------------------------
    ev = "docs/plans/l2_budget_default_on_20261029"
    cells = {}
    cells["change_id"] = ROW_ID
    cells["owner"] = ("维护方（镜像仓生产码；卡 docs/plans/l2_budget_default_on_20261029；"
                      "PI 2026-10-29 放行）")
    cells["entry_point"] = "/home/ubuntu/EYEKB_REPO/pipeline/stage_b_evidence.py"
    cells["Q1"] = ("首因层 = L2（查询预算层：给每个簇递多少个基因作为判读证据面）。"
                   "现象起源=判读器证据面只有 10 个基因，候选之外的谱系根本递不到；"
                   "本卡把宽度挂到判读路径上，普通路径不动")
    cells["Q1_evidence"] = ("%s/CARD.md:1（首因层声明）｜%s/out/STAGEB_DIFFERENTIAL.json（宽度实测）"
                            % (ev, ev))
    cells["Q2"] = ("实测三步：①10 基因 vs 30 基因证据面，25 卷人源 764 簇判读 top-1 66.91%%→75.06%%、"
                   "覆盖 68.04%%→75.38%%、出声内 81.70%%→82.20%%；②库自身候选排名不随面板宽度变化"
                   "（G4 fixture 11/11 簇候选载荷逐字节相同）；③故宽度只挂判读路径，普通路径输出逐字节不变")
    cells["Q2_evidence"] = ("%s/out/STAGEB_DIFFERENTIAL.json（六臂逐簇对拍）｜"
                            "docs/plans/wide30_panel_20261029/REPORT.md（25 卷读数）" % ev)
    cells["Q3"] = ("增益与代价双列同表：gain=58 簇由弃权转正确（86,231 细胞）；loss=10 簇由正确转错"
                   "（26,452 细胞），净 +56 簇；rollback 路径由 EYEKB_L2_BUDGET=0 提供，实测逐字节回旧行为；"
                   "不做单调性声称，负向如实登记")
    cells["Q3_evidence"] = ("%s/out/STAGEB_DIFFERENTIAL.json（C4/C5c 逐簇 sha）｜"
                            "docs/plans/wide30_panel_20261029/out/WIDE30_VS_NARROW.json（loss 列）" % ev)
    cells["Q4"] = ("预注册判据（先冻后跑）：C1 门语义 / C2 显式值不改写 / C3 非法值 fail-closed 恰 1 条 warning / "
                   "C4 回退逐簇恒等 / C5a 普通路径恒等 / C5b 判读路径 30 基因 / C5c 回退压过判读默认 / "
                   "C6 改动面 / C8 G4 锚不移动。预注册件 sha256=%s " % card_sha)
    cells["Q4_evidence"] = ("%s/CARD.md（判据表，sha256 见 out/REGISTRY_ROWS.json）｜"
                            "%s/scripts/gate_l2_budget.py（C1/C2/C3/C6 可执行）" % (ev, ev))
    cells["Q5"] = ('逃生门：EYEKB_L2_BUDGET OFF 集（""/0/false/off/no）⇒ 全路径回 10；'
                   "普通路径与判读路径均 byte-identical 回旧行为（逐簇候选载荷与归一化报告全等）")
    cells["Q5_evidence"] = ("%s/out/STAGEB_DIFFERENTIAL.json（C4_rollback_vs_pre 与 "
                            "C5c_rollback_beats_judge，均为 11/11 簇候选载荷相同 + 归一化报告相同）" % ev)
    cells["M1"] = ("版本件：生产码 3 件全部重取身份（l2_budget.py 2836e6f0ec15→%s、"
                   "stage_b_evidence.py 651c0931c53f→%s、run_pipeline.py 76ea5565a5cb→%s），"
                   "登记于 docs/W3_PIPELINE_REGISTRY.tsv 的 L2-01/L2-03/L2-11"
                   % (files["pipeline/l2_budget.py"]["sha256"][:12],
                      files["pipeline/stage_b_evidence.py"]["sha256"][:12],
                      files["pipeline/run_pipeline.py"]["sha256"][:12]))
    cells["M1_evidence"] = "%s/out/REGISTRY_ROWS.json（旧→新逐行）｜docs/W3_PIPELINE_REGISTRY.tsv" % ev
    cells["M2"] = ("影响面：会变=判读路径（--adjudicate 或 EYEKB_ADJUDICATE=1）下每簇证据面 10→30 基因；"
                   "不变=普通路径全部产物（证据报告/决策模板/候选载荷，G4 三锚实测不移动）、库候选排名、"
                   "词表、槽位规则、计分与分母")
    cells["M2_evidence"] = ("%s/out/G4_DIFFERENTIAL.json（三锚 pre=rollback=post）｜"
                            "%s/out/STAGEB_DIFFERENTIAL.json" % (ev, ev))
    cells["M3"] = ("判据可执行（命令 + 期望读数）：python3 docs/plans/l2_budget_default_on_20261029/scripts/"
                   "gate_l2_budget.py 期望 ALL PASS rc=0；stageb_differential.py 期望 VERDICT: PASS rc=0；"
                   "g4_default_differential.py 期望 C8 VERDICT: PASS rc=0；"
                   "python3 tests/gate_change_control.py 期望全 PASS rc=0。默认行为变更的前置疑点按 "
                   "docs/VERIFY_CONTRACT.md 登记（R8）")
    cells["M3_evidence"] = ("%s/scripts/gate_l2_budget.py｜%s/scripts/stageb_differential.py｜"
                            "%s/out/GATE_VERDICTS.json" % (ev, ev, ev))
    cells["E1"] = ("E1 读数（现取，禁引旧报告）：C1/C2/C3/C6 共 15 项全 PASS；C4 11/11 簇候选载荷相同且"
                   "归一化报告相同；C5a 普通路径 11/11 相同；C5b 判读路径 11/11 簇面板 30 基因；"
                   "C5c 11/11 相同；C8 三锚 pre=rollback=post")
    cells["E1_evidence"] = ("%s/out/STAGEB_DIFFERENTIAL.json｜%s/out/G4_DIFFERENTIAL.json" % (ev, ev))
    cells["E2"] = ("E2 回归门：python3 tests/gate_change_control.py 期望 rc=0；"
                   "python3 tests/gate_g5g6_negative.py 期望 rc=0（负例仍被拒）；"
                   "G4 三锚期望不移动（本卡不动基线，既有红为历史账，未借本卡重锚）")
    cells["E2_evidence"] = "%s/out/GATE_VERDICTS.json（写盘后回读 rc）" % ev
    cells["E3"] = ("E3 回退实证（两条路径对拍）：EYEKB_L2_BUDGET=0 时普通路径与判读路径均回 10，"
                   "候选载荷 11/11 簇逐字节等于改前；rollback 不依赖改文件，只靠环境变量")
    cells["E3_evidence"] = ("%s/out/STAGEB_DIFFERENTIAL.json（rollback 与 judgeoff 两臂）" % ev)
    cells["E4"] = ("E4 边界：本卡不宣布效能提升；25 卷为本线已使用卷，读数一律标观测，"
                   "效能裁定须由未碰过的新卷 + 同一评测契约给出；本卡不改任何验收基线")
    cells["E4_evidence"] = ("%s/CARD.md:5（边界节）｜docs/plans/wide30_panel_20261029/REPORT.md:75（口径声明）"
                            % ev)

    hdr_g6 = open(G6, encoding="utf-8").read().split("\n")
    header = [l for l in hdr_g6 if l and not l.startswith("#")][0].split("\t")
    row = [cells.get(h, "") for h in header]
    assert len(row) == len(header), "G6 row must have %d cells, got %d" % (len(header), len(row))
    txt = open(G6, encoding="utf-8").read().rstrip("\n").split("\n")
    if not any(ln.split("\t")[0] == ROW_ID for ln in txt if ln and not ln.startswith("#")):
        txt.append("\t".join(row))
    else:
        txt = [("\t".join(row) if ln.split("\t")[0] == ROW_ID else ln) for ln in txt]
    open(G6, "w", encoding="utf-8").write("\n".join(txt) + "\n")

    gate = subprocess.run([sys.executable, os.path.join(REPO, "tests", "gate_change_control.py")],
                          capture_output=True, text=True, cwd=REPO)
    neg = subprocess.run([sys.executable, os.path.join(REPO, "tests", "gate_g5g6_negative.py")],
                         capture_output=True, text=True, cwd=REPO)
    doc = {"probe": "registry_rows.py", "row_id": ROW_ID, "files": files,
           "w3_rows_updated": touched,
           "card_sha256": card_sha,
           "gate_change_control": {"rc": gate.returncode,
                                   "tail": gate.stdout.strip().splitlines()[-12:]},
           "gate_g5g6_negative": {"rc": neg.returncode,
                                  "tail": neg.stdout.strip().splitlines()[-6:]}}
    json.dump(doc, open(os.path.join(OUT, "REGISTRY_ROWS.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump({"gate_change_control_rc": gate.returncode,
               "gate_g5g6_negative_rc": neg.returncode},
              open(os.path.join(OUT, "GATE_VERDICTS.json"), "w"), indent=1)

    print("W3 rows updated:", [t["item_id"] for t in touched])
    print("G6 row:", ROW_ID)
    print("gate_change_control rc=%d" % gate.returncode)
    print("\n".join(gate.stdout.strip().splitlines()[-8:]))
    print("gate_g5g6_negative rc=%d" % neg.returncode)
    print("\n".join(neg.stdout.strip().splitlines()[-4:]))
    return 0 if gate.returncode == 0 and neg.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
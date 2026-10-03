# -*- coding: utf-8 -*-
"""
errata_run5face_t133f7dea.py — in-place erratum applier for EVAL_RUN5FACE_20260925.md, attribution ②
Card: t_133f7dea (2026-09-25)
Defect: §attribution② and §qualitative wrongly attributed Q6::24's kb_top1 and the three-vote consensus to Keratocytes;
     the landed artifacts (truth_table/p2_strict/verdict, mutually corroborating) = a Myofibroblast/SMC mural takeover chain.
Discipline: errata-source-fix —— true .bak pre-image (created once only) + PRE sha assertion + anchor count==1 else
     abort without landing + version line + end-of-document erratum record + idempotent re-entry (ALREADY_APPLIED).
Red line: only touch the two passages bound to the sentence; all other criteria/numbers untouched. P1 21/33, P2 1/33, PASS/FAIL conclusions unchanged.
NOTE: string literals below are the historical run's embedded content (matched against and written into the
frozen erratum document); they are intentionally untranslated per the NEVER-TOUCH rule. Only comments were translated.
"""
import hashlib
import json
import os
import shutil
import sys

ROOT = "/mnt/D/EyeKB/plans/evalset"
TGT = os.path.join(ROOT, "EVAL_RUN5FACE_20260925.md")
BAK = TGT + ".bak_20260925_t133f7dea"
OUTDIR = os.path.join(ROOT, "errata_run5face_t133f7dea_20260925")
LEDGER = os.path.join(OUTDIR, "landing_ledger.json")
LOG = os.path.join(OUTDIR, "apply.log")
PRE_CANON = os.path.join(OUTDIR, "PRE_CANONICAL_sha.txt")

PRE_SHA_EXPECT = "d77ec739daeb4544dcbcbd0404768e60eb50c5ee3a5e1aded91482ac50cbdc1b"

# ---- anchors and replacements (full-line exact) ----
OLD_L18 = "② **Keratocytes 词条过火（P2 实证 1 簇 + 疑似连坐）**：Q6::24 author=Pericytes 6477/6565（98.7% 纯壁细胞），kb_top1=Keratocytes，三票共识跟词条判 Keratocytes——**上午 keratocyte 闭环救回 Q6::15 的同一把钥匙，这轮把 Pericytes 簇开成了别人的门**。KERA/ALDH3A1/NNMT 面板对 pericyte 的交叉反应从未被检过（keratocyte 补录时的 D001 审计盲区：眼表词条用视网膜图谱做不了邻类审计，OUT 22 类的代价此刻显形）。"

NEW_L18 = "② **Myofibroblast/SMC mural 词条接管链（P2 实证 1 簇）**：Q6::24 author=Pericytes 6477/6565（98.7% 纯壁细胞），kb_top1=Myofibroblast，kb_names=Myofibroblast|SMC|MG（Pericyte 词条未上榜），三票共识=Smooth Muscle Cells——这轮把 Pericytes 簇开成别人门的是 Myofibroblast/SMC mural 词条接管链（映射歧义 Myofibroblast→Fibroblasts|Smooth Muscle Cells ambiguous），不是 Keratocytes。原稿把本簇词条归属与三票共识错记为 Keratocytes，经 KB6b 卡落地件核对（run5_truth_table.tsv / run5_p2_pollution_table_strict.tsv / run5_verdict.json 三件互证一致）证伪，已按落地件改写并见卷末★勘误记录。Keratocytes 的真实交叉信号在 Q6::20（truth=Epithelium，kb_top1=Keratocytes）：判读员正确覆盖词条判 Epithelium（P1 命中）；kb_top1=Keratocytes 的 5 簇（Q6::15/21/20/14/28）无一产生跟票（3 簇正确覆盖、2 簇平票），原「疑似连坐」一并证伪。KERA/ALDH3A1/NNMT 面板对 pericyte 的交叉反应从未被检过（keratocyte 补录时的 D001 审计盲区：眼表词条用视网膜图谱做不了邻类审计，OUT 22 类的代价此刻显形）——该残留限制仍成立，但与本案无关，本案机制在 mural 词条链。"

OLD_L23 = "- P2 PASS 但 1/33 擦线——**词条反噬第一案成立**，Keratocytes 面板必须复审（KB6b 卡）。"

NEW_L23 = "- P2 PASS 但 1/33 擦线——**词条反噬第一案成立**（反噬主体按落地件修正为 Myofibroblast/SMC mural 词条链，非 Keratocytes），mural 词条与 Pericyte 边界必须复审（KB6b 卡，落地件 plans/kb6b_face_20260925/）。"

ANCHOR_VER = "- 裁决件：scoring/run5_verdict.json（脚本 scripts/run5_verdict.py）"
VER_LINE = "> 版本：v1.1（2026-09-25，t_133f7dea 勘误：§归因②/§定性 的 Q6::24 词条归属按 KB6b 落地件就地改写为 Myofibroblast/SMC mural 链；P2 1/33 计数与 PASS 结论不变，其余判据/数字零触碰。★卷末勘误记录）"

ERRATA_SECTION = """
## ★勘误记录（v1.0→v1.1 · t_133f7dea · 2026-09-25）
- 缺陷：原 §归因② 与 §定性 把 P2 违例簇 Q6::24 的 kb_top1 与三票共识归为 Keratocytes（并推测连坐）。
- 证伪（落地件三件互证一致）：scoring/run5_truth_table.tsv 行 Q6::24：kb_top1=Myofibroblast、kb_names=Myofibroblast|SMC|MG、三票全=Smooth Muscle Cells（Pericyte 未上榜）；scoring/run5_p2_pollution_table_strict.tsv 与 scoring/run5_verdict.json P2_strict.evidence 同口径。kb_top1=Keratocytes 的 5 簇（Q6::15/21/20/14/28）无一产生跟票：Q6::21/20/14 三票正确覆盖（P1 命中），Q6::15/28 平票无共识。
- 修正：归因②改绑 Myofibroblast/SMC mural 词条接管链；Keratocytes 真实交叉信号登记在 Q6::20（truth=Epithelium，判读员正确覆盖，属 P1 命中而非违例）。P2 1/33 计数与 PASS 结论不变（violation 定义按落地件仍成立）；P1 21/33 及其余判据零触碰。
- 下游引用扫描（claim-propagation 只读）：KB6b 卡 AUDIT_KB6b_D002_separation.md L12/L23、PREREG_KB6b.md L9、review/prereg_review_prompt.txt L45 引原句为被审对象 = 勘误语境豁免不改；KB6 主报告（plans/kb6_audit_20260924/）、plans/BRIEF_*、稿面文件无原句复述（M1 草稿暂无该句落盘）。明细见 errata_run5face_t133f7dea_20260925/errata_scan.tsv。
- 证据链：前像 EVAL_RUN5FACE_20260925.md.bak_20260925_t133f7dea（PRE sha d77ec739daeb4544dcbcbd0404768e60eb50c5ee3a5e1aded91482ac50cbdc1b）；落纸器 scripts/errata_run5face_t133f7dea.py；台账+扫描件 plans/evalset/errata_run5face_t133f7dea_20260925/。
"""


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def log(msg, lines_log):
    print(msg)
    lines_log.append(msg)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    lines_log = []

    raw = open(TGT, "rb").read()
    if b"\r" in raw:
        print("ABORT: 目标件含 CR，本卡按 LF 设计")
        sys.exit(2)
    cur = raw.decode("utf-8")

    # idempotency guard
    if "## ★勘误记录（v1.0→v1.1 · t_133f7dea · 2026-09-25）" in cur:
        log("ALREADY_APPLIED（幂等重入）：目标件已含本卡勘误记录，零写入退出。", lines_log)
        open(LOG, "a", encoding="utf-8").write("\n".join(lines_log) + "\n")
        sys.exit(0)

    # PRE sha assertion (against current state, before landing)
    pre_sha = sha(TGT)
    if pre_sha != PRE_SHA_EXPECT:
        print("ABORT: PRE sha 不匹配（可能有并发写入），不落盘")
        print("  got :", pre_sha)
        print("  want:", PRE_SHA_EXPECT)
        sys.exit(3)

    # true .bak pre-image created once only
    if not os.path.exists(BAK):
        shutil.copy2(TGT, BAK)
        log("前像已建: %s (sha==PRE 断言: %s)" % (os.path.basename(BAK), sha(BAK) == pre_sha), lines_log)
    else:
        bak_sha = sha(BAK)
        if bak_sha != PRE_SHA_EXPECT:
            print("ABORT: 既有 .bak 与 PRE_CANONICAL 不符，勿猜")
            print("  bak :", bak_sha)
            sys.exit(4)
        log("前像已存在（只建一次纪律通过）: %s" % os.path.basename(BAK), lines_log)
    if not os.path.exists(PRE_CANON):
        open(PRE_CANON, "w", encoding="utf-8").write(PRE_SHA_EXPECT + "  EVAL_RUN5FACE_20260925.md  pre-image of .bak_20260925_t133f7dea  card=t_133f7dea\n")

    lines = cur.split("\n")

    # anchor count==1 assertions
    ops = []
    def one_hit(pred, desc):
        hits = [i for i, l in enumerate(lines) if pred(l)]
        if len(hits) != 1:
            print("ABORT: 锚点 %s 命中 %d 次（应=1），不落盘" % (desc, len(hits)))
            sys.exit(5)
        return hits[0]

    i18 = one_hit(lambda l: l == OLD_L18, "OLD_L18(整行)")
    i23 = one_hit(lambda l: l == OLD_L23, "OLD_L23(整行)")
    iver = one_hit(lambda l: l == ANCHOR_VER, "版本行锚点(整行)")
    if any(l == VER_LINE for l in lines):
        print("ABORT: 版本行已在位（半落纸态？）"); sys.exit(6)
    if "## ★勘误记录" in cur:
        print("ABORT: 已存在其他★勘误记录节，勿双写"); sys.exit(7)

    lines[i18] = NEW_L18
    ops.append({"op": "replace_line", "pre_line": i18 + 1, "tag": "归因②整行改写",
                "old_len": len(OLD_L18), "new_len": len(NEW_L18)})
    lines[i23] = NEW_L23
    ops.append({"op": "replace_line", "pre_line": i23 + 1, "tag": "定性节KB6b指针行改写",
                "old_len": len(OLD_L23), "new_len": len(NEW_L23)})
    # insertion order: note that inserting shifts line numbers -- insert back-to-front to avoid misalignment
    # version line: inserted after the verdict-artifact line
    lines.insert(iver + 1, VER_LINE)
    ops.append({"op": "insert_after_line", "pre_line": iver + 1, "tag": "版本行 v1.1"})
    # end-of-document erratum record
    body = "\n".join(lines)
    if not body.endswith("\n"):
        body += "\n"
    body += ERRATA_SECTION
    ops.append({"op": "append", "tag": "卷末★勘误记录（6行）"})

    open(TGT, "wb").write(body.encode("utf-8"))
    post_sha = sha(TGT)
    log("落纸完成 PRE=%s POST=%s" % (pre_sha, post_sha), lines_log)

    # replay proof: applying the same ops to .bak must reproduce the current file byte-for-byte
    blines = open(BAK, "rb").read().decode("utf-8").split("\n")
    j18 = [i for i, l in enumerate(blines) if l == OLD_L18][0]
    j23 = [i for i, l in enumerate(blines) if l == OLD_L23][0]
    jv = [i for i, l in enumerate(blines) if l == ANCHOR_VER][0]
    blines[j18] = NEW_L18
    blines[j23] = NEW_L23
    blines.insert(jv + 1, VER_LINE)
    bbody = "\n".join(blines)
    if not bbody.endswith("\n"):
        bbody += "\n"
    bbody += ERRATA_SECTION
    replay_ok = (bbody.encode("utf-8") == open(TGT, "rb").read())
    log("重放证明（.bak+声明ops==现件逐字节）: %s" % ("PASS" if replay_ok else "FAIL"), lines_log)

    # zero-claim residue: the defective sentence must not persist in assertive form
    residue = body.count(OLD_L18) + body.count(OLD_L23)
    log("缺陷原句残留计数: %d（应=0）" % residue, lines_log)

    ledger = {
        "card": "t_133f7dea",
        "file": TGT,
        "bak": BAK,
        "pre_sha256": pre_sha,
        "post_sha256": post_sha,
        "ops": ops,
        "replay_byte_identical": replay_ok,
        "defect_sentence_residue": residue,
    }
    with open(LEDGER, "w", encoding="utf-8") as f:
        json.dump(ledger, f, ensure_ascii=False, indent=1)
    log("台账: %s" % LEDGER, lines_log)
    open(LOG, "a", encoding="utf-8").write("\n".join(lines_log) + "\n")
    if not replay_ok or residue != 0:
        sys.exit(8)


if __name__ == "__main__":
    main()

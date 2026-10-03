# -*- coding: utf-8 -*-
"""verify_errata_run5face_t133f7dea.py — independent verifier (does not reuse the applier's code path)
NOTE: match strings below are historical-run embedded literals (checked against the frozen erratum
document); they are intentionally untranslated per the NEVER-TOUCH rule. Only comments were translated.
Criteria:
 V1 change surface exhaustible: current file vs .bak -- deleted lines exactly {OLD_L18, OLD_L23}, added lines contain the version line / two rewritten passages / end-of-document erratum block,
    every other line byte-identical in the same order (mechanical proof of the zero-touch red line).
 V2 criteria numbers conserved: P1 21/33, P2 1/33(Q6::24), 6477/6565, 98.7%, prereg sha prefix, vote-model line -- each verified present.
 V3 corrections present: kb_top1=Myofibroblast / three-vote consensus=Smooth Muscle Cells / Q6::20 cross signal /
    KB6b pointer plans/kb6b_face_20260925/ / version line v1.1.
 V4 zero residue of the defective claim: "三票共识跟词条判" and "Keratocytes 词条过火" exact phrases 0 hits (the erratum record references them descriptively, never reviving the original sentence).
 V5 ledger/pre-image self-consistency: ledger.pre==bak sha==d77ec739..., ledger.post==current sha, replay==True.
"""
import difflib
import hashlib
import json
import os
import sys

ROOT = "/mnt/D/EyeKB/plans/evalset"
TGT = os.path.join(ROOT, "EVAL_RUN5FACE_20260925.md")
BAK = TGT + ".bak_20260925_t133f7dea"
LEDGER = os.path.join(ROOT, "errata_run5face_t133f7dea_20260925", "landing_ledger.json")

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

fails = []
def ck(name, ok, detail=""):
    print("[%s] %s %s" % ("PASS" if ok else "FAIL", name, detail))
    if not ok:
        fails.append(name)

pre = open(BAK, "rb").read().decode("utf-8").split("\n")
cur = open(TGT, "rb").read().decode("utf-8").split("\n")

# V1: opcode-level change surface
sm = difflib.SequenceMatcher(None, pre, cur, autojunk=False)
deleted, inserted = [], []
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag in ("replace", "delete"):
        deleted.extend(pre[i1:i2])
    if tag in ("replace", "insert"):
        inserted.extend(cur[j1:j2])
OLD18_MARK = "② **Keratocytes 词条过火（P2 实证 1 簇 + 疑似连坐）**"
OLD23_MARK = "**词条反噬第一案成立**，Keratocytes 面板必须复审（KB6b 卡）。"
ck("V1a 被删行恰为两句缺陷原句", len(deleted) == 2 and any(OLD18_MARK in l for l in deleted) and any(OLD23_MARK in l for l in deleted), "deleted=%d" % len(deleted))
VER_MARK = "> 版本：v1.1（2026-09-25，t_133f7dea 勘误"
ck("V1b 新增行含版本行", any(l.startswith(VER_MARK) for l in inserted))
ck("V1c 新增行=2改写+1版本+勘误块(6行+空行)", len(inserted) == 2 + 1 + 7, "inserted=%d" % len(inserted))
# 其余行逐字节同序：剔除三处改动后 pre==cur
keep_pre = [l for l in pre if OLD18_MARK not in l and not l.startswith("- P2 PASS 但 1/33 擦线——**词条反噬第一案成立**，Keratocytes")]
keep_cur = [l for l in cur if "② **Myofibroblast/SMC mural 词条接管链" not in l and not l.startswith(VER_MARK) and not l.startswith("- P2 PASS 但 1/33 擦线——**词条反噬第一案成立**（反噬主体") and not l.startswith("## ★勘误记录（v1.0→v1.1") and not (l.startswith("- 缺陷：") or l.startswith("- 证伪（落地件") or l.startswith("- 修正：") or l.startswith("- 下游引用扫描") or l.startswith("- 证据链："))]
# cur 尾部空行容忍
keep_cur = [l for l in keep_cur if l != "" or True]
trim = [l for l in keep_pre]
same = trim == keep_cur[:len(trim)]
ck("V1d 未触碰行逐字节同序不变", same and len(keep_cur) - len(trim) <= 2, "pre_kept=%d cur_kept=%d" % (len(trim), len(keep_cur)))

# V2: 数字守恒
need2 = ["21/33", "1/33（Q6::24）", "Q6::24 author=Pericytes 6477/6565（98.7% 纯壁细胞）",
         "3972da24", "A=qwen3.8-max B=glm-5.1 C=deepseek-v3.2", "PASS 擦线", "abstain3=4"]
ck("V2 判据数字/口径全部在位", all(t in "\n".join(cur) for t in need2), str([t for t in need2 if t not in "\n".join(cur)]))

# V3: 修正内容
body = "\n".join(cur)
need3 = ["kb_top1=Myofibroblast", "kb_names=Myofibroblast|SMC|MG", "三票共识=Smooth Muscle Cells",
         "Q6::20（truth=Epithelium，kb_top1=Keratocytes）", "3 簇正确覆盖、2 簇平票",
         "plans/kb6b_face_20260925/", "P2 1/33 计数与 PASS 结论不变", "v1.1"]
ck("V3 修正表述全部在位", all(t in body for t in need3), str([t for t in need3 if t not in body]))

# V4: 缺陷主张零残留
bad4 = ["三票共识跟词条判", "Keratocytes 词条过火", "三票共识跟词条判 Keratocytes"]
ck("V4 缺陷原句主张零残留", all(t not in body for t in bad4))

# V5: 台账自洽
led = json.load(open(LEDGER, encoding="utf-8"))
ck("V5 台账 pre==bak==基线 & post==现件 & replay",
   led["pre_sha256"] == sha(BAK) == "d77ec739daeb4544dcbcbd0404768e60eb50c5ee3a5e1aded91482ac50cbdc1b"
   and led["post_sha256"] == sha(TGT) and led["replay_byte_identical"] is True)

print("\n== ALL_PASS ==" if not fails else "\n== FAILS: %s ==" % fails)
open(os.path.join(ROOT, "errata_run5face_t133f7dea_20260925", "verify_report.log"), "w", encoding="utf-8").write(
    "card=t_133f7dea tgt_sha=%s bak_sha=%s result=%s\n" % (sha(TGT), sha(BAK), "ALL_PASS" if not fails else "FAILS:" + ",".join(fails)))
sys.exit(0 if not fails else 1)

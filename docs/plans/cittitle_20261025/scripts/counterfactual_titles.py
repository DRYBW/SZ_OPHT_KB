#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""counterfactual_titles.py — CITTITLE (card t_d8e7f2d4): measure the title key before and after the
backfill, and attribute the change, so "the title key improved" is a reading and not a claim.

Question this answers: *did the citation side's missing/clipped title key actually decide the
match rate, or was the low rate telling us the two libraries really disagree?*

Design (stated up front, because two of the answers are only meaningful together):
  * The unit of the headline table is the DISTINCT CITED PAPER (denominator = the number of distinct
    pmids in the frozen registry), mirroring the LINKKEY card's denominator so the readings are
    comparable. A per-record table is emitted next to it.
  * The pre-fix title of a paper is the LONGEST non-empty title among its citation records (the
    LINKKEY rule: on the clipped side the longest value carries the most information).
  * Caliber A = the normalised titles are equal; caliber B = their first 40 normalised characters are
    equal. Both are reported; the higher one is never reported alone.
  * Normalisation N1 = NFKC + lower + non-alphanumerics folded to spaces. N2 = N1 after HTML-entity
    unescaping, because 41 corpus titles carry entities (`&lt;i&gt;PRRX1&lt;/i&gt;`) and a reader who
    only ran N1 would file those as "the libraries disagree" when it is a display artefact.
  * **Circularity, stated rather than hidden**: the post-fix comparison joins the citation title and
    the corpus title *from the same corpus*, so its rate is ~100% BY CONSTRUCTION. It is reported
    because it is the definition of the repaired key, but it carries no evidence that the two
    libraries agree. The evidence sits in three non-circular columns that are measured alongside it:
      (i)   the SAME comparison against two OTHER corpus copies (v2.4.2 pointer copy, v2.6-dev) —
            titles backfilled from copy 1, matched against copy 2/3;
      (ii)  the field-agreement controls on the same join (journal, year) — a wrong join would show
            up there as well as in the titles;
      (iii) the pre-fix titles that were ALREADY complete (never clipped, never blank): those were
            written by the frozen builder, not by this card, and matched against the corpus they
            should already be ~100%. Whatever they are, they bound how much of the pre-fix miss was
            "the libraries disagree" rather than "the key was defective".

Reads: the frozen registry, the two delivered twins, the corpus copies. Writes only into out/.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cittitle_common as cc  # noqa: E402

ROOT = Path("/home/ubuntu/EYEKB_REPO")
DEFAULT_OUT = HERE.parent / "out"

FROZEN_REG = ROOT / "kb" / "link_registry" / "LINK_REGISTRY_v1.jsonl"
ANCHOR = DEFAULT_OUT / "LINK_REGISTRY_v2_cittitle.jsonl"
DROPIN = DEFAULT_OUT / "LINK_REGISTRY_v2_cittitle_dropin.jsonl"

PRIMARY = ROOT / "literature_db" / "v2.4.2_2026-09_slim" / "papers.jsonl"
OTHER_CORPORA = (
    Path("/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4.2_2026-09/papers.jsonl"),
    Path("/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10/papers.jsonl"),
)

REASON_TEXT = {
    "TITLE_EMPTY_CITED": "引用侧题名栏为空：该记录由 gene index（全文扫描）路线补入，"
                         "冻结的构建脚本在该路线写死 title=\"\"",
    "TITLE_CAPPED_120": "引用侧题名被硬截到 120 字符：它是语料全题名的前缀，全等判定必然失败",
    "TITLE_DISPLAY_ARTIFACT": "两侧题名只差展示标记：HTML 标签 / HTML 实体 / Unicode 破折号 / "
                              "多余空白（N1 下不等、N2 下相等）——不是两库分歧",
    "TITLE_OTHER_DIFF": "两侧题名在 N1 与 N2 下都不等，且不属上述三类（逐行给出两侧原文）",
    "PREPRINT_ID": "引用侧 id 为预印本 PPR_*（非 8 位 PMID 形态）",
    "CORPUS_MISSING": "该 pmid 在语料中不存在",
}


_TSV_WS = re.compile(r"[\t\r\n]+")


def cell(s) -> str:
    """One TSV cell: embedded tabs/newlines are folded to spaces.

    Needed because a corpus title can itself contain a newline (measured: pmid 40552921, whose title
    carries a line break inside `rlbp1b -/-`), and a hand-written TSV has no escaping — the row would
    silently split into three physical lines and the reader would see a broken record. The independent
    verifier caught exactly that on the first run.
    """
    return _TSV_WS.sub(" ", str(s if s is not None else ""))


def load_registry(p: Path):
    return [json.loads(ln) for ln in p.read_text(encoding="utf-8").split("\n") if ln.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()
    out = Path(args.out)

    pre_rows = load_registry(FROZEN_REG)
    anchor_rows = load_registry(ANCHOR)
    dropin_rows = load_registry(DROPIN)
    if not (len(pre_rows) == len(anchor_rows) == len(dropin_rows)):
        print("FAIL: row count differs between the frozen registry and the twins")
        return 2

    meta = cc.load_corpus_meta(PRIMARY)
    others = []
    for p in OTHER_CORPORA:
        if p.is_file():
            others.append((str(p), cc.load_corpus_meta(p)))

    # ---------------------------------------------------------------- per-paper pre-fix state
    pre_titles = defaultdict(list)          # pmid -> list of citation titles
    rec_meta = defaultdict(lambda: {"n_records": 0, "entries": set(), "sources": Counter(),
                                    "journal": Counter(), "year": Counter()})
    ledger = []
    for row, arow, drow in zip(pre_rows, anchor_rows, dropin_rows):
        eid, ctype = row.get("entry_id", ""), row.get("cell_type", "")
        for c0, c1, c2 in zip(row.get("citations") or [], arow.get("citations") or [],
                              drow.get("citations") or []):
            pmid = str(c0.get("pmid") or "")
            m = meta.get(pmid) or {}
            ct = m.get("title") or ""
            t0 = c0.get("title") or ""
            t1 = c1.get("title_full") or ""
            t2 = c2.get("title") or ""
            pre_titles[pmid].append(t0)
            info = rec_meta[pmid]
            info["n_records"] += 1
            info["entries"].add(eid)
            info["sources"][c0.get("evidence_source") or ""] += 1
            info["journal"][(c0.get("journal") or "").strip()] += 1
            info["year"][str(c0.get("year") or "").strip()] += 1
            # precise pre-fix class: "clipped" only when the corpus title is LONGER than 120 and the
            # cited value is exactly its 120-char prefix. A 120-char title that is genuinely 120
            # characters long is NOT a defect and must not be counted as one.
            if not t0.strip():
                cls = "EMPTY"
            elif len(t0) == cc.LEGACY_TRUNCATION and len(ct) > cc.LEGACY_TRUNCATION \
                    and cc.norm_title_display(ct).startswith(cc.norm_title_display(t0)):
                # display-tolerant: the retrieval route carried the plain-text form of the title
                # while papers.jsonl carries the marked-up one, so a byte-exact prefix test files 21
                # genuinely capped records as "complete" (found by the independent verifier)
                cls = "CAPPED_120"
            elif len(ct) == cc.LEGACY_TRUNCATION and ct == t0:
                cls = "GENUINE_120"
            else:
                cls = "FULL_OK"
            ledger.append({
                "pmid": pmid, "entry_id": eid, "cell_type": ctype,
                "evidence_source": c0.get("evidence_source") or "",
                "corpus_title_len": len(ct),
                "pre_title_len": len(t0), "pre_state": cc.title_state(t0), "pre_class": cls,
                "pre_strict_match": int(cc.tables_equal(t0, ct)),
                "pre_prefix40_match": int(cc.tables_prefix_equal(t0, ct)),
                "post_title_len": len(t1),
                "post_strict_match": int(cc.tables_equal(t1, ct)),
                "post_prefix40_match": int(cc.tables_prefix_equal(t1, ct)),
                "doi_present": int(bool(m.get("doi"))),
                "pmcid_present": int(bool(m.get("pmcid"))),
            })

    papers = sorted(pre_titles)
    pre_pick = {p: max(pre_titles[p], key=len) if any(t.strip() for t in pre_titles[p]) else ""
                for p in papers}

    def rate(fn, title_of, corpus_meta, unescape=False):
        ok = 0
        misses = []
        for p in papers:
            ct = (corpus_meta.get(p) or {}).get("title") or ""
            if not ct:
                misses.append((p, "CORPUS_MISSING")); continue
            if fn(title_of(p), ct, unescape):
                ok += 1
            else:
                misses.append((p, None))
        return ok, misses

    def classify(p, cited_title, ct):
        """Why one paper failed a title caliber — a named cause per row, never a bare count.

        Priority order matters and is fixed: a wrong corpus is impossible here (every cited id was
        resolved), so the first three classes are the two structural defects of the frozen builder
        plus the display-artefact class, and only then "genuinely different".
        """
        if not ct.strip():
            return "CORPUS_MISSING"
        if not cited_title.strip():
            return "TITLE_EMPTY_CITED"
        # The cap test is display-tolerant: the retrieval route carried the plain-text form while
        # `papers.jsonl` carries the marked-up one, so a byte-exact prefix test under-counts the cap.
        if len(ct) > cc.LEGACY_TRUNCATION and len(cited_title) == cc.LEGACY_TRUNCATION \
                and cc.norm_title_display(ct).startswith(cc.norm_title_display(cited_title)):
            return "TITLE_CAPPED_120"
        if cc.norm_title_display(ct) == cc.norm_title_display(cited_title):
            return "TITLE_DISPLAY_ARTIFACT"
        if not str(p).isdigit():
            return "PREPRINT_ID"
        return "TITLE_OTHER_DIFF"

    calibers = {}
    for cname, fn in (("A_strict_full_equality", cc.tables_equal),
                      ("B_prefix40", cc.tables_prefix_equal)):
        for norm_name, unesc in (("N1_raw", False), ("N2_display_stripped", True)):
            for arm, title_of, corpus_meta in (
                    ("pre", lambda p: pre_pick[p], meta),
                    ("post", lambda p: (meta.get(p) or {}).get("title") or "", meta)):
                # NB: `unescape` is passed BY KEYWORD. `tables_prefix_equal(a, b, n=40,
                # unescape=False)` takes the third positional slot as the prefix length, so a
                # positional call would silently compare every title against a 0-character prefix
                # and report "everything with a non-empty title matches". Caught by the
                # cross-corpus column disagreeing with this one (369 vs 370) during the first run.
                ok, misses = rate(lambda a, b, u, fn=fn: fn(a, b, unescape=u), title_of,
                                  corpus_meta, unesc)
                reasons = Counter()
                rows_out = []
                for p, forced in misses:
                    r = forced or classify(p, title_of(p), (meta.get(p) or {}).get("title") or "")
                    reasons[r] += 1
                    rows_out.append({"pmid": p, "caliber": cname, "norm": norm_name, "arm": arm,
                                     "cited_title": title_of(p),
                                     "corpus_title": (meta.get(p) or {}).get("title") or "",
                                     "reason_code": r,
                                     "reason_text": REASON_TEXT.get(r, "")})
                calibers[f"{cname}|{norm_name}|{arm}"] = {
                    "caliber": cname, "normalisation": norm_name, "arm": arm,
                    "n": len(papers), "matched": ok, "rate": round(100.0 * ok / max(1, len(papers)), 2),
                    "unmatched": len(misses), "reasons": dict(reasons), "rows": rows_out,
                }

    # ---------------------------------------------------------------- cross-corpus (non-circular)
    cross = {}
    for label, cm in others:
        for cname, fn, unesc_x in (("A_strict_full_equality", cc.tables_equal, False),
                                   ("B_prefix40", cc.tables_prefix_equal, False),
                                   ("A_strict_full_equality_N2", cc.tables_equal, True),
                                   ("B_prefix40_N2", cc.tables_prefix_equal, True)):
            for arm, title_of in (("pre", lambda p: pre_pick[p]),
                                  ("post_from_primary", lambda p: (meta.get(p) or {}).get("title") or "")):
                ok = 0
                bad = []
                for p in papers:
                    ct = (cm.get(p) or {}).get("title") or ""
                    if not ct:
                        bad.append({"pmid": p, "reason_code": "CORPUS_MISSING"}); continue
                    if fn(title_of(p), ct, unescape=unesc_x):
                        ok += 1
                    else:
                        bad.append({"pmid": p, "reason_code": classify(p, title_of(p), ct)})
                cross[f"{label}|{cname}|{arm}"] = {
                    "corpus": label, "caliber": cname, "arm": arm, "n": len(papers),
                    "matched": ok, "rate": round(100.0 * ok / max(1, len(papers)), 2),
                    "unmatched": len(papers) - ok, "sample_misses": bad[:5],
                }

    # ---------------------------------------------------------------- field-agreement controls
    controls = {"journal_agree": 0, "journal_denom": 0, "year_agree": 0, "year_denom": 0,
                "pre_full_ok_strict": 0, "pre_full_ok_denom": 0,
                "pre_capped_prefix40": 0, "pre_capped_denom": 0}
    for p in papers:
        cj = rec_meta[p]["journal"]
        cy = rec_meta[p]["year"]
        cm = meta.get(p) or {}
        cj_side = max(cj, key=cj.get) if cj else ""
        if cj_side:
            controls["journal_denom"] += 1
            if cc.norm_title(cj_side) == cc.norm_title(cm.get("journal") or ""):
                controls["journal_agree"] += 1
        cy_side = max(cy, key=cy.get) if cy else ""
        if cy_side:
            controls["year_denom"] += 1
            if str(cy_side) == str(cm.get("year") or ""):
                controls["year_agree"] += 1
        t0 = pre_pick[p]
        ct = cm.get("title") or ""
        if t0.strip() and len(t0) != cc.LEGACY_TRUNCATION:
            controls["pre_full_ok_denom"] += 1
            if cc.tables_equal(t0, ct, True):
                controls["pre_full_ok_strict"] += 1
        if t0 and len(ct) > cc.LEGACY_TRUNCATION and t0 == ct[:cc.LEGACY_TRUNCATION]:
            controls["pre_capped_denom"] += 1
            if cc.tables_prefix_equal(t0, ct):
                controls["pre_capped_prefix40"] += 1

    # ---------------------------------------------------------------- outputs
    ledger_p = out / "CITATION_TITLE_LEDGER_v1.tsv"
    cols = list(ledger[0])
    with ledger_p.open("w", encoding="utf-8") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in ledger:
            fh.write("\t".join(cell(r[c]) for c in cols) + "\n")
    pre_cls = Counter(r["pre_class"] for r in ledger)

    by_paper_cols = ["pmid", "n_records", "n_entries", "cited_title_state", "cited_title_len",
                     "corpus_title_len", "corpus_title", "pre_strict_match", "pre_prefix40_match",
                     "pre_reason_code", "reason_text"]
    by_paper_p = out / "CITATION_TITLE_BY_PAPER_v1.tsv"
    with by_paper_p.open("w", encoding="utf-8") as fh:
        fh.write("\t".join(by_paper_cols) + "\n")
        for p in papers:
            t0 = pre_pick[p]
            ct = (meta.get(p) or {}).get("title") or ""
            st = cc.title_state(t0)
            if cc.tables_equal(t0, ct):
                rc = ""
            else:
                rc = classify(p, t0, ct)
            fh.write("\t".join([cell(p), str(rec_meta[p]["n_records"]),
                                str(len(rec_meta[p]["entries"])), st, str(len(t0)), str(len(ct)),
                                cell(ct), str(int(cc.tables_equal(t0, ct))),
                                str(int(cc.tables_prefix_equal(t0, ct))), cell(rc),
                                cell(REASON_TEXT.get(rc, "") if rc else "")]) + "\n")

    unmatched_p = out / "UNMATCHED_PRE_v1.tsv"
    with unmatched_p.open("w", encoding="utf-8") as fh:
        fh.write("pmid\tcaliber\tnormalisation\tcited_title\tcorpus_title\treason_code\treason_text\n")
        n_un = 0
        for k, v in calibers.items():
            if v["arm"] != "pre":
                continue
            for r in v["rows"]:
                n_un += 1
                fh.write("\t".join([cell(r["pmid"]), cell(r["caliber"]), cell(r["norm"]),
                                    cell(r["cited_title"]), cell(r["corpus_title"]),
                                    cell(r["reason_code"]), cell(r["reason_text"])]) + "\n")

    post_unmatched = out / "UNMATCHED_POSTFIX_v1.tsv"
    with post_unmatched.open("w", encoding="utf-8") as fh:
        fh.write("pmid\tcaliber\tnormalisation\tcited_title\tcorpus_title\treason_code\treason_text\n")
        n_post_un = 0
        for k, v in calibers.items():
            if v["arm"] != "post":
                continue
            for r in v["rows"]:
                n_post_un += 1
                fh.write("\t".join([cell(r["pmid"]), cell(r["caliber"]), cell(r["norm"]),
                                    cell(r["cited_title"]), cell(r["corpus_title"]),
                                    cell(r["reason_code"]), cell(r["reason_text"])]) + "\n")

    summary = {
        "card": "t_d8e7f2d4",
        "unit": "distinct cited paper (pmid) in the frozen registry",
        "n_papers": len(papers),
        "n_citation_records_in_ledger": len(ledger),
        "inputs": {
            "frozen_registry": {"path": str(FROZEN_REG),
                                "sha256": hashlib.sha256(FROZEN_REG.read_bytes()).hexdigest()},
            "anchor_twin": {"path": str(ANCHOR),
                            "sha256": hashlib.sha256(ANCHOR.read_bytes()).hexdigest()},
            "corpus_primary": {"path": str(PRIMARY),
                               "sha256": hashlib.sha256(PRIMARY.read_bytes()).hexdigest()},
            "corpus_others": [{"path": p, "sha256": hashlib.sha256(Path(p).read_bytes()).hexdigest()}
                              for p, _ in others],
        },
        "calibers": {k: {kk: vv for kk, vv in v.items() if kk != "rows"}
                     for k, v in calibers.items()},
        "cross_corpus": cross,
        "controls": controls,
        "ledger_counts": {
            "pre_class": dict(pre_cls),
            "pre_class_definition": {
                "EMPTY": "citation record had no title at all (gene-index route)",
                "CAPPED_120": "citation title is exactly the corpus title's 120-char prefix and the "
                              "corpus title is longer — the frozen builder's cap",
                "GENUINE_120": "corpus title is itself exactly 120 characters — NOT a defect",
                "FULL_OK": "citation title was already the complete title",
            },
            "post_class_note": "post-fix, `title_full`/drop-in `title` is the complete title for "
                               "every record; 32 records read as TRUNCATED_120 under the blunt "
                               "len==120 test because those papers' real titles are 120 chars long",
        },
        "unmatched_rows": {"pre": n_un, "post": n_post_un},
    }
    (out / "CITATION_TITLE_COUNTERFACTUAL_v1.json").write_text(
        json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    # ---------------------------------------------------------------- human table (markdown)
    md = []
    md.append("# CITTITLE — 反事实证明：改前 / 改后（口径并报，禁只报高的那个）\n")
    md.append(f"卡 `t_d8e7f2d4`　单位 = 冻结 registry 中**去重被引论文**（分母 {len(papers)}）；"
              f"引用记录 {len(ledger)} 条。\n")
    md.append("| 口径 | 规范化 | 改前对上 | 改前率 | 改后对上 | 改后率 | 增量 |")
    md.append("|---|---|---|---|---|---|---|")
    for cname in ("A_strict_full_equality", "B_prefix40"):
        for norm_name in ("N1_raw", "N2_display_stripped"):
            pre = calibers[f"{cname}|{norm_name}|pre"]
            post = calibers[f"{cname}|{norm_name}|post"]
            md.append(f"| {cname} | {norm_name} | {pre['matched']} | {pre['rate']}% | "
                      f"{post['matched']} | {post['rate']}% | +{post['matched'] - pre['matched']} |")
    md.append("")
    md.append("## 逐条原因（改前未对上，按口径展开）\n")
    for cname in ("A_strict_full_equality", "B_prefix40"):
        for norm_name in ("N1_raw", "N2_display_stripped"):
            v = calibers[f"{cname}|{norm_name}|pre"]
            md.append(f"- **{cname} / {norm_name}**：未对上 {v['unmatched']} 条 —— "
                      + "、".join(f"`{k}` {n}" for k, n in sorted(v["reasons"].items(),
                                                                  key=lambda kv: -kv[1])))
    md.append("")
    md.append("## 非圆形证据（关键：改后 100% 是同源回填的构造结果，不构成「两库一致」的证据）\n")
    md.append("| 交叉语料 | 口径 | 臂 | 对上/分母 | 率 |")
    md.append("|---|---|---|---|---|")
    for k, v in cross.items():
        md.append(f"| {Path(v['corpus']).parent.name} | {v['caliber']} | {v['arm']} | "
                  f"{v['matched']}/{v['n']} | {v['rate']}% |")
    md.append("")
    md.append("## 同 join 的旁证控制（若 pmid↔paper_id 接错，这里必然先塌）\n")
    md.append(f"- 期刊一致：{controls['journal_agree']}/{controls['journal_denom']}")
    md.append(f"- 年份一致：{controls['year_agree']}/{controls['year_denom']}")
    md.append(f"- 改前**本来就完整**的题名（非空、非 120）与语料严格全等："
              f"{controls['pre_full_ok_strict']}/{controls['pre_full_ok_denom']}")
    md.append(f"- 改前**被截断**的题名在 40 字前缀口径下与语料相等："
              f"{controls['pre_capped_prefix40']}/{controls['pre_capped_denom']}")
    md.append("")
    md.append("## 记录级归因（改前缺陷形态，逐条计数）\n")
    for k, v in sorted(pre_cls.items(), key=lambda kv: -kv[1]):
        md.append(f"- {k}: {v}")
    md.append("")
    md.append("## 后修未对上（{0} 行；空表 = 无行可登，不是静默丢弃）\n".format(n_post_un))
    (out / "CITATION_TITLE_COUNTERFACTUAL_v1.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"[counterfactual] papers={len(papers)} records={len(ledger)}")
    for cname in ("A_strict_full_equality", "B_prefix40"):
        for norm_name in ("N1_raw", "N2_display_stripped"):
            pre = calibers[f"{cname}|{norm_name}|pre"]
            post = calibers[f"{cname}|{norm_name}|post"]
            print(f"  {cname:<24} {norm_name:<18} pre {pre['matched']}/{pre['n']} "
                  f"({pre['rate']}%) -> post {post['matched']}/{post['n']} ({post['rate']}%)")
    print(f"[counterfactual] pre ledger classes {dict(pre_cls)}")
    print(f"[counterfactual] controls {controls}")
    print(f"[counterfactual] unmatched rows: pre={n_un} post={n_post_un}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
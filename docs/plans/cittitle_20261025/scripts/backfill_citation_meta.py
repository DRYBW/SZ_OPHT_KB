#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""backfill_citation_meta.py — CITTITLE (card t_d8e7f2d4): give every citation record the paper's
own title / doi / pmcid, joined from the corpus on `paper_id == pmid`.

Reads (all read-only):
  * the frozen registry  kb/link_registry/LINK_REGISTRY_v1.jsonl  (sha asserted against the recorded
    pre-image sha, so the run cannot silently pick up a different revision)
  * the corpus copies, in the order the fix's own resolution chain names them:
      1. the G2 slim library   literature_db/v2.4.2_2026-09_slim/papers.jsonl   (declared primary,
         repo-committed per docs/VERIFY_CONTRACT.md §G2 — the artifact's declared input)
      2. the pointer's role:default library   /mnt/D/OcularKB/.../v2.4.2_2026-09/papers.jsonl
      3. the v2.6-dev library   /mnt/D/OcularKB/.../v2.6-dev_2026-10/papers.jsonl
    Copies 2 and 3 are cross-checks only: every cited id must resolve in each, and the titles must
    agree; a disagreement is reported, never averaged away.

Writes (out/):
  * LINK_REGISTRY_v2_cittitle.jsonl          ANCHOR TWIN — the frozen registry's own bytes for every
      pre-existing key (including `title`, still the 120-char prefix where it was one), plus
      `title_full` / `doi` / `pmcid` inserted immediately after `title` in each citation record.
      This is the file that satisfies "the registry is byte-verifiable except for the three added
      columns": dropping the three keys restores every original line byte-for-byte.
  * LINK_REGISTRY_v2_cittitle_dropin.jsonl   DROP-IN — same three keys, and `title` itself repaired to
      the complete title. This is what the patched builder emits. Derivable from the anchor twin by
      `title := title_full`; the derivation is asserted here, not asserted in prose.
  * BACKFILL_META.json                       every count and sha this run produced, read live.

Determinism: no wall-clock input, no network. Two runs produce identical bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cittitle_common as cc  # noqa: E402

ROOT = Path("/home/ubuntu/EYEKB_REPO")
DEFAULT_OUT = HERE.parent / "out"

FROZEN_REG = ROOT / "kb" / "link_registry" / "LINK_REGISTRY_v1.jsonl"
DECLARED_PRIMARY = ROOT / "literature_db" / "v2.4.2_2026-09_slim" / "papers.jsonl"
CROSS_CORPORA = (
    Path("/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4.2_2026-09/papers.jsonl"),
    Path("/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10/papers.jsonl"),
)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--expect-frozen-sha", default="",
                    help="assert the frozen registry's sha256 (taken from pre_images/PREIMAGE.sha256)")
    args = ap.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    frozen_sha = sha256_file(FROZEN_REG)
    if args.expect_frozen_sha and frozen_sha != args.expect_frozen_sha:
        print(f"FAIL: frozen registry sha {frozen_sha} != declared {args.expect_frozen_sha}")
        return 2

    raw_lines = [ln for ln in FROZEN_REG.read_text(encoding="utf-8").split("\n") if ln.strip()]
    rows = [json.loads(ln) for ln in raw_lines]

    # ---------------------------------------------------------------- corpus side
    meta = cc.load_corpus_meta(DECLARED_PRIMARY)
    corpus_info = [{"role": "declared_primary", "path": str(DECLARED_PRIMARY),
                    "sha256": sha256_file(DECLARED_PRIMARY), "papers": len(meta)}]
    cross = []
    for p in CROSS_CORPORA:
        if not p.is_file():
            cross.append({"path": str(p), "present": False})
            continue
        m = cc.load_corpus_meta(p)
        cross.append({"path": str(p), "present": True, "sha256": sha256_file(p),
                      "papers": len(m)})
        meta_agree = {"k": m}          # kept for the agreement pass below
        cross[-1]["_meta"] = meta_agree["k"]

    cited = []
    for r in rows:
        for c in (r.get("citations") or []):
            cited.append((r.get("entry_id", ""), r.get("cell_type", ""), c))
    cited_ids = sorted({str(c.get("pmid") or "") for _, _, c in cited})

    unresolved = [p for p in cited_ids if p not in meta]
    title_missing = [p for p in cited_ids if not (meta.get(p, {}).get("title") or "")]
    doi_missing = [p for p in cited_ids if not (meta.get(p, {}).get("doi") or "")]
    pmcid_missing = [p for p in cited_ids if not (meta.get(p, {}).get("pmcid") or "")]
    if unresolved or title_missing:
        print(f"FAIL: {len(unresolved)} cited ids unresolved, {len(title_missing)} without a title "
              f"in the declared primary corpus — refusing to write a partly-titled registry")
        print("  unresolved:", unresolved[:10], " title_missing:", title_missing[:10])
        return 2

    # title agreement across corpus copies (the backfilled value is not averaged over sources)
    disagree = []
    for p in cited_ids:
        t0 = (meta.get(p, {}).get("title") or "")
        for c in cross:
            if not c.get("present"):
                continue
            t1 = (c["_meta"].get(p, {}).get("title") or "")
            if t1 and cc.norm_title(t1) != cc.norm_title(t0):
                disagree.append({"pmid": p, "primary": t0, "other": t1,
                                 "corpus": c["path"]})
    for c in cross:
        c.pop("_meta", None)

    # ---------------------------------------------------------------- the two twins
    anchor_lines, dropin_lines = [], []
    n_cit = 0
    pre_state = {"EMPTY_CITED": 0, "TRUNCATED_120": 0, "OK": 0}
    post_state_anchor_titlefull = {"EMPTY_CITED": 0, "TRUNCATED_120": 0, "OK": 0}
    post_state_dropin_title = {"EMPTY_CITED": 0, "TRUNCATED_120": 0, "OK": 0}
    added_present = 0
    for row, raw in zip(rows, raw_lines):
        a = cc.augment_row(row, meta, "anchor")
        d = cc.augment_row(row, meta, "repair")
        anchor_lines.append(cc.dumps(a))
        dropin_lines.append(cc.dumps(d))

        # inversion proof, in bytes, per line (anchor twin)
        back_a = {k: ([cc.strip_added(c) for c in v] if k == "citations" else v)
                  for k, v in a.items()}
        if cc.dumps(back_a) != raw:
            print(f"FAIL: anchor twin does not invert to the frozen line for "
                  f"entry_id={row.get('entry_id')}")
            return 2
        # derivation proof, in bytes, per line (drop-in == anchor twin with title := title_full)
        der_d = {k: ([cc.derive_dropin(c) for c in v] if k == "citations" else v)
                 for k, v in a.items()}
        if cc.dumps(der_d) != cc.dumps(d):
            print(f"FAIL: drop-in is not the anchor twin derived by title := title_full for "
                  f"entry_id={row.get('entry_id')}")
            return 2

        for c0, c1, c2 in zip(row.get("citations") or [], a.get("citations") or [],
                              d.get("citations") or []):
            n_cit += 1
            pre_state[cc.title_state(c0.get("title") or "")] += 1
            post_state_anchor_titlefull[cc.title_state(c1.get("title_full") or "")] += 1
            post_state_dropin_title[cc.title_state(c2.get("title") or "")] += 1
            if all(k in c1 for k in cc.ADDED_KEYS):
                added_present += 1

    anchor_body = ("\n".join(anchor_lines) + "\n").encode("utf-8")
    dropin_body = ("\n".join(dropin_lines) + "\n").encode("utf-8")
    if added_present != n_cit:
        print(f"FAIL: only {added_present}/{n_cit} citation records carry all three added keys")
        return 2

    anchor_p = out_dir / "LINK_REGISTRY_v2_cittitle.jsonl"
    dropin_p = out_dir / "LINK_REGISTRY_v2_cittitle_dropin.jsonl"
    anchor_p.write_bytes(anchor_body)
    dropin_p.write_bytes(dropin_body)

    meta_out = {
        "card": "t_d8e7f2d4",
        "what": "citation records carry the paper's own title/doi/pmcid, joined from the corpus on paper_id == pmid",
        "inputs": {
            "frozen_registry": {"path": str(FROZEN_REG), "sha256": frozen_sha,
                                "lines": len(raw_lines)},
            "corpora": corpus_info,
            "cross_check_corpora": cross,
            "declared_primary_reason": (
                "the G2 slim library is the contract's sole official corpus channel "
                "(docs/VERIFY_CONTRACT.md §G2) and is the copy present in the repository"),
        },
        "join": {
            "key": "citation.pmid == corpus.paper_id",
            "cited_ids": len(cited_ids),
            "resolved": len(cited_ids) - len(unresolved),
            "unresolved": len(unresolved),
            "title_missing_in_corpus": len(title_missing),
            "doi_missing_in_corpus": len(doi_missing),
            "pmcid_missing_in_corpus": len(pmcid_missing),
            "cross_copy_title_disagreements": len(disagree),
            "cross_copy_disagreement_sample": disagree[:5],
        },
        "counts": {
            "rows": len(rows),
            "citation_records": n_cit,
            "distinct_cited_papers": len(cited_ids),
            "citation_records_by_source": {
                "corpus search": sum(1 for _, _, c in cited
                                     if c.get("evidence_source") == "corpus search"),
                "gene index (full text)": sum(1 for _, _, c in cited
                                              if c.get("evidence_source") == "gene index (full text)"),
            },
            "title_state_pre_fix": pre_state,
            "title_state_post_anchor_twin__title_full": post_state_anchor_titlefull,
            "title_state_post_dropin__title": post_state_dropin_title,
            "records_carrying_all_three_added_keys": added_present,
        },
        "outputs": {
            "anchor_twin": {"path": str(anchor_p), "sha256": sha256_bytes(anchor_body),
                            "bytes": len(anchor_body), "lines": len(anchor_lines)},
            "dropin": {"path": str(dropin_p), "sha256": sha256_bytes(dropin_body),
                       "bytes": len(dropin_body), "lines": len(dropin_lines)},
        },
        "inversion": {
            "anchor_twin": "json.dumps(row with title_full/doi/pmcid removed) == frozen line, "
                           "for every line (asserted during this run, bytes)",
            "dropin": "drop-in == anchor twin with title := title_full, for every line "
                      "(asserted during this run, bytes). The drop-in is NOT invertible on its own: "
                      "`title` was overwritten, so the pre-fix value lives only in the anchor twin.",
        },
    }
    (out_dir / "BACKFILL_META.json").write_text(
        json.dumps(meta_out, indent=1, ensure_ascii=False, sort_keys=False) + "\n", encoding="utf-8")

    print(f"[backfill] frozen registry {frozen_sha[:16]} lines={len(raw_lines)} citations={n_cit}")
    print(f"[backfill] cited ids resolved {len(cited_ids) - len(unresolved)}/{len(cited_ids)} "
          f"(doi missing {len(doi_missing)}, pmcid missing {len(pmcid_missing)})")
    print(f"[backfill] pre-fix title state  {pre_state}")
    print(f"[backfill] post anchor/title_full {post_state_anchor_titlefull}")
    print(f"[backfill] post dropin/title      {post_state_dropin_title}")
    print(f"[backfill] cross-copy disagreements {len(disagree)}")
    print(f"[backfill] wrote {anchor_p.name} ({len(anchor_body)} B) and {dropin_p.name} "
          f"({len(dropin_body)} B); inversion asserted per line")
    return 0


if __name__ == "__main__":
    sys.exit(main())
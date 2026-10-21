#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step G1 — every number the report quotes, extracted from the artefacts in one pass.

The report is not allowed to carry a number that cannot be recomputed from a file on disk, so the
numbers are produced here (from the dumps and tables this card wrote) and the report cites this file.
Each row is (name, value, source artefact, how it was obtained).

Usage: <py> g1_numbers.py --out out/REPORT_NUMBERS.tsv
"""
import argparse
import hashlib
import json
import os
import pathlib
import subprocess

PLAN = pathlib.Path(__file__).resolve().parents[1]
REPO = PLAN.parents[2]
OUT = PLAN / "out"
# The three dumps are ~1.4-2.5 MB each and the base-commit tree they were taken from is a 220 MB
# copy of the repository, so they live in the declared local evidence root rather than in the
# commit. Override with EYEKB_SS_BIG or --big when reproducing somewhere else.
BIG = pathlib.Path(os.environ.get("EYEKB_SS_BIG",
                                  "/mnt/D/EyeKB/plans/shipped_surface_20261022/out"))
BASE_COMMIT = "954aeae3656541a6af285452c17c613ab539d5de"
rows = []


def add(name, value, source, how):
    rows.append((name, str(value), source, how))


def load(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


def sha256_of(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def git_show(rel):
    """The committed bytes of `rel` at BASE_COMMIT (the pre-change state, read from git, not from a
    copy on disk)."""
    return subprocess.run(["git", "-C", str(REPO), "show", f"{BASE_COMMIT}:{rel}"],
                          check=True, capture_output=True).stdout.decode("utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    pre = load(BIG / "DUMP_PRE_HEAD_v2.json")
    post2 = load(BIG / "DUMP_POST_WORKTREE_v2.json")
    post3 = load(BIG / "DUMP_POST_WORKTREE_v3.json")
    hist = {t: load(f"/tmp/ss_verify/dump_{t}.json") for t in ("a400315", "c4d04d9")}
    rec_head = json.loads(git_show("tests/fixtures/tool_panel_baseline.json"))
    rec_new = load(REPO / "tests" / "fixtures" / "tool_panel_baseline.json")

    # --- defect 1: the panel ---------------------------------------------------------------
    add("panel.calls", sum(1 for k in pre if k.startswith("panel::")),
        "out/DUMP_PRE_HEAD_v2.json", "count of panel:: keys")
    refused = [k for k in pre if k.startswith("panel::") and pre[k]["is_error"]]
    add("panel.refused_at_HEAD", len(refused), "out/DUMP_PRE_HEAD_v2.json", "is_error=True")
    moved_ans = [k for k in pre if k.startswith("panel::") and not pre[k]["is_error"]
                 and rec_head["calls"].get(k.split("panel::", 1)[1]) != pre[k]["md5"]]
    add("panel.answered_and_moved", len(moved_ans), "out/DUMP_PRE_HEAD_v2.json + HEAD fixture",
        "digest differs and is_error=False")
    add("panel.recorded.legacy_panel", rec_head["legacy_panel"], "HEAD fixture", "field")
    add("panel.recorded.full_panel", rec_head["full_panel"], "HEAD fixture", "field")
    add("panel.new.legacy_panel", rec_new["legacy_panel"], "tests/fixtures/tool_panel_baseline.json",
        "field")
    add("panel.new.full_panel", rec_new["full_panel"], "tests/fixtures/tool_panel_baseline.json",
        "field")
    add("panel.new.refused_calls", len(rec_new.get("refused_calls") or []),
        "tests/fixtures/tool_panel_baseline.json", "len(refused_calls)")
    add("panel.new.n_calls", rec_new["n_calls"], "tests/fixtures/tool_panel_baseline.json", "field")
    for k in refused:
        add("panel.refused_key", k.split("panel::", 1)[1], "out/DUMP_PRE_HEAD_v2.json",
            "is_error=True at HEAD")
    # the four refusals are refused at every commit measured
    for tag, d in hist.items():
        same = sum(1 for k in refused if k in d and d[k]["is_error"])
        add(f"panel.refused_at_{tag}", f"{same}/{len(refused)}", f"/tmp/ss_verify/dump_{tag}.json",
            "is_error on the same keys")

    # --- defect 1b: the one answered move --------------------------------------------------
    k = 'panel::explain_annotation:{"cell_type": "Mueller cell"}'
    for tag, d in list(hist.items()) + [("HEAD", pre)]:
        add(f"mueller.md5_at_{tag}", d[k]["md5"], f"dump at {tag}", "md5 field")
    add("mueller.md5_recorded", rec_head["calls"]['explain_annotation:{"cell_type": "Mueller cell"}'],
        "HEAD fixture", "calls[key]")
    diffs = []

    def walk(a_, b_, path=""):
        if isinstance(a_, dict) and isinstance(b_, dict):
            for kk in sorted(set(a_) | set(b_)):
                walk(a_.get(kk, "<absent>"), b_.get(kk, "<absent>"), f"{path}.{kk}")
        elif isinstance(a_, list) and isinstance(b_, list):
            for i in range(max(len(a_), len(b_))):
                walk(a_[i] if i < len(a_) else "<absent>", b_[i] if i < len(b_) else "<absent>",
                     f"{path}[{i}]")
        elif a_ != b_:
            diffs.append((path, a_, b_))

    walk(hist["a400315"][k]["payload"], pre[k]["payload"])
    add("mueller.field_diffs_a400315_to_HEAD", len(diffs),
        "dumps at a400315 and HEAD", "recursive leaf diff of the parsed payload")
    add("mueller.field_diff_paths", ";".join(sorted({p.rsplit("[", 1)[0] for p, _, _ in diffs})),
        "same", "distinct field paths of the diffs")

    # --- defect 1c: the version sweep ------------------------------------------------------
    patched, vers = {}, set()
    import re
    for kk in (kk for kk in pre if kk.startswith("panel::")):
        for v in re.findall(r"pydantic\.dev/(\d+\.\d+)/", pre[kk]["text"]):
            vers.add(v)
    add("panel.refusal_text_version", sorted(vers), "out/DUMP_PRE_HEAD_v2.json",
        "regex pydantic.dev/<ver>/ in the refusal texts")

    # --- defect 2: the stage surface -------------------------------------------------------
    for tag, d in (("pre", pre), ("post_v3", post3)):
        lits = {kk: v for kk, v in d.items() if kk.startswith("literal::")}
        add(f"stage.{tag}.rows", len(lits), f"dump {tag} ({BIG})", "count of literal:: keys")
        with_block = [kk for kk, v in lits.items()
                      if (v.get("payload") or {}).get("stage_literal")]
        add(f"stage.{tag}.rows_with_stage_literal_block", len(with_block), f"dump {tag} ({BIG})",
            "payload.stage_literal present")
    changed = [kk for kk in pre if kk.startswith("literal::") and kk in post3
               and pre[kk]["md5"] != post3[kk]["md5"]]
    add("stage.changed_pre_to_post", f"{len(changed)}/42", "dumps pre and post_v3",
        "md5 differs per (species,tissue,literal)")
    for pair in (("human", "retina"), ("human", "RPE"), ("mouse", "retina")):
        sp, ti = pair
        kid = f"literal::{sp}::{ti}::'organoid'"
        for tag, d in (("pre", pre), ("post", post3)):
            v = d[kid]
            p = v.get("payload") or {}
            add(f"stage.organoid.{sp}.{ti}.{tag}",
                f"entry={p.get('entry_id') or p.get('mode') or p.get('error', '')[:40]} "
                f"organism_stage={p.get('organism_stage')} "
                f"flag={(p.get('stage_literal') or {}).get('flag')} bytes={v['bytes']}",
                f"dump {tag} ({BIG})", "payload fields for the organoid literal")

    # --- the marker file that lives only on the data mount ---------------------------------
    mv8 = pathlib.Path("/mnt/D/EyeKB/kb/markers/markers_v8_dev_retina.json")
    add("markers_v8.sha256", sha256_of(mv8) if mv8.is_file() else "absent", str(mv8),
        "sha256sum")
    add("markers_v8.in_repo", (REPO / "kb" / "markers" / "markers_v8_dev_retina.json").is_file(),
        "kb/markers/", "is_file()")

    # --- file identity of what this commit ships -------------------------------------------
    for rel in ("mcp_server/eyekb_core.py", "mcp_server/server.py", "README.md",
                "tests/probe_tool_panel_identity.py", "tests/fixtures/tool_panel_baseline.json",
                "docs/W3_PIPELINE_REGISTRY.tsv", "docs/W3_MANIFEST.sha256"):
        p = REPO / rel
        add(f"file.sha256.{rel}", f"{sha256_of(p)} bytes={p.stat().st_size}", rel, "sha256sum")
    for rel in ("tests/probe_tool_panel_identity.py", "tests/fixtures/tool_panel_baseline.json",
                "mcp_server/eyekb_core.py", "mcp_server/server.py", "README.md"):
        blob = subprocess.run(["git", "-C", str(REPO), "show", f"{BASE_COMMIT}:{rel}"],
                              check=True, capture_output=True).stdout
        add(f"file.sha256_HEAD.{rel}", f"{hashlib.sha256(blob).hexdigest()} bytes={len(blob)}",
            f"git show {BASE_COMMIT[:7]}:{rel}", "sha256 of the committed blob")

    dest = pathlib.Path(a.out)
    hdr = "name\tvalue\tsource\thow"
    dest.write_text(hdr + "\n" + "\n".join("\t".join(r) for r in rows) + "\n", encoding="utf-8")
    print(f"{dest}  rows={len(rows)}")
    for r in rows:
        print(f"  {r[0]:<46} {r[1][:88]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
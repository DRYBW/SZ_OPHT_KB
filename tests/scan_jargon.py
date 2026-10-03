#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_jargon.py — EyeKB internal-jargon scanner gate
===================================================
Origin: ARCH-GOV t_9b244bd7 (2026-09-30), turning the one-off manual
"final jargon sweep" of 2026-09-29/30 into a re-runnable script. The term list
and exemption list = jargon_glossary.json in this directory (the single source
of truth — to change terms, change the JSON, not this script).

Scanned: repo Markdown (README.md + all .md under docs/).
Default scope (--scope outward): applies exempt_patterns from the JSON — historical
originals / internal record layers (docs/plans, docs/wiki, docs/recon, legacy backups,
desensitization reports, sync notes) are not retroactively enforced; outward-facing
live docs get no exemption.
With --scope all, only the glossary and this script itself are exempt (full audit).

Usage:
    python tests/scan_jargon.py                 # run from repo root or anywhere; locates the repo root automatically
    python tests/scan_jargon.py --root /path/to/repo --json out.json
    python tests/scan_jargon.py --scope all
    python tests/scan_jargon.py --fail-on-hit   # exit 1 on any hit (hookable into CI / sync gates)

Exit codes: 0 = completed (regardless of hits, unless --fail-on-hit and hits>0 → 1); 2 = argument/file error.
"""
import argparse
import json
import os
import sys


def load_glossary(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def is_exempt(relpath: str, patterns) -> bool:
    rp = relpath.replace(os.sep, "/")
    return any(p in rp for p in patterns)


def iter_markdown(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "node_modules")]
        for fn in filenames:
            if fn.lower().endswith((".md", ".markdown")):
                yield os.path.join(dirpath, fn)


def main():
    ap = argparse.ArgumentParser(description="EyeKB internal-jargon scanner gate")
    default_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--root", default=default_root, help="repository root (default = the repo this script lives in)")
    ap.add_argument("--scope", choices=["outward", "all"], default="outward",
                    help="outward=exempt historical originals (default); all=scan the whole repo (only the glossary and this script are exempt)")
    ap.add_argument("--json", dest="json_out", default=None, help="path for the machine-readable result")
    ap.add_argument("--fail-on-hit", action="store_true", help="exit code 1 when hits>0")
    ap.add_argument("--context", type=int, default=0, help="context length printed per hit (chars, 0=no context)")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"ERROR: root does not exist: {root}", file=sys.stderr)
        return 2
    glossary_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jargon_glossary.json")
    try:
        gl = load_glossary(glossary_path)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: failed to read the glossary {glossary_path}: {exc}", file=sys.stderr)
        return 2

    terms = [(t["term"], t.get("replacement", ""), t.get("category", "")) for t in gl.get("terms", [])]
    self_rel = os.path.relpath(os.path.abspath(__file__), root).replace(os.sep, "/")
    gloss_rel = os.path.relpath(glossary_path, root).replace(os.sep, "/")

    results = []
    total = 0
    files_scanned = 0
    files_hit = 0
    for path in sorted(iter_markdown(root)):
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        if rel in (self_rel, gloss_rel):
            continue
        if args.scope == "outward" and is_exempt(rel, gl.get("exempt_patterns", [])):
            continue
        if args.scope == "all" and is_exempt(rel, [self_rel, gloss_rel]):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as exc:
            print(f"WARN: read failed {rel}: {exc}", file=sys.stderr)
            continue
        files_scanned += 1
        hits = []
        for term, rep, cat in terms:
            n = text.count(term)
            if n:
                idx = text.find(term)
                snippet = ""
                if args.context:
                    snippet = text[max(0, idx - args.context): idx + len(term) + args.context].replace("\n", " ")
                hits.append({"term": term, "count": n, "replacement": rep, "category": cat, "snippet": snippet})
        if hits:
            files_hit += 1
            total += sum(h["count"] for h in hits)
            results.append({"file": rel, "hits": sorted(hits, key=lambda h: -h["count"])})

    print(f"# EyeKB jargon scan  scope={args.scope}  root={root}")
    print(f"# glossary {len(terms)} terms | scanned {files_scanned} Markdown files")
    if results:
        for r in results:
            per = sum(h["count"] for h in r["hits"])
            terms_str = ", ".join(f"{h['term']}x{h['count']}" for h in r["hits"])
            print(f"  {r['file']}  residue {per}  ({terms_str})")
    print(f"total residue: {total} (files hit: {files_hit})")

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump({"scope": args.scope, "glossary_terms": len(terms),
                       "files_scanned": files_scanned, "files_hit": files_hit,
                       "total_hits": total, "results": results}, fh, ensure_ascii=False, indent=1)
        print(f"machine-readable result: {args.json_out}")

    if args.fail_on_hit and total > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

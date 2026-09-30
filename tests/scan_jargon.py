#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_jargon.py — EyeKB 内部工作词（黑话）扫描门
================================================
来源：ARCH-GOV t_9b244bd7（2026-09-30），把 2026-09-29/30 一次性人工
"黑话终扫"固化为可复跑脚本。词表与豁免清单 = 同目录 jargon_glossary.json
（唯一权威源，改词表改 JSON，不改本脚本）。

扫描对象：仓内 Markdown（README.md + docs/ 全部 .md）。
默认口径（--scope outward）：应用 JSON 中 exempt_patterns —— 历史原件/内部
记录层（docs/plans、docs/wiki、docs/recon、legacy 备份、脱敏报告、同步注记）
不追溯；对外活文档不豁免。
--scope all 时仅豁免词表与本脚本自身（全量审计用）。

用法：
    python tests/scan_jargon.py                 # 从仓根或任意位置跑，自动定位仓根
    python tests/scan_jargon.py --root /path/to/repo --json out.json
    python tests/scan_jargon.py --scope all
    python tests/scan_jargon.py --fail-on-hit   # 有命中则 exit 1（可挂 CI/同步门）

退出码：0 = 完成（无论是否有命中，除非 --fail-on-hit 且命中>0 → 1）；2 = 参数/文件错误。
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
    ap = argparse.ArgumentParser(description="EyeKB 内部工作词扫描门")
    default_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--root", default=default_root, help="仓库根目录（默认=脚本所在仓）")
    ap.add_argument("--scope", choices=["outward", "all"], default="outward",
                    help="outward=豁免历史原件（默认）；all=全仓扫描（仅豁免词表与本脚本）")
    ap.add_argument("--json", dest="json_out", default=None, help="机读结果输出路径")
    ap.add_argument("--fail-on-hit", action="store_true", help="命中>0 时退出码 1")
    ap.add_argument("--context", type=int, default=0, help="每命中打印上下文长度（字符，0=不打印）")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"ERROR: root 不存在: {root}", file=sys.stderr)
        return 2
    glossary_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jargon_glossary.json")
    try:
        gl = load_glossary(glossary_path)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: 词表读取失败 {glossary_path}: {exc}", file=sys.stderr)
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
            print(f"WARN: 读取失败 {rel}: {exc}", file=sys.stderr)
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

    print(f"# EyeKB 黑话扫描  scope={args.scope}  root={root}")
    print(f"# 词表 {len(terms)} 词 | 扫描 {files_scanned} 个 Markdown 文件")
    if results:
        for r in results:
            per = sum(h["count"] for h in r["hits"])
            terms_str = ", ".join(f"{h['term']}x{h['count']}" for h in r["hits"])
            print(f"  {r['file']}  残留 {per}  ({terms_str})")
    print(f"残留合计: {total} （命中文件 {files_hit} 个）")

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump({"scope": args.scope, "glossary_terms": len(terms),
                       "files_scanned": files_scanned, "files_hit": files_hit,
                       "total_hits": total, "results": results}, fh, ensure_ascii=False, indent=1)
        print(f"机读结果: {args.json_out}")

    if args.fail_on_hit and total > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

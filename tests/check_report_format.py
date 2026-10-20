#!/usr/bin/env python3
"""Report format checker for EyeKB deliverables.

Enforces the delivery format standard:
  - only #, ##, ### heading levels
  - no unordered lists (-, *, +) and no ordered lists (1. 2. 3.)
  - paragraphs separated by exactly one blank line
  - no leading indentation on body text or headings
  - every ## section carries at least one bolded key figure or claim
Fenced code blocks and markdown tables are exempt from the no-list and
no-indent rules, and are allowed to hold consecutive lines.

Usage: python3 check_report_format.py <report.md> [more.md ...]
Exit 0 = PASS, 1 = FAIL. Prints one line per rule with counts.
"""
import re
import sys

LIST_UNORDERED = re.compile(r"^\s*[-*+]\s+\S")
LIST_ORDERED = re.compile(r"^\s*\d+[.)]\s+\S")
HEADING = re.compile(r"^(#{1,6})\s+\S")
TABLE = re.compile(r"^\s*\|")


def check(path):
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")

    in_fence = False
    h_max = 0
    lists = []
    indents = []
    tight = []
    sections = []  # (heading line no, has_bold)
    for i, raw in enumerate(lines, 1):
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped.startswith("#"):
            m = HEADING.match(raw)
            if m:
                lvl = len(m.group(1))
                h_max = max(h_max, lvl)
                if lvl == 2:
                    sections.append([i, False])
            if raw[: len(raw) - len(raw.lstrip(" \t"))]:
                indents.append(i)
            continue
        if LIST_UNORDERED.match(raw) or LIST_ORDERED.match(raw):
            lists.append(i)
            continue
        if not stripped:
            continue
        if raw[: len(raw) - len(raw.lstrip(" \t"))] and not TABLE.match(raw):
            indents.append(i)
        if "**" in raw and sections:
            sections[-1][1] = True

    last = None
    for i, raw in enumerate(lines, 1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#") or TABLE.match(raw):
            last = "skip"
            continue
        if stripped.startswith("```"):
            last = "skip"
            continue
        if last == "text":
            tight.append(i)
        last = "text"

    # Appendix-style sections are pure tables; bold figures are not required there.
    def is_appendix(lineno):
        title = lines[lineno - 1].lstrip("#").strip()
        low = title.casefold()
        return ("附表" in title or "附录" in title or "数据表" in title
                or "appendix" in low)

    bolds_missing = [n for n, ok in sections if not ok and not is_appendix(n)]
    fails = []
    if h_max > 3:
        fails.append("heading level exceeds ###")
    if lists:
        fails.append("list lines: %d (first %s)" % (len(lists), lists[:5]))
    if indents:
        fails.append("indented lines: %d (first %s)" % (len(indents), indents[:5]))
    if tight:
        fails.append("missing blank line before: %d (first %s)" % (len(tight), tight[:5]))
    if bolds_missing:
        fails.append("## sections without bold figure: %d (first %s)" % (len(bolds_missing), bolds_missing[:5]))

    status = "PASS" if not fails else "FAIL"
    print("%s %s" % (status, path))
    print("  lines=%d  sections=%d  max_heading=%d  lists=%d  indents=%d  tight_paras=%d  sections_without_bold=%d"
          % (len(lines), len(sections), h_max, len(lists), len(indents), len(tight), len(bolds_missing)))
    for f in fails:
        print("  - " + f)
    return not fails


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: check_report_format.py <report.md> [...]")
        sys.exit(1)
    ok = all(check(p) for p in sys.argv[1:])
    sys.exit(0 if ok else 1)

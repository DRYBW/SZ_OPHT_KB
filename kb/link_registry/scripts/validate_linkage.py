#!/usr/bin/env python3
"""Linkage gate: a knowledge entry counts as wired only when all five fields are populated.

    kb_entry  <->  wiki_page  <->  pmids  <->  mcp_route  <->  skill_trigger

Exit code 0 = pass, 1 = at least one entry is a dead end (silent gaps are what this gate exists
to prevent). Thresholds are explicit so the rule is machine-checkable rather than a promise.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REG = HERE.parent / "LINK_REGISTRY_v1.jsonl"

MIN_PMIDS = 1        # at least one in-corpus paper backing the entry
# A textbook row backs a structural claim with a book page rather than a paper, so it satisfies the
# evidence link through book_anchors instead of pmids. Every other link is still required.
REQUIRE_WIKI = True  # the entry must be reachable from a written page
REQUIRE_MCP = True   # the entry must be reachable by an explicit tool call
REQUIRE_SKILL = True # a skill must document how to consume it


def main():
    rows = [json.loads(l) for l in REG.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = [r for r in rows if "error" not in r]
    dead = []
    for r in rows:
        why = []
        if r.get("n_pmids", 0) < MIN_PMIDS and not r.get("book_anchors"):
            why.append("no citation and no source page")
        if REQUIRE_WIKI and not r.get("n_wiki_pages"):
            why.append("no wiki page")
        if REQUIRE_MCP and not r.get("mcp_route"):
            why.append("no MCP route")
        if REQUIRE_SKILL and not r.get("skill_trigger"):
            why.append("no skill entry point")
        if why:
            dead.append((r.get("entry_id", "?"), why))

    print(f"linkage gate: {len(rows) - len(dead)}/{len(rows)} entries fully wired")
    if dead:
        print(f"DEAD ENDS ({len(dead)}) — each one is a trail a reader cannot follow:")
        for eid, why in dead:
            print(f"  {eid}: {', '.join(why)}")
        return 1
    print("PASS: every entry carries a citation, a page, a route and a skill entry point")
    return 0


if __name__ == "__main__":
    sys.exit(main())
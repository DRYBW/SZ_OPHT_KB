#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""[KB9B t_3bbc769f] Consumer-side narrow guard: KB9 (ocular-surface increment) evidence entries
must not occupy the FRONT ranks of the annotation candidate slice. PI ruling 2026-10-08 =
T7_TRIAGE_20261006.md option B (keep k9 in service, fix the consumption surface only).

Mechanism = demote (stable partition): ranking/unranked entries whose marker-file basename is a
k9 library file are moved to the tail of the list BEFORE the existing [:3] slice at each of the
5 consumer sites. The MCP server-side ranking body itself, the raw kb_marker response stored in
the report json, and gene_to_celltypes are untouched (zero server diff — this module is imported
by pipeline consumers only).

Fallback switch (single env line, repo default-ON convention like EYEKB_ACT_K9 / CN-REWRITE CH-4):
  env EYEKB_KB9_CONSUME_GUARD in {0,false,off,no} (casefold) = OFF -> demote_kb9 returns the input
  list OBJECT unchanged (byte-identical to pre-fix production; proven by the OFF battery).
  unset / any other value = ON.

Mechanism literals grepped 2026-10-08 from the code under test (BRIEF gate: no preset literals):
- discriminator field: mcp_server/eyekb_core.py:423/426/488 — owner[ct] = str(path), so every
  ranking entry carries library = absolute path of its marker file; verified live on production
  server response (plans/kb9_consume_fix_20261008/out/PROBE_STRUCTURE.json: the inflammation-panel
  rank[1] Conj_epithelium_suprabasal carries library basename
  markers_k9_ocs_increment.json);
- k9 marker file: MARKER_LIBS["k9_ocs"] = kb/markers/markers_k9_ocs_increment.json
  (mcp_server/eyekb_core.py:224) — basename compare keeps the guard robust across repo path
  relocations (/home/ubuntu/EYEKB_REPO vs /mnt/D mirrors);
- slice sites: [:3] at pipeline/run_pipeline.py:164-165; pipeline/stage_b_evidence.py:231-232,
  :323 (decisions_template top_candidates), :380-381 (report-md candidate display);
  pipeline/llm_assist.py:33/42 (LLM evidence brief marker_candidates).
"""
import os

# k9-class marker library file basenames (grep source above; extend here if a future k9 increment
# file joins K9_DEFAULT_LIBS — the guard is intentionally data-file-identity based, not name-list)
K9_MARKER_BASENAMES = frozenset({"markers_k9_ocs_increment.json"})


def guard_enabled():
    """env EYEKB_KB9_CONSUME_GUARD: unset/any other value = ON; {0,false,off,no} (casefold) = OFF revert."""
    return (os.environ.get("EYEKB_KB9_CONSUME_GUARD", "1") or "1").strip().casefold() not in (
        "0", "false", "off", "no")


def _is_kb9(entry):
    if not isinstance(entry, dict):
        return False
    lib = str(entry.get("library", "")).replace("\\", "/")
    return lib.rsplit("/", 1)[-1] in K9_MARKER_BASENAMES


def demote_kb9(entries):
    """Stable demotion of k9-class entries to the tail of a query_marker candidate list (dicts with
    cell_type/library keys). Returns the SAME input object when guard OFF, list empty, or no k9
    entry present — zero mutation of the non-k9 path (byte-identity guarantee at consumer sites)."""
    if not entries or not guard_enabled():
        return entries
    tail = [x for x in entries if _is_kb9(x)]
    if not tail:
        return entries
    head = [x for x in entries if not _is_kb9(x)]
    return head + tail

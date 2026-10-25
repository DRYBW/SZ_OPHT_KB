#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mcp_server/corpus_stats.py — bundled-corpus numbers for the service self-description.

Why this exists
    The shipped service description used to hard-code its corpus size ("bundled corpus of
    2,713 papers / 174,616 passages"), which was the v2.0_2026-09 build the service was
    launched with (see kb/literature_db/EYEKB_DB_POINTER.yaml, block v2.0_2026-09, role
    history: "served as the search_literature built-in corpus before 2026-10-01"). The
    bundled corpus has since been re-cut to v2.4.2_2026-09_slim (3,869 papers /
    242,928 passages; switch card t_b94d0999, role: default since 2026-10-01) and the
    description was never updated, so the service advertised numbers that did not belong
    to the corpus it bundles. Rather than hard-coding a third generation of stale numbers,
    the description now renders from the bundled corpus' own build record at import time;
    a frozen fallback keeps the service startable on a fresh clone, before the G2 Release
    asset (the corpus is NOT in the git tree — see docs/VERIFY_CONTRACT.md §G2).

What is read
    literature_db/v2.4.2_2026-09_slim/build_stats.json, keys n_papers / n_chunks — the
    shipped bundled corpus' own build record. Repo-relative: the module resolves the
    repository root from its own location, works from any cwd.

Machine gate
    tests/gate_mcpdesc_corpus.py (G11 in tests/run_gates.sh) re-reads the same sources and
    FAILs when the rendered description numbers, the fallback constants, the bundled
    build_stats.json and the pointer's registered v2.4.2 identity (kb/literature_db/
    EYEKB_DB_POINTER.yaml, block v2.4.2_2026-09: unique_papers / chunks) stop agreeing.
    The pointer block is repo-committed, so the fallback stays pinned to a shipped identity
    even on a fresh clone where the corpus asset itself has not been unpacked yet.

Stdlib only; read-only; no network. The only read is one small bounded file.
"""
import json
from pathlib import Path

_MODULE = Path(__file__).resolve()
MODULE_DIR = _MODULE.parent
REPO_ROOT = _MODULE.parents[1]

# The bundled corpus shipped with this repository (repo-relative; NOT in git — delivered
# via the G2 Release asset, docs/VERIFY_CONTRACT.md §G2). One exact path on purpose: a
# corpus re-cut renames the directory, this module stops finding the build record, the
# fallback takes over and the G11 gate flags the tree, so the change has to re-point this
# constant in the same wave as the corpus re-cut instead of silently advertising the old
# corpus under a new name.
BUILD_STATS_REL = "literature_db/v2.4.2_2026-09_slim/build_stats.json"
BUILD_STATS_PATH = REPO_ROOT / BUILD_STATS_REL

# Frozen on 2026-10-25 from the shipped bundled corpus build record
# (literature_db/v2.4.2_2026-09_slim/build_stats.json, keys n_papers / n_chunks; the same
# values are registered in kb/literature_db/EYEKB_DB_POINTER.yaml under v2.4.2_2026-09:
# unique_papers 3869 / chunks 242928). Used only when BUILD_STATS_PATH cannot be read
# (fresh clone, G2 asset not yet unpacked) so the description always states the true
# identity of the bundled corpus. The G11 gate pins these constants to the pointer block;
# a digit sabotaged in either direction of the pair FAILs the gate.
FALLBACK_PAPERS = 3869
FALLBACK_CHUNKS = 242928


def read_bundled_stats():
    """(papers, chunks, error) from the bundled corpus' own build record.

    Returns (None, None, reason) when the record is absent (fresh clone, G2 asset not yet
    unpacked) or malformed; never raises.
    """
    try:
        data = json.loads(BUILD_STATS_PATH.read_text(encoding="utf-8"))
        papers = int(data["n_papers"])
        chunks = int(data["n_chunks"])
        if papers <= 0 or chunks <= 0:
            raise ValueError(f"non-positive counts: n_papers={papers}, n_chunks={chunks}")
        return papers, chunks, ""
    except Exception as exc:  # corpus absent or malformed build record
        return None, None, f"{BUILD_STATS_REL}: {exc}"


def corpus_stats():
    """(papers, chunks, source) — the numbers the service description renders.

    source names where the numbers came from (live or fallback) with the file and the
    keys; the fallback form appends the reason the live read could not be used.
    """
    papers, chunks, err = read_bundled_stats()
    if papers is not None:
        return papers, chunks, f"live:{BUILD_STATS_REL}#n_papers,n_chunks"
    reason = err or "unknown reason"
    return (FALLBACK_PAPERS, FALLBACK_CHUNKS,
            f"fallback:{BUILD_STATS_REL}#n_papers,n_chunks ({reason})")


def corpus_line():
    """The description's corpus clause fragment, e.g. "3,869 papers / 242,928 passages"."""
    papers, chunks, _ = corpus_stats()
    return f"{papers:,} papers / {chunks:,} passages"


BUNDLED_CORPUS_LINE = corpus_line()

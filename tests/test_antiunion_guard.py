#!/usr/bin/env python3
"""Unit tests for the anti-union (composite entry) guard in mcp_server/eyekb_core.py.

Covers: gate default state, composite detection (strict full-set superset only), that subsets
survive, that single-gene entries are never composites, and that a composite-free panel is
returned untouched (no friendly fire). No data, no network.

Run: python3 tests/test_antiunion_guard.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "mcp_server"))

import eyekb_core as core  # noqa: E402


def _rank(*pairs):
    return [{"cell_type": ct, "n_shared": n} for ct, n in pairs]


def test_gate_default_off():
    os.environ.pop("EYEKB_KB_ANTIUNION", None)
    assert core._antiunion_enabled() is False, "unset must be OFF (registered default off)"
    for v in ("0", "false", "off", "no", ""):
        os.environ["EYEKB_KB_ANTIUNION"] = v
        assert core._antiunion_enabled() is False, f"{v!r} must be OFF"
    for v in ("1", "true", "ON", "yes"):
        os.environ["EYEKB_KB_ANTIUNION"] = v
        assert core._antiunion_enabled() is True, f"{v!r} must be ON"
    os.environ.pop("EYEKB_KB_ANTIUNION", None)


def test_union_entry_demoted_subsets_kept():
    markers = {"pr": ["RHO", "PDE6A", "ARR3", "GNAT2"],
               "rod": ["RHO", "PDE6A"],
               "cone": ["ARR3", "GNAT2"],
               "mg": ["RLBP1", "GLUL"]}
    rank = _rank(("pr", 4), ("rod", 2), ("cone", 2))
    kept, demoted = core._antiunion_split(rank, markers)
    assert [r["cell_type"] for r in kept] == ["rod", "cone"], kept
    assert len(demoted) == 1 and demoted[0]["cell_type"] == "pr", demoted
    assert demoted[0]["superset_of"] == ["cone", "rod"], demoted


def test_no_composite_no_change():
    markers = {"rod": ["RHO", "PDE6A"], "cone": ["ARR3", "GNAT2"], "mg": ["RLBP1", "GLUL"]}
    rank = _rank(("rod", 2), ("cone", 2), ("mg", 1))
    kept, demoted = core._antiunion_split(rank, markers)
    assert kept == rank and demoted == [], (kept, demoted)


def test_single_gene_entries_never_composite():
    # detection needs both sets >= 2 genes, so a 1-gene subset never triggers a demotion
    markers = {"a": ["X"], "b": ["X", "Y"]}
    kept, demoted = core._antiunion_split(_rank(("b", 2), ("a", 1)), markers)
    assert [r["cell_type"] for r in kept] == ["b", "a"] and demoted == [], (kept, demoted)
    markers2 = {"a": ["X"], "b": ["Y"]}
    kept2, demoted2 = core._antiunion_split(_rank(("a", 1), ("b", 1)), markers2)
    assert kept2 == _rank(("a", 1), ("b", 1)) and demoted2 == [], (kept2, demoted2)


def test_only_present_candidates_considered():
    # 'pr' is a superset of rod/cone in the panel, but neither is in the ranking -> nothing demoted
    markers = {"pr": ["RHO", "ARR3"], "rod": ["RHO"], "cone": ["ARR3"], "mg": ["RLBP1"]}
    rank = _rank(("pr", 2), ("mg", 1))
    kept, demoted = core._antiunion_split(rank, markers)
    assert [r["cell_type"] for r in kept] == ["pr", "mg"] and demoted == [], (kept, demoted)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} anti-union guard tests passed")

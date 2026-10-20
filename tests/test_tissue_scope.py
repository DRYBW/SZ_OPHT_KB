#!/usr/bin/env python3
"""Unit tests for the TISSUE-SCOPE candidate exclusion layer (PREREG gate A5).

Covers, per pre-registration:
  1. no tissue argument      → no tissue_scope key at all (default path untouched)
  2. tissue + switch OFF     → status='disabled', candidates NOT narrowed
  3. tissue + switch ON      → foreign classes removed, legitimate ones kept
  4. tissue with no prior    → status='unavailable', candidates NOT narrowed (fail OPEN)
  5. empty-inventory tissue  → get_tissue_composition reports inventory_status='absent'
  6. cross-library aliases   → retina_interneuron::Rod etc. removed as a group with 'Rod'
  7. red line                → the crosswalk carries class names, never composition numbers

No pytest dependency: plain asserts + main() runner, same style as test_antiunion_guard.py.

Run: python3 tests/test_tissue_scope.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("EYEKB_REPO", os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "mcp_server"))

import eyekb_core as core  # noqa: E402

CORNEAL_GENES = ["KRT12", "KRT3", "KRT19", "MUC5AC", "LTF", "LYZ", "KRT15", "DCN", "LUM"]
RETINAL_GENES = ["RHO", "NRL", "NR2E3", "PDE6B", "POU4F2", "RBPMS", "GAD1", "TFAP2A"]


def tops(resp):
    return [r["cell_type"] for r in resp["celltype_ranking"]]


def base_of(ct):
    return str(ct).split("::")[-1]


def with_env(value, fn):
    """Run fn with EYEKB_TISSUE_SCOPE=value (None = unset), restoring the old value."""
    old = os.environ.get("EYEKB_TISSUE_SCOPE")
    try:
        if value is None:
            os.environ.pop("EYEKB_TISSUE_SCOPE", None)
        else:
            os.environ["EYEKB_TISSUE_SCOPE"] = value
        return fn()
    finally:
        if old is None:
            os.environ.pop("EYEKB_TISSUE_SCOPE", None)
        else:
            os.environ["EYEKB_TISSUE_SCOPE"] = old


def test_no_tissue_attaches_nothing():
    r = with_env("1", lambda: core.query_marker(genes=RETINAL_GENES))
    assert "tissue_scope" not in r, "switch ON but no tissue must leave the default surface untouched"
    assert "tissue_excluded_candidates" not in r


def test_tissue_with_switch_off_does_not_narrow():
    def go():
        full = core.query_marker(genes=CORNEAL_GENES)
        scoped = core.query_marker(genes=CORNEAL_GENES, tissue="retina")
        return full, scoped
    full, scoped = with_env(None, go)
    assert tops(full) == tops(scoped), "a tissue argument alone must never delete candidates"
    assert scoped["tissue_scope"]["status"] == "disabled"
    assert "tissue_excluded_candidates" not in scoped


def test_retina_removes_ocular_surface_identity():
    def go():
        return core.query_marker(genes=CORNEAL_GENES), core.query_marker(genes=CORNEAL_GENES, tissue="retina")
    full, scoped = with_env("1", go)
    assert "Conj_epithelium_basal" in tops(full)
    assert "Conj_epithelium_basal" not in tops(scoped)
    excluded = [c["cell_type"] for c in scoped["tissue_excluded_candidates"]]
    assert "Conj_epithelium_basal" in excluded
    assert scoped["tissue_scope"]["status"] == "applied"


def test_retina_keeps_invivo_stromal_and_immune():
    scoped = with_env("1", lambda: core.query_marker(genes=CORNEAL_GENES, tissue="retina"))
    assert "Fibroblast" in tops(scoped), (
        "Fibroblast occurs in retina sections; absence from a 10-row baseline is not evidence "
        "of absence and must not delete it")


def test_ocular_surface_removes_retinal_neurons():
    def go():
        return core.query_marker(genes=RETINAL_GENES), core.query_marker(
            genes=RETINAL_GENES, tissue="ocular_surface")
    full, scoped = with_env("1", go)
    assert any(base_of(x) == "Rod" for x in tops(full))
    assert tops(scoped) == []
    excluded = [base_of(c["cell_type"]) for c in scoped["tissue_excluded_candidates"]]
    assert "Rod" in excluded


def test_cross_library_aliases_excluded_as_group():
    scoped = with_env("1", lambda: core.query_marker(genes=RETINAL_GENES, tissue="ocular_surface"))
    excluded = [c["cell_type"] for c in scoped["tissue_excluded_candidates"]]
    assert "retina_interneuron::Rod" in excluded
    assert "retina_v6::Rod" in excluded


def test_absent_inventory_fails_open():
    def go():
        return (core.query_marker(genes=CORNEAL_GENES),
                core.query_marker(genes=CORNEAL_GENES, tissue="choroid"))
    full, scoped = with_env("1", go)
    assert tops(full) == tops(scoped), "no prior → no narrowing"
    assert scoped["tissue_scope"]["status"] == "unavailable"
    assert scoped["tissue_scope"]["inventory_status"] == "absent"


def test_unknown_tissue_fails_open():
    scoped = with_env("1", lambda: core.query_marker(genes=CORNEAL_GENES, tissue="no_such_tissue"))
    assert scoped["tissue_scope"]["status"] == "unavailable"
    assert scoped["tissue_scope"]["reason"] == "tissue_not_in_crosswalk"


def test_composition_reports_absent_inventory():
    for t in ("choroid", "iris", "lens", "sclera", "conjunctiva"):
        r = core.get_tissue_composition("human", t)
        assert r["inventory_status"] == "absent", t
        assert "not been built" in r["inventory_note"], t


def test_composition_reports_available_inventory():
    r = core.get_tissue_composition("human", "retina")
    assert r["inventory_status"] == "available"
    cw = r["tissue_class_crosswalk"]
    assert "Rod" in cw["kb_classes"]
    assert "class names only" in cw["note"]


def test_crosswalk_declares_no_composition_numbers():
    """Red line: the crosswalk must carry class names, never composition quantities.

    Precise check (prose is allowed to *mention* percentages; numbers are not allowed):
      * no key anywhere named like pct/percent/fraction/median/iqr/weight
      * every entry under classes[] / excluded_classes[] is a plain string
    """
    p = os.path.join(REPO, "kb", "baselines", "_tissue_class_crosswalk_v1.json")
    d = json.load(open(p))
    bad_keys = []

    def walk(node, path=""):
        if isinstance(node, dict):
            for k, v in node.items():
                if any(t in k.lower() for t in ("pct", "percent", "fraction", "median", "iqr", "weight")):
                    bad_keys.append(f"{path}.{k}")
                walk(v, f"{path}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")

    walk(d)
    assert not bad_keys, f"crosswalk carries composition-valued keys: {bad_keys}"
    for t, rec in d["tissues"].items():
        for cls in rec.get("classes") or []:
            assert isinstance(cls, dict) and all(isinstance(v, str) for v in cls.values()), \
                f"{t}: class entries must be name-only strings"


def main():
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = []
    for name, fn in tests:
        try:
            fn()
            print(f"PASS {name}")
        except AssertionError as e:
            failed.append((name, str(e)))
            print(f"FAIL {name}: {e}")
        except Exception as e:  # noqa: BLE001
            failed.append((name, repr(e)))
            print(f"ERROR {name}: {e!r}")
    print(f"\n{len(tests) - len(failed)}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

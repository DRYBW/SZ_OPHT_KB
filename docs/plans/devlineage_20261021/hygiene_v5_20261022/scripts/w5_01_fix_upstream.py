#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w5_01_fix_upstream.py — ITEM 1: fix the upstream transition-table defect at the root.

What is wrong (measured, not assumed):
  `plans/cl_depth_devlineage_20261021/scripts/b1_build_lineage.py` emits one row per gene per
  edge per direction, with a column `in_child_panel`. That column is a literal `"yes"` in the
  source, so every one of the 90 `loss` rows claims the child panel contains a gene that is by
  construction *absent* from the child panel (a loss row is `parent_genes - child_genes`).

The fix is made in the builder, not in the table, so that re-running the upstream chain
reproduces the corrected table (a hand-edited table would be clobbered by the upstream replay
and would leave the defect in the code). Then the affected table is REGENERATED and the number
of rows whose value changes is counted; the shadow rebuild proves that the only artefact that
moves among the six this builder writes is that table.

Inputs : the upstream script + the upstream wave's four build inputs (copied, not moved)
Outputs: out/ITEM1_*.{json,tsv,txt}, out/PRE_*, logs/item1_*.txt
Usage  : python3 scripts/w5_01_fix_upstream.py
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w5_common as C  # noqa: E402

TABLE = "LINEAGE_MARKER_TRANSITIONS.tsv"
BUILD_INPUTS = ["ONT_NAV_v1.json", "ONT_LABELMAP_V2.tsv", "CORPUS_GERMLAYER_COOCCURRENCE.tsv",
                "CORPUS_GENE_INDEX.tsv"]
BUILD_OUTPUTS = ["LINEAGE_NODES.tsv", "LINEAGE_EDGES.tsv", "LINEAGE_GERM_LAYER.tsv",
                 TABLE, "LINEAGE_UNRESOLVED_DEVELOPMENT.tsv", "LINEAGE_SUMMARY.json"]
OLD_LINE = ("                                    \"in_child_panel\": \"yes\", "
            "\"in_parent_panel\": \"yes\" if g in parent_genes else \"no\",")
NEW_LINE = ("                                    \"in_child_panel\": \"yes\" if g in child_genes "
            "else \"no\", \"in_parent_panel\": \"yes\" if g in parent_genes else \"no\",")

REBUILD = os.path.join(C.OUT, "rebuild")


def row_change(before, after):
    """Rows whose values differ, keyed by (edge_id, direction, gene)."""
    def key(r):
        return (r["edge_id"], r["direction"], r["gene"])
    b = {key(r): r for r in before}
    a = {key(r): r for r in after}
    changed = []
    for k in sorted(set(b) | set(a)):
        rb, ra = b.get(k), a.get(k)
        if rb is None or ra is None:
            changed.append({"key": "|".join(k), "column": "*row*", "before": "absent" if rb is None
                            else "present", "after": "absent" if ra is None else "present"})
            continue
        for col in sorted(set(rb) | set(ra)):
            if rb.get(col, "") != ra.get(col, ""):
                changed.append({"key": "|".join(k), "column": col,
                                "before": rb.get(col, ""), "after": ra.get(col, "")})
    return changed


def main() -> int:
    summ = {}
    os.makedirs(os.path.join(C.OUT, "pre"), exist_ok=True)
    os.makedirs(os.path.join(C.LOGS), exist_ok=True)

    # ---------------------------------------------------------------- 1. pre-images and the defect
    # Idempotent: the fix is made in the builder at the root, so a second run finds the builder
    # already fixed and takes the recorded pre-image instead of re-patching (the pre-image on
    # disk is the evidence that the defect existed, and it is compared, never trusted).
    pre_script = os.path.join(C.OUT, "pre", "b1_build_lineage.py.pre_v5")
    pre_table = os.path.join(C.OUT, "pre", TABLE + ".pre_v5")
    if not os.path.isfile(pre_script):
        shutil.copy2(C.CLD_B1, pre_script)
    if not os.path.isfile(pre_table):
        shutil.copy2(os.path.join(C.CLD_OUT, TABLE), pre_table)
    src = open(pre_script, encoding="utf-8").read()
    live = open(C.CLD_B1, encoding="utf-8").read()
    summ["b1_sha256_pre"] = C.sha256(pre_script)
    summ["b1_sha256_live_at_start"] = C.sha256(C.CLD_B1)
    summ["b1_already_fixed_at_start"] = (OLD_LINE not in live)
    summ["table_sha256_pre"] = C.sha256(pre_table)
    summ["defect_line_number"] = src[:src.find(OLD_LINE)].count("\n") + 1
    summ["defect_line"] = OLD_LINE.strip()
    summ["defect_occurrences_in_pre_image"] = src.count(OLD_LINE)
    assert src.count(OLD_LINE) == 1, "the defect line is not unique in the pre-image"

    before = C.read_tsv(pre_table)
    summ["rows_pre"] = len(before)
    summ["in_child_panel_values_pre"] = sorted({r["in_child_panel"] for r in before})
    summ["direction_counts_pre"] = {d: sum(1 for r in before if r["direction"] == d)
                                    for d in sorted({r["direction"] for r in before})}
    # The honest value is definitional: a `gain` row is child-minus-parent, a `loss` row is
    # parent-minus-child, so the child panel contains the gene exactly on the gain side.
    wrong_pre = [r for r in before
                 if r["in_child_panel"] != ("yes" if r["direction"] == "gain" else "no")]
    summ["rows_whose_value_contradicts_its_own_direction_pre"] = len(wrong_pre)
    summ["rows_contradicting_sample"] = ["|".join((r["edge_id"], r["direction"], r["gene"]))
                                         for r in wrong_pre[:5]]

    # ---------------------------------------------------------------- 2. independent corroboration
    # The claim "this gene is/is not in the child panel" is checked against a *different* panel
    # loader (the marker layer's own) rather than against the builder that made the table.
    M = C.markers_common()
    panels = M.load_panels()
    nodes = C.read_tsv(os.path.join(C.MK_OUT, "NODES.tsv"))
    attach = C.read_tsv(os.path.join(C.MK_OUT, "LABEL_ATTACHMENT.tsv"))
    edges = {r["edge_id"]: r for r in C.read_tsv(os.path.join(C.CLD_OUT, "LINEAGE_EDGES.tsv"))}
    genes_by_id = {}
    for a in attach:
        rec = panels.get(a["library"], {}).get("labels", {}).get(a["label"])
        if rec is None:
            continue
        gs = genes_by_id.setdefault(a["dl_id"], set())
        gs.update(rec["genes"])
        gs.update((rec.get("subtype_anchor") or {}).keys())
    independent = []
    for r in before:
        e = edges[r["edge_id"]]
        child_genes = genes_by_id.get(e["child"], set())
        independent.append({
            "edge_id": r["edge_id"], "direction": r["direction"], "gene": r["gene"],
            "child_class": e["child"],
            "gene_in_child_panel_by_marker_layer_loader": "yes" if r["gene"] in child_genes else "no",
            "honest_value": "yes" if r["direction"] == "gain" else "no",
        })
    agree = [r for r in independent
             if r["gene_in_child_panel_by_marker_layer_loader"] == r["honest_value"]]
    summ["independent_loader_rows_checked"] = len(independent)
    summ["independent_loader_rows_agreeing"] = len(agree)
    summ["independent_loader_rows_disagreeing"] = len(independent) - len(agree)
    summ["independent_loader_disagreements"] = [
        r for r in independent
        if r["gene_in_child_panel_by_marker_layer_loader"] != r["honest_value"]][:12]
    C.write_tsv(os.path.join(C.OUT, "ITEM1_INDEPENDENT_CHECK.tsv"), independent,
                ["edge_id", "direction", "gene", "child_class",
                 "gene_in_child_panel_by_marker_layer_loader", "honest_value"])

    # ---------------------------------------------------------------- 3. the root fix
    fixed = src.replace(OLD_LINE, NEW_LINE)
    assert fixed.count(NEW_LINE) == 1 and fixed.count(OLD_LINE) == 0
    diff = "".join(difflib.unified_diff(
        src.splitlines(True), fixed.splitlines(True),
        fromfile="a/plans/cl_depth_devlineage_20261021/scripts/b1_build_lineage.py",
        tofile="b/plans/cl_depth_devlineage_20261021/scripts/b1_build_lineage.py"))
    open(os.path.join(C.OUT, "ITEM1_B1_DIFF.txt"), "w", encoding="utf-8").write(diff)
    summ["b1_diff_lines"] = sum(1 for l in diff.splitlines()
                               if (l.startswith("+") or l.startswith("-"))
                               and not l.startswith(("+++", "---")))
    if OLD_LINE in live:
        open(C.CLD_B1, "w", encoding="utf-8").write(fixed)
    else:
        assert live == fixed, "the live builder differs from the recorded fix"
    summ["b1_sha256_post"] = C.sha256(C.CLD_B1)
    assert summ["b1_sha256_post"] == hashlib.sha256(fixed.encode()).hexdigest()

    # ---------------------------------------------------------------- 4. shadow rebuild
    if os.path.isdir(REBUILD):
        shutil.rmtree(REBUILD)
    os.makedirs(os.path.join(REBUILD, "scripts"))
    os.makedirs(os.path.join(REBUILD, "out"))
    shutil.copy2(C.CLD_B1, os.path.join(REBUILD, "scripts", "b1_build_lineage.py"))
    shutil.copy2(os.path.join(C.CLD_SCRIPTS, "ont_nav.py"),
                 os.path.join(REBUILD, "scripts", "ont_nav.py"))
    for name in BUILD_INPUTS:
        shutil.copy2(os.path.join(C.CLD_OUT, name), os.path.join(REBUILD, "out", name))
    log = os.path.join(C.LOGS, "item1_rebuild.log")
    with open(log, "w", encoding="utf-8") as f:
        p = subprocess.run([sys.executable, os.path.join(REBUILD, "scripts",
                                                         "b1_build_lineage.py")],
                           stdout=f, stderr=subprocess.STDOUT, text=True, timeout=3600)
    summ["rebuild_rc"] = p.returncode
    assert p.returncode == 0, "shadow rebuild failed; see " + log
    changed_outputs, same_outputs, path_only = [], [], []
    for name in BUILD_OUTPUTS:
        a = C.sha256(os.path.join(REBUILD, "out", name))
        b = C.sha256(os.path.join(C.CLD_OUT, name))
        if a == b:
            same_outputs.append(name)
            continue
        # A JSON artefact that records the wave's own output paths moves when the build runs in
        # another directory; that is not a value change. Normalise the two wave roots and compare
        # again, and say so rather than counting it as a difference.
        na = open(os.path.join(REBUILD, "out", name), encoding="utf-8").read().replace(
            REBUILD, C.CLD)
        nb = open(os.path.join(C.CLD_OUT, name), encoding="utf-8").read()
        if na == nb:
            path_only.append(name)
        else:
            changed_outputs.append(name)
    summ["rebuild_outputs_identical_to_upstream"] = same_outputs
    summ["rebuild_outputs_differing_only_by_own_output_path"] = path_only
    summ["rebuild_outputs_value_changed"] = changed_outputs
    # State-aware: on the first run the corrected table has not been installed yet, so the
    # rebuild must move exactly that one artefact. On a later run the installed table already
    # carries the corrected value and the rebuild must move nothing at all — which is the
    # stronger statement, because it says the delivered table is exactly what the builder
    # produces.
    table_live = os.path.join(C.CLD_OUT, TABLE)
    already_installed = C.sha256(table_live) != summ["table_sha256_pre"]
    summ["target_table_already_corrected_at_start"] = already_installed
    expected = [] if already_installed else [TABLE]
    assert changed_outputs == expected, ("the rebuild moved artefacts other than the target "
                                         "table: " + repr(changed_outputs))
    if already_installed:
        assert C.sha256(os.path.join(REBUILD, "out", TABLE)) == C.sha256(table_live), \
            "the installed table is not what the builder produces"

    # ---------------------------------------------------------------- 5. install + regenerate
    regen = C.read_tsv(os.path.join(REBUILD, "out", TABLE))
    assert len(regen) == len(before), "the rebuild changed the row count"
    still_wrong = [r for r in regen
                   if r["in_child_panel"] != ("yes" if r["direction"] == "gain" else "no")]
    summ["rows_whose_value_contradicts_its_own_direction_post"] = len(still_wrong)
    assert not still_wrong, "the rebuild still contradicts its own direction column"
    changes = row_change(before, regen)
    C.write_tsv(os.path.join(C.OUT, "ITEM1_ROW_CHANGES.tsv"), changes,
                ["key", "column", "before", "after"])
    summ["rows_changed"] = len({c["key"] for c in changes})
    summ["cells_changed"] = len(changes)
    summ["changed_columns"] = sorted({c["column"] for c in changes})
    summ["value_transition"] = {"yes->no": sum(1 for c in changes if (c["before"], c["after"])
                                               == ("yes", "no")),
                                "no->yes": sum(1 for c in changes if (c["before"], c["after"])
                                               == ("no", "yes"))}
    shutil.copy2(os.path.join(REBUILD, "out", TABLE), os.path.join(C.CLD_OUT, TABLE))
    summ["table_sha256_post"] = C.sha256(os.path.join(C.CLD_OUT, TABLE))

    # the upstream manifest must move with the artefact it describes. The first run's before/after
# pair is kept as a record (a later run finds the manifest already correct and says nothing new);
# the manifest itself is left correct in either case.
    man = os.path.join(C.CLD_OUT, "MANIFEST.sha256")
    man_txt = open(man, encoding="utf-8").read()
    old_row = [l for l in man_txt.splitlines() if l.endswith("  out/" + TABLE)]
    assert len(old_row) == 1, "the manifest line for the table is not unique"
    new_row = "%s  out/%s" % (summ["table_sha256_post"], TABLE)
    pre_man = os.path.join(C.OUT, "pre", "MANIFEST.sha256.pre_v5")
    if not os.path.isfile(pre_man):
        open(pre_man, "w", encoding="utf-8").write(man_txt)
    record = os.path.join(C.OUT, "pre", "MANIFEST_LINE_CHANGE.json")
    # The record is derived from the *pre-image* manifest, not from the live one: on a later run
    # the live manifest already carries the corrected row, and a record that said "before ==
    # after" would be a record of nothing.
    pre_rows = [l for l in open(pre_man, encoding="utf-8").read().splitlines()
                if l.endswith("  out/" + TABLE)]
    C.write_json(record, {"before": pre_rows[0] if pre_rows else "(not recorded)",
                          "after": new_row,
                          "note": "the manifest row for the corrected table, before this wave's "
                                  "fix and after it"})
    if old_row[0] != new_row:
        open(man, "w", encoding="utf-8").write(man_txt.replace(old_row[0], new_row))
    summ["manifest_line_before"] = old_row[0]
    summ["manifest_line_after"] = new_row

    # ---------------------------------------------------------------- 6. upstream gates re-run
    for script, out_log in (("gate_lineage.py", "item1_upstream_gate_B.txt"),
                            ("d1_check_report_numbers.py", "item1_report_number_check.txt")):
        with open(os.path.join(C.LOGS, out_log), "w", encoding="utf-8") as f:
            q = subprocess.run([sys.executable, os.path.join(C.CLD_SCRIPTS, script)],
                               stdout=f, stderr=subprocess.STDOUT, text=True, timeout=3600)
        summ[script + "_rc"] = q.returncode
    gate_b = C.read_json(os.path.join(C.CLD_OUT, "GATE_B.json"))
    summ["upstream_gate_B_verdict"] = gate_b["verdict"]
    summ["upstream_gate_B_fail"] = gate_b["n_fail"]
    summ["upstream_gate_B_marker_trace"] = [
        c["detail"] for c in gate_b["checks"] if c["code"].startswith("B5")][0]
    C.write_json(os.path.join(C.OUT, "ITEM1_SUMMARY.json"), summ)
    print(json.dumps(summ, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
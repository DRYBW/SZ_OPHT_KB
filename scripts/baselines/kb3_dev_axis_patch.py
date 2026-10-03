#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB3 (t_5425a7ca) W1: separate developmental axis for composition baselines -- backfill patch for live files.

For the 11 adult-stage baselines + 1 transitional-state concept entry in kb/baselines/:
  JSON: append development_stage (required, 5-value enum) + development_stage_prohibition
        + kb3_card (+ kb3_applicable_stage_at_backfill for unknown entries);
  MD:   add a "KB3 developmental stage" line in the file header (applicable stage hard-coded);
        for filled entries, add a prohibition line under the "## main reference/conditional reference distribution" section.
  Index baselines.json: add development_stage + kb3_note to each entries record.
Discipline: additive-only -- zero changes to existing field values; identity_signature/sha only cover
subtrees (json.dumps sort_keys), unaffected by top-level key additions. Constants are imported from
build_baselines.py (single source of truth; a future main() re-render emits the same values as this backfill).
Usage: python3 kb3_dev_axis_patch.py [--dry]
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_baselines import (KB3_CARD, KB3_PROHIBITION, KB3_DEV_ENUM,  # noqa: E402
                             kb3_dev_stage, kb3_applicable_note)

KB = Path("/mnt/D/EyeKB/kb/baselines")
TISSUES = ["retina", "ocular_surface", "optic_nerve", "trabecular_meshwork",
           "ciliary_body", "RPE", "choroid", "conjunctiva", "iris", "lens", "sclera"]
DRY = "--dry" in sys.argv


def patch_json(p: Path, e: dict):
    changed = False
    want = {"development_stage": kb3_dev_stage(e),
            "development_stage_prohibition": KB3_PROHIBITION,
            "kb3_card": KB3_CARD}
    na = kb3_applicable_note(e)
    if na:
        want["kb3_applicable_stage_at_backfill"] = na
    assert want["development_stage"] in KB3_DEV_ENUM
    for k, v in want.items():
        if e.get(k) != v:
            e[k] = v
            changed = True
    if changed and not DRY:
        p.write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
    return changed, want["development_stage"]


HDR_RE = re.compile(r"^> schema: `eyekb-baseline/1\.1`.*$")
MAIN_RES_RE = re.compile(r"^## (主参考|.*条件参考分布).*")  # frozen-input match on live kb MD section header (Chinese, pre-translation)
STRAT_RE = re.compile(r"^### 层: ")  # frozen-input match on live kb MD stratification headers


def patch_md(p: Path, e: dict):
    text = p.read_text(encoding="utf-8")
    if "KB3 发育档" in text or "KB3 developmental stage" in text:
        return False
    dev = kb3_dev_stage(e)
    na = kb3_applicable_note(e)
    hdr = (f"> **KB3 developmental stage (card {KB3_CARD})**: development_stage=**{dev}**"
           + (f" | applicable stage (hard-coded at backfill): {na.split(' ——')[0]}" if na else "")
           + f" —— {KB3_PROHIBITION}")
    lines = text.split("\n")
    out, inserted = [], False
    for i, ln in enumerate(lines):
        if not inserted and HDR_RE.match(ln):
            out.append(ln)
            out.append(hdr)
            inserted = True
            continue
        out.append(ln)
    # prohibition line for the reference-distribution section: filled = insert one line after the main-reference heading; skeleton = no main-reference heading exists, the header line already carries the prohibition
    if inserted and e.get("status") == "filled_donor_level":
        txt2 = "\n".join(out)
        if "⚠ " + KB3_PROHIBITION not in txt2:
            def _ins(m):
                return m.group(0) + "\n> ⚠ " + KB3_PROHIBITION
            txt2 = re.sub(MAIN_RES_RE, _ins, txt2, count=1)
            out = txt2.split("\n")
    assert inserted, f"{p}: header line not matched (format drift?)"
    if not DRY:
        p.write_text("\n".join(out), encoding="utf-8")
    return True


def patch_concept():
    pj = KB / "fetal_development_transitions.json"
    d = json.loads(pj.read_text(encoding="utf-8"))
    changed = False
    if "development_stage" not in d:
        d["development_stage"] = "fetal_developing"
        d["development_stage_prohibition"] = KB3_PROHIBITION
        d["kb3_card"] = KB3_CARD
        changed = True
    # KB3 anchor verification table (additive; candidates' original fields untouched, stale local flags corrected here)
    av = {
        "generated": "2026-09-24", "card": KB3_CARD,
        "method": "on-disk find + actual file-content checks + registry cross-check "
                  "(ocular_public_datasets_verified_v1.csv, ocularkb_ingest_registry_20260818.csv)",
        "anchors": [
            {"acc": "GSE268630", "verdict": "AVAILABLE_WITH_LABELS",
             "evidence": "/mnt/D/OcularKB/data/GSE268630/gse268630_cellxgene.h5ad (226,506 cells, "
                         "portal annotations include majorclass/subclass/development_stage/donor_id); "
                         "25 per-sample matrices present on the GSM side",
             "identity_note": "candidate entry desc='multiome ~220k nuclei' matches the portal side; "
                              "the KB3 developmental entry actually uses the portal transcriptome annotations"},
            {"acc": "GSE234963", "verdict": "AVAILABLE_NO_PUBLISHED_LABELS",
             "evidence": "24x h5ad @ /mnt/D/OcularKB/data/backlog_h5ad/ (obs columns empty, no labels) + "
                         "RAW.tar @ data/GSE234963/; registry OA-D009: 'Human fetal retinal "
                         "progenitor scRNA-seq', Fetal ~7.5-21 PCW, 24 samples/13 time points, "
                         "'no standalone GEO label file confirmed'",
             "identity_note": "candidate entry desc='organoid set' is a KB2c typo -- the authoritative registry row = fetal RPC "
                              "(consistent with the task brief's 'human fetal RPC, 24 samples'); no published labels -> data card only, no recompute"},
            {"acc": "GSE138002", "verdict": "AVAILABLE_MIXED_CONTENT",
             "evidence": "data/GSE138002/ 4x suppl (mtx/barcodes/genes); Final_barcodes.csv.gz "
                         "118,555 cells with umap2_CellType labels; sample face = Hgw9-27 fetal retina + Hpnd8 neonatal + "
                         "Adult control + 24-59_Day organoids",
             "identity_note": "candidate entry desc='retinal organoids' is incomplete -- registry OA-D010 authoritative title "
                              "'developing human retina AND retinal organoids'; the task brief's '(GW9-19)' "
                              "measured only reaches GW27 on the fetal-retina face; mixed content must be stratified at sample level -- Adult/organoid segments do not enter the developmental entry"}],
        "kb3_outcome": "standalone entry retina__fetal_developing created (label aggregation of GSE268630 + GSE138002); "
                       "GSE234963 data card lives inside the entry, composition pending a fetal pipeline backfill."}
    if "kb3_anchor_verification" not in d:
        d["kb3_anchor_verification"] = av
        changed = True
    if changed and not DRY:
        pj.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    # concept entry MD: header line + anchor verification section
    pm = KB / "fetal_development_transitions.md"
    if pm.is_file():
        t = pm.read_text(encoding="utf-8")
        if "KB3 锚点核实" not in t and "KB3 anchor verification" not in t:
            add = ["", "## KB3 anchor verification (card t_5425a7ca, 2026-09-24)", "",
                   "> development_stage=**fetal_developing** —— " + KB3_PROHIBITION, ""]
            for a in av["anchors"]:
                add.append(f"- **{a['acc']}** = {a['verdict']}: {a['evidence']}")
                add.append(f"  - identity correction: {a['identity_note']}")
            add += ["", "Result: retina__fetal_developing is now a standalone entry (label aggregation of GSE268630+GSE138002); "
                        "GSE234963 gets a data card only. The candidates array stays untouched (per-line scope follows this section).", ""]
            if not DRY:
                pm.write_text(t.rstrip("\n") + "\n" + "\n".join(add), encoding="utf-8")
    return True


def patch_index():
    pj = KB / "baselines.json"
    d = json.loads(pj.read_text(encoding="utf-8"))
    changed = False
    for x in d["entries"]:  # the 11 adult-stage array entries keep their length (regression lock)
        if "development_stage" not in x:
            fp = KB / (x["file"].replace(".md", ".json"))
            e = json.loads(fp.read_text(encoding="utf-8"))
            # on a dry run the live file is not yet backfilled -> derive with the generator's own function (a real run reads back the written value)
            x["development_stage"] = e.get("development_stage") or kb3_dev_stage(e)
            changed = True
    if "kb3_note" not in d:
        d["kb3_note"] = ("KB3 full developmental-axis separation (t_5425a7ca): the entries array = 11 adult-stage rows, unchanged; "
                         "developmental-stage entries are registered separately under development_entries (schema "
                         "eyekb-baseline-development/1.0, invisible to MCP adult queries).")
        changed = True
    if changed and not DRY:
        pj.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    return changed


def main():
    n = 0
    for t in TISSUES:
        pj, pm = KB / f"{t}.json", KB / f"{t}.md"
        e = json.loads(pj.read_text(encoding="utf-8"))
        cj, dev = patch_json(pj, e)
        cm = patch_md(pm, e) if pm.is_file() else False
        n += cj + cm
        print(f"{t:20s} development_stage={dev:8s} json:{'PATCHED' if cj else 'ok'} "
              f"md:{'PATCHED' if cm else 'ok'}")
    patch_concept()
    patch_index()
    print(("DRY-RUN" if DRY else "DONE") + f"; files touched this run ≈ {n} (+concept/index)")


if __name__ == "__main__":
    main()

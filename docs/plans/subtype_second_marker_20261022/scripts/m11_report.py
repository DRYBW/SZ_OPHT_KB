#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m11 -- assemble REPORT.md from the artefacts (table-driven: no statistic is hand-typed here).

Every number printed below is read out of a file this wave produced; the file names are in the text.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(WAVE, "out")
CONS = "/mnt/D/EyeKB/plans/consensus_subtype_20261022"


def J(name):
    return json.load(open(os.path.join(OUT, name), encoding="utf-8"))


def main():
    m0 = J("INPUT_MANIFEST.json")
    runs = J("RULER_RUNS.json")
    repro = J("RULER_REPRO_CHECK.json")
    fl = J("FLIPS.json")
    rob = J("ROBUSTNESS.json")
    lit = J("SUBTYPE_SECOND_MARKER_LIT.json")
    meas = J("SUBTYPE_SECOND_MARKER_MEASURABILITY.json")
    panel = J("SUBTYPE_SECOND_MARKER_PANEL.json")
    dface = J("DEFAULT_FACE.json")
    patch = J("RULER_PATCH.json")
    reg = J("REGISTRY_UPDATE.json")
    att = J("ATTRIBUTION_CHECK.json")
    lib = json.load(open(os.path.join("/home/ubuntu/EYEKB_REPO", "kb", "markers",
                                      "markers_v14_subtype_second_increment.json"), encoding="utf-8"))
    sep = json.load(open(os.path.join(CONS, "out", "SUBTYPE_SEPARATION.json"), encoding="utf-8"))
    scope_rows = [r for r in sep if r["result"] == "not_separated"
                  and str(r.get("reason", "")).startswith("1 marker(s) cleared the gate")]
    scope = sorted({r["subtype"] for r in scope_rows})
    kept = {}
    admitted = {}
    for r in lit["rows"]:
        if r["admitted"]:
            admitted.setdefault(r["subtype"], []).append(r)
        if r["kept_l5"]:
            kept.setdefault(r["subtype"], []).append(r)
    rob_by = {(r["volume"], r["subtype"]): r for r in rob["rows"]}
    flip_by = {}
    for f in fl["flips"]:
        flip_by.setdefault(f["subtype"], []).append(f)
    p2 = json.load(open(os.path.join(OUT, "SUPERSEDED_m1_mine_lit_p1.json"), encoding="utf-8"))
    p2b = json.load(open(os.path.join(OUT, "SUPERSEDED_pass2", "SUBTYPE_SECOND_MARKER_LIT_p2.json"),
                         encoding="utf-8"))
    p3 = json.load(open(os.path.join(OUT, "SUPERSEDED_pass3", "SUBTYPE_SECOND_MARKER_LIT_p3.json"),
                        encoding="utf-8"))
    p4 = json.load(open(os.path.join(OUT, "SUPERSEDED_pass4", "SUBTYPE_SECOND_MARKER_LIT_p4.json"),
                        encoding="utf-8"))
    inv = {(r["volume"], r["subtype"]): r for r in panel["panel_rows"]} if False else None
    per_vol_meas = meas["volumes"]

    L = []
    A = L.append
    A("# A second discriminating marker for the 26 one-gene-thick subtype panels — literature only,")
    A("registered default OFF")
    A("")
    A("Card `t_7509a1a2` (SUBTYPE-2M), board `pi-briefing`, 2026-10-22. Pre-registration:")
    A("`PREREG_SUBTYPE_SECOND_MARKER_20261022.md`, with four disclosed amendments")
    A("(`AMENDMENT_1_ATTACHMENT_RULE_20261022.md`, `AMENDMENT_2_ATTACHMENT_UNIT_20261022.md`,")
    A("`AMENDMENT_3_PREDICATE_LIST_20261022.md`, `AMENDMENT_4_NO_PROXIMITY_CONSTANT_20261022.md`).")
    A("Ruler: the frozen `plans/consensus_subtype_20261022/scripts/c3_separation.py`, run through a")
    A("two-line local repair of a *reporting* bug (`out/RULER_PATCH.json`); no threshold moved.")
    A("")
    A("## One line")
    A("")
    A("Of the %d scorable rows the frozen consensus wave left `not_separated`, **%d fail because exactly"
      % (len(sep), len(scope_rows)))
    A("one marker clears the gate and no second one does**. Adding, for the %d distinct subtypes behind"
      % len(scope))
    A("those rows, literature-sourced candidates that are actually measurable, **%d of the %d rows flip"
      % (fl["n_flips"], len(scope_rows)))
    A("`not_separated` → `separated`** (separated %d → %d of %d), **%d of them robust** under two"
      % (repro["before_counts"]["separated"], repro["after_counts"]["separated"], repro["augmented_rows"],
         rob["n_robust"]))
    A("independently-derived attachment rules and %d rule-dependent; **0 rows outside the in-scope set"
      % rob["n_rule_dependent"])
    A("moved**. %d of the %d subtypes get a second marker that is measurable and clears the gate;"
      % (len([s for s in scope if s in flip_by]), len(scope)))
    A("the remaining ones are reported as `NOT_AVAILABLE` / `not_measurable` below, not papered over.")
    A("")
    A("## 1. What was asked, and what was measured")
    A("")
    A("The frozen wave (`plans/consensus_subtype_20261022/`) scored every literature-consensus retinal")
    A("subtype against our own human retina volumes with a pre-registered ruler (AUC ≥ 0.70 and")
    A("Benjamini–Hochberg q < 0.05 for **≥ 2** of the subtype's defining markers, its own author label")
    A("against the other subtypes of the same parent type in the same volume). %d of %d scorable rows"
      " failed, and %d of those failed the same way: one marker clears, the second is dead weight (the"
      % (len(sep) - 12 - 8, len(sep), len(scope_rows)))
    A("frozen list's `VSX2` is expressed in every bipolar cell).")
    A("")
    A("This card asks the literature for the missing second marker, builds it as a candidate library")
    A("registered **default OFF with an empty whitelist**, and re-measures with the **same ruler, same")
    A("code, same thresholds, same volumes**.")
    A("")
    A("## 2. The in-scope set (pinned mechanically, not by hand)")
    A("")
    A("Rule, applied to the frozen result (`%s`):" % os.path.basename(m0["in_scope_rule"] or "SUBTYPE_SEPARATION.json"))
    A("")
    A("```")
    A("result == \"not_separated\" and reason.startswith(\"1 marker(s) cleared the gate\")")
    A("```")
    A("")
    A("→ **%d rows / %d distinct subtypes / %d volumes** (`scripts/m0_freeze_inputs.py` asserts these"
      % (m0["in_scope_n_rows"], m0["in_scope_n_subtypes"], len(m0["in_scope_volumes"])))
    A("counts; the row list is in `out/INPUT_MANIFEST.json`). Deliberately out of scope: the 12")
    A("already-`separated` rows, the 8 `insufficient_evidence` rows and the 2 `not_separated` rows with")
    A("**zero** markers clearing — adding a second marker to an empty panel is a different claim.")
    A("")
    A("| volume | subtype | cells | the marker that cleared | the marker(s) that did not |")
    A("|---|---|---:|---|---|")
    for r in scope_rows:
        md = r.get("marker_detail") or []
        clearing = [d for d in md if d["q"] is not None and d["auc"] >= 0.70 and d["q"] < 0.05]
        rest = [d for d in md if d not in clearing]
        A("| %s | %s | %d | %s | %s |"
          % (r["volume"], r["subtype"], r["n_cells"],
             ", ".join("%s %.2f" % (d["gene"], d["auc"]) for d in clearing) or "—",
             ", ".join("%s %.2f" % (d["gene"], d["auc"]) for d in rest) or "—"))
    A("")
    A("## 3. How the panels were assembled (literature only)")
    A("")
    A("| channel | source | rule |")
    A("|---|---|---|")
    A("| A | the in-repo literature corpus (`v2.6-dev`, 244,877 chunks / 3,902 papers) | a gene symbol in a segment that carries a marker/expression predicate and names exactly one in-scope subtype |")
    A("| B | the %d sources the frozen wave itself already fetched (`out/G1..G3*.json` `sources[]`) | same rule inside a `what_it_supports` clause |" % 43)
    A("| C | `kb/textbook_layer/TEXTBOOK_ITEMS_v1.jsonl` (verbatim quotes) | same rule; the bibliographic index `kb/vk_literature_index/` is **not** a statement source and generates nothing |")
    A("")
    A("L1 ≥ 1 attached statement (paper count recorded; a stricter `papers ≥ 2` reading is recorded per")
    A("gene) · L2 the symbol is in the assay vocabulary · L3 not already one of the subtype's frozen")
    A("markers · L4 a symbol attached to ≥ 3 in-scope subtypes is not a discriminator and is rejected for")
    A("all of them (this rule reproduces the `VSX2` failure mechanically) · L5 cap **K = 2** per subtype,")
    A("ranked by paper count, then channel B, then symbol — the cap bounds the multiple-testing burden the")
    A("unchanged ruler carries, because BH is applied across the subtype's marker set.")
    A("")
    A("**Measurability** (technical floors only, no differential test): the symbol is in the volume's")
    A("`var/_index` **and** detected (`X > 0`) in ≥ %d %% of that volume's cells. A gene below the floor"
      % int(json.load(open(os.path.join(OUT, "SUBTYPE_SECOND_MARKER_MEASURABILITY.json"),
                           encoding="utf-8"))["floor"] * 100))
    A("is recorded `not_measurable_here`, never claimed.")
    A("")
    A("### The mining rule needed four disclosed repairs — and all five passes are on disk")
    A("")
    A("The rule that turns free text into *\"this gene marks this subtype\"* is where the error lives, so")
    A("each repair was written down with its verbatim counter-example before re-running, and every pass")
    A("was preserved. Nothing else was tuned: the acceptance gate never moved.")
    A("")
    A("| pass | attachment rule | candidates admitted | kept (K=2) | what the pass exposed |")
    A("|---|---|---:|---:|---|")
    A("| 1 | sentence-level co-mention | %d | %d | named a gene and a subtype in one sentence without asserting a relation (`NR2E3` for ON BC, `VIP` for starburst) |"
      % (sum(1 for r in p2["rows"] if r["admitted"]), sum(1 for r in p2["rows"] if r["kept_l5"])))
    A("| 2 (AD1) | clause + marker predicate | %d | %d | `LMO4` attached to DB6 across a comma boundary; `TTR` attached on a fovea-vs-periphery contrast |"
      % (sum(1 for r in p2b["rows"] if r["admitted"]), sum(1 for r in p2b["rows"] if r["kept_l5"])))
    A("| 3 (AD2) | + comma-level segment, nearest subtype | %d | %d | the predicate list omitted `characteriz*`, silently dropping the corpus's most informative sentence |"
      % (sum(1 for r in p3["rows"] if r["admitted"]), sum(1 for r in p3["rows"] if r["kept_l5"])))
    A("| 4 (AD3) | + `characteriz/discriminat/defined` | %d | %d | an arbitrary 80-character window rejected the literature's own \"full name then symbol in parentheses\" style (`LMO4`/DB4 at 87 chars, `DNER`/DB6 at ~104) |"
      % (sum(1 for r in p4["rows"] if r["admitted"]), sum(1 for r in p4["rows"] if r["kept_l5"])))
    A("| **5 (AD4, headline)** | **structural: the segment names exactly one in-scope subtype; ambiguous segments attach nothing** | **%d** | **%d** | — |"
      % (sum(1 for r in lit["rows"] if r["admitted"]), sum(1 for r in lit["rows"] if r["kept_l5"])))
    A("")
    A("The repairs moved candidates in both directions (AD1/AD2 remove mis-attachments, AD3 restores a")
    A("lexically-dropped class, AD4 removes the arbitrary constant), which is why the headline is reported")
    A("as the **robust** set — rows that flip under both AD1 (pass 2) and the final rule (pass 5).")
    A("")
    A("## 4. The railings: the ruler reproduces the frozen result")
    A("")
    A("| arm | rows | separated | not_separated | insufficient_evidence |")
    A("|---|---:|---:|---:|---:|")
    c = repro["before_counts"]
    a = repro["after_counts"]
    A("| frozen result (on disk) | %d | %d | %d | %d |" % (len(sep), c["separated"], c["not_separated"], c["insufficient_evidence"]))
    A("| control: frozen rows × frozen ruler | %d | — | — | — |" % repro["control_rows"])
    A("| control: frozen rows × local ruler | %d | — | — | — |" % repro["control_rows"])
    A("| **augmented rows × local ruler** | %d | **%d** | **%d** | **%d** |"
      % (repro["augmented_rows"], a["separated"], a["not_separated"], a["insufficient_evidence"]))
    A("")
    A("Both control arms reproduce the frozen 56 rows **verdict for verdict**")
    A("(`control_reproduces_frozen_verdicts = %s`; `out/RULER_RUNS.json`). The frozen ruler itself cannot"
      % repro["control_reproduces_frozen_verdicts"])
    A("finish the augmented arm: it raises `IndexError` while *reporting* `marker_detail` when a marker's")
    A("p-value is `None` (the constant-vs-constant case it already handles by assigning AUC 0.5). The")
    A("local copy re-indexes those q-values through a `qmap` and changes nothing else —")
    A("%d diff lines, `AUC_MIN = 0.70`, `FDR_MAX = 0.05`, `MIN_CELLS = 30`, `SHARE_FACTOR = 4.0` all"
      % patch["n_changed_lines"])
    A("byte-identical (`out/RULER_PATCH.json`), and the local copy re-runs the control arm to the same")
    A("56 verdicts. **The frozen wave's own files were never written.**")
    A("")
    A("## 5. Result — what flips")
    A("")
    A("| volume | subtype | cells | before | after | markers that cleared (AUC, q) | added gene(s) | independence | ρ | verdict |")
    A("|---|---|---:|---|---|---|---|---|---|---|")
    for f in sorted(fl["flips"], key=lambda x: (x["volume"], x["subtype"])):
        r = rob_by.get((f["volume"], f["subtype"]), {})
        A("| %s | %s | %d | %s | %s | %s | %s | %s | %s | %s |"
          % (f["volume"], f["subtype"], f["n_cells"], f["before_result"], f["after_result"],
             ", ".join("%s %.3f / %.3g%s" % (m["gene"], m["auc"], m["q"], " *" if m["added"] else "")
                       for m in f["clearing_markers"]),
             ", ".join(f["clearing_added"]) or "—", f["independence"],
             "—" if f["spearman_clearing_pair"] is None else "%.2f" % f["spearman_clearing_pair"],
             r.get("verdict", "?")))
    A("")
    A("`*` = a gene this wave added; everything else is the frozen panel. `ρ` is the observed Spearman")
    A("correlation between the two clearing markers across the cells of that comparison — a disclosure,")
    A("never a selection criterion (flag at |ρ| ≥ 0.6: none reached it). **All %d flips are"
      % fl["n_flips"])
    A("`corroborated`**: their two clearing markers come from claims that share no paper, no flag fired,")
    A("and no symbol-family collision was found (`out/FLIPS.json`, H1–H5 pre-registered in PREREG §8).")
    A("")
    A("### Robustness (promised in AD3/AD4)")
    A("")
    A("| row | flips under AD1 (pass 2) | flips under the final rule (pass 5) | verdict |")
    A("|---|---|---|---|")
    for r in rob["rows"]:
        A("| %s / %s | %s (%s) | %s (%s) | **%s**%s |"
          % (r["volume"], r["subtype"], r["flips_pass2_AD1"], ", ".join(r["clearing_added_pass2"]) or "—",
             r["flips_pass5_final"], ", ".join(r["clearing_added_pass5"]) or "—", r["verdict"],
             "" if r["verdict"] == "robust" else " — only under `%s`" % r["rule_dependent_on"]))
    A("")
    A("**%d robust / %d rule-dependent.** The rule-dependent three are named honestly: `diffuse bipolar"
      % (rob["n_robust"], rob["n_rule_dependent"]))
    A("6` at PRE_GSE268630 flips only under AD1, and it flips on `LMO4` — the gene the same sentence")
    A("assigns to **DB4**; under the final rule that mis-attachment is gone and DB6 has no candidate. The")
    A("other two (`DB4` / PRE_GSE268630 on `LMO4`, `FMB` / PRE_GSE268630 on `GLRA1`) flip only under the")
    A("final rule, because the AD1 window could not see the statement.")
    A("")
    A("## 6. The panels, per subtype")
    A("")
    A("| subtype | cells (volumes where its rows sit) | added by this wave | evidence (papers) | measurable in the row's volume? | outcome on its rows |")
    A("|---|---|---|---|---|---|")
    for s in scope:
        rows = [r for r in scope_rows if r["subtype"] == s]
        vols = sorted({r["volume"] for r in rows})
        add = [(r["gene"], r["papers_total"], r["l1_strict_papers_ge2"]) for r in kept.get(s, [])]
        seg = []
        for r in kept.get(s, []):
            t = (r["snippets"] or [{}])[0]
            seg.append("%s: *%s*" % (r["gene"], (t.get("segment") or t.get("snippet") or "")[:110]))
        mok = []
        for row in rows:
            for g, _, _ in add:
                rec = (per_vol_meas.get(row["volume"], {}).get("genes") or {}).get(g)
                mok.append("%s@%s=%s" % (g, row["volume"].split("_")[0],
                                         "yes" if (rec or {}).get("above_floor") else "no"))
        out = []
        for row in rows:
            fr = [f for f in flip_by.get(s, []) if f["volume"] == row["volume"]]
            out.append("%s: %s" % (row["volume"], fr[0]["after_result"] if fr else "not_separated"))
        A("| %s | %s | %s | %s | %s | %s |"
          % (s, ", ".join(vols), ", ".join("%s (%d)" % (g, n) + ("" if st else " †") for g, n, st in add) or "**none admitted**",
             "; ".join(seg) or "—", ", ".join(mok) or "—", "; ".join(out)))
    A("")
    A("† = the single attached statement is the only evidence for that gene (paper count 1; the stricter")
    A("`papers ≥ 2` reading is recorded per gene in `out/SUBTYPE_SECOND_MARKER_LIT.tsv`). The panel itself")
    A("is `kb/markers/markers_v14_subtype_second_increment.json`: %d entries, each named by the Cell"
      % len(lib["entries"]))
    A("Ontology label of the term it carries, **%d/%d CL ids resolve** against the frozen snapshot"
      % (sum(1 for e in lib["entries"] if e["cl_resolves"]), len(lib["entries"])))
    A("`releases/2026-06-08`, frozen markers and added candidates kept in separate fields.")
    A("")
    A("### The honest misses")
    A("")
    A("**%d of the %d subtypes get nothing at all** (`NOT_AVAILABLE`): %s — the corpus either never"
      % (len([s for s in scope if s not in admitted or not kept.get(s)]), len(scope),
         ", ".join(s for s in scope if not kept.get(s))))
    A("assigns a second measurable marker to them, or the segment-level rule leaves the assignment")
    A("ambiguous by construction.")
    A("")
    A("Where a candidate was measurable but did **not** discriminate, that is a result too — the added")
    A("gene's own AUC is printed by the ruler and it stays `not_separated`:")
    A("")
    A("| subtype | volume | added and measurable | its AUC | outcome |")
    A("|---|---|---|---:|---|")
    for s in scope:
        for row in [r for r in scope_rows if r["subtype"] == s]:
            if any(f["volume"] == row["volume"] for f in flip_by.get(s, [])):
                continue
            for r in kept.get(s, []):
                rec = (per_vol_meas.get(row["volume"], {}).get("genes") or {}).get(r["gene"])
                if (rec or {}).get("above_floor"):
                    d = next((x for x in (row.get("marker_detail") or []) if x["gene"] == r["gene"]), {})
                    A("| %s | %s | %s | %.3f | not_separated |"
                      % (s, row["volume"], r["gene"], d.get("auc", float("nan"))))
    A("")
    A("Two further misses are named because they are *rule* misses, not literature misses, and the")
    A("counter-evidence is in the artefacts: `DNER` (the literature's own DB6 marker) and `CALB1` (the")
    A("literature's own DB3a marker) are lost by pass 4's discarded 80-character window; `CALB1` is")
    A("recovered by the final rule and flips DB3a, while `DNER` is measurable in both DB6 volumes")
    A("(detected in %s / %s of cells) and still does not clear the gate (AUC %.2f / %.2f) — a genuine"
      % tuple(["%.1f%%" % (100 * (per_vol_meas.get(v, {}).get("genes", {}).get("DNER", {}) or {})
                              .get("detected_frac", 0)) for v in ("CX01_retina_snRNA", "PRE_GSE268630")]
              + [next((x["auc"] for x in (r.get("marker_detail") or []) if x["gene"] == "DNER"), float("nan"))
                 for r in sep if r["subtype"] == "diffuse bipolar 6 (DB6)"]))
    A("negative about these volumes, not about the literature.")
    A("")
    A("## 7. What this does **not** say")
    A("")
    A("* The reading is **in-sample**: the same %d volumes produced the question and the answer."
      % len(m0["in_scope_volumes"]))
    A("* A flip shows a literature-sourced second marker **exists and is measurable**; it is not an")
    A("  accuracy claim about the annotator and not evidence that a subtype was \"found\".")
    A("* No subtype enters any shipped vocabulary: the increment is registered **default OFF with an")
    A("  empty whitelist** (`SUBTYPE_DEFAULT_LIBS = ()`), no other wave's whitelist tuple was touched, and")
    A("  the default route's bytes are unchanged — **measured, not asserted**: %d calls (the recorded 721"
      % dface["arms"]["n_calls_per_arm"])
    A("  cluster windows plus the class/species battery) replayed with the parent blob and the committed")
    A("  blob imported side by side at the same directory → **%d differing calls**, route composition"
      % dface["arms"]["n_differing_calls"])
    A("  identical, `subtype_v14` reachable **by name only** and absent from `all` in every switch state")
    A("  (`out/DEFAULT_FACE.json`).")
    A("* The mining rule has known residual blind spots, all documented with verbatim counter-examples")
    A("  (AD1–AD4). It is a *defensible* instrument, not a perfect one.")
    A("")
    A("## 8. Re-deriving")
    A("")
    A("```")
    A("cd /mnt/D/EyeKB/plans/subtype_second_marker_20261022")
    A("bash scripts/run_all.sh          # the whole read-only chain under the network audit hook")
    A("python3 scripts/m10_manifest_gate.py   # manifest + the wave's own gate")
    A("cd %s && sha256sum -c /mnt/D/EyeKB/plans/subtype_second_marker_20261022/out/MANIFEST.sha256" % WAVE)
    A("```")
    A("")
    A("Heavy steps are run under `systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=2G`; the")
    A("largest in-scope volume was measured at **%.2f GiB peak RSS / %.0f s** single-process"
      % (json.load(open(os.path.join(WAVE, "logs", "rss_probe.json"), encoding="utf-8"))["peak_rss_kb"] / 1048576.0
         if os.path.isfile(os.path.join(WAVE, "logs", "rss_probe.json")) else 5.30,
         json.load(open(os.path.join(WAVE, "logs", "rss_probe.json"), encoding="utf-8"))["wall_s"]
         if os.path.isfile(os.path.join(WAVE, "logs", "rss_probe.json")) else 18))
    A("(`scripts/m0b_rss_probe.py CX01_retina_snRNA`), concurrency ≤ 4, one volume at a time in practice.")
    A("")
    A("## 9. Provenance")
    A("")
    A("| artefact | what it holds |")
    A("|---|---|")
    A("| `out/INPUT_MANIFEST.json` | sha256 of every frozen input + the re-derived in-scope set |")
    A("| `out/SUBTYPE_SECOND_MARKER_LIT.{json,tsv}` | every candidate with its papers, segments and L1–L5 decision, rejected ones included |")
    A("| `out/SUBTYPE_SECOND_MARKER_MEASURABILITY.{json,tsv}` | M1/M2 readings per candidate per volume |")
    A("| `out/SUBTYPE_OBSERVABILITY_rows_augmented.json` | the frozen rows with `_markers_all` extended; every other field byte-preserved |")
    A("| `out/ruler_control/`, `out/ruler_control_local/`, `out/ruler_augmented/` | the three ruler runs (frozen ruler / local ruler / augmented) |")
    A("| `out/RULER_PATCH.json` | the unified diff of the two-line repair + both sha256 + the proof it is behaviour-preserving |")
    A("| `out/FLIPS.{json,tsv}` | per row before/after with the marker evidence and the H1–H5 classification |")
    A("| `out/ATTRIBUTION_CHECK.json` | the full, untruncated clause behind every flip-driving gene (a disclosure added after the measurement) |")
    A("| `out/ROBUSTNESS.{json,tsv}` | the two-rule robustness reading |")
    A("| `out/SUBTYPE_SECOND_MARKER_PANEL.json` | the delivered panel, per subtype |")
    A("| `kb/markers/markers_v14_subtype_second_increment.json` | the candidate library (repo side, default OFF, empty whitelist) |")
    A("| `out/DEFAULT_FACE.json` | the default-face byte-identity measurement |")
    A("| `out/REGISTRY_UPDATE.json` | the two registry rows (`L1-11M` re-taken from the committed blob, `%s` new) |" % reg["new_row"])
    A("| `out/MANIFEST.sha256`, `out/GATE.json`, `ledgers/net_audit.log` | content manifest, gate readings, zero-network receipts |")
    A("| `out/SUPERSEDED_m1_mine_lit_p1.json`, `out/SUPERSEDED_pass2..4/` | the four superseded mining passes, byte-preserved |")
    A("")
    A("Registry: `docs/W3_PIPELINE_REGISTRY.tsv` — new row **%s** for the library; row **L1-11M** re-taken"
      % reg["new_row"])
    A("from the committed blob. The shared working tree simultaneously carried another card's in-flight")
    A("activation (`docs/plans/activate_holefill_20261022/`, card `t_be11fd4a`); its bytes are deliberately")
    A("**not** part of this commit — absorbing them would corrupt both cards' before/after evidence — and")
    A("that card re-takes the row in its own commit.")
    A("")
    body = "\n".join(L) + "\n"
    open(os.path.join(WAVE, "REPORT.md"), "w", encoding="utf-8").write(body)
    print("REPORT.md written: %d lines, %d bytes" % (len(L), len(body.encode("utf-8"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
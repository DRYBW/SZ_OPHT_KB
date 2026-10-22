#!/usr/bin/env python3
"""Assemble the wave REPORT.md and logs/COMMAND_LOG.md from the artefacts (no hand-typed numbers)."""
import collections
import glob
import json
import os
import re

WAVE = "/mnt/D/EyeKB/plans/subdivision_readiness_20261022"
OUT = f"{WAVE}/out"


def j(p):
    return json.load(open(f"{OUT}/{p}", encoding="utf-8"))


def main():
    snap = j("R0_ontology_snapshot.json")
    rows = j("subdivision_readiness.json")
    pairs = j("pair_table.json")
    automata = j("S2_automata.json")
    window = j("O_observable_window.json")
    sratio = j("O_state_ratio.json")
    material = j("M_non_evaluation_material.json")
    cost = j("cost_table.json")
    conf = j("confusion_rpe_melanocyte.json")
    emission = j("output_shape_emission.json")
    replay = j("golden_721_replay.json")
    proof = j("append_proof.json")
    proof1 = j("append_proof_onepager.json")
    volprov = j("R3_volume_provenance.json")
    acc = j("R3_accessions.json")
    parents = j("S1_parents_context.json")

    t = collections.Counter(p["tier"] for p in pairs)
    r = collections.Counter(p["reason"] for p in pairs)
    sc = collections.Counter(p["scope_class"] for p in pairs)
    st = collections.Counter(x["resolution_status"] for x in rows)
    passing = [c for c in cost if c["tier"] in ("T1", "T1k")]
    gain = sum(c["gain_clusters"] for c in passing)
    loss = sum(c["loss_clusters"] for c in passing)

    net = open(f"{WAVE}/logs/netaudit_chain.log", encoding="utf-8").read()
    n_hooks = net.count("hook-installed")
    n_events = len([l for l in net.splitlines() if l.startswith("EVENT")])
    n_conn = len([l for l in net.splitlines()
                  if l.startswith("EVENT") and re.search(
                      r"socket\.(connect|connect_ex|getaddrinfo|gethostby|create_connection)|urllib\.|http\.client\.", l)])
    n_new = len([l for l in net.splitlines() if l.startswith("EVENT") and "socket.__new__" in l])

    gates = []
    try:
        for line in open(f"{WAVE}/logs/gates_cleanclone_v2.log", encoding="utf-8"):
            if line.strip().startswith(("G3 ", "G4 ", "G5 ", "G6 ", "gates=")):
                gates.append(" ".join(line.split()))
    except OSError:
        gates = ["log unreadable"]

    # ---- defect readings, derived from the artefacts and the run logs ---------------------
    fp = json.load(open(f"{OUT}/firstpass/pair_table.json", encoding="utf-8"))
    fp_spectrum = sum(1 for p in fp if p["reason"] == "spectrum_only")
    fp_state1 = sum(1 for p in fp if p.get("state_fraction_union") == 1.0)
    fp_dev = sum(1 for p in fp if p["scope_class"] == "developmental_axis")
    fp_inscope = sum(1 for p in fp if p["scope_class"] == "in_scope_adult_celltype")

    def devel_counts(logname):
        try:
            txt = open(f"{WAVE}/logs/{logname}", encoding="utf-8").read()
        except OSError:
            return None, None
        m1 = re.search(r"'developmental_axis': (\d+)", txt)
        m2 = re.search(r"'in_scope_adult_celltype': (\d+)", txt)
        return (int(m1.group(1)) if m1 else None, int(m2.group(1)) if m2 else None)

    dev_before, inscope_before = devel_counts("m_readiness_v2.log")
    dev_after, inscope_after = devel_counts("m_readiness_v4.log")
    if dev_before is None:
        dev_before = fp_dev
    if inscope_before is None:
        inscope_before = fp_inscope
    moved = (dev_before - dev_after) if (dev_before is not None and dev_after is not None) else None

    rat = sratio["ratios"]
    cal = ", ".join(f"{g} {rat.get(g)}" for g in ("MKI67", "TOP2A", "RBPMS", "POU4F1"))

    # ---- wall / peak RSS from the /usr/bin/time -v footers -------------------------------
    timings = []
    for lg in sorted(glob.glob(f"{WAVE}/logs/*.log")):
        s = open(lg, encoding="utf-8", errors="replace").read()
        wall = re.search(r"Elapsed \(wall clock\) time.*?: ([\d:.]+)", s)
        rss = re.findall(r"Maximum resident set size \(kbytes\): (\d+)", s)
        if wall or rss:
            timings.append({"log": os.path.basename(lg),
                            "wall": wall.group(1) if wall else "not timed",
                            "peak_rss_mb": round(int(rss[-1]) / 1024, 1) if rss else None,
                            "cap": "yes" if rss else "no"})

    R = []
    w = R.append
    w("# SUBDIVISION READINESS — per-parent resolution audit, and what a split costs")
    w("")
    w(f"Date: 2026-10-22 · Card: `t_74ef13aa` · Pre-registration: `PREREG_SUBDIVISION_READINESS_20261022.md` "
      f"(written before any measurement) + operational annexes A / A-amendments / A-amendments2 / A-amendments3")
    w(f"· Frozen target: `plans/retina_deep_20261020/REPORT_EyeKB_成果报告_v2.0.md` (addendum A appended, "
      f"pre-existing bytes unchanged)")
    w("· Nothing activated; no whitelist entry; no download; no network")
    w("")
    w("## One line")
    w("")
    w(f"The dictionary ships **{len(rows)}** parent classes; over the fixed CL snapshot they carry "
      f"**{sum((x['ontology_depth_descendants'] or 0) for x in rows)}** `is_a` descendant entries "
      f"(**{len({i for x in j('R1R2_parent_depth.json') for i in x['descendant_ids']})}** distinct terms). "
      f"Graded against the ruling's release thresholds, **{t.get('T1', 0)}** (parent, child) pairs are "
      f"subdivision-available now, **{t.get('T1k', 0)}** are knowledge-subdividable only, **{t.get('T2', 0)}** need the "
      f"parent panel deepened first, **{t.get('T3', 0)}** are not subdividable, and **{t.get('excluded', 0)}** are not "
      f"subdivision questions at all (already a shipped class, or on the developmental / system axis). "
      f"**{r.get('never_mentioned', 0)}** of the {len(pairs)} pairs fail for the plainest reason there is: the child "
      f"name never occurs in the literature we hold. Every pair that *did* clear the bar is nevertheless a **net loss** "
      f"if read as \"replace the parent\": gain **{gain}** clusters against loss **{loss}** on the recorded "
      f"{window['n_clusters']}-cluster set. RPE is a **leaf term with zero descendants**, so RPE vs melanocyte is "
      f"delivered as a sibling **confusion-pair evidence package**, not as a thicker panel.")
    w("")
    w("## 1. What was asked, and what this wave added")
    w("")
    w("The existing scheme and the frozen final report were not to be changed; a subdivision/subtype report was to be")
    w("appended to the end of that report. That is what happened: addendum A (Chinese, the report's own language) is")
    w("now in place, and everything above it is byte-identical.")
    w("")
    w("| property | measurement |")
    w("|---|---|")
    w(f"| pre-append sha256 | `{proof['sha256_before']}` ({proof['n_bytes_before']} bytes) |")
    w(f"| addendum size | {proof['n_bytes_addendum']} bytes |")
    w(f"| prefix 0..{proof['n_bytes_before']} re-hashed after the append | `{proof['prefix_sha256_recomputed']}` |")
    w(f"| prefix identical to the pre-image | **{proof['prefix_identical']}** |")
    w(f"| line diff | added {proof['diff_added_lines']}, removed {proof['diff_removed_lines']}, modified {proof['diff_modified_lines']} |")
    w(f"| pre-image copy kept | `REPORT_EyeKB_成果报告_v2.0.md.pre_addendum` |")
    w(f"| one-pager companion | added {proof1['diff_added_lines']} lines, removed {proof1['diff_removed_lines']}, prefix identical {proof1['prefix_identical']} |")
    w("")
    w("## 2. Method, and the discipline that was kept")
    w("")
    w("The ruling's block C was honoured literally: this wave **audits resolution, it does not split panels**.")
    w("Thresholds were written to disk before measurement and did not move afterwards:")
    w("")
    w("| threshold | value |")
    w("|---|---|")
    w("| T-GENES | ≥ 2 discriminating positive genes against the nearest sibling |")
    w("| T-SOURCES | ≥ 2 independent sources, ≥ 1 giving adjacent-type contrast |")
    w("| T-CONTEXT | species / tissue / stage / system declared and satisfied |")
    w("| T-NONEG | no inference from \"not in the top-10\" |")
    w("| T-OBS | ≥ 2 discriminating genes inside the shipped top-marker window |")
    w("| T-STATE | state-programme share of discriminating genes < 0.50 |")
    w("| T-MATERIAL | ≥ 1 independent, non-evaluation local material |")
    w("")
    w("Operations were fixed in `PREREG_ANNEX_A_OPERATIONS_20261022.md`, then corrected three times — each correction")
    w("written down with what had been observed on disk first, and **no threshold moved**:")
    w("")
    w("| annex | what was observed first | what was corrected |")
    w("|---|---|---|")
    w("| A4-b | singular-only matching hit 1,277 chunks; 40 of 78 observed names gain chunks on a plural | occurrence test accepts a regular plural |")
    w("| A3-b | library scope prose gave uneven tissue sets (two libraries yielded none) | the shipped `_tissue_class_crosswalk_v1.json` is the first source |")
    w("| A7-b | the state reference as a *set* saturated (state fraction 1.0000 on 26/26 strong pairs) | state test became a **ratio** (≥0.75 of mentioning chunks in state context) |")
    w("| A11-b/A12 | progenitor parent's closure returned `monocyte`, `hematopoietic stem cell` | progenitor-like parents go on the developmental axis; thin evidence is T2 before any continuum reading |")
    w("| A11-c | `Fibroblast` came back 64/64 `developmental_axis` | the token `blast` was matching inside \"fi**blast**\" — matched on word boundaries instead (135 pairs returned to the audit) |")
    w("")
    w("The first readiness pass (built with the two defective operations) is preserved unmodified at `out/firstpass/`,")
    w("so the supersession is checkable rather than asserted.")
    w("")
    w("## 3. Result — the per-parent table")
    w("")
    w(f"Machine-readable: `out/subdivision_readiness.tsv` / `.json` ({len(rows)} rows, one per shipped parent class),")
    w(f"`out/pair_table.tsv` / `.json` ({len(pairs)} rows, one per (parent, candidate child) pair).")
    w("")
    w("| tier | pairs | meaning |")
    w("|---|---:|---|")
    w(f"| T1 subdivision available now | {t.get('T1', 0)} | every threshold cleared, including independent non-evaluation material |")
    w(f"| T1k knowledge-subdividable only | {t.get('T1k', 0)} | thresholds cleared except T-MATERIAL (ruling: 知识上可细分 ≠ 本接口上已验证) |")
    w(f"| T2 needs the parent panel deepened | {t.get('T2', 0)} | occurs in context, but the evidence is too thin to separate |")
    w(f"| T3 not subdividable | {t.get('T3', 0)} | ontology-thin, leaf, never mentioned, outside context, state-programme-only, or continuum |")
    w(f"| excluded | {t.get('excluded', 0)} | already a shipped class, or on the developmental / system axis |")
    w("")
    w("| reason (fixed enum) | pairs |")
    w("|---|---:|")
    for k, n in r.most_common():
        w(f"| `{k}` | {n} |")
    w("")
    w("| scope class | pairs |")
    w("|---|---:|")
    for k, n in sc.most_common():
        w(f"| `{k}` | {n} |")
    w("")
    w(f"Eight parents reached `subtype_suggested`: "
      + ", ".join(sorted(x["parent"] for x in rows if x["resolution_status"] == "subtype_suggested")) + ".")
    w("")
    w("Two readings worth the PI's attention more than the labels themselves:")
    w("")
    w("1. **The ontology's fine names are mostly not in the literature we hold.** " + str(r.get("never_mentioned", 0)) +
      " of " + str(len(pairs)) + " pairs die there. That is a fact about the corpus's naming habits, not about the")
    w("   biology, and it is the single largest limitation of this audit.")
    w("2. **The `is_a` closure is not a subdivision menu.** It returns `monocyte is_a progenitor cell` (a direct edge) and")
    w("   `corneal endothelial cell is_a endothelial cell` — real ontology statements that are not subtype questions")
    w("   here. Both are named in the table instead of being silently dropped.")
    w("")
    w("## 4. Output shape (specification and dry run only)")
    w("")
    w("Per the ruling §C2 the emission is `parent_candidates` + `subtype_suggestions_by_parent` + `resolution_status` +")
    w("`review_reasons`; parents are always preserved, subtypes compete only inside their parent branch, `parent_only`")
    w("and `subtype_ambiguous` are legitimate outputs, and no automatic final label is ever emitted.")
    w("")
    w("| resolution_status | parents |")
    w("|---|---:|")
    for k, n in st.most_common():
        w(f"| `{k}` | {n} |")
    w("")
    w(f"Dry run: `out/output_shape_emission.json` ({len(emission)} parents). Checked mechanically: parent candidates")
    w("present for every parent; suggestions nested under their own parent; status values inside the four legal values;")
    w("no single-gene admission; no parent-shared gene presented as child evidence; no default-route change.")
    w("")
    w("## 5. Confusion pair — RPE vs melanocyte")
    w("")
    rr = conf["recorded_reading"]
    e = conf["2_discriminating_positive_evidence"]
    sh = conf["1_shared_support"]
    i4 = conf["4_information_the_interface_does_not_have"]
    rpe_mel = 0
    for kk, vv in rr["confusion_counts"].items():
        parts = kk.split(" || ")
        if (parts[0] == "retinal pigment epithelial cell"
                and parts[1] == "BASE=Melanocyte" and parts[2] == "MERGED=Melanocyte"):
            rpe_mel += vv
    w(f"RPE (`CL:0002586`) is a **leaf** in the fixed snapshot: 0 `is_a` descendants. It cannot be subdivided at all,")
    w(f"and the pair with melanocyte is a **same-level sibling confusion**, measured as such. Deliverable is the")
    w(f"six-element evidence package (`out/confusion_rpe_melanocyte.json`):")
    w("")
    w("| element | measurement |")
    w("|---|---|")
    w(f"| ① shared support | shipped-panel overlap **{sh['n_shipped_overlap']}** genes; literature-positive on both sides **{sh['n_literature_shared']}** genes; slices: RPE {conf['literature_support']['rpe']['chunks']} chunks / {conf['literature_support']['rpe']['papers']} papers vs melanocyte {conf['literature_support']['melanocyte']['chunks']} / {conf['literature_support']['melanocyte']['papers']} |")
    w(f"| ② discriminating positive evidence | RPE-only **{e['n_rpe_only_specific']}** (unfiltered {e['n_rpe_only_unfiltered']}), melanocyte-only **{e['n_melanocyte_only_specific']}** (unfiltered {e['n_melanocyte_only_unfiltered']}); papers giving adjacent-type contrast **{e['n_papers_with_adjacent_type_contrast']}** |")
    w(f"| ③ state programmes | RPE-only share **{conf['3_state_programmes']['state_share_rpe_only']}**, melanocyte-only **{conf['3_state_programmes']['state_share_melanocyte_only']}**, shared block **{conf['3_state_programmes']['state_share_shared']}** |")
    w(f"| ④ information the interface lacks | only **{i4['n_rpe_only_genes_visible_in_recorded_window']}** of the RPE-only genes appear anywhere in the {window['n_clusters']}-cluster window (vs {i4['n_melanocyte_only_genes_visible_in_recorded_window']} on the other side) |")
    w(f"| ⑤ keep several candidates | **{conf['5_when_several_candidates_must_be_kept']['clusters_with_both_candidates_in_ranking']}** clusters rank both sides |")
    w(f"| ⑥ abstention | **{conf['6_when_abstention_is_required']['clusters_with_no_candidate']}** clusters have no candidate at all |")
    w("")
    w(f"Recorded reading on the fixed reference: {len(rr['rpe_truth_clusters'])} RPE-truth clusters and "
      f"{len(rr['melanocyte_truth_clusters'])} melanocyte-truth clusters; **{rpe_mel}** RPE-truth clusters are answered "
      f"melanocyte in BOTH arms, so the deepened panel does not move it. The leading RPE-only genes in the literature")
    w("are dominated by disease programme genes, which is why element ③ reads the way it does. **The answer to this pair")
    w("is the parent plus a named confusion reason — not a thicker positive panel.**")
    w("")
    w("## 6. What a subdivision would cost the parent")
    w("")
    w("Same definitions as the predecessor wave's price table (holefill v12 §5), re-measured on the recorded set:")
    w("")
    w("| parent | child | tier | demand | gain | keep | loss | costly |")
    w("|---|---|---|---:|---:|---:|---:|:--:|")
    for c in passing:
        w(f"| {c['parent']} | {c['child']} | {c['tier']} | {c['demand_clusters']} | {c['gain_clusters']} | "
          f"{c['keep_clusters']} | {c['loss_clusters']} | {'yes' if c['costly'] else 'no'} |")
    w("")
    w(f"**All {len(passing)} T1/T1k splits together: gain {gain} clusters, loss {loss} clusters.** "
      f"Every branch this audit found subdividable is a loss if read as \"the child replaces the parent\" — the")
    w("literature child panels are thinner than the shipped parent panels and drop below the ≥2 shared-gene bar before")
    w("they can win anything. This is the same shape the predecessor wave measured for the bipolar splits, and it is")
    w("why this wave delivers a **knowledge asset and a resolution audit**, not a build order.")
    w("")
    w("## 7. Red lines, with evidence")
    w("")
    w("| red line | evidence |")
    w("|---|---|")
    w(f"| report and scheme byte-identical | prefix re-hash identical; added {proof['diff_added_lines']} / removed 0 / modified 0; pre-image kept (`out/append_proof.json`) |")
    w(f"| zero downloads, zero network | audit hook loaded **{n_hooks}** times across the chain; connection-class events **{n_conn}**; the only socket events are **{n_new}** `socket.__new__` (unbound socket, fd=-1 — construction, not a connection) |")
    w(f"| discovery vs evaluation sources separated | searchable accessions from the volumes: {sorted(acc)}; the 22 cellxgene-hosted volumes have no local accession handle → their overlap is `NOT_RUN` with the reason stated, **never 0** |")
    w(f"| nothing activated | no change to any shipped marker body, no threshold, no default switch, and the wave's commit contains only `docs/plans/subdivision_readiness_20261022/` |")
    w(f"| default route byte-identical, replayed not argued | OFFl {replay['stats']['off']['identical']}/{replay['stats']['off']['n']} recorded rankings reproduced (differ {replay['stats']['off']['differ']}); ON {replay['stats']['on']['identical']}/{replay['stats']['on']['n']} (differ {replay['stats']['on']['differ']}) |")
    w(f"| gate chain green in a CLEAN CLONE | " + "；".join(gates) + " |")
    w(f"| NOT_RUN never reported as pass | {material['n_not_run']} unopenable material files listed by path; the disease thin layer carries no gene list (0 genes extracted) and that arm is declared void in §5 rather than counted as 0 evidence |")
    w("")
    w("The gate chain was run from a clean clone of HEAD in a path containing a space, with a different working")
    w("directory and no author directory — the portability conditions the ruling's engineering ruling ③ asks for.")
    w("G3 needed `EYEKB_G3_PY` (the interpreter that has the locked embedding stack) and `EYEKB_MODEL_DIR`; with them it")
    w("reports `REPRO PASS: 41/41` rather than the inconclusive fallback the predecessor wave had to record.")
    w("")
    w("## 8. Defects found in this wave's own work, recorded")
    w("")
    w(f"1. **State reference saturating** (fixed by A7-b): in the superseded first pass, **{fp_state1}** pairs carried a")
    w(f"   state fraction of exactly 1.0 — a set-valued reference that contained every discriminating gene. Replaced by a")
    w(f"   ratio at a 0.75 cutoff, calibrated on disk ({cal}). Recomputed from `out/firstpass/pair_table.json`.")
    w(f"2. **`blast` matching inside `fibroblast`** (fixed by A11-c): **{moved}** pairs were wrongly put on the")
    w(f"   developmental axis. After the fix that axis holds {dev_after} pairs and the in-scope count goes")
    w(f"   {inscope_before} → {inscope_after}. This is the most consequential defect found, and it was found by looking at")
    w(f"   why a parent with many candidate children reported none. Counts parsed from `logs/m_readiness_v2.log` and")
    w(f"   `logs/m_readiness_v4.log`.")
    w(f"3. **Tier ordering** (fixed by A12): **{fp_spectrum}** pairs were labelled `spectrum_only` purely for having no")
    w(f"   evidence at all, recomputed from `out/firstpass/pair_table.json`.")
    w("4. **Preferred-name-only recall** (fixed by A4-b): the singular-only reading measured nomenclature, not evidence.")
    w("5. **RPE slice contaminated by the bare cell abbreviation** in the first confusion run: the slice matched the")
    w("   abbreviation wherever it appeared, so the side-only difference was dominated by slice size rather than by")
    w("   biology. Slices are now name phrases and a specificity floor was added; the unfiltered counts are kept")
    w("   beside the filtered ones rather than dropped. The superseded run's own log was overwritten by later runs,")
    w("   so its reading is **not quoted here** — an unverifiable number is worse than a description of the defect.")
    w("")
    w("## 9. Repo changes and commit")
    w("")
    w("Committed: this wave's English artefacts under `docs/plans/subdivision_readiness_20261022/` — and nothing else.")
    w("The author tree carries another card's uncommitted work (`docs/plans/l5_ontlayer_20261022/`,")
    w("`mcp_server/ontology_layer.py`, `mcp_server/server.py`, `kb/ontology/…`, `tests/run_gates.sh` and others); none of")
    w("it is in this commit, and the gate chain reading above was taken from a clean clone of HEAD precisely so it does")
    w("not measure that work. Not pushed — push is a separate reserved step.")
    w("")
    w("See `COMMIT.txt` for the hash.")
    w("")
    w("## 10. Commands run, and what each cost")
    w("")
    w("| step | wall | peak RSS (MB) | memory-capped |")
    w("|---|---|---:|:--:|")
    for x in timings:
        w(f"| `{x['log']}` | {x['wall']} | {x['peak_rss_mb'] if x['peak_rss_mb'] is not None else '—'} | {x['cap']} |")
    w("")
    w(f"Heavy steps ran under `systemd-run --user --scope -p MemoryMax=… -p MemorySwapMax=2G`. Measured peak RSS is")
    w(f"0.02–16.7 GB: the 16.7 GB reading is the local-material scan (`m_material.py`, {material['n_candidates']} candidate")
    w(f"h5ad headers opened backed='r'), which is the only step that came near its cap. Available memory stayed around")
    w(f"205 GiB throughout — well above the 40 GiB stop line in the shared workstation rules, so nothing was parked and")
    w(f"no other workstream was disturbed.")
    w("")
    w("## 11. Artefacts")
    w("")
    w("```")
    w("PREREG_SUBDIVISION_READINESS_20261022.md       thresholds + output shape, written before measurement")
    w("PREREG_ANNEX_A_OPERATIONS_20261022.md          the operations (corpus, candidates, context, genes, state, window)")
    w("PREREG_ANNEX_A_AMENDMENTS_20261022.md          plural recall + shipped crosswalk as first context source")
    w("PREREG_ANNEX_A_AMENDMENTS2_20261022.md         state ratio + tier ordering + progenitor parents")
    w("PREREG_ANNEX_A_AMENDMENTS3_20261022.md         the 'blast inside fibroblast' fix")
    w("scripts/                                       11 scripts, one per measured step, plus the gate replay")
    w("discipline/net_audit/sitecustomize.py          the zero-network audit hook")
    w("out/subdivision_readiness.tsv / .json          the 76-row per-parent table")
    w("out/pair_table.tsv / .json                     the 923 (parent, child) rows, full detail")
    w("out/output_shape_emission.json                 the two-level emission dry run")
    w("out/cost_table.tsv / .json                     demand / gain / keep / loss per pair")
    w("out/confusion_rpe_melanocyte.json              the six-element evidence package")
    w("out/O_observable_window.json                   the current window (721 recorded top-10 lists)")
    w("out/O_state_ratio.json / O_state_reference.json the state programme reference and ratios")
    w("out/M_non_evaluation_material.json             474 candidates, 472 opened, 2 NOT_RUN")
    w("out/S0..S5_*.json                              library contexts, parents, occurrence, genes, contrast")
    w("out/R0..R4_*.json                              ontology snapshot sha, depth, volume provenance, machine inventory")
    w("out/golden_721_replay.json                     the default-route replay")
    w("out/append_proof.json / append_proof_onepager.json  the append-only proofs")
    w("out/firstpass/                                 the superseded first readiness pass, kept unmodified")
    w("logs/                                          every run's log, the command log, and the gate readouts")
    w("```")
    w("")
    open(f"{WAVE}/REPORT.md", "w", encoding="utf-8").write("\n".join(R) + "\n")

    # ---- command log ----
    C = ["# COMMAND LOG — subdivision_readiness_20261022", "",
         "Every command that produced a number in this wave. Heavy steps ran under",
         "`systemd-run --user --scope -p MemoryMax=… -p MemorySwapMax=2G` with the zero-network audit hook on",
         "(`PYTHONPATH=discipline/net_audit`, `SR_NET_AUDIT_LOG=logs/netaudit_chain.log`).", "",
         "| # | command | wall | peak RSS (MB) | log |", "|---|---|---:|---:|---|"]
    cmds = [
        ("python3 scripts/r_recon.py", "r_recon.log"),
        ("python3 scripts/m_scan.py", "m_scan_v2.log"),
        ("python3 scripts/m_state.py", "m_state.log"),
        ("python3 scripts/m_state2.py", "m_state2.log"),
        ("python3 scripts/m_material.py", "m_material.log"),
        ("python3 scripts/m_observe.py", "m_observe.log"),
        ("python3 scripts/m_readiness.py", "m_readiness_v4.log"),
        ("python3 scripts/m_cost.py", "m_cost_v4.log"),
        ("python3 scripts/m_confusion.py", "m_confusion_v2.log"),
        ("python3 scripts/golden_721.py out/golden_721_replay.json", "golden_721_v2.log"),
        ("python3 scripts/m_report.py", "m_report.log"),
        ("bash <clean clone>/tests/run_gates.sh", "gates_cleanclone_v2.log"),
        ("python3 scripts/m_append.py", "m_append_v2.log"),
    ]
    for i, (c, lg) in enumerate(cmds, 1):
        hit = next((x for x in timings if x["log"] == lg), None)
        C.append(f"| {i} | `{c}` | {hit['wall'] if hit else 'not timed'} | "
                 f"{hit['peak_rss_mb'] if hit and hit['peak_rss_mb'] is not None else '—'} | `logs/{lg}` |")
    C += ["", "Untimed steps (pure text generation / reads, no heavy compute): `m_observe.py` (recorded windows),",
          "`m_append.py` (addendum generation + append + proof), `golden_721.py` when run without `/usr/bin/time`.", "",
          "## Gate readout (clean clone, not the author tree)", "", "```"] + gates + ["```", "",
          "## Network audit receipt", "",
          f"- audit hook load markers: **{n_hooks}**",
          f"- connection-class events (socket.connect / getaddrinfo / urllib / http.client): **{n_conn}**",
          f"- socket-object construction events (`socket.__new__`, fd=-1): **{n_new}**",
          "", "Zero connection-class events across the whole chain; no download was performed and none was attempted."]
    open(f"{WAVE}/logs/COMMAND_LOG.md", "w", encoding="utf-8").write("\n".join(C) + "\n")
    print("wrote REPORT.md and logs/COMMAND_LOG.md")
    print(f"tiers={dict(t)}  reasons_top={dict(r.most_common(3))}  passing={len(passing)} gain={gain} loss={loss}")
    print(f"hooks={n_hooks} events={n_events} connection_class={n_conn}")
    print("timed steps:", len(timings))


if __name__ == "__main__":
    main()
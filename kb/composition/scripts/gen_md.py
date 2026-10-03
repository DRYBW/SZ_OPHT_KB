#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_md.py — renders human-readable md from EXPECTED_COMPOSITION_v0.json + selfcheck artifacts (v0, 2026-09-28)"""
import json, pathlib, csv, collections
KB=pathlib.Path("<EYEKB>/kb/composition")
face=json.load(open(KB/"EXPECTED_COMPOSITION_v0.json"))
summ=json.load(open(KB/"selfcheck/summary.json"))
flags=list(csv.DictReader(open(KB/"selfcheck/flags.tsv"),delimiter="\t"))

# ---------- EXPECTED_COMPOSITION_v0.md
L=["# EXPECTED_COMPOSITION_v0 — Normal Adult Eye Composition Prior Surface (Human-readable Version)",
"",
f"> Generated {face['generated']} | Card {face['card']} | Authority: {face['authority']}",
">",
"> **⛔ Wiring status: `"+face["wiring"]+"`** — any runtime consumption on this facet (MCP/baselines/scoring/gating) requires a separate card and approval, PI decision.",
"",
"## 0. Positioning and Scope (Read This First)",
f"- Face semantics: **{face['denominator_semantics']}**",
"- Evidence level:" + "；".join(f"{k}={v}" for k,v in face["evidence_grades"].items()),
"- Lineage declaration (anti-circularity clause):" + face["lineage_declaration"],
"- Interval mechanical rules (pre-registered):" + face["interval_rule"],
"- Scope:" + json.dumps(face["scope"],ensure_ascii=False),
"",]
for page,p in face["pages"].items():
    L.append(f"## 1.{list(face['pages']).index(page)+1} page: {page}")
    L.append(f"- registry anchor: {p['registry_anchor']}")
    L.append(f"- donor-level master record: {p['donor_main']}")
    L.append("")
    L.append("| Cell Type | Low % | Mid % | High % | Evidence | B Status | Row-wise PMID | Donor-level Measured (median/iqr/range) |")
    L.append("|---|---|---|---|---|---|---|---|")
    for r in p["rows"]:
        am=r.get("a_measured") or {}
        meas=f"{am.get('donor_median_pct','–')} / {am.get('donor_iqr_pct','–')} / {am.get('donor_range_pct','–')}" if am else "–"
        lo,mi,hi=(r['low_pct'],r['mid_pct'],r['high_pct'])
        L.append(f"| {r['cell_type']} ({r['label_cn']}) | {lo if lo is not None else 'null'} | {mi if mi is not None else 'null'} | {hi if hi is not None else 'null'} | {r['evidence']} | {r['grade_b_status']} | {', '.join(r['pmids']) or '—'} | {meas} |")
    L.append("")
    L.append("### Row-wise Literature Anchors (On-disk ingested literature original sentences, B-level locatable)")
    for r in p["rows"]:
        if not r["literature_anchors"]: continue
        L.append(f"- **{r['cell_type']}**")
        for a in r["literature_anchors"]:
            q=("“"+a["quote"]+"”") if a.get("quote") else "(Bibliographic anchor; no verbatim text)"
            L.append(f"  - PMID {a['pmid']} [{a['kind']}] {q} — {a['note']}")
    L.append("")
L.append("## 2. PMID Bibliographic Triple-Criteria Self-Check")
v=face["pmid_verification"]
L.append(f"- Criteria: {v['criteria']}; total PMIDs {v['pmids_total']}, non-compliant ledger rows {v['ledger_fail_rows']}")
L.append("- Itemized details in `ledgers/PROVENANCE_COMP_v0.tsv`")
L.append("")
L.append("## 3. Known Limitations and Caveats")
for c in face["caveats"]: L.append(f"- {c}")
if face.get("rows_missing_pmid"):
    L.append(f"- Rows missing line-by-line PMID (pre-activation obligation OB-1): {', '.join(face['rows_missing_pmid'])}")
for ob in face.get("activation_obligations",[]): L.append(f"- Activation obligation {ob}")
L.append("- Disease-state proportions not built (PDR annotation unreliable scope maintained); developmental axis (fetal/organoid) values folded out, citation records retained.")
L.append("- 'INTAKE ledger 392 entries' executed per task specification original text, incorporated into 'on-disk ingested RAG literature (papers.jsonl v2.4.2) metadata verifiable' scope (deviation statement: no literature ledger file named INTAKE with exactly 392 entries found on disk; methods-scrna index page has exactly 392 papers, included as one of the verifiable sets).")
L.append("")
L.append("## 4. Self-check and Activation")
L.append("- Self-check flag report: `COMP_SELFFLAG_20260928.md` (outputs only flag list and proportion distribution, no erroneous annotation conclusions).")
L.append("- This face defaults OFF; wiring it into the interpretation layer (unexpected flagger) is a separate-card, separate-batch item.")
(KB/"EXPECTED_COMPOSITION_v0.md").write_text("\n".join(L),encoding="utf-8")

# ---------- COMP_SELFFLAG_20260928.md
R=["# COMP_SELFFLAG_20260928 — EXPECTED_COMPOSITION_v0 self-check flag report (read-only, outputs flags not conclusions)",
"",
f"> Card {face['card']} | Input: `EXPECTED_COMPOSITION_v0.json` × on-disk frozen artifacts (kb/baselines, plans/evalset frozen items, demo_gse165784 v2 consensus draft table)",
"> **⛔ This face is not wired. Flags = prompts for re-review, not annotation errors; wiring and activation require separate cards and approval (PI decision).**",
"",
"## 0. Method",
"- Reconciliation targets: Ground truth composition of each member in the evaluation volume (Q1–Q9, ground truth = author-level/portal annotations or mapped_10class; not re-annotation by own clustering) + demo GSE165784 v2 Track B consensus annotation draft (disease material, demonstrating gate behavior).",
"- Flag rules: pct < low → BELOW; pct > high → ABOVE; off-face identities (T / macrophage / fibroblast / progenitor …) → off_face_identity disclosure row; the proportion denominator is all cells of the dataset.",
"- Built-in reverse quality check clause: If flagged type proportion >20% in healthy public sets → honestly report \"face too narrow = issue with the face definition, not the data\".",
"- Out-of-domain axes (excluded from reverse quality check denominator): Q7 mouse (species axis), Q8 fetal (developmental axis), Q6 (same construction source as ocular surface = circular reference), Q9 demo (disease surgical material, usage_scope prohibits use as standard control).",
"",
"## 1. Summary Flag Rate",
"",
"| Dataset | Face | Cell Count | Flagged Rows/Face Rows | Flag Rate | Reverse Quality Check |",
"|---|---|---|---|---|---|"]
for s in summ:
    R.append(f"| {s['dataset']} | {s['page']} | {s['total_cells']:,} | {s['n_flagged']}/{s['face_rows']} | {s['flag_pct']}% | {s['reverseQC']} |")
R+=["",
"## 2. Flag Details (Row-by-Row Dataset × Cell Type)","",
"| Dataset | Row | Observed % | Surface Interval [Low, High] | Status |","|---|---|---|---|---|"]
byd=collections.defaultdict(list)
for f in flags: byd[f["dataset"]].append(f)
for ds,rows in byd.items():
    for f in rows:
        iv=f"[{f['low']},{f['high']}]" if f["low"] not in (None,"") else "null (disclosure row)"
        R.append(f"| {ds} | {f['row']} | {f['pct']} | {iv} | {f['status']} |")
R+=["","## 3. Reverse Quality Control Verification (Built-in Clauses)",""]
trig=[s for s in summ if s["reverseQC"].startswith("TRIGGER")]
cnt=sum(1 for s in summ if s["in_scope"]=="yes") if False else sum(1 for s in summ if s["dataset"] in ("Q1_Lukowski2019","Q2_GSE155288","Q3","Q4","Q5b"))
R+=[f"- Healthy public sets included in reverse quality control: Q1/Q2/Q3/Q4/Q5b (total {cnt}, human, normal, adult retina).",
    f"- **Trigger (>20% of types flagged): {len(trig)} items —— " + "; ".join(f"{s['dataset']} {s['flag_pct']}%" for s in trig) + "**" if trig else "- No trigger.",
    "- Reading (factual, not conclusion): Per built-in clauses, this first indicates that the **v0 interval is too narrow for cross-platform/cross-sampling-region/sorting designs**, a scope issue rather than a data issue. Specific attributions: Q1/Q2 = foveal sampling + scRNA cell suspension (main face archive uses snRNA nuclear suspension; Astra T2 has declared the two metrics are not directly comparable); Q3/Q4 = Macroglia signature splitting criteria + CD73/CD90 sorting design elevating BC/MG and suppressing Rods; Q5b shares origin with main face archive (HRCA internal composition), flag rate 0 represents an **upper bound of circular self-validation, not good generalization**.",
    "- Disposition Recommendation (not auto-approved; submit to PI alongside text when activating separate cards/approvals): Stratify v1 intervals by suspension_type (nuclear/cell) and sampling region (fovea/peripheral/whole retina/sorted); or define the 'prior surface' as a conditional surface with design exemptions.",
    "",
"## 4. Off-Surface Identity Disclosure (Non-flagged, informational)","",
"### Q8 Fetal (Out-of-Domain Axis Behavior Record)",
"- retinal progenitor cell is the largest class at 73,569/226,506=32.5% (denominator re-reviewed = def.classes total sum = full file) — The adult surface lacks a progenitor row, so all entries fall into off_face_identity; expected behavior of developmental material against the adult surface.",
"",
"### Top Off-Surface Identity Rows per Dataset"]
for ds,rows in byd.items():
    offs=[f for f in rows if f["status"]=="off_face_identity"][:8]
    if offs: R.append(f"- **{ds}**: "+ "; ".join(f"{f['row'].split('::',1)[1]} {f['pct']}%" for f in offs))
R+=["",
"## 5. Declaration",
"- This report outputs only the flag list and proportion distribution; flags ≠ annotation errors; no existing annotations are judged correct or incorrect based on this report.",
"- This face is unwired, default OFF; wiring and activation require a separate task card and approval batch.",
"- Reproduction: `python3 scripts/build_expected_composition_v0.py && python3 scripts/selfcheck_comp_v0.py && python3 scripts/gen_md.py` (logs logs/selfcheck_run.log).",
""]
(KB/"COMP_SELFFLAG_20260928.md").write_text("\n".join(R),encoding="utf-8")
print("md written:", (KB/'EXPECTED_COMPOSITION_v0.md').stat().st_size, (KB/'COMP_SELFFLAG_20260928.md').stat().st_size)

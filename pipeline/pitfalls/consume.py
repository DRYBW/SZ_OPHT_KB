#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""consume.py — shadow-mode consumption of known-issues claims (page pulls + risk flags); WIRE-P1 deliverable 3 (REV-1 finalized).

Consumption semantics (astra T4/T5/T6 anchoring, take stricter; overrides qwen proxy-audit version PITFALL_OVERRIDE):
  - **shadow: Record flags and re-review requirements only; automatic relabeling/downgrading/vote overriding is prohibited.**
    Reading revisions still follow the original three independent reading votes and S0 hard gate. This module does not generate suggested_grade_cap (this column is deprecated).
  - Page pull: (species, tissue) → full cells page + resolution of citation pointers on species/tissue/pattern pages
    → Merge applicable claim sets for this cell.
  - Visibility firewall (T6): entries with answer_dependency≠none (=blind_safe=false),
    On the **pre-annotated human surface** (evidence_report.md header + decisions_template.csv)
    Output only structured flags (claim_id + risk_level + review_required),
    failure_mode/mitigation free text is **not injected** (left to post_decision/curator surface);
    general methodological entries with blind_safe=true may include short mitigation rules.
  - This module is invoked by run_pipeline only during the reading completion phase; reading evidence JSON/feed items/blind review digest
    Do not import this module (tests/test_s0_gate.py T4 AST-level machine check + firewall grep).

Audit: write to shadow_flags.jsonl on every risk flag hit
  {ts, run_id, claim_id, cluster_id, risk_level, evidence_source_type,
   answer_dependency, blind_safe, action:"risk_flag_only(no_auto_override)"}。
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGES = HERE / "pages"

# Class-anchor tokens (prefix match) → controlled class names. Variable names avoid the *TOKENS keyword family (gateway sanitization trap, empirically verified 2026-09-29).
def _anchor_vocab():
    return {
        "Endo": ["endo", "endothel"], "Micro": ["microglia", "micro"],
        "MG": ["müller glia", "muller glia", "müller", "muller", "mg"],
        "Astro": ["astro"], "Rod": ["rod"], "Cone": ["cone"],
        "BC": ["bipolar", "bc"], "RPE": ["rpe", "pigment epithel"],
        "RGC": ["ganglion", "rgc"], "Pericyte": ["pericyte"],
        "SMC": ["smooth muscle", "smc"], "Keratocytes": ["keratocyt"],
        "Fibroblast": ["fibroblast"], "Proliferating": ["proliferat", "cell cycle", "mki67"],
        "Erythroid": ["erythro", "rbc"], "T_cell": ["t cell", "t-cell", "lymphoid"],
        "Mac_Tissue": ["mac", "macrophage", "myeloid", "mono"],
        "Epithelium_generic": ["epithel"],
    }


CLASS_MAP_VOCAB = _anchor_vocab()

# The applies_to_classes field in claims does not conform to the atomic contract (astra schema lacks such anchor fields);
# This batch is a consumer-side enhancement: infers class anchors based on failure_mode keywords from origin, used only for **risk flag hits**,
# Never drives adjudication changes. Hit logic is conservative: flags are raised only when candidate class names directly correspond to classes mentioned in the failure mode text.
_ANCHOR_HINTS = {
    "endothel": ["Endo"], "Endothelium": ["Endo"], "microglia": ["Micro"], "Microglia": ["Micro"],
    "müller": ["MG"], "Astrocyte": ["Astro"], "astrocyte": ["Astro"],
    "Rod": ["Rod"], "rod": ["Rod"], "Bipolar": ["BC"], "bipolar": ["BC"],
    "rpe": ["RPE"], "Proliferative": ["Proliferating"], "proliferat": ["Proliferating"],
    "Myeloid lineage": ["Mac_Tissue", "Micro"], "myeloid": ["Mac_Tissue", "Micro"],
    "Blood": ["Erythroid"], "blood": ["Erythroid"], "Epithelium": ["Epithelium_generic"],
    "epithel": ["Epithelium_generic"], "Pericytes": ["Pericyte"], "pericyte": ["Pericyte"],
    "granularity": ["MG", "Astro"], "ambient": ["Rod", "BC"],
}


def _claim_class_anchors(claim):
    fm = (claim.get("failure_mode", "") + " " + claim.get("observable_signature", "")).lower()
    out = set()
    for kw, cls in _ANCHOR_HINTS.items():
        if kw.lower() in fm:
            out.update(cls)
    return sorted(out)


def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


def class_match(candidate, applies):
    if not applies or not candidate:
        return False
    low = _norm(candidate)
    for a in applies:
        for tok in CLASS_MAP_VOCAB.get(a, [a.lower()]):
            t = _norm(tok)
            if t and re.search(r"\b" + re.escape(t), low):
                return True
    return False


# Dictionary organization name → canonical page coordinates (COORDINATE_TAXONOMY_v1.md §6, C6/C7 approval; zero changes to service dictionary)
PULL_TISSUE_ALIAS = {"fibrovascular_membrane": "fibrovascular_membrane",
                     "fibrovascular membrane": "fibrovascular_membrane",
                     "pdr_membrane": "fibrovascular_membrane",
                     "lacrimal": "lacrimal_gland"}


def _load(fname):
    p = PAGES / fname
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def pull_claims(species, tissue):
    """Return (full set of applicable claims for this cell, list of dangling ref_ids). Full claim set = entries from all visible pages ∪ resolved cited pointers."""
    tissue = PULL_TISSUE_ALIAS.get(tissue, tissue)
    # Global claim index (for pointer resolution)
    gidx = {}
    for pg in (PAGES.rglob("*.json")):
        if pg.name in ("INDEX.json", "EXCLUSIONS.json"):
            continue
        d = json.loads(pg.read_text(encoding="utf-8"))
        for e in d.get("entries") or []:
            if "claim_id" in e:
                gidx.setdefault(e["claim_id"], e)
    wanted = [f"cells/{species}__{tissue}.json", f"species/{species}.json",
              f"tissue/{tissue}.json"]
    seen, out, dangling = set(), [], []
    for w in wanted:
        pg = _load(w)
        if not pg:
            continue
        for e in pg.get("entries") or []:
            if e["claim_id"] not in seen:
                seen.add(e["claim_id"])
                out.append(e)
        for pt in pg.get("pointers") or []:
            rid = pt["ref_id"]
            if rid in seen:
                continue
            if rid in gidx:
                seen.add(rid)
                c = dict(gidx[rid])
                c["_cited_from"] = w
                out.append(c)
            else:
                dangling.append((w, rid))
    out.sort(key=lambda x: x["claim_id"])
    return out, dangling


def _pre_annotation_line(c):
    """Pre-annotated short human lexical surface lines. blind_safe=false structures flags only, no free text."""
    if c.get("blind_safe", True):
        mit = c.get("mitigation") or c.get("failure_mode", "")
        return (f"- `{c['claim_id']}` [{c['evidence_source_type']}/"
                f"risk={c['risk_level']}] {mit}")
    return (f"- `{c['claim_id']}` [risk={c['risk_level']}/"
            f"review_required=manual_post_decision] (open after free-text reading)")


def attention_section(species, tissue, s0_meta=None):
    claims, dangling = pull_claims(species, tissue)
    pub = [c for c in claims if c.get("blind_safe", True)]
    red = [c for c in claims if not c.get("blind_safe", True)]
    lines = ["## This-slot attention list (known-issues shadow: log flags only, do not alter readings; no free text in this segment)", "",
             f"- Judgment coordinates: species=`{species}`, tissue=`{tissue}`"
             + (f"(Source `{(s0_meta or {}).get('source', 'manual')}`"
                + (", override audit trail: s0_overridden_by_user"
                   if (s0_meta or {}).get("overridden_by_user") else "") + "）"
                if s0_meta else ""),
             f"- Applicable claims: {len(claims)} entries (blind-evaluation safe {len(pub)} / open after reading {len(red)})."
             "This segment contains only structured flags (astra conservative default: no free-text known-issues before blind review);"
             "Short rules and sources see `shadow_attention.json` (human-facing after reading),"
             "Automatic naming/downgrade change always = 0.", "",
             "| claim_id | risk | source_type | blind_safe | re-review requirement |",
             "|---|---|---|---|---|"]
    for c in claims:
        lines.append(f"| `{c['claim_id']}` | {c['risk_level']} | "
                     f"{c['evidence_source_type']} | {str(c['blind_safe']).lower()} | "
                     + ("Manual re-review after reading (free-text post_decision)"
                        if not c["blind_safe"] else "Optional re-review (general methodological short rules in machine-readable file)")
                     + " |")
    lines.append("")
    machine = {"schema": "eyekb-shadow-attention/1.0", "species": species, "tissue": tissue,
               "mode": "shadow_no_auto_override", "n_claims": len(claims),
               "claims": [{k: c.get(k) for k in
                           ("claim_id", "risk_level", "evidence_source_type", "source_check",
                            "answer_dependency", "blind_safe", "visibility", "home")}
                          for c in claims]}
    return lines, machine, claims, dangling


def cluster_flags(claims, cluster_top_candidates):
    """Per cluster: risk flags for class anchor hits. **No cap, no override**, only review requirements."""
    flags, audit = [], []
    for c in claims:
        anchors = _claim_class_anchors(c)
        if not anchors:
            continue
        hit = next((cand for cand in (cluster_top_candidates or [])
                    if class_match(cand, anchors)), None)
        if not hit:
            continue
        flags.append(f"REVIEW:{c['claim_id']}({c['risk_level']})")
        audit.append({"claim_id": c["claim_id"],
                      "cluster_candidate": hit,
                      "risk_level": c["risk_level"],
                      "evidence_source_type": c["evidence_source_type"],
                      "answer_dependency": c["answer_dependency"],
                      "blind_safe": c["blind_safe"],
                      "action": "risk_flag_only(no_auto_override)"})
    return flags, audit


def write_outputs(out_dir, species, tissue, claims, per_cluster_audit, run_id, dangling):
    out_dir = Path(out_dir)
    def _red(c, k):
        # Non-blind-safe entries: free text sanitized to post_decision standard even within full record files
        if not c.get("blind_safe", True) and k in ("failure_mode", "mitigation",
                                                   "observable_signature"):
            return "REDACTED:post_decision"
        return c.get(k)
    att = {"schema": "eyekb-shadow-attention/1.0", "species": species, "tissue": tissue,
           "mode": "shadow_no_auto_override", "run_id": run_id,
           "link_resolution": {"dangling_pointers": dangling, "all_resolved": not dangling},
           "claims": [{**{k: c.get(k) for k in
                          ("claim_id", "risk_level", "evidence_source_type", "source_check",
                           "answer_dependency", "blind_safe", "visibility")},
                       **{k: _red(c, k) for k in ("failure_mode", "mitigation")}}
                      for c in claims]}
    (out_dir / "shadow_attention.json").write_text(
        json.dumps(att, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    n = 0
    with open(out_dir / "shadow_flags.jsonl", "w", encoding="utf-8") as f:
        for a in per_cluster_audit:
            f.write(json.dumps({"ts": time.strftime("%F %T"), "run_id": run_id, **a},
                               ensure_ascii=False) + "\n")
            n += 1
    with open(out_dir / "shadow_flags.jsonl", "a", encoding="utf-8") as f:
        f.write(f"# shadow: risk flags in this run = {n}; all are review prompts only, automatic naming/downgrade changes = 0"
                "(Termination condition monitoring: auto-relabeling due to pitfalls must always be 0)\\n")
    return att, n

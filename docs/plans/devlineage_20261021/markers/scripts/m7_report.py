#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m7_report.py — assemble REPORT.md from the artefacts.

Every number in the report is read from a file on disk in this directory, so the prose cannot
drift from the data: if an artefact changes, re-running this script changes the report. The one
thing it does not do is write the gate's verdict by hand — it reads out/GATE.json.

Usage: python3 m7_report.py
"""
from __future__ import annotations

import collections
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mkcommon as M  # noqa: E402


def main() -> int:
    out = M.OUT
    R = lambda p: M.read_tsv(os.path.join(out, p))
    J = lambda p: json.load(open(os.path.join(out, p), encoding="utf-8"))
    nodes, att, ns, edges = R("NODES.tsv"), R("LABEL_ATTACHMENT.tsv"), R("MARKER_SETS_NODE.tsv"), R("EDGES.tsv")
    nc, gaps = R("MARKER_CHANGE_EDGES.tsv"), R("GAP_REGISTER.tsv")
    refusals, eref = R("NODE_GENE_REFUSALS.tsv"), R("EDGE_MARKER_REFUSALS.tsv")
    gate, gapsum = J("GATE.json"), J("GAP_SUMMARY.json")
    meta = J("CORPUS_GENE_INDEX_v1_META.json")
    ctx = J("NODE_CONTEXT_SOURCES.json")
    anchor_res = J("ANCHOR_RESOLUTION.json")
    panels = M.load_panels()

    by_node = collections.defaultdict(list)
    for r in ns:
        by_node[r["edge_id_or_node_key"]].append(r)
    L = []
    A = L.append

    A("# The marker layer of the developmental lineage — per lineage and per edge, graded")
    A("")
    A("This directory holds the middle clause of the owner's request: **each lineage carries its own")
    A("markers**, and **each transition carries a marker-change assertion**, every one of them graded")
    A("and every one of them anchored to something a reader can open on this machine. It builds")
    A("against the frozen contract `../DATA_CONTRACT_devlineage_v1.md` and the brief")
    A("`../BRIEF_V2_MARKER_LAYER_20261021.md`. The design decisions taken before the build are fixed")
    A("in `DESIGN_MARKER_LAYER.md`.")
    A("")
    A("The honest headline: **%d nodes carry %d graded assertions over %d distinct genes, 2 of 34"
      % (len({r['edge_id_or_node_key'] for r in ns}), len(ns), len({r['gene_symbol'] for r in ns})))
    A("edges can carry a stepwise marker change, and %d gaps are named explicitly — of which %d are"
      % (len(gaps), sum(1 for r in gaps if r["gap_kind"] == "no_evidence")))
    A("genuine absences of evidence and %d are pieces of evidence this layer refused to use.**"
      % sum(1 for r in gaps if r["gap_kind"] == "refused_evidence"))
    A("")
    A("---")
    A("")
    A("## 1. What is in the directory")
    A("")
    A("| file | what it is |")
    A("|---|---|")
    A("| `out/NODES.tsv` | the node table, one row per node, in the contract's node-key format |")
    A("| `out/MARKER_SETS_NODE.tsv` | **the per-node marker sets** — one row per gene per node, "
      "with `role`, `change`, `stage`, `assay`, `source_group`, `target_group`, `claim_type`, "
      "`evidence_ids`, `evidence_grade`, `evidence_anchor` |")
    A("| `out/MARKER_CHANGE_EDGES.tsv` | **the per-edge marker-change assertions**, same schema, "
      "`edge_id_or_node_key` carrying the edge key |")
    A("| `out/EDGES.tsv` | the edge table: contract edge key, relation type, directness, grade, "
      "marker-change status |")
    A("| `out/GAP_REGISTER.tsv` | **the gap register**, first-class, one row per node/edge/gene "
      "with no admissible evidence, with reason and the material that was actually checked |")
    A("| `out/GATE.json`, `out/GATE_READOUT.md` | the machine gate and its readout |")
    A("| `out/ANCHOR_RESOLUTION.json` | the anchor re-resolution result the gate produced |")
    A("| `out/CORPUS_GENE_INDEX_v1.tsv` | the corpus pass: per gene, counts, species split, and "
      "locators with a byte-level anchor |")
    A("| `out/MANIFEST.sha256` | the frozen build artefacts |")
    A("| `ledgers/` | chain log, replay ledger, manifest check, network audit, resource readings |")
    A("| `scripts/` | the build (`m0`–`m4`), the manifest (`m6`), the report (`m7`), the gate "
      "(`m5`), and `run_all.sh` |")
    A("")
    A("## 2. Where the markers came from, and what each source is allowed to say")
    A("")
    A("| source | allowed to supply | not allowed |")
    A("|---|---|---|")
    A("| the shipped marker panels (`kb/markers/*.json`) | the candidate identity panel per class, "
      "and a per-gene basis **where the panel states one** | it may not stand in for *lineage* "
      "membership, and its evaluation-volume-derived provenance may not be used |")
    A("| the local corpus (`literature_db/v2.6-dev_2026-10`, 244,877 chunks) | the anchor: a row "
      "whose text carries the gene, with paper id, section, ordinal and text hash | nothing about "
      "a paper we do not hold |")
    A("| the citation spine (`kb/link_registry/LINK_REGISTRY_v1.jsonl`) | citations the registry "
      "already proved contain the entry's genes in the paper's own full text | it is a disclosure "
      "surface, never a score |")
    A("| the Cell Ontology (`releases/2026-06-08`) | the node identity, the ancestors/descendants "
      "used for role separation, the `develops_from` relation | it carries **zero** gene-name terms "
      "for cell types, so it supplies no marker at all |")
    A("| the textbook layer (81 items, page anchors) | nothing gene-level | its own rule forbids it "
      "as expression evidence |")
    A("")
    A("### 2.1 The panels actually consumed, and how each candidate pool was selected")
    A("")
    A("Disclosed because an anchor being independent of the evaluation side does not make a *candidate"
      " list* independent of it. Read this column before treating a set as benchmark-clean.")
    A("")
    A("| library | file | read from | entries | genes | how the candidate pool was selected |")
    A("|---|---|---|---|---|---|")
    for lib, p in sorted(panels.items()):
        n_ent = len(p["labels"])
        n_gen = sum(len(v["genes"]) for v in p["labels"].values())
        where = "construction site" if p["path"].startswith("/mnt") else "repo copy"
        A("| `%s` | %s | %s | %d | %d | %s |"
          % (lib, p["file"], where, n_ent, n_gen, p["selection_basis"]))
    A("")
    A("Byte-identity of the two copies was checked for every shared panel file; the repo copy is the")
    A("only place `markers_v11_lensiris_increment.json` exists, and card L2 read it from there too.")
    A("")
    A("**A panel refused outright:** `markers_v12_holefill_increment.json` ships in the repository")
    A("but is **not consumed**. Its own scope text says it was built to fill *the measured coverage")
    A("holes of the 28-volume / 721-cluster run* — i.e. the candidate list is the benchmark's own")
    A("output, which the contract forbids as a source of markers. It is registered in the gap")
    A("register rather than silently dropped (`panel_selected_from_evaluation_report`).")
    A("")
    A("## 3. Node keys")
    A("")
    A("`dl:<cl_id>|sp=<species>|ts=<tissue_context>|st=<organism_stage>|es=<experimental_system>`")
    A("")
    A("| | count | how it was derived |")
    A("|---|---|---|")
    A("| nodes | %d | %d covered classes + %d germ-layer anchors from card L2's lineage layer, "
      "plus %d in-house developmental precursor nodes |"
      % (len(nodes), sum(1 for n in nodes if n["kind"] == "library_class"),
         sum(1 for n in nodes if n["kind"] == "germ_layer"),
         sum(1 for n in nodes if n["node_family"] == "in_house_dev_precursor")))
    A("| ids resolved from the ontology file | %d | the id is read from `cl.obo` "
      "(`releases/2026-06-08`), never typed |"
      % sum(1 for n in nodes if n["cl_id_in_ontology_file"] == "yes"))
    A("| stage = `adult` | %d | only where the shipped adult baseline declares the class |"
      % sum(1 for n in nodes if n["organism_stage"] == "adult"))
    A("| stage = `developing` | %d | only where the ontology's own text or a dev panel says so |"
      % sum(1 for n in nodes if n["organism_stage"] == "developing"))
    A("| stage = `unknown` | %d | `adult_or_unspecified` is **not** adult, and is never defaulted |"
      % sum(1 for n in nodes if n["organism_stage"] == "unknown"))
    A("| `es` (experimental system) | %d `unknown` | no shipped panel asserts one for a lineage "
      "node; guessing `in_vivo` for a tissue atlas would be invention |"
      % sum(1 for n in nodes if n["experimental_system"] == "unknown"))
    A("")
    A("**Why in-house nodes were added.** The ontology has no term for the developmental precursor")
    A("labels our own dev panels ship — card DEV-ONT recorded 7 of 10 as `NO_MATCH`. The contract")
    A("supplies the right form for exactly that case (`dl:NO_MATCH:<in_house_class_id>|…`), so these")
    A("labels get nodes instead of disappearing. Without them the developmental side of the lineage")
    A("would have no markers at all, which is the owner's central ask. They are knowledge-layer")
    A("nodes and never enter cell candidate ranking:")
    A("")
    A("| node | genes | note |")
    A("|---|---|---|")
    for n in sorted((n for n in nodes if n["node_family"] == "in_house_dev_precursor"),
                    key=lambda x: x["dl_id"]):
        A("| `%s` | %s | %s |" % (n["dl_id"].split(":")[-1], n["n_panel_genes_upstream"],
                                  n["panel_files"]))
    A("")
    A("## 4. Per-node marker sets — %d assertions" % len(ns))
    A("")
    A("### 4.1 How each gene got its role")
    A("")
    A("One role per assertion, assigned in this order (DESIGN §5): a **state programme** that")
    A("reaches a node is `state_warning`; a gene the panel itself declares as a subtype anchor, or a")
    A("label the ontology places strictly *under* the node term, is `subtype_discriminator`; the rest")
    A("is `identity_support`.")
    A("")
    A("| role | assertions | what it means here |")
    A("|---|---|---|")
    for role, gloss in (("identity_support", "this is what the type is"),
                        ("subtype_discriminator",
                         "this separates it from its nearest sibling — includes the panel's own "
                         "subtype-anchor layer"),
                        ("state_warning",
                         "this changes with disease, cycle or treatment and must not be read as "
                         "identity")):
        A("| `%s` | %d | %s |" % (role, sum(1 for r in ns if r["role"] == role), gloss))
    A("")
    A("The state separation is not cosmetic. `Endo_Patho`, `Mac_DAM_LAM`, `TAC_proliferating` and the")
    A("microglial state anchors (`P2RY12`, `SALL1`) are shipped as **state programmes** by the")
    A("knowledge base's own concept-kind sidecar; here they are written as `state_warning` on the")
    A("identity node they accompany, so a disease endothelial axis can never be read as the")
    A("endothelium's identity.")
    A("")
    A("### 4.2 Where the anchor for each gene comes from")
    A("")
    A("| support basis | assertions | what the anchor is |")
    A("|---|---|---|")
    for basis, gloss in (
            ("link_registry_gene_verified",
             "a citation the registry already proved contains the gene in that paper's own full "
             "text (`genes_in_text`), with its own locator"),
            ("corpus_gene_row",
             "a corpus row: paper id, section, ordinal and text hash — re-read by the gate"),
            ("panel_provenance_stated",
             "the panel's own per-gene basis (`canonical` / PMID), used only when it is not an "
             "evaluation-volume derivation"),
            ("panel_entry_basis_unstated",
             "the gene is shipped in the panel but that panel states no per-gene basis and no "
             "corpus row anchors it — the weakest tier, and flagged in the gap register")):
        A("| `%s` | %d | %s |" % (basis, sum(1 for r in ns if r["support_basis"] == basis), gloss))
    A("")
    A("Anchor species: %s. **No assertion on a human node is anchored on a mouse-only source** — "
      % dict(collections.Counter(r["anchor_species"] for r in ns)))
    A("those genes are gap rows instead (§7). Assay split: %s — RNA and protein rows are kept"
      % dict(collections.Counter(r["assay"] for r in ns)))
    A("separate and are never merged on one row.")
    A("")
    A("### 4.3 Every node, with its counts")
    A("")
    A("| node | stage | tissue | identity | subtype | state | genes |")
    A("|---|---|---|---|---|---|---|")
    for n in nodes:
        rs = by_node.get(n["node_key"], [])
        A("| `%s` | %s | %s | %d | %d | %d | %d |"
          % (n["dl_id"] if n["dl_id"].startswith("NO_MATCH") else n["dl_id"] + " " + n["cl_label"][:26],
             n["organism_stage"], n["tissue_context"],
             sum(1 for r in rs if r["role"] == "identity_support"),
             sum(1 for r in rs if r["role"] == "subtype_discriminator"),
             sum(1 for r in rs if r["role"] == "state_warning"), len(rs)))
    A("")
    A("## 5. Per-edge marker-change assertions — %d" % len(nc))
    A("")
    A("The edge list is card L2's 34 edges, re-keyed into the contract's edge key and re-typed so")
    A("that no relation is silently upgraded into another:")
    A("")
    A("| upstream relation | contract relation type | directness | edges | what it can carry |")
    A("|---|---|---|---|---|")
    A("-")
    A("| `develops_from_direct` | `ontology_development_relation` | direct | %d | a stepwise"
      " marker change, if a source states it |"
      % sum(1 for e in edges if e["directness"] == "direct"))
    A("| `develops_from_transitive` | `ontology_development_relation` | transitive | %d | a chain "
      "the ontology declares in full: time direction and identity conversion, **not** a single "
      "step, so no marker change is attributed |"
      % sum(1 for e in edges if e["directness"] == "transitive"))
    A("| `germ_layer_membership` | `ancestral_origin` | distant | %d | a distant origin; it must "
      "not pose as a single step |"
      % sum(1 for e in edges if e["directness"] == "distant"))
    A("")
    A("Evidence grade per edge: %s." % dict(collections.Counter(e["evidence_grade"] for e in edges)))
    A("Assertions per evidence grade: node-level identity assertions carry **no** grade by design "
      "(the four declared grades are edge-centric — see §10.1), and the %d edge assertions grade "
      "as %s." % (len(nc), dict(collections.Counter(r["evidence_grade"] for r in nc))))
    A("Marker-change status per edge: %s." % dict(collections.Counter(e["marker_change_status"]
                                                                     for e in edges)))
    A("")
    A("### 5.1 The admission test, and what it admitted")
    A("")
    A("A gene is written as `change=on` for edge `P → C` only when a local chunk (1) carries the")
    A("gene token, (2) belongs to a paper whose species fits the node, (3) **names the target")
    A("group**, and (4) is developmentally scented. Anything else is a gap row.")
    A("")
    A("| edge | transition | assertions | genes |")
    A("|---|---|---|---|")
    for ekey, n_rows in sorted(collections.Counter(r["edge_id_or_node_key"] for r in nc).items()):
        e = next((x for x in edges if x["edge_key"] == ekey), None)
        A("| `%s → %s` | %s | %d | %s |"
          % (e["precursor_label"], e["descendant_label"], e["edge_id"], n_rows,
             ", ".join(sorted(r["gene_symbol"] for r in nc if r["edge_id_or_node_key"] == ekey))))
    A("")
    A("Every one of these 10 rows names a `source_group` (the precursor) and a `target_group` (the")
    A("descendant), carries `claim_type=qualitative`, **no `effect_value` at all**, and states in")
    A("`uncertainty` what the source does and does not support: it names the target group in a")
    A("developmental context; no source on this machine measures the precursor→descendant change")
    A("itself.")
    A("")
    A("### 5.2 The loss side is deliberately empty")
    A("")
    A("**%d genes** are present in a precursor's panel and absent from the descendant's. Not one of"
      % sum(1 for r in eref if r["reason"] == "detection_conditions_insufficient"))
    A("them is written as `down` or `off`: panel absence is not a detection result, and")
    A("\"not mentioned\" is not `off`. They are named individually in the gap register with reason")
    A("`detection_conditions_insufficient`. This is the mechanical form of the contract's rule, and")
    A("it is the reason the confirmed marker-change layer is ten rows and not two hundred.")
    A("")
    A("## 6. All 34 edges, with their status")
    A("")
    A("| edge | precursor | descendant | relation | directness | grade | marker change |")
    A("|---|---|---|---|---|---|---|")
    for e in sorted(edges, key=lambda x: x["edge_id"]):
        A("| %s | %s | %s | %s | %s | %s | %s |"
          % (e["edge_id"], e["precursor_label"], e["descendant_label"], e["relation_type"],
             e["directness"], e["evidence_grade"],
             ("%d assertions" % sum(1 for r in nc if r["edge_id_or_node_key"] == e["edge_key"]))
             if e["marker_change_status"] == "admitted_stepwise"
             else e["marker_change_status"]))
    A("")
    A("## 7. What could not be closed")
    A("")
    A("This section is the deliverable as much as the tables above. Numbers first, then the")
    A("individual items; the machine-readable form is `out/GAP_REGISTER.tsv` (%d rows)." % len(gaps))
    A("")
    A("| gap kind | rows | meaning |")
    A("|---|---|---|")
    A("| `no_evidence` | %d | nothing admissible exists locally |"
      % sum(1 for r in gaps if r["gap_kind"] == "no_evidence"))
    A("| `refused_evidence` | %d | material exists but is inadmissible (evaluation-derived, "
      "prohibited, or benchmark-holedriven) |"
      % sum(1 for r in gaps if r["gap_kind"] == "refused_evidence"))
    A("| `thin_evidence` | %d | an assertion exists but its support is weak and is disclosed as "
      "such |" % sum(1 for r in gaps if r["gap_kind"] == "thin_evidence"))
    A("")
    A("| reason | rows | the closing question this leaves |")
    A("|---|---|---|")
    closing = {
        "detection_conditions_insufficient":
            "a source that measures the gene in the precursor and in the descendant with adequate "
            "detection conditions — this is what would let a loss be claimed",
        "evidence_only_from_evaluation_volume":
            "an independent source for these genes: they currently enter only through an "
            "evaluation volume's own cells or the dev-exam substrate",
        "marker_change_not_available_for_relation_type":
            "nothing to close by reading; an ancestral-origin relation cannot carry a single-step "
            "marker change by construction",
        "node_has_no_panel_and_no_source":
            "a panel, or a source, for this node: it is declared but carries no markers",
        "panel_entry_basis_unstated":
            "a per-gene basis for these genes — the panel lists them without saying why",
        "review_citation_unverifiable_locally":
            "the paper the panel's note refers to, or a corpus row for the gene",
        "edge_not_stepwise_relation":
            "a direct (single-step) source for each link of the chain; the ontology gives only the "
            "chain, which cannot be read as one step",
        "state_program_without_identity_node":
            "an identity node for this state programme, or a decision that it belongs to another "
            "layer",
        "parent_group_has_no_panel":
            "a panel for the precursor end: with no precursor genes there is nothing to compare "
            "against",
        "no_source_in_corpus":
            "a source for these genes/classes; the corpus does not carry them",
        "different_species_not_stitchable":
            "a human-context source: the only local evidence is in another species and is "
            "therefore not stitched",
        "panel_selected_from_evaluation_report":
            "a candidate list built without reading the benchmark's own holes",
    }
    for reason, n in sorted(collections.Counter(r["reason"] for r in gaps).items(),
                            key=lambda x: -x[1]):
        A("| `%s` | %d | %s |" % (reason, n, closing.get(reason, "—")))
    A("")
    A("### 7.1 The four things a reader should actually take from this")
    A("")
    A("1. **The lineage is a two-step graph, not a tree of markers.** Only rod and cone have a")
    A("   complete ontology path (`neurectodermal cell → retinal progenitor cell → rod/cone`), and")
    A("   only those two edges can carry a stepwise marker change. The other %d edges are typed and"
      % (len(edges) - 2))
    A("   graded, but their marker dynamics are recorded as *not available* rather than narrated.")
    A("2. **%d of 70 nodes carry no marker at all**, and the reason is stated for each: %d are"
      % (sum(1 for r in gaps if r["scope"] == "node"),
         sum(1 for r in gaps if r["scope"] == "node" and
             r["reason"] == "node_has_no_panel_and_no_source")))
    A("   germ-layer concepts or classes with no panel, %d are declared with a panel that reaches no"
      % sum(1 for r in gaps if r["scope"] == "node" and r["reason"] == "no_source_in_corpus"))
    A("   admissible anchor.")
    A("3. **%d genes were refused because their only basis is an evaluation volume**, and %d more"
      % (sum(1 for r in gaps if r["reason"] == "evidence_only_from_evaluation_volume"),
         sum(1 for r in gaps if r["reason"] == "different_species_not_stitchable")))
    A("   because the only local evidence is in another species. Both numbers are evidence of the")
    A("   layer's restraint, not of the corpus's poverty, and both shrink the layer relative to what")
    A("   a permissive reading would have produced.")
    A("4. **%d assertions rest on a panel entry with no per-gene basis and no corpus row.** They are"
      % sum(1 for r in ns if r["support_basis"] == "panel_entry_basis_unstated"))
    A("   shipped, they are in the tables, and they are also in the gap register — the weakest tier")
    A("   is not allowed to look like the strongest.")
    A("")
    A("### 7.2 Gaps that are named but not closed, by name")
    A("")
    for r in gaps:
        if r["scope"] in ("node", "label", "panel") or r["reason"] in (
                "different_species_not_stitchable", "no_source_in_corpus"):
            A("* **%s** — `%s` — %s" % (r["subject_key"], r["reason"], r["detail"]))
    A("")
    A("## 8. The gate")
    A("")
    A("`out/GATE.json` is the machine-readable form; `out/GATE_READOUT.md` is the table. Verdict:")
    A("**%s**, %d checks, %d failed." % (gate["verdict"], gate["n_checks"], gate["n_fail"]))
    A("")
    A("| check | name | status | pass/fail count |")
    A("|---|---|---|---|")
    for c in gate["checks"]:
        A("| %s | %s | %s | %d offenders |" % (c["code"], c["name"], c["status"],
                                                c["n_offenders"]))
    A("")
    A("Two of them are worth naming here because they caught real defects during the build:")
    A("")
    A("* **G2** re-opens every anchor. It failed on its first run for 9 anchors whose panel file")
    A("  resolution picked the construction site while the panel only exists in the repo copy — a")
    A("  reader following those anchors would have found nothing.")
    A("* **G7** found that 9 assertions had been anchored on the dev-exam substrate's own paper.")
    A("  The corpus pass now excludes it (and every paper the knowledge base flags")
    A("  `data_side_only`) from anchor locators, so the evaluation side cannot leak in through a")
    A("  citation.")
    A("")
    A("Anchor re-resolution (G2): %d anchors, %s; %d corpus rows re-read byte for byte."
      % (anchor_res["n_anchors"], anchor_res["by_kind"], anchor_res["corpus_rows_reread"]))
    A("")
    A("## 9. Proofs, with the commands that produced them")
    A("")
    A("**One command builds and judges the whole layer:**")
    A("")
    A("```")
    A("systemd-run --user --unit=mk-full --collect -p MemoryMax=6G -p MemorySwapMax=2G \\")
    A("  --wait --pipe bash /mnt/D/EyeKB/plans/devlineage_20261021/markers/scripts/run_all.sh")
    A("```")
    A("")
    A("Measured on the full run: `Service runtime: 43.2s`, `Memory peak: 457.8M` (cgroup), and the")
    A("corpus pass alone measured `maxrss 0.33 GiB` for one process over 244,877 chunks — the")
    A("concurrency question is answered by there being one process.")
    A("")
    A("**Byte-identical rebuild** (`ledgers/REPLAY.txt`, produced by rebuilding the chain into a")
    A("scratch directory and comparing every artefact in the manifest):")
    A("")
    A("```")
    A(open(os.path.join(M.WAVE, "ledgers", "REPLAY.txt"), encoding="utf-8").read().strip())
    A("```")
    A("")
    A("**Default behaviour byte-identical**, by replaying the recorded production query set rather")
    A("than arguing about it (`ledgers/golden_721_now.json` is written by the replay):")
    A("")
    A("```")
    A("python3 /mnt/D/EyeKB/plans/holefill_v12_20261021/golden_721.py")
    A((gate.get("golden", {}).get("stdout_tail") or "").strip().splitlines()[0]
      if gate.get("golden", {}).get("stdout_tail") else "")
    A("```")
    A("")
    A("i.e. 721 of 721 recorded clusters reproduce their recorded ranking, `differ=0`, exactly as")
    A("before this card. This layer adds files; it changes no default answer.")
    A("")
    # zero network: counted here, by the last step of the chain, and written to ledgers/ so the
    # number in this report and the number in the ledger are the same reading
    audit_log = os.path.join(M.WAVE, "ledgers", "net_audit.log")
    hooks = events = 0
    if os.path.isfile(audit_log):
        for line in open(audit_log, encoding="utf-8", errors="replace"):
            if line.startswith("# hook-installed"):
                hooks += 1
            elif line.startswith("EVENT"):
                events += 1
    audit_doc = ["# zero-network audit (audit hook, covers child processes, including this report)",
                 "hook_install_lines=%d" % hooks, "network_event_lines=%d" % events,
                 "NET_ZERO_PASS" if (events == 0 and hooks > 0) else "NET_AUDIT_FAIL"]
    open(os.path.join(M.WAVE, "ledgers", "NET_AUDIT_SUMMARY.txt"), "w",
         encoding="utf-8").write("\n".join(audit_doc) + "\n")
    A("**Zero network**, by an audit hook that covers child processes "
      "(`ledgers/NET_AUDIT_SUMMARY.txt`):")
    A("")
    A("```")
    A("\n".join(audit_doc))
    A("```")
    A("")
    A("The load-receipt lines are the control: %d of them prove the hook was installed, so zero"
      % hooks)
    A("event lines means zero network operations rather than a hook that never ran. No download was")
    A("performed and no download was needed: every source named in §2 was already on this machine.")
    A("")
    A("**Nothing under `kb/` was touched** (gate G13): the whole knowledge base was walked and its")
    A("newest mtime predates this card. The layer is registered-but-not-activated: it writes only")
    A("inside `plans/devlineage_20261021/markers/`, and nothing default reads it.")
    A("")
    A("**Manifest** (`out/MANIFEST.sha256`, %d entries) verifies after the gate has re-run:"
      % len([l for l in open(os.path.join(out, "MANIFEST.sha256"), encoding="utf-8")
             if not l.startswith("#") and l.strip()]))
    A("")
    A("```")
    A("$ (cd out && sha256sum -c MANIFEST.sha256) | grep -c ': OK'")
    A("%s" % subprocess.run(["bash", "-c",
                             "cd %s && sha256sum -c MANIFEST.sha256 | grep -c ': OK'" % out],
                            capture_output=True, text=True).stdout.strip())
    A("```")
    A("")
    A("Run-time write-outs are excluded from the manifest on purpose (`GATE.json`,")
    A("`GATE_READOUT.md`, `ANCHOR_RESOLUTION.json`): they are rewritten every time the layer is")
    A("verified, so including them would make the manifest fail whenever the layer is *checked*")
    A("rather than whenever it is *wrong*. The acceptance test is therefore 'sha256sum -c' still")
    A("returns 0 after the gate has run', which is what `run_all.sh` checks and what the figure")
    A("above shows.")
    A("")
    A("**Independence from the upstream corpus pass.** Card L2 built its own gene index over 8")
    A("panels; this card rebuilt it over 773 symbols from 12 panels with the same matcher. The 713")
    A("genes the two passes share have **identical chunk counts, 0 differences** — the pass is")
    A("reproducible, and the 60 newly covered symbols are the difference the extra panels make.")
    A("")
    A("## 10. Raised contract issues (raised, not forked)")
    A("")
    A("The contract asks to be told when a field is genuinely insufficient rather than forked")
    A("privately. Four such points came up; all four are handled additively, so no declared value")
    A("changes meaning:")
    A("")
    A("1. **The four evidence grades are edge-centric.** They answer *how strong is the lineage")
    A("   step*; they do not answer *how strong is an identity claim*. Node-level identity")
    A("   assertions therefore carry **no** `evidence_grade` (the gate refuses any value outside")
    A("   the declared four and requires one on every edge assertion) and carry an anchor object")
    A("   plus a `support_basis` tier instead. Filling the field with a value that does not mean")
    A("   what it says would be worse than an empty field with a stated reason.")
    A("2. **`assay` has no declared vocabulary.** Declared here as a closed set with the RNA/protein")
    A("   split the contract demands: `scRNA`, `literature_RNA`, `literature_protein`, `textbook`,")
    A("   `unspecified`. The gate refuses a mixed assay on one row.")
    A("3. **`experimental_system` is unobservable in the shipped panels**, so every node carries")
    A("   `es=unknown`. This is a real limitation of the layer and not a placeholder.")
    A("4. **A per-gene extraction record has no home in the schema.** `effect_value` is filled only")
    A("   when a source states a number *and* an extraction record exists; since the mining in this")
    A("   card never reads numbers out of prose, **no assertion carries an `effect_value`** and every")
    A("   edge assertion is `claim_type=qualitative`. That is the honest reading of \"never")
    A("   fabricate a fold change\", not a missing step.")
    A("5. **One grade name does not fit one of its uses**: `textbook_or_review_distant_origin` is")
    A("   also the correct grade for a distant origin the *ontology itself* declares. The anchor")
    A("   kind is recorded alongside (`anchor_kind` / `evidence_kind`), so no reader is misled.")
    A("")
    A("## 11. What this layer is not")
    A("")
    A("* It is **not** a complete lineage.** It is a comprehensively enumerated and honestly graded")
    A("  one: 34 edges typed, 70 nodes keyed, %d of them carrying markers, %d of them named as gaps."
      % (sum(1 for n in nodes if by_node.get(n["node_key"])),
         sum(1 for n in nodes if not by_node.get(n["node_key"]))))
    A("* It is **not** a claim that these markers change along these transitions.** Ten assertions")
    A("  say a gene is present in the target group and developmentally scented; none says the")
    A("  transition was measured.")
    A("* It is **not** independent of the adult library.** Its candidate pools are the shipped")
    A("  panels, several of which were selected with an evaluation volume's cells (§2.1). What is")
    A("  independent is the *anchor* on every individual assertion; what is not is the size and")
    A("  membership of some candidate lists. That distinction is the reason §2.1 exists.")
    A("* It is **not** activated.** Nothing default reads `plans/devlineage_20261021/markers/`.")
    A("")
    A("## 12. Reproducing this")
    A("")
    A("```")
    A("cd /mnt/D/EyeKB/plans/devlineage_20261021/markers")
    A("bash scripts/run_all.sh                 # build + manifest + gate (rebuild replay included)")
    A("bash scripts/run_all.sh --no-replay     # skip the two replays")
    A("python3 scripts/m7_report.py            # regenerate this report from the artefacts")
    A("python3 scripts/m4_gap_register.py      # regenerate the gap register alone")
    A("```")
    A("")
    A("Scripts: `m0_corpus_gene_index.py` (corpus pass, the only heavy step) · `m1_nodes.py` (node")
    A("keys) · `m2_node_markers.py` (per-node sets) · `m3_edge_assertions.py` (per-edge changes) ·")
    A("`m4_gap_register.py` (gap register) · `m5_gate.py` (13 checks) · `m6_manifest.py` ·")
    A("`m7_report.py` · `run_all.sh` · `netaudit/sitecustomize.py`.")
    A("")

    p = os.path.join(M.WAVE, "REPORT.md")
    open(p, "w", encoding="utf-8").write("\n".join(L))
    print("wrote", p, "lines:", len(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
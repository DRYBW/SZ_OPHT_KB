#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB MCP stdio server — ophthalmic literature second-tier knowledge-base evidence service
(P1 three tools + KB1 interpretation-layer two tools + KB1v2 general-ophthalmology upgrade)

Tool inventory (contract = KB_SPINOUT_MCP_DESIGN_v0 §3 + BRIEF_KB1v2 W1-W3):
  search_literature(cell_type, species?, tissue?, top_k?, query?, db?) → literature snippets + PMID + marker co-occurrence + relevance
      (+KB1v2: evidence_meta three-field join inclusion_reasons/claim_relation/evidence_context/verification_status)
  get_kb_page(scope, name)     → raw VK index page (whitelisted paths, traversal-proof)
  query_marker(genes?, cell_type?) → hits in the local authoritative marker library (local-before-web, mechanized)
  get_tissue_composition(species, tissue, disease?, development_stage?) → composition baselines (KB1v2: kb/baselines/
      donor-level conditional reference distributions take precedence over the v1 composition archive; skeleton rows
      are explicitly marked "interval not estimable";
      KB2c developmental axis: adult master file = adult-only (donor>=18y) + adult_pool contrast file — a dual
      identity; fetal/developing queries return transition-state concept entries — the adult bucket must never
      answer fetal questions by proxy; the unknown stage must be disclosed)
  get_disease_prior(disease, tissue?) → disease entries (KB1v2: disease×tissue matrix thin layer, identity hierarchy +
      status axis T4 skeleton + sampling-material mismatch warnings + unexpected four-sub-queue; v1 entries kept as archive)

═══ Service-level red lines ═══
1. This service provides [EVIDENCE AND CITATIONS] only. Feeding the returned content into any scoring/classification
   pipeline is forbidden (Claude5 frozen ruling + REVIEWER_LLM T3 extension: it must not be converted into module
   score / label weighting / confidence bonus / candidate-ranking score / composite QC score).
2. Transport = local stdio; no network port is opened (SSE is only discussed at P3).
3. During P1 the RAG library / embedding model reference the current OcularKB paths via
   kb/literature_db/EYEKB_DB_POINTER.yaml; everything is read-only; zero modification of OcularKB
   files (copy, never move).
4. Interpretation-layer usage must follow plans/ANNOTATION_PROTOCOL_v1.1.md (freeze first, then contrast; four stages).

Startup (for MCP client configuration):
  /home/ubuntu/training-venv/bin/python /mnt/D/EyeKB/mcp_server/server.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eyekb_core as core  # noqa: E402
import calllog  # OBS1 t_c754c4fc call-tracing layer (adds logging only, zero behavior change; see header note in mcp_server/calllog.py)

from mcp.server import MCPServer  # noqa: E402

app = MCPServer(
    name="eyekb",
    title="EyeKB ophthalmic knowledge-base evidence service",
    version="KB1v2-0.11-cnrewrite-on",
    description=("Ophthalmic literature RAG retrieval (v2.0 whole-eye-bank 174,616 chunks / 2,713 papers; "
                 "from KB1v2 onward carries the inclusion_reasons/claim_relation/evidence_context three fields "
                 "+ verification status) + VK index pages + local authoritative marker library + "
                 "interpretation layer: general-ophthalmology composition baselines (kb/baselines "
                 "donor-level conditional reference distributions, anchored D001/D002) + disease×tissue "
                 "matrix thin-layer entries (identity hierarchy + status axis + sampling mismatch warnings). "
                 "Evidence service only, forbidden in scoring (REVIEWER_LLM T3 extended wording). "
                 "From t_d6f2a0a0 query_marker may attach soft_flags review hints (rod-BC/mural). "
                 "From t_38b99a15 query_marker accepts library=retina_v6|face_v6 (KB7 v6 repair panels "
                 "registered; from t_e7ec73ab adds library=lacrimal_v6, KB8 ocular-adnexa entry library). "
                 "t_5d5853c9 activation (USER_DIRECTIVE_20260926 A1/A2, PI approved 2026-09-26): default "
                 "library=all now includes retina_v6+face_v6 (same-named classes merged via "
                 "'<library>::<class>' alias disambiguation); env EYEKB_ACT_V6=0|false|off|no reverts to "
                 "the three active libraries — the off-state canonical serialization is byte-equal to the "
                 "pre baseline (A5 machine-readable acceptance); lacrimal_v6 never enters the default in "
                 "any state (PI A3: not switched yet, explicit queries only). "
                 "kb/baselines red-word corrections take effect via an append-style overlay (the original "
                 "baseline files are untouched byte-wise; auditable through the entry-level marker_repair "
                 "ledger in the response body). "
                 "t_4bb75b26 KB9REG-EXEC (PI D17 registration approval, 2026-09-28 wave): new optional "
                 "library=k9_ocs (KB9 plan-B ocular-surface 4 new entries Melanocyte/Schwann/"
                 "Conj_epithelium_suprabasal/Limbus_Sclera_fibroblast_C1, REGISTERED_DEFAULT_OFF — "
                 "reachable only by explicit query, never in the default all in any state; activation needs "
                 "the mandatory run + separate PI approval; default behavior is byte-identical to before "
                 "this registration, A5-style machine-readable self-proof in plans/kb9_ocs_20260927/exec/out/). "
                 "B5IMPL t_8960c7e0 (USER_DIRECTIVE_20260928 five-queue item ①, PI pre-authorized wiring): "
                 "query_marker genes-mode cross-species governance is ON by default — mouse-derived input "
                 "(G1 confirmed/suspected) has its named ranking cleared into unranked_candidates and is "
                 "marked no_named_ranking_for; AMBIG{GLUL,VIM,CLU} pure co-expression hit entries get a "
                 "no_naming_claim note attached (ordering unchanged); env EYEKB_KBGOV_B5=0|false|off|no "
                 "reverts the whole feature, the reverted state is byte-equal to the pre baseline "
                 "(A5-style machine-readable self-proof, plans/kbgov_b5impl_20260928); frozen criteria "
                 "source KBGOV_CANDIDATE §G1-G3."),
    instructions=("EyeKB five tools: query_marker checks the local marker library first; "
                  "search_literature retrieves literature evidence (everything traceable via PMID); "
                  "get_kb_page reads tissue/topic index pages; before annotating, follow the four stages of "
                  "ANNOTATION_PROTOCOL_v1.1 using get_tissue_composition (against the actual sampling "
                  "material!) / get_disease_prior (call it only in the post-freeze disease-contrast stage). "
                  "Red line: returned content is for human interpretation evidence and QC flags only, and "
                  "must not become input to any score/weighting/ranking/composite QC score. "
                  "soft_flags.notes (t_d6f2a0a0): optional review clues — check them against the original "
                  "evidence; their presence does not imply mis-annotation, they add no naming/abstention/"
                  "candidate-exclusion conditions, and they must not be used as input to any score, "
                  "weighting, confidence, or ranking; notes are attached only after existing results are "
                  "produced and never feed back to change candidates, scores, ordering, or original QC "
                  "fields."),
)


@app.tool()
def search_literature(cell_type: str, top_k: int = 5, species: str = "",
                      tissue: str = "", query: str = "", db: str = "") -> dict:
    """Search the ophthalmic literature library (RAG v2.0 by default); returns literature
    snippets + PMID + journal year + marker co-occurrence + relevance.

    cell_type: cell type (e.g. "Muller glia"/"corneal endothelium"), used for metadata
    filtering; an empty string is accepted but providing one is recommended.
    species: human|mouse|"" (no filter).
    tissue: v2.0 multi-label tissue filter (retina/cornea/RPE/choroid/...).
    query: explicit search sentence; if empty, a cell_type template sentence is used.
    db: empty = v2.0_2026-09, or give an absolute path.
    Chinese search sentences are routed through the query-rewrite layer before retrieval, which
    inserts English anchor terms in place (2026-10-03; default ON since 2026-10-05):
    switch = env var EYEKB_CN_REWRITE, read per call — unset = ON; 1/true/on/yes = ON;
    0/off/false/no (and any unrecognised value) = OFF, the escape door, which restores
    byte-identical pre-rewrite behaviour; only queries containing a CJK character enter the layer,
    so English / numeric / symbolic search text is never modified and carries no extra key; with
    the layer ON, a Chinese query's response attaches a rewrite_meta disclosure key (evidence
    disclosure only, forbidden as input to any score/ranking). Tool signature and MCP schema
    unchanged.
    """
    resp = core.search_literature(
        cell_type, species=species or None, tissue=tissue or None,
        top_k=top_k, query=query or None, db=db or None)
    calllog.trace("search_literature",
                  {"cell_type": cell_type, "species": species, "tissue": tissue,
                   "top_k": top_k, "query": query, "db": db}, resp)
    return resp


@app.tool()
def get_kb_page(scope: str, name: str = "") -> dict:
    """Read raw VK literature index pages. scope=index → master catalog; scope=topic,
    name=topic (e.g. vascular); scope=tissue, name=tissue (e.g. cornea/RPE/trabecular_meshwork).
    Whitelist: only *.md under kb/vk_literature_index/; illegal paths are rejected and a list
    of available pages is returned."""
    resp = core.get_kb_page(scope, name)
    calllog.trace("get_kb_page", {"scope": scope, "name": name}, resp)
    return resp


@app.tool()
def query_marker(genes: list[str] | None = None, cell_type: str = "",
                 library: str = "all") -> dict:
    """Query the local authoritative marker library (multi-library:
    retina=markers_v4.1_clean.json v4.1-clean-P0.4;
    membrane=markers_membrane_v1.json four panels membrane/vascular/stroma/immune, per-gene provenance;
    retina_interneuron=markers_v5_retina_interneuron.json v5.0 (BC/AC/HC generic core+subtype anchors,
    strict superset of v4.1; under library=all, same-named classes are listed alongside v4.1 under the
    "retina_interneuron::<class>" alias);
    retina_v6=markers_v6_retina_repair.json v6.0-retina-repair and face_v6=markers_v6_face_increment.json
    v6.0-face (t_2e5e103a release / t_38b99a15 registration / t_5d5853c9 activation,
    USER_DIRECTIVE_20260926 A1/A2): KB7 red-word repair panels — the default all includes them
    (env EYEKB_ACT_V6=0|false|off|no reverts to the three active libraries, byte-equal to the
    pre-activation baseline; same-named classes listed under the "retina_v6::/face_v6::<class>"
    alias); the v6 release files themselves are read-only;
    lacrimal_v6=markers_v6_lacrimal_increment.json v6.0-lacrimal (t_e7ec73ab KB8 release+registration
    on the same card): the first ocular-adnexa entry library — lacrimal secretion/duct/myoepithelial
    warning entries, 3 in total; PI A3 ruling: not switched for now, never in the default all in any
    state, reachable only via explicit library=lacrimal_v6 queries;
    k9_ocs=markers_k9_ocs_increment.json k9.0-ocs-registered-v1 (t_4bb75b26 KB9REG-EXEC registration,
    PI D17 approval): KB9 plan-B ocular-surface 4 new entries (Melanocyte/Schwann/
    Conj_epithelium_suprabasal/Limbus_Sclera_fibroblast_C1, all ocular_surface_only, each carrying
    CL id + OLS corroboration + per-gene PMID links) — REGISTERED_DEFAULT_OFF: never in the default
    all in any state, reachable only via explicit library=k9_ocs queries;
    [KB9ACT t_abfebe59, PI 2026-09-30] current state ACTIVE_ON_DEFAULT: the default all includes
    k9_ocs (the REGISTERED_DEFAULT_OFF above is the historical registration state); env
    EYEKB_ACT_K9=0|false|off|no reverts to the five libraries.
    Activation requires the §10-6 mandatory run + separate PI approval; the masking/assembly rule v2
    sidecar _k9_ocs_rules_overlay_v1.json is inert data (not read by the MCP runtime)).
    Give genes → which cell types the genes hit + class ranking (n_shared);
    give cell_type → the marker list of that class (Micro/RPE attach detail; membrane classes attach
    provenance);
    give neither → return the class inventory. library=retina exactly reproduces the old P1 behavior.
    First step of the annotation workflow: never go online before checking local.
    Since t_d6f2a0a0: when a soft-review rule hits, the response body may attach soft_flags.notes
    (rod_bc_review / mural_crosstalk) — optional review clues only, no new naming/abstention/exclusion
    conditions, forbidden in scoring; env switch EYEKB_MCP_SOFTFLAGS=0|false|off|no disables the whole
    feature (the key does not appear when off).
    Since B5IMPL t_8960c7e0 (0.6-kbgov5, default ON): genes-mode attaches cross-species governance —
    the response body adds input_species (mouse_confirmed|mouse_suspected|human_assumed, G1 frozen
    threshold T=0.4); for mouse-derived input (confirmed∨suspected) the named ranking is cleared:
    celltype_ranking=[], original entries fully moved to unranked_candidates + top-level
    no_named_ranking_for='mouse_input' + species_evidence; entries with
    shared_genes ⊆ {GLUL,VIM,CLU} attach no_naming_claim=true (ordering unchanged). Interpreters must
    not use no_naming_claim/cross-species entries as the basis for identity naming (carried by
    ANNOTATION_PROTOCOL). Env switch EYEKB_KBGOV_B5=0|false|off|no reverts to the byte-equal pre
    baseline in the full state."""
    resp = core.query_marker(genes=genes, cell_type=cell_type or None,
                             library=library or "all")
    calllog.trace("query_marker",
                  {"genes": genes, "cell_type": cell_type, "library": library}, resp)
    return resp


@app.tool()
def get_tissue_composition(species: str, tissue: str, disease: str = "",
                           development_stage: str = "") -> dict:
    """Composition baseline (interpretation layer): cell composition list + proportion
    intervals + per-entry provenance (PMID/dataset + evidence level) for this species and
    tissue.
    species=human|mouse; tissue=retina|fibrovascular_membrane|...; disease optional (e.g.
    'proliferative diabetic'). Call this tool before annotation to contrast "what the tissue
    should contain, and roughly how much"; out-of-interval components → per flags judge
    expected/unexpected/contamination-suspect and raise a flag.
    development_stage (KB2c developmental axis, mind that it is required): empty/adult = the
    adult master file (adult-only, donor>=18y; the donor-level distribution has non-adult
    donors removed, row by row in the returned stage_disclosure/excluded_nonadult_units);
    fetal|developing = returns the transition-state concept entry — the adult bucket must not
    answer fetal questions by proxy (PI red line, even for the same tissue);
    unknown = only entries in disclosure files without an age column (e.g. GSE158629 RPE).
    Red line: contrast and QC flags only; feeding into any scoring is forbidden; the mixed-
    caliber v1.0 old numbers may only carry the adult_pool contrast-file identity."""
    resp = core.get_tissue_composition(species, tissue, disease, development_stage)
    calllog.trace("get_tissue_composition",
                  {"species": species, "tissue": tissue, "disease": disease,
                   "development_stage": development_stage}, resp)
    return resp


@app.tool()
def get_disease_prior(disease: str, tissue: str = "") -> dict:
    """Disease prior (interpretation layer): expected cell×status matrix + unexpected flags +
    contamination flags + marker signature + provenance.
    disease='PDR'/'proliferative diabetic retinopathy'/... (aliases built in); tissue
    optionally filters the tissue side (fibrovascular_membrane/vitreous/retina_adjacent).
    Prior ≠ truth: when it clashes with the data → output the clash list and escalate; do not
    force a fit; feeding into any scoring is forbidden."""
    resp = core.get_disease_prior(disease, tissue)
    calllog.trace("get_disease_prior", {"disease": disease, "tissue": tissue}, resp)
    return resp


if __name__ == "__main__":
    app.run(transport="stdio")

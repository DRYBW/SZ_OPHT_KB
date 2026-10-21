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
    version="KB1v2-0.14-kb11a-reasonjoin",
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
    """Retrieve literature passages for a cell type / tissue from the bundled ophthalmic corpus.
    Returns passage text, PMID, journal, year, the marker genes that co-occur, and a relevance
    score. top_k controls how many passages come back (default 5).

    cell_type: metadata filter, e.g. "Muller glia" or "corneal endothelium". Recommended.
    species:   human | mouse | "" (no filter).
    tissue:    multi-label tissue filter, e.g. retina, cornea, RPE, choroid.
    query:     your own search sentence; when empty, a template sentence is built from cell_type.
    db:        empty = the bundled v2.0_2026-09 corpus, or an absolute path to another corpus.

    Chinese questions are accepted. A deterministic term-level bridge inserts English anchor
    terms in place without deleting any of your characters; it is not a translator. English,
    numeric and symbolic queries pass through untouched. A Chinese query's response carries a
    rewrite_meta key disclosing what was inserted -- disclosure only, it never affects ranking.
    Set EYEKB_CN_REWRITE=0 to turn the bridge off.
    """
    resp = core.search_literature(
        cell_type, species=species or None, tissue=tissue or None,
        top_k=top_k, query=query or None, db=db or None)
    calllog.trace("search_literature",
                  {"cell_type": cell_type, "species": species, "tissue": tissue,
                   "top_k": top_k, "query": query, "db": db}, resp)
    return resp


@app.tool()
def get_kb_page(scope: str, name: str = "", summary: bool = False) -> dict:
    """Read a knowledge-base page as shipped (markdown). Three page types:
      scope="index"                 the master catalog of every page.
      scope="topic",  name="..."    a topic page, e.g. vascular.
      scope="tissue", name="..."    a tissue page, e.g. cornea, RPE, trabecular_meshwork.
    scope is required; name is required for topic and tissue. An unknown or illegal path is
    rejected, and the response lists the pages that do exist.

    summary=true returns one row per page (title, scope, path, size in characters) instead of the
    page text. The catalogue page runs to roughly 139,000 characters, so use summary when you only
    need to see which pages exist before reading one. summary=false, the default, is unchanged.
    """
    resp = core.get_kb_page(scope, name, summary)
    calllog.trace("get_kb_page", {"scope": scope, "name": name, "summary": summary}, resp)
    return resp


@app.tool()
def query_marker(genes: list[str] | None = None, cell_type: str = "",
                 library: str = "all",
                 species: str = "", volume_id: str = "", volume_species: str = "",
                 tissue: str = "") -> dict:
    """Look up the local marker library. Three ways to call it.
    genes=[...]      -> which cell types those genes point to, with n_shared = how many of your
                        genes each candidate shares; the ranking is the answer.
    cell_type="..."  -> that class's authoritative marker list.
    neither          -> the class inventory.

    library: "all" (default) searches every active library; pass one name to restrict to it:
    retina, retina_interneuron, retina_v6, face_v6, membrane, k9_ocs, retina_v7, retina_dev,
    lacrimal_v6. library="retina" reproduces the original single-library behaviour exactly.

    Species routing (genes mode). The species is decided from `species` first, then from
    volume_species / volume_id, then from gene-symbol morphology. Mouse-derived input never gets
    a named ranking: celltype_ranking is emptied, the entries move to unranked_candidates, and
    no_named_ranking_for="mouse_input" records why. If no source can decide, the response sets
    species_unresolved and species_review_required -- the service never silently assumes human.

    Things the response tells you, and how to read them:
      soft_flags.notes   optional review clues (rod_bc_review, mural_crosstalk). Clues only:
                         they change no name, no abstention and no exclusion.
      state_annotations  cell-state / program terms, kept apart from identity classes.
      no_naming_claim    entries whose shared genes are all housekeeping-like (GLUL, VIM, CLU).
                         Ordering is unchanged, but do not name a cell type from these alone.

    Check locally first: this is the first step of the annotation workflow, before any online
    literature search.
    """
    resp = core.query_marker(genes=genes, cell_type=cell_type or None,
                             library=library or "all",
                             species=species or None, volume_id=volume_id or None,
                             volume_species=volume_species or None, tissue=tissue or None)
    _trace_args = {"genes": genes, "cell_type": cell_type, "library": library}
    if species or volume_id or volume_species:
        _trace_args.update({k: v for k, v in (("species", species), ("volume_id", volume_id),
                                              ("volume_species", volume_species)) if v})
    if tissue:
        _trace_args["tissue"] = tissue
    calllog.trace("query_marker", _trace_args, resp)
    return resp


@app.tool()
def get_tissue_composition(species: str, tissue: str, disease: str = "",
                           development_stage: str = "") -> dict:
    """Expected cell composition for a species x tissue: per-cell-type proportion intervals, plus
    per-row provenance (PMID / dataset and evidence grade).

    species: human | mouse.
    tissue:  retina | fibrovascular_membrane | ... (the response reports what is covered).
    disease: optional, e.g. "proliferative diabetic"; empty = normal tissue.
    development_stage: empty = the adult baseline (donors 18y+, non-adult donors removed row by
      row and listed in stage_disclosure / excluded_nonadult_units). "fetal" or "developing"
      returns the developmental transition entry instead -- adult numbers must not answer a
      fetal question, even for the same tissue. "unknown" = only entries whose disclosure files
      carry no age column.

    How to read it: these are reference intervals, not acceptance thresholds. A proportion
    clearly outside its interval raises an advisory flag for you to revisit -- it can be a
    sampling difference, an enrichment protocol, or an annotation error. Contrast and QC only:
    never feed these numbers into scoring.

    Call this before annotating, to fix what the tissue should contain and roughly how much.
    """
    resp = core.get_tissue_composition(species, tissue, disease, development_stage)
    calllog.trace("get_tissue_composition",
                  {"species": species, "tissue": tissue, "disease": disease,
                   "development_stage": development_stage}, resp)
    return resp


@app.tool()
def get_disease_prior(disease: str, tissue: str = "") -> dict:
    """Disease x tissue background layer: the expected cell-type x status matrix, flags for
    unexpected and contamination-suspect populations, marker signatures, and provenance.

    disease: built-in aliases, e.g. "PDR" or "proliferative diabetic retinopathy".
    tissue:  optional filter, e.g. fibrovascular_membrane, vitreous, retina_adjacent.

    How to read it: a prior is not truth. When the data and the prior clash, the response returns
    the clash list for you to adjudicate. Do not force a fit, and do not feed the prior into
    scoring.
    """
    resp = core.get_disease_prior(disease, tissue)
    calllog.trace("get_disease_prior", {"disease": disease, "tissue": tissue}, resp)
    return resp


if __name__ == "__main__":
    app.run(transport="stdio")

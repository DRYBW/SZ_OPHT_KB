#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB MCP stdio server — ophthalmic knowledge-base evidence service.

Five tools: three retrieval/evidence tools plus two interpretation-layer tools.

Tool inventory:
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
1. This service provides [EVIDENCE AND CITATIONS] only. Feeding the returned content into any
   scoring/classification pipeline is forbidden: it must not be converted into a module score,
   label weighting, confidence bonus, candidate-ranking score or composite QC score.
2. Transport = local stdio; no network port is opened.
3. The knowledge base directory is resolved through kb/literature_db/EYEKB_DB_POINTER.yaml and is
   opened read-only. Nothing outside it is read or written.
4. Interpretation-layer usage follows the four-stage annotation protocol shipped in
   docs/skills/protocols/ANNOTATION_PROTOCOL_v1.3.md (fix the expected composition first, then
   contrast).

Running it (MCP client configuration):
  command: <python interpreter with this repository's requirements installed>
  args:    ["<path to this repository>/mcp_server/server.py"]
  Transport is local stdio; no port is opened and no outbound request is made.
  The literature corpus for search_literature resolves in this order: environment variable
  EYEKB_DB_DIR -> the entry marked `role: default` in kb/literature_db/EYEKB_DB_POINTER.yaml that
  exists on disk -> the single unpacked corpus inside this repository. The other four tools read
  the repository's own kb/ directory only, so a fresh clone needs no configuration for them.
  Toggles and the CJK query bridge are documented in the repository README.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eyekb_core as core  # noqa: E402
import calllog  # call-tracing layer: logging only, no change in behaviour (see mcp_server/calllog.py)

from mcp.server import MCPServer  # noqa: E402
from mcp.types import ToolAnnotations  # noqa: E402


def _read_only(title: str) -> ToolAnnotations:
    """Annotation shared by every tool in this service: it only reads from the bundled
    knowledge base. No writes, no outbound network calls, and repeated calls with the same
    arguments return the same answer.

    The hints are passed by their wire names (camelCase) and accepted as such by every
    MCP SDK release this server is known to run under.
    """
    return ToolAnnotations(title=title, readOnlyHint=True, destructiveHint=False,
                           idempotentHint=True, openWorldHint=False)

app = MCPServer(
    name="eyekb",
    title="EyeKB ophthalmic knowledge-base evidence service",
    version="KB1v2-0.14-kb11a-reasonjoin",
    description=("Ophthalmic knowledge base for cell-type annotation. (1) Literature retrieval over a "
                 "bundled corpus of 2,713 papers / 174,616 passages covering the whole eye; each result "
                 "carries PMID, journal, year, co-occurring markers, a relevance score and the "
                 "inclusion_reasons / claim_relation / evidence_context fields plus a verification status. "
                 "(2) Knowledge-base index pages (tissue and topic). (3) A local authoritative marker "
                 "library, queryable as a whole or by library name (retina, retina_interneuron, retina_v6, "
                 "retina_v7, retina_dev, face_v6, membrane, k9_ocs, lacrimal_v6), with species routing for "
                 "gene-symbol queries. (4) An interpretation layer: donor-level expected-composition "
                 "baselines and a disease x tissue matrix with sampling-material mismatch warnings. "
                 "Red line: returned content is evidence for human interpretation and QC only; it must not "
                 "become input to any score, weighting, ranking or composite QC score. "
                 "Behaviour toggles, each of which restores the previous behaviour when switched off: "
                 "EYEKB_ACT_V6, EYEKB_ACT_ANTSEG, EYEKB_KBGOV_B5, EYEKB_CN_REWRITE; the additional marker "
                 "libraries are opt-in by name and never enter the default set. Optional libraries stay "
                 "reachable by explicit query only, in any state."),
    instructions=("EyeKB five tools: query_marker checks the local marker library first; "
                  "search_literature retrieves literature evidence (everything traceable via PMID); "
                  "get_kb_page reads tissue/topic index pages; before annotating, follow the four stages of "
                  "the annotation protocol (docs/skills/protocols/ANNOTATION_PROTOCOL_v1.3.md) using "
                  "get_tissue_composition (against the actual sampling material!) / get_disease_prior "
                  "(call it only in the post-freeze disease-contrast stage). "
                  "Red line: returned content is for human interpretation evidence and QC flags only, and "
                  "must not become input to any score/weighting/ranking/composite QC score. "
                  "soft_flags.notes: optional review clues — check them against the original "
                  "evidence; their presence does not imply mis-annotation, they add no naming/abstention/"
                  "candidate-exclusion conditions, and they must not be used as input to any score, "
                  "weighting, confidence, or ranking; notes are attached only after existing results are "
                  "produced and never feed back to change candidates, scores, ordering, or original QC "
                  "fields."),
)


@app.tool(title="Search ophthalmic literature", annotations=_read_only("Search ophthalmic literature"))
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
    terms in place without deleting any of your characters; it is not a translator. The bridge
    table ships separately: point EYEKB_CN_BRIDGE_TSV at one to enable it, otherwise your query
    runs unchanged and rewrite_meta reports bridge_missing. English, numeric and symbolic queries
    never enter the layer. A Chinese query's response carries a rewrite_meta key disclosing what
    was inserted -- disclosure only, it never affects ranking. Set EYEKB_CN_REWRITE=0 to turn the
    bridge off.
    """
    resp = core.search_literature(
        cell_type, species=species or None, tissue=tissue or None,
        top_k=top_k, query=query or None, db=db or None)
    calllog.trace("search_literature",
                  {"cell_type": cell_type, "species": species, "tissue": tissue,
                   "top_k": top_k, "query": query, "db": db}, resp)
    return resp


@app.tool(title="Read knowledge-base page", annotations=_read_only("Read knowledge-base page"))
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


@app.tool(title="Look up marker library", annotations=_read_only("Look up marker library"))
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


@app.tool(title="Expected tissue composition", annotations=_read_only("Expected tissue composition"))
def get_tissue_composition(species: str, tissue: str, disease: str = "",
                           development_stage: str = "", detail: str = "full") -> dict:
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

    detail: "full" (default) returns the complete record, including the stratum breakdown, the
    stage disclosure and the caliber metadata. "answer" returns the proportions, the state layer,
    the flags and the caveats only, and names what it left out in omitted_fields. Use "answer" when
    you are reading the numbers rather than auditing them; every row keeps its own citations either
    way.
    """
    resp = core.get_tissue_composition(species, tissue, disease, development_stage, detail)
    calllog.trace("get_tissue_composition",
                  {"species": species, "tissue": tissue, "disease": disease,
                   "development_stage": development_stage, "detail": detail}, resp)
    return resp


@app.tool(title="Disease x tissue prior", annotations=_read_only("Disease x tissue prior"))
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


@app.tool(title="Explain an annotation", annotations=_read_only("Explain an annotation"))
def explain_annotation(cell_type: str, tissue: str = "", top_k: int = 5) -> dict:
    """Evidence trail behind a cell-type label: the markers that identify it, the knowledge-base
    library it comes from, the pages that describe it, any textbook edition+page behind its
    definition, and the papers that back it.

    cell_type: the label to explain (e.g. "RPE", "Muller glia", "lens fiber cell").
    tissue: optional filter over the attached citations.
    top_k: how many citations to return.

    Each citation carries PMID + journal + year and resolves inside the corpus shipped with this
    server, so a reader can check the trail without network access. Call this when writing up an
    annotation and the citation has to be shown next to the label.
    Disclosure surface: not an input to any score, weighting, ranking or confidence measure.
    """
    resp = core.explain_annotation(cell_type, tissue=tissue or None, top_k=top_k)
    calllog.trace("explain_annotation",
                  {"cell_type": cell_type, "tissue": tissue, "top_k": top_k}, resp)
    return resp


if __name__ == "__main__":
    app.run(transport="stdio")

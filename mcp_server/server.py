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
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eyekb_core as core  # noqa: E402
import calllog  # call-tracing layer: logging only, no change in behaviour (see mcp_server/calllog.py)
import corpus_stats  # bundled-corpus numbers for the description below (see mcp_server/corpus_stats.py;
                     # machine gate G11 tests/gate_mcpdesc_corpus.py pins it to the bundled build_stats.json
                     # and to the pointer's registered v2.4.2 identity; frozen fallback for fresh clones)

from mcp.server import MCPServer  # noqa: E402
from mcp.types import ToolAnnotations  # noqa: E402

# --- release identity ----------------------------------------------------------------
# The handshake carries a protocol generation label; that label describes the wire contract and
# has to stay stable. What changes from release to release is the identity of the shipped bytes,
# so the label is followed by that identity here, and a caller can also ask for it explicitly
# (get_release_identity). Both read docs/RELEASE_IDENTITY.json, which
# scripts/release_identity.py re-takes in the same commit as any byte change.
PROTOCOL_GENERATION = "KB1v2-0.14-kb11a-reasonjoin"
IDENTITY_RECORD = Path(__file__).resolve().parent.parent / "docs" / "RELEASE_IDENTITY.json"


def _release_info():
    blank = {"release_id": "unrecorded", "protocol_generation": PROTOCOL_GENERATION,
             "taken_at_commit": "", "n_files": 0, "algorithm": "",
             "coverage": "", "source": "docs/RELEASE_IDENTITY.json (absent or unreadable)",
             "recorded": False}
    try:
        rec = json.loads(IDENTITY_RECORD.read_text(encoding="utf-8"))
    except Exception:
        return blank
    out = dict(blank)
    for k in ("release_id", "taken_at_commit", "n_files", "algorithm", "coverage",
              "protocol_generation", "service_build_id", "knowledge_bundle_id",
              "effective_profile_id"):
        if k in rec and rec[k] not in (None, ""):
            out[k] = rec[k]
    out["source"] = "docs/RELEASE_IDENTITY.json"
    out["recorded"] = bool(rec.get("release_id"))
    return out


RELEASE_INFO = _release_info()
SERVER_VERSION = f"{PROTOCOL_GENERATION}+{RELEASE_INFO['release_id']}"


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
    version=SERVER_VERSION,
    description=("Ophthalmic knowledge base for cell-type annotation. (1) Literature retrieval over a "
                 f"bundled corpus of {corpus_stats.BUNDLED_CORPUS_LINE} covering the whole eye; each result "
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
    instructions=("EyeKB tools: query_marker checks the local marker library first; "
                  "search_literature retrieves literature evidence (everything traceable via PMID); "
                  "get_kb_page reads tissue/topic index pages; before annotating, follow the four stages of "
                  "the annotation protocol (docs/skills/protocols/ANNOTATION_PROTOCOL_v1.3.md) using "
                  "get_tissue_composition (against the actual sampling material!) / get_disease_prior "
                  "(call it only in the post-freeze disease-contrast stage). "
                  "get_release_identity reports which release of this service is answering. "
                  "Before any comparison, declare the tissue from the dataset's own metadata "
                  "(docs/TISSUE_DECLARATION_RULE.md); a declaration chosen after the score is read "
                  "is not admissible. "
                  "Red line: returned content is for human interpretation evidence and QC flags only, and "
                  "must not become input to any score/weighting/ranking/composite QC score. "
                  "soft_flags.notes: optional review clues — check them against the original "
                  "evidence; their presence does not imply mis-annotation, they add no naming/abstention/"
                  "candidate-exclusion conditions, and they must not be used as input to any score, "
                  "weighting, confidence, or ranking; notes are attached only after existing results are "
                  "produced and never feed back to change candidates, scores, ordering, or original QC "
                  "fields."),
)


# --- ontology explanation layer: registered, read-only, OFF by default -------------------------
# The capability (resolve_term / get_ancestors / compare_terms / explain_class_mapping) is
# registered in kb/ontology/ONT_LAYER_REGISTRY_v1.json with an EMPTY whitelist: nothing is
# advertised and nothing is imported unless the route variable names the tool explicitly. With the
# route unset, the advertised tool list and every answer are byte-identical to the release before
# this capability existed (tests/probe_tool_panel_identity.py, and the recorded request replay in
# docs/plans/l5_ontlayer_20261022/).
ONT_LAYER_TOOLS = ("resolve_term", "get_ancestors", "compare_terms", "explain_class_mapping")
ONT_LAYER_ROUTE_ENV = "EYEKB_ONT_LAYER"
ONT_LAYER_REGISTRY = Path(__file__).resolve().parent.parent / "kb" / "ontology" / \
    "ONT_LAYER_REGISTRY_v1.json"


def _ont_layer_route():
    """The explicitly routed tools, in registry order. Empty unless the caller names them."""
    raw = os.environ.get(ONT_LAYER_ROUTE_ENV) or ""
    named = [t.strip() for t in raw.split(",") if t.strip()]
    return [t for t in ONT_LAYER_TOOLS if t in named]


ONT_LAYER_ROUTED = _ont_layer_route()
_ont = None
if ONT_LAYER_ROUTED:                       # imported only when explicitly routed
    import ontology_layer as _ont        # noqa: E402


def _ont_call(fn, **kw):
    """One call into the layer. A snapshot that cannot be read is reported as it is - the layer
    never answers from a placeholder, and a missing shipped asset is a defect, not an environment
    error."""
    try:
        snap = _ont.layer()
    except Exception as e:                                   # repository root not found
        return {"error": "ontology_layer_unavailable", "reason": f"{type(e).__name__}: {e}",
                "note": "the layer could not resolve its assets; no answer is produced from "
                        "anything else"}
    if snap.anchor.get("status") != "RESOLVED":
        return {"error": "ontology_anchor_not_resolved",
                "anchor": snap.anchor.get("anchor"),
                "anchor_status": snap.anchor.get("status"),
                "manifest": snap.anchor.get("manifest"),
                "note": "the fixed ontology snapshot is missing or its hash does not match the "
                        "recorded one. That is a delivery defect; no answer is produced from an "
                        "unverified snapshot."}
    return fn(snap, **kw)


@app.tool(title="Search ophthalmic literature", annotations=_read_only("Search ophthalmic literature"))
def search_literature(cell_type: str, top_k: int = 5, species: str = "",
                      tissue: str = "", query: str = "", db: str = "",
                      dev_stage: str = "") -> dict:
    """Retrieve literature passages for a cell type / tissue from the bundled ophthalmic corpus.
    Returns passage text, PMID, journal, year, the marker genes that co-occur, and a relevance
    score. top_k controls how many passages come back (default 5).

    cell_type: metadata filter, e.g. "Muller glia" or "corneal endothelium". Recommended.
    species:   human | mouse | "" (no filter).
    tissue:    multi-label tissue filter, e.g. retina, cornea, RPE, choroid.
    query:     your own search sentence; when empty, a template sentence is built from cell_type.
    db:        empty = default resolution (EYEKB_DB_DIR env -> the pointer's role:default corpus -> the
               bundled v2.4.2_2026-09_slim corpus), or an absolute path to another corpus.
    dev_stage: "" / "any" (default) = the adult face, which excludes fetal-only and developing-only
               papers. "fetal_developing" | "adult" | "unknown" = ask for that stage explicitly; the
               gate stands down and that stage's own papers are returned. Fetal / developing work is
               kept in the corpus and reachable this way — it is put on its own shelf, not deleted.

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
        top_k=top_k, query=query or None, db=db or None,
        dev_stage=dev_stage or None)
    calllog.trace("search_literature",
                  {"cell_type": cell_type, "species": species, "tissue": tissue,
                   "top_k": top_k, "query": query, "db": db, "dev_stage": dev_stage}, resp)
    return resp


def _normalise_detail(value):
    """Fold a caller's detail argument to one of the recognised tiers, or "" (no choice made).

    Recognised: "full", "answer" (the page inventory / compact answer), "outline" (a page's
    structure without its bulk) and "slice" (consecutive verbatim lines). Unrecognised non-empty
    values keep the pre-change behaviour ("full") rather than silently downgrading a caller who
    typed something the tool does not know. A boolean is accepted because callers have passed one:
    `True` used to raise AttributeError inside the core, so it now means "full" and `False` means
    "answer" — the same reading a human gives those two words.
    """
    if isinstance(value, bool):
        return "full" if value else "answer"
    if value is None:
        return ""
    s = str(value).strip().lower()
    if s in ("answer", "compact", "brief", "short"):
        return "answer"
    if s in ("outline", "toc", "structure"):
        return "outline"
    if s in ("slice", "lines", "paged"):
        return "slice"
    if s in ("full", "heavy", "all"):
        return "full"
    return "full" if s else ""


def _default_tier(fallback="answer"):
    """The shipped default tier, with a single-variable revert path.

    Unset or unrecognised -> `fallback`. `EYEKB_DEFAULT_DETAIL=full` makes the heavy tier the
    default again for every tool that reads this, which is the revert path the card pre-registers.

    The environment name is written literally rather than through a constant on purpose: the switch
    registry generator scans the source for `os.environ` reads, so a name reached through a variable
    would become a switch nobody can find in docs/SWITCH_COVERAGE_REGISTRY.tsv.
    """
    raw = str(os.environ.get("EYEKB_DEFAULT_DETAIL") or "").strip().lower()
    if raw in ("full", "heavy", "all"):
        return "full"
    if raw in ("answer", "compact", "brief", "short"):
        return "answer"
    return fallback


def _tier_note(tier, extra=""):
    """Disclosure block for a tier the caller did not ask for. A smaller answer may not hide that
    it is smaller: the note names the tier and the one call that returns the whole thing."""
    note = (
        "This is the compact default tier. Nothing was removed from the knowledge base and the "
        "full answer is one call away: pass detail=\"full\" (on get_kb_page, summary=False does "
        "the same thing). Set EYEKB_DEFAULT_DETAIL=full to make the full tier the default again."
    )
    if extra:
        note = note + " " + extra
    return {"detail_applied": tier, "detail_note": note}


PAGE_OUTLINE_THRESHOLD = 20000   # characters; above this a page defaults to its outline
SLICE_DEFAULT_LINES = 100        # verbatim lines per slice when the caller does not say


def _split_lines(text):
    """The page as lines, with the rule that makes slicing lossless: "\\n".join(all slices) == text."""
    return str(text).split("\n")


def _outline_view(scope, name, text):
    """Structure without the bulk: headings, per-section sizes, paper counts, year histogram.

    Every number here is derived from the text handed in, at call time. The counting rule is stated
    in the response (chars_taken_as = 'len(line) + 1 for each line in the section, terminator
    included'), so a reader can recompute it rather than trust it.
    """
    lines = _split_lines(text)
    front, body_start = {}, 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                for ln in lines[1:i]:
                    k, _, v = ln.partition(":")
                    if k.strip():
                        front[k.strip()] = v.strip()
                body_start = i + 1
                break
    sections, cur = [], None
    for idx in range(body_start, len(lines)):
        ln = lines[idx]
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            cur = {"level": len(m.group(1)), "heading": m.group(2).strip(),
                   "start_line": idx + 1, "lines": 0, "chars": 0, "paper_rows": 0}
            sections.append(cur)
        elif cur is not None:
            cur["lines"] += 1
            cur["chars"] += len(ln) + 1
            if ln.startswith("- PMID"):
                cur["paper_rows"] += 1
    years, papers = {}, 0
    for ln in lines:
        if ln.startswith("- PMID"):
            papers += 1
            m = re.search(r"\((\d{4})\)", ln)
            if m:
                years[m.group(1)] = years.get(m.group(1), 0) + 1
    heads = [s["heading"] for s in sections]
    return {
        "scope": scope, "name": name, "view": "outline",
        "chars": len(text), "lines": len(lines),
        "front_matter": front,
        "sections": sections,
        "papers": {"rows": papers, "by_year": dict(sorted(years.items()))},
        "headings_unique": len(heads) == len(set(heads)),
        "chars_taken_as": "len(line) + 1 per line in the section, terminator included",
        "read_it": {
            "part": "detail=\"slice\" with offset/limit (default %d lines); slices concatenate with "
                    "a newline and reproduce the page exactly" % SLICE_DEFAULT_LINES,
            "whole": "detail=\"full\" (or summary=false) returns the page text",
        },
    }


def _slice_view(scope, name, text, offset, limit):
    """Consecutive verbatim lines. No parsing, so the union of all slices is the page."""
    lines = _split_lines(text)
    try:
        off = int(offset)
    except (TypeError, ValueError):
        off = 0
    try:
        lim = int(limit)
    except (TypeError, ValueError):
        lim = SLICE_DEFAULT_LINES
    if off < 0 or lim <= 0:
        return {"error": "offset must be >= 0 and limit must be > 0",
                "got": {"offset": offset, "limit": limit},
                "total_lines": len(lines),
                "hint": "use offset=0 and a positive limit; detail=\"outline\" first if you need "
                        "to know how big the page is"}
    part = lines[off:off + lim]
    nxt = off + len(part)
    eof = nxt >= len(lines)
    return {
        "scope": scope, "name": name, "view": "slice",
        "total_lines": len(lines), "offset": off, "limit": lim,
        "returned": len(part), "next_offset": None if eof else nxt, "eof": eof,
        "join": "\\n",
        "lines": part,
    }


@app.tool(title="Read knowledge-base page", annotations=_read_only("Read knowledge-base page"))
def get_kb_page(scope: str, name: str = "", summary: bool | None = None,
                detail: str = "", offset: int = 0,
                limit: int = SLICE_DEFAULT_LINES) -> dict:
    """Read a knowledge-base page as shipped (markdown).
      scope="index"              the master catalog of every page.
      scope="topic", name="..."  a topic page, e.g. vascular.
      scope="tissue",name="..."  a tissue page, e.g. cornea, RPE, trabecular_meshwork.
    scope is required; name is required for topic and tissue. An unknown path is rejected and
    the response lists the pages that do exist.

    Size first. The index is about 140,000 characters of text but about 4,000 as an inventory, so
    scope="index" defaults to the inventory. One page runs from about 1,500 to about 191,000
    characters, so a page above 20,000 characters defaults to its OUTLINE: headings, per-section
    sizes, how many paper lines and a year histogram. A shorter page is returned in full.

    detail: "outline" = structure only; "slice" = consecutive verbatim lines (offset/limit, default
    100 lines, and the slices concatenate with a newline to reproduce the page exactly); "full" =
    the page text; "answer" = the page inventory. Empty means the default above. Same field name as
    get_tissue_composition, so one habit covers both tools. summary=true still equals
    detail="answer"; an explicit detail wins if the two disagree.
    """
    sc = str(scope or "").strip().lower()
    _d = _normalise_detail(detail)
    implicit = not _d
    if implicit and summary is not None:
        _d = "answer" if summary else "full"
        implicit = False   # an explicit `summary` is a caller choice, so its bytes stay as shipped
    if implicit and sc == "index":
        _d = _default_tier("answer")     # the catalogue: an inventory unless the revert is set

    if _d == "answer":
        resp = core.get_kb_page(scope, name, True)
        if implicit and isinstance(resp, dict):
            resp = dict(resp)
            resp.update(_tier_note("answer"))
        calllog.trace("get_kb_page", {"scope": scope, "name": name, "summary": True,
                                      "detail": _d, "implicit": implicit}, resp)
        return resp

    # Everything else needs the page text. Fetch once, then shape it.
    resp = core.get_kb_page(scope, name, False)
    text = resp.get("content") if isinstance(resp, dict) else None
    if text is None:      # rejected path / missing page: hand the core's own answer back untouched
        calllog.trace("get_kb_page", {"scope": scope, "name": name, "summary": False,
                                      "detail": _d or None, "implicit": implicit}, resp)
        return resp

    if implicit:
        heavy = _default_tier("outline")          # EYEKB_DEFAULT_DETAIL=full -> "full"
        _d = ("outline" if heavy != "full" and len(text) > PAGE_OUTLINE_THRESHOLD else "full")

    if _d == "outline":
        out = _outline_view(scope, name, text)
    elif _d == "slice":
        out = _slice_view(scope, name, text, offset, limit)
    else:
        out = resp                                # "full": byte-for-byte what the core returned

    if implicit and isinstance(out, dict) and _d != "full":
        extra = ""
        if _d == "outline":
            extra = ("This page is %d characters, so the outline is the default; read any part of it "
                     "with detail=\"slice\" and offset/limit." % len(text))
        out = dict(out)
        out.update(_tier_note(_d, extra))
    calllog.trace("get_kb_page", {"scope": scope, "name": name, "summary": False,
                                  "detail": _d, "implicit": implicit,
                                  "offset": offset, "limit": limit}, out)
    return out


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
                           development_stage: str = "", detail: str = "") -> dict:
    """Expected cell composition for a species x tissue: per-cell-type proportion intervals, plus
    per-row provenance (PMID / dataset and evidence grade).

    species: human | mouse.
    tissue:  retina | fibrovascular_membrane | ... (the response reports what is covered).
    disease: optional, e.g. "proliferative diabetic"; empty = normal tissue.
    development_stage: empty = the adult baseline (donors 18y+). "fetal" or "developing"
      returns that stage instead, because adult numbers must not answer a fetal question even
      for the same tissue. An unrecognised literal (including "organoid") reaches the unknown
      tier and names itself in a stage_literal block rather than silently falling back to adult.

    How to read it: reference intervals, not acceptance thresholds. A proportion clearly
    outside its interval raises an advisory flag to revisit -- a sampling difference, an
    enrichment protocol, or an annotation error. Contrast and QC only; never feed these numbers
    into scoring.

    Call this before annotating, to fix what the tissue should contain and roughly how much.

    Size: about 91,000 characters in full, so the default is the compact tier. detail="answer"
    keeps the proportions, the state layer, the flags and the caveats, and names what it left out
    in omitted_fields -- about 25,000 characters. Every row keeps its own citations either way, so
    the compact tier is not an evidence-poor tier. detail="full" returns everything, and
    EYEKB_DEFAULT_DETAIL=full restores the full tier as the default.
    """
    _d = _normalise_detail(detail)
    implicit = not _d
    if implicit:
        _d = _default_tier("answer")
    resp = core.get_tissue_composition(species, tissue, disease, development_stage, _d)
    if implicit and _d == "answer" and isinstance(resp, dict):
        resp = dict(resp)
        resp.update(_tier_note("answer"))
    calllog.trace("get_tissue_composition",
                  {"species": species, "tissue": tissue, "disease": disease,
                   "development_stage": development_stage, "detail": _d,
                   "implicit": implicit}, resp)
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

    cell_type: the label to explain (e.g. "RPE", "Muller glia", "lens fiber cell"). Both the
    library's own short name ("MG") and the Cell Ontology label for the same entry ("Mueller cell")
    resolve to the same record; the response says which one was used in matched_by.
    tissue: optional filter over the attached citations.
    top_k: how many citations to return.

    Each citation carries PMID + journal + year and resolves inside the corpus shipped with this
    server, so a reader can check the trail without network access. Each one also says whether it was
    checked against the paper's own full text: gene_match is true when at least one of the entry's
    marker genes actually occurs in that paper, genes_in_text lists which, and evidence_locator gives
    the chunk and section. gene_match false means the paper is about the cell type but does not name
    the genes used here. Call this when writing up an annotation and the citation has to be shown
    next to the label.
    Disclosure surface: not an input to any score, weighting, ranking or confidence measure.
    """
    resp = core.explain_annotation(cell_type, tissue=tissue or None, top_k=top_k)
    calllog.trace("explain_annotation",
                  {"cell_type": cell_type, "tissue": tissue, "top_k": top_k}, resp)
    return resp


# --- the four ontology tools: registered only when explicitly routed ---------------------------
# Titles say what they do; the docstrings say what the answer is and is not. They do not write to
# the call log: the capability's claim is that it reads and nothing else.
if "resolve_term" in ONT_LAYER_ROUTED:

    @app.tool(title="Resolve a Cell Ontology term", annotations=_read_only("Resolve a Cell Ontology term"))
    def resolve_term(term: str) -> dict:
        """Which Cell Ontology term is this, and how sure is that?

        term: a CL identifier, a preferred label, an alternate identifier, or an exact synonym.

        The answer separates what the graph says from what may be concluded. resolution_status is
        explicit, and a non-unique match is never resolved by preference: same-label-different-concept
        and synonym ambiguity both come back as `ambiguous` with the candidates listed, for review.
        An obsolete term is reported as obsolete, and a replacement is named only when the ontology
        declares exactly one. `assessment` states whether the answer is usable here, and is
        `not_assessed` when no task context was supplied.

        Read-only, deterministic, single fixed snapshot (release and file hash in the answer). Not
        an input to any score, weighting, ranking or confidence measure.
        """
        return _ont_call(lambda s, **k: s.resolve_term(term))


if "get_ancestors" in ONT_LAYER_ROUTED:

    @app.tool(title="Cell Ontology ancestors", annotations=_read_only("Cell Ontology ancestors"))
    def get_ancestors(term: str, max_depth: int = 0) -> dict:
        """What the `is_a` graph says is above a term, and along which path.

        term: as resolve_term. max_depth: 0 = every ancestor, otherwise that many levels up.

        Every ancestor carries the levels above, the shortest path from the term, the line of the
        ontology file it was read from, and whether it is an extremely broad ("blanket") ancestor -
        a relation that only reaches such a term does not meet the minimum reporting granularity.
        Ancestors declared or implied outside the snapshot are counted, not invented.
        """
        return _ont_call(lambda s, **k: s.get_ancestors(term, max_depth))


if "compare_terms" in ONT_LAYER_ROUTED:

    @app.tool(title="Compare two Cell Ontology terms", annotations=_read_only("Compare two Cell Ontology terms"))
    def compare_terms(ours: str, theirs: str, evidence_source: str = "",
                      evidence_assertion: str = "", context: str = "") -> dict:
        """How do two terms relate, and how far may that relation be used?

        ours / theirs: CL identifiers or labels (resolved as in resolve_term).
        evidence_source / evidence_assertion: explicit incompatibility evidence, if you have it.

        The verdict is one of five buckets: same_term, ours_broader, ours_narrower,
        confirmed_incompatible, not_supported_by_is_a. A coarser answer is a resolution limitation,
        not a biological error. No ancestor relation is NOT proof of mutual exclusion: it is
        reported as not_supported_by_is_a, which is neither counted as correct nor announced as a
        confirmed error, and `confirmed_incompatible` is reached only when incompatibility evidence
        is supplied, in which case it is recorded with the verdict.

        Two records come back side by side and neither is derived from the other: `is_a_relation`
        (what the graph says) and `assessment` (whether the answer holds under this sample, task
        granularity and evidence), each with ancestor_path and unresolved_reason.
        """
        return _ont_call(lambda s, **k: s.compare_terms(
            ours, theirs, evidence_source=evidence_source,
            evidence_assertion=evidence_assertion, context=context))


if "explain_class_mapping" in ONT_LAYER_ROUTED:

    @app.tool(title="Explain a class mapping", annotations=_read_only("Explain a class mapping"))
    def explain_class_mapping(internal_class_id: str, reference_term: str = "") -> dict:
        """What backs the mapping this library ships for one of our classes?

        internal_class_id: a library class or short name, e.g. "RPE" or "Rod".
        reference_term: optional - a term to compare the mapped CL term against.

        Returns the shipped mapping (source file and its hash), whether the term it names is
        present in the fixed snapshot, the graph facts behind it (parents, multiple inheritance,
        ancestor and descendant counts, any declared developmental relation) and an assessment.
        A class with no shipped mapping is reported as not_mapped; nothing is invented for it, and
        the shipped class dictionary is never rewritten.
        """
        return _ont_call(lambda s, **k: s.explain_class_mapping(internal_class_id,
                                                                reference_term))


@app.tool(title="Report the release identity",
          annotations=_read_only("Report the release identity"))
def get_release_identity() -> dict:
    """Which release of this service is answering?

    Returns the release identity derived from the shipped bytes (docs/RELEASE_IDENTITY.json),
    the protocol generation label carried in the handshake, and how to recompute the identity
    (`python3 scripts/release_identity.py --check`). The identity changes whenever the
    tracked bytes ship differently, so two releases are distinguishable without comparing
    commits by hand. Call this when a result has to be tied to a release.

    It is an explicit call by design: the identity is not injected into the answers of the
    other tools, because their bytes are the evidence surface and are captured by
    tests/fixtures/tool_panel_baseline.json. Disclosure surface only: not an input to any
    score, weighting, ranking or confidence measure.
    """
    resp = {k: RELEASE_INFO[k] for k in ("release_id", "protocol_generation", "taken_at_commit",
                                         "n_files", "algorithm", "coverage", "source", "recorded")}
    resp["recompute"] = "python3 scripts/release_identity.py --check"
    resp["handshake_version"] = SERVER_VERSION
    # Release identity in four layers (a caller needs the resolvable manifest identifier together
    # with the configuration that was actually in force), plus the release manifest it is bound to.
    resp["identity_layers"] = {
        "protocol_generation": RELEASE_INFO.get("protocol_generation") or PROTOCOL_GENERATION,
        "service_build_id": RELEASE_INFO.get("service_build_id"),
        "knowledge_bundle_id": RELEASE_INFO.get("knowledge_bundle_id"),
        "effective_profile_id": RELEASE_INFO.get("effective_profile_id"),
        "release_manifest": "docs/RELEASE_MANIFEST_v1.json",
        "note": ("The four layers are separate on purpose: the wire contract, the server code, the "
                 "shipped knowledge assets, and what actually took effect in this run. "
                 "effective_profile_id is taken over the observed toggle values and the registered "
                 "capabilities, with volatile fields excluded, so the same configuration gives the "
                 "same value on any day."),
    }
    resp["registered_capabilities"] = [{
        "capability_id": "ont_explain_layer",
        "registered": True,
        "default_state": "OFF",
        "whitelist": [],
        "route_env": ONT_LAYER_ROUTE_ENV,
        "advertised_now": list(ONT_LAYER_ROUTED),
        "registry": "kb/ontology/ONT_LAYER_REGISTRY_v1.json",
        "note": ("Registered read-only and OFF by default with an empty whitelist: the four "
                 "ontology tools are advertised only when the route variable names them "
                 "explicitly, and are never part of the default tool set."),
    }] if ONT_LAYER_REGISTRY.is_file() else []
    resp["note"] = ("Identity of the shipped bytes of this checkout. An identity that does not "
                    "match the release you intend to cite means the checkout moved: re-run "
                    "`python3 scripts/release_identity.py` to see the current value.")
    calllog.trace("get_release_identity", {}, resp)
    return resp


if __name__ == "__main__":
    app.run(transport="stdio")

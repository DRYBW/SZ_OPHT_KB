#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB tool kernel (pure implementation of the three tools, decoupled from the MCP transport layer)

Discipline red lines (inherited from KB_SPINOUT_MCP_DESIGN_v0 §6 + USER_DIRECTIVE_20260923):
1. The evidence service never enters scoring — this module only provides retrieval/page/marker facts;
   no consumer may use the returned content as classification-scoring input (Claude5 frozen ruling,
   service-level red line).
2. Copy, never move — all paths this module reads: on the EyeKB side they are P0/P1a copies; the RAG
   library and embedding model reference the current OcularKB paths during P1 (read-only).
3. Marker-query order mechanized: query_marker is the first step of the annotation workflow; never go
   online before checking local.
"""
import gzip
import json
import os
import re
import sys
from pathlib import Path

EYEKB_ROOT = Path(__file__).resolve().parents[1]          # /mnt/D/EyeKB
CLIENTS = EYEKB_ROOT / "clients"
KB = EYEKB_ROOT / "kb"
VK_DIR = (KB / "vk_literature_index").resolve()
MARKER_JSON = KB / "markers" / "markers_v4.1_clean.json"
POINTER_YAML = KB / "literature_db" / "EYEKB_DB_POINTER.yaml"

# Soft-review hint layer (t_d6f2a0a0 / D4): appends notes only after existing results; changes no
# candidate/ordering/score
import softflags as _sf  # noqa: E402
# [SPECROUTE t_b9952795 · USER_DIRECTIVE_20261012 §三③] L1 species-route resolution layer
# (three-source priority + evidence families + forced mouse path). opt-in escape door
# EYEKB_SPECIES_ROUTE (unset = OFF = the byte-exact pre-wiring state); the sole authoritative
# criterion source = plans/x10_improve_20261012/W2_SPROUTE/SPEC_SPECIES_ROUTING.md.
import species_route as _species_route  # noqa: E402
# Query-rewrite layer (2026-10-03): Chinese query → English search expression; env EYEKB_CN_REWRITE
# default OFF; in the off state rewrite_query passes through with zero touching. Missing file/bridge =
# inert zero-disturbance state, external machines run as usual.
try:
    import rewrite_cn as _rw  # noqa: E402
except Exception:
    _rw = None

# Read-only constants on the OcularKB side (P1 references current paths; after the P2 physical
# migration, repoint to EyeKB-local)
OCULARKB_RAG = Path("/mnt/D/OcularKB/ocularkb/rag")
DEFAULT_DB_DIR = OCULARKB_RAG / "literature_db" / "v2.4.2_2026-09"  # 2026-10-01 audit fix: last fallback aligned with the default library (the old value v2.0 was a pre-switch leftover)

# Import the copied retrieval kernel (verbatim copy of ocularkb/rag/scripts/stage3_retrieve.py)
sys.path.insert(0, str(CLIENTS / "ocularkb" / "rag" / "scripts"))
import stage3_retrieve as _s3  # noqa: E402


# ---------------------------------------------------------------- Tool 1
# Default-DB resolution chain (external-machine usability fix, 2026-09-30, PI "upload it once it
# passes verification" wave):
# 1) env EYEKB_DB_DIR  2) pointer role:default entry (absolute or repo-root relative) if it exists
# 3) the repo's only corpus (auto-discovered right after a Release unpack)  4) production hard-coded
# fallback path (behavior identical to the old version)
def _default_db_dir():
    env = os.environ.get("EYEKB_DB_DIR")
    if env:
        return env
    try:
        txt = POINTER_YAML.read_text(encoding="utf-8")
        cur_path = None
        for ln in txt.splitlines():
            s = ln.strip()
            if s.startswith("path:"):
                cur_path = s.split("path:", 1)[1].strip()
            elif s.startswith("role:") and "default" in s and cur_path:
                p = Path(cur_path)
                if not p.is_absolute():
                    p = KB.parent / cur_path
                if p.is_dir():
                    return str(p)
    except Exception:
        pass
    for base in (KB / "literature_db", KB.parent / "literature_db"):
        if base.is_dir():
            cands = sorted(d for d in base.iterdir()
                           if d.is_dir() and (d / "chunks.parquet").is_file())
            if len(cands) == 1:
                return str(cands[0])
    return str(DEFAULT_DB_DIR)


def search_literature(cell_type, species=None, tissue=None, top_k=5,
                      query=None, db=None):
    """Literature-snippet retrieval: passes through to stage3_retrieve.retrieve().

    db: None → resolve the library via the _default_db_dir() chain; or an explicit directory path.
    The species/tissue/cell_type three-way filter passes through (landed per Claude5 review request).
    """
    db_dir = str(db) if db else _default_db_dir()
    # Query-rewrite layer wiring point: rewrite only when an explicit query exists and the switch is
    # on; off/empty query → zero touching.
    query_used, rw_meta = (query, None)
    if _rw is not None and query:
        query_used, rw_meta = _rw.rewrite_query(query)
    res = _s3.retrieve(cell_type, species=species or None, top_k=int(top_k),
                       query=query_used or None, tissue=tissue, db_dir=db_dir)
    # K3 additive join-table: attach inclusion_reason (intake-reason categorization) to each hit;
    # retrieval semantics untouched
    try:
        rm = _reason_map()
        for hit in (res or {}).get("results", []):
            tag = rm.get(str(hit.get("pmid")))
            if tag:
                hit.update(tag)
    except Exception:
        pass
    if rw_meta is not None and isinstance(res, dict):
        # auditable disclosure key that exists only when the switch is on (off-state responses gain no keys)
        res["rewrite_meta"] = rw_meta
    return res


# ---------------------------------------------------------------- Tool 2
_PAGE_RE_OK = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")

def list_kb_pages():
    """Index-page listing inside the whitelisted directory."""
    out = []
    for p in sorted(VK_DIR.glob("*.md")):
        kind = ("index" if p.name == "INDEX.md"
                else "tissue" if p.name.startswith("tissue-")
                else "topic")
        out.append({"page": p.stem, "scope": kind, "file": p.name})
    return out


def _first_heading(path):
    """First markdown heading of a page, used only by the summary view."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                s = line.strip()
                if s.startswith("#"):
                    return s.lstrip("#").strip()
                if s:
                    return s[:80]
    except OSError:
        return None
    return None


def get_kb_page(scope, name="", summary=False):
    """Read raw VK index pages. Whitelist anti-traversal:
    - only *.md inside kb/vk_literature_index/ allowed
    - name allows only [A-Za-z0-9_-]; after resolution the realpath must still be inside the
      whitelisted directory

    summary=True returns the page inventory (one row per page: title, path, size) instead of the
    full text. The catalogue page runs to ~139k characters, which is more than a caller usually
    wants when it only needs to see what exists. summary only reshapes the response; it never
    changes which pages are visible or how they are addressed, and the default path
    (summary=False) is byte-identical to before.
    """
    scope = (scope or "").strip().lower()
    name = (name or "").strip()
    if summary:
        rows = []
        for p in list_kb_pages():
            fname = p["file"] if isinstance(p, dict) else os.path.basename(str(p))
            f = (VK_DIR / fname).resolve()
            ok = f.is_file()
            rows.append({
                "page": p.get("page") if isinstance(p, dict) else fname,
                "scope": p.get("scope") if isinstance(p, dict) else None,
                "exists": ok,
                "chars": f.stat().st_size if ok else None,
                "title": _first_heading(f) if ok else None,
            })
        return {"scope": "summary", "n_pages": len(rows), "pages": rows}
    if scope == "index":
        fname = "INDEX.md"
    elif scope == "topic":
        fname = f"{name}.md"
    elif scope == "tissue":
        fname = f"tissue-{name}.md" if not name.startswith("tissue-") else f"{name}.md"
    else:
        return {"error": f"scope must be index|topic|tissue, got: {scope!r}",
                "available": list_kb_pages()}
    if not all(c in _PAGE_RE_OK for c in name) and scope != "index":
        return {"error": f"name contains illegal characters (whitelist [A-Za-z0-9_-]): {name!r}"}
    target = (VK_DIR / fname).resolve()
    # Double insurance: realpath prefix check (guards against ../ and symlink escapes; the check is
    # kept even on NTFS where symlinks are absent)
    if not str(target).startswith(str(VK_DIR) + os.sep) and target != VK_DIR:
        return {"error": "path traversal rejected (white-list enforcement)"}
    if target.suffix != ".md" or not target.is_file():
        return {"error": f"page not found: scope={scope} name={name}",
                "hint": "use the list view first: the returned available field enumerates all pages",
                "available": list_kb_pages()}
    return {"scope": scope, "name": name, "file": str(target),
            "content": target.read_text(encoding="utf-8")}


# ---------------------------------------------------------------- Tool 3
# Multi-marker-library support (P1opt-O4, closed-v1 pending-confirmation item 5):
#   library="retina"   → markers_v4.1_clean.json (exactly reproduces old P1 behavior)
#   library="membrane" → markers_membrane_v1.json (four panels membrane/vascular/stroma/immune)
#   library="retina_interneuron" → markers_v5_retina_interneuron.json (v5.0, KB5v2 t_9714f560 release;
#       BC/AC/HC generic core+subtype-anchor supplements, strict superset of v4.1; in single-library
#       queries the class names are the canonical names BC/AC/HC) [t_d07ab64f wiring]
#   library="all"      → merge of the active set (provenance listed per file; same-named classes are
#       presented as "<library>::<class>" alias rows per the disambiguation rule, registered-library
#       canonical names / semantics unchanged; v5-over-v4.1 takes exactly this form).
#       [ACT t_5d5853c9 · USER_DIRECTIVE_20260926 A1/A2/A5 activation switch, PI approved 2026-09-26]
#       The active set is controlled by env EYEKB_ACT_V6 (read per call, same style as softflags):
#         unset/non-off value = ON (activated default state): five libraries = the three active ones
#           + retina_v6 + face_v6.
#           retina_v6's 10 classes share names with v4.1 → merged as "retina_v6::<class>" alias rows;
#           face_v6 stromal Keratocytes/Fibroblast/Pericyte/Myofibroblast share names with membrane
#           → "face_v6::<class>" aliases; SMC plus Conj_epithelium_basal/superficial are new canonical
#           classes.
#           micro_detail/rpe_detail for Micro/RPE queries follow last-writer-wins by dbs load order →
#           in the ON state the v6 release-file detail is taken (repair-panel merge semantics, declared
#           done in the closing card).
#         ∈ {0,false,off,no} = OFF (reverted state): the three active libraries; responses are
#           canonical-serialization-equal to the pre_change baseline (A5 machine-readable acceptance,
#           sf13-style self-proof).
#       Hard-coded whitelist {retina_v6, face_v6} — lacrimal_v6 is banned from the default path in any
#       state (PI A3 ruling: not switched yet; only explicit library=lacrimal_v6 routing keeps the
#       t_e7ec73ab registration as-is).
#   —— explicit library routing (registered since t_38b99a15/t_e7ec73ab, reachable before activation;
#      activation changes its semantics not at all) ——
#   library="retina_v6" → markers_v6_retina_repair.json (v6.0-retina-repair: 10 classes' red-word
#       repairs + subtype_anchor_layer + microglia_repair; file read-only, body must not be edited)
#   library="face_v6"   → markers_v6_face_increment.json (v6.0-face: ocular-surface stromal 4 red-word
#       repairs + B1 new entries; no top-level markers key — derived by normalizing
#       stromal_repair/face_increment.core at load time, source file zero-modified;
#       granularity_note_stromal_caution is attached to hit classes)
#   library="lacrimal_v6" → markers_v6_lacrimal_increment.json (v6.0-lacrimal, KB8: lacrimal secretion/
#       duct/myoepithelial warning entries, 3 in total; likewise derived at load; reachable via
#       explicit queries only, never in the default all — PI A3 not switched yet)
#   library="k9_ocs" → markers_k9_ocs_increment.json (k9.0-ocs-registered-v1, KB9 plan-B ocular-surface
#       4 new entries: Melanocyte/Schwann/Conj_epithelium_suprabasal/Limbus_Sclera_fibroblast_C1, all
#       applicability=ocular_surface_only; each carrying CL id + OLS corroboration + per-gene PMID links.
#       [KB9REG-EXEC t_4bb75b26 · PI D17 approved registration, 2026-09-28 wave] REGISTERED_DEFAULT_OFF:
#       reachable via explicit routing only, never in the default all in any state (not in the
#       V6_DEFAULT_LIBS whitelist, same discipline as lacrimal_v6); activation requires the §10-6
#       mandatory run + separate PI approval — this registration contains no activation mechanism.
#       The companion masking/applicability + assembly rule v2 = the same-directory
#       _k9_ocs_rules_overlay_v1.json (inert data file: not read by this loader, not consumed by the
#       MCP runtime; consumption surface = evaluation/interpretation runs reading the file directly).
MARKER_DIR = (KB / "markers")
MARKER_LIBS = {"retina": MARKER_JSON,
               "membrane": MARKER_DIR / "markers_membrane_v1.json",
               "retina_interneuron": MARKER_DIR / "markers_v5_retina_interneuron.json",
               "retina_v6": MARKER_DIR / "markers_v6_retina_repair.json",
               "face_v6": MARKER_DIR / "markers_v6_face_increment.json",
    # lacrimal_v6 = KB8, the first ocular-adnexa entry library (t_e7ec73ab, 2026-09-25): 3 entries
    #   (secretion/duct/myoepithelial warning) + reference_layer; no top-level markers key — derived by
    #   normalizing lacrimal_increment.core at load (body zero-modified)
    #   [t_5d5853c9] PI A3 = not switched yet: banned from the V6_DEFAULT_LIBS whitelist, reachable via
    #   explicit routing only
    "lacrimal_v6": MARKER_DIR / "markers_v6_lacrimal_increment.json",
    # k9_ocs = KB9 plan-B ocular-surface 4 new entries (t_4bb75b26 registered, default OFF; the top-level
    #   markers key was derived and written at registration time, so loading reads it directly with no
    #   runtime derivation; copy-not-move with the build base file, whose sha is inside
    #   registration_provenance)
    "k9_ocs": MARKER_DIR / "markers_k9_ocs_increment.json",
    # retina_v7 = KB10 retina vascular/myeloid increment (t_50003494 registered, 2026-10-01):
    #   10 entries (Endo + arterial/venous/capillary partitions / Pericyte / SMC / Microglia /
    #   Macrophage / DAM_LAM / Endo_Patho), applicability=retina_only, per-gene PMID chains +
    #   OLS corroboration. REGISTERED_DEFAULT_OFF: not in the V6/K9 whitelist, the default all
    #   is zero-disturbance in any state; reachable only via explicit library=retina_v7;
    #   activation requires separate PI approval + the mandatory run + the Lukowski endothelium
    #   re-test (KB9ACT precedent). Rollback = delete this line + revert the server version
    #   pointer (see plans/kb10_retina_vascular_20261001/wire_diff).
    "retina_v7": MARKER_DIR / "markers_v7_panel_increment.json",
    # retina_dev = dev panel (v9.1-dev-panel-20261002; RW2 t_70f6340a double-pass; DEV-ACT
    #   t_f7d4985e registration + wiring): 14 entries = RPC/NRPC lineages + per-lineage
    #   precursors + TAC_proliferating/Retinal_Proliferating. SECTION B-6 scope on this surface =
    #   the library-registration row itself, so explicit library=retina_dev is reachable here;
    #   the dev-axis auto-merge (development_stage routing) is a D-side DEV-ACT wiring and is NOT
    #   part of this backflow. F3's off-domain probe already reads this path via DEV_PANEL_FILE.
    #   Rollback = delete this line (reverts to the pre-backflow dangling reference).
    "retina_dev": MARKER_DIR / "markers_v9_dev_retina.json",
    # antseg_v10 = non-retinal ocular-tissue increment (2026-10-20): 28 entries covering lens
    #   (epithelium/fibre), cornea (epithelium/endothelium/basal/transit-amplifying), conjunctiva
    #   (epithelium/goblet), trabecular meshwork, ciliary body (pigmented/non-pigmented epithelium,
    #   ciliary muscle), iris pigment epithelium, keratocytes, and the generic stromal / immune /
    #   vascular / neural classes that the retinal dictionary never carried.
    #   Candidate genes were harvested from the project literature corpus (3,869 papers) restricted
    #   to symbols present in the assay; the identity segment is ranked by literature support and the
    #   discrimination segment by target-vs-neighbour detection ratio. Every entry carries a CL id.
    #   REGISTERED_DEFAULT_OFF: not part of the default `all` set unless EYEKB_ACT_ANTSEG is set;
    #   activation of the default surface requires separate PI approval. Rollback = delete this line.
    "antseg_v10": MARKER_DIR / "markers_v10_antseg_increment.json"}

# [ACT t_5d5853c9] v6-merge whitelist for the default all — hard-coded; env values can only toggle the
# whole feature, never inject any library
V6_DEFAULT_LIBS = ("retina_v6", "face_v6")


def _v6_act_enabled():
    """env EYEKB_ACT_V6 ∈ {0,false,off,no} (casefold) = OFF revert; unset/any other value = ON activation."""
    v = (os.environ.get("EYEKB_ACT_V6") or "").strip().casefold()
    return v not in {"0", "false", "off", "no"}


K9_DEFAULT_LIBS = ("k9_ocs",)  # [ACT t_abfebe59 · KB9ACT plan A (PI released 2026-09-30, obligation gates OB-1..5 all cleared; following the ACT-v6 discipline)] hard-coded whitelist — env values can only toggle the whole feature, never inject any library; lacrimal_v6 ban in any state is preserved


def _k9_act_enabled():
    """env EYEKB_ACT_K9 ∈ {0,false,off,no} (casefold) = OFF revert; unset/any other value = ON activation."""
    v = (os.environ.get("EYEKB_ACT_K9") or "").strip().casefold()
    return v not in {"0", "false", "off", "no"}


# [ANTSEG t_antseg_v10] non-retinal increment whitelist.  Registered on the default `all` route as
# of 2026-10-20 (PI override, see `_antseg_act_enabled`).  Semantics: {0,false,off,no} = OFF;
# unset/empty/any other value = ON.
ANTSEG_DEFAULT_LIBS = ("antseg_v10",)


def _antseg_act_enabled():
    """env EYEKB_ACT_ANTSEG — {0,false,off,no} = OFF; unset/empty/anything else = ON.

    DEFAULT ON since 2026-10-20 by PI decision after a per-tissue re-measurement of the shipped
    code (plans/retina_deep_20261020/RESULT_PER_TISSUE_ANTSEG_20261020.md). The 2026-10-20 external
    acceptance round closed every engineering item (A-F) but withheld the default-on signature on
    two governance points: (1) the declared `scope_tissues` range is not yet confirmed and frozen by
    a source independent of this round's effect data, and (2) the pre-registered condition for
    activation — an independent anterior-segment author-annotated volume — is still unmet.

    THIS IS A PI-SIGNED OVERRIDE, NOT AN AUDIT PASS. The acceptance verdict on default activation
    remains withheld; what the PI weighed instead is the measured per-tissue effect of the shipped
    path: same_cl 32.11% -> 39.46% (+7.36pp) over 28 volumes / 721 clusters / 1,495,330 cells, with
    posterior tissues byte-unchanged (retina, RPE, optic nerve, iris all +0.00pp, zero harm cells)
    and 2,008 already-correct cells (0.13pp) relabelled in the anterior segment.

    The kill switch is explicit: EYEKB_ACT_ANTSEG=0 restores the 2026-10-20 pre-flip OFF state
    byte-for-byte (740/740 requests, 4,672,539 bytes, measured at the same path). Reverting to a
    default-OFF registration means restoring the `"" in the OFF set` form of this predicate.
    """
    v = (os.environ.get("EYEKB_ACT_ANTSEG") or "").strip().casefold()
    return v not in {"0", "false", "off", "no"}


# ---------------------------------------------------------------- increment eligibility guard
# [ANTSEGGUARD 2026-10-20 · activation ON by PI override · SOL acceptance round closed A-F,
#  withheld the default-on signature on two governance points · evidence =
#  plans/retina_deep_20261020/RESULT_ANTSEG_GUARD_20261020.md §9 and
#  RESULT_PER_TISSUE_ANTSEG_20261020.md §3]
# Why: switching the v10 anterior-segment increment on raises same_cl +6.98pp, but unguarded it
# answers 10.67pp more cells at coin-flip quality (47.0% correct) and silently relabels 1.64pp of
# already-correct cells. Each condition removes one MEASURED failure mode:
#   * n_shared >= 2            single-gene coincidences      -> new-answer precision 47.0% -> 75.5%
#   * declared tissue scope    posterior volume routed to an anterior library           -> 82.5%
#   * margin >= incumbent + 2  a narrower class displacing a correct generic class on a 1-gene
#                              difference -> harm 1.64pp -> 0.13pp, net same_cl +6.38 -> +7.36
# Scope: classes OWNED by the increment library, on the default composite route (library="all")
# only — a caller that names library="antseg_v10" has already chosen its scope, and production
# classes keep their own admission rule untouched.
#
# These three conditions are an admission POLICY, not a significance or calibrated-reliability
# rule: the score is raw n_shared, so two shared genes are not two independent pieces of evidence.
# The margin is deliberately asymmetric in favour of the incumbents (a tie goes to the class that
# was already answerable); abstention stays legitimate, so the policy trades recall for precision.
#
# Wiring invariants (SOL item C):
#   1. state_program entries never raise the bar — they do not compete for the top-1 slot;
#   2. a failed increment candidate is removed BEFORE any step that could let it delete a
#      production candidate (the CL-key merge), so nothing unrecoverable happens;
#   3. the CL-key merge, which does choose between increment and production candidates, runs
#      only after this filter has passed.
ANTSEG_LIB_BASENAME = "markers_v10_antseg_increment.json"
ANTSEG_MIN_SHARED = 2
ANTSEG_MARGIN = 2


def _antseg_scope_tissues(dbs):
    """Declared anterior-segment scope, read from the increment file itself (never hard-coded).

    Missing/empty declaration -> () and the caller fails CLOSED for increment classes, reporting
    the gap: a library that does not say where it applies may not enter the automatic route.
    This validates the caller's `tissue` STRING against the declaration; it does not establish
    that the tissue metadata is itself correct — that remains the caller's responsibility.
    """
    for _n, path, db in dbs:
        if Path(path).name == ANTSEG_LIB_BASENAME:
            v = db.get("scope_tissues")
            if isinstance(v, list):
                return tuple(str(x).strip().casefold() for x in v if str(x).strip())
    return ()


def _antseg_is_increment(r, owner_map):
    """True iff this candidate's owning library is the increment file (ownership = file basename)."""
    return Path(owner_map.get(r["cell_type"], "")).name == ANTSEG_LIB_BASENAME


def _antseg_guard_split(rank_full, owner_map, tissue, scope_tissues, is_state_entry):
    """Return (kept, demoted, status). A hard set filter — it never touches any score.

    `is_state_entry(e)` lets the caller exclude non-competing state_program entries from the
    incumbent margin, so that a state entry cannot raise the admission bar for a real cell type.

    A return of (rank_full, [], None) means "the guard did not apply" (no increment candidate
    present) and the caller must not add any key to the response.
    """
    inc = [r for r in rank_full if _antseg_is_increment(r, owner_map)]
    if not inc:
        return rank_full, [], None
    status = {"library": ANTSEG_LIB_BASENAME, "min_shared": ANTSEG_MIN_SHARED,
              "margin": ANTSEG_MARGIN, "applies_to": "increment_classes_only"}
    if not scope_tissues:
        kept = [r for r in rank_full if not _antseg_is_increment(r, owner_map)]
        demoted = [{"cell_type": r["cell_type"], "n_shared": r["n_shared"],
                    "reason": "no_declared_scope"} for r in rank_full
                   if _antseg_is_increment(r, owner_map)]
        status["status"] = "no_declared_scope"
        return kept, demoted, status
    key = str(tissue or "").strip().casefold().replace(" ", "_")
    if not key or not any(t in key for t in scope_tissues):
        kept = [r for r in rank_full if not _antseg_is_increment(r, owner_map)]
        demoted = [{"cell_type": r["cell_type"], "n_shared": r["n_shared"],
                    "reason": "out_of_declared_tissue_scope"} for r in rank_full
                   if _antseg_is_increment(r, owner_map)]
        status["status"] = "out_of_scope"
        status["tissue"] = tissue
        return kept, demoted, status
    best_inc = max([r["n_shared"] for r in rank_full
                    if not _antseg_is_increment(r, owner_map) and not is_state_entry(r)] or [0])
    kept, demoted = [], []
    for r in rank_full:
        if _antseg_is_increment(r, owner_map) and (
                r["n_shared"] < ANTSEG_MIN_SHARED
                or r["n_shared"] < best_inc + ANTSEG_MARGIN):
            demoted.append({"cell_type": r["cell_type"], "n_shared": r["n_shared"],
                            "reason": "below_increment_eligibility",
                            "best_incumbent_n_shared": best_inc,
                            "needs_n_shared": max(ANTSEG_MIN_SHARED, best_inc + ANTSEG_MARGIN)})
            continue
        kept.append(r)
    status["status"] = "in_scope"
    status["tissue"] = tissue
    status["best_incumbent_n_shared"] = best_inc
    return kept, demoted, status


# ---------------------------------------------------------------- Anti-union (composite entry) guard
# [ANTIUNION 2026-10-20 · PI "ok" batch release · prereg = plans/oss_check_20261019/
#  scorer_guard_20261020/PREREG_ANTIUNION_GUARD_20261020.md]
# Why: genes-mode ranks by raw n_shared, so any entry whose marker set is a strict superset of
# another entry (a union such as pr = rod ∪ cone, or macro = three macrophage classes merged)
# dominates its subsets for EVERY query. Empirical: adding such entries moves dr-sc
# (32 clusters / 316,932 cells, PI-signed truth) from 43.8% to 5.2% while the 28 homogeneous
# volumes move only 0.2pp — i.e. invisible on the data the KB was built on.
# Fix = assembly layer, not scoring layer: composite entries are not real cell types, so ON
# removes them from the named ranking (additive key composite_demoted) instead of inventing a
# scale-invariant score (that alternative costs 4.7pp on 28 volumes even with no composites).
# Gate: EYEKB_KB_ANTIUNION, REGISTERED_DEFAULT_OFF — unset = OFF = pre-wiring bytes; enabling by
# default is a PI-reserved gate. Detection uses FULL marker sets (never the query intersection),
# so genes shared with housekeeping panels cannot create false positives; single-gene entries are
# never treated as composites.
def _antiunion_enabled():
    """env EYEKB_KB_ANTIUNION ∈ {1,true,on,yes} (casefold) = ON; unset/anything else = OFF."""
    v = (os.environ.get("EYEKB_KB_ANTIUNION") or "").strip().casefold()
    return v in {"1", "true", "on", "yes"}


def _antiunion_split(rank_full, markers):
    """Return (kept_ranking, demoted_list). A candidate is composite iff its complete marker set
    strictly contains another candidate's complete marker set belonging to a DIFFERENT cell type.

    Same-name entries are never composites: the default route loads several libraries, and
    `retina_interneuron::AC` (thick panel) legitimately contains `retina_v6::AC` / `AC` (thinner
    panels) — those are version duplicates of one cell type, not unions. Demoting them would drop
    the finest panel (golden regression: 155/721 production clusters changed). Deterministic:
    input order kept."""
    present = [r["cell_type"] for r in rank_full]
    sets = {ct: {str(g).upper() for g in (markers.get(ct) or []) if str(g).strip()} for ct in present}
    short = {ct: ct.split("::")[-1].strip().casefold() for ct in present}
    composite = {}
    for a in present:
        A = sets[a]
        if len(A) < 2:
            continue
        subs = [b for b in present
                if b != a and short[b] != short[a] and 2 <= len(sets[b]) < len(A)
                and sets[b] <= A]
        if subs:
            composite[a] = sorted(subs)
    if not composite:
        return rank_full, []
    kept = [r for r in rank_full if r["cell_type"] not in composite]
    demoted = [{"cell_type": r["cell_type"], "n_shared": r["n_shared"],
                "superset_of": composite[r["cell_type"]],
                "reason": "composite_superset_entry"}
               for r in rank_full if r["cell_type"] in composite]
    return kept, demoted


# ---------------------------------------------------------------- CL naming-key layer
# [CLKEY 2026-10-20 · PI "都改" · prereg = plans/oss_check_20261019/scorer_guard_20261020/
#  cl_unify/PREREG_CL_UNIFY_20261020.md]
# Why: one CL cell type can appear in the loaded libraries under several spellings
# (Fibroblast / Limbus_Sclera_fibroblast_C1, Mac_Tissue / Mac_DAM_LAM, Endo / retina_v7::Endo).
# Ranking by raw n_shared lets each spelling take its own candidate slot, pushing the genuine
# runner-up down — the same class of assembly defect as the composite-entry case. The fix is at
# the assembly layer: group ranked candidates by CL idid and keep only the best-ranked member of
# each group in celltype_ranking, moving the rest to the additive key cl_duplicate_demoted.
# Gate: EYEKB_CL_KEY, REGISTERED_DEFAULT_OFF — unset = OFF = pre-wiring bytes. Consequence of a
# missing/corrupt label map is an inert no-op (never an exception).
CL_LABELMAP_FILE = MARKER_DIR / "markers_cl_alignment_v2_unified.json"
_CL_LABELMAP_CACHE = {}  # {"path": str, "mtime": float, "map": dict} once loaded


def _cl_key_enabled():
    """env EYEKB_CL_KEY ∈ {1,true,on,yes} (casefold) = ON; unset/anything else = OFF."""
    v = (os.environ.get("EYEKB_CL_KEY") or "").strip().casefold()
    return v in {"1", "true", "on", "yes"}


def _cl_labelmap():
    """Lazily load the CL label map -> {label: {"cl_id","cl_label"}}. None = feature inert.

    Degradation is deliberate: a missing file, a stale path or a corrupt body must leave the
    scorer behaving exactly as before rather than raising inside a query.
    """
    p = CL_LABELMAP_FILE
    try:
        if not p.is_file():
            return None
        mt = p.stat().st_mtime
        if _CL_LABELMAP_CACHE and _CL_LABELMAP_CACHE.get("map") is not None \
                and _CL_LABELMAP_CACHE.get("path") == str(p) \
                and _CL_LABELMAP_CACHE.get("mtime") == mt:
            return _CL_LABELMAP_CACHE["map"]
        with open(p, encoding="utf-8") as f:
            db = json.load(f)
        labels = db.get("labels")
        if not isinstance(labels, dict) or not labels:
            return None
        m = {k: {"cl_id": (v or {}).get("cl_id"), "cl_label": (v or {}).get("cl_label")}
             for k, v in labels.items()}
        _CL_LABELMAP_CACHE["path"] = str(p)
        _CL_LABELMAP_CACHE["mtime"] = mt
        _CL_LABELMAP_CACHE["map"] = m
        return m
    except Exception:
        return None


def _cl_dedup_split(rank_full, labelmap):
    """Return (kept_ranking, demoted_list, attached).

    Candidates whose resolved CL id is identical are collapsed to the best-ranked one.
    Candidates with no CL id (documented no_match, or a label outside the map) are never
    merged — the map's gaps must not silently delete real candidates. Deterministic: input
    order preserved, so the surviving order equals the ranking order minus the merged rows.
    """
    if not labelmap:
        return rank_full, [], {}
    first_by_cl = {}
    keep, demoted = [], []
    for r in rank_full:
        ct = r["cell_type"]
        short = ct.split("::")[-1].strip()
        rec = labelmap.get(short) or labelmap.get(ct)
        cid = (rec or {}).get("cl_id")
        if not cid:
            keep.append(r)
            continue
        if cid not in first_by_cl:
            first_by_cl[cid] = ct
            keep.append({**r, "cl_id": cid, "cl_label": (rec or {}).get("cl_label")})
        else:
            demoted.append({"cell_type": ct, "n_shared": r.get("n_shared"),
                            "cl_id": cid, "cl_label": (rec or {}).get("cl_label"),
                            "merged_into": first_by_cl[cid],
                            "reason": "same_cell_ontology_term"})
    attached = {r["cell_type"]: r["cl_id"] for r in keep if r.get("cl_id")}
    return keep, demoted, attached


# ---------------------------------------------------------------- TISSUE-SCOPE candidate exclusion layer
# [TISSUESCOPE 2026-10-20 · PI directive "补" after the audit found tissue/inventory was never fixed in MCP]
# Criteria source = plans/oss_check_20261019/scorer_guard_20261020/PREREG_TISSUE_SCOPE_20261020.md
# Data source    = kb/baselines/_tissue_class_crosswalk_v1.json (explicit, withdrawable, per-row provenance)
#
# Mechanism level: hard SET filter on the candidate list, applied BEFORE the ranking is returned —
# same layer as the anti-union guard, never a score term. The crosswalk carries class NAMES only, no
# composition percentages, so no composition quantity can reach scoring.
# Default OFF: EYEKB_TISSUE_SCOPE unset → this whole block is skipped and the response is byte-equal to
# the pre-wiring baseline (acceptance gate A1). A `tissue` argument alone only ATTACHES a status record;
# it never narrows candidates unless the switch is on.
CROSSWALK_PATH = None  # resolved lazily by _crosswalk_path() (KBB is not in scope on this surface)
_CROSSWALK = {"loaded": False, "data": None}


def _crosswalk_path():
    here = Path(__file__).resolve().parent
    return here.parent / "kb" / "baselines" / "_tissue_class_crosswalk_v1.json"


def _load_crosswalk():
    """Lazy, cached load. Missing/corrupt file → None (callers must treat as unavailable)."""
    if _CROSSWALK["loaded"]:
        return _CROSSWALK["data"]
    _CROSSWALK["loaded"] = True
    try:
        with open(_crosswalk_path()) as f:
            _CROSSWALK["data"] = json.load(f)
    except (OSError, ValueError):
        _CROSSWALK["data"] = None
    return _CROSSWALK["data"]


def _tissue_scope_enabled():
    """env EYEKB_TISSUE_SCOPE ∈ {0,false,off,no} (casefold) = explicit OFF revert; unset/any other
    value = ON (default-on, same semantics as EYEKB_KBGOV_B5 above).

    Default changed to ON on 2026-10-20 (PI "ok"); criteria source =
    plans/oss_check_20261019/scorer_guard_20261020/tissue_scope/PREREG_TISSUE_SCOPE_DEFAULT_ON_20261020.md.
    Safety boundary: narrowing runs only inside the `if tissue:` branch, so a call WITHOUT a tissue
    argument stays byte-identical to the pre-change response (gate D1) even though the switch is on.
    """
    v = (os.environ.get("EYEKB_TISSUE_SCOPE") or "").strip().casefold()
    return v not in {"0", "false", "off", "no"}


def _abstain_reason_enabled():
    """env EYEKB_ABSTAIN_REASON = 1/on/true/yes enables the diagnostic abstention record.

    Default OFF (unset = OFF, the inverse polarity of _tissue_scope_enabled): this key exists only
    so callers and reports can tell a coverage gap from a deliberate withhold. Writing it changes
    response bytes, so it must stay opt-in to keep the frozen default-face anchor intact.
    """
    v = (os.environ.get("EYEKB_ABSTAIN_REASON") or "").strip().casefold()
    return v in {"1", "on", "true", "yes"}


def _fallback_widen_enabled(tissue=None):
    """env EYEKB_FALLBACK_WIDEN turns on the fallback widening for empty rankings.

    Default OFF: unset means the whole mechanism is skipped, so the response is byte-identical to
    the pre-wiring baseline. EYEKB_FALLBACK_WIDEN_DENY_TISSUES holds a comma-separated tissue list
    the mechanism must not run on (an empty entry list means "all tissues allowed").

    Criteria source: plans/retina_deep_20261020/PREREG_FALLBACK_WIDEN_V3_20261021.md. This is a
    caller-visible behaviour switch, not a scoring change: the scorer, the panels, the admission
    floor and the tie-break rules are untouched.
    """
    v = (os.environ.get("EYEKB_FALLBACK_WIDEN") or "").strip().casefold()
    if v not in {"1", "on", "true", "yes"}:
        return False
    deny = [t.strip().casefold() for t in
            (os.environ.get("EYEKB_FALLBACK_WIDEN_DENY_TISSUES") or "").split(",") if t.strip()]
    return not (tissue and tissue.strip().casefold() in deny)


def _fallback_widen_floor():
    """Acceptance floor for a widened answer: shared genes between query and winning class."""
    try:
        return int((os.environ.get("EYEKB_FALLBACK_WIDEN_MIN_SHARED") or "5").strip())
    except ValueError:
        return 5


def _tissue_inventory(tissue):
    """Crosswalk record for a tissue, or None when this tissue has no usable prior.

    A record with inventory_status != 'available' or an empty class list is NOT usable: the
    caller must fail OPEN (no narrowing) and surface the gap — an empty inventory must never be
    read as 'this tissue has no cells'.
    """
    cw = _load_crosswalk()
    if not cw:
        return None
    key = (tissue or "").strip().casefold().replace(" ", "_")
    rec = (cw.get("tissues") or {}).get(key)
    return rec


def _tissue_scope_split(rank_full, tissue):
    """Return (kept, excluded, status_dict).

    Rule: a candidate is excluded iff its base class appears in THIS tissue's explicitly authored
    excluded_classes list (clearly foreign signature identities). Classes merely absent from the
    inventory are NOT excluded — a 10-row baseline is not evidence of absence in tissue, and
    in-vivo vascular/immune/stromal populations the row set does not enumerate must stay nameable.

    A tissue whose inventory_status is not 'available' fails OPEN (no narrowing): without a prior
    there is nothing to justify deleting candidates (PREREG A4).
    """
    base = lambda ct: str(ct).split("::")[-1].strip()
    cw = _load_crosswalk()
    status = {"tissue": tissue, "status": "unavailable", "reason": ""}
    if not cw:
        status["reason"] = "crosswalk_missing"
        return rank_full, [], status
    key = (tissue or "").strip().casefold().replace(" ", "_")
    rec = (cw.get("tissues") or {}).get(key)
    if not rec:
        status["reason"] = "tissue_not_in_crosswalk"
        return rank_full, [], status
    status["inventory_status"] = rec.get("inventory_status", "available")
    if rec.get("inventory_status") != "available":
        status["reason"] = rec.get("reason") or "inventory_absent"
        return rank_full, [], status

    strict = bool(cw.get("strict_whitelist", False))
    banned = {str(c).strip() for c in (rec.get("excluded_classes") or [])}
    whitelist = {str(c.get("kb_class")).strip() for c in (rec.get("classes") or []) if c.get("kb_class")}

    kept, excluded = [], []
    for r in rank_full:
        b = base(r["cell_type"])
        if b in banned or (strict and whitelist and b not in whitelist):
            excluded.append({"cell_type": r["cell_type"], "n_shared": r.get("n_shared"),
                             "reason": "tissue_excluded_class"})
        else:
            kept.append(r)
    status.update({"status": "applied", "mode": "strict_whitelist" if strict else "explicit_exclusions",
                   "n_before": len(rank_full), "n_after": len(kept),
                   "n_excluded": len(excluded),
                   "excluded_classes": sorted(banned)})
    return kept, excluded, status


# ---------------------------------------------------------------- KBGOV-B5 cross-species ranking governance layer
# [B5IMPL t_8960c7e0 · USER_DIRECTIVE_20260928 five-queue item ① · PI pre-authorized wiring]
# Input-species governance for query_marker genes-mode. Sole authoritative criteria source =
# plans/kb_gov_20260928/KBGOV_CANDIDATE.md §G1/§G2/§G3 (main candidate B5, mechanical A/B double-gate
# evidence on file; frozen input sha in plans/kbgov_b5impl_20260928/ledgers/SHA_PRE_B5IMPL.txt):
#   G1 decision tier: three signals title_frac (capitalization convention) / msp (Gm\d+|.*Rik$) /
#       m_only (mouse-unique symbols), frozen threshold T=0.4 (calibration file
#       kbgov_g1_calibration.json: human 231 clusters title_frac max=0.0, mouse 59 clusters min=0.8,
#       human_misdetections=[]).
#   G2 B5 caliber: both mouse_confirmed ∧ mouse_suspected refuse named answers — celltype_ranking is
#       fully moved to unranked_candidates (entries kept, non-named ranking), top level adds
#       no_named_ranking_for='mouse_input' + species_evidence; human_assumed gets zero intervention
#       (pre-registered regression gate = 230 human clusters ranking displacement 0.0%, overkill line
#       >5%).
#   G3 annotation tier (no reordering): shared_genes ⊆ AMBIG{GLUL,VIM,CLU} ∧ n_shared≥1 → entry gets
#       no_naming_claim=true + reason='ambiguous_coexpression_only'; ordering and entry retention
#       untouched (consumer protocol: interpreters must not use flagged entries as the basis for
#       identity naming — carried by the interpretation protocol).
# env switch EYEKB_KBGOV_B5: unset/any other value = ON (the 0.6-kbgov5 implementation default);
#   ∈{0,false,off,no} = OFF reverted state — genes-mode responses byte-equal to the pre baseline
#   (A5-style machine-readable self-proof, comparison table out/B5IMPL_A5_ROLLBACK.tsv). Vocab load
#   failure → whole layer degrades to legacy behavior (fail-soft, one-time stderr registration, no
#   throw). Importing the experiment replica is forbidden — this layer is an independent implementation
#   inside production code, and two-source agreement against the replica is the gate (b505/b506).
#   REGISTERED_DEFAULT_OFF semantics (k9_ocs/lacrimal_v6 not in the default) are orthogonal to this
#   layer and must not be broken.
KBGOV_VOCAB = Path(__file__).resolve().parent / "kbgov_vocab.json.gz"
KBGOV_T_FROZEN = 0.4                                  # frozen criterion (changing it = changing the pre-registration, forbidden)
KBGOV_AMBIG = frozenset({"GLUL", "VIM", "CLU"})       # frozen anchor set (no self-extension — the overkill amplifier was demonstrated)
_KBGOV_RE_LETTER = re.compile(r"[A-Za-z]")
_KBGOV_RE_TITLE = re.compile(r"^[A-Z][a-z]")
_KBGOV_RE_GM = re.compile(r"^Gm\d+$")
_KBGOV_RE_RIK = re.compile(r"Rik$")
_kbgov_voc_cache = {"sig": None, "data": None, "warned": False}


def _kbgov_b5_enabled():
    """env EYEKB_KBGOV_B5 ∈ {0,false,off,no} (casefold) = OFF revert; unset/any other value = ON governance."""
    v = (os.environ.get("EYEKB_KBGOV_B5") or "").strip().casefold()
    return v not in {"0", "false", "off", "no"}


def _kbgov_vocab():
    """Lazily load the sha-anchored vocabulary (mcp_server/kbgov_vocab.json.gz = byte-for-byte copy of
    the KBGOV frozen artifact, sha256 9b504a2e...). Returns (HUMSYM, MOUSYM_raw, MOUSYM_upper) or None
    (degrade to legacy)."""
    st = _kbgov_voc_cache
    sig = None
    try:
        p_st = KBGOV_VOCAB.stat()
        sig = (p_st.st_mtime_ns, p_st.st_size)
    except OSError:
        pass
    if sig is not None and st["sig"] == sig and st["data"] is not None:
        return st["data"]
    try:
        with gzip.open(KBGOV_VOCAB, "rt", encoding="utf-8") as f:
            v = json.load(f)
        data = (frozenset(v["hum"]), frozenset(v["m_raw"]), frozenset(v["m_up"]))
        st.update(sig=sig, data=data)
        return data
    except Exception as e:  # noqa: BLE001
        if not st["warned"]:
            sys.stderr.write(f"[kbgov-b5] vocab load failed ({type(e).__name__}: {e}) "
                             f"-> B5 degraded to legacy behavior\n")
            st["warned"] = True
        return None


def _kbgov_g1_tier(raw_genes, hum, m_raw, m_up):
    """G1 input-species decision (production implementation, criteria verbatim-identical to the
    replica kbgov_ab.tier_of). Input = the raw-case gene-name list (before upper()).
    Returns (tier, evidence)."""
    letters = [g for g in raw_genes if _KBGOV_RE_LETTER.search(g)]
    title = [g for g in letters if (not g.isupper()) and _KBGOV_RE_TITLE.match(g)]
    msp = [g for g in raw_genes if _KBGOV_RE_GM.match(g) or _KBGOV_RE_RIK.search(g)]
    monly = [g for g in raw_genes
             if g.upper() not in hum and (g.upper() in m_up or g in m_raw)]
    tf = len(title) / max(len(letters), 1)
    ev = {"title_frac": round(tf, 3), "msp": len(msp), "m_only": len(monly),
          "msp_examples": list(msp)[:5], "m_only_examples": list(monly)[:5]}
    if tf < KBGOV_T_FROZEN:
        return "human_assumed", ev
    return ("mouse_confirmed" if (msp or monly) else "mouse_suspected"), ev


def _kbgov_govern_genes_resp(resp, raw_gl, species=None, volume_id=None, volume_species=None):
    """B5 governance branch: mutates the genes-mode resp in place (G3 annotation → G2 refusal move).
    Zero changes when the vocabulary is unavailable (fail-soft=legacy). Returns the governance state
    for tracing/tests.

    [SPECROUTE t_b9952795] the species decision is handed over to the L1 resolution layer
    (three-source priority + evidence families, SPEC §2/§3); effective only when the
    EYEKB_SPECIES_ROUTE escape door is explicitly powered on, otherwise the legacy branch runs
    verbatim (OFF state = the full pre-wiring state)."""
    if _species_route.enabled():
        return _species_route.attach(resp, raw_gl, explicit=species,
                                     volume_id=volume_id, volume_species=volume_species)
    voc = _kbgov_vocab()
    if voc is None:
        return {"applied": False, "reason": "vocab_unavailable"}
    hum, m_raw, m_up = voc
    tier, ev = _kbgov_g1_tier(raw_gl, hum, m_raw, m_up)
    flagged = []
    for e in resp["celltype_ranking"]:
        sh = e.get("shared_genes") or []
        if e.get("n_shared", 0) >= 1 and sh and set(sh) <= KBGOV_AMBIG:
            e["no_naming_claim"] = True
            e["reason"] = "ambiguous_coexpression_only"
            flagged.append(e["cell_type"])
    resp["input_species"] = tier
    refused = tier in ("mouse_confirmed", "mouse_suspected")
    if refused:
        resp["unranked_candidates"] = resp["celltype_ranking"]
        resp["celltype_ranking"] = []
        resp["no_named_ranking_for"] = "mouse_input"
        resp["species_evidence"] = ev
    return {"applied": True, "tier": tier, "refused": refused, "flagged": flagged}


def _load_marker_dbs(library="all"):
    lib = (library or "all").strip().lower()
    if lib == "all":
        names = ["retina", "membrane", "retina_interneuron"]  # the three active libraries (OFF state = full set)
        if _v6_act_enabled():
            names = names + list(V6_DEFAULT_LIBS)  # whitelist append; lacrimal_v6 never here
        if _k9_act_enabled():
            names = names + list(K9_DEFAULT_LIBS)  # [ACT t_abfebe59] k9_ocs append; no injectable lib names
        if _antseg_act_enabled():
            names = names + list(ANTSEG_DEFAULT_LIBS)  # [ANTSEG] non-retinal increment, ON since 2026-10-20
    elif lib in MARKER_LIBS:
        names = [lib]
    else:
        raise ValueError("library must be one of retina|membrane|retina_interneuron|retina_v6|"
                         "face_v6|lacrimal_v6|k9_ocs|retina_v7|retina_dev|antseg_v10|all, got: "
                         + repr(library))
    dbs = []
    for n in names:
        p = MARKER_LIBS[n]
        if p.is_file():
            with open(p, encoding="utf-8") as f:
                db = json.load(f)
            if n in ("face_v6", "lacrimal_v6") and "markers" not in db:
                # Normalize-and-derive at load time (release-file bodies zero-modified): each
                # *_repair/*_increment's core[{gene,...}] → class-name → gene list; classes with empty
                # core are kept (0 independent criteria genes are registered as-is)
                derived = {}
                # [X4B-FIX determinism t_95015c8a] the original srcs was a set literal whose iteration
                # order follows PYTHONHASHSEED — face_v6's two sources have no class-name overlap, but
                # the derived insertion order fixes the tie order of the ranking surface (measured: the
                # PRE code flips twice in 6 consecutive runs, see out/ASSERT_DETERMINISM.json). Now an
                # explicit tuple pinned to ("stromal_repair","face_increment") = the seed0 iteration
                # order of the original set, i.e. the guard-OFF state stays byte-identical to the
                # pre-wiring baseline (measured under PYTHONHASHSEED=0) while becoming deterministic
                # across processes; same spirit as the ERRATA-E3 BLAS pins.
                srcs = (("stromal_repair", "face_increment") if n == "face_v6"
                        else ("lacrimal_increment",))
                for src in srcs:
                    for cls, e in (db.get(src) or {}).items():
                        derived[cls] = [str(x.get("gene", "")).strip().upper()
                                        for x in (e.get("core") or [])
                                        if isinstance(x, dict) and x.get("gene")]
                db = dict(db)
                db["markers"] = derived
            dbs.append((n, p, db))
    return dbs


# ---------------------------------------- X4B-FIX concept-kind stratification + off-domain flag (t_95015c8a)
# Pre-registration = plans/x4b_fix_20261012/PREREG_X4BFIX.md §1/§3 (mirror of the D-side production
# implementation, same semantics; Chinese-commented sibling lives at /mnt/D/EyeKB/mcp_server/eyekb_core.py).
# F1: on the genes-mode ranking surface, entries annotated concept_kind=state_program in the sidecar
# (proliferation/disease-state programs) take no part in cell_type candidate ranking — they are moved
# to the additive key state_annotations (present only when non-empty; kept entries/order/fields untouched).
# F3: off_domain advisory for "adult vocabulary on a fetal volume" (inert data read of the dev-panel
# file; the dev panel is never merged into the ranking surface — adult-path semantics frozen).
# Global rollback: env EYEKB_STATE_GUARD ∈ {0,false,off,no} (strip+casefold) = OFF = pre-wiring
# behavior (zero new keys on both surfaces; explicit-route error strings byte-untouched, proved by T3);
# unset/any other value = ON (following the ACT-v6 discipline).
# Sidecar fail-soft: missing/corrupt file = no filtering (identical to pre-wiring) + one-time stderr note.
CONCEPT_KIND_SIDECAR = MARKER_DIR / "_concept_kind_sidecar_v1.json"
DEV_PANEL_FILE = MARKER_DIR / "markers_v9_dev_retina.json"  # F3 probe data source (== MARKER_LIBS["retina_dev"] path on the D production face)
_ck_cache = {"sig": None, "kindmap": None, "devsets": None, "warned": False}


def _state_guard_enabled():
    """env EYEKB_STATE_GUARD ∈ {0,false,off,no} (casefold) = OFF rollback; unset/other values = ON."""
    v = (os.environ.get("EYEKB_STATE_GUARD") or "").strip().casefold()
    return v not in {"0", "false", "off", "no"}


def _concept_kind_map():
    """Lazily load the sidecar -> {(library basename, entry): concept_kind} or None (degraded = no filtering)."""
    st = _ck_cache
    try:
        p_st = CONCEPT_KIND_SIDECAR.stat()
        sig = (p_st.st_mtime_ns, p_st.st_size)
    except OSError:
        return None
    if st["sig"] == sig and st["kindmap"] is not None:
        return st["kindmap"]
    try:
        with open(CONCEPT_KIND_SIDECAR, encoding="utf-8") as f:
            d = json.load(f)
        km = {}
        for fname, ann in (d.get("libs") or {}).items():
            for entry, a in (ann or {}).items():
                if isinstance(a, dict) and a.get("concept_kind"):
                    km[(fname, entry)] = a["concept_kind"]
        st.update(sig=sig, kindmap=km)
        return km
    except Exception as e:  # noqa: BLE001
        if not st["warned"]:
            sys.stderr.write(f"[x4bfix-f1] sidecar load failed ({type(e).__name__}: {e}) "
                             f"-> concept-kind filter disabled\n")
            st["warned"] = True
        return None


def _dev_panel_gene_sets():
    """F3 probe: dev-panel entry gene sets (inert data read; missing/corrupt file -> None = probe off)."""
    st = _ck_cache
    try:
        p_st = DEV_PANEL_FILE.stat()
        sig = (p_st.st_mtime_ns, p_st.st_size)
    except OSError:
        return None
    if st.get("dev_sig") == sig and st.get("devsets") is not None:
        return st["devsets"]
    try:
        with open(DEV_PANEL_FILE, encoding="utf-8") as f:
            d = json.load(f)
        ds = {e: set(g.upper() for g in gs) for e, gs in (d.get("markers") or {}).items()}
        st.update(dev_sig=sig, devsets=ds)
        return ds
    except Exception:  # noqa: BLE001
        return None


def _x4b_state_map():
    """The (library basename, entry name) -> concept_kind map when the state split is active,
    else None. Single source of truth for "is this entry a non-competing state program?" — shared
    by the split itself and by callers that must not count state entries as incumbents."""
    if not _state_guard_enabled():
        return None
    return _concept_kind_map()


def _x4b_state_kind(e, km):
    """concept_kind of one ranking entry, or None. Never mutates the entry."""
    if km is None:
        return None
    name = str(e.get("cell_type", ""))
    base = Path(str(e.get("library", ""))).name
    ent = name.split("::")[-1]
    return km.get((base, ent)) or km.get((base, name))


def _x4b_split_state_ranking(rank_full, km=None):
    """F1 split: return (cell_type ranking surface, state_annotations sidecar list).

    Match key = (owner library basename, entry name; disambiguated 'lib::name' takes the '::' suffix).
    Both lists keep the original relative order (stable). OFF / no sidecar / zero hits -> (list, []).

    `km` may be supplied by a caller that already resolved `_x4b_state_map()`; passing it explicitly
    guarantees the split and that caller used the same snapshot.
    """
    if km is None:
        km = _x4b_state_map()
    if km is None:
        return rank_full, []
    kept, states = [], []
    for e in rank_full:
        if _x4b_state_kind(e, km) == "state_program":
            s = dict(e)
            s["concept_kind"] = "state_program"
            states.append(s)
        else:
            kept.append(e)
    return kept, states


def _x4b_off_domain_flag(gl, kept_ranking):
    """F3 criterion (frozen in PREREG §3.1, no post-hoc thresholds): dev_best >= 2 and
    dev_best > top1.n_shared (empty ranking counts as 0) -> advisory dict; else None.
    Adds a key only; never touches the ranking body."""
    if not _state_guard_enabled():
        return None
    ds = _dev_panel_gene_sets()
    if not ds:
        return None
    gset = set(gl)
    best, best_terms = 0, []
    for entry, gs in ds.items():
        n = len(gset & gs)
        if n > best:
            best, best_terms = n, [entry]
        elif n == best and n > 0:
            best_terms.append(entry)
    top1_ns = int(kept_ranking[0]["n_shared"]) if kept_ranking else 0
    if best >= 2 and best > top1_ns:
        return {"flag": "possible_dev_fetal_content", "dev_best": best,
                "dev_best_terms": sorted(best_terms)[:3],
                "hint": ("fetal/developing material should pass development_stage "
                         "(fetal|developing|postnatal) to route the dev panel library (retina_dev)")}
    return None


def query_marker(genes=None, cell_type=None, library="all",
                 species=None, volume_id=None, volume_species=None, tissue=None,
                 fallback_genes=None, _widen_depth=0):
    """Local authoritative marker library query (multi-library; see MARKER_LIBS).
    - cell_type mode: return that class's markers (retina library attaches micro/rpe detail)
    - genes mode: which classes each gene reverse-hits
    genes: list[str] or comma/space-separated str. Both empty → return the class inventory.
    Cross-library class-name conflicts are disambiguated as "library::class" (v1 has none; conflict
    list in provenance.conflicts).
    library=retina_v6|face_v6 (t_38b99a15 registration): KB7 v6 repair panels; t_5d5853c9 activation
    (USER_DIRECTIVE_20260926 A1/A2): default all includes retina_v6+face_v6, env EYEKB_ACT_V6=0
    |false|off|no reverts to the three active libraries (byte-equal to the pre-activation baseline);
    lacrimal_v6 never in the default in any state (PI A3 not switched yet, explicit routing only);
    v6 release-file bodies are read-only at query time.
    library=k9_ocs (t_4bb75b26 registration, PI D17): KB9 plan-B ocular-surface 4 new entries
    REGISTERED_DEFAULT_OFF — never in the default all in any state (not in V6_DEFAULT_LIBS, no
    activation env), reachable via explicit queries only; activation requires the §10-6 mandatory
    run + separate PI approval.
    """
    dbs = _load_marker_dbs(library)
    markers, owner = {}, {}
    seen_upper = {}
    conflicts = []
    for name, path, db in dbs:
        for ct, gs in db.get("markers", {}).items():
            up = ct.upper()
            if up in seen_upper:  # cross-library class-name conflict → disambiguating suffix (display name keeps original case, v1 semantics)
                alt = f"{name}::{ct}"
                conflicts.append({"class": ct, "kept": ct, "alias": alt})
                markers[alt] = [g.upper() for g in gs]
                owner[alt] = str(path)
                continue
            markers[ct] = [g.upper() for g in gs]
            owner[ct] = str(path)
            seen_upper[up] = ct
    prov = {"library_requested": library,
            "files": [{"library": n, "path": str(p), "version": d.get("version"),
                       "note": d.get("note")} for n, p, d in dbs],
            "conflicts": conflicts}
    # Reverse-lookup index
    gene2ct = {}
    for ct, gs in markers.items():
        for g in gs:
            gene2ct.setdefault(g, []).append(ct)

    if cell_type:
        want = cell_type.strip().upper()
        hit = {ct: gs for ct, gs in markers.items() if ct.upper() == want}
        extra = {}
        if want in ("MICRO", "MICROGLIA"):
            for _, _, db in dbs:
                if "micro_detail" in db:
                    extra["micro_detail"] = db["micro_detail"]
        if want == "RPE":
            for _, _, db in dbs:
                if "rpe_detail" in db:
                    extra["rpe_detail"] = db["rpe_detail"]
        # Per-gene provenance for the membrane library (given only for hit classes, to control
        # response volume)
        for name, path, db in dbs:
            for ct in hit:
                raw = ct.split("::")[-1]
                pp = (db.get("provenance") or {}).get(raw)
                if pp and db.get("version", "").startswith("v1-membrane"):
                    extra[f"provenance_{raw}"] = pp
        # face_v6 (t_38b99a15 wiring) / lacrimal_v6 (t_e7ec73ab wiring): when a hit is a v6 entry,
        # attach the release file's granularity_note_* warning notes (data-side originals). After the
        # t_5d5853c9 activation face_v6 is inside the default all → queries for same-named stromal
        # classes (incl. the membrane canonical row) may attach the stromal caution; lacrimal_v6 is
        # explicit-routing only.
        for name, path, db in dbs:
            for gkey, gval in db.items():
                if not str(gkey).startswith("granularity_note_"):
                    continue
                if gval and any(ct.split("::")[-1] in (db.get("markers") or {})
                                for ct in hit):
                    extra[f"v6_{gkey}"] = gval
                    break
        resp = {"mode": "cell_type", "query": cell_type, "found": bool(hit),
                "markers": hit, "detail": extra, "provenance": prov}
        return _sf.wrap_resp(resp, markers, "cell_type",
                             found_classes=list(hit.keys()), provenance=prov)

    if genes:
        if isinstance(genes, str):
            raw_gl = [g.strip() for g in genes.replace(",", " ").split() if g.strip()]
        else:
            raw_gl = [str(g).strip() for g in genes if str(g).strip()]
        gl = [g.upper() for g in raw_gl]  # verbatim-equivalent to the old per-element strip().upper() (proved by the OFF full-equality gate)
        hits = {g: gene2ct.get(g, []) for g in gl}
        score = {}
        for ct in markers:
            n = sum(1 for g in gl if g in markers[ct])
            if n:
                score[ct] = {"n_shared": n, "shared_genes":
                             [g for g in gl if g in markers[ct]], "library": owner[ct]}
        ranked = sorted(score.items(), key=lambda kv: -kv[1]["n_shared"])
        # [X4B-FIX F1] concept-kind stratification on the ranking surface: state_program entries are
        # moved out into the additive key state_annotations (present only when non-empty; kept
        # entries/order/fields byte-untouched; entirely bypassed in the OFF state = pre-wiring bytes)
        rank_full = [{"cell_type": c, **s} for c, s in ranked]
        # [ANTIUNION 2026-10-20] composite (strict-superset) entries dropped from the named ranking.
        # OFF (default) = this block is skipped entirely → bytes equal the pre-wiring response.
        composite_demoted = []
        if _antiunion_enabled():
            rank_full, composite_demoted = _antiunion_split(rank_full, markers)
        # [TISSUESCOPE 2026-10-20] tissue-level candidate exclusion (hard set filter, never a score).
        # OFF (default) = skipped entirely → bytes equal the pre-wiring response; a tissue argument
        # alone only attaches the status record so callers can see whether a prior exists at all.
        tissue_scope = None
        tissue_excluded = []
        if tissue:
            if _tissue_scope_enabled():
                rank_full, tissue_excluded, tissue_scope = _tissue_scope_split(rank_full, tissue)
            else:
                rec = _tissue_inventory(tissue) or {}
                tissue_scope = {"tissue": tissue, "status": "disabled",
                                "inventory_status": rec.get("inventory_status", "not_in_crosswalk"),
                                "reason": "switch_off: EYEKB_TISSUE_SCOPE not enabled; candidates not narrowed"}
        # [ANTSEGGUARD 2026-10-20] increment eligibility: hard filter on the default composite
        # route only. Position matters (SOL item C wiring invariants):
        #   * AFTER the anti-union / tissue-scope filters, so "ownership" and the incumbent margin
        #     are measured on the candidate set that those rules really leave;
        #   * BEFORE the CL-key merge, because that merge keeps only the best-ranked member of each
        #     CL group — if a failing increment candidate ran first it could delete a production
        #     candidate of the same CL and the deletion would be unrecoverable;
        #   * state_program entries are excluded from the margin (see `_antseg_guard_split`) — they
        #     leave the ranking entirely, so they must not raise the bar for a real cell type.
        antseg_demoted = []
        antseg_guard = None
        _state_km = _x4b_state_map()   # one snapshot shared by the guard and the split below
        if (str(library or "all").strip().lower() == "all"
                and any(Path(owner[c]).name == ANTSEG_LIB_BASENAME for c in owner)):
            rank_full, antseg_demoted, antseg_guard = _antseg_guard_split(
                rank_full, owner, tissue, _antseg_scope_tissues(dbs),
                lambda e: _x4b_state_kind(e, _state_km) == "state_program")
        # [CLKEY 2026-10-20] same-cell-ontology-term merge (assembly layer, never a score change).
        # OFF (default) = skipped entirely → bytes equal the pre-wiring response. Runs after the
        # anti-union, tissue-scope and increment-eligibility filters so it merges what actually
        # survives, and before the state split so the state bucket keeps its existing semantics.
        cl_demoted = []
        if _cl_key_enabled():
            rank_full, cl_demoted, _cl_attached = _cl_dedup_split(rank_full, _cl_labelmap())
        rank_kept, state_ann = _x4b_split_state_ranking(rank_full, _state_km)
        # compatibility field: on a single library the top-level auc_threshold semantics are kept
        auc = next((d.get("auc_threshold") for _, _, d in dbs if d.get("auc_threshold")), None)
        resp = {"mode": "genes", "query": gl, "gene_to_celltypes": hits,
                "celltype_ranking": rank_kept,
                "auc_threshold": auc, "provenance": prov}
        if state_ann:
            resp["state_annotations"] = state_ann
        if composite_demoted:
            resp["composite_demoted"] = composite_demoted
        # [TISSUESCOPE 2026-10-20] additive keys, present only when a tissue was supplied
        if tissue_scope is not None:
            resp["tissue_scope"] = tissue_scope
        if tissue_excluded:
            resp["tissue_excluded_candidates"] = tissue_excluded
        if cl_demoted:
            resp["cl_duplicate_demoted"] = cl_demoted
        # [ANTSEGGUARD 2026-10-20] additive keys, written only when the guard actually ran (the
        # increment is loaded on the default route). OFF state -> not present -> bytes unchanged.
        if antseg_guard is not None:
            resp["antseg_guard"] = antseg_guard
        if antseg_demoted:
            resp["antseg_guard_demoted"] = antseg_demoted
        # [ABSTAINREASON 2026-10-21] Why did this query get no answer? Additive key, opt-in only.
        # Default OFF (EYEKB_ABSTAIN_REASON unset) -> key never written -> default bytes unchanged.
        # Motivation: abstention is 17.79pp of the evaluation corpus and callers had no way to tell
        # "we have no evidence" (a coverage gap) from "we deliberately withheld a candidate" (the
        # guards doing their job). Those two need opposite responses from a user.
        if _abstain_reason_enabled() and not rank_kept:
            causes = []
            if not score:
                causes.append("no_marker_overlap")
            if composite_demoted:
                causes.append("composite_superset")
            if tissue_excluded:
                causes.append("tissue_out_of_scope")
            if antseg_demoted:
                causes.append("increment_guard")
            if state_ann:
                causes.append("state_program_only")
            if cl_demoted:
                causes.append("cl_duplicate_collapse")
            resp["abstain_reason"] = {
                "cause": causes[0] if len(causes) == 1 else ("multiple" if causes else "unknown"),
                "causes": causes,
                "n_query_genes": len(gl),
                "n_genes_with_hit": sum(1 for g in gl if hits.get(g)),
                "n_scored_classes": len(score),
                "demoted": {"composite_superset": len(composite_demoted),
                            "tissue_out_of_scope": len(tissue_excluded),
                            "increment_guard": len(antseg_demoted),
                            "state_program_only": len(state_ann or []),
                            "cl_duplicate_collapse": len(cl_demoted)},
            }
        # [X4B-FIX F3] off-domain low-confidence advisory (additive key only; criterion frozen in
        # PREREG §3.1 — the dev-panel file being absent on this surface makes the probe inert, zero
        # drift). Attached on the default all-route only — the "adult vocabulary on fetal material"
        # coverage-routing scenario is precisely the default route; explicit single-library responses
        # stay zero-change (T4 literal caliber, finalized 2026-10-12 after battery evidence).
        if ((library or "all").strip().lower()) == "all":
            od = _x4b_off_domain_flag(gl, rank_kept)
            if od:
                resp["off_domain"] = od
        # [KBGOV-B5] governance branch — skipped entirely in the OFF state; resp equals the pre baseline (A5 acceptance gate)
        if _kbgov_b5_enabled():
            _kbgov_govern_genes_resp(resp, raw_gl, species=species, volume_id=volume_id,
                                     volume_species=volume_species)
        # [FALLBACKWIDEN 2026-10-21] Empty ranking + a wider gene list offered by the caller ->
        # re-ask once on that wider list and accept the answer only if the winner shares at least
        # _fallback_widen_floor() genes. Caller-visible behaviour switch, default OFF: in the OFF
        # state this block never runs, so default bytes are unchanged. Nothing here re-scores,
        # re-ranks or relaxes a guard - the second call is the same query on more genes, and the
        # answer is only adopted when the evidence meets the floor.
        if (fallback_genes and _widen_depth == 0 and not resp["celltype_ranking"]
                and _fallback_widen_enabled(tissue)):
            fb_resp = query_marker(genes=fallback_genes, library=library, species=species,
                                  volume_id=volume_id, volume_species=volume_species,
                                  tissue=tissue, _widen_depth=1)
            fb_rank = fb_resp.get("celltype_ranking") or []
            if fb_rank and fb_rank[0].get("n_shared", 0) >= _fallback_widen_floor():
                fb_resp["fallback_widen"] = {
                    "from_genes": len(gl),
                    "to_genes": len(fb_resp.get("query") or []),
                    "n_shared": fb_rank[0].get("n_shared"),
                    "floor": _fallback_widen_floor(),
                    "reason": "empty_ranking_at_narrow_query",
                }
                return fb_resp
        return _sf.wrap_resp(resp, markers, "genes", query_genes=gl,
                             ranking=resp["celltype_ranking"], provenance=prov)

    return {"mode": "list", "cell_types": sorted(markers), "provenance": prov}


# ---------------------------------------------------------------- Tools 4/5: interpretation-layer priors (KB1, KB1v2 extension)
PRIORS_DIR = (KB / "priors").resolve()
BASELINES_DIR = (KB / "baselines").resolve()  # KB1v2-W1: general ophthalmology composition baseline layer (donor level)


def _apply_marker_repairs(priors):
    """KB7-WIRE (t_38b99a15) item ②: baseline::retina 4 red-word marker fixes — an append-style overlay.

    The original baseline JSON stays byte-untouched; the single authoritative source of the fix
    semantics =
    kb/markers/markers_v6_retina_repair.json#baseline_retina4_disposition (t_2e5e103a frozen release).
    This function applies the row_fixes of kb/baselines/_marker_repair_*.json (schema
    eyekb-marker-repair/1.0, which does not match the eyekb-baseline/ prefix → is never loaded as an
    entry) onto the entries already loaded in memory; a failed row match (cell_type + old_markers
    verbatim full equality) → that row is skipped and registered truthfully in skipped_rows
    (fail-closed: no numbers are changed from memory). Only the marker description layer is touched;
    composition fractions / distributions / identity signatures stay exactly as in the source file."""
    if not BASELINES_DIR.is_dir():
        return
    for p in sorted(BASELINES_DIR.glob("_marker_repair_*.json")):
        try:
            rep = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not str(rep.get("schema", "")).startswith("eyekb-marker-repair/"):
            continue
        entry = priors.get(rep.get("target_entry_id", ""))
        if not isinstance(entry, dict):
            continue
        applied, skipped = [], []
        for fix in rep.get("row_fixes", []):
            rows = entry.get(fix.get("target_list", "states"), [])
            hit_row = None
            for r in rows:
                if (isinstance(r, dict) and r.get("cell_type") == fix.get("cell_type")
                        and r.get("markers") == fix.get("old_markers")):
                    hit_row = r
                    break
            if hit_row is None:
                skipped.append({"cell_type": fix.get("cell_type"),
                                "reason": "old_markers row match failed (baseline body drifted or was "
                                          "already fixed) — not applied; reported rather than edited "
                                          "on assumption"})
                continue
            hit_row["markers"] = list(fix.get("new_markers", []))
            hit_row["marker_revision"] = {
                "old_markers": list(fix.get("old_markers", [])),
                "removed": fix.get("removed", []),
                "added_ref": fix.get("added_ref", ""),
                "note": fix.get("note", ""),
                "disposition_source": rep.get("disposition_source", ""),
                "repair_file": p.name,
                "repair_card": rep.get("card", ""),
            }
            applied.append(fix.get("cell_type"))
        entry["marker_repair"] = {
            "file": str(p), "schema": rep.get("schema"),
            "version": rep.get("version"), "card": rep.get("card"),
            "created": rep.get("created"),
            "original_body_untouched": True,
            "disposition_source": rep.get("disposition_source", ""),
            "applied_rows": applied, "skipped_rows": skipped,
            "residual_observations": rep.get("residual_observations", []),
            "redline": ("this fix affects only the marker description layer; composition fractions / "
                        "distributions / identity signatures keep the original file values; the original "
                        "usage_redline is unchanged — for interpretation contrast and QC flags only, "
                        "never for scoring"),
        }


def _load_priors():
    """Scan kb/priors/**/*.json (schema eyekb-prior/1.0) + kb/baselines/*.json
    (schema eyekb-baseline/1.0, KB1v2) → {entry_id: dict}.
    baseline entries carry _kind='baseline' and take query precedence over the older composition
    entries (copy, never move; the old entries stay archived)."""
    out = {}
    for p in sorted(PRIORS_DIR.rglob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if d.get("schema") == "eyekb-prior/1.0":
            d["_file"] = str(p)
            d.setdefault("_kind", "legacy")
            out[d["entry_id"]] = d
        elif d.get("schema") == "eyekb-disease/1.1":
            # KB1v2-W2: disease thin-layer entries (identity hierarchy + state axis), query precedence over v1 disease entries
            d["_file"] = str(p)
            d["_kind"] = "disease_v2"
            out[d["entry_id"]] = d
    if BASELINES_DIR.is_dir():
        for p in sorted(BASELINES_DIR.glob("*.json")):
            if p.name in ("baselines.json", "fetal_development_transitions.json",
                          "_STAGE_DISCLOSURE.json"):
                continue
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            if str(d.get("schema", "")).startswith("eyekb-baseline/"):
                # KB2c: both 1.0 and 1.1 are accepted; 1.1 carries the organism_stage dual developmental-axis tiers
                d["_file"] = str(p)
                d["_kind"] = "baseline"
                out[d["entry_id"]] = d
    _apply_marker_repairs(out)  # KB7-WIRE ② (t_38b99a15): append-style red-word fix overlay layer
    return out


def _fetal_concept_response(request_stage):
    """KB2c red line 1: fetal/developing queries must not borrow the adult bucket — returns the transition-state concept entry (ruling Q5)."""
    p = BASELINES_DIR / "fetal_development_transitions.json"
    concept = None
    if p.is_file():
        try:
            concept = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            concept = None
    return {"mode": "fetal_development_concept",
            "entry_id": "fetal_development_transitions",
            "request_stage": request_stage,
            "note": ("the KB currently has no filled fetal/developing composition baseline; per the KB2c "
                     "ruling and the PI red line, adult baselines must not answer fetal/developing-stage "
                     "questions by proxy (\"even for the same tissue, fetal profiles are not "
                     "interchangeable with adult ones\" — the maintainer's methodological rule). "
                     "The active interpretation engine must abstain on fetal/developing-stage samples "
                     "(E4 = OOD_strict)."),
            "concept": concept,
            "source_file": str(p),
            "usage_redline": ("this response is not a composition baseline; extrapolating the fraction "
                              "intervals of adult entries onto fetal/developing material is forbidden.")}


def _resolve_sources(entry):
    """sid → traceable source object (PMID/path); interpretation-layer red line: every expectation is expected to carry a citation."""
    return {s["sid"]: {k: v for k, v in s.items() if k != "sid"}
            for s in entry.get("sources", [])}


def _composition_answer_view(resp):
    """Return only the parts of a composition response that answer the question.

    Rows carry their own citations (sources_resolved per row), so the provenance lookup, the
    stratum breakdown, the stage disclosure and the caliber metadata can be left out without
    losing evidence. What is dropped is named in omitted_fields, and repeated calls with
    detail="full" (the default) return everything exactly as before.
    """
    keep = ("entry_id", "title", "species", "tissue", "disease", "organism_stage",
            "development_stage", "rows", "states", "fine_types", "flags", "caveats",
            "source_file", "usage_redline", "usage_scope", "inventory_status", "inventory_note",
            "baseline_status", "distribution_method", "composition_status", "stage_query_note")
    out = {k: resp[k] for k in keep if k in resp}
    dropped = sorted(k for k in resp if k not in out)
    out["detail"] = "answer"
    out["omitted_fields"] = dropped
    out["omitted_note"] = (
        "These fields were left out to keep the response readable. Their absence is a size choice, "
        "not a statement that the evidence is missing: every row still carries its own citations "
        "in sources_resolved. Call again with detail=\"full\" (the default) for strata, "
        "stage_disclosure, provenance and the rest of the caliber metadata.")
    return out


def get_tissue_composition(species, tissue, disease="", development_stage="", detail="full"):
    """Composition-baseline query: cell-composition list + fraction intervals + citations for this
    species and tissue (optionally with a disease).
    species: human|mouse|...; tissue: retina|fibrovascular_membrane|...; disease optional.
    development_stage (KB2c two-axis retrieval): ""|any = main-file caliber (adult-only entries);
    adult = adult main file;
    fetal|developing = returns the transition-state concept entry (borrowing the adult bucket is
    forbidden, PI red line); unknown = only the unknown-tier entries
    (e.g. GSE158629 RPE, a source with no age column). postnatal→developing, organoid→unknown+flag
    (ruling Q1 mapping).
    Returned rows = main table (normal entries major_classes / disease membrane entries
    major_compartments) + state layer + flags + caveats + provenance. Evidence and QC flags only,
    never for scoring."""
    want = (development_stage or "").strip().lower()
    if want == "postnatal":
        want = "developing"
    if want in ("fetal", "developing"):
        return _fetal_concept_response(want)
    priors = _load_priors()
    sp = (species or "").strip().lower()
    ti = (tissue or "").strip().lower()
    dis = (disease or "").strip().lower()
    cands = []
    for e in priors.values():
        if sp and e.get("species", "").lower() != sp:
            continue
        if ti and ti not in (e.get("tissue", "") or "").lower():
            continue
        if dis:
            if (e.get("disease") or "").lower().find(dis) < 0:
                continue
        elif e.get("disease"):
            # no disease given → only baseline entries are wanted; but if this tissue has only disease
            # entries, return those too and mark them
            cands.append((2, e))
            continue
        cands.append((0 if not dis else 1, e))
    if not cands:
        return {"error": f"no matching composition entry (species={species!r} tissue={tissue!r} disease={disease!r})",
                "available": [{"entry_id": e["entry_id"], "species": e.get("species"),
                               "tissue": e.get("tissue"), "disease": e.get("disease")}
                              for e in priors.values()]}
    cands.sort(key=lambda x: (x[0], 0 if x[1].get("_kind") == "baseline" else 1))
    # KB2c: development_stage=unknown → only the unknown-tier entries (e.g. RPE); adult/"" → the current main file
    if want == "unknown":
        unk = [c for c in cands if str(c[1].get("organism_stage", "")).startswith("unknown")]
        if not unk:
            return {"mode": "no_unknown_stage_entry", "request_stage": "unknown",
                    "note": (f"this query has no organism_stage=unknown tier entry (species={species!r} "
                             f"tissue={tissue!r}); the unknown-tier source list is in "
                             f"kb/baselines/_STAGE_DISCLOSURE.md"),
                    "disclosure_file": str(BASELINES_DIR / "_STAGE_DISCLOSURE.md")}
        cands = unk
    entry = cands[0][1]
    rows = entry.get("major_classes") or entry.get("major_compartments") or []
    for r in rows:  # guard: every source_id in the row must resolve
        r["sources_resolved"] = [_resolve_sources(entry).get(s, {"sid": s, "MISSING": True})
                                 for s in r.get("source_ids", [])]
    resp = {"entry_id": entry["entry_id"], "title": entry["title"],
            "species": entry.get("species"), "tissue": entry.get("tissue"),
            "disease": entry.get("disease"), "frozen_date": entry.get("frozen_date"),
            "organism_stage": entry.get("organism_stage",
                                        "unannotated(v1 archived entry — adult assertions must use the "
                                        "kb/baselines v1.1 main file)"),
            # KB3 (t_5425a7ca) clause 6: a composition statement must be able to answer "which development
            # stage" — exit-level pass-through
            "development_stage": entry.get("development_stage", "unknown"),
            "evidence_grades": entry.get("evidence_grades"),
            "rows": rows,
            "states": entry.get("states") or entry.get("myeloid_states") or [],
            "fine_types": entry.get("fine_types"),
            "flags": entry.get("flags"),
            "caveats": entry.get("caveats"),
            "provenance": _resolve_sources(entry),
            "source_file": entry["_file"],
            "usage_redline": ("for interpretation contrast and QC flags only; converting it into a "
                              "module score / label weighting / confidence bonus / candidate ranking "
                              "score / composite QC score is forbidden (KB1v2 red line 1, fully "
                              "inheriting the REVIEWER_LLM T3 extended wording)")}
    # [TISSUESCOPE 2026-10-20] inventory_status: an EMPTY major_classes list must never be read as
    # "this tissue has no cells". It means the prior has not been built yet. Callers get an explicit
    # gap signal plus whatever class list IS available from the crosswalk (names only, no fractions).
    _cw = _load_crosswalk() or {}
    _ti = (tissue or "").strip().casefold().replace(" ", "_")
    _rec = (_cw.get("tissues") or {}).get(_ti)
    if not rows:
        resp["inventory_status"] = "absent"
        resp["inventory_note"] = ("major_classes is empty for this tissue: the composition prior has "
                                  "not been built. This is a GAP, not a statement that the tissue "
                                  "contains no cells.")
    else:
        resp["inventory_status"] = "available"
    if _rec is not None:
        resp["tissue_class_crosswalk"] = {
            "crosswalk": "_tissue_class_crosswalk_v1.json",
            "inventory_status": _rec.get("inventory_status"),
            "kb_classes": [c.get("kb_class") for c in (_rec.get("classes") or [])],
            "unmapped_baseline_rows": _rec.get("unmapped_rows") or [],
            "note": "class names only; candidate-exclusion prior, never a score or weight"}
    # KB1v2 (REVIEWER_LLM T2): baseline entries pass through their caliber fields; skeleton entries are
    # explicitly marked "interval not estimable"
    if entry.get("_kind") == "baseline":
        resp.update({
            "baseline_status": entry.get("status"),
            "anchor": entry.get("anchor"),
            "t2_fields": entry.get("t2_fields"),
            "usage_scope": entry.get("usage_scope"),
            "distribution_method": entry.get("distribution_method"),
            "donor_level_main": entry.get("donor_level_main"),
            "pooled_all_cells": entry.get("pooled_all_cells"),
            "composition_status": entry.get("composition_status"),
            "mapping_from_t_6f5cc731": entry.get("mapping_from_t_6f5cc731"),
            "verdict": entry.get("verdict"),
            # KB2c dual-tier pass-through on the developmental axis (red line: the two tiers keep separate
            # identity signatures; unknown must be disclosed)
            "stage_axis": entry.get("stage_axis"),
            "stage_note": entry.get("stage_note"),
            "stage_disclosure": entry.get("stage_disclosure"),
            "excluded_nonadult_units": entry.get("excluded_nonadult_units"),
            "adult_only_meta": entry.get("adult_only_meta"),
            "donor_level_adult_pool_contrast": entry.get("donor_level_adult_pool_contrast"),
            "pooled_adult_only_main": entry.get("pooled_adult_only_main"),
            "identity_signature": entry.get("identity_signature"),
            "strata": entry.get("strata"),
            "stage_query_note": (
                "main file = adult-only (donor_age>=18y, KB2c ruling Q2); citing the mixed-caliber v1.0 "
                "legacy numbers may only be attached to "
                "donor_level_adult_pool_contrast (tier=...__adult_pool__v1.0); the two tiers' signatures "
                "are not interchangeable; fetal/developing queries must not borrow this entry "
                "(the transition-state concept entry is returned instead)"
                if entry.get("organism_stage") == "adult" else
                "this entry has organism_stage=unknown — citing it as an adult baseline is forbidden "
                "(KB2c red line 2 disclosure entry)"
                if str(entry.get("organism_stage", "")).startswith("unknown") else ""),
        })
    # KB7-WIRE ② (t_38b99a15): pass-through of the marker-fix ledger (the field appears only on entries that
    # already carry the overlay; unfixed entries see a zero-change response) — consumers can audit old→new
    # and the citation
    if entry.get("marker_repair"):
        resp["marker_repair"] = entry["marker_repair"]
    if (detail or "").strip().lower() in ("answer", "compact", "brief", "short"):
        return _composition_answer_view(resp)
    return resp


def get_disease_prior(disease, tissue=""):
    """Disease-prior query: expected cell×state matrix + unexpected/contamination flags + marker
    signatures + citations.
    disease: substring matching (e.g. 'proliferative'/'PDR' → the proliferative diabetic retinopathy
    entry); tissue optionally filters the tissue side.
    Evidence and QC flags only, never for scoring."""
    priors = _load_priors()
    dis = (disease or "").strip().lower()
    alias = {"pdr": "proliferative diabetic", "增殖期糖网": "proliferative diabetic",
             "增殖型糖尿病视网膜病变": "proliferative diabetic",
             "proliferative dr": "proliferative diabetic"}
    dis = alias.get(dis, dis)
    ti = (tissue or "").strip().lower()
    ddis = (lambda e: (e.get("disease") or "").lower())
    hits = [e for e in priors.values()
            if (ddis(e) and dis and dis in ddis(e))
            or dis in (e.get("entry_id", "").lower())
            or any(dis in w for w in (e.get("title", "") or "").lower().split()[:6])]
    if not hits and dis:
        hits = [e for e in priors.values()
                if e.get("disease") and (set(dis.split()) & set(ddis(e).split()))]
    # disease judgement entries (kb/priors/disease/, carrying the expected matrix) take precedence over
    # composition entries (composition/);
    # KB1v2: new-schema thin-layer entries (disease_v2) take precedence over v1 disease entries
    hits.sort(key=lambda e: (0 if e.get("_kind") == "disease_v2" else
                             (1 if e.get("expected_cell_state_matrix") else 2)))
    if not hits:
        return {"error": f"no matching disease entry: {disease!r}",
                "available": [{"entry_id": e["entry_id"], "disease": e.get("disease")}
                              for e in priors.values() if e.get("disease")]}
    entry = hits[0]
    matrix = entry.get("expected_cell_state_matrix") or []
    if ti:
        matrix = [m for m in matrix if ti in (m.get("tissue") or "").lower()]
    src = _resolve_sources(entry)
    for m in entry.get("expected_cell_state_matrix") or []:
        m["sources_resolved"] = [src.get(s, {"sid": s, "MISSING": True})
                                 for s in m.get("source_ids", [])]
    resp = {"entry_id": entry["entry_id"], "title": entry["title"],
            "disease": entry.get("disease"), "species": entry.get("species"),
            "organism_stage": entry.get("organism_stage",
                                        "unannotated(v1 archived entry)"),  # KB2c clause 6: an assertion must carry its development stage
            "tissue_scope": entry.get("tissue_scope"),
            "expected_cell_state_matrix": matrix,
            "unexpected_flags": entry.get("unexpected_flags"),
            "contamination_flags": entry.get("contamination_flags"),
            "signatures": entry.get("signatures"),
            "caveats": entry.get("caveats"),
            "provenance": src, "source_file": entry["_file"],
            "usage_redline": ("for interpretation contrast and QC flags only; converting it into a "
                              "module score / label weighting / confidence bonus / candidate ranking "
                              "score / composite QC score is forbidden (KB1v2 red line 1, fully "
                              "inheriting the REVIEWER_LLM T3 extended wording)")}
    # KB1v2-W2 (T4/T2): thin-layer entries pass through identity hierarchy / state axis / evidence conditions
    # / mismatch warnings
    if entry.get("_kind") == "disease_v2":
        resp.update({
            "schema_version": entry.get("schema"),
            "context": entry.get("context"),
            "usage_scope": entry.get("usage_scope"),
            "sampling_mismatch_warning": entry.get("sampling_mismatch_warning"),
            "identity_hierarchies": entry.get("identity_hierarchies"),
            "state_axes": entry.get("state_axes"),
            "signature_evidence_T4": entry.get("signature_evidence_T4"),
            "unexpected_disposition_queues": entry.get("unexpected_disposition_queues"),
            "minimum_usability_criteria": entry.get("minimum_usability_criteria"),
            "matrix_anchor": entry.get("matrix_anchor"),
        })
    return resp


# ------------------------------------------------- reason-tag join table (K3->KB1v2-W4 three fields)
# KB11-A convergence (card t_0ec42aa8, 2026-10-15): the join table is switched to the v2.4.2 full
# sidecar (kb/literature_db/evidence_meta_v2.4.2_2026-10.jsonl; 3885 rows / 3885 unique PMIDs,
# a strict superset of the v2.0 file). Authority layers are separate and must not be collapsed:
# content authority = that file, byte-identical on both mirror sides (sha256 25f225db...); delivery
# authority = this repository copy; runtime entry = the D-side service directory, unchanged.
# Retrieval semantics / ranking / scoring are untouched -- additive join fields only (the K3
# additive contract is unchanged).
# Fallback shape follows the runtime entry: a missing primary file falls back to v2.0, so a
# rollback is "restore the previous file layout", not "edit this code back".
# External face: the v2.4.2 rows carry Chinese reviewer prose in exactly two leaves
# (evidence_context.locator_anchor, claim_relation[].note). This repository copy is the English
# delivery face, so the sampling point below renders a sanitised projection instead of
# machine-translating: a dict key or list element whose subtree carries CJK is dropped, and
# residual CJK code points are stripped from surviving plain strings. Judge: CJK count on the
# external output path = 0.
REASON_SIDECAR = (EYEKB_ROOT / "kb" / "literature_db" /
                  "evidence_meta_v2.4.2_2026-10.jsonl")
_REASON_SIDECAR_V20 = (EYEKB_ROOT / "kb" / "literature_db" /
                       "evidence_meta_v2.0_2026-09.jsonl")  # pre-KB11 default, kept as fallback
_REASON_SIDECAR_V1 = (EYEKB_ROOT / "kb" / "literature_db" /
                      "inclusion_reason_v2.0_2026-09.jsonl")  # v1 archive, read-only
_reason_cache = {"path": None, "mtime": None, "map": {}}

_CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\u3000-\u303f\uff00-\uffef]")
_WS_RE = re.compile(r"[ \t]{2,}")
_DROP = object()


def _external_face(v):
    """Project a reason-join value onto the English delivery face (CJK dropped, never translated)."""
    if isinstance(v, str):
        if not _CJK_RE.search(v):
            return v
        s = _WS_RE.sub(" ", _CJK_RE.sub("", v)).strip()
        return s if s else _DROP
    if isinstance(v, list):
        return [y for y in (_external_face(x) for x in v) if y is not _DROP]
    if isinstance(v, dict):
        out = {}
        for k, x in v.items():
            y = _external_face(x)
            if y is not _DROP:
                out[k] = y
        return out
    return v


def _ext(v):
    y = _external_face(v)
    return None if y is _DROP else y


def _reason_sidecar_path():
    return REASON_SIDECAR if REASON_SIDECAR.is_file() else _REASON_SIDECAR_V20


def _reason_map():
    path = _reason_sidecar_path()
    try:
        mt = path.stat().st_mtime
    except Exception:
        return {}
    if _reason_cache["mtime"] != mt or _reason_cache["path"] != str(path):
        _reason_cache["map"] = {}
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                    _reason_cache["map"][str(d["pmid"])] = {
                        "inclusion_reason": _ext(d["inclusion_reason"]),
                        "reason_confidence": _ext(d["confidence"]),
                        "reason_method": _ext(d.get("matched_rule", "")),
                        # KB1v2-W4 three-field pass-through: multi-select + claim relation
                        # + evidence context
                        "inclusion_reasons": _ext(d.get("inclusion_reasons")),
                        "claim_relation": _ext(d.get("claim_relation")),
                        "evidence_context": _ext(d.get("evidence_context")),
                        "evidence_verification_status": _ext(d.get("verification_status")),
                    }
                except Exception:
                    continue
        _reason_cache["mtime"] = mt
        _reason_cache["path"] = str(path)
    return _reason_cache["map"]


# ---------------------------------------------------------------- Tool 6: annotation evidence
# Reader-facing evidence trail for a cell-type entry. This is a disclosure
# surface: it reports what identifies an entry, where the knowledge came from, which pages describe
# it and which papers in the shipped corpus back it. Like the retrieval service, it must not be
# consumed as input to any score, weighting, ranking or confidence measure.
LINK_REGISTRY = KB / "link_registry" / "LINK_REGISTRY_v1.jsonl"
_link_cache = {"mtime": None, "rows": []}


def _link_rows():
    """Lazy-load the link registry, re-reading it when the file changes on disk."""
    try:
        mt = LINK_REGISTRY.stat().st_mtime
    except OSError:
        return []
    if _link_cache["mtime"] != mt:
        rows = []
        try:
            for line in LINK_REGISTRY.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    d = json.loads(line)
                    if "error" not in d:
                        rows.append(d)
        except Exception:
            rows = []
        _link_cache["rows"] = rows
        _link_cache["mtime"] = mt
    return _link_cache["rows"]


def _link_norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def explain_annotation(cell_type, tissue=None, top_k=5):
    """Evidence bundle behind a cell-type entry.

    cell_type: the label to explain (e.g. "RPE", "Muller glia", "lens fiber cell").
    tissue: optional filter over the attached citations (retina/cornea/RPE/...).
    top_k: how many citations to return.

    Returns the entry's marker panel, the library it lives in, whether it is reachable on the
    default answer surface or only by explicit routing, the knowledge-base pages that describe it,
    any textbook edition+page anchor behind its definition, and the papers in the shipped corpus
    that back it — each with journal and year, so the trail can be checked without network access.
    Unknown labels return the nearest available entries instead of an empty object.
    """
    rows = _link_rows()
    if not rows:
        return {"error": "link registry not found",
                "expected_at": str(LINK_REGISTRY),
                "hint": "rebuild it with kb/link_registry/scripts/build_link_registry.py"}
    want = _link_norm(cell_type)
    exact = [r for r in rows if _link_norm(r.get("cell_type")) == want]
    if not exact and want:
        exact = [r for r in rows if want in _link_norm(r.get("cell_type"))]
    if not exact:
        return {"found": False, "cell_type": cell_type,
                "available": sorted({r.get("cell_type", "") for r in rows if r.get("cell_type")})}
    hits = []
    for r in exact:
        cites = r.get("citations", [])
        if tissue:
            t = str(tissue).lower()
            filt = [c for c in cites if t in str(c.get("tissues", "")).lower()]
            if filt:
                cites = filt
        hits.append({
            "entry_id": r.get("entry_id"),
            "cell_type": r.get("cell_type"),
            "library": r.get("library"),
            "key_markers": r.get("genes_top", []),
            "n_genes": r.get("n_genes"),
            "wiki_pages": r.get("wiki_pages", []),
            "textbook_anchors": [{"book": b, "page": p} for b, p in r.get("book_anchors", [])],
            "citations": [{"pmid": c.get("pmid"), "title": c.get("title"),
                           "journal": c.get("journal"), "year": c.get("year"),
                           "tissues": c.get("tissues"), "marker_genes": c.get("marker_genes"),
                           "relevance": c.get("relevance"), "snippet": c.get("chunk")}
                          for c in cites[:int(top_k)]],
            "mcp_route": r.get("mcp_route"),
            "skill": r.get("skill_trigger"),
        })
    return {"found": True, "cell_type": cell_type, "n_matches": len(hits),
            "entries": hits,
            "discipline": "evidence disclosure only — not an input to any score, weighting or ranking"}


if __name__ == "__main__":
    # minimal self-test without MCP (tool kernel layer)
    print(json.dumps(query_marker(cell_type="RPE", library="retina"), ensure_ascii=False)[:400])
    print(json.dumps(query_marker(cell_type="Endo")["found"], ensure_ascii=False))
    print(json.dumps(get_kb_page("topic", "vascular")["file"], ensure_ascii=False))
    print(json.dumps(get_kb_page("topic", "../../etc/passwd"), ensure_ascii=False))

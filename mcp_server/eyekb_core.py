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


def get_kb_page(scope, name=""):
    """Read raw VK index pages. Whitelist anti-traversal:
    - only *.md inside kb/vk_literature_index/ allowed
    - name allows only [A-Za-z0-9_-]; after resolution the realpath must still be inside the
      whitelisted directory
    """
    scope = (scope or "").strip().lower()
    name = (name or "").strip()
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
    "k9_ocs": MARKER_DIR / "markers_k9_ocs_increment.json"}

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


def _kbgov_govern_genes_resp(resp, raw_gl):
    """B5 governance branch: mutates the genes-mode resp in place (G3 annotation → G2 refusal move).
    Zero changes when the vocabulary is unavailable (fail-soft=legacy). Returns the governance state
    for tracing/tests."""
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
    elif lib in MARKER_LIBS:
        names = [lib]
    else:
        raise ValueError("library must be one of retina|membrane|retina_interneuron|retina_v6|"
                         "face_v6|lacrimal_v6|k9_ocs|all, got: " + repr(library))
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
                srcs = ({"stromal_repair", "face_increment"} if n == "face_v6"
                        else {"lacrimal_increment"})
                for src in srcs:
                    for cls, e in (db.get(src) or {}).items():
                        derived[cls] = [str(x.get("gene", "")).strip().upper()
                                        for x in (e.get("core") or [])
                                        if isinstance(x, dict) and x.get("gene")]
                db = dict(db)
                db["markers"] = derived
            dbs.append((n, p, db))
    return dbs


def query_marker(genes=None, cell_type=None, library="all"):
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
        # compatibility field: on a single library the top-level auc_threshold semantics are kept
        auc = next((d.get("auc_threshold") for _, _, d in dbs if d.get("auc_threshold")), None)
        resp = {"mode": "genes", "query": gl, "gene_to_celltypes": hits,
                "celltype_ranking": [{"cell_type": c, **s} for c, s in ranked],
                "auc_threshold": auc, "provenance": prov}
        # [KBGOV-B5] governance branch — skipped entirely in the OFF state; resp equals the pre baseline (A5 acceptance gate)
        if _kbgov_b5_enabled():
            _kbgov_govern_genes_resp(resp, raw_gl)
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


def get_tissue_composition(species, tissue, disease="", development_stage=""):
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


# ------------------------------------------------- reason-tag join table (K3→KB1v2-W4 three fields)
REASON_SIDECAR = (EYEKB_ROOT / "kb" / "literature_db" /
                  "evidence_meta_v2.0_2026-09.jsonl")
_REASON_SIDECAR_V1 = (EYEKB_ROOT / "kb" / "literature_db" /
                      "inclusion_reason_v2.0_2026-09.jsonl")  # v1 archive, read-only
_reason_cache = {"mtime": None, "map": {}}


def _reason_map():
    try:
        mt = REASON_SIDECAR.stat().st_mtime
    except Exception:
        return {}
    if _reason_cache["mtime"] != mt:
        _reason_cache["map"] = {}
        with open(REASON_SIDECAR, encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                    _reason_cache["map"][str(d["pmid"])] = {
                        "inclusion_reason": d["inclusion_reason"],
                        "reason_confidence": d["confidence"],
                        "reason_method": d.get("matched_rule", ""),
                        # KB1v2-W4 (REVIEWER_LLM T5) three-field pass-through: multi-select + claim relation
                        # + evidence context
                        "inclusion_reasons": d.get("inclusion_reasons"),
                        "claim_relation": d.get("claim_relation"),
                        "evidence_context": d.get("evidence_context"),
                        "evidence_verification_status": d.get("verification_status"),
                    }
                except Exception:
                    continue
        _reason_cache["mtime"] = mt
    return _reason_cache["map"]


if __name__ == "__main__":
    # minimal self-test without MCP (tool kernel layer)
    print(json.dumps(query_marker(cell_type="RPE", library="retina"), ensure_ascii=False)[:400])
    print(json.dumps(query_marker(cell_type="Endo")["found"], ensure_ascii=False))
    print(json.dumps(get_kb_page("topic", "vascular")["file"], ensure_ascii=False))
    print(json.dumps(get_kb_page("topic", "../../etc/passwd"), ensure_ascii=False))

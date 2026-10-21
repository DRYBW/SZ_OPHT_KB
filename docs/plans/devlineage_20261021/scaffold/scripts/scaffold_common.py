#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scaffold_common.py - shared vocabulary, key grammar and loaders for the scaffold card.

Frozen contract: /mnt/D/EyeKB/plans/devlineage_20261021/DATA_CONTRACT_devlineage_v1.md
Everything here is read from local authority only (the Cell Ontology release on disk, our own
marker libraries, our own baselines, our own corpus). Zero network, stdlib + pyarrow only.

The contract's key grammar is enforced on both sides: `build_node_key` writes it and
`parse_node_key` reads it back, so a delivered key can never drift from the contract without a
gate failure.
"""
from __future__ import annotations

import collections
import csv
import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SCAFFOLD = os.path.dirname(HERE)                   # plans/devlineage_20261021/scaffold
WAVE = os.path.dirname(SCAFFOLD)                   # plans/devlineage_20261021  (the card's wave)
PLANS = os.path.dirname(WAVE)                      # plans/

FIRST_PASS = os.path.join(PLANS, "cl_depth_devlineage_20261021")
ONT_WAVE = os.path.join(PLANS, "devline_ont_20261002")
ONT_OBO = os.path.join(ONT_WAVE, "downloads", "cl.obo")
ONT_NAV = os.path.join(FIRST_PASS, "out", "ONT_NAV_v1.json")
ONT_LABELMAP = os.path.join(FIRST_PASS, "out", "ONT_LABELMAP_V2.tsv")
FIRSTPASS_NODES = os.path.join(FIRST_PASS, "out", "LINEAGE_NODES.tsv")
FIRSTPASS_EDGES = os.path.join(FIRST_PASS, "out", "LINEAGE_EDGES.tsv")
FIRSTPASS_GERM = os.path.join(FIRST_PASS, "out", "LINEAGE_GERM_LAYER.tsv")
FIRSTPASS_UNRESOLVED = os.path.join(FIRST_PASS, "out", "LINEAGE_UNRESOLVED_DEVELOPMENT.tsv")
FIRSTPASS_FOURWAY = os.path.join(FIRST_PASS, "out", "GRANULARITY_FOURWAY_721.tsv")
PRECURSOR_EDGES = os.path.join(ONT_WAVE, "out", "PRECURSOR_EDGES.tsv")
EYE_SUBGRAPH = os.path.join(ONT_WAVE, "out", "cl_eye_subgraph.json")
DEV3_TERMS = os.path.join(ONT_WAVE, "out", "DEV3_CANDIDATE_DEVELOPMENTAL_TERMS.tsv")
D1_TABLE = os.path.join(ONT_WAVE, "out", "D1_ADULT_PANEL_vs_CL.tsv")
D2_TABLE = os.path.join(ONT_WAVE, "out", "D2_V8_PRECURSOR_vs_CL.tsv")
D3_TABLE = os.path.join(ONT_WAVE, "out", "D3_DEV_EXAM_LABELS_vs_CL.tsv")

BASELINE_DIR = "/mnt/D/EyeKB/kb/baselines"
MARKER_DIR = "/mnt/D/EyeKB/kb/markers"
TEXTBOOK = "/mnt/D/EyeKB/kb/textbook_layer/TEXTBOOK_ITEMS_v1.jsonl"
CORPUS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10"
CHUNKS = os.path.join(CORPUS, "chunks.parquet")
PAPERS = os.path.join(CORPUS, "papers.jsonl")

OUT = os.path.join(SCAFFOLD, "out")
LEDGERS = os.path.join(SCAFFOLD, "ledgers")
LOGS = os.path.join(SCAFFOLD, "logs")

# ---------------------------------------------------------------- vocabulary (contract, verbatim)
REL_TYPES = ("ontology_development_relation", "direct_lineage",
             "ancestral_origin", "trajectory_association")
GRADES = ("direct_lineage_support", "identity_conversion_not_direct",
          "textbook_or_review_distant_origin", "trajectory_only")
# Grades a confirmed edge may carry. `trajectory_only` is explicitly not admitted by the
# contract ("Not admitted as a confirmed edge: pseudotime only; co-expression or
# transcriptional similarity only; ...").
ADMITTED_GRADES = ("direct_lineage_support", "identity_conversion_not_direct",
                   "textbook_or_review_distant_origin")
STAGES = ("fetal", "adult", "developing", "unknown")
ES_VOCAB = ("in_vivo", "organoid", "iPSC_derived", "culture", "unknown")
ADMISSION = ("confirmed", "rejected")

NODE_KINDS = ("library_class", "ontology_intermediate", "origin_anchor")
LIB_FILES = ["markers_v4.1_clean.json", "markers_v5_retina_interneuron.json",
             "markers_v6_retina_repair.json", "markers_v6_face_increment.json",
             "markers_v6_lacrimal_increment.json", "markers_v7_panel_increment.json",
             "markers_k9_ocs_increment.json", "markers_membrane_v1.json",
             "markers_v8_dev_retina.json", "markers_v9_dev_retina.json",
             "markers_v10_antseg_increment.json", "markers_v11_lensiris_increment.json"]
DEV_PANELS = ("markers_v8_dev_retina.json", "markers_v9_dev_retina.json")
NESTED = ("face_increment", "stromal_repair", "lacrimal_increment")

# The developmental word list this repository already uses for the stage axis (KB3), applied
# to a term's own text. Word-bounded: a substring rule would call `fibroblast` a developmental
# state because of `blast` and move a mature cell onto the developing side.
DEV_WORDS = ("progenitor", "precursor", "stem cell", "blast", "neuroepithel", "immature",
             "fetal", "embryonic", "transit amplifying", "transit-amplifying", "proliferat")
DEV_PATTERNS = [(w, re.compile(r"(?<![a-z])" + w.replace(" ", r"\s+") + r"(?![a-z])"))
                for w in DEV_WORDS]
# Two of the words are stems, and our own library labels join words with `_`: reading a label
# needs both allowances, or `Proliferating` and `TAC_transit_amplifying` are missed (measured).
DEV_STEMS = ("proliferat", "neuroepithel")
DEV_LABEL_PATTERNS = [
    (w, re.compile(r"(?<![a-z])" + w.replace(" ", r"[\s_\-]+") + (r"[a-z]*" if w in DEV_STEMS else "")
                   + r"(?![a-z])"))
    for w in DEV_WORDS]


def norm(s) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


def dev_word_in(text) -> str:
    """The developmental word a text carries (recorded so the stage call is auditable)."""
    blob = str(text or "").lower()
    for w, pat in DEV_PATTERNS:
        if pat.search(blob):
            return w
    return ""


def dev_word_in_label(text) -> str:
    """Same, for a library label: separators are `_`/`-` and `proliferat*` is a stem."""
    blob = str(text or "").lower()
    for w, pat in DEV_LABEL_PATTERNS:
        if pat.search(blob):
            return w
    return ""


# ---------------------------------------------------------------- key grammar
_NODE_KEY_RE = re.compile(
    r"^dl:(?P<cl>CL:\d+|NO_MATCH:[^|]+)"
    r"\|sp=(?P<sp>[A-Za-z0-9_.\-]+)"
    r"\|ts=(?P<ts>[A-Za-z0-9_.\-]+)"
    r"\|st=(?P<st>fetal|adult|developing|unknown)"
    r"\|es=(?P<es>in_vivo|organoid|iPSC_derived|culture|unknown)$")
_EDGE_KEY_RE = re.compile(
    r"^(?P<prec>dl:CL:\d+\|[^>]*?\|\S+?)->(?P<desc>dl:CL:\d+\|[^>]*?\|\S+?)"
    r"\|rel=(?P<rel>[a-z_]+)$")


def build_node_key(cl: str, sp: str, ts: str, st: str, es: str) -> str:
    for v in (sp, ts, st, es):
        if "|" in str(v) or " " in str(v) or not str(v):
            raise ValueError(f"illegal node-key field value: {v!r}")
    if st not in STAGES:
        raise ValueError(f"stage outside the four-level axis: {st!r}")
    if es not in ES_VOCAB:
        raise ValueError(f"experimental system outside the contract vocabulary: {es!r}")
    return f"dl:{cl}|sp={sp}|ts={ts}|st={st}|es={es}"


def parse_node_key(key: str) -> dict:
    m = _NODE_KEY_RE.match(str(key))
    if not m:
        raise ValueError(f"node key does not parse against the contract grammar: {key!r}")
    d = m.groupdict()
    return {"cl": d["cl"], "sp": d["sp"], "ts": d["ts"], "st": d["st"], "es": d["es"]}


def build_edge_key(prec_node: str, desc_node: str, rel: str) -> str:
    if rel not in REL_TYPES:
        raise ValueError(f"relation type outside the contract vocabulary: {rel!r}")
    return f"{prec_node}->{desc_node}|rel={rel}"


def parse_edge_key(key: str) -> dict:
    """Read an edge key back. A node key never contains `->`, so the first one is the separator;
    the last `|rel=` belongs to the edge (node keys carry no `rel` field)."""
    key = str(key)
    i = key.find("->")
    if i < 0:
        raise ValueError(f"edge key has no precursor->descendant separator: {key!r}")
    prec, rest = key[:i], key[i + 2:]
    j = rest.rfind("|rel=")
    if j < 0:
        raise ValueError(f"edge key has no |rel= field: {key!r}")
    desc, rel = rest[:j], rest[j + len("|rel="):]
    if rel not in REL_TYPES:
        raise ValueError(f"edge key relation not in vocabulary: {rel!r}")
    # both halves must themselves parse as node keys, and must agree with their |rel= field
    parse_node_key(prec)
    parse_node_key(desc)
    if f"{prec}->{desc}|rel={rel}" != key:
        raise ValueError(f"edge key is not in canonical order: {key!r}")
    return {"precursor": prec, "descendant": desc, "rel": rel}


# ---------------------------------------------------------------- loaders
def load_label_map() -> dict:
    """label -> row from the first pass's label map (CL id read from the ontology file there)."""
    out = {}
    with open(ONT_LABELMAP, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            out[r["label"]] = r
    return out


def load_panels():
    """label -> (genes, source files) from the marker libraries this repository ships."""
    panels, files = {}, {}
    for fname in LIB_FILES:
        path = os.path.join(MARKER_DIR, fname)
        if not os.path.isfile(path):
            continue
        payload = json.load(open(path, encoding="utf-8"))
        ent = dict(payload.get("markers") or {})
        for k in NESTED:
            v = payload.get(k)
            if isinstance(v, dict):
                ent.update({kk: vv for kk, vv in v.items() if isinstance(vv, dict)})
        for e in (payload.get("entries") or []):
            if isinstance(e, dict) and e.get("class_name"):
                ent.setdefault(e["class_name"], e)
        for label, v in ent.items():
            genes = v if isinstance(v, list) else (v.get("markers") if isinstance(v, dict) else None)
            if genes:
                panels.setdefault(label, set()).update(str(g).upper() for g in genes)
            files.setdefault(label, set()).add(os.path.basename(path))
    return panels, files


def load_baselines() -> dict:
    """baseline file -> {stage, species, keys, class_shares}. Read-only, our own artefacts."""
    out = {}
    for p in sorted(glob.glob(os.path.join(BASELINE_DIR, "*.json"))):
        name = os.path.basename(p)
        if name.startswith("_"):
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        stage = str(d.get("development_stage") or d.get("organism_stage") or "")
        pool, shares = set(), {}
        for field in ("donor_level_main", "pooled_adult_only_main",
                      "donor_level_adult_pool_contrast", "pooled_adult_pool_contrast"):
            v = d.get(field)
            if isinstance(v, dict):
                pool |= {str(k) for k in v}
        for mc in (d.get("major_classes") or []):
            if isinstance(mc, dict) and mc.get("class"):
                pool.add(str(mc["class"]))
                if mc.get("donor_median_pct") is not None:
                    shares[str(mc["class"])] = mc["donor_median_pct"]
        for st in (d.get("states") or []):
            if isinstance(st, dict) and st.get("cell_type"):
                pool.add(str(st["cell_type"]))
        out[name] = {"path": p, "stage": stage, "species": d.get("species"),
                     "entry_id": d.get("entry_id"), "keys": pool, "shares": shares,
                     "title": d.get("title")}
    return out


def eval_volume_tokens() -> list:
    """The evaluation volumes' own identifiers, used only to prove they are NOT referenced."""
    tok = set()
    if os.path.isfile(FIRSTPASS_FOURWAY):
        with open(FIRSTPASS_FOURWAY, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                if r.get("vol"):
                    tok.add(r["vol"])
    tok.add("oss_check_20261019")
    return sorted(tok)


def read_tsv(path) -> list:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_tsv(path, rows, cols) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter="\t", extrasaction="ignore", restval="")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {path}  ({len(rows)} rows)")
    return path


def write_json(path, obj) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"wrote {path}")
    return path


def sha256(path) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def counts(seq) -> dict:
    return dict(collections.Counter(seq))
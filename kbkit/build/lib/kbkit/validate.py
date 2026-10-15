"""Machine gates.  `kbkit validate <plugin-dir>` runs all of these.

Every gate emits findings with a rule id, so a failure tells a builder exactly
which design rule they broke.  Gates never "fix" anything: they only report.

Gate ids map 1:1 onto the rules documented in schema.py.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import SCHEMA_VERSION
from .schema import (
    ANNOTATION_LEVEL, ASSAY, DIRECTION, EVIDENCE_LEVEL, INCLUSION_REASON,
    ORGANISM_STAGE, REQUIRED_FILES, SAMPLING_MATERIAL, SPECIES,
)


class Finding:
    def __init__(self, gate, path, message, severity="error"):
        self.gate, self.path, self.message, self.severity = gate, path, message, severity

    def __str__(self):
        return "[%s] %s: %s (%s)" % (self.severity.upper(), self.gate, self.message, self.path)


def _iter_json(root, sub):
    d = root / sub
    if not d.exists():
        return []
    return sorted(p for p in d.rglob("*.json") if not p.name.startswith("_"))


def _enum(gate, where, value, allowed, f):
    if value not in allowed:
        f.append(Finding(gate, where, "%r not in %s" % (value, sorted(allowed))))
        return False
    return True


# ── G0: structure ─────────────────────────────────────────────────────────────
def gate_structure(root, f):
    for name in REQUIRED_FILES:
        if not (root / name).exists():
            f.append(Finding("G0-structure", str(root / name), "required path missing"))


# ── G1: plugin.yaml ───────────────────────────────────────────────────────────
def gate_plugin(root, f):
    p = root / "plugin.yaml"
    if not p.exists():
        return None
    try:
        import yaml
        cfg = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception as exc:                                   # noqa: BLE001
        f.append(Finding("G1-plugin", str(p), "unparseable YAML: %s" % exc))
        return None
    for key in ("name", "tissue", "species", "schema_version", "plugin_version",
                "build_lock", "axes", "licence"):
        if key not in cfg:
            f.append(Finding("G1-plugin", str(p), "missing key %r" % key))
    if cfg.get("schema_version") not in (None, SCHEMA_VERSION):
        f.append(Finding("G1-plugin", str(p), "schema_version %r != kit %r"
                         % (cfg.get("schema_version"), SCHEMA_VERSION)))
    axes = cfg.get("axes") or {}
    for axis in ("species", "tissue", "organism_stage"):
        if axis not in axes:
            f.append(Finding("G1-plugin", str(p), "axes missing %r" % axis))
    for s in cfg.get("species") or []:
        _enum("G1-plugin", str(p), s, SPECIES, f)
    return None


# ── G2: marker entries (R1 direction, R2 provenance) ──────────────────────────
def gate_markers(root, f):
    for p in _iter_json(root, "markers"):
        data = json.loads(p.read_text(encoding="utf-8"))
        entries = data if isinstance(data, list) else [data]
        for i, e in enumerate(entries):
            w = "%s#%d" % (p.name, i)
            for key in ("entry_id", "cell_type", "cl_id", "species",
                        "organism_stage", "genes", "version"):
                if key not in e:
                    f.append(Finding("G2-markers", w, "missing field %r" % key))
            _enum("G2-markers", w, e.get("organism_stage"), ORGANISM_STAGE, f)
            _enum("G2-markers", w, e.get("species"), SPECIES, f)
            cl = e.get("cl_id")
            if cl is not None and not (str(cl).startswith("CL:") or cl == "NO_MATCH"):
                f.append(Finding("G2-markers", w,
                                 "cl_id %r must be a CL: term or NO_MATCH (no near terms)" % cl))
            for g in e.get("genes") or []:
                gw = "%s gene=%s" % (w, g.get("gene"))
                if "gene" not in g:
                    f.append(Finding("G2-markers", w, "gene item without 'gene'"))
                    continue
                if "direction" not in g:
                    f.append(Finding("G2-markers", gw, "R1 VIOLATION: no direction"))
                else:
                    _enum("G2-markers", gw, g["direction"], DIRECTION, f)
                prov = g.get("provenance")
                if not prov:
                    f.append(Finding("G2-markers", gw, "R2 VIOLATION: no provenance"))
                elif not isinstance(prov, dict) or not (prov.get("pmid") or prov.get("dataset")):
                    f.append(Finding("G2-markers", gw,
                                     "R2 VIOLATION: provenance needs pmid or dataset, got %r" % prov))
                _enum("G2-markers", gw, g.get("evidence_level"), EVIDENCE_LEVEL, f)


# ── G3: baselines (R4 per-donor range, no point estimates) ────────────────────
def gate_baselines(root, f):
    for p in _iter_json(root, "baselines"):
        data = json.loads(p.read_text(encoding="utf-8"))
        entries = data if isinstance(data, list) else [data]
        for i, e in enumerate(entries):
            w = "%s#%d" % (p.name, i)
            for key in ("entry_id", "species", "tissue", "organism_stage",
                        "sampling_material", "disease_stage", "treatment_background",
                        "assay", "enrichment_step", "n_donors", "cells"):
                if key not in e:
                    f.append(Finding("G3-baselines", w, "missing field %r" % key))
            _enum("G3-baselines", w, e.get("organism_stage"), ORGANISM_STAGE, f)
            _enum("G3-baselines", w, e.get("sampling_material"), SAMPLING_MATERIAL, f)
            _enum("G3-baselines", w, e.get("assay"), ASSAY, f)
            nd = e.get("n_donors")
            if isinstance(nd, int) and nd < 2:
                f.append(Finding("G3-baselines", w,
                                 "R4: n_donors=%d — per-donor ranges need >=2 donors" % nd))
            for c in e.get("cells") or []:
                cw = "%s %s" % (w, c.get("cell_type"))
                pr = c.get("proportion")
                if not (isinstance(pr, (list, tuple)) and len(pr) == 2):
                    f.append(Finding("G3-baselines", cw,
                                     "R4 VIOLATION: proportion must be [lo, hi], got %r" % pr))
                else:
                    lo, hi = pr
                    if not (0.0 <= lo <= hi <= 1.0):
                        f.append(Finding("G3-baselines", cw,
                                         "proportion range invalid: %r" % (pr,)))
                    if lo == hi:
                        f.append(Finding("G3-baselines", cw,
                                         "R4: zero-width range %r looks like a point estimate" % (pr,)))
                if not c.get("pmid"):
                    f.append(Finding("G3-baselines", cw, "R2 VIOLATION: no pmid"))
                _enum("G3-baselines", cw, c.get("evidence_level"), EVIDENCE_LEVEL, f)


# ── G4: disease entries (R5 type x state) ─────────────────────────────────────
STATE_WORDS_HINT = {"proliferating", "inflammatory", "foam", "foamy", "activated",
                    "dam", "lam", "senescent", "apoptotic"}
LINEAGE_WORDS = {"macrophage", "microglia", "fibroblast", "endothelial", "pericyte",
                 "astrocyte", "muller", "müller", "rod", "cone", "bipolar", "amacrine",
                 "horizontal", "ganglion", "rpe", "keratocyte"}


def gate_disease(root, f):
    for p in _iter_json(root, "disease"):
        data = json.loads(p.read_text(encoding="utf-8"))
        entries = data if isinstance(data, list) else [data]
        for i, e in enumerate(entries):
            w = "%s#%d" % (p.name, i)
            for key in ("entry_id", "disease", "species", "tissue",
                        "organism_stage", "context", "cells"):
                if key not in e:
                    f.append(Finding("G4-disease", w, "missing field %r" % key))
            _enum("G4-disease", w, e.get("organism_stage"), ORGANISM_STAGE, f)
            for c in e.get("cells") or []:
                cw = "%s %s" % (w, c.get("cell_type"))
                if "state" not in c:
                    f.append(Finding("G4-disease", cw, "R5 VIOLATION: missing 'state' "
                                                      "(type x state is two-level by construction)"))
                if not c.get("pmid"):
                    f.append(Finding("G4-disease", cw, "R2 VIOLATION: no pmid"))
                ct = str(c.get("cell_type", "")).lower()
                # R5 guard: a state word must not be standing in as the cell type
                if ct in STATE_WORDS_HINT and ct not in LINEAGE_WORDS:
                    f.append(Finding("G4-disease", cw,
                                     "R5 VIOLATION: %r is a state word used as a cell type" % ct))


# ── G5: registry (R6 ground-truth admissibility) ──────────────────────────────
def gate_registry(root, f):
    p = root / "registry.yaml"
    if not p.exists():
        return
    try:
        import yaml
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception as exc:                                   # noqa: BLE001
        f.append(Finding("G5-registry", str(p), "unparseable YAML: %s" % exc))
        return
    for i, e in enumerate(data.get("datasets") or []):
        w = "registry.yaml#%d" % i
        for key in ("dataset_id", "accession", "species", "tissue",
                    "organism_stage", "annotation_level", "source"):
            if key not in e:
                f.append(Finding("G5-registry", w, "missing field %r" % key))
        _enum("G5-registry", w, e.get("organism_stage"), ORGANISM_STAGE, f)
        _enum("G5-registry", w, e.get("species"), SPECIES, f)
        lvl = e.get("annotation_level")
        _enum("G5-registry", w, lvl, ANNOTATION_LEVEL, f)
        if lvl is not None and lvl != "per_cell_author":
            f.append(Finding("G5-registry", w,
                             "R6: %r is NOT admissible as evaluation ground truth "
                             "(admissible: per_cell_author only)" % lvl,
                             severity="warning"))


# ── G6: query templates (inclusion_reason taxonomy) ───────────────────────────
def gate_templates(root, f):
    p = root / "query_templates.yaml"
    if not p.exists():
        return
    try:
        import yaml
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception as exc:                                   # noqa: BLE001
        f.append(Finding("G6-templates", str(p), "unparseable YAML: %s" % exc))
        return
    for i, t in enumerate(data.get("templates") or []):
        w = "query_templates.yaml#%d" % i
        for key in ("name", "query", "inclusion_reason"):
            if key not in t:
                f.append(Finding("G6-templates", w, "missing field %r" % key))
        _enum("G6-templates", w, t.get("inclusion_reason"), INCLUSION_REASON, f)
        if t.get("inclusion_reason") == "developmental_composition" and "stage_scope" not in t:
            f.append(Finding("G6-templates", w,
                             "developmental_composition requires 'stage_scope'"))


GATES = [
    ("G0-structure", gate_structure),
    ("G1-plugin",    gate_plugin),
    ("G2-markers",   gate_markers),
    ("G3-baselines", gate_baselines),
    ("G4-disease",   gate_disease),
    ("G5-registry",  gate_registry),
    ("G6-templates", gate_templates),
]


def validate(root):
    """Run every gate.  Returns (findings, stats)."""
    root = Path(root)
    findings = []
    for _, fn in GATES:
        out = fn(root, findings)
        # gates communicate by appending to `findings`; a gate must never
        # return a value (returning a dict here once leaked its keys into the
        # finding list as bare strings).
        if out:
            raise AssertionError("gate %r returned a value; gates must append only" % fn.__name__)
    # de-duplicate (some checks can fire from two call sites)
    seen, uniq = set(), []
    for fd in findings:
        key = (fd.gate, fd.path, fd.message)
        if key not in seen:
            seen.add(key)
            uniq.append(fd)
    errors = [x for x in uniq if x.severity == "error"]
    warnings = [x for x in uniq if x.severity == "warning"]
    stats = {
        "marker_files": len(_iter_json(root, "markers")),
        "baseline_files": len(_iter_json(root, "baselines")),
        "disease_files": len(_iter_json(root, "disease")),
        "errors": len(errors),
        "warnings": len(warnings),
    }
    return uniq, stats

"""kbkit command line.

    kbkit init <tissue> <dir>     scaffold a tissue plugin from the schema
    kbkit validate <dir>          run every machine gate
    kbkit serve <dir>             thin stdio query service over the plugin

`init` derives the skeleton from kbkit.schema, so the templates and the gates
cannot drift apart: there is one definition of what a plugin is.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import SCHEMA_VERSION, __version__
from .schema import (ANNOTATION_LEVEL, ASSAY, DIRECTION, EVIDENCE_LEVEL,
                     INCLUSION_REASON, ORGANISM_STAGE, SAMPLING_MATERIAL, SPECIES)
from .validate import GATES, validate


# ── init ──────────────────────────────────────────────────────────────────────
PLUGIN_YAML = """# {name} — tissue knowledge-base plugin
name: {tissue}-kb
tissue: {tissue}
species: [human]
schema_version: "{schema_version}"
plugin_version: "0.0.1"

# Every axis below is first-class.  organism_stage is NOT redundant with
# species+tissue: fetal, developing and adult tissue of the same organ are
# different knowledge domains and must not share entries.
axes:
  species: {species}
  tissue: [{tissue}]
  organism_stage: {stages}

# Pin the inputs this plugin was built against (corpus version, ontology
# release, marker panel version).  A plugin without a build lock is not
# reproducible.
build_lock:
  ontology_release: "UNSET"
  corpus_version: "UNSET"
  panel_version: "UNSET"

licence: "UNSET"
contact: ""
"""

MARKER_TEMPLATE = """[
  {{
    "entry_id": "{tissue}:0001",
    "schema_version": "{schema_version}",
    "species": "human",
    "tissue": "{tissue}",
    "organism_stage": "adult",
    "cell_type": "REPLACE_ME",
    "cl_id": "NO_MATCH",
    "version": "0.0.1",
    "discipline_note": "",
    "genes": [
      {{
        "gene": "REPLACE_ME",
        "direction": "+",
        "provenance": {{"pmid": "00000000"}},
        "evidence_level": "C",
        "context": "",
        "panel": "core"
      }}
    ]
  }}
]
"""

BASELINE_TEMPLATE = """[
  {{
    "entry_id": "{tissue}:baseline:0001",
    "schema_version": "{schema_version}",
    "species": "human",
    "tissue": "{tissue}",
    "organism_stage": "adult",
    "sampling_material": "other",
    "disease_stage": "control",
    "treatment_background": "none",
    "assay": "scRNA",
    "enrichment_step": "none",
    "n_donors": 2,
    "cells": [
      {{
        "cell_type": "REPLACE_ME",
        "proportion": [0.01, 0.05],
        "pmid": "00000000",
        "evidence_level": "C"
      }}
    ]
  }}
]
"""

DISEASE_TEMPLATE = """[
  {{
    "entry_id": "{tissue}:disease:0001",
    "schema_version": "{schema_version}",
    "species": "human",
    "tissue": "{tissue}",
    "organism_stage": "adult",
    "disease": "REPLACE_ME",
    "context": "",
    "unexpected_flags": [],
    "contamination_flags": [],
    "cells": [
      {{
        "cell_type": "REPLACE_ME",
        "state": "REPLACE_ME_STATE",
        "signature": [],
        "pmid": "00000000"
      }}
    ]
  }}
]
"""

REGISTRY_YAML = """# Datasets that may serve as reference baseline sources or as evaluation
# ground truth.
#
# annotation_level semantics:
#   per_cell_author    -> admissible as evaluation ground truth
#   per_cluster_author -> usable as reference, NOT as ground truth
#   per_cell_consensus -> our own call; using it as truth is circular
#   sorted_pool        -> not cells
#   none               -> unusable for both
datasets: []
"""

QUERY_TEMPLATES_YAML = """# Literature retrieval templates.  A paper is filed under the reason it was
# put in the corpus; the corpus is a reading basis, not an undifferentiated
# pile of PDFs.
#
# inclusion_reason must be one of:
{reasons}
templates: []
"""

ONTOLOGY_README = """# Ontology

Place the ontology sub-graph and the concept mapping table here.

Rules:
- Every cell-type entry must carry an ontology identifier, or the literal
  `NO_MATCH` when the ontology genuinely has no term.  A near term must never
  be attached by hand.
- The sub-graph is extracted from a pinned release; record the release in
  plugin.yaml's build_lock.ontology_release.
"""

EXTENSIONS_README = """# Extensions

Anything the core schema cannot express goes here rather than into the core
schema.  An empty directory is a valid state; an ad-hoc field added to a core
entity is not.

This directory exists so that the core stays tissue-independent: if a tissue
needs something the core does not model, that is evidence the core is working
as intended, not evidence it should grow.
"""


def cmd_init(args):
    root = Path(args.dir)
    tissue = args.tissue
    if root.exists() and any(root.iterdir()) and not args.force:
        print("refusing to write into non-empty directory: %s (use --force)" % root)
        return 2
    for sub in ("markers", "baselines", "disease", "ontology", "extensions"):
        (root / sub).mkdir(parents=True, exist_ok=True)

    (root / "plugin.yaml").write_text(
        PLUGIN_YAML.format(name=tissue, tissue=tissue, schema_version=SCHEMA_VERSION,
                           species=sorted(SPECIES), stages=sorted(ORGANISM_STAGE)),
        encoding="utf-8")
    (root / "markers" / "_TEMPLATE.json").write_text(
        MARKER_TEMPLATE.format(tissue=tissue, schema_version=SCHEMA_VERSION),
        encoding="utf-8")
    (root / "baselines" / "_TEMPLATE.json").write_text(
        BASELINE_TEMPLATE.format(tissue=tissue, schema_version=SCHEMA_VERSION),
        encoding="utf-8")
    (root / "disease" / "_TEMPLATE.json").write_text(
        DISEASE_TEMPLATE.format(tissue=tissue, schema_version=SCHEMA_VERSION),
        encoding="utf-8")
    (root / "registry.yaml").write_text(REGISTRY_YAML, encoding="utf-8")
    (root / "query_templates.yaml").write_text(
        QUERY_TEMPLATES_YAML.format(reasons="\n".join("  #   - " + r for r in sorted(INCLUSION_REASON))),
        encoding="utf-8")
    (root / "ontology" / "README.md").write_text(ONTOLOGY_README, encoding="utf-8")
    (root / "extensions" / "README.md").write_text(EXTENSIONS_README, encoding="utf-8")

    # vocabulary reference, generated from the schema so it cannot drift
    vocab = {
        "schema_version": SCHEMA_VERSION,
        "species": sorted(SPECIES),
        "organism_stage": sorted(ORGANISM_STAGE),
        "direction": sorted(DIRECTION),
        "evidence_level": sorted(EVIDENCE_LEVEL),
        "sampling_material": sorted(SAMPLING_MATERIAL),
        "assay": sorted(ASSAY),
        "annotation_level": sorted(ANNOTATION_LEVEL),
        "inclusion_reason": sorted(INCLUSION_REASON),
    }
    (root / "VOCABULARY.json").write_text(json.dumps(vocab, indent=2) + "\n", encoding="utf-8")
    print("scaffolded %s plugin at %s (schema %s)" % (tissue, root, SCHEMA_VERSION))
    print("next:  kbkit validate %s" % root)
    return 0


# ── validate ──────────────────────────────────────────────────────────────────
def cmd_validate(args):
    findings, stats = validate(args.dir)
    print("kbkit validate — %s" % args.dir)
    print("  schema %s | gates %s" % (SCHEMA_VERSION, ", ".join(g for g, _ in GATES)))
    print("  files: markers=%d baselines=%d disease=%d" % (
        stats["marker_files"], stats["baseline_files"], stats["disease_files"]))
    if findings:
        for fd in findings:
            print("  " + str(fd))
    print("  -> %d error(s), %d warning(s)" % (stats["errors"], stats["warnings"]))
    if stats["errors"]:
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


# ── serve ─────────────────────────────────────────────────────────────────────
def _load_plugin(root):
    import yaml
    cfg = yaml.safe_load((Path(root) / "plugin.yaml").read_text(encoding="utf-8"))
    entries = []
    d = Path(root) / "markers"
    if d.exists():
        for p in sorted(d.rglob("*.json")):
            if p.name.startswith("_"):
                continue
            data = json.loads(p.read_text(encoding="utf-8"))
            entries.extend(data if isinstance(data, list) else [data])
    return cfg, entries


def _rank(entries, genes, species=None, stage=None):
    """Rank cell types by directional marker overlap.

    score+ counts query genes matching a '+' marker of the entry;
    score- counts query genes matching a '-' marker.
    Ordering is a three-part total order: (-score+, +score-, entry_id).
    No weights are involved, and no default is invented when nothing matches.
    """
    gq = set(genes)
    rows = []
    for e in entries:
        if species and e.get("species") != species:
            continue
        if stage and e.get("organism_stage") != stage:
            continue
        pos = {g["gene"] for g in e.get("genes", []) if g.get("direction") == "+"}
        neg = {g["gene"] for g in e.get("genes", []) if g.get("direction") == "-"}
        rows.append({
            "entry_id": e["entry_id"],
            "cell_type": e.get("cell_type"),
            "cl_id": e.get("cl_id"),
            "score_pos": len(gq & pos),
            "score_neg": len(gq & neg),
            "matched_pos": sorted(gq & pos),
            "matched_neg": sorted(gq & neg),
        })
    rows.sort(key=lambda r: (-r["score_pos"], r["score_neg"], r["entry_id"]))
    return rows


def cmd_serve(args):
    """Thin line-oriented stdio service: one JSON request per line, one JSON
    response per line.  Deliberately minimal: a service shell, not a product."""
    cfg, entries = _load_plugin(args.dir)
    print(json.dumps({"ready": True, "tissue": cfg.get("tissue"),
                      "entries": len(entries), "schema_version": SCHEMA_VERSION}),
          flush=True)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError as exc:
            print(json.dumps({"error": "bad json: %s" % exc}), flush=True)
            continue
        if req.get("op") == "query_marker":
            rows = _rank(entries, req.get("genes") or [],
                         species=req.get("species"), stage=req.get("organism_stage"))
            if not rows or rows[0]["score_pos"] == 0:
                out = {"op": "query_marker", "result": "NO_MATCH",
                       "reason": "no positive-direction marker overlap",
                       "candidates": []}
            else:
                out = {"op": "query_marker", "result": rows[0]["cell_type"],
                       "top": rows[:req.get("top_k", 5)]}
            print(json.dumps(out), flush=True)
        elif req.get("op") == "ping":
            print(json.dumps({"op": "ping", "ok": True}), flush=True)
        else:
            print(json.dumps({"error": "unknown op %r" % req.get("op")}), flush=True)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="kbkit", description="tissue knowledge-base construction kit")
    ap.add_argument("--version", action="version", version="kbkit %s (schema %s)" % (__version__, SCHEMA_VERSION))
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="scaffold a tissue plugin")
    p.add_argument("tissue")
    p.add_argument("dir")
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser("validate", help="run every machine gate")
    p.add_argument("dir")
    p.set_defaults(fn=cmd_validate)

    p = sub.add_parser("serve", help="thin stdio query service")
    p.add_argument("dir")
    p.set_defaults(fn=cmd_serve)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())

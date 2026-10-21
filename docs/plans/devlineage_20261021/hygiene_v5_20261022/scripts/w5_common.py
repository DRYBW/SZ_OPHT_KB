#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w5_common.py — shared paths and helpers for the wave-5 lineage-hygiene card.

Everything this wave reads lives under one data root so the gate can be re-run from a clean
clone of the repository with `W5_DATA_ROOT=<root>` and no author-machine path baked into a
comparison (the data itself is local material and stays outside the repository; only the
wave's own scripts, artefacts and report are mirrored into the repository).

Nothing here writes anywhere except the wave's own directories.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys

WAVE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(WAVE, "out")
LEDGERS = os.path.join(WAVE, "ledgers")
LOGS = os.path.join(WAVE, "logs")
SCRIPTS = os.path.join(WAVE, "scripts")

# The data root. Local material (knowledge base, literature corpus, upstream waves) lives on the
# data volume and is never copied into a repository; it is named once here so a reader can see
# every input and so a clone can be pointed at the same root explicitly.
DATA_ROOT = os.environ.get("W5_DATA_ROOT", "/mnt/D/EyeKB")

DEVLIN = os.path.join(DATA_ROOT, "plans", "devlineage_20261021")
SCAFFOLD = os.path.join(DEVLIN, "scaffold")
SCAF_OUT = os.path.join(SCAFFOLD, "out")
MARKERS = os.path.join(DEVLIN, "markers")
MK_OUT = os.path.join(MARKERS, "out")
MK_SCRIPTS = os.path.join(MARKERS, "scripts")
CONTRACT = os.path.join(DEVLIN, "DATA_CONTRACT_devlineage_v1.md")

CLD = os.path.join(DATA_ROOT, "plans", "cl_depth_devlineage_20261021")
CLD_OUT = os.path.join(CLD, "out")
CLD_SCRIPTS = os.path.join(CLD, "scripts")
CLD_B1 = os.path.join(CLD_SCRIPTS, "b1_build_lineage.py")

KB = os.path.join(DATA_ROOT, "kb")
KB_MARKERS = os.path.join(KB, "markers")
REPO = "/home/ubuntu/EYEKB_REPO"
REPO_KB = os.path.join(REPO, "kb")
REPO_KB_MARKERS = os.path.join(REPO_KB, "markers")
REPO_CORE = os.path.join(REPO, "mcp_server", "eyekb_core.py")
SITE_CORE = os.path.join(DATA_ROOT, "mcp_server", "eyekb_core.py")

ONT = os.path.join(DATA_ROOT, "plans", "devline_ont_20261002", "downloads", "cl.obo")
CORPUS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10"
CHUNKS = os.path.join(CORPUS, "chunks.parquet")
PAPERS = os.path.join(CORPUS, "papers.jsonl")

# the recorded production query set (default-behaviour identity proof)
GOLDEN = os.path.join(DATA_ROOT, "plans", "holefill_v12_20261021", "golden_721.py")
GOLDEN_RECORDED = os.path.join(DATA_ROOT, "plans", "holefill_v12_20261021", "out",
                               "golden_721_BEFORE.json")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_tsv(path, rows, cols):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter="\t", extrasaction="ignore",
                           lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def markers_common():
    """The marker layer's own shared module, imported read-only.

    Reused rather than re-implemented: the four-condition admission rule, the panel loader and
    the evaluation-side vocabulary must be the *same* code this wave reconciles against, not a
    second dialect of it.
    """
    if MK_SCRIPTS not in sys.path:
        sys.path.insert(0, MK_SCRIPTS)
    import mkcommon  # noqa: E402
    return mkcommon


def free_gib():
    with open("/proc/meminfo", encoding="utf-8") as f:
        for line in f:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / 1048576.0
    return -1.0
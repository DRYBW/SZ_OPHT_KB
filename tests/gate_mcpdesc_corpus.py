#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/gate_mcpdesc_corpus.py — G11 gate: the shipped description's corpus numbers are
enforced against the bundled corpus, not trusted.

Why this gate exists (card t_2a047be0, 2026-10-25)
    The service description hard-coded its launch-era corpus size ("bundled corpus of
    2,713 papers / 174,616 passages" = the v2.0_2026-09 build, retired as built-in on
    2026-10-01) while the bundled corpus had been re-cut to v2.4.2_2026-09_slim
    (3,869 papers / 242,928 passages). The description now renders from
    mcp_server/corpus_stats.py, which reads the bundled corpus' own build record
    (literature_db/v2.4.2_2026-09_slim/build_stats.json, keys n_papers / n_chunks) at
    import time, with a frozen fallback for a fresh clone (the corpus is not in the git
    tree — G2 Release asset). This gate re-derives every number from disk and FAILs when
    they stop agreeing.

Checks (each fail-closed; a FAIL names the check code, never just "G11 FAIL"):
  G11-C01 STATS-SOURCE        the bundled build_stats.json parses; n_papers / n_chunks are
                              positive ints. Absent file (fresh clone, G2 asset not
                              unpacked) is INCONCLUSIVE, not a pass: the description cannot
                              be verified against the corpus on this tree (the chain counts
                              rc=3 as not-pass, same shape as the G3 degraded-engine
                              precedent). A present-but-malformed record is FAIL.
  G11-C02 RENDER-NO-HARDCODE  the description's corpus clause in mcp_server/server.py is fed
                              by corpus_stats (no digit baked into the clause — a hand-edited
                              literal is exactly the defect this gate exists for), and the
                              retired v2.0 numbers (their literal forms) appear nowhere in
                              server.py. corpus_stats.py is exempt from the stale-number
                              scan on purpose: its provenance docstring quotes the retired
                              numbers as the reason the gate exists (a registered
                              reference, not a rendered claim).
  G11-C03 RENDER-MATCH        the numbers corpus_stats actually renders (the same module the
                              server description is built from) equal the bundled
                              build_stats.json on disk. Guards the dynamic machinery itself:
                              a re-pointed/rewritten module that renders a different corpus
                              than the one bundled FAILs here.
  G11-C04 FALLBACK-IDENTITY   the frozen fallback constants (what a fresh clone sees before
                              the G2 asset is unpacked) equal the pointer's registered
                              v2.4.2_2026-09 identity (kb/literature_db/EYEKB_DB_POINTER.yaml,
                              block v2.4.2_2026-09, keys unique_papers / chunks —
                              repo-committed, so this check is verifiable on any clone) and
                              that block still is role: default. A digit sabotaged in the
                              fallback FAILs here.
  G11-C05 POINTER-AGREE       the bundled build record (live) equals the pointer's registered
                              v2.4.2 identity — the G2 asset and the registered default
                              corpus are the same build; a re-cut that updated one but not
                              the other FAILs here. INCONCLUSIVE together with C01 when the
                              corpus asset is absent.
  G11-C06 SELF-TEST           the gate's own comparators are proven to flag the planted
                              violation shapes (hard-coded literal clause, drifted pair,
                              mutated pointer) — so a scanner that flags nothing cannot pass.
                              Runs against synthetic strings only; the real tree is never
                              modified.

Stdlib only; zero network; zero GPU; read-only on the real tree (the self-test uses
synthetic in-memory strings). Deterministic; no wall-clock input.

Usage (from anywhere; paths resolve off this file's location):
  python3 tests/gate_mcpdesc_corpus.py
  python3 tests/gate_mcpdesc_corpus.py --json out/G11_RESULTS.json

Exit codes: 0 = PASS, 2 = FAIL (fail-closed), 3 = INCONCLUSIVE (corpus asset absent on
this tree; the one-click entry counts rc=3 as not-pass).
"""
from __future__ import annotations

import argparse
import importlib.util
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER_PY = ROOT / "mcp_server" / "server.py"
CORPUS_STATS_PY = ROOT / "mcp_server" / "corpus_stats.py"
BUILD_STATS_JSON = ROOT / "literature_db" / "v2.4.2_2026-09_slim" / "build_stats.json"
POINTER_YAML = ROOT / "kb" / "literature_db" / "EYEKB_DB_POINTER.yaml"

POINTER_BLOCK = "v2.4.2_2026-09"           # role: default — the registered built-in identity
SENTINEL_CLAUSE = "bundled corpus of"      # the description's corpus clause marker
SENTINEL_END = "covering the whole eye"
STALE_NUMBERS = re.compile(r"2,?713|174,?616")   # retired v2.0_2026-09 identity, literal forms


def sha256_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ------------------------------------------------------------------ C01
def check_stats_source():
    if not BUILD_STATS_JSON.is_file():
        return "INCONCLUSIVE", None, (
            f"bundled build record not on disk: {BUILD_STATS_JSON.relative_to(ROOT)} "
            f"(fresh clone; the corpus ships as the G2 Release asset)")
    try:
        data = json.loads(BUILD_STATS_JSON.read_text(encoding="utf-8"))
        papers = int(data["n_papers"])
        chunks = int(data["n_chunks"])
        if papers <= 0 or chunks <= 0:
            raise ValueError(f"non-positive counts n_papers={papers} n_chunks={chunks}")
        return "PASS", {"papers": papers, "chunks": chunks}, ""
    except Exception as exc:
        return "FAIL", None, f"malformed build record: {exc}"


# ------------------------------------------------------------------ C02
def find_description_block(src: str) -> str:
    """The description=( ... ) argument block of the MCPServer() call (heuristic slice)."""
    start = src.find("description=(")
    if start < 0:
        raise ValueError("no description=( found in server.py")
    end = src.find("instructions=(", start)
    if end < 0:
        raise ValueError("no instructions=( found after description=( — block boundary moved")
    return src[start:end]


def clause_offenses(desc_block: str) -> list:
    """Hard-coded digits (or a missing corpus_stats reference) inside the corpus clause."""
    off = []
    i = desc_block.find(SENTINEL_CLAUSE)
    if i < 0:
        return [f"description block: no {SENTINEL_CLAUSE!r} clause found"]
    j = desc_block.find(SENTINEL_END, i)
    if j < 0:
        return [f"description block: no {SENTINEL_END!r} after the clause (boundary moved)"]
    clause = desc_block[i + len(SENTINEL_CLAUSE):j]
    digits = [ch for ch in clause if ch.isdigit()]
    if digits:
        off.append("corpus clause contains baked-in digits "
                   f"{digits!r} in {clause!r} (the numbers must render from corpus_stats, "
                   f"not a literal)")
    if "corpus_stats." not in clause:
        off.append(f"corpus clause no longer references corpus_stats "
                   f"(dynamic render unwired): {clause!r}")
    return off


def check_render_no_hardcode():
    src = SERVER_PY.read_text(encoding="utf-8")
    off = []
    try:
        desc = find_description_block(src)
        off += clause_offenses(desc)
    except ValueError as exc:
        off.append(str(exc))
    hits = STALE_NUMBERS.findall(src)
    off += [f"retired v2.0 number {h!r} present in server.py" for h in hits]
    return ("PASS" if not off else "FAIL"), off


# ------------------------------------------------------------------ module loading
def load_corpus_stats_module():
    spec = importlib.util.spec_from_file_location("gate_g11_corpus_stats", CORPUS_STATS_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ C03
def check_render_match(mod, stats):
    if stats is None:
        return "INCONCLUSIVE", None, "no live build record on this tree (see C01)"
    papers, chunks, source = mod.corpus_stats()
    if (papers, chunks) != (stats["papers"], stats["chunks"]):
        return "FAIL", {"rendered": [papers, chunks],
                        "build_stats": [stats["papers"], stats["chunks"]]}, \
               "rendered numbers disagree with the bundled build record"
    expected = f"{papers:,} papers / {chunks:,} passages"
    if mod.BUNDLED_CORPUS_LINE != expected:
        return "FAIL", {"BUNDLED_CORPUS_LINE": mod.BUNDLED_CORPUS_LINE,
                        "expected": expected}, \
               "BUNDLED_CORPUS_LINE does not match corpus_stats() output"
    return "PASS", {"rendered": [papers, chunks], "source": source}, ""


# ------------------------------------------------------------------ C04/C05
def pointer_block_numbers(text: str, block_name: str):
    """(numbers, role_line) for a two-space-indented block in EYEKB_DB_POINTER.yaml.

    Stdlib mini-parse: the pointer file is YAML-shaped but the gate deliberately reads only
    the two numeric keys and the role of the named block, so no YAML dependency is taken.
    """
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == block_name + ":" and ln.startswith("  "):
            start = i
            break
    if start is None:
        raise ValueError(f"pointer block {block_name} not found")
    out, role_line = {}, ""
    for ln in lines[start + 1:]:
        if ln.strip() and not ln.startswith("    "):
            break  # dedent: the block ended
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("role:"):
            role_line = s.split("#", 1)[0].strip()
        for key in ("chunks", "unique_papers"):
            if s.startswith(key + ":"):
                raw = s.split(":", 1)[1].split("#", 1)[0].strip()
                out[key] = int(raw)
    for key in ("chunks", "unique_papers"):
        if key not in out:
            raise ValueError(f"pointer block {block_name}: missing {key}")
    return out, role_line


def check_fallback_identity(mod):
    try:
        nums, role_line = pointer_block_numbers(
            POINTER_YAML.read_text(encoding="utf-8"), POINTER_BLOCK)
    except Exception as exc:
        return "FAIL", None, f"pointer identity unreadable: {exc}"
    if "default" not in role_line:
        return "FAIL", {"role_line": role_line}, \
               f"pointer block {POINTER_BLOCK} is no longer role: default — the fallback pins the wrong block"
    fb = (int(mod.FALLBACK_PAPERS), int(mod.FALLBACK_CHUNKS))
    reg = (nums["unique_papers"], nums["chunks"])
    if fb != reg:
        return "FAIL", {"fallback": list(fb), "pointer": list(reg)}, \
               f"fallback constants disagree with the pointer's registered {POINTER_BLOCK} identity"
    return "PASS", {"fallback": list(fb), "pointer": list(reg)}, ""


def check_pointer_agree(stats):
    if stats is None:
        return "INCONCLUSIVE", None, "no live build record on this tree (see C01)"
    try:
        nums, _role = pointer_block_numbers(
            POINTER_YAML.read_text(encoding="utf-8"), POINTER_BLOCK)
    except Exception as exc:
        return "FAIL", None, f"pointer identity unreadable: {exc}"
    live = (stats["papers"], stats["chunks"])
    reg = (nums["unique_papers"], nums["chunks"])
    if live != reg:
        return "FAIL", {"build_stats": list(live), "pointer": list(reg)}, \
               f"bundled build record disagrees with the pointer's registered {POINTER_BLOCK} identity"
    return "PASS", {"build_stats": list(live), "pointer": list(reg)}, ""


# ------------------------------------------------------------------ C06
def _pairs_equal(a, b) -> bool:
    return (a["papers"], a["chunks"]) == (b["papers"], b["chunks"])


def self_test() -> list:
    """Planted-shape battery over the gate's own comparators (synthetic strings only)."""
    off = []
    bad_clause = ('"(1) Literature retrieval over a "\n'
                  '                 "bundled corpus of 3,859 papers / 242,918 passages '
                  'covering the whole eye; "')
    if not clause_offenses(bad_clause):
        off.append("self-test: a hard-coded clause was not flagged")
    good_clause = ('"(1) Literature retrieval over a "\n'
                   '                 f"bundled corpus of {corpus_stats.BUNDLED_CORPUS_LINE} '
                   'covering the whole eye; "')
    fp = clause_offenses(good_clause)
    if fp:
        off.append(f"self-test: the clean dynamic clause was flagged (false positive): {fp}")
    ref = {"papers": 3869, "chunks": 242928}
    if _pairs_equal({"papers": 3860, "chunks": 242928}, ref):
        off.append("self-test: a drifted paper count pair was treated as equal")
    if not _pairs_equal({"papers": 3869, "chunks": 242928}, ref):
        off.append("self-test: an equal pair was treated as drifted")
    try:
        mutated = ("# synthetic\n  v imaginary:\n    chunks: 1\n    unique_papers: 1\n"
                   "  v2.4.2_2026-09:\n    role: default\n"
                   "    chunks: 242927\n    unique_papers: 3869\n")
        nums, _role = pointer_block_numbers(mutated, POINTER_BLOCK)
        if nums != {"chunks": 242927, "unique_papers": 3869}:
            off.append(f"self-test: pointer parser mis-read the mutated block: {nums}")
    except Exception as exc:
        off.append(f"self-test: pointer parser failed on a well-formed synthetic block: {exc}")
    return off


# ------------------------------------------------------------------ driver
def main() -> int:
    ap = argparse.ArgumentParser(description="G11: description corpus numbers vs bundled corpus")
    ap.add_argument("--json", default="", help="write the machine-readable runout here")
    args = ap.parse_args()

    checks: list = []

    def add(cid, name, verdict, detail, extra=None):
        row = {"id": cid, "name": name, "verdict": verdict, "detail": detail}
        if extra:
            row["extra"] = extra
        checks.append(row)

    v1, stats, d1 = check_stats_source()
    add("G11-C01", "STATS-SOURCE", v1,
        d1 or f"bundled build record parses: n_papers={stats['papers']}, "
              f"n_chunks={stats['chunks']}",
        ({"path": str(BUILD_STATS_JSON.relative_to(ROOT)),
          "sha256": sha256_of(BUILD_STATS_JSON)} if stats else None))

    v2, off2 = check_render_no_hardcode()
    add("G11-C02", "RENDER-NO-HARDCODE", v2,
        "; ".join(off2) if off2 else
        "corpus clause renders from corpus_stats; retired v2.0 numbers absent from server.py")

    try:
        mod = load_corpus_stats_module()
    except Exception as exc:
        add("G11-C03", "RENDER-MATCH", "FAIL", f"corpus_stats module failed to import: {exc}")
        add("G11-C04", "FALLBACK-IDENTITY", "FAIL", "fallback identity unverifiable (module broken)")
    else:
        v3, x3, d3 = check_render_match(mod, stats)
        add("G11-C03", "RENDER-MATCH", v3, d3 or
            (f"rendered == bundled build record: {x3['rendered'][0]} papers / "
             f"{x3['rendered'][1]} chunks ({x3['source']})" if isinstance(x3, dict) else ""),
            x3 if isinstance(x3, dict) else None)
        v4, x4, d4 = check_fallback_identity(mod)
        add("G11-C04", "FALLBACK-IDENTITY", v4, d4 or
            (f"fallback == pointer {POINTER_BLOCK} identity: "
             f"{x4['pointer'][0]} papers / {x4['pointer'][1]} chunks"
             if isinstance(x4, dict) else ""),
            x4 if isinstance(x4, dict) else None)

    v5, x5, d5 = check_pointer_agree(stats)
    add("G11-C05", "POINTER-AGREE", v5, d5 or "bundled build record == registered v2.4.2 identity",
        x5 if isinstance(x5, dict) else None)

    off6 = self_test()
    add("G11-C06", "SELF-TEST", "FAIL" if off6 else "PASS",
        "; ".join(off6) if off6 else
        "planted hard-coded clause / drifted pair / mutated pointer all flagged")

    verdicts = {c["verdict"] for c in checks}
    if "FAIL" in verdicts:
        final, rc = "FAIL", 2
    elif "INCONCLUSIVE" in verdicts:
        final, rc = "INCONCLUSIVE", 3
    else:
        final, rc = "PASS", 0

    summary = {
        "gate": "G11",
        "script": "tests/gate_mcpdesc_corpus.py",
        "final": final,
        "ok": final == "PASS",
        "checks": checks,
    }
    lines = "\n".join(f"  {c['id']} {c['name']:<20} {c['verdict']:<13} "
                      f"{(c['detail'] or '')[:140]}" for c in checks)
    print(f"[G11] description corpus coherence: {final} (rc={rc})")
    print(lines)
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n",
                                   encoding="utf-8")
        print(f"[G11] runout -> {args.json}")
    return rc


if __name__ == "__main__":
    sys.exit(main())

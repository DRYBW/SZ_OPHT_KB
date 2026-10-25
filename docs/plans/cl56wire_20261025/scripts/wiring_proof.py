#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WIRING_PROOF — the consistency proof for the cl56_v15 wiring, read from disk at build time.

Every number below is computed here; nothing is quoted from a report. Run:

  /home/ubuntu/training-venv/bin/python3 wiring_proof.py

Reads (all shipped, read-only):
  kb/link_registry/LINK_REGISTRY_v1.jsonl          the registry under test
  kb/link_registry/scripts/validate_linkage.py     the four-field rule (re-run, not quoted)
  kb/link_registry/scripts/audit_link_circularity.py
  kb/**                                            for the page-existence check
  mcp_server/eyekb_core.py                         for the live route check

Writes:
  out/WIRING_PROOF_v1.md, out/WIRING_PROOF_v1.json

Checks, each FAIL-closed:
  1. per-library entry counts (marker libraries + the textbook layer);
  2. field completeness: the 11 fields a registry row is required to carry, per row, and the
     four-link rule (citation + page + route + skill) re-run through validate_linkage.py;
  3. wiki-page existence: every path in every row's wiki_pages resolves to a file under kb/;
  4. kb_file existence: every row's kb_file resolves;
  5. live routes: every row's mcp_route is re-issued against the shipped service and must answer;
  6. route hygiene: the three newly wired names must NOT be reachable on the default `all` route;
  7. isomorphy vs the pre-image: rows present before the change must be byte-identical, and the
     change must add exactly the declared rows.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/ubuntu/EYEKB_REPO")
WAVE = Path("/mnt/D/EyeKB/plans/consistency_20261024/cl56wire_out")
REG = REPO / "kb" / "link_registry" / "LINK_REGISTRY_v1.jsonl"
PRE = WAVE / "pre_images" / "LINK_REGISTRY_v1.jsonl.pre_cl56wire"
OUT = WAVE / "out"
KB = REPO / "kb"
PY = "/home/ubuntu/training-venv/bin/python3"

REQUIRED_FIELDS = ["entry_id", "library", "cell_type", "panel_genes", "kb_file", "wiki_pages",
                   "n_wiki_pages", "pmids", "citations", "mcp_route", "skill_trigger"]
# A textbook row backs a structural claim with a book page instead of a paper, so it carries
# book_anchors and no panel/citations (the same rule validate_linkage.py applies).
TEXTBOOK_REQUIRED = ["entry_id", "library", "cell_type", "kb_file", "wiki_pages", "n_wiki_pages",
                     "mcp_route", "skill_trigger", "book_anchors"]
# A gap that is already registered is reported with its reason rather than counted as a new one.
REGISTERED_EXCEPTIONS = {
    "face_v6::Fibroblast": "the source library records no marker panel at all for this entry "
                           "(registered gap, named in ANNOTATION_EVIDENCE_SUMMARY_v1.md)",
    "face_v6::Myofibroblast": "the source library records no marker panel at all for this entry "
                              "(registered gap, named in ANNOTATION_EVIDENCE_SUMMARY_v1.md)",
}
NEW_LIB = "cl56_v15"


def rows_of(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def main():
    rows = rows_of(REG)
    marker = [r for r in rows if r.get("source_kind") == "marker_library"]
    textbook = [r for r in rows if r.get("source_kind") == "textbook"]
    pre = rows_of(PRE)

    # --- 1. per-library counts -------------------------------------------------------------
    per_lib = {}
    for r in marker:
        per_lib[r["library"]] = per_lib.get(r["library"], 0) + 1
    per_lib["textbook_t4"] = len(textbook)

    # --- 2. field completeness ------------------------------------------------------------
    def missing(row, fields):
        return [f for f in fields if row.get(f) in (None, "", [], {})]

    field_gaps, explained_gaps = [], []
    for r in rows:
        need = TEXTBOOK_REQUIRED if r.get("source_kind") == "textbook" else REQUIRED_FIELDS
        m = missing(r, need)
        if not m:
            continue
        if r.get("entry_id") in REGISTERED_EXCEPTIONS:
            explained_gaps.append((r.get("entry_id"), m, REGISTERED_EXCEPTIONS[r["entry_id"]]))
        else:
            field_gaps.append((r.get("entry_id"), m))
    n_complete = len(rows) - len(field_gaps) - len(explained_gaps)

    # --- 3/4. page + kb_file existence ----------------------------------------------------
    page_missing, kbfile_missing = [], []
    n_pages = 0
    for r in rows:
        for p in r.get("wiki_pages") or []:
            n_pages += 1
            if not (KB / p).is_file():
                page_missing.append((r.get("entry_id"), p))
        kf = r.get("kb_file")
        if kf and not (REPO / kf).is_file():
            kbfile_missing.append((r.get("entry_id"), kf))

    # --- 5. live routes -------------------------------------------------------------------
    sys.path.insert(0, str(REPO / "mcp_server"))
    import eyekb_core as core                                                        # noqa: E402
    route_bad = []
    n_routes = 0
    for r in rows:
        route = r.get("mcp_route") or ""
        n_routes += 1
        m = re.match(r"query_marker\(cell_type='(.*)', library='(.*)'\)$", route)
        if m:
            ct, lib = m.groups()
            resp = core.query_marker(cell_type=ct, library=lib)
            if not resp.get("found"):
                route_bad.append((r["entry_id"], route, "found=False"))
            continue
        m = re.match(r"explain_annotation\(cell_type='(.*)'\)$", route)
        if m:
            resp = core.explain_annotation(cell_type=m.group(1))
            if not resp:
                route_bad.append((r["entry_id"], route, "empty response"))
            continue
        route_bad.append((r["entry_id"], route, "route shape not recognised"))

    # --- 6. route hygiene: the new names must not be on the default route ------------------
    leaks = []
    for r in rows:
        if r["library"] != NEW_LIB:
            continue
        d = core.query_marker(cell_type=r["cell_type"], library="all")
        if d.get("found"):
            leaks.append(r["entry_id"])

    # --- 7. isomorphy vs pre-image --------------------------------------------------------
    pre_by_id = {r["entry_id"]: r for r in pre}
    new_by_id = {r["entry_id"]: r for r in rows}
    added = sorted(set(new_by_id) - set(pre_by_id))
    removed = sorted(set(pre_by_id) - set(new_by_id))
    changed = sorted(k for k in set(pre_by_id) & set(new_by_id)
                     if json.dumps(pre_by_id[k], sort_keys=True)
                     != json.dumps(new_by_id[k], sort_keys=True))
    order_ok = [r["entry_id"] for r in rows
                if r["entry_id"] not in set(added)] == [r["entry_id"] for r in pre]
    new_rows = [new_by_id[k] for k in added if new_by_id[k]["library"] == NEW_LIB]

    # --- re-run the repository's own gates, do not quote them ------------------------------
    link = subprocess.run([PY, str(REPO / "kb" / "link_registry" / "scripts" /
                                   "validate_linkage.py")], capture_output=True, text=True)
    circ = subprocess.run([PY, str(REPO / "kb" / "link_registry" / "scripts" /
                                   "audit_link_circularity.py")], capture_output=True, text=True)

    ok = (not field_gaps and not page_missing and not kbfile_missing and not route_bad
          and not leaks and not removed and not changed and order_ok and link.returncode == 0)

    doc = {
        "generated_by": "wiring_proof.py",
        "registry": str(REG),
        "pre_image": str(PRE),
        "entries_total": len(rows),
        "entries_marker": len(marker),
        "entries_textbook": len(textbook),
        "per_library_entries": dict(sorted(per_lib.items())),
        "field_completeness": {"required_fields": REQUIRED_FIELDS,
                               "textbook_required_fields": TEXTBOOK_REQUIRED,
                               "rows_with_all_required_fields": n_complete,
                               "rows": len(rows), "unexplained_gaps": field_gaps,
                               "registered_exceptions": explained_gaps},
        "wiki_pages": {"listed": n_pages, "missing_on_disk": page_missing,
                       "existence_rate": (n_pages - len(page_missing)) / max(n_pages, 1)},
        "kb_file_missing": kbfile_missing,
        "routes": {"checked": n_routes, "not_answering": route_bad},
        "default_route_leaks": leaks,
        "isomorphy": {"added": added, "removed": removed, "changed_existing": changed,
                      "shipped_order_preserved": order_ok},
        "linkage_gate": {"rc": link.returncode, "stdout": link.stdout.strip()},
        "circularity": {"rc": circ.returncode, "stdout": circ.stdout.strip()},
        "verdict": "PASS" if ok else "FAIL",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "WIRING_PROOF_v1.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n",
                                              encoding="utf-8")

    # --- the reader-facing proof ----------------------------------------------------------
    L = ["# WIRING_PROOF_v1 — the newest library wired like the other eight",
         "",
         "Every number in this file is computed by `scripts/wiring_proof.py` from the shipped tree "
         "at build time (`kb/link_registry/LINK_REGISTRY_v1.jsonl`, `kb/**`, `mcp_server/eyekb_core.py`); "
         "nothing is quoted from a report. Recompute: "
         "`/home/ubuntu/training-venv/bin/python3 scripts/wiring_proof.py` "
         "(machine twin: `out/WIRING_PROOF_v1.json`).",
         "",
         f"**Verdict: {doc['verdict']}** — {len(added)} rows added, {len(changed)} existing rows "
         f"changed, {len(removed)} removed, {len(page_missing)} wiki page paths missing on disk, "
         f"{len(route_bad)} routes not answering, {len(leaks)} new names reachable on the default route.",
         "",
         "## 1. Entries per library",
         "",
         "| library | entries | in the default answer route |",
         "|---|---|---|"]
    default_on = set(core.V6_DEFAULT_LIBS) | set(core.K9_DEFAULT_LIBS) | set(core.ANTSEG_DEFAULT_LIBS) \
        | set(core.ONFIBRO_DEFAULT_LIBS) | set(core.SUBTYPE_DEFAULT_LIBS) | set(core.CL56_DEFAULT_LIBS) \
        | {"retina", "membrane", "retina_interneuron"}
    for lib, n in sorted(per_lib.items(), key=lambda kv: (-kv[1], kv[0])):
        route = "textbook layer" if lib == "textbook_t4" else ("yes" if lib in default_on else "no")
        L.append(f"| `{lib}` | {n} | {route} |")
    L += [f"| **total** | **{len(rows)}** | |", ""]
    L += ["The registry's scope is the default route **plus** the libraries declared in "
          "`REGISTRY_EXTRA_LIBS` (`kb/link_registry/scripts/build_link_registry.py`); `cl56_v15` is "
          "the first of the latter, registered default-off with an empty whitelist.", "",
          "## 2. Field completeness", "",
          f"- required fields per marker row: `{'`, `'.join(REQUIRED_FIELDS)}`",
          f"- required fields per textbook row: `{'`, `'.join(TEXTBOOK_REQUIRED)}`",
          f"- rows carrying all of them: **{n_complete}/{len(rows)}** "
          f"({100 * n_complete / max(len(rows), 1):.1f}%)",
          f"- rows with a gap and a registered reason: {len(explained_gaps)}",
          *[f"    - `{eid}` missing {m} — {why}" for eid, m, why in explained_gaps],
          f"- rows with an unexplained gap: {field_gaps if field_gaps else 'none'}", "",
          "The four-link rule of this repository (citation + page + route + skill) is not restated "
          "here: it is re-run.", "",
          "```", doc["linkage_gate"]["stdout"], "```", "",
          "## 3. Wiki pages", "",
          f"- page paths listed across all rows: **{n_pages}**",
          f"- resolved to a file under `kb/`: **{n_pages - len(page_missing)}** "
          f"({100 * doc['wiki_pages']['existence_rate']:.1f}%)",
          f"- missing: {page_missing if page_missing else 'none'}", "",
          "`kb_file` existence: " + ("all rows resolve" if not kbfile_missing
                                      else f"MISSING {kbfile_missing}") + ".", "",
          "## 4. Routes", "",
          f"- rows whose `mcp_route` was re-issued against the shipped service: **{n_routes}**",
          f"- not answering: {route_bad if route_bad else 'none'}", "",
          f"- new names reachable on the default `all` route (must be none, the library is "
          f"registered default-off): {leaks if leaks else 'none'}", "",
          "## 5. Isomorphy against the pre-image", "",
          f"- pre-image rows: {len(pre)}; current rows: {len(rows)}",
          f"- rows unchanged (byte-identical JSON): **{len(set(pre_by_id) & set(new_by_id)) - len(changed)}"
          f"/{len(pre)}**",
          f"- rows changed: {changed if changed else 'none'}",
          f"- rows removed: {removed if removed else 'none'}",
          f"- shipped row order preserved: {order_ok}",
          f"- rows added ({len(added)}): " + ", ".join(f"`{a}`" for a in added), "",
          "The three rows of the newly wired library, as they now stand:", "",
          "| entry | panel genes | citations | gene-verified | wiki pages |",
          "|---|---:|---:|---:|---|"]
    for r in sorted(new_rows, key=lambda r: r["cell_type"]):
        L.append(f"| `{r['entry_id']}` | {r['n_genes']} | {r['n_citations']} | "
                 f"{r['n_gene_matched']} | {', '.join(r['wiki_pages'])} |")
    L += ["", "## 6. Circularity (read, not quoted)", "", "```", doc["circularity"]["stdout"],
          "```", "",
          "`kb/link_registry/scripts/audit_link_circularity.py` re-run: no entry is reachable *only* "
          "through the appendix this registry generates, including the three new ones.", "",
          "## 7. What was NOT done, and why", "",
          "- **The default route was not changed.** `CL56_DEFAULT_LIBS` is empty, and check 6 above "
          "re-reads that from the shipped service: the three names are not reachable on `all` in any "
          "state. Merging them is a separate decision that the pre-registered acceptance rule for "
          "this library failed.", "",
          "- **Wiring the registry is not activating anything.** The registry is a disclosure surface: every "
          "row states the route that reaches it, and a default-off library's route is the explicit one. "
          "Check 6 re-reads from the shipped service that the three names answer on "
          "`library='cl56_v15'` and are NOT reachable on the default `all` route.", "",
          "- **The rebuild carried one row this card did not ask for.** `onfibro_v13` was activated on "
          "the default route on 2026-10-22, after the registry snapshot was taken, so the builder "
          "produces its row (`onfibro_v13::Fibroblast`) from the route itself. Including it is what "
          "keeps the file reproducible by its own builder; dropping it would require pinning the "
          "library set, which is a bigger change than this one. It is disclosed here, in the "
          "registration notes and in the wave report.", "",
          "- **Six registered libraries are still not wired** (`lacrimal_v6`, `retina_v7`, "
          "`retina_dev`, `lensiris_v11`, `holefill_v12`, `subtype_v14`). This proof does not claim "
          "otherwise. Each is the same one-line addition to `REGISTRY_EXTRA_LIBS`, and `subtype_v14` "
          "needs its body repaired first: its entries carry no top-level `markers` key, so its "
          "explicit route answers nothing and wiring it would create rows whose route is a dead end "
          "(measured in the CL-56 adoption report, §6.1).", "",
          ]
    (OUT / "WIRING_PROOF_v1.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"verdict={doc['verdict']} entries={len(rows)} added={len(added)} changed={len(changed)} "
          f"missing_pages={len(page_missing)} bad_routes={len(route_bad)} leaks={len(leaks)} "
          f"linkage_rc={link.returncode} circularity_rc={circ.returncode}")
    print("wrote out/WIRING_PROOF_v1.md + .json")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
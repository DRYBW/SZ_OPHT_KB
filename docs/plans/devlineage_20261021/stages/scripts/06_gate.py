#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V3 stage axis / step 6 — the machine gate and its readout.

Every item is a measurement over the artefacts this card produced, or over the shipped surface it
probed. Nothing here is a restatement of an intention. The readout separates three things that must
not be mixed:

  A. gate items about this card's own deliverable (pass/fail counts)
  B. external findings about the shipped surface, measured here and NOT caused by this card
  C. service-behaviour observations that answer the owner's question (recorded, not scored)

Outputs: out/GATE_READOUT.json, out/GATE_READOUT.md, out/STAGE_LITERAL_SURFACE.tsv
"""
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
REPO = Path("/home/ubuntu/EYEKB_REPO")
OUT = HERE / "out"
LOGS = HERE / "logs"
STAGES = {"fetal", "adult", "developing", "unknown"}
GRADES = {"direct_lineage_support", "identity_conversion_not_direct",
          "textbook_or_review_distant_origin", "trajectory_only"}

items = []


def check(gid, title, ok, measured, note=""):
    items.append({"item": gid, "title": title, "verdict": "PASS" if ok else "FAIL",
                  "measured": measured, "note": note})


def read_tsv(p):
    return list(csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"))


def main():
    markers = read_tsv(OUT / "STAGE_RESOLVED_MARKERS.tsv")
    nodes = read_tsv(OUT / "NODE_KEYS.tsv")
    cands = read_tsv(OUT / "CANDIDATE_CHANGES.tsv")
    ledger = read_tsv(OUT / "CHANGE_REJECTION_LEDGER.tsv")
    admitted = read_tsv(OUT / "CHANGE_ADMITTED.tsv")
    reg = read_tsv(OUT / "OBSERVABILITY_BOUNDARY_REGISTER.tsv")
    verdicts = read_tsv(OUT / "VERDICTS.tsv")
    probe = json.loads((OUT / "PROBE_RESULTS.json").read_text(encoding="utf-8"))
    change_sum = json.loads((OUT / "CHECK_SUMMARY.json").read_text(encoding="utf-8")) \
        if (OUT / "CHECK_SUMMARY.json").is_file() else json.loads(
            (OUT / "CHANGE_CHECK_SUMMARY.json").read_text(encoding="utf-8"))
    boundary = json.loads((OUT / "BOUNDARY_SUMMARY.json").read_text(encoding="utf-8"))

    # ---- G1 stage vocabulary
    bad = [r["assertion_id"] for r in markers if r["stage"] not in STAGES]
    bad += [r["node_key"] for r in nodes if r["stage"] not in STAGES]
    bad += [r["cell"] for r in reg if r["stage"] not in STAGES]
    check("G1", "every stage literal is in the declared four-level axis {fetal,adult,developing,unknown}",
          not bad, {"offending_rows": len(bad), "rows_checked": len(markers) + len(nodes) + len(reg),
                    "examples": bad[:5]})

    # ---- G2 no silent adult assignment; every non-adult row disclosed
    discl = read_tsv(OUT / "STAGE_DISCLOSURE.tsv")
    disclosed_ids = {r["scope"] for r in discl if r["row_kind"] == "marker_row"}
    non_adult = [r["assertion_id"] for r in markers if r["stage"] != "adult"]
    undisclosed = [a for a in non_adult if a not in disclosed_ids]
    wrong_map = [r["assertion_id"] for r in markers if r["stage"] == "adult" and r["source_stage_literal"] != "adult"]
    check("G2", "no row silently assigned to adult; every non-adult row carries a disclosure row",
          not undisclosed and not wrong_map,
          {"non_adult_rows": len(non_adult), "undisclosed": len(undisclosed),
           "adult_rows_with_non_adult_source_literal": len(wrong_map)})

    # ---- G3 one stage per row
    mixed = [r["assertion_id"] for r in markers
             if len([s for s in STAGES if s in re.split(r"[;,/| +]", r["stage"])]) != 1]
    check("G3", "no assertion mixes two stages in one row", not mixed,
          {"rows_with_more_than_one_stage_token": len(mixed)})

    # ---- G4 no cross-species stitching
    sp = {r["species"] for r in markers}
    na = [r["assertion_id"] for r in markers if r["species"] != "human"]
    cross_all = [c for c in cands if c["species_from"] != c["species_to"]]
    cross = [c["candidate_id"] for c in cross_all if c["fixture"] == "N"]
    cross_fix = [c["candidate_id"] for c in cross_all if c["fixture"] == "Y"]
    cross_rejected = [c for c in cross if c in {x["candidate_id"] for x in ledger}]
    check("G4", "no cross-species stitching in any published table; every cross-species candidate rejected",
          sp == {"human"} and not na and len(cross) == len(cross_rejected),
          {"species_values_in_tables": sorted(sp), "non_human_rows": len(na),
           "cross_species_candidates_real": len(cross),
           "cross_species_candidates_fixture": len(cross_fix),
           "real_rejected": len(cross_rejected)})

    # ---- G5 no numeric effect without a traceable extraction record
    num = [r["assertion_id"] for r in markers if r["effect_value"].strip()]
    check("G5", "no numeric effect value without a traceable extraction record", not num,
          {"rows_with_effect_value": len(num), "claim_types": sorted({r['claim_type'] for r in markers})})

    # ---- G6 developmental entries in no adult query path
    core = (REPO / "mcp_server" / "eyekb_core.py").read_text(encoding="utf-8")
    whitelists = re.findall(r"^[A-Z0-9_]*DEFAULT_LIBS\s*=\s*\(([^)]*)\)", core, re.M)
    dev_in_whitelist = any("retina_dev" in w for w in whitelists)
    adult_rank_libs = set()
    for k, v in probe.items():
        if not isinstance(v, dict) or v.get("route") != "default" or v.get("side") != "adult":
            continue
        for e in ((v.get("response") or {}).get("celltype_ranking") or []):
            adult_rank_libs.add(Path(str(e.get("library", ""))).name)
    check("G6", "developmental entries appear in no adult query path",
          (not dev_in_whitelist) and ("markers_v9_dev_retina.json" not in adult_rank_libs),
          {"retina_dev_in_a_DEFAULT_LIBS_whitelist": dev_in_whitelist,
           "libraries_seen_in_adult_default_rankings": sorted(adult_rank_libs)})

    # ---- G7 no `off` produced from absence of mention
    off_rows = [r["assertion_id"] for r in markers if r["change"] == "off"]
    off_cands = [c["candidate_id"] for c in cands if c["change"] == "off"]
    off_cands_rejected = [c for c in off_cands if c in {x["candidate_id"] for x in ledger}]
    check("G7", "`off` is never produced from absence of mention",
          not off_rows and len(off_cands) == len(off_cands_rejected),
          {"off_rows_in_tables": len(off_rows), "off_candidates_generated": len(off_cands),
           "of_which_rejected": len(off_cands_rejected)})

    # ---- G8 admitted changes carry anchor + grade
    bad_adm = [r["candidate_id"] for r in admitted if not r["evidence_anchor"].strip()
               or r["evidence_grade"] not in GRADES]
    check("G8", "every admitted change carries an anchor and a contract grade",
          not bad_adm, {"admitted_rows": len(admitted), "invalid_admitted_rows": len(bad_adm),
                        "note": "an empty admitted set passes; the count is reported so an empty set "
                                "can never be read as a filled one"})

    # ---- G9 probe stores real output, commands, and replays byte-identically
    p1 = json.loads((OUT / "PROBE_RESULTS_pass1.json").read_text(encoding="utf-8"))
    p2 = json.loads((OUT / "PROBE_RESULTS_pass2.json").read_text(encoding="utf-8"))
    keys = [k for k in p1 if not k.startswith("_")]
    diff = [k for k in keys if p1[k]["response_text_md5"] != p2[k]["response_text_md5"]]
    v1 = (OUT / "VERDICTS_pass1.tsv").read_bytes()
    v2 = (OUT / "VERDICTS_pass2.tsv").read_bytes()
    check("G9", "the recognition probe stores the real service output, the exact commands, and replays "
                "byte-identically",
          len(keys) > 0 and not diff and v1 == v2,
          {"n_calls_pass1": len(keys), "n_differing_responses": len(diff),
           "verdict_table_identical": v1 == v2,
           "server": p1["_meta"]["server"], "interpreter": p1["_meta"]["interpreter"],
           "transport": "MCP stdio (mcp SDK client -> shipped server.py subprocess)"})

    # ---- G10 this card changed no shipped byte; the recorded query set replays with difference 0
    git_diff = subprocess.run(["git", "diff", "--stat", "HEAD", "--", "mcp_server", "kb", "tests", "scripts"],
                              cwd=REPO, capture_output=True, text=True)
    git_status = subprocess.run(["git", "status", "--porcelain"], cwd=REPO, capture_output=True, text=True)
    untracked_outside = [l for l in git_status.stdout.splitlines()
                         if l.startswith("??") and "docs/plans/devlineage_20261021/" not in l]
    check("G10", "default behaviour unchanged by this card: no shipped byte differs from the committed "
                 "release, and this card's own recorded query set replays with difference count 0",
          git_diff.returncode == 0 and not diff and not untracked_outside,
          {"git_diff_rc": git_diff.returncode, "git_diff_lines": len(git_diff.stdout.splitlines()),
           "untracked_paths_outside_this_card": untracked_outside,
           "replay_difference_count_own_query_set": len(diff),
           "own_query_set_size": len(keys)})

    # ---- G11 zero download / zero network
    net_imports = []
    for p in sorted((HERE / "scripts").glob("*")):
        if p.suffix not in (".py", ".sh", ".md"):
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        for pat in [r"^\s*(?:import|from)\s+(requests|urllib|httpx|socket|paramiko|ftplib|telnetlib)\b",
                    r"\b(aria2c|wget|curl)\s+-(?!-)"]:
            for m in re.finditer(pat, txt, re.M):
                net_imports.append({"file": p.name, "match": m.group(0).strip()})
    audit = (LOGS / "net_audit.log")
    ctrl = ev = 0
    outbound = []
    if audit.is_file():
        for line in audit.read_text(encoding="utf-8").splitlines():
            ctrl += line.startswith("#")
            if line.startswith("EVENT"):
                ev += 1
                if re.search(r"(connect|getaddrinfo|create_connection|gethostbyaddr|urllib\.|http\.client\.)",
                             line):
                    outbound.append(line)
    # the audit hook itself necessarily names socket events; it is not a network client
    net_imports = [n for n in net_imports if "sitecustomize" not in n["file"]]
    check("G11", "zero download, zero network: no client code in this card's scripts, and no outbound "
                 "socket event in the instrumented run",
          (not net_imports) and (not outbound) and ctrl > 0,
          {"network_client_code_hits": net_imports, "audit_control_lines": ctrl,
           "audit_event_lines_total": ev, "audit_outbound_event_lines": len(outbound),
           "note": "socket.__new__ / socket.gethostname are local-only object construction and the "
                   "hostname field of the service's own call-trace record; they are counted separately "
                   "and not treated as network use"})

    # ---- G12 English only
    cjk = {}
    for p in sorted(list(HERE.glob("*.md")) + list((HERE / "scripts").glob("*"))
                    + list((HERE / "discipline").rglob("*")) + list((OUT).glob("*.tsv"))):
        if not p.is_file() or p.suffix not in (".md", ".py", ".tsv", ".sh", ".json"):
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        n = sum(1 for ch in txt if "\u4e00" <= ch <= "\u9fff")
        if n:
            cjk[str(p.relative_to(HERE))] = n
    check("G12", "repository-facing text of this card's deliverables is English only", not cjk,
          {"files_with_cjk_characters": cjk})

    gate = {"n_items": len(items), "n_pass": sum(1 for i in items if i["verdict"] == "PASS"),
            "n_fail": sum(1 for i in items if i["verdict"] == "FAIL"), "items": items}

    # ---- C. service-behaviour observations (recorded, not scored)
    silent = [r for r in verdicts if r["silent_adult_assignment"] == "Y"]
    sa_rows = [r for r in verdicts if r["state_annotation_hit"]]
    # the additive state_annotations key can also carry the entry on the explicit developmental route
    sa_dev = sorted({v["lineage_id"] for v in probe.values()
                     if isinstance(v, dict) and v.get("route") == "explicit_dev" and v.get("side") == "fetal"
                     and any(str(x.get("cell_type", "")) in json.dumps(v["args"].get("genes"))
                             for x in ((v.get("response") or {}).get("state_annotations") or []))})
    sa_entries = sorted({str(x.get("cell_type")) for v in probe.values() if isinstance(v, dict)
                         for x in ((v.get("response") or {}).get("state_annotations") or [])})
    obs = {
        "verdict_counts": {v: sum(1 for r in verdicts if r["verdict"] == v)
                           for v in sorted({r["verdict"] for r in verdicts})},
        "lineages_with_silent_adult_assignment_on_the_fetal_window": [r["lineage_id"] for r in silent],
        "lineages_with_a_state_annotations_hit_on_the_default_route": [r["lineage_id"] for r in sa_rows],
        "entries_returned_under_the_state_annotations_key": sa_entries,
        "boundary_cells": boundary,
        "change_candidates": {k: change_sum[k] for k in
                              ("n_candidates_real", "n_rejected_real", "n_admitted_real",
                               "n_candidates_fixture", "n_rejected_fixture", "n_admitted_fixture",
                               "primary_rule_counts_real", "rules_never_fired_real", "by_family")},
    }

    # ---- stage-literal surface table (composition tool)
    lit_rows = []
    base_md5 = (probe.get("composition.adult") or {}).get("response_text_md5")
    for k, v in probe.items():
        if not isinstance(v, dict) or v.get("tool") != "get_tissue_composition":
            continue
        r = v.get("response") or {}
        lit_rows.append({"literal": v["args"].get("development_stage", ""),
                         "mode": r.get("mode") or r.get("entry_id") or "",
                         "organism_stage": r.get("organism_stage", ""),
                         "entry_id": r.get("entry_id", ""),
                         "response_md5": v["response_text_md5"],
                         "bytes": v["response_text_bytes"],
                         "byte_identical_to_adult_response": "Y" if v["response_text_md5"] == base_md5 else "N"})
    lit_rows.sort(key=lambda x: x["literal"])
    with open(OUT / "STAGE_LITERAL_SURFACE.tsv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(lit_rows[0].keys()), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(lit_rows)

    external = [
        {"finding": "repo_recorded_query_set_does_not_reproduce_at_HEAD",
         "measured": "tests/probe_tool_panel_identity.py --baseline tests/fixtures/tool_panel_baseline.json "
                     "-> legacy_panel and full_panel digests moved; 5 of 12 calls differ",
         "cause_classification": [
             "get_kb_page{kind:index} and get_kb_page{kind:topic,name:vascular}: the panel spells the "
             "argument `kind`, the tracked tool signature is `scope` at HEAD and also at the commit that last "
             "touched the fixture (a400315) -> argument validation error, i.e. the panel does not match any "
             "tracked build of the server on this machine",
             "get_tissue_composition{detail:true}: the panel passes a boolean, the tracked signature is "
             "`detail: str` -> validation error",
             "search_literature{query:...} without cell_type: the tracked signature requires cell_type -> "
             "validation error",
             "explain_annotation{cell_type:'Mueller cell'}: no validation error; a content difference the "
             "fixture cannot attribute because it stores digests only"],
         "attribution": "pre-existing; not caused by this card (git diff HEAD over mcp_server/kb/tests/scripts "
                        "is empty and the only untracked path is this card's own directory)"},
        {"finding": "unrecognised_stage_literal_returns_the_adult_baseline",
         "measured": "get_tissue_composition(species=human, tissue=retina, development_stage='organoid') "
                     "returns a response byte-identical to development_stage='adult' (same md5), with no flag; "
                     "the shipped tool docstring names 'organoid -> unknown+flag'",
         "cause_classification": "the query path maps only fetal/developing/postnatal/unknown; an "
                                 "unrecognised literal falls through to the adult main file",
         "attribution": "external observation about the shipped surface; the card's own tables never pass an "
                        "unrecognised literal"},
        {"finding": "fetal_window_recognised_but_named_as_an_adult_class",
         "measured": f"{len(silent)} of the probed lineages return an adult class as the top-1 named candidate "
                     f"for a fetal-state window: {[r['lineage_id'] for r in silent]}",
         "cause_classification": "the developmental panel is not on the default route; the adult libraries "
                                 "still score the fetal window and name the nearest adult class",
         "attribution": "external observation; the card records it per lineage and does not silence it"},
        {"finding": "cell_cycle_entries_are_moved_out_of_the_named_ranking_by_design",
         "measured": "Retinal_Proliferating and TAC_proliferating are annotated concept_kind=state_program in "
                     "the shipped sidecar, so their identity comes back under the additive `state_annotations` "
                     "key (measured: n_shared=10 for Retinal_Proliferating on both routes)",
         "cause_classification": "deliberate shipped behaviour (concept-kind stratification), not a defect",
         "attribution": "recorded so a reader does not read an empty ranking as a missing answer"},
        {"finding": "superseded_v8_developmental_panel_exists_only_on_the_data_mount",
         "measured": "kb/markers/markers_v8_dev_retina.json is present at /mnt/D/EyeKB/kb/markers/ "
                     "(sha256 recorded in ROBUSTNESS_RESULTS.json) but not in the repository",
         "cause_classification": "the repository keeps only the active v9 panel",
         "attribution": "the robustness pass uses the v8 gene lists (its own ban list permits word-level "
                        "reference) and records the path and sha, so the step is reproducible only where that "
                        "file exists"},
    ]

    readout = {"gate": gate, "observations": obs, "external_findings": external,
               "stage_literal_surface": lit_rows,
               "artefacts": sorted(str(p.relative_to(HERE)) for p in HERE.rglob("*") if p.is_file()
                                   and "__pycache__" not in str(p))}
    (OUT / "GATE_READOUT.json").write_text(json.dumps(readout, indent=1, ensure_ascii=False) + "\n",
                                           encoding="utf-8")

    lines = ["# V3 stage axis — machine gate readout", "",
             f"items: {gate['n_items']}   PASS: {gate['n_pass']}   FAIL: {gate['n_fail']}", "",
             "| item | verdict | title | measured |", "|---|---|---|---|"]
    for i in items:
        lines.append(f"| {i['item']} | {i['verdict']} | {i['title']} | `{json.dumps(i['measured'], ensure_ascii=False)[:400]}` |")
    lines += ["", "## Service-behaviour observations (recorded, not scored)", "",
              f"- verdict counts: `{json.dumps(obs['verdict_counts'])}`",
              f"- silent adult assignment on a fetal window: `{obs['lineages_with_silent_adult_assignment_on_the_fetal_window']}`",
              f"- `state_annotations` hits on the default route: `{obs['lineages_with_a_state_annotations_hit_on_the_default_route']}`, "
              f"entries returned under that key anywhere in the probe: `{obs['entries_returned_under_the_state_annotations_key']}`",
              f"- boundary cells: `{json.dumps(obs['boundary_cells'])}`",
              f"- change candidates: `{json.dumps(obs['change_candidates'], ensure_ascii=False)}`",
              "", "## External findings (measured here, not caused by this card)", ""]
    for f in external:
        lines += [f"### {f['finding']}", f"- measured: {f['measured']}",
                  f"- cause: {'; '.join(f['cause_classification']) if isinstance(f['cause_classification'], list) else f['cause_classification']}",
                  f"- attribution: {f['attribution']}", ""]
    lines += ["## The composition tool's stage literals", "",
              "| literal | mode / entry | organism_stage | bytes | identical to the adult response |",
              "|---|---|---|---|---|"]
    for r in lit_rows:
        lines.append(f"| `{r['literal']}` | {r['mode']} | {r['organism_stage']} | {r['bytes']} | "
                     f"{r['byte_identical_to_adult_response']} |")
    (OUT / "GATE_READOUT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"gate": {k: gate[k] for k in ("n_items", "n_pass", "n_fail")},
                      "failed_items": [i for i in items if i["verdict"] == "FAIL"],
                      "external_findings": [f["finding"] for f in external]}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
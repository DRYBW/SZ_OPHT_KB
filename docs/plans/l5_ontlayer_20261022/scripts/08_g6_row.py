#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append this card's change-control row to the machine-readable G6 instance.

    python3 docs/plans/l5_ontlayer_20261022/scripts/08_g6_row.py

The row is the same shape as every other row in that file: 12 content cells (Q1-Q5 / M1-M3 / E1-E4),
3 identity cells, and an evidence cell next to each content cell. Every evidence cell carries a path
that resolves (repo-relative, or the declared local evidence root) and a concrete reading (a sha256,
an rc, or a command), because the gate that reads this file requires exactly that.

Exit codes: 0 = the row is present (added or already there); 1 = the instance file is missing a
required column (nothing written).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = next(d for d in [HERE] + list(HERE.parents)
            if (d / "kb").is_dir() and (d / "mcp_server").is_dir())
INST = ROOT / "docs/CHANGE_CONTROL_G6_INSTANCE.tsv"
CHANGE_ID = "CHG-20261022-ONT-LAYER"
EVID = "docs/plans/l5_ontlayer_20261022"

ROW = {
    "change_id": CHANGE_ID,
    "owner": ("Maintainer (repository delivery surface; card t_ad7463d9, the Cell Ontology "
              "explanation layer)"),
    "entry_point": "python3 tests/gate_ontology_layer.py --service-python <interpreter>",
    "Q1": ("First-cause layer = L1 (the service loading surface) for the new capability, and L6 (the "
           "delivery surface) for the two gates and the records. The gap being closed is that the "
           "ontology work existed as an analysis asset but was not reachable through the shipped "
           "service: the service matched labels to a curated sidecar and nothing else. This change "
           "makes the ontology navigable read-only, and freezes the pre-change baseline before "
           "touching anything."),
    "Q1_evidence": (f"{EVID}/out/BASELINE_FREEZE.json (pointer, sha256 0c915fc9e1ff3c4e… for the frozen "
                    f"file) and {EVID}/REPORT.md:1"),
    "Q2": ("Layer to fix = the same two layers (L1 for the capability, L6 for the gates and records; "
           "no upstream patch, no transitional artefact). Files added: "
           "mcp_server/ontology_layer.py; kb/ontology/ (snapshot + manifest + registry); "
           "tests/gate_ontology_layer.py; tests/gate_ontlayer_portability.py; "
           "docs/ONTOLOGY_LAYER_CONTRACT_v1.md. Files changed: mcp_server/server.py (conditional "
           "tool registration + the identity layers), scripts/release_identity.py (four layers + the "
           "release manifest), tests/run_gates.sh (G7/G8 in the chain), README.md, "
           "docs/VERIFY_CONTRACT.md, docs/VERSION_NOTES.md, and the two registration surfaces."),
    "Q2_evidence": f"{EVID}/REPORT.md:1 the change list with its measurements",
    "Q3": ("Blast radius per reading, with the rollback/negative term stated rather than omitted: "
           "(1) every answer of every existing tool is unchanged - 54 of the 55 calls of the recorded "
           "request set are byte-identical, and the tool list is unchanged; (2) exactly one call "
           "moves: get_release_identity, the explicit identity interface, by design and stated; "
           "(3) the legacy panel digests do not move (e8e6c263… / 3f1f52cb…); (4) no accuracy, "
           "coverage or recognition gain is claimed anywhere - ontology agreement rising is not "
           "recognition rising, and the card is a negative-direction report on that point; "
           "(5) rollback is one switch: unsetting EYEKB_ONT_LAYER returns the pre-change surface. "
           "No default-ON behaviour changed, so nothing became worse by default either."),
    "Q3_evidence": (f"{EVID}/out/REPLAY_COMPARISON.json:1 (55 calls, 1 moved) and "
                    f"{EVID}/out/PANEL_SETTLEMENT.json:1"),
    "Q4": ("Criteria frozen before the run: the baseline was frozen first, in a checkout of the "
           "baseline revision, and the acceptance assertions were stated before the post-change "
           "measurements - legacy and full panel digests unchanged; every call of the recorded "
           "request set byte-identical except the identity call; 0 refused calls; every manifest "
           "anchor RESOLVED; the five-bucket recomputation over the frozen 721-pair list equal to "
           "the earlier reading; a missing, altered or unlisted asset reported as a failure rather "
           "than as an environment error. The granularity rule (a blanket ancestor cannot carry an "
           "answer, threshold 200) was declared in the registry before any comparison was run."),
    "Q4_evidence": (f"{EVID}/out/BASELINE_FREEZE_16c6b28aab8f.json:1 and "
                    f"{EVID}/out/BUCKET_SUMMARY.json:1 (cross_check_identical=true); registry payload "
                    f"sha256 411f3f3cede72843a9862c4e72dcca4545b2d34acdf087984952bbadc2b1b182"),
    "Q5": ("Escape door: EYEKB_ONT_LAYER. Unset or empty = the four ontology tools are not registered, "
           "the layer is not even imported, and the surface is byte-identical to the release before "
           "the change (measured over the recorded request set: 54/54 other calls identical, tool "
           "list unchanged). The registry ships an EMPTY whitelist, so there is no default entry "
           "point to the capability in any state, and the per-tool route registers exactly the tools "
           "named. The legacy panel switch behaviour used by the rest of the chain is untouched."),
    "Q5_evidence": (f"{EVID}/out/PRE_TOOLS.txt and {EVID}/out/POST_TOOLS.txt (identical, seven "
                    f"tools); {EVID}/out/PRE_REPLAY_HASHES.tsv vs POST_REPLAY_HASHES.tsv"),
    "M1": ("Version artefact: no file was edited without its previous state remaining retrievable. "
           "The pre-change bytes of every changed file are the committed revision "
           "16c6b28aab8ffda11a4a89d21075ae217e740771 (git show <rev>:<path>), the pre-change fixture "
           "of the panel is read out of git as 435bb92^:tests/fixtures/tool_panel_baseline.json, and "
           "the pre-change identity record is preserved inside the frozen baseline."),
    "M1_evidence": (f"git show 16c6b28aab8ffda11a4a89d21075ae217e740771:mcp_server/server.py "
                    f"| sha256sum; {EVID}/out/BASELINE_FREEZE_16c6b28aab8f.json:1 "
                    f"(release_identity.release_id = 3c17853873ca)"),
    "M2": ("Impact list per file: added = mcp_server/ontology_layer.py (new module), "
           "kb/ontology/cl/releases/2026-06-08/cl-base.obo (new asset), "
           "kb/ontology/ONTOLOGY_SNAPSHOT_MANIFEST_v1.json, kb/ontology/ONT_LAYER_REGISTRY_v1.json, "
           "kb/ontology/scripts/build_ont_manifest.py, tests/gate_ontology_layer.py, "
           "tests/gate_ontlayer_portability.py, docs/ONTOLOGY_LAYER_CONTRACT_v1.md, "
           "docs/RELEASE_MANIFEST_v1.json, this card's directory; changed = mcp_server/server.py, "
           "scripts/release_identity.py, tests/run_gates.sh, README.md, docs/VERIFY_CONTRACT.md, "
           "docs/VERSION_NOTES.md, docs/W3_PIPELINE_REGISTRY.tsv, docs/GATE_INVENTORY_G5G6.tsv, "
           "docs/RELEASE_IDENTITY.json. Do NOT move: every other service answer (measured), the "
           "legacy panel digests, the corpus pointer, the class dictionary, the evaluation volumes."),
    "M2_evidence": f"{EVID}/REPORT.md:1 and the ledger rows re-taken by {EVID}/scripts/07_registry_rows.py",
    "M3": ("Regression gate, runnable command and concrete threshold: "
           "`bash tests/run_gates.sh` must report G3, G4, G5, G6, G7 and G8 and the chain summary "
           "with gates=6 failed=0 (CHAIN PASS); G3 needs the corpus named by §G2 and the G1-locked "
           "interpreter (EYEKB_G3_PY). The two new gates are registered in "
           "docs/GATE_INVENTORY_G5G6.tsv and report should-run / did-run / pass / fail / not-run: G7 "
           "9/9 and G8 6/6 here, each ending in a single three-state verdict. No default-ON behaviour "
           "changed, so no existing gate gains a precondition."),
    "M3_evidence": (f"{EVID}/logs/ G7.json and G8.json readouts; "
                    f"{EVID}/REPORT.md:1 the gate table with the five counts"),
    "E1": ("sha256 evidence taken fresh in this commit, none quoted from an earlier report: run "
           "`sha256sum` over the added and changed delivery files. The current values are in the "
           "ledger rows re-taken by scripts/07_registry_rows.py, and the ontology snapshot reads "
           "c6274fb65cdf740b983a06b74cb678814249d7f8e580c2ec9de54bf204a2b1c7 (3,757,082 bytes)."),
    "E1_evidence": (f"{EVID}/out/BASELINE_FREEZE_16c6b28aab8f.json:1 (per-file sha256 for the whole "
                    f"service surface); kb/ontology/ONTOLOGY_SNAPSHOT_MANIFEST_v1.json:1"),
    "E2": ("Rollback identity, two independent paths: path 1 - the pre-change state is the committed "
           "tree at 16c6b28aab8f, and the recorded request set replayed in a checkout of it "
           "reproduces 55/55 of the same-path PRE digests; path 2 - with the change in place, "
           "unsetting EYEKB_ONT_LAYER leaves all 54 non-identity calls bit-identical and the tool "
           "list unchanged, so the switch is a complete rollback of the observable surface. "
           "Command: python3 docs/plans/l5_ontlayer_20261022/scripts/03_replay_request_set.py "
           "--compare PRE.json POST.json -> differing=1, tools unchanged."),
    "E2_evidence": (f"{EVID}/out/PRE_REPLAY_HASHES.tsv and {EVID}/out/POST_REPLAY_HASHES.tsv; "
                    f"{EVID}/out/BASELINE_FREEZE_16c6b28aab8f.json:1"),
    "E3": ("Differential reading, negative column included, no gains-only reporting: the five-bucket "
           "recomputation over the frozen 721-cluster population (1,495,330 cells) is same_term 212 / "
           "ours_broader 150 / ours_narrower 15 / confirmed_incompatible 0 / not_supported_by_is_a "
           "344, identical to the earlier reading bucket for bucket; the negative direction is "
           "stated - confirmed_incompatible is 0 because no explicit incompatibility evidence was "
           "supplied, the fine-resolution bucket earns nothing, and 0 of the coarse rows reach only a "
           "blanket ancestor while the rule is exercised by the gate's own battery. This change "
           "produces no accuracy, coverage or recognition gain and claims none: it corrects how a "
           "comparison is worded and how far an answer may be used."),
    "E3_evidence": f"{EVID}/out/BUCKET_SUMMARY.json:1 and {EVID}/out/TABLE_2_GRANULARITY.tsv:1",
    "E4": ("Registry entry: docs/W3_PIPELINE_REGISTRY.tsv rows L6-06 (README), L6-01 "
           "(docs/VERIFY_CONTRACT.md) and L6-07 (docs/VERSION_NOTES.md) re-taken from live bytes in "
           "this commit, plus new rows for the added artefacts (mcp_server/ontology_layer.py, the "
           "ontology snapshot, the registration record, the two gates, the contract document and this "
           "card's report); docs/GATE_INVENTORY_G5G6.tsv gains G7 and G8 and re-takes the G2 row for "
           "docs/VERIFY_CONTRACT.md; docs/RELEASE_IDENTITY.json and docs/RELEASE_MANIFEST_v1.json are "
           "re-taken in the same commit, and the four identity layers are verified by "
           "scripts/release_identity.py --check."),
    "E4_evidence": (f"{EVID}/scripts/07_registry_rows.py:1 the re-take script; "
                    f"docs/RELEASE_IDENTITY.json:1"),
}


def main() -> int:
    lines = INST.read_text(encoding="utf-8").splitlines()
    hdr_i = next(i for i, ln in enumerate(lines) if ln and not ln.startswith("#"))
    hdr = lines[hdr_i].split("\t")
    missing = [c for c in ROW if c not in hdr]
    if missing:
        print(f"FAIL: the instance file has no such column(s): {missing}")
        return 1
    rows = [ln.split("\t") for ln in lines[hdr_i + 1:] if ln.strip()]
    if any(r and r[0] == CHANGE_ID for r in rows):
        print(f"row already present: {CHANGE_ID}")
        return 0
    rows.append([ROW.get(c, "") for c in hdr])
    INST.write_text("\n".join(lines[:hdr_i + 1] + ["\t".join(r) for r in rows]) + "\n",
                    encoding="utf-8")
    print(f"appended {CHANGE_ID}: {len(hdr)} cells, "
          f"{sum(1 for c in hdr if c.endswith('_evidence'))} evidence cells")
    return 0


if __name__ == "__main__":
    sys.exit(main())
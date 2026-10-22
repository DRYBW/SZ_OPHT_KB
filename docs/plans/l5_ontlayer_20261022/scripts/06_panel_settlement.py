#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Settle the 5-of-12 panel mismatch explicitly, with both readings kept.

The developmental-lineage card reported that the repository's recorded tool panel did not reproduce
at HEAD (5 of 12 calls differed) and deliberately did not repair it, because the fixture belongs to
another card's scope. This script settles the question for the baseline of this card:

    python3 docs/plans/l5_ontlayer_20261022/scripts/06_panel_settlement.py

It writes out/PANEL_SETTLEMENT.json with
  * the PRE-IMAGE: the fixture as it stood before it was re-recorded (`git show <rev>:<path>`), its
    sha256 and the two panel digests it recorded;
  * the CURRENT fixture at HEAD, its sha256 and its recorded digests;
  * the LIVE reading of the probe in this checkout, run again here rather than quoted;
  * the attribution already established by the card that re-recorded the fixture, and the fact that
    this card did not touch it.

Nothing is overwritten: the pre-image is read out of git, and the fixture is left exactly as the
card that owns it left it.

Exit codes: 0 = settled and written; 3 = git could not supply the pre-image (nothing is claimed).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = next(d for d in [HERE] + list(HERE.parents)
            if (d / "kb").is_dir() and (d / "mcp_server").is_dir())
OUT = ROOT / "docs/plans/l5_ontlayer_20261022/out"
FIXTURE = "tests/fixtures/tool_panel_baseline.json"
# The commit that re-recorded the fixture (the card that owns it), and the commit before it.
RERECORD_COMMIT = "435bb92"


def git(*args) -> str:
    p = subprocess.run(["git", "-C", str(ROOT)] + list(args), capture_output=True, text=True,
                       timeout=300)
    return p.stdout if p.returncode == 0 else ""


def digests_of(text: str) -> dict:
    try:
        d = json.loads(text)
    except Exception:
        return {"_unreadable": True}
    return {"legacy_panel": d.get("legacy_panel"), "full_panel": d.get("full_panel"),
            "n_calls": d.get("n_calls"), "refused_calls": d.get("refused_calls"),
            "provenance": d.get("provenance")}


def main() -> int:
    pre_text = git("show", f"{RERECORD_COMMIT}^:{FIXTURE}")
    if not pre_text:
        print("CANNOT SETTLE: git could not supply the pre-image of the fixture.")
        return 3
    cur_path = ROOT / FIXTURE
    cur_text = cur_path.read_text(encoding="utf-8")
    py = os.environ.get("EYEKB_G7_PY") or os.environ.get("EYEKB_G3_PY") or sys.executable
    probe = subprocess.run([py, str(ROOT / "tests/probe_tool_panel_identity.py"),
                            "--baseline", str(cur_path)], cwd=str(ROOT), capture_output=True,
                           text=True, timeout=900,
                           env={**{k: v for k, v in os.environ.items() if k != "PYTHONPATH"},
                                "EYEKB_ONT_LAYER": ""})
    live = {}
    for line in probe.stdout.splitlines():
        s = line.strip()
        if s.startswith('"legacy_panel"') or s.startswith('"full_panel"'):
            k, _, v = s.partition(":")
            live[k.strip('"')] = v.strip().strip('",')

    out = {
        "schema": "eyekb-panel-settlement/1.0",
        "card": "L5 baseline freeze + read-only Cell Ontology explanation layer",
        "question": "the recorded tool panel does not reproduce at HEAD (5 of 12 calls differed)",
        "verdict": "STALE FIXTURE - already settled, by another card, before this baseline was frozen",
        "pre_image": {
            "source": f"git show {RERECORD_COMMIT}^:{FIXTURE}",
            "sha256": hashlib.sha256(pre_text.encode()).hexdigest(),
            "recorded": digests_of(pre_text),
        },
        "current": {
            "source": FIXTURE,
            "sha256": hashlib.sha256(cur_text.encode()).hexdigest(),
            "recorded": digests_of(cur_text),
        },
        "live_reading_here": {
            "probe": "tests/probe_tool_panel_identity.py --baseline tests/fixtures/tool_panel_baseline.json",
            "interpreter": py,
            "digests": live,
            "rc": probe.returncode,
            "verdict": ({0: "IDENTITY PASS: the fixture reproduces at this HEAD",
                        1: "STILL MOVED at this HEAD - read the probe output; do not cite a frozen "
                           "baseline",
                        3: "COULD NOT BE EVALUATED with this interpreter (the MCP SDK is not "
                           "importable): not a result about the service, and not a pass. Re-run "
                           "with EYEKB_G7_PY pointing at an interpreter that has it."}
                       .get(probe.returncode,
                            f"UNEXPECTED exit {probe.returncode} - read the probe output")),
        },
        "attribution": {
            "settled_by": f"the card that re-recorded the fixture in commit {RERECORD_COMMIT}",
            "what_moved_and_why": [
                "four calls were refused on arguments the tool never accepted (the fixture spelled "
                "get_kb_page's argument `kind` where the documented signature is `scope`, passed a "
                "boolean for `detail` where the signature is a string, and omitted the required "
                "`cell_type`); a refusal is produced by the argument-validation layer, embeds the "
                "validator's own version string, and therefore cannot be an anchor at all",
                "one call had genuinely moved before this card started: explain_annotation for the "
                "Cell Ontology label resolved to a different answer than the one recorded",
            ],
            "re_recorded_with": "the documented signatures, no refused calls, plus an interpreter "
                                "provenance block",
        },
        "ownership": {
            "fixture_owner": "the shipped-surface card that re-recorded it; the file is registered "
                             "as its own delivery record",
            "what_this_card_did": "read the pre-image out of git, re-ran the probe, and recorded "
                                  "both readings. The fixture was NOT overwritten, and neither "
                                  "version was edited.",
        },
        "rule": "a baseline is not declared frozen on a panel that does not reproduce: the "
                "mismatch is settled first, and the settlement names the owner of the fixture.",
    }
    target = OUT / "PANEL_SETTLEMENT.json"
    target.write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                      encoding="utf-8")
    sha = hashlib.sha256(target.read_bytes()).hexdigest()
    (OUT / "PANEL_SETTLEMENT.sha256").write_text(f"{sha}  PANEL_SETTLEMENT.json\n", encoding="utf-8")
    print(json.dumps({"verdict": out["verdict"], "live": out["live_reading_here"]["verdict"],
                      "pre_image_recorded": out["pre_image"]["recorded"],
                      "current_recorded": out["current"]["recorded"],
                      "sha256": sha}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
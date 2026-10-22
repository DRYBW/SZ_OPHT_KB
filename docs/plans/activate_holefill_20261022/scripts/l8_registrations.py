#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""l8 -- land this card's registration restoration in the repository, with the registration surface
re-taken in the same commit.

Because card t_7509a1a2 has by now committed its own registration (`86d37a3`, which correctly echoes
the anchor line), the shared file is free and this card's restoration is the only remaining core change
in the working tree (`git diff HEAD -- mcp_server/eyekb_core.py` = the six restored lines). Landing it
means re-taking the rows and identity records the byte change invalidates:

  L1-11M  the delivery copy of the service core  -> sha/bytes/mtime + the activation/defect note
  docs/SWITCH_COVERAGE_REGISTRY.tsv              -> regenerated from source (a switch added by the
                                                    sibling card's commit left it drifted, which made
                                                    G10 R1 red at this card's first commit)
  docs/RELEASE_IDENTITY.json / docs/RELEASE_MANIFEST_v1.json
  docs/W3_MANIFEST.sha256                        -> re-frozen LAST, after the registry's final bytes

Writes out/REGISTRY_ROWS.json.
"""
import csv
import datetime
import hashlib
import json
import os
import subprocess
import sys

REPO = "/home/ubuntu/EYEKB_REPO"
REG = os.path.join(REPO, "docs", "W3_PIPELINE_REGISTRY.tsv")
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out"))

NOTE = (
    " | 2026-10-22 card t_be11fd4a (ACT-holefill): the working tree gains the restored `holefill_v12` "
    "registration line that commit 0312016 had dropped (see row L1-26 for the full record: the "
    "activation it was being measured for was ruled NO-GO on the pre-registered acceptance rule, the "
    "library stays REGISTERED_DEFAULT_OFF, and the restoration was proven neutral on the shipped "
    "default route -- 721/721 recorded cluster windows and 229/229 battery calls byte-identical, "
    "out/RESTORE.json). Re-taken from live bytes in the same commit as the change; the release "
    "identity and docs/W3_MANIFEST.sha256 are re-taken after it.")


def sha_live(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def stat_row(rel):
    p = os.path.join(REPO, rel)
    st = os.stat(p)
    return (hashlib.sha256(open(p, "rb").read()).hexdigest(), str(st.st_size),
            datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"))


def main():
    rows = list(csv.reader(open(REG, encoding="utf-8"), delimiter="\t"))
    hdr = rows[0]
    assert hdr[1] == "item_id" and hdr[10] == "sha256" and len(hdr) == 17, "registry schema moved"
    idx = {r[1]: i for i, r in enumerate(rows) if len(r) == 17 and r[1]}
    doc = {"probe": "l8_registrations.py", "registry": "docs/W3_PIPELINE_REGISTRY.tsv",
           "registry_sha256_before": hashlib.sha256(open(REG, "rb").read()).hexdigest(),
           "rows": {}}

    core_sha, core_b, core_m = stat_row("mcp_server/eyekb_core.py")
    i = idx["L1-11M"]
    doc["rows"]["L1-11M"] = {"before": {"sha256": rows[i][10], "bytes": rows[i][11]},
                             "after": {"sha256": core_sha, "bytes": core_b, "mtime": core_m}}
    rows[i][10], rows[i][11], rows[i][12] = core_sha, core_b, core_m
    if not rows[i][15].endswith(NOTE):
        rows[i][15] = rows[i][15] + NOTE
        doc["rows"]["L1-11M"]["note_appended"] = True

    body = "\n".join("\t".join(r) for r in rows) + "\n"
    assert body.count("\n") == len(rows), "row count changed while serialising"
    tmp = REG + ".tmp-activate"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(body)
    os.replace(tmp, REG)
    doc["registry_sha256_after"] = hashlib.sha256(open(REG, "rb").read()).hexdigest()
    doc["verdict"] = "PASS" if core_sha != doc["rows"]["L1-11M"]["before"]["sha256"] else "FAIL"
    os.makedirs(OUT, exist_ok=True)
    json.dump(doc, open(os.path.join(OUT, "REGISTRY_ROWS.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps(doc, ensure_ascii=False, indent=1)[:1200])
    # the switch registry is regenerated from source by the repository's own tool
    p = subprocess.run(["/usr/bin/python3", os.path.join(REPO, "scripts", "switch_coverage",
                                                        "gen_switch_registry.py")],
                       capture_output=True, text=True, cwd=REPO)
    print("gen_switch_registry rc=%d %s" % (p.returncode, (p.stdout or p.stderr).strip()[-200:]))
    return 0 if (doc["verdict"] == "PASS" and p.returncode == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
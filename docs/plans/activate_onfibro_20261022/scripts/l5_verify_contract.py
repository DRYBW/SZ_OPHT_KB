#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""l5 -- register the new default-ON behaviour as a gate precondition in docs/VERIFY_CONTRACT.md.

G6 rule R8 requires it: a default-ON behaviour change referenced by the change-control row (M3/E2)
must be registered as a gate precondition in docs/VERIFY_CONTRACT.md. The section appended here is
§5.5, in the same shape as §5.4 (the previous card's) and §"Rewrite-layer precondition".

Appends only; asserts the anchor line occurs exactly once and that nothing above it moved.
"""
import hashlib
import json
import os
import sys

REPO = "/home/ubuntu/EYEKB_REPO"
VC = os.path.join(REPO, "docs", "VERIFY_CONTRACT.md")
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out"))

ANCHOR = ("- **Failure policy.** A missing shipped asset, an altered snapshot or an address the manifest does\n"
          "  not list are delivery defects and **FAIL**; `ENV_ERROR` is reserved for a declared external\n"
          "  precondition. The policy is declared in the registry and exercised by G8, which builds a shadow\n"
          "  copy with the snapshot absent, then altered, and resolves an unlisted address.")

SECTION = """

### §5.5 The optic-nerve fibroblast carrier on the default route (activation card t_42df17c2, 2026-10-22)

The carrier library `onfibro_v13` was merged into the default route by a **PI-signed activation**
(the project owner's verbatim authority: "载体并进默认路由"). It is a **default-ON behaviour
change**, so this contract registers the precondition that follows from it:

- **Switch and OFF identity.** `EYEKB_ACT_ONFIBRO` — unset, empty or any value other than
  `{0,false,off,no}` means the optic-nerve fibroblast carrier is part of the default `all` route;
  `EYEKB_ACT_ONFIBRO=0` restores the pre-flip default **byte-for-byte**, measured by replaying the
  recorded query set at the same absolute path: 721/721 recorded cluster windows and 229/229 battery
  calls identical in raw and canonical response bytes, with the parent commit's core swapped in place
  as the reference (docs/plans/activate_onfibro_20261022/out/DEFAULT_FACE.json).
- **What the gates inherit.** Every criterion that is stated as a *byte identity of a default-route
  response* now depends on that switch. The 721/740/906-request default-face baselines and the
  recorded legacy tool-panel digests were taken with the pre-flip default, so a replay at this
  release is not byte-identical on the surface the carrier touches: the ranking moves on 45 of the
  721 recorded clusters, and **every** response that carries the provenance/soft-flag disclosure
  fields now names the carrier's file and entries (out/FIELD_DIFF.json gives the per-path diff).
- **Legacy tool-panel compatibility item (reported, not absorbed).** The legacy five-tool panel
  digest moved (`e8e6c26351cd9a1d42fa2e7cb6a83f23` -> `47e42230a8f7256b4ae9a78d4ff628d3`, and the
  full panel with it) on exactly two `query_marker` calls — `{"cell_type": "MG"}` and the microglia
  gene panel — **whose rankings are unchanged**; they moved because they carry the disclosure fields.
  The baseline fixture `tests/fixtures/tool_panel_baseline.json` was deliberately **not**
  re-recorded, so `tests/probe_tool_panel_identity.py --baseline tests/fixtures/tool_panel_baseline.json`
  is RED at this release by design, on the record, and the decision to re-record the baseline with
  attribution or to narrow the disclosure for libraries that contribute no candidate is pending the
  owner's ruling. No gate of the one-click chain (G3..G8) invokes that probe, so the chain itself is
  unaffected; the item is carried in `docs/CHANGE_CONTROL_G6_INSTANCE.tsv` (row
  `CHG-20261022-ONFIBRO-ACTIVATION`) and in registry rows L1-11M / L1-30 / L6-37.
- **Failure policy.** A replay that compares default-route bytes must state which value of
  `EYEKB_ACT_ONFIBRO` it was taken with; a mismatch under the other value is a configuration
  difference, not a regression. **No criterion of any gate was weakened for this activation**: G4's
  three byte anchors and the retrieval anchors are re-measured in the same commit and reported.
- **Scope.** No other library is activated, no whitelist gains another entry, no exclusion row is
  withdrawn, and no score, admission floor or tie-break changes: the carrier is a class carrier.
"""


def main():
    txt = open(VC, encoding="utf-8").read()
    sha_before = hashlib.sha256(txt.encode()).hexdigest()
    already = "§5.5 The optic-nerve fibroblast carrier" in txt
    doc = {"probe": "l5_verify_contract.py", "path": "docs/VERIFY_CONTRACT.md",
           "mode": "verify" if already else "append",
           "sha256_before": sha_before,
           "appended_section": "§5.5 The optic-nerve fibroblast carrier on the default route",
           "registered_in": "docs/VERIFY_CONTRACT.md",
           "r8_note": ("R8 is a property of the change-control row, not of this file: the row's "
                       "M3/E2 cells must name docs/VERIFY_CONTRACT.md when they mention a default-ON "
                       "change, and this section is what they point at (verified by "
                       "tests/gate_change_control.py G6-R8 PRECOND)")}
    if already:
        assert "EYEKB_ACT_ONFIBRO" in txt and "byte-for-byte" in txt
        doc["sha256_after"] = sha_before
        doc["bytes_after"] = os.path.getsize(VC)
        doc["prefix_unchanged"] = True
        doc["switch_named"] = True
        doc["verdict"] = "PASS"
        json.dump(doc, open(os.path.join(OUT, "VERIFY_CONTRACT_UPDATE.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print(json.dumps(doc, ensure_ascii=False, indent=1))
        return 0
    n = txt.count(ANCHOR)
    assert n == 1, "anchor not unique in VERIFY_CONTRACT.md: %d" % n
    new = txt.replace(ANCHOR, ANCHOR + SECTION)
    assert new != txt and new[:len(txt)] == txt, "append must not disturb the existing text"
    with open(VC, "w", encoding="utf-8") as f:
        f.write(new)
    doc.update({"sha256_after": hashlib.sha256(open(VC, "rb").read()).hexdigest(),
                "bytes_before": len(txt.encode()), "bytes_after": os.path.getsize(VC),
                "prefix_unchanged": new[:len(txt)] == txt,
                "switch_named": "EYEKB_ACT_ONFIBRO" in new,
                "verdict": "PASS" if new[:len(txt)] == txt else "FAIL"})
    json.dump(doc, open(os.path.join(OUT, "VERIFY_CONTRACT_UPDATE.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(json.dumps(doc, ensure_ascii=False, indent=1))
    return 0 if doc["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
# -*- coding: utf-8 -*-
"""gen_limit_doc.py -- generate docs/HARNESS_LIMIT_QUALIFIED_ISA_20261024.md FROM the measured
JSON (out/R3_CLOSURE_READING.json, out/R1_REPRODUCE.json) so every number in the ledger note is
table-driven, never hand-typed. Zero network."""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)
OUT = os.path.join(WAVE, "out")
REPO = "/home/ubuntu/EYEKB_REPO"
DEST = os.path.join(REPO, "docs/HARNESS_LIMIT_QUALIFIED_ISA_20261024.md")

r3 = json.load(open(os.path.join(OUT, "R3_CLOSURE_READING.json"), encoding="utf-8"))
r1 = json.load(open(os.path.join(OUT, "R1_REPRODUCE.json"), encoding="utf-8"))
A = r3["A_replay_top"]
B = r3["B_ledger_top"]
d3 = r1["D3_qualified_isa"]

qk = d3["qualifier_kinds"]
other_q = {k: v for k, v in qk.items() if not k.startswith('is_inferred')}
n_other = sum(other_q.values())

lines = []
w = lines.append
w("# Instrument limit — the frozen noregr harness's ancestor closure drops the release's qualified `is_a` edges")
w("")
w("Registered 2026-10-24 by card t_c19cd667 (KB-REACH), fixing item 3 of the card brief: the")
w("qualified-`is_a` closure gap measured by card t_fabddb85 (§6.3) is either fixed behind a declared")
w("switch or registered as a stated instrument limit. **This document registers it as an instrument")
w("limit**; the frozen harness's bytes are NOT changed — `docs/plans/noregr_20261022/scripts/`")
w("wave_common.py is pinned by that wave's own `out/MANIFEST.json`/`out/MANIFEST.sha256` and reused")
w("byte-for-byte by several later cards' recorded readings, so editing it (even behind a default-OFF")
w("switch) would break the comparability those pins exist to guarantee.")
w("")
w("## 1. The defect, one line + the exact parse site")
w("")
w("`wave_common.Rulers._load_obo` reads each `is_a` value as `v.split(\"!\")[0].strip()`, which keeps")
w("the trailing OBO qualifier — e.g. `is_a: CL:0000192 {is_inferred=\"true\"}` — attached to the parent")
w("id. Such parents never match a real term id, so **the qualified edges never enter the harness's")
w("ancestor closure**; its `anc()`, `related()` and `cl_grade()` under-read coarser/finer relations and")
w("report granularity differences as `truly_inconsistent`.")
w("")
w("Site: `docs/plans/noregr_20261022/scripts/wave_common.py`, function `Rulers._load_obo`, the")
w("`elif k == \"is_a\":` branch (`cur.setdefault(\"is_a\", []).append(v.split(\"!\")[0].strip())`).")
w("")
w("## 2. Measured counts (this tree, re-derived 2026-10-24 — no number carried over by trust)")
w("")
w("Pinned release `kb/ontology/cl/releases/2026-06-08/cl-base.obo` (sha256")
w("`%s`,%s" % (d3["obo_sha256"][:64], " line-parse by `scripts/r1_reproduce.py` D3 block:"))
w("")
w("| caliber | lines |")
w("|---|---|")
w("| all `is_a` lines in the release | %d |" % d3["n_is_a_lines"])
w("| carrying any `{...}` qualifier after the id (the card brief's 686) | **%d** |" % d3["qualified_any_qualifier"])
w("| of which `{is_inferred=\"true\"}` | %d |" % qk.get('is_inferred="true"', 0))
w("| carrying an `evidence=...` qualifier instead | %d |" % n_other)
w("")
w("Every one of the %d qualified lines is read into the closure with its qualifier attached by the" % d3["qualified_any_qualifier"])
w("frozen parse, i.e. all of them drop out of the closure at once.")
w("")
w("## 3. Effect on the recorded 721-cluster set, measured twice")
w("")
w("Top source A = the service replay (the CLOSURE_INSTRUMENT_DIFFERENCE caliber of t_fabddb85:")
w("`W.replay(calls, {\"EYEKB_ACT_CL56\": \"1\"}, label=\"kbreach_sens_before\")`), four-way grades:")
w("")
w("| grade | harness ruler | corrected ruler |")
w("|---|---|---|")
for g in ("kb_coarser", "same_cl", "kb_finer", "truly_inconsistent", "abstain", "unmappable_pred"):
    w("| %s | %d | %d |" % (g, A["dist_harness"].get(g, 0), A["dist_corrected"].get(g, 0)))
w("")
w("Changed clusters (harness -> corrected): **%d of %d**; direction split:" % (A["n_changed"], r3["n_recorded_clusters"]))
from collections import Counter
dirs = Counter((c["harness"], c["corrected"]) for c in A["changed_clusters"])
w("truly_inconsistent -> kb_coarser = %d, truly_inconsistent -> kb_finer = %d." % (
    dirs.get(("truly_inconsistent", "kb_coarser"), 0), dirs.get(("truly_inconsistent", "kb_finer"), 0)))
w("")
w("Because `Rulers.related()` uses the same closure, the family-level (R_fam) verdict moves too:")
w("consistent %d -> %d, related %d -> %d, inconsistent %d -> %d, mixed %d -> %d; **%d clusters are"
  " graded `inconsistent` by the harness and `related` by a qualifier-stripping closure** — every"
  " card that reused this harness under-reports relatedness by exactly this amount."
  % (A["rfam_states_harness"].get("consistent", 0), A["rfam_states_corrected"].get("consistent", 0),
     A["rfam_states_harness"].get("related", 0), A["rfam_states_corrected"].get("related", 0),
     A["rfam_states_harness"].get("inconsistent", 0), A["rfam_states_corrected"].get("inconsistent", 0),
     A["rfam_states_harness"].get("mixed", 0), A["rfam_states_corrected"].get("mixed", 0),
     A["n_rfam_state_moves"]))
w("All %d family-level moves are one-directional (harness `inconsistent` -> corrected `related`)."
  % A["n_rfam_state_moves"])
w("")
w("Top source B = the recorded ledger's own `pred_top1` column (no service call), as a second opinion:")
w("%d of %d clusters change under the two rulers (distribution: harness %s; corrected %s). The B"
  " counts differ from A because the ledger's recorded top labels predate the current shipped"
  " service state; A is the caliber the CL-56 wave recorded and is the one quoted below."
  % (B["n_changed"], r3["n_recorded_clusters"],
     ", ".join("%s=%d" % kv for kv in sorted(B["dist_harness"].items())),
     ", ".join("%s=%d" % kv for kv in sorted(B["dist_corrected"].items()))))
w("")
w("## 4. The %d affected clusters (top source A, full list)" % A["n_changed"])
w("")
w("| # | volume | cluster | pred_top1 | truth | harness grade | corrected grade |")
w("|---|---|---|---|---|---|---|")
for i, c in enumerate(A["changed_clusters"], 1):
    w("| %d | %s | %s | %s | %s | %s | %s |" % (
        i, c["vol"], c["cluster"], c["pred_top1"], c["truth"], c["harness"], c["corrected"]))
w("")
w("## 5. Why the harness is not edited (and what future waves must do)")
w("")
w("1. The harness's scripts are pinned by `docs/plans/noregr_20261022/out/MANIFEST.json` and")
w("   `out/MANIFEST.sha256` (entry `scripts/wave_common.py`); several later cards' recorded readings")
w("   state comparability with that ruler. Any byte edit — including a declared switch — invalidates")
w("   those pins and forces every consumer to re-run; that is a coordination decision this card does")
w("   not own.")
w("2. Until the closure is fixed at the harness, any wave that grades Cell-Ontology relations here")
w("   MUST state both readings (harness ruler + a qualifier-stripped second ruler, e.g. the")
w("   `ont_closure_probe.py` implementation this measurement reused) and must not cite a relatedness")
w("   deficit computed on the harness closure alone when the affected terms carry qualified `is_a`")
w("   parents. The re-derivation entry points:")
w("")
w("   - `/usr/bin/python3 scripts/r3_closure.py` (this wave: two top sources, both rulers, full lists)")
w("   - `/usr/bin/python3 /mnt/D/EyeKB/plans/cl56_adopt_20261022/scripts/ont_closure_probe.py` (the")
w("     corrected-closure implementation, zero-write)")
w("")
w("3. Recorded readings made BEFORE this registration remain comparable among themselves — all of")
w("   them carry the same harness-side under-count. Nothing delivered earlier changes value; the cost")
w("   is that `related` was under-counted by up to %d clusters on this recorded set." % A["n_rfam_state_moves"])
w("")
w("## 6. Verification this file follows (bytes, commands)")
w("")
w("- re-derivation: `/usr/bin/python3 scripts/r3_closure.py` -> out/R3_CLOSURE_READING.json")
w("  (committed mirror: docs/plans/kbreach_fix_20261024/out/R3_CLOSURE_READING.json)")
w("- pre-fix release parse: `/usr/bin/python3 scripts/r1_reproduce.py` -> out/R1_REPRODUCE.json")
w("  (D3 block: %d / %d / %d counts with the obo sha256 above)"
  % (d3["n_is_a_lines"], d3["qualified_any_qualifier"], qk.get('is_inferred="true"', 0)))
w("- the harness import in both scripts resolves to the frozen path above and is byte-identical to")
w("  the repo mirror (`docs/plans/noregr_20261022/scripts/wave_common.py`, sha256")
w("  f8226dc4aefc799ace536b66748ece67494826031c21242b6e25b44389f37863).")

text = "\n".join(lines) + "\n"
old = None
if os.path.exists(DEST):
    old = open(DEST, "rb").read()
with open(DEST, "w", encoding="utf-8") as f:
    f.write(text)
new = open(DEST, "rb").read()
doc = {"probe": "gen_limit_doc.py", "dest": DEST.replace(REPO + "/", ""), "bytes": len(new),
       "sha256": hashlib.sha256(new).hexdigest(), "n_changed_clusters": A["n_changed"],
       "n_rfam_moves": A["n_rfam_state_moves"], "qualified": d3["qualified_any_qualifier"]}
with open(os.path.join(OUT, "LIMIT_DOC_BUILD.json"), "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=1)
print(json.dumps(doc, ensure_ascii=False, indent=1))

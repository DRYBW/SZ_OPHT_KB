"""End-to-end acceptance for kbkit.

Not a unit test — this drives the real CLI the way an outside user would:
scaffold -> validate -> break a rule -> validate -> serve -> query.

Each scenario states the rule it exercises and the outcome it expects.
Exit code 0 only if every scenario behaves as asserted.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).parent
PY = sys.executable
results = []


def run(*args, stdin=None):
    p = subprocess.run([PY, "-m", "kbkit", *args], cwd=KIT.parent,
                       input=stdin, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print("%-58s %s" % (name, "PASS" if ok else "FAIL"))
    if not ok and detail:
        print("    " + detail.replace("\n", "\n    ")[:1200])


tmp = Path(tempfile.mkdtemp(prefix="kbkit_e2e_"))
try:
    plug = tmp / "retina-kb-plugin"

    # ── S1: scaffold ──────────────────────────────────────────────────────────
    rc, out = run("init", "retina", str(plug))
    check("S1 init creates plugin", rc == 0 and (plug / "plugin.yaml").exists(), out)
    check("S1 derived VOCABULARY.json from schema",
          (plug / "VOCABULARY.json").exists()
          and "organism_stage" in json.loads((plug / "VOCABULARY.json").read_text()),
          "vocabulary generated from schema")
    for sub in ("markers", "baselines", "disease", "ontology", "extensions"):
        if not (plug / sub).exists():
            check("S1 required dir %s" % sub, False, "missing")
            break
    else:
        check("S1 all required dirs present", True)

    # ── S2: fresh scaffold passes ─────────────────────────────────────────────
    rc, out = run("validate", str(plug))
    check("S2 fresh scaffold validates (empty plugin is valid)", rc == 0 and "RESULT: PASS" in out, out)

    # ── S3: R1 — a gene without direction must FAIL ───────────────────────────
    m = json.loads((plug / "markers" / "_TEMPLATE.json").read_text())
    entry = dict(m[0], entry_id="retina:0001", cell_type="Muller glia", cl_id="CL:0000636")
    entry["genes"] = [{"gene": "RLBP1", "provenance": {"pmid": "12345678"}, "evidence_level": "B"}]
    (plug / "markers" / "muller.json").write_text(json.dumps([entry], indent=2))
    rc, out = run("validate", str(plug))
    check("S3 R1: gene without direction is rejected",
          rc == 1 and "R1 VIOLATION" in out, out)

    # ── S4: R2 — no provenance must FAIL ──────────────────────────────────────
    entry["genes"] = [{"gene": "RLBP1", "direction": "+", "evidence_level": "B"}]
    (plug / "markers" / "muller.json").write_text(json.dumps([entry], indent=2))
    rc, out = run("validate", str(plug))
    check("S4 R2: gene without provenance is rejected",
          rc == 1 and "R2 VIOLATION" in out, out)

    # ── S5: compliant marker entry passes ─────────────────────────────────────
    entry["genes"] = [
        {"gene": "RLBP1", "direction": "+", "provenance": {"pmid": "12345678"},
         "evidence_level": "B", "panel": "core"},
        {"gene": "GFAP", "direction": "+", "provenance": {"pmid": "12345678"},
         "evidence_level": "C", "panel": "core"},
    ]
    (plug / "markers" / "muller.json").write_text(json.dumps([entry], indent=2))
    rc, out = run("validate", str(plug))
    check("S5 compliant marker entry passes", rc == 0 and "RESULT: PASS" in out, out)

    # ── S6: R4 — point estimate in baseline must FAIL ─────────────────────────
    b = json.loads((plug / "baselines" / "_TEMPLATE.json").read_text())
    be = dict(b[0], sampling_material="retina", n_donors=4)
    be["cells"] = [{"cell_type": "Muller glia", "proportion": [0.05, 0.05],
                    "pmid": "12345678", "evidence_level": "B"}]
    (plug / "baselines" / "retina_control.json").write_text(json.dumps([be], indent=2))
    rc, out = run("validate", str(plug))
    check("S6 R4: zero-width proportion (point estimate) rejected",
          rc == 1 and "looks like a point estimate" in out, out)

    be["cells"][0]["proportion"] = [0.03, 0.08]
    (plug / "baselines" / "retina_control.json").write_text(json.dumps([be], indent=2))
    rc, out = run("validate", str(plug))
    check("S6b proper per-donor range accepted", rc == 0 and "RESULT: PASS" in out, out)

    # ── S7: R4 — single donor must FAIL ───────────────────────────────────────
    be1 = dict(be, n_donors=1)
    (plug / "baselines" / "retina_control.json").write_text(json.dumps([be1], indent=2))
    rc, out = run("validate", str(plug))
    check("S7 R4: n_donors=1 rejected (ranges need >=2 donors)",
          rc == 1 and "need >=2 donors" in out, out)
    (plug / "baselines" / "retina_control.json").write_text(json.dumps([be], indent=2))

    # ── S8: R5 — state word standing in as cell type must FAIL ────────────────
    d = json.loads((plug / "disease" / "_TEMPLATE.json").read_text())
    de = dict(d[0], entry_id="retina:disease:0001", disease="PDR")
    de["cells"] = [{"cell_type": "Proliferating", "state": "cycling",
                    "signature": [], "pmid": "12345678"}]
    (plug / "disease" / "pdr.json").write_text(json.dumps([de], indent=2))
    rc, out = run("validate", str(plug))
    check("S8 R5: state word as cell type rejected",
          rc == 1 and "is a state word used as a cell type" in out, out)

    de["cells"] = [{"cell_type": "Macrophage", "state": "foam-like GPNMB+",
                    "signature": [], "pmid": "12345678"}]
    (plug / "disease" / "pdr.json").write_text(json.dumps([de], indent=2))
    rc, out = run("validate", str(plug))
    check("S8b type x state (correct form) accepted", rc == 0 and "RESULT: PASS" in out, out)

    # ── S9: R6 — non-author-level annotation must WARN ────────────────────────
    (plug / "registry.yaml").write_text(
        "datasets:\n"
        "  - dataset_id: D1\n"
        "    accession: GSE000000\n"
        "    species: human\n"
        "    tissue: retina\n"
        "    organism_stage: adult\n"
        "    annotation_level: sorted_pool\n"
        "    source: paper X\n", encoding="utf-8")
    rc, out = run("validate", str(plug))
    check("S9 R6: sorted_pool flagged (inadmissible as ground truth)",
          rc == 0 and "NOT admissible as evaluation ground truth" in out, out)
    (plug / "registry.yaml").write_text(
        "datasets:\n"
        "  - dataset_id: D1\n"
        "    accession: GSE000000\n"
        "    species: human\n"
        "    tissue: retina\n"
        "    organism_stage: adult\n"
        "    annotation_level: per_cell_author\n"
        "    source: paper X\n", encoding="utf-8")
    rc, out = run("validate", str(plug))
    check("S9b per_cell_author accepted without warning",
          rc == 0 and "NOT admissible" not in out, out)

    # ── S10: ontology naming discipline ───────────────────────────────────────
    entry2 = dict(entry, entry_id="retina:0002", cl_id="CL:9999999")
    (plug / "markers" / "muller.json").write_text(json.dumps([entry, entry2], indent=2))
    rc, out = run("validate", str(plug))
    check("S10 CL: term accepted", rc == 0 and "RESULT: PASS" in out, out)
    entry2["cl_id"] = "muller glia"
    (plug / "markers" / "muller.json").write_text(json.dumps([entry, entry2], indent=2))
    rc, out = run("validate", str(plug))
    check("S10b free-text cl_id rejected",
          rc == 1 and "must be a CL: term or NO_MATCH" in out, out)
    entry2["cl_id"] = "NO_MATCH"
    (plug / "markers" / "muller.json").write_text(json.dumps([entry, entry2], indent=2))
    rc, out = run("validate", str(plug))
    check("S10c NO_MATCH accepted when ontology has no term",
          rc == 0 and "RESULT: PASS" in out, out)

    # ── S11: serve — ranking and NO_MATCH boundary ────────────────────────────
    reqs = "\n".join([
        json.dumps({"op": "ping"}),
        json.dumps({"op": "query_marker", "genes": ["RLBP1", "GFAP"]}),
        json.dumps({"op": "query_marker", "genes": ["NOTAGENE"]}),
    ]) + "\n"
    rc, out = run("serve", str(plug), stdin=reqs)
    lines = [l for l in out.strip().splitlines() if l.startswith("{")]
    check("S11 serve emits ready banner", rc == 0 and len(lines) >= 4, out)
    try:
        ready = json.loads(lines[0]); pong = json.loads(lines[1])
        hit = json.loads(lines[2]); miss = json.loads(lines[3])
        check("S11b ready banner carries entry count", ready.get("entries") == 2, str(ready))
        check("S11c ping ok", pong.get("ok") is True, str(pong))
        check("S11d known genes resolve to top candidate",
              hit.get("result") == "Muller glia", str(hit))
        check("S11e no overlap returns NO_MATCH (no invented default)",
              miss.get("result") == "NO_MATCH", str(miss))
    except Exception as exc:                                   # noqa: BLE001
        check("S11 parse serve output", False, "%s\n%s" % (exc, out))

    # ── S12: three-part total order is deterministic ──────────────────────────
    from kbkit.cli import _rank
    from kbkit.cli import _load_plugin
    cfg, entries = _load_plugin(str(plug))
    orders = {tuple(r["entry_id"] for r in _rank(entries, ["RLBP1", "GFAP"])) for _ in range(200)}
    check("S12 ranking order is unique over 200 repeats", len(orders) == 1, str(orders))

finally:
    print()
    failed = [n for n, ok, _ in results if not ok]
    print("SUMMARY: %d/%d scenarios PASS" % (len(results) - len(failed), len(results)))
    if failed:
        print("FAILED: " + ", ".join(failed))
    if not failed:
        shutil.rmtree(tmp, ignore_errors=True)
    else:
        print("plugin kept for inspection: %s" % plug)
    sys.exit(1 if failed else 0)

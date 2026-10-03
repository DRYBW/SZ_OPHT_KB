#!/usr/bin/env python3
"""audit_annotations.py — check external annotation results against the known-issues layer (flags only; labels are never rewritten).

Input: CSV with columns including at least cluster_id, label; species/tissue can be specified row-wise or via
--species/--tissue global defaults (inline values take precedence). Tissue names use the controlled vocabulary alias table of this repository.
Output: <out>/annotations_audit.csv per-cluster flags + <out>/audit_summary.json summary.
Semantic discipline (consistent with runtime prompt injection):
  - Generate only REVIEW prompts and coordinate evidence status; never rewrite/downgrade/rename any annotation labels;
  - entry verification status is registered as-is: the first batch is entirely "Bibliographic record verified; manual re-review in progress"; treat the hints accordingly.
"""
import argparse, csv, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import consume  # noqa: E402


def _canon_tissue(t):
    t = str(t or "").strip().lower()
    t = consume.PULL_TISSUE_ALIAS.get(t, t.replace(" ", "_"))
    return t


def _load_grid():
    g = json.loads((HERE / "matrix" / "MATRIX_GRID.json").read_text(encoding="utf-8"))
    return {c["cell_id"]: c for c in g["cells"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="incsv", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--species", default="human")
    ap.add_argument("--tissue", default="retina")
    a = ap.parse_args()

    grid = _load_grid()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    claims_cache, rows = {}, []
    coords_seen = {}

    with open(a.incsv, newline="", encoding="utf-8-sig") as f:
        for rec in csv.DictReader(f):
            cid = (rec.get("cluster_id") or "").strip()
            label = (rec.get("label") or "").strip()
            sp = (rec.get("species") or a.species).strip().lower()
            ti = _canon_tissue(rec.get("tissue") or a.tissue)
            key = (sp, ti)
            if key not in claims_cache:
                try:
                    claims_cache[key] = consume.pull_claims(sp, ti)[0]
                except Exception:
                    claims_cache[key] = []
            claims = claims_cache[key]
            flags, audit = consume.cluster_flags(claims, [label] if label else [])
            cell = grid.get(f"{sp}__{ti}")
            coords_seen[key] = coords_seen.get(key, 0) + 1
            rows.append({
                "cluster_id": cid, "species": sp, "tissue": ti, "label": label,
                "grid_state": cell["grid_state"] if cell else "NOT_IN_TAXONOMY",
                "coordinate_activated": cell["activated"] if cell else "-",
                "n_claims_at_coordinate": len(claims),
                "pitfall_review_flags": ";".join(flags),
                "flagged_claim_ids": ";".join(x["claim_id"] for x in audit),
            })

    cols = list(rows[0].keys()) if rows else ["cluster_id", "species", "tissue",
          "label", "grid_state", "coordinate_activated", "n_claims_at_coordinate",
          "pitfall_review_flags", "flagged_claim_ids"]
    with open(out / "annotations_audit.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

    summary = {
        "tool": "eyekb-annotation-audit/1.0",
        "semantics": "advisory_risk_flags_only(no_relabel_no_cap_no_override)",
        "n_clusters": len(rows),
        "n_with_flags": sum(1 for r in rows if r["pitfall_review_flags"]),
        "coordinates": {f"{s}__{t}": n for (s, t), n in sorted(coords_seen.items())},
        "registry_status": "entries locator-verified; human clinical audit in progress "
                           "(treat flags as review cues, not verdicts)",
        "inputs": {"csv": str(a.incsv), "default_species": a.species,
                   "default_tissue": _canon_tissue(a.tissue)},
    }
    (out / "audit_summary.json").write_text(
        json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""audit_annotations.py — 对外部注释结果的已知问题对照（只举旗，不改写标签）。

输入：CSV，列至少含 cluster_id,label；species/tissue 可逐行给，或用
--species/--tissue 全局默认（行内值优先）。tissue 名走本仓受控词表别名表。
输出：<out>/annotations_audit.csv 逐簇旗标 + <out>/audit_summary.json 汇总。
语义纪律（与运行时提示注入一致）：
  - 只产生 REVIEW 提示与坐标证据状态，绝不改写/降级/更名任何注释标签；
  - 条目核验状态如实登记：首批全部为"题录已核、人工复审进行中"，提示按参考对待。
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

#!/usr/bin/env python3
"""FAIRX4A / step A1 — X2-style lenient alias layer on X4A, built under the
pre-registered rules in PREREG_FAIRX4A_20261024.md §2.2 (R1-R5).

Reads  (never writes): arms/cw_x4a.tsv, arms/pred_*_x4a*.tsv, arms/engine_gold_x4a.tsv
Writes (all new files, official artifacts untouched):
  out/ARM_A_label_inventory.tsv     — every (arm, raw_label): cells, mapped target, in-gold status
  out/WHITELIST_X4A.tsv             — admitted lenient edges (R1/R2/R5)
  out/WHITELIST_REJECTED_X4A.tsv    — rejected candidates + reason code (R4 / R1)
  out/ARM_A_unreachable_mass.tsv    — lineage-unreachable cell mass per arm/label + truth distribution
  out/ARM_A_oracle_bound.json       — unattainable upper bound (all unreachable cells named correctly)
  cw_x4a_lenient.tsv                — official cw + admitted edges (revise-in-place; no duplicate keys)
  out/WHITELIST_X4A.sha256, out/CW_LENIENT_X4A.sha256

No engine call here: the whitelist + lenient crosswalk are frozen by sha256 BEFORE scoring (rule R3).
"""
import csv, hashlib, json, os, collections

P = "/mnt/D/EyeKB/plans/toolbenchmark_20261010_x4clean"
WORK = "/mnt/D/EyeKB/plans/fairex4a_20261024"
OUT = f"{WORK}/out"
os.makedirs(OUT, exist_ok=True)

ARMS = ["C1", "C2", "A1a_eyesgpt", "A1b_scgpt", "B1a_celltypist", "B1b_celltypist"]
PRED = {
    "C1": f"{P}/arms/pred_C1_x4a.tsv",
    "C2": f"{P}/arms/pred_C2_x4a.tsv",
    "A1a_eyesgpt": f"{P}/arms/pred_A1a_eyesgpt_x4a.tsv",
    "A1b_scgpt": f"{P}/arms/pred_A1b_scgpt_x4a_raw.tsv",
    "B1a_celltypist": f"{P}/arms/pred_B1a_celltypist_x4a.tsv",
    "B1b_celltypist": f"{P}/arms/pred_B1b_celltypist_x4a.tsv",
}
ABSTAIN = {"true", "yes", "abstain"}

# ---- frozen gold ----
gold = {}
for r in csv.DictReader(open(f"{P}/arms/engine_gold_x4a.tsv"), delimiter="\t"):
    gold[r["cell_id"]] = (r["truth_lineage"], r["truth_celltype"])
LIN_C = sorted({v[0] for v in gold.values()})
CT_C = sorted({v[1] for v in gold.values()})
print("gold", len(gold), "lineages", LIN_C, "n_ct", len(CT_C))

# ---- official crosswalk (read-only) ----
cw_rows = []
cw = {}
with open(f"{P}/arms/cw_x4a.tsv", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        cw_rows.append(r)
        k = (r["arm"], r["raw_label"])
        assert k not in cw, f"official cw duplicate key {k}"
        cw[k] = r
print("official cw rows", len(cw_rows))

# ---- PRE-REGISTERED admitted edges (PREREG §2.2 R5) ----
MULLER_LABELS = ["Mueller cell", "Mu_ller", "imGlia", "Glia", "Early Glia"]
MULLER_EVID = ("R5 Muller-family within-glia rename: Muller glia is the retinal macroglia; the gold's glial "
               "vocabulary is {astrocyte, oligodendrocyte, OPC, Schwann x2} with no Muller term, and astrocyte "
               "(CL:0000127) is its only macroglial landing point. Same family as the X2 precedent's Glia->glia "
               "edge. Kept as its own edge_class so the report can show totals with and without it.")
ADMITTED = {lab: ("glia", "astrocyte", "muller_within_glia", MULLER_EVID) for lab in MULLER_LABELS}
# No other edge passes R1/R4 — see REJECTED table for the explicit necrology.

NEURON_MARK = ("amacrine", "bipolar", "horizontal", "ganglion", "parasol", "midget", "rod", "cone",
               "starburst", "photoreceptor", "progenitor", "rpc")
NEURON_LIN = {"RetinalInterneuron", "RGC", "Photoreceptor", "RetinalProgenitor"}


def classify_reject(pl, pc, lab):
    if pl in NEURON_LIN or any(k in str(pc).lower() for k in NEURON_MARK) \
            or any(k in str(lab).lower() for k in NEURON_MARK):
        return ("R4_neuron",
                "retinal neuron / photoreceptor / progenitor identity: the gold's five lineages "
                "(glia/immune/pigmented/stromal/vascular) contain no neuronal class, so no "
                "human-acceptable naming act exists; mapping it would manufacture movement (PREREG R4)")
    return ("R1_no_gold_class",
            "no gold class is a synonym or subtype of this identity; a human adjudicator would leave it "
            "unresolved rather than assign a foreign lineage")


inv_rows, whitelist_rows, rejected_rows = [], [], []
mass_all = {}
for arm in ARMS:
    pred = {}
    for r in csv.DictReader(open(PRED[arm]), delimiter="\t"):
        pred[r["cell_id"]] = (r["raw_label"], str(r.get("abstain", "0")).lower() in ABSTAIN)
    assert len(pred) == len(gold), (arm, len(pred), len(gold))
    cnt = collections.Counter(v[0] for v in pred.values())

    mass = collections.defaultdict(collections.Counter)      # arm: raw_label -> truth_lineage counts
    per_truth = collections.Counter()                        # arm: truth_lineage of unreachable cells
    for cid, (gl, gc) in gold.items():
        lab, ab = pred[cid]
        m = cw.get((arm, lab))
        if ab or m is None or m["confidence"].lower() in {"med", "low", "flagged", "uncertain"}:
            continue
        if m["lineage"] not in LIN_C:
            mass[lab][gl] += 1
            per_truth[gl] += 1
    mass_all[arm] = {"by_label": {k: dict(v) for k, v in mass.items()}, "by_truth": dict(per_truth),
                     "n_unreachable": int(sum(per_truth.values()))}

    for lab, n in cnt.most_common():
        m = cw.get((arm, lab))
        if m is None:
            inv_rows.append([arm, lab, n, "", "", "", "UNMAPPED", ""])
            continue
        pl, pc, conf = m["lineage"], m["canonical_cell_type"], m["confidence"]
        lin_ok, ct_ok = pl in LIN_C, pc in CT_C
        status = ("in_gold_both" if (lin_ok and ct_ok) else
                  ("lineage_ok_ct_out" if lin_ok else "lineage_out_of_gold"))
        inv_rows.append([arm, lab, n, pl, pc, conf, status, ""])
        if lab in ADMITTED:
            # ct-layer-only edge (lineage already inside the gold five): still a pre-registered
            # lenient edge, listed so the deliverable is complete; `layer` column says which layer moves.
            _tl, _tc, _edge, _ev = ADMITTED[lab]
            layer = "ct_only" if lin_ok else "lineage+ct"
            whitelist_rows.append([arm, lab, n, layer, pl, pc, _tl, _tc, _edge, _ev])
        if lin_ok:
            continue
        if lab in ADMITTED:
            pass
        else:
            code, why = classify_reject(pl, pc, lab)
            rejected_rows.append([arm, lab, n, pl, pc, code, why])

    print(f"arm {arm:16s} labels={len(cnt):3d} unreachable_cells={mass_all[arm]['n_unreachable']:6d} "
          f"admitted_edges={sum(1 for r in whitelist_rows if r[0]==arm)}", flush=True)


def write_tsv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    print("WROTE", path, len(rows), "rows")


write_tsv(f"{OUT}/ARM_A_label_inventory.tsv",
          ["arm", "raw_label", "n_cells", "mapped_lineage", "mapped_ct", "confidence", "status", "note"],
          inv_rows)
write_tsv(f"{OUT}/WHITELIST_X4A.tsv",
          ["arm", "raw_label", "n_cells", "layer", "official_lineage", "official_ct", "lenient_lineage",
           "lenient_ct", "edge_class", "evidence"],
          whitelist_rows)
write_tsv(f"{OUT}/WHITELIST_REJECTED_X4A.tsv",
          ["arm", "raw_label", "n_cells", "official_lineage", "official_ct", "reason_code", "reason"],
          rejected_rows)

# unreachable mass table
mass_rows = []
for arm in ARMS:
    for lab, d in sorted(mass_all[arm]["by_label"].items(), key=lambda kv: -sum(kv[1].values())):
        mass_rows.append([arm, lab, sum(d.values())] + [d.get(k, 0) for k in LIN_C])
    mass_rows.append([arm, "__TOTAL__", mass_all[arm]["n_unreachable"]] +
                     [mass_all[arm]["by_truth"].get(k, 0) for k in LIN_C])
write_tsv(f"{OUT}/ARM_A_unreachable_mass.tsv",
          ["arm", "raw_label", "n_cells_unreachable"] + [f"truth_{k}" for k in LIN_C],
          mass_rows)

# ---- lenient crosswalk: official rows + admitted edges (revise in place, never duplicate) ----
new_rows, revised = [], []
for r in cw_rows:
    k = (r["arm"], r["raw_label"])
    if k in cw and r["raw_label"] in ADMITTED:
        tl, tc, edge, ev = ADMITTED[r["raw_label"]]
        nr = dict(r)
        nr["lineage"], nr["canonical_cell_type"], nr["confidence"] = tl, tc, "high"
        nr["evidence"] = (f"[LENIENT {edge}] official was ({r['lineage']}/{r['canonical_cell_type']}); "
                          f"{ev}")
        revised.append([r["arm"], r["raw_label"], r["lineage"], r["canonical_cell_type"], tl, tc])
        new_rows.append(nr)
    else:
        new_rows.append(r)
# append edges whose key does not exist yet
existing = {(r["arm"], r["raw_label"]) for r in new_rows}
appended = []
for arm, lab, n, layer, pl, pc, tl, tc, edge, ev in whitelist_rows:
    if (arm, lab) in existing:
        continue
    new_rows.append({"arm": arm, "raw_label": lab, "lineage": tl, "canonical_cell_type": tc,
                     "confidence": "high", "evidence": f"[LENIENT {edge}] added; official had no row; {ev}"})
    appended.append([arm, lab, tl, tc])

keys = [(r["arm"], r["raw_label"]) for r in new_rows]
assert len(keys) == len(set(keys)), "lenient cw has duplicate (arm, raw_label) keys"
assert len(new_rows) == len(cw_rows) + len(appended), (len(new_rows), len(cw_rows), len(appended))
with open(f"{WORK}/cw_x4a_lenient.tsv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["arm", "raw_label", "lineage", "canonical_cell_type", "confidence",
                                      "evidence"], delimiter="\t", lineterminator="\n")
    w.writeheader()
    for r in new_rows:
        w.writerow({k: r[k] for k in w.fieldnames})
print("LENIENT CW: official rows", len(cw_rows), "-> new", len(new_rows),
      "| revised in place", len(revised), "| appended", len(appended))

# ---- oracle bound (explicitly unattainable) ----
def macro_f1(pairs, classes):
    tp = collections.Counter(); fp = collections.Counter(); fn = collections.Counter()
    for p, g in pairs:
        if p is None:
            fn[g] += 1
        elif p == g:
            tp[g] += 1
        else:
            fp[p] += 1; fn[g] += 1
    f1 = {}
    for c in classes:
        pr = tp[c] / (tp[c] + fp[c]) if tp[c] + fp[c] else 0.0
        rc = tp[c] / (tp[c] + fn[c]) if tp[c] + fn[c] else 0.0
        f1[c] = 2 * pr * rc / (pr + rc) if pr + rc else 0.0
    return sum(f1.values()) / len(f1), f1


oracle = {}
for arm in ARMS:
    pred = {}
    for r in csv.DictReader(open(PRED[arm]), delimiter="\t"):
        pred[r["cell_id"]] = (r["raw_label"], str(r.get("abstain", "0")).lower() in ABSTAIN)
    asis, orac = [], []
    for cid, (gl, gc) in gold.items():
        lab, ab = pred[cid]
        m = cw.get((arm, lab))
        pl = None if (ab or m is None or m["confidence"].lower() in
                      {"med", "low", "flagged", "uncertain"}) else m["lineage"]
        if pl is not None and pl not in LIN_C:
            asis.append((None, gl)); orac.append((gl, gl))   # oracle: named correctly
        else:
            asis.append((pl if (pl in LIN_C) else None, gl))
            orac.append((pl if (pl in LIN_C) else None, gl))
    m_asis, _ = macro_f1(asis, LIN_C)
    m_orac, f1o = macro_f1(orac, LIN_C)
    oracle[arm] = {"macro_f1_as_is": round(m_asis, 4), "macro_f1_if_all_unreachable_named_correctly": round(m_orac, 4),
                   "n_unreachable": mass_all[arm]["n_unreachable"],
                   "note": "UNATTAINABLE oracle: an alias maps a LABEL, not a cell; the same label carries "
                           "different true lineages. Reported only to bound what any alias layer could ever move."}
    print(f"oracle {arm:16s} as-is {m_asis:.4f} -> oracle {m_orac:.4f} (n_unreachable {mass_all[arm]['n_unreachable']})")
json.dump(oracle, open(f"{OUT}/ARM_A_oracle_bound.json", "w"), indent=1)

with open(f"{OUT}/ARM_A_lenient_cw_edits.json", "w") as f:
    json.dump({"revised_in_place": revised, "appended": appended,
               "official_rows": len(cw_rows), "lenient_rows": len(new_rows)}, f, indent=1)

# ---- reconcile the unreachable/ct-out mass against the engine's own n_invalid_projection ----
off = json.load(open(f"{P}/arms/ALL_SCORES.json"))["x4a"]
recon = []
for arm in ARMS:
    n_lin = mass_all[arm]["n_unreachable"]
    n_ct_only = sum(int(r[2]) for r in inv_rows if r[0] == arm and r[6] == "lineage_ok_ct_out")
    n_unmapped = sum(int(r[2]) for r in inv_rows if r[0] == arm and r[6] == "UNMAPPED"
                     and r[1] not in ("unknown", "STAGE_A_QC_DROP"))
    eng = int(off[arm]["n_invalid_projection"])
    recon.append([arm, eng, n_lin, n_ct_only, n_unmapped, n_lin + n_ct_only + n_unmapped,
                  "EXACT" if n_lin + n_ct_only + n_unmapped == eng else "DIFF=%d" % (
                      eng - (n_lin + n_ct_only + n_unmapped))])
    print(f"recon {arm:16s} engine_invalid={eng:6d} lineage_unreachable={n_lin:6d} "
          f"ct_only={n_ct_only:6d} unmapped={n_unmapped} sum={n_lin+n_ct_only+n_unmapped}")
write_tsv(f"{OUT}/ARM_A_invalid_reconciliation.tsv",
          ["arm", "n_invalid_projection_official", "n_lineage_unreachable", "n_ct_only_invalid",
           "n_unmapped_extra", "sum", "match"], recon)

for p in [f"{OUT}/WHITELIST_X4A.tsv", f"{WORK}/cw_x4a_lenient.tsv"]:
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    side = f"{OUT}/WHITELIST_X4A.sha256" if p.endswith("WHITELIST_X4A.tsv") else f"{OUT}/CW_LENIENT_X4A.sha256"
    open(side, "w").write(f"{h}  {os.path.basename(p)}\n")
    print("SHA", h, p)
print("ARM_A_WHITELIST_BUILD_DONE")

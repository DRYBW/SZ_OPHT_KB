#!/usr/bin/env python3
"""A discriminating state reference (Annex A7 amendment A7-b).

A gene is `state_dependent` iff at least R of the discovery-corpus chunks that mention it are
state-context chunks (cell-cycle arm, or disease/treatment arm). R is reported at several cutoffs so the
reader can see the operation's sensitivity; the pre-registered tier test uses R = 0.75.

One pass over the corpus. Read-only, no network.
"""
import collections
import json
import re

import pyarrow.dataset as ds

WAVE = "/mnt/D/EyeKB/plans/subdivision_readiness_20261022"
OUT = f"{WAVE}/out"
CORPUS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10/chunks.parquet"
GENE_VOCAB = "/mnt/D/EyeKB/plans/antseg_fill_20261020/out/gene_vocab.json"

_UP = "A-Z"
# The gene-token recipe has one home (m_scan.py); import it rather than restating the pattern.
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("m_scan", "/mnt/D/EyeKB/plans/subdivision_readiness_20261022/scripts/m_scan.py")
_m = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_m)
TOKEN = _m.TOKEN

CC_RE = re.compile(r"cell cycle|mitotic|proliferat|MKI67|TOP2A|Ki-?67|cycling|proliferation", re.I)
DIS_RE = re.compile(r"disease|patholog|degenerat|dystroph|gliosis|inflam|injur|AMD|diabet|"
                    r"retinopathy|glaucoma|fibro", re.I)
TRE_RE = re.compile(r"treated|treatment|inhibitor|\bknockout\b|knock-?down|overexpress|"
                    r"stimulat|exposed to|administered|transfect", re.I)
CUTOFFS = [0.50, 0.75, 0.90]


def main():
    vocab = set(json.load(open(GENE_VOCAB)))
    total = collections.Counter()
    arm = {"cc": collections.Counter(), "dis": collections.Counter(), "tre": collections.Counter()}
    anystate = collections.Counter()
    n_chunks = 0
    n_cc = n_dis = n_tre = 0

    pf = ds.dataset(CORPUS).to_batches(batch_size=20000, columns=["text"])
    for b in pf:
        for body in b.column("text").to_pylist():
            if not body:
                continue
            n_chunks += 1
            toks = {t for t in TOKEN.findall(body) if t in vocab}
            if not toks:
                continue
            for t in toks:
                total[t] += 1
            hit_any = False
            if CC_RE.search(body):
                n_cc += 1
                hit_any = True
                for t in toks:
                    arm["cc"][t] += 1
            if DIS_RE.search(body):
                n_dis += 1
                hit_any = True
                for t in toks:
                    arm["dis"][t] += 1
            if TRE_RE.search(body):
                n_tre += 1
                hit_any = True
                for t in toks:
                    arm["tre"][t] += 1
            if hit_any:
                for t in toks:
                    anystate[t] += 1

    print(f"chunks={n_chunks}  cc={n_cc}  disease={n_dis}  treatment={n_tre}", flush=True)
    ratios, anys = {}, {}
    for g, n in total.items():
        s = anystate[g]
        anys[g] = s
        ratios[g] = round(min(1.0, s / n), 4)

    sets = {}
    for cut in CUTOFFS:
        # require >= 3 mentions so a single state-context mention cannot brand a gene
        sets[str(cut)] = sorted(g for g, r in ratios.items() if r >= cut and total[g] >= 3)
    print("state_dependent set sizes:", {k: len(v) for k, v in sets.items()}, flush=True)

    doc = {"source_corpus": CORPUS, "definition": "Annex A7-b: state ratio = state-context chunks / all chunks",
           "cutoffs": CUTOFFS, "min_mentions": 3,
           "n_chunks": n_chunks, "n_cc": n_cc, "n_disease": n_dis, "n_treatment": n_tre,
           "arm_sizes": {k: len(v) for k, v in arm.items()},
           "state_dependent_by_cutoff": sets,
           "n_genes_scored": len(ratios),
           "ratios": ratios}
    json.dump(doc, open(f"{OUT}/O_state_ratio.json", "w"), ensure_ascii=False, indent=1)
    print("wrote", f"{OUT}/O_state_ratio.json")


if __name__ == "__main__":
    main()
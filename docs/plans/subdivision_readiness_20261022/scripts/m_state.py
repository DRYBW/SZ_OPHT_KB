#!/usr/bin/env python3
"""The state-programme reference, built from local material only (Annex A7).

Arms:
  cell_cycle   - the dictionary's own proliferation entries, plus genes of discovery-corpus chunks whose text
                 matches the pre-registered cell-cycle vocabulary
  disease      - the genes recorded in the shipped disease thin layer kb/priors/disease/*.json, plus genes of
                 discovery-corpus chunks whose text matches a disease token
  treatment    - genes of discovery-corpus chunks whose text matches a treatment/injury token

Read-only, no network.
"""
import collections
import glob
import json
import re
import sys

import pyarrow.dataset as ds

WAVE = "/mnt/D/EyeKB/plans/subdivision_readiness_20261022"
OUT = f"{WAVE}/out"
CORPUS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10/chunks.parquet"
GENE_VOCAB = "/mnt/D/EyeKB/plans/antseg_fill_20261020/out/gene_vocab.json"
DICT = "/home/ubuntu/EYEKB_REPO/kb/markers/markers_cl_alignment_v2_unified.json"

_UP = "A-Z"
TOKEN = re.compile(r"\b[" + _UP + "][" + _UP + r"0-9]{1,13}(?:-[" + _UP + r"0-9]{1,6})?\b")

CC_RE = re.compile(r"cell cycle|mitotic|proliferat|MKI67|TOP2A|Ki-?67|cycling", re.I)
DIS_RE = re.compile(r"disease|patholog|degenerat|dystroph|gliosis|inflam|injur|AMD|diabet|"
                    r"retinopathy|glaucoma|fibro", re.I)
TRE_RE = re.compile(r"treated|treatment|inhibitor|\bknockout\b|knock-?down|overexpress|"
                    r"stimulat|exposed to|administered|transfect", re.I)

PROLIF_LABELS = ["Proliferating", "Retinal_Proliferating", "TAC_proliferating"]


def main():
    vocab = set(json.load(open(GENE_VOCAB)))

    # arm 1a: the dictionary's own proliferation entries
    dic = json.load(open(DICT))
    libs = {}
    for lib, meta in dic["libraries"].items():
        p = f"/home/ubuntu/EYEKB_REPO/kb/markers/{meta['file']}"
        try:
            doc = json.load(open(p))
        except Exception:
            continue
        mk = doc.get("markers") if isinstance(doc, dict) else None
        if isinstance(mk, dict):
            libs.update({k: v for k, v in mk.items()})
    cc_dict = sorted({g for lab in PROLIF_LABELS for g in (libs.get(lab) or [])})
    print(f"dictionary proliferation genes: {len(cc_dict)} -> {cc_dict}", flush=True)

    # arm 2: the shipped disease thin layer
    dis_layer = {}
    for p in sorted(glob.glob("/home/ubuntu/EYEKB_REPO/kb/priors/disease/*.json")):
        try:
            doc = json.load(open(p))
        except Exception:
            continue
        found = set()

        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if isinstance(v, str) and v in vocab and k.lower() in (
                            "gene", "genes", "marker", "markers", "symbol", "symbols"):
                        found.add(v)
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(doc)
        dis_layer[p.split("/")[-1]] = sorted(found)
        print(f"   {p.split('/')[-1]:50s} genes={len(found)}", flush=True)
    dis_genes = sorted({g for v in dis_layer.values() for g in v})

    # arms 1b/2b/3b: corpus chunks by state context
    pdf = ds.dataset(CORPUS).to_table(columns=["text"]).to_pandas()
    low = pdf["text"].fillna("")
    arms = {}
    for name, rx in (("cell_cycle", CC_RE), ("disease", DIS_RE), ("treatment", TRE_RE)):
        sel = low.str.contains(rx, regex=True, na=False)
        genes = collections.Counter()
        for body in low[sel]:
            for t in TOKEN.findall(body):
                if t in vocab:
                    genes[t] += 1
        arms[name] = {"n_chunks": int(sel.sum()), "n_genes": len(genes),
                      "genes": sorted(g for g, n in genes.items() if n >= 2)}
        print(f"   corpus arm {name:12s} chunks={int(sel.sum()):>7d} genes(>=2 chunks)={len(arms[name]['genes'])}",
              flush=True)

    state = sorted(set(cc_dict) | set(arms["cell_cycle"]["genes"])
                   | set(dis_genes) | set(arms["disease"]["genes"]) | set(arms["treatment"]["genes"]))
    doc = {"source_corpus": CORPUS, "definition": "Annex A7 state reference",
           "dictionary_proliferation_genes": cc_dict,
           "disease_thin_layer": dis_layer,
           "corpus_arms": arms,
           "state_reference_genes": state,
           "n_state_reference_genes": len(state)}
    json.dump(doc, open(f"{OUT}/O_state_reference.json", "w"), ensure_ascii=False, indent=1)
    print(f"state reference genes = {len(state)}")
    print("wrote", f"{OUT}/O_state_reference.json")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Step 1 of the subdivision-readiness measurement: one pass over the discovery corpus.

Produces, per (candidate child name, shipped parent):
  occurrence  - chunks / distinct studies / tissues, total and inside the parent's declared target context,
                on two channels kept apart: the term's CL preferred name, and its CL synonyms
  genes       - genes seen in >= 1 distinct study, with a per-study count (>= 2 = a positive gene)
  contrast    - papers in which the name co-occurs with a sibling name in one chunk carrying contrast language

Nothing is taken from any reference label of an evaluation volume. Corpus is the discovery library.
Read-only, no network.
"""
import collections
import json
import re
import sys

import pyarrow.dataset as ds

sys.path.insert(0, "/mnt/D/EyeKB/plans/holefill_v12_20261021")
import cl_nav  # noqa: E402

WAVE = "/mnt/D/EyeKB/plans/subdivision_readiness_20261022"
OUT = f"{WAVE}/out"
CORPUS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10/chunks.parquet"
GENE_VOCAB = "/mnt/D/EyeKB/plans/antseg_fill_20261020/out/gene_vocab.json"
DICT = "/home/ubuntu/EYEKB_REPO/kb/markers/markers_cl_alignment_v2_unified.json"
OBO = "/mnt/D/OcularKB/ocularkb/rag/ontology/cl-base.obo"

CONTRAST = re.compile(r"differ|distinct|versus|\bvs\b|contrast|discriminat|separate|distinguish|"
                      r"unique to|specific to|unlike|whereas", re.I)
_UP = "A-Z"
TOKEN = re.compile(r"\b[" + _UP + "][" + _UP + r"0-9]{1,13}(?:-[" + _UP + r"0-9]{1,6})?\b")

# Stage / system tokens are matched against the library files' own declarations
# (candidate declarations, not literature claims).
DEV_TOKENS = ["fetal", "developing", "development", "precursor"]
SYSTEM_TOKENS = {"organoid_or_ipsc": ["organoid", "ipsc", "ips"]}
CORPUS_TISSUES = ["retina", "RPE", "optic_nerve", "conjunctiva", "cornea", "ciliary_body",
                  "lens", "choroid", "trabecular_meshwork", "sclera", "iris"]

# Artifact classes that are not gene symbols; the same stop list the repository's own mining
# recipe uses, extended by the tokens of this wave's declaration vocabulary.
STOP = set("""DNA RNA PCR FBS DMEM PBS EDTA DAPI CDNA MRNA SIRNA QPCR RNAI RNASEQ ATAC SEQ
WHO FDA USA UK EU BMI CT MRI CDS UTR KO WT HET FIG SUPP TABLE AA AB ABC ANOVA SD SEM CI FACS
PCA TSNE UMAP QC GO KEGG GSEA FPKM TPM RPKM CPM DE DEG DAB FITC PE APC HRP BSA SDS PAGE GTP GDP
ATP ADP AMP NAD MACS RIPA TBS TBST MOPS HEPES YEAST MALE FEMALE LEFT RIGHT NOD SCID IRB IACUC
NIH AMD DR PDR NPDR ONH LEC LFC AUC ROC PR SEN SPEC EM TBD NS MPS LPS IFN IL TNF TGF VEGF EGF
FGF IGF PDGF BMP WNT SHH NOTCH JAK STAT MAPK AKT MTOR ERK PI3K NFKB PKC CAMP CGMP GMP GSH ROS
AAV LENTI CRISPR CAS9 TALEN HPA GTEX TCGA GEO SRA ENA EBI NCBI EMBL DDBJ PDB CNV GWAS SNP SNPS
QTL EQTL MAF LD UMI FOV ROI CZI SLIDE SVS OME
RPE ONH TM CB LEC IPSC ESC PSC CNS PNS RGC BC AC HC MG SMC""".split())


CROSSWALK = "/home/ubuntu/EYEKB_REPO/kb/baselines/_tissue_class_crosswalk_v1.json"


def crosswalk_tissues():
    """Shipped, PI-authorized class -> tissue table (A3-b source 1)."""
    doc = json.load(open(CROSSWALK))
    out = collections.defaultdict(list)
    for tissue, v in (doc.get("tissues") or {}).items():
        for c in (v.get("classes") or []):
            k = c.get("kb_class")
            if k:
                out[k].append(tissue)
    return {k: sorted(set(v)) for k, v in out.items()}


def library_context():
    """Per library named in the dictionary: declared tissues / stage / system, read from disk."""
    dic = json.load(open(DICT))
    ctx = {}
    for lib, meta in dic["libraries"].items():
        path = f"/home/ubuntu/EYEKB_REPO/kb/markers/{meta['file']}"
        decl = {"file": meta["file"], "state": meta.get("state"), "keys": {}, "tissues": [],
                "stage": "adult", "system": "in_vivo", "label_count": meta.get("labels")}
        try:
            doc = json.load(open(path))
        except Exception as e:
            decl["error"] = str(e)[:200]
            ctx[lib] = decl
            continue
        if not isinstance(doc, dict):
            ctx[lib] = decl
            continue
        blob = []
        for k in ("scope_tissues", "applicability", "scope", "species", "organism_stage",
                  "development_stage", "note"):
            if k in doc:
                v = doc[k]
                s = " ".join(str(x) for x in v) if isinstance(v, list) else str(v)
                decl["keys"][k] = s[:400]
                blob.append(s)
        low = " ".join(blob).lower()
        for t in CORPUS_TISSUES:
            if t.lower() in low:
                decl["tissues"].append(t)
        if any(x in low for x in DEV_TOKENS):
            decl["stage"] = "fetal_developing"
        for k, toks in SYSTEM_TOKENS.items():
            if any(x in low for x in toks):
                decl["system"] = k
        ctx[lib] = decl
    return ctx


def build_automata(terms, name2parents):
    """Two automata: CL preferred names, and unambiguous CL synonyms pre-mapped to a name."""
    pref = {n: n for n in name2parents}                       # key -> canonical preferred name
    syn_raw = collections.defaultdict(set)                    # synonym -> set(canonical names)
    for nm in name2parents:
        pass
    # gather synonyms per canonical preferred name
    canon_of_term = {}
    for tid, t in terms.items():
        n = t.get("name")
        if n and n in name2parents:
            canon_of_term[tid] = n
    for tid, canon in canon_of_term.items():
        for s in terms[tid].get("synonyms") or []:
            s = s.strip()
            if not s or len(s) < 4:
                continue
            syn_raw[s.lower()].add(canon)
    ambiguous = {s: sorted(v) for s, v in syn_raw.items() if len(v) > 1}
    syn = {s: next(iter(v)) for s, v in syn_raw.items()
           if len(v) == 1 and next(iter(v)).lower() != s}
    return pref, syn, ambiguous


def compile_pat(keys):
    ks = sorted(keys, key=len, reverse=True)
    return re.compile(r"(?<![a-z0-9])(" + "|".join(re.escape(k) for k in ks) + r")(?:s|es)?(?![a-z0-9])")


def main():
    dic = json.load(open(DICT))
    labels = dic["labels"]
    obo = cl_nav.load(OBO)
    terms = obo["terms"]
    lctx = library_context()
    json.dump(lctx, open(f"{OUT}/S0_library_context.json", "w"), ensure_ascii=False, indent=1)
    print("== S0 library contexts (read from the library files) ==", flush=True)
    for lib, c in sorted(lctx.items()):
        print(f"   {lib:20s} tissues={c['tissues']} stage={c['stage']} system={c['system']}",
              flush=True)

    xw = crosswalk_tissues()
    parents, name2parents = [], collections.defaultdict(list)
    for lab, meta in labels.items():
        cid = meta.get("cl_id")
        libs = meta.get("libraries") or []
        tissues, stage, system = set(), "adult", "in_vivo"
        for lib in libs:
            c = lctx.get(lib) or {}
            tissues |= set(c.get("tissues") or [])
            if c.get("stage") == "fetal_developing":
                stage = "fetal_developing"
            if c.get("system") == "organoid_or_ipsc":
                system = "organoid_or_ipsc"
        cw = xw.get(lab) or []
        tissue_source = ("crosswalk+library" if (cw and tissues) else
                         ("crosswalk" if cw else ("library" if tissues else "undeclared")))
        tissues = set(cw) | tissues
        desc = cl_nav.descendants(cid, OBO) if cid else []
        children = sorted({terms[x]["name"] for x in desc if (terms.get(x) or {}).get("name")})
        parents.append({"parent": lab, "cl_id": cid, "cl_label": meta.get("cl_label"),
                        "libraries": libs, "tissues": sorted(tissues), "stage": stage,
                        "system": system, "tissue_source": tissue_source,
                        "n_children": len(children), "children": children})
        for nm in children:
            name2parents[nm].append(lab)
    json.dump(parents, open(f"{OUT}/S1_parents_context.json", "w"), ensure_ascii=False, indent=1)
    p_tissue_map = {p["parent"]: set(p["tissues"]) for p in parents}
    p_declared = {p["parent"]: bool(p["tissues"]) for p in parents}
    print(f"== S1 parents={len(parents)} candidate child names={len(name2parents)} ==", flush=True)

    pref, syn, ambiguous = build_automata(terms, name2parents)
    json.dump({"n_preferred": len(pref), "n_synonyms_unambiguous": len(syn),
               "n_synonyms_ambiguous_rejected": len(ambiguous),
               "ambiguous_sample": dict(list(ambiguous.items())[:40])},
              open(f"{OUT}/S2_automata.json", "w"), ensure_ascii=False, indent=1)
    pat_pref = compile_pat(pref)
    pat_syn = compile_pat(syn) if syn else None
    print(f"== S2 preferred={len(pref)} synonyms(unambiguous)={len(syn)} "
          f"synonyms(ambiguous, rejected)={len(ambiguous)} ==", flush=True)

    vocab = set(json.load(open(GENE_VOCAB)))
    print(f"== S3 gene vocabulary={len(vocab)} ==", flush=True)

    pdf = ds.dataset(CORPUS).to_table(
        columns=["paper_id", "species", "tissue", "tissue_labels", "text", "marker_genes"]).to_pandas()
    print(f"== S4 corpus chunks={len(pdf)} ==", flush=True)
    low = pdf["text"].fillna("").str.lower()

    hit_pref = low.str.findall(pat_pref).map(lambda x: {v for v in x if v in pref})
    hit_syn = (low.str.findall(pat_syn).map(lambda x: {syn[v] for v in x if v in syn})
               if pat_syn is not None else None)
    keep = hit_pref.map(bool).to_numpy()
    n_pref_chunks = int(keep.sum())
    if hit_syn is not None:
        ks = hit_syn.map(bool).to_numpy()
        n_syn_chunks = int(ks.sum())
        keep = keep | ks
    else:
        n_syn_chunks = 0
    print(f"   chunks matching a preferred name: {n_pref_chunks}   "
          f"matching a synonym: {n_syn_chunks}   union: {int(keep.sum())}", flush=True)
    del low

    pdf = pdf.loc[keep].copy()
    pdf["names"] = [(set(a) | set(b if b is not None else ())) for a, b in
                    zip(hit_pref[keep], hit_syn[keep] if hit_syn is not None else
                        [set()] * int(keep.sum()))]
    pdf["names"] = pdf["names"].map(lambda s: tuple(sorted(s)))
    del hit_pref, hit_syn

    occ = collections.defaultdict(lambda: {"chunks": 0, "chunks_any": 0, "papers": set(),
                                           "tissues": collections.Counter(),
                                           "species": collections.Counter(),
                                           "chunks_pref": 0, "chunks_syn": 0})
    gene_cnt = collections.defaultdict(collections.Counter)
    contrast_pairs = collections.Counter()
    n_papers = 0

    for pid, g in pdf.groupby("paper_id", sort=False):
        n_papers += 1
        species = g["species"].fillna("").str.lower().to_numpy()
        tissue = g["tissue"].fillna("").to_numpy()
        tlabs = g["tissue_labels"].to_numpy()
        texts = g["text"].fillna("").to_numpy()
        mgenes = g["marker_genes"].to_numpy()
        gnames = g["names"].to_numpy()
        ctx_cache = {}
        paper_genes = collections.defaultdict(set)
        for i in range(len(g)):
            nm_set = gnames[i]
            if not nm_set:
                continue
            sp_ok = species[i] in ("human", "both")
            tl = tlabs[i]
            tset = set(tl) if tl is not None else set()
            tset.add(tissue[i])
            gs = None
            for nm in nm_set:
                for par in name2parents[nm]:
                    key = (par, nm)
                    ok = ctx_cache.get(key)
                    if ok is None:
                        ok = bool(sp_ok and ((tset & p_tissue_map[par]) or not p_declared[par]))
                        ctx_cache[key] = ok
                    o = occ[key]
                    o["chunks_any"] += 1
                    o["species"][species[i]] += 1
                    if ok:
                        o["chunks"] += 1
                        o["tissues"][tissue[i]] += 1
                        o["papers"].add(str(pid))
                    if gs is None:
                        body = texts[i]
                        gs = {t for t in TOKEN.findall(body) if t in vocab and t not in STOP}
                        mg = mgenes[i]
                        if mg is not None:
                            gs |= {str(x) for x in mg if str(x) in vocab}
                    if ok and gs:
                        paper_genes[key] |= gs
            if len(nm_set) >= 2 and CONTRAST.search(texts[i]):
                contrast_pairs[(str(pid), nm_set)] += 1
        for key, gs in paper_genes.items():
            c = gene_cnt[key]
            for gn in gs:
                c[gn] += 1

    print(f"== S5 aggregated over {n_papers} papers ==", flush=True)

    occ_out = {}
    for (par, nm), o in occ.items():
        occ_out[f"{par}\t{nm}"] = {
            "parent": par, "child": nm,
            "n_chunks_any_context": o["chunks_any"], "n_chunks_in_context": o["chunks"],
            "n_studies_in_context": len(o["papers"]), "papers": sorted(o["papers"]),
            "tissues_in_context": o["tissues"].most_common(),
            "species_any_context": o["species"].most_common()}
    json.dump(occ_out, open(f"{OUT}/S5_occurrence.json", "w"), ensure_ascii=False, indent=1)

    genes_out = {}
    for (par, nm), c in gene_cnt.items():
        pos = {g: n for g, n in c.items() if n >= 2}
        genes_out[f"{par}\t{nm}"] = {"parent": par, "child": nm, "n_genes_seen": len(c),
                                     "n_positive_genes_ge2studies": len(pos), "positive": pos}
    json.dump(genes_out, open(f"{OUT}/S5_genes.json", "w"), ensure_ascii=False, indent=1)

    co = collections.defaultdict(set)
    for (pid, nmset), _ in contrast_pairs.items():
        for a in nmset:
            for b in nmset:
                if a < b:
                    co[f"{a}\t{b}"].add(pid)
    json.dump({k: sorted(v) for k, v in co.items()},
              open(f"{OUT}/S5_contrast_cooccurrence.json", "w"), ensure_ascii=False, indent=1)
    print(f"   occurrence rows={len(occ_out)}  gene rows={len(genes_out)}  "
          f"contrast chunks={len(contrast_pairs)}  contrast pairs={len(co)}", flush=True)
    print("[scan done]", flush=True)


if __name__ == "__main__":
    main()
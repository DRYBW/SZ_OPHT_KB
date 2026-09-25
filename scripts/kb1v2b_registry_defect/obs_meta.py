import h5py, numpy as np, json, collections
P = "/mnt/D/OcularKB/data/HRA000728_tm_cb/HRA000728_tm_cb.h5ad"
f = h5py.File(P, "r")

def dec(g):
    """decode a categorical/string group -> np.array of str"""
    if isinstance(g, h5py.Group):
        cats = g["categories"][:]
        codes = g["codes"][:]
        cats = np.array([c.decode() if isinstance(c, bytes) else str(c) for c in cats])
        out = np.where(codes >= 0, cats[np.clip(codes, 0, None)], "<NA>")
        return out.astype(object)
    v = g[:]
    return np.array([x.decode() if isinstance(x, bytes) else str(x) for x in v], dtype=object)

print("=== uns ===")
for k in f["uns"].keys():
    item = f["uns"][k]
    try:
        v = item[()]
        if isinstance(v, bytes):
            v = v.decode()
        print(f"  {k}: {v!r}")
    except Exception as e:
        print(f"  {k}: <{type(item).__name__} {e}>")

obs = f["obs"]
print("\n=== tissue ===")
tissue = dec(obs["tissue"])
tto = dec(obs["tissue_ontology_term_id"])
study = dec(obs["study"])
donor = dec(obs["donor_id"])
tt = dec(obs["tissue_type"])
for t in sorted(set(tissue)):
    m = tissue == t
    ids = sorted(set(tto[m]))
    st = collections.Counter(study[m])
    dn = len(set(donor[m]))
    print(f"  {t!r} n={m.sum()} donors={dn} onto={ids} tissue_type={sorted(set(tt[m]))} study={dict(st)}")

print("\n=== study ===")
for s in sorted(set(study)):
    print(f"  {s!r} n={(study==s).sum()}")

print("\n=== uvea subset cross-tab ===")
mu = tissue == "uvea"
print("uvea n =", mu.sum(), " donors =", len(set(donor[mu])))
print("  donor_id:", dict(collections.Counter(donor[mu])))
print("  study:", dict(collections.Counter(study[mu])))
print("  tissue_ontology_term_id:", dict(collections.Counter(tto[mu])))
print("  tissue_type:", dict(collections.Counter(tt[mu])))
for k in ["part", "sample_id", "sampleid", "library_id", "fileid", "majorclass", "cell_type",
          "author_cell_type", "disease", "reported_diseases", "donor_age", "sex", "assay",
          "suspension_type", "sample_collection_method", "cell_number_loaded", "tissue_source",
          "is_primary_data"]:
    if k in obs:
        v = dec(obs[k])
        c = collections.Counter(v[mu])
        top = c.most_common(12)
        print(f"  {k} ({len(c)} uniq): {top}")
f.close()

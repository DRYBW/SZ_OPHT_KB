import h5py, numpy as np, collections
P = "/mnt/D/OcularKB/data/HRA000728_tm_cb/HRA000728_tm_cb.h5ad"
f = h5py.File(P, "r")
obs = f["obs"]

def dec(g):
    if isinstance(g, h5py.Group):
        cats = np.array([c.decode() if isinstance(c, bytes) else str(c) for c in g["categories"][:]])
        codes = g["codes"][:]
        return np.where(codes >= 0, cats[np.clip(codes, 0, None)], "<NA>").astype(object)
    v = g[:]
    return np.array([x.decode() if isinstance(x, bytes) else str(x) for x in v], dtype=object)

tissue = dec(obs["tissue"]); sampleid = dec(obs["sampleid"]); donor = dec(obs["donor_id"])
major = dec(obs["majorclass"]); study = dec(obs["study"]); part = dec(obs["part"])

CLASSES = ["Ciliary_Muscle", "CB_PCE", "CB_NPCE", "Fibroblast", "Schwann Cell", "Melanocyte",
           "Immune Cell", "Endothelium", "Pericyte"]

def comp(mask, label):
    n = int(mask.sum())
    c = collections.Counter(major[mask])
    print(f"\n-- {label}  n={n}")
    for cl in CLASSES:
        print(f"     {cl:16s} {c.get(cl,0):8d}  {100.0*c.get(cl,0)/max(n,1):6.2f}%")
    # TM subtypes
    print("     [detail]", collections.Counter(dec(obs['author_cell_type'])[mask]).most_common(20))

print("=========== AGGREGATE ===========")
for t in ["ciliary body", "eye trabecular meshwork", "uvea"]:
    comp(tissue == t, f"tissue={t}")

print("\n=========== PER-SAMPLE: uvea samples vs same-donor other samples ===========")
for s in ["3v31_BCM_23_0574_TM_CB", "3v31_BCM_23_0574_CB_bead",
          "3v31_BCM_23_1169_TM_CB", "3v31_BCM_23_1169_CB_bead",
          "3v31_BCM_23_0792_TM_CB", "3v31_BCM_23_0794-TM_CB", "3v31_BCM_24_0215_TM_CB"]:
    m = sampleid == s
    if m.sum() == 0:
        print("MISSING", s); continue
    comp(m, f"sample={s} tissue={sorted(set(tissue[m]))}")

print("\n=========== donor counts ===========")
print("total donors:", len(set(donor)), " total nuclei:", len(donor))
for t in ["ciliary body", "eye trabecular meshwork", "uvea"]:
    m = tissue == t
    print(f"  {t}: nuclei={m.sum()} donors={len(set(donor[m]))}")
print("  donors with uvea only:", len([d for d in set(donor) if (tissue[donor==d]=='uvea').all()]))
print("  donors with uvea + other:", len([d for d in set(donor) if (tissue[donor==d]=='uvea').any() and not (tissue[donor==d]=='uvea').all()]))

# TM-type vs CB-type in uvea
mu = tissue == "uvea"
aut = dec(obs["author_cell_type"])
TM_TYPES = {"BeamA", "BeamB", "JCT", "TMFibro", "Schlemm_Endothelium"}
CB_TYPES = {"Ciliary_Muscle", "CB_PCE", "CB_NPCE_1", "CB_NPCE_2", "CB_Fibro"}
tm_like = np.isin(aut, list(TM_TYPES))
cb_like = np.isin(aut, list(CB_TYPES))
print("\n=== uvea: TM-type vs CB-type vs other ===")
print("  TM-like:", int((mu & tm_like).sum()), " CB-like:", int((mu & cb_like).sum()),
      " other:", int((mu & ~tm_like & ~cb_like).sum()))
f.close()

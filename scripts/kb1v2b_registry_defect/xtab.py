import h5py, numpy as np, collections, json
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
study = dec(obs["study"]); part = dec(obs["part"]); major = dec(obs["majorclass"])
author = dec(obs["author_cell_type"]); celltype = dec(obs["cell_type"])

print("=== sampleid x tissue (all 3 tissues) ===")
samples = sorted(set(sampleid))
print(f"{'sampleid':40s} {'ciliary body':>13s} {'TM':>13s} {'uvea':>13s}  donor  study")
for s in samples:
    m = sampleid == s
    cb = int(((tissue == "ciliary body") & m).sum())
    tm = int(((tissue == "eye trabecular meshwork") & m).sum())
    uv = int(((tissue == "uvea") & m).sum())
    dn = sorted(set(donor[m]))
    st = sorted(set(study[m]))
    print(f"{s:40s} {cb:13d} {tm:13d} {uv:13d}  {','.join(dn):22s} {','.join(st)}")
print("\n n_samples:", len(samples))

print("\n=== donor x tissue (uvea donors only) ===")
uvd = sorted(set(donor[tissue == "uvea"]))
for d in uvd:
    m = donor == d
    print(f"  {d}: total={m.sum()} cb={(tissue[m]=='ciliary body').sum()} tm={(tissue[m]=='eye trabecular meshwork').sum()} uvea={(tissue[m]=='uvea').sum()} samples={sorted(set(sampleid[m]))}")

print("\n=== part x tissue (counts) ===")
parts = sorted(set(part))
print(f"{'part':16s} {'ciliary body':>13s} {'TM':>13s} {'uvea':>13s}")
for p in parts:
    m = part == p
    print(f"{p:16s} {int(((tissue=='ciliary body')&m).sum()):13d} {int(((tissue=='eye trabecular meshwork')&m).sum()):13d} {int(((tissue=='uvea')&m).sum()):13d}")

print("\n=== uvea: majorclass x author_cell_type (full) ===")
mu = tissue == "uvea"
for (mj, ac), n in sorted(collections.Counter(zip(major[mu], author[mu])).items(), key=lambda x: -x[1]):
    print(f"  {n:6d}  {mj:22s} <- {ac}")

print("\n=== uvea: donor x majorclass ===")
for d in uvd:
    m = (donor == d) & mu
    c = collections.Counter(major[m])
    print(f"  {d} (n={m.sum()}): {c.most_common()}")

print("\n=== uvea: cell_type full counts ===")
print(collections.Counter(celltype[mu]).most_common())

print("\n=== uvea: library_id_repository / reference_genome / alignment ===")
for k in ["library_id_repository", "reference_genome", "alignment_software", "gene_annotation_version",
          "institute", "intronic_reads_counted", "sequenced_fragment", "donor_cause_of_death",
          "donor_living_at_sample_collection", "sample_preservation_method", "suspension_derivation_process",
          "suspension_dissociation_reagent", "tissue_handling_interval"]:
    if k in obs:
        v = dec(obs[k]); print(f"  {k}: {collections.Counter(v[mu]).most_common(6)}")
f.close()

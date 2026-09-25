import h5py, sys, numpy as np
P = "/mnt/D/OcularKB/data/HRA000728_tm_cb/HRA000728_tm_cb.h5ad"
f = h5py.File(P, "r")
print("== root keys ==", list(f.keys()))
obs = f["obs"]
print("== obs keys ==")
for k in obs.keys():
    g = obs[k]
    cls = g.attrs.get("_index", None)
    enc = g.attrs.get("encoding-type", b"")
    print("  ", k, "|", g.__class__.__name__, "| encoding=", enc, "| index=", cls)
print("== var keys ==", list(f["var"].keys()))
print("== uns keys ==", list(f["uns"].keys()))
print("n_obs =", obs.attrs.get("_index", None), f["obs"][list(obs.keys())[0]].shape)

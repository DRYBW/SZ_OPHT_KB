"""t_7898fde9 报告数字自检 — 逐条重算 kb1v2b_registry_defect_hasa_uvea_20260923.md 的台面数字。
只读。输出 PASS/FAIL 逐条。"""
import h5py, numpy as np, collections, json, os, hashlib

P = "/mnt/D/OcularKB/data/HRA000728_tm_cb/HRA000728_tm_cb.h5ad"
R = []
def chk(name, got, want):
    ok = (got == want)
    R.append((ok, name, got, want))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got={got} want={want}")

f = h5py.File(P, "r")
obs = f["obs"]

def dec(g):
    if isinstance(g, h5py.Group):
        cats = np.array([c.decode() if isinstance(c, bytes) else str(c) for c in g["categories"][:]])
        codes = g["codes"][:]
        return np.where(codes >= 0, cats[np.clip(codes, 0, None)], "<NA>").astype(object)
    return np.array([x.decode() if isinstance(x, bytes) else str(x) for x in g[:]], dtype=object)

tissue = dec(obs["tissue"]); study = dec(obs["study"]); donor = dec(obs["donor_id"])
major = dec(obs["majorclass"]); aut = dec(obs["author_cell_type"])
celltype = dec(obs["cell_type"]); sampleid = dec(obs["sampleid"])

# --- 规模 ---
chk("n_obs", len(study), 1102250)
chk("obs 列数(不含_index)", len([k for k in obs.keys() if k != "_index"]), 50)
chk("tissue: ciliary body", int((tissue == "ciliary body").sum()), 863922)
chk("tissue: eye trabecular meshwork", int((tissue == "eye trabecular meshwork").sum()), 184922)
chk("tissue: uvea", int((tissue == "uvea").sum()), 53406)
chk("tissue 三类和 == n_obs", int((tissue == "ciliary body").sum() + (tissue == "eye trabecular meshwork").sum() + (tissue == "uvea").sum()), 1102250)
chk("study: chen_tm_cb", int((study == "chen_tm_cb").sum()), 1044541)
chk("study: sanes_GSE199013", int((study == "sanes_GSE199013").sum()), 57709)
chk("donors total", len(set(donor)), 70)
chk("donors ciliary body", len(set(donor[tissue == "ciliary body"])), 59)
chk("donors TM", len(set(donor[tissue == "eye trabecular meshwork"])), 25)
chk("donors uvea", len(set(donor[tissue == "uvea"])), 5)
chk("majorclass 词表", len(set(major)), 9)
chk("cell_type 词表", len(set(celltype)), 15)

# --- uvea 切片 ---
mu = tissue == "uvea"
chk("uvea: 100% chen_tm_cb", int((study[mu] == "chen_tm_cb").sum()), 53406)
chk("uvea: sanes 贡献 0", int((study[mu] == "sanes_GSE199013").sum()), 0)
chk("uvea 文库数", len(set(sampleid[mu])), 5)
uv_samples = sorted(set(sampleid[mu]))
chk("uvea 文库名全含 _TM_CB", all("TM_CB" in s for s in uv_samples), True)
chk("uvea 供者数", len(set(donor[mu])), 5)

C = collections.Counter(major[mu])
CA = collections.Counter(aut[mu])
chk("uvea Ciliary_Muscle", CA["Ciliary_Muscle"], 19422)
chk("uvea CB_Fibro", CA["CB_Fibro"], 10963)
# author_cell_type 词表里没有 "TMFibro" 这个值 —— TM 型成纤维被拆成 BeamA/BeamB/JCT；
# part 列层级的 TMFibro = BeamA+JCT+BeamB
chk("uvea author_cell_type 无 TMFibro 值", CA["TMFibro"], 0)
chk("uvea part=TMFibro", collections.Counter(dec(obs["part"])[mu])["TMFibro"], 7153)
chk("uvea author_cell_type 中 TMFibro/Beam 系", sum(CA[k] for k in ["BeamA", "BeamB", "JCT"]), 3516 + 1035 + 2602)
chk("uvea Schwann Cell", C["Schwann Cell"], 6339)
chk("uvea Melanocyte", C["Melanocyte"], 4835)
chk("uvea Immune Cell", C["Immune Cell"], 3235)
chk("uvea Endothelium", C["Endothelium"], 888)
chk("uvea CB_PCE", C["CB_PCE"], 318)
chk("uvea CB_NPCE", C["CB_NPCE"], 19)
chk("uvea Pericyte", C["Pericyte"], 234)
chk("uvea Schlemm_Endothelium", CA["Schlemm_Endothelium"], 7)
chk("uvea Vascular_Endothelium", CA["Vascular_Endothelium"], 881)

TM_TYPES = {"BeamA", "BeamB", "JCT", "TMFibro", "Schlemm_Endothelium"}
CB_TYPES = {"Ciliary_Muscle", "CB_PCE", "CB_NPCE_1", "CB_NPCE_2", "CB_Fibro"}
tmm = np.isin(aut, list(TM_TYPES)); cbm = np.isin(aut, list(CB_TYPES))
chk("uvea TM 型", int((mu & tmm).sum()), 7160)
chk("uvea CB 型", int((mu & cbm).sum()), 30722)
chk("uvea 其他", int((mu & ~tmm & ~cbm).sum()), 15524)
chk("uvea TM+CB+其他 == 53406", int((mu & tmm).sum() + (mu & cbm).sum() + (mu & ~tmm & ~cbm).sum()), 53406)
# uvea 内的 TM 型成纤维：author_cell_type 拆分为 BeamA/BeamB/JCT（无 TMFibro 值）
chk("uvea BeamA+JCT+BeamB", sum(CA[k] for k in ["BeamA", "JCT", "BeamB"]), 7153)

# --- 同供者 CB 文库对照 ---
def epi(s):
    m = sampleid == s
    return int((aut[m] == "CB_PCE").sum() + (aut[m] == "CB_NPCE_1").sum() + (aut[m] == "CB_NPCE_2").sum()), int(m.sum())
e1, n1 = epi("3v31_BCM_23_0574_CB_bead"); chk("0574 CB_bead 上皮占比%", round(100 * e1 / n1, 2), 48.74)
e2, n2 = epi("3v31_BCM_23_0574_TM_CB");   chk("0574 TM_CB 上皮占比%", round(100 * e2 / n2, 2), 0.0)
e3, n3 = epi("3v31_BCM_23_1169_CB_bead"); chk("1169 CB_bead 上皮占比%", round(100 * e3 / n3, 2), 71.36)
e4, n4 = epi("3v31_BCM_23_1169_TM_CB");   chk("1169 TM_CB 上皮占比%", round(100 * e4 / n4, 2), 1.62)
chk("0574 CB_bead n", n1, 38633); chk("0574 TM_CB n", n2, 16795)
chk("1169 CB_bead n", n3, 16835); chk("1169 TM_CB n", n4, 8955)

# --- sanes 层样本 ---
ms = study == "sanes_GSE199013"
chk("sanes 样本数", len(set(sampleid[ms])), 9)
chk("sanes 核数", int(ms.sum()), 57709)
chk("sanes tissue 只有 CB/TM", sorted(set(tissue[ms])), ["ciliary body", "eye trabecular meshwork"])

# --- 文件锚定 ---
st = os.stat(P)
chk("file size", st.st_size, 9663215939)
chk("sha256", hashlib.sha256(open(P, "rb").read()).hexdigest(),
    "827d640de274423537ebbad9181ed2cc333a74664cf57647b77206020ecad21d")
f.close()

# --- 登记层假阴性 ---
d = json.load(open("/mnt/D/OcularKB/registry/E2_final_integrity_audit_precutoff_20260905.json"))
chk("E2 rows", len(d["rows"]), 66)
chk("E2 MISSING_LOCAL 行数", sum(1 for e in d["rows"] if e["verdict"] == "MISSING_LOCAL"), 4)
chk("E2 其中 HRA 假阴性", sum(1 for e in d["rows"] if e["verdict"] == "MISSING_LOCAL" and e["accession"].startswith("HRA")), 2)
chk("registry_reconciled HRA in_local=False", 
    [l.split(",")[1] for l in open("/mnt/D/OcularKB/registry/registry_reconciled_20260831.csv") if l.startswith("HRA")], ["False", "False"])
chk("e1 正则不含 HRA", "HRA" in open("/mnt/D/OcularKB/scripts/e1_registry_reconcile.py").read().split("\n")[10], False)

npass = sum(1 for ok, *_ in R if ok)
print(f"\n=== {npass}/{len(R)} PASS ===")
if npass != len(R):
    print("FAILED:", [(n, g, w) for ok, n, g, w in R if not ok])

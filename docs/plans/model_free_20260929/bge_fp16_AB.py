#!/usr/bin/env python3
"""bge fp32->fp16 量化 A/B: 转半精度权重, 跑黄金41, 逐位对比 fp32 基线。
过门=可上传半量版; 不过=维持 fp32。"""
import json, os, importlib.util, subprocess, sys

SRC = "/mnt/D/OcularKB/models/bge-large-en-v1.5"
DST = "/home/ubuntu/models_bge_fp16/bge-large-en-v1.5"
os.makedirs(DST, exist_ok=True)

# 1) copy small configs
for f in os.listdir(SRC):
    if f != "model.safetensors" and os.path.isfile(os.path.join(SRC, f)):
        subprocess.run(["cp", os.path.join(SRC, f), os.path.join(DST, f)])
for d in ("1_Pooling",):
    if os.path.isdir(os.path.join(SRC, d)):
        subprocess.run(["cp", "-r", os.path.join(SRC, d), DST])
# config.json 声明 float16, 防 transformers 升回 fp32
cfg = json.load(open(os.path.join(DST, "config.json")))
cfg["torch_dtype"] = "float16"
json.dump(cfg, open(os.path.join(DST, "config.json"), "w"), indent=2)

# 2) convert weights
from safetensors.torch import load_file, save_file
import torch
t = load_file(os.path.join(SRC, "model.safetensors"))
t16 = {k: v.half() for k, v in t.items()}
save_file(t16, os.path.join(DST, "model.safetensors"))
sz32 = os.path.getsize(os.path.join(SRC, "model.safetensors")) / 1e6
sz16 = os.path.getsize(os.path.join(DST, "model.safetensors")) / 1e6
print(f"weights MB fp32={sz32:.0f} -> fp16={sz16:.0f}")
sys.stdout.flush()

# 3) golden 41 under fp16 model
spec = importlib.util.spec_from_file_location(
    "s3", "/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928/clients/ocularkb/rag/scripts/stage3_retrieve.py")
s3 = importlib.util.module_from_spec(spec)
os.environ["EYEKB_MODEL_DIR"] = DST
spec.loader.exec_module(s3)
exp = json.load(open("/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928/tests/REPRO_EXPECTED.json"))["results"]
mis = []
for i, c in enumerate(exp):
    r = s3.retrieve(c["cell_type"], species=c.get("species"), top_k=5,
                    tissue=c.get("tissue"),
                    db_dir="/home/ubuntu/RAG_SLIM_V242/literature_db/v2.4.2_2026-09_slim")
    got = [x["pmid"] for x in r["results"]]
    if got != c["top_pmids"]:
        mis.append({"i": i, "ct": c["cell_type"], "exp": c["top_pmids"], "got": got})
    if i % 10 == 0:
        print(f"...{i}/41"); sys.stdout.flush()
print(json.dumps({"fp16_model_overlap_pass": len(exp) - len(mis), "of": len(exp),
                  "mismatch_first5": mis[:5]}, ensure_ascii=False, indent=1))

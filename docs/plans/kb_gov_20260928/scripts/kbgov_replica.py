#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kbgov_replica.py — 实验侧复刻 eyekb_core.query_marker(genes-mode) v1.0 语义。
禁 import 生产码（kb_gov_20260928/KBGOV_PREREG_v1.0.md §2）：本文件为独立重写，
语义逐点对照 /mnt/D/EyeKB/mcp_server/eyekb_core.py（只读，sha 在 PRE 台账）：
  1) 库装载序 retina→membrane→retina_interneuron→retina_v6→face_v6（v6 激活态）；
     face_v6 无 markers 顶层键时由 stromal_repair/face_increment.core 归一派生（同生产原文）。
  2) 类名 upper 冲突消歧：首现保正名，后续 `库名::类名` 别名。
  3) 输入 strip().upper()，保留重复（生产 sum(1 for g in gl ...) 对重复基因双计）。
  4) n_shared = Σ[gl 中基因 ∈ 类面板]；n=0 不进；排序 = 按 -n_shared 稳定排序（同分保插入序）。
不含 soft_flags 注记层（calllog 留痕证明不改排序）。"""
import json
import re

KB = "/mnt/D/EyeKB/kb/markers"
# 与生产 MARKER_LIBS 同路径（只读消费）
LIB_ORDER = [
    ("retina", f"{KB}/markers_v4.1_clean.json"),
    ("membrane", f"{KB}/markers_membrane_v1.json"),
    ("retina_interneuron", f"{KB}/markers_v5_retina_interneuron.json"),
    ("retina_v6", f"{KB}/markers_v6_retina_repair.json"),
    ("face_v6", f"{KB}/markers_v6_face_increment.json"),
]


def _face_v6_derived(db):
    derived = {}
    for src in ("stromal_repair", "face_increment"):
        for cls, e in (db.get(src) or {}).items():
            derived[cls] = [str(x.get("gene", "")).strip().upper()
                            for x in (e.get("core") or [])
                            if isinstance(x, dict) and x.get("gene")]
    return derived


def load_markers(library="all"):
    """返回 (markers: dict[显示类名 -> [GENE,...]], owner: dict[类名 -> 路径]) —
    与生产 query_marker 装配段逐行同构（library 仅支持 all=现库激活态）。"""
    assert library == "all", "本卡口径=A 现库（library=all, v6 激活态）"
    markers, owner, seen_upper = {}, {}, {}
    for name, path in LIB_ORDER:
        db = json.load(open(path, encoding="utf-8"))
        if name == "face_v6" and "markers" not in db:
            db["markers"] = _face_v6_derived(db)
        for ct, gs in (db.get("markers") or {}).items():
            up = ct.upper()
            if up in seen_upper:
                alt = f"{name}::{ct}"
                markers[alt] = [g.upper() for g in gs]
                owner[alt] = path
                continue
            markers[ct] = [g.upper() for g in gs]
            owner[ct] = path
            seen_upper[up] = ct
    return markers, owner


def rank_genes(genes, markers=None, owner=None):
    """复刻 query_marker genes-mode 的 ranking 装配：返回有序 [(类名, n_shared, shared_genes)]。"""
    if markers is None:
        markers, owner = load_markers()
    if isinstance(genes, str):
        gl = [g.strip().upper() for g in genes.replace(",", " ").split() if g.strip()]
    else:
        gl = [str(g).strip().upper() for g in genes if str(g).strip()]
    score = {}
    for ct in markers:
        n = sum(1 for g in gl if g in markers[ct])
        if n:
            score[ct] = {"n_shared": n, "shared_genes": [g for g in gl if g in markers[ct]]}
    ranked = sorted(score.items(), key=lambda kv: -kv[1]["n_shared"])
    return [(c, s["n_shared"], s["shared_genes"]) for c, s in ranked], gl


if __name__ == "__main__":
    mk, ow = load_markers()
    r, gl = rank_genes(["Grin3a", "Calb2", "Kcnip4", "Galntl6", "Rbfox1", "Sncg",
                        "Thy1", "Lrrc4c", "Kcnd2", "Tshz2", "Tafa1", "Nrn1", "Csmd3",
                        "Rprm", "Stmn2", "Pvalb", "Atp1b1", "Lingo2", "Nefm"], mk, ow)
    print("classes loaded:", len(mk))
    print("selftest Q7::52 seat-A:", [c for c, n, s in r])
    # 期望 [Pericyte, Fibroblast, retina_interneuron::AC, retina_v6::AC]

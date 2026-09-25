#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB1v2-W5: vk 文献索引页 ↔ 判读层四向链接 (幂等追加, 页面带版本号)

四向 = 疾病条目 ↔ 组成基线 ↔ RAG reason-tag(evidence_meta sidecar) ↔ 文献索引页。
Astra T5: 仅文献链接不足以审计 → 每页链接到稳定概念 ID / 条目文件 / sidecar 字段路径。
"""
import re
from pathlib import Path

VK = Path("/mnt/D/EyeKB/kb/vk_literature_index")
MARK = "<!-- KB1V2-WIKILINKS v1.1 -->"
VER = "判读层链接版本: KB1v2 (2026-09-23, t_16c3e020)"

TISSUE_BASELINE = {  # vk 组织页 → kb/baselines 文件
    "cornea": "ocular_surface", "conjunctiva": "conjunctiva", "sclera": "sclera",
    "RPE": "RPE", "choroid": "choroid", "ciliary_body": "ciliary_body",
    "iris": "iris", "lens": "lens", "optic_nerve": "optic_nerve",
    "trabecular_meshwork": "trabecular_meshwork",
}
TOPIC_HINT = {
    "dr-diabetic-retinopathy": "疾病矩阵: kb/priors/disease/_DISEASE_TISSUE_MATRIX.md; "
                               "示例格: PDR__fibrovascular_membrane.md",
    "vascular": "疾病矩阵 PDR 格 patho_endothelial 签名 (signature_evidence_T4)",
    "glial-microglia": "概念表 EYEKBC-0001/0011/0012 (来源判定封顶=转录相似, Astra T4)",
    "amd": "疾病矩阵 nAMD/GA 行 (placeholder)", "glaucoma": "疾病矩阵 glaucoma 行 (placeholder)",
    "inherited-disease": "疾病矩阵 (无格; 最小可用标准把关)",
    "metabolism": "签名层 metabolic 相关走 evidence_context.methods",
    "methods-scrna": "注释协议 ANNOTATION_PROTOCOL_v1.1.md + EVAL_Rubric_v1.md",
    "photoreceptor": "视网膜基线 kb/baselines/retina.md (Rod/Cone 供者级分布)",
    "retina-development": "视网膜基线 caveat 4 (发育/类器官不适用成体基线)",
    "regeneration": "概念表 EYEKBC-0009/0011", "rpe": "基线 RPE 骨架 + 视网膜基线 RPE 混入旗",
    "aging": "视网膜基线 (供者老年段为主)", "models": "取样材料错配警示 (示例格 §)",
    "other": "", "visual-function": "",
}


def block_for(name: str) -> str:
    base = TISSUE_BASELINE.get(name)
    lines = ["", "---", MARK, f"## 判读层链接 ({VER})", ""]
    if base:
        lines.append(f"- **组成基线**: [kb/baselines/{base}.md](/mnt/D/EyeKB/kb/baselines/{base}.md)"
                     f" — 供者级条件参考分布 (锚定 registry 标准集或 t_6f5cc731 映射)")
    hint = TOPIC_HINT.get(name)
    if hint:
        lines.append(f"- **判读层锚**: {hint}")
    lines += [
        "- **RAG reason-tag**: 每条 PMID 的入库原因/论断关系/证据条件见 "
        "`/mnt/D/EyeKB/kb/literature_db/evidence_meta_v2.0_2026-09.jsonl` "
        "(键=pmid; 字段 inclusion_reasons / claim_relation / evidence_context / verification_status); "
        "MCP `search_literature` 命中自动联表带出",
        "- **概念 ID 映射**: `/mnt/D/EyeKB/kb/priors/concepts.tsv`",
        "- 红线: 本页与全部链接内容仅证据引用与 QC 旗, 禁入打分 (ANNOTATION_PROTOCOL_v1.1.md §0)",
        ""]
    return "\n".join(lines)


def main():
    n_new = n_skip = 0
    for p in sorted(VK.glob("*.md")):
        txt = p.read_text(encoding="utf-8")
        if MARK in txt:
            n_skip += 1
            continue
        name = re.sub(r"^(tissue-|topic-)", "", p.stem)
        p.write_text(txt.rstrip() + "\n" + block_for(name), encoding="utf-8")
        n_new += 1
    print("vk pages linked:", n_new, "| already had links (skipped):", n_skip)


if __name__ == "__main__":
    main()

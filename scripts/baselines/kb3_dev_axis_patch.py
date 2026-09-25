#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB3 (t_5425a7ca) W1: 组成基线发育轴单列 —— 现件回填补丁。

对 kb/baselines/ 的 11 条成人档基线 + 1 条转换态概念条目:
  JSON: 追加 development_stage (必填, 5 值枚举) + development_stage_prohibition
        + kb3_card (+ unknown 条的 kb3_applicable_stage_at_backfill);
  MD:   文件头加 "KB3 发育档" 行 (适用阶段写死);
        filled 条的 "## 主参考/对照档" 参考分布段加禁令一行。
  索引 baselines.json: 每条 entries 记录加 development_stage + kb3_note。
纪律: additive-only —— 零改现有字段值; identity_signature/sha 均只覆盖子树
(json.dumps sort_keys) 不受顶层加键影响。常量从 build_baselines.py 导入
(单一真源, 未来 main() 重渲染输出与本次回填一致)。
用法: python3 kb3_dev_axis_patch.py [--dry]
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_baselines import (KB3_CARD, KB3_PROHIBITION, KB3_DEV_ENUM,  # noqa: E402
                             kb3_dev_stage, kb3_applicable_note)

KB = Path("/mnt/D/EyeKB/kb/baselines")
TISSUES = ["retina", "ocular_surface", "optic_nerve", "trabecular_meshwork",
           "ciliary_body", "RPE", "choroid", "conjunctiva", "iris", "lens", "sclera"]
DRY = "--dry" in sys.argv


def patch_json(p: Path, e: dict):
    changed = False
    want = {"development_stage": kb3_dev_stage(e),
            "development_stage_prohibition": KB3_PROHIBITION,
            "kb3_card": KB3_CARD}
    na = kb3_applicable_note(e)
    if na:
        want["kb3_applicable_stage_at_backfill"] = na
    assert want["development_stage"] in KB3_DEV_ENUM
    for k, v in want.items():
        if e.get(k) != v:
            e[k] = v
            changed = True
    if changed and not DRY:
        p.write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
    return changed, want["development_stage"]


HDR_RE = re.compile(r"^> schema: `eyekb-baseline/1\.1`.*$")
MAIN_RES_RE = re.compile(r"^## (主参考|.*条件参考分布).*")  # filled 参考分布段
STRAT_RE = re.compile(r"^### 层: ")


def patch_md(p: Path, e: dict):
    text = p.read_text(encoding="utf-8")
    if "KB3 发育档" in text:
        return False
    dev = kb3_dev_stage(e)
    na = kb3_applicable_note(e)
    hdr = (f"> **KB3 发育档 (卡片 {KB3_CARD})**: development_stage=**{dev}**"
           + (f" | 适用档(回填时写死): {na.split(' ——')[0]}" if na else "")
           + f" —— {KB3_PROHIBITION}")
    lines = text.split("\n")
    out, inserted = [], False
    for i, ln in enumerate(lines):
        if not inserted and HDR_RE.match(ln):
            out.append(ln)
            out.append(hdr)
            inserted = True
            continue
        out.append(ln)
    # 参考分布段禁令行: filled=主参考标题后插一行; skeleton=主参考不存在, 头行已含禁令
    if inserted and e.get("status") == "filled_donor_level":
        txt2 = "\n".join(out)
        if "⚠ " + KB3_PROHIBITION not in txt2:
            def _ins(m):
                return m.group(0) + "\n> ⚠ " + KB3_PROHIBITION
            txt2 = re.sub(MAIN_RES_RE, _ins, txt2, count=1)
            out = txt2.split("\n")
    assert inserted, f"{p}: 头行未命中 (格式漂移?)"
    if not DRY:
        p.write_text("\n".join(out), encoding="utf-8")
    return True


def patch_concept():
    pj = KB / "fetal_development_transitions.json"
    d = json.loads(pj.read_text(encoding="utf-8"))
    changed = False
    if "development_stage" not in d:
        d["development_stage"] = "fetal_developing"
        d["development_stage_prohibition"] = KB3_PROHIBITION
        d["kb3_card"] = KB3_CARD
        changed = True
    # KB3 锚点核实表 (additive; candidates 原字段不动, stale 的 local 标记在此纠正)
    av = {
        "generated": "2026-09-24", "card": KB3_CARD,
        "method": "盘上 find + 文件内容实测 + registry (ocular_public_datasets_verified_v1.csv, "
                  "ocularkb_ingest_registry_20260818.csv) 交叉核对",
        "anchors": [
            {"acc": "GSE268630", "verdict": "AVAILABLE_WITH_LABELS",
             "evidence": "/mnt/D/OcularKB/data/GSE268630/gse268630_cellxgene.h5ad (226,506 细胞, "
                         "portal 注释含 majorclass/subclass/development_stage/donor_id); "
                         "GSM 面 25 单样本矩阵在盘",
             "identity_note": "候选条 desc='multiome ~22万核' 与 portal 面一致; "
                              "KB3 发育条目实采 portal 转录组注释"},
            {"acc": "GSE234963", "verdict": "AVAILABLE_NO_PUBLISHED_LABELS",
             "evidence": "24×h5ad @ /mnt/D/OcularKB/data/backlog_h5ad/ (obs 列=空, 无标签) + "
                         "RAW.tar @ data/GSE234963/; registry OA-D009: 'Human fetal retinal "
                         "progenitor scRNA-seq', Fetal ~7.5-21 PCW, 24 samples/13 时间点, "
                         "'no standalone GEO label file confirmed'",
             "identity_note": "候选条 desc='类器官集' 系 KB2c 笔误 —— registry 权威行=胎 RPC "
                              "(与任务书'人胎 RPC 24 样本'一致); 无公开标签 → 只立数据卡不实算"},
            {"acc": "GSE138002", "verdict": "AVAILABLE_MIXED_CONTENT",
             "evidence": "data/GSE138002/ 4×suppl (mtx/barcodes/genes); Final_barcodes.csv.gz "
                         "118,555 细胞含 umap2_CellType 标签; 样本面=Hgw9-27 胎网 + Hpnd8 新生 + "
                         "Adult 对照 + 24-59_Day 类器官",
             "identity_note": "候选条 desc='视网膜类器官' 不完整 —— registry OA-D010 权威标题 "
                              "'developing human retina AND retinal organoids'; 任务书 '(GW9-19)' "
                              "实测胎网面到 GW27; 混内容必须按样本级拆层, Adult/类器官段不进发育条目"}],
        "kb3_outcome": "retina__fetal_developing 独立条目已建 (GSE268630 + GSE138002 标签聚合); "
                       "GSE234963 数据卡在条目内、组成待 fetal 管线回填。"}
    if "kb3_anchor_verification" not in d:
        d["kb3_anchor_verification"] = av
        changed = True
    if changed and not DRY:
        pj.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    # 概念条 MD: 头行 + 锚点核实段
    pm = KB / "fetal_development_transitions.md"
    if pm.is_file():
        t = pm.read_text(encoding="utf-8")
        if "KB3 锚点核实" not in t:
            add = ["", "## KB3 锚点核实 (卡片 t_5425a7ca, 2026-09-24)", "",
                   "> development_stage=**fetal_developing** —— " + KB3_PROHIBITION, ""]
            for a in av["anchors"]:
                add.append(f"- **{a['acc']}** = {a['verdict']}: {a['evidence']}")
                add.append(f"  - 身份纠正: {a['identity_note']}")
            add += ["", "结果: retina__fetal_developing 已独立立条目 (GSE268630+GSE138002 标签聚合); "
                        "GSE234963 只立数据卡。candidates 原数组不动 (逐行口径以本段为准)。", ""]
            if not DRY:
                pm.write_text(t.rstrip("\n") + "\n" + "\n".join(add), encoding="utf-8")
    return True


def patch_index():
    pj = KB / "baselines.json"
    d = json.loads(pj.read_text(encoding="utf-8"))
    changed = False
    for x in d["entries"]:  # 11 条成人档数组不动长度 (回归锁)
        if "development_stage" not in x:
            fp = KB / (x["file"].replace(".md", ".json"))
            e = json.loads(fp.read_text(encoding="utf-8"))
            # dry-run 时现件尚未回填 → 用生成器同一判定函数推导 (真跑时读到已写入值)
            x["development_stage"] = e.get("development_stage") or kb3_dev_stage(e)
            changed = True
    if "kb3_note" not in d:
        d["kb3_note"] = ("KB3 发育轴全量单列 (t_5425a7ca): entries 数组=11 条成人档不变; "
                         "发育期独立条目登记于 development_entries (schema "
                         "eyekb-baseline-development/1.0, MCP 成人查询不可见)。")
        changed = True
    if changed and not DRY:
        pj.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    return changed


def main():
    n = 0
    for t in TISSUES:
        pj, pm = KB / f"{t}.json", KB / f"{t}.md"
        e = json.loads(pj.read_text(encoding="utf-8"))
        cj, dev = patch_json(pj, e)
        cm = patch_md(pm, e) if pm.is_file() else False
        n += cj + cm
        print(f"{t:20s} development_stage={dev:8s} json:{'PATCHED' if cj else 'ok'} "
              f"md:{'PATCHED' if cm else 'ok'}")
    patch_concept()
    patch_index()
    print(("DRY-RUN" if DRY else "DONE") + f"; files touched this run ≈ {n} (+concept/index)")


if __name__ == "__main__":
    main()

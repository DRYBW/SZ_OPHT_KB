#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB 物种路由解析层 —— L1 知识面权威入口件 + L5 门控面判据落地。

卡 t_b9952795 (W2) ｜ 判据唯一权威源 = plans/x10_improve_20261012/W2_SPROUTE/SPEC_SPECIES_ROUTING.md
（本件禁自设阈值/证据族/优先级；改判据 → 先出新版 SPEC，再改本件常量）。

═══════════ 缺陷背景（一行为可复算）═══════════
生产码 eyekb_core._kbgov_g1_tier 以「大小写惯例 title_frac」为**必要条件**：
    if tf < T: return "human_assumed"        # ← msp/m_only 两个大小写不敏感信号被短路绕过
上游 stage_a 已把基因符号统一大写 → tf ≡ 0 → 鼠卷（X9A）64/64 簇判 human_assumed，
B5 鼠拒答路径从未触发（X10-D CANDIDATE_WIRING_DIAGNOSIS §2.5）。

═══════════ 本层做什么（SPEC §2/§3）═══════════
三源优先级，严格短路、低优先源不得覆盖高优先源：
    S1 显式参数 species=human|mouse
    S2 卷元数据 volume_species=… 或 volume_id → 卷物种登记表
    S3 符号形态（证据族 E1/E2/E3 + 大小写惯例降级为辅助档）
三源皆无可判证据 → route="undetermined" + 显式旗标（**不得静默假定 human**）。

═══════════ 逃生门（SPEC §6.1，opt-in 反相，特此登记）═══════════
env EYEKB_SPECIES_ROUTE ∈ {1,true,on,yes}（strip+casefold）= ON；未设/空/其它 = OFF = 接线前
逐字节全态（本件不被调用，调用方走 legacy）。反相理由：本层给响应**新增键**=信息契约 I 变更，
确认期（IMPROVE_WAVE_X10_PLAN_v0.2 §1.5）只允许 D 版本变动，故默认不上电；翻档到期日 2026-10-19。
"""
from __future__ import annotations

import gzip
import json
import os
import re
import sys
from pathlib import Path

SPEC_VERSION = "spec-route-v1.0"
SPEC_SEQ = 1  # 与 CHANGELOG 序号对齐（SPECIES_ROUTE_CHANGELOG.md）

EYEKB_ROOT = Path(__file__).resolve().parents[1]              # /mnt/D/EyeKB
KBGOV_VOCAB = Path(__file__).resolve().parent / "kbgov_vocab.json.gz"   # 只读, 零字节改动
REGISTRY = EYEKB_ROOT / "kb" / "species_route" / "VOLUME_SPECIES_REGISTRY_v1.tsv"

# ---- 冻结判定常量（逐字对应 SPEC §3；改值=改预注册，禁）----
T_FROZEN = 0.4          # 大小写惯例辅助档阈值（沿用 B5 冻结值）
E3_QUORUM = 2           # E3 弱证据配额门（SPEC §3.2）
AMBIG = frozenset({"GLUL", "VIM", "CLU"})   # B5-G3 冻结锚集（逐字一致；ON 路径原样保留 G3 标注）
_RE_GM = re.compile(r"^GM\d+$")
_RE_RIK = re.compile(r"RIK$")
# 假阳性防火墙：跨物种共享符号族（线粒体/核糖体/RNA 类）——校准资产 33/33 人源假阳性全在此族
_RE_AMBIG = re.compile(r"^MT[-0-9]|^MT$|^RPL\d|^RPS\d|^MRPL\d|^MRPS\d|^RNA|^TRNA|^SNOR|^SCARNA")
_RE_LETTER = re.compile(r"[A-Za-z]")
_RE_TITLE = re.compile(r"^[A-Z][a-z]")

_ROUTES = ("human", "mouse", "undetermined")
_SOURCES = ("explicit_param", "volume_metadata", "symbol_morphology", "unresolved")

_cache = {"sig": None, "voc": None, "warned": False, "reg_sig": None, "reg": None}


# ---------------------------------------------------------------- 门与装载
def enabled() -> bool:
    """逃生门（SPEC §6.1）：∈{1,true,on,yes} = ON；未设/空/其它 = OFF（反相 opt-in）。"""
    v = (os.environ.get("EYEKB_SPECIES_ROUTE") or "").strip().casefold()
    return v in {"1", "true", "on", "yes"}


def _norm_species(v):
    """归一 species/volume_species 取值；无法识别 → None（视为未提供）。"""
    s = (str(v) if v is not None else "").strip().casefold()
    if s in ("human", "homo_sapiens", "hs", "人"):
        return "human"
    if s in ("mouse", "mus_musculus", "mm", "鼠", "小鼠"):
        return "mouse"
    return None


def _vocab():
    """惰性加载冻结词表（hum/m_up/m_raw/h2m，全部按 upper 归一）。缺件/坏件 → None（fail-soft）。"""
    st = _cache
    try:
        p = KBGOV_VOCAB.stat()
        sig = (p.st_mtime_ns, p.st_size)
    except OSError:
        sig = None
    if sig is not None and st["sig"] == sig and st["voc"] is not None:
        return st["voc"]
    try:
        with gzip.open(KBGOV_VOCAB, "rt", encoding="utf-8") as f:
            raw = json.load(f)
        rev = {}
        for h, m in (raw.get("h2m") or {}).items():
            rev.setdefault(str(m).upper(), set()).add(str(h).upper())
        voc = {
            "hum": frozenset(str(x).upper() for x in raw["hum"]),
            "m_up": frozenset(str(x).upper() for x in raw["m_up"]),
            "m_raw": frozenset(str(x).upper() for x in raw["m_raw"]),
            "h2m": {str(k).upper(): str(v).upper() for k, v in (raw.get("h2m") or {}).items()},
            "rev": {k: frozenset(v) for k, v in rev.items()},
        }
        st.update(sig=sig, voc=voc)
        return voc
    except Exception as e:  # noqa: BLE001
        if not st["warned"]:
            sys.stderr.write(f"[species-route] vocab load failed ({type(e).__name__}: {e}) "
                             f"-> morphology channel degraded (S1/S2 仍可用)\n")
            st["warned"] = True
        return None


def registry():
    """卷物种登记表（append-only TSV: volume_id<TAB>species<TAB>registered_at<TAB>note）。缺件 → {}。"""
    st = _cache
    try:
        p = REGISTRY.stat()
        sig = (p.st_mtime_ns, p.st_size)
    except OSError:
        return {}
    if st["reg_sig"] == sig and st["reg"] is not None:
        return st["reg"]
    reg = {}
    try:
        with open(REGISTRY, encoding="utf-8") as f:
            for ln in f:
                if not ln.strip() or ln.startswith("#"):
                    continue
                parts = ln.rstrip("\n").split("\t")
                if len(parts) < 2:
                    continue
                sp = _norm_species(parts[1])
                if sp:
                    reg[parts[0].strip()] = sp
    except Exception:  # noqa: BLE001
        return {}
    st.update(reg_sig=sig, reg=reg)
    return reg


# ---------------------------------------------------------------- 证据族（SPEC §3.2）
def e1(u: str) -> bool:
    """E1: 鼠特异命名法 ^Gm\\d+$ / Rik$（大小写不敏感）。校准资产 human 231 簇 0 命中。"""
    return bool(_RE_GM.match(u) or _RE_RIK.search(u))


def e2(u: str, voc) -> bool:
    """E2: 非同一性直系同源对的鼠侧符号（∃h∈hum, h!=u, h2m[h]==u）。"""
    if u in voc["hum"]:
        return False
    return any(h != u and h in voc["hum"] for h in voc["rev"].get(u, ()))


def ambiguous(u: str, voc) -> bool:
    """假阳性防火墙：跨物种共享符号族 + 同一性映射（两物种同符号）。"""
    return bool(_RE_AMBIG.match(u)) or voc["h2m"].get(u) == u


def e3(u: str, voc) -> bool:
    """E3: 仅鼠表存在（弱证据，需配额门）。"""
    return u not in voc["hum"] and not ambiguous(u, voc) and u in voc["m_up"]


def morphology(raw_genes):
    """S3 形态判定（SPEC §3.3 判定树）。返回 (route, tier, detail)。vocab 不可用 → (None, None, …)。"""
    voc = _vocab()
    ups = [str(g).strip().upper() for g in raw_genes if str(g).strip()]
    letters = [g for g in raw_genes if _RE_LETTER.search(str(g))]
    titles = [g for g in letters if (not str(g).isupper()) and _RE_TITLE.match(str(g))]
    tf = round(len(titles) / max(len(letters), 1), 3)
    detail = {"title_frac": tf, "E1": [], "E2": [], "E3": [],
              "human_evidence_n": 0, "vocab_available": voc is not None}
    if voc is None:
        return None, None, detail
    h1 = sorted({u for u in ups if e1(u)})
    h2 = sorted({u for u in ups if e2(u, voc)})
    h3 = sorted({u for u in ups if e3(u, voc)})
    hh = sorted({u for u in ups if u in voc["hum"] or voc["h2m"].get(u) == u})
    # 兼容 B5 既有证据键（msp=^Gm\d+$|Rik$ 形态；m_only=旧定义，仅作对照登记，不参与判定）
    msp = sorted({g for g in raw_genes
                  if _RE_GM.match(str(g).strip().upper()) or _RE_RIK.search(str(g).strip().upper())})
    m_only = sorted({g for g in raw_genes
                     if str(g).strip().upper() not in voc["hum"]
                     and (str(g).strip().upper() in voc["m_up"] or str(g).upper() in voc["m_raw"])})
    detail.update({"E1": h1, "E2": h2, "E3": h3, "human_evidence_n": len(hh),
                   "msp": len(msp), "m_only": len(m_only),
                   # 诊断量（**不参与判定**）：标题面符号中"人表条目"的占比。
                   # 用途 = IMPACT_SURFACE §8.3 登记的 B5 限制①（真人源 title-case 输入在无 S1/S2 时
                   # 仍判 mouse_suspected）的后续判据素材；本版不动判定（保 290 表可复现）。
                   "letter_human_frac": round(
                       len([u for u in {str(g).strip().upper() for g in letters}
                            if u in voc["hum"] or voc["h2m"].get(u) == u]) / max(len(letters), 1), 3),
                   "msp_examples": msp[:5], "m_only_examples": m_only[:5],
                   "E3_quorum_met": len(h3) >= E3_QUORUM})
    if h1 or h2 or len(h3) >= E3_QUORUM:
        return "mouse", "mouse_confirmed", detail
    if tf >= T_FROZEN:
        return "mouse", "mouse_suspected", detail
    if hh:
        return "human", "human_assumed", detail
    return "undetermined", "human_assumed", detail


# ---------------------------------------------------------------- 解析主入口
def resolve(raw_genes, explicit=None, volume_id=None, volume_species=None):
    """三源优先级解析（SPEC §2）。返回 dict（route/tier/source/unresolved/review_required/evidence）。

    严格短路：S1 命中即返回（低优先源读数只并列登记在 evidence.conflicts）。
    缺参不报错、不缺省报 human；registry 未命中登记 registry_miss=True。
    """
    ex = _norm_species(explicit)
    vs = _norm_species(volume_species)
    reg, reg_hit, reg_miss = None, None, False
    if volume_id:
        reg = registry()
        reg_hit = reg.get(str(volume_id))
        reg_miss = reg_hit is None
    m_route, m_tier, m_detail = morphology(raw_genes)
    detail = {"S1": ex, "S2": vs if vs else reg_hit, "volume_id": volume_id,
              "registry_miss": bool(reg_miss), "morphology": m_detail, "conflicts": []}

    def _finish(route, tier, source):
        if m_route is not None and m_route != route:
            detail["conflicts"].append({"source": "symbol_morphology", "route": m_route, "tier": m_tier})
        unresolved = route == "undetermined"
        return {"spec_version": SPEC_VERSION, "route": route, "tier": tier, "source": source,
                "unresolved": unresolved, "review_required": unresolved, "evidence": detail}

    # S1 显式参数
    if ex:
        return _finish(ex, "mouse_confirmed" if ex == "mouse" else "human_assumed", "explicit_param")
    # S2 卷元数据（显式卷物种 > 登记表）
    if vs:
        return _finish(vs, "mouse_confirmed" if vs == "mouse" else "human_assumed", "volume_metadata")
    if reg_hit:
        return _finish(reg_hit, "mouse_confirmed" if reg_hit == "mouse" else "human_assumed",
                       "volume_metadata")
    # S3 符号形态
    if m_route is not None:
        return _finish(m_route, m_tier, "symbol_morphology" if m_route != "undetermined" else "unresolved")
    # 三源皆不可判（含 vocab 不可用）
    detail["conflicts"].append({"source": "morphology", "route": None,
                                "reason": "vocab_unavailable" if m_detail.get("vocab_available") is False
                                          else "no_evidence"})
    return _finish("undetermined", "human_assumed", "unresolved")


def attach(resp, raw_genes, explicit=None, volume_id=None, volume_species=None):
    """把解析结果写入 genes-mode resp（就地，仅新增键；SPEC §5）。

    鼠路径 → B5-G2 拒答形态；人路径 → 零干预；未定 → 零读数干预 + 显式旗标。
    返回治理状态 dict（供测试/留痕）。"""
    r = resolve(raw_genes, explicit=explicit, volume_id=volume_id, volume_species=volume_species)
    ev = dict(r["evidence"])
    # B5-G3 标注档（**逐字保留**：ON 路径同样执行；SPEC §5"不改既有语义"）。
    # 判据 = shared_genes ⊆ AMBIG{GLUL,VIM,CLU} ∧ n_shared≥1 → no_naming_claim + reason；排序与保留不动。
    flagged = []
    for e in resp["celltype_ranking"]:
        sh = e.get("shared_genes") or []
        if e.get("n_shared", 0) >= 1 and sh and set(sh) <= AMBIG:
            e["no_naming_claim"] = True
            e["reason"] = "ambiguous_coexpression_only"
            flagged.append(e["cell_type"])
    if r["route"] == "mouse":
        resp["unranked_candidates"] = resp["celltype_ranking"]
        resp["celltype_ranking"] = []
        resp["no_named_ranking_for"] = "mouse_input"
        resp["species_evidence"] = {"title_frac": ev["morphology"]["title_frac"],
                                   "msp": ev["morphology"]["msp"], "m_only": ev["morphology"]["m_only"],
                                   "msp_examples": ev["morphology"]["msp_examples"],
                                   "m_only_examples": ev["morphology"]["m_only_examples"],
                                   "source": r["source"], "spec_version": r["spec_version"]}
    resp["input_species"] = r["tier"]
    resp["species_route"] = r["route"]
    resp["species_source"] = r["source"]
    resp["species_evidence_detail"] = ev
    if r["unresolved"]:
        resp["species_unresolved"] = True
        resp["species_review_required"] = True
    r["flagged"] = flagged
    return r


if __name__ == "__main__":  # 自检（不联网、零下载）
    cases = {
        "mouse_uppercase_no_param": (["PCP2", "CAR8", "TRPM1"], {}),
        "mouse_uppercase_declared": (["PCP2", "RHO", "CALM1"], {"volume_species": "mouse"}),
        "human_uppercase": (["RHO", "PCP2", "TRPM1"], {}),
        "human_declared_overrides_morphology": (["CAR8", "RHO"], {"explicit": "human"}),
        "mito_only_human": (["MT-ATP6", "MT-CO1", "MT-CO3"], {}),
        "undetermined": (["XKR4", "MADCAM1", "SPATA31A3"], {}),
    }
    for k, (g, kw) in cases.items():
        r = resolve(g, **kw)
        print(f"{k:38s} route={r['route']:13s} tier={r['tier']:16s} src={r['source']:18s} "
              f"unresolved={r['unresolved']!s:5s} E1={r['evidence']['morphology'].get('E1')} "
              f"E2={r['evidence']['morphology'].get('E2')} E3n={len(r['evidence']['morphology'].get('E3') or [])}")
    print("gate EYEKB_SPECIES_ROUTE enabled() =", enabled())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB 工具内核 (三工具的纯实现, 与 MCP 传输层解耦)

纪律红线 (继承 KB_SPINOUT_MCP_DESIGN_v0 §6 + USER_DIRECTIVE_20260923):
1. 证据服务不进打分 —— 本模块只提供检索/页面/marker 事实, 任何消费方禁止
   将返回内容作为分类打分输入 (Claude5 冻结裁定, 服务级红线)。
2. copy 不 move —— 本模块读取的全部路径: EyeKB 侧为 P0/P1a 复制品;
   RAG 库与 embedding 模型 P1 阶段引用 OcularKB 现路径 (只读)。
3. marker 查询顺序机器化: query_marker 是注释流程第一步, 未查本地不联网。
"""
import gzip
import json
import os
import re
import sys
from pathlib import Path

EYEKB_ROOT = Path(__file__).resolve().parents[1]          # /mnt/D/EyeKB
CLIENTS = EYEKB_ROOT / "clients"
KB = EYEKB_ROOT / "kb"
VK_DIR = (KB / "vk_literature_index").resolve()
MARKER_JSON = KB / "markers" / "markers_v4.1_clean.json"
POINTER_YAML = KB / "literature_db" / "EYEKB_DB_POINTER.yaml"

# 软复核提示层 (t_d6f2a0a0 / D4): 只在既有结果后附加注记, 不改任何候选/排序/打分
import softflags as _sf  # noqa: E402

# OcularKB 侧只读常量 (P1 引用现路径; P2 物理迁移后改指 EyeKB 本地)
OCULARKB_RAG = Path("/mnt/D/OcularKB/ocularkb/rag")
DEFAULT_DB_DIR = OCULARKB_RAG / "literature_db" / "v2.0_2026-09"

# 导入复制品检索内核 (verbatim copy of ocularkb/rag/scripts/stage3_retrieve.py)
sys.path.insert(0, str(CLIENTS / "ocularkb" / "rag" / "scripts"))
import stage3_retrieve as _s3  # noqa: E402


# ---------------------------------------------------------------- 工具 1
# 默认库解析链（外机可用修复，2026-09-30，PI 放行"验证过就上传"波）：
# 1) env EYEKB_DB_DIR  2) 指针 role:default 条目（绝对或仓根相对）且存在
# 3) 本仓唯一语料（Release 解包即自动发现）  4) 回退生产硬路径（行为与旧版恒等）
def _default_db_dir():
    env = os.environ.get("EYEKB_DB_DIR")
    if env:
        return env
    try:
        txt = POINTER_YAML.read_text(encoding="utf-8")
        cur_path = None
        for ln in txt.splitlines():
            s = ln.strip()
            if s.startswith("path:"):
                cur_path = s.split("path:", 1)[1].strip()
            elif s.startswith("role:") and "default" in s and cur_path:
                p = Path(cur_path)
                if not p.is_absolute():
                    p = KB.parent / cur_path
                if p.is_dir():
                    return str(p)
    except Exception:
        pass
    for base in (KB / "literature_db", KB.parent / "literature_db"):
        if base.is_dir():
            cands = sorted(d for d in base.iterdir()
                           if d.is_dir() and (d / "chunks.parquet").is_file())
            if len(cands) == 1:
                return str(cands[0])
    return str(DEFAULT_DB_DIR)


def search_literature(cell_type, species=None, tissue=None, top_k=5,
                      query=None, db=None):
    """文献片段检索: 透传 stage3_retrieve.retrieve()。

    db: None → 按 _default_db_dir() 解析链选库; 或显式目录路径。
    species/tissue/cell_type 三维过滤透传 (Claude5 审核要求落地)。
    """
    db_dir = str(db) if db else _default_db_dir()
    res = _s3.retrieve(cell_type, species=species or None, top_k=int(top_k),
                       query=query or None, tissue=tissue, db_dir=db_dir)
    # K3 additive 联表: 每条命中挂 inclusion_reason (入库原因归类), 不触碰检索语义
    try:
        rm = _reason_map()
        for hit in (res or {}).get("results", []):
            tag = rm.get(str(hit.get("pmid")))
            if tag:
                hit.update(tag)
    except Exception:
        pass
    return res


# ---------------------------------------------------------------- 工具 2
_PAGE_RE_OK = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")

def list_kb_pages():
    """白名单目录内的索引页清单。"""
    out = []
    for p in sorted(VK_DIR.glob("*.md")):
        kind = ("index" if p.name == "INDEX.md"
                else "tissue" if p.name.startswith("tissue-")
                else "topic")
        out.append({"page": p.stem, "scope": kind, "file": p.name})
    return out


def get_kb_page(scope, name=""):
    """读 VK 索引页原文。白名单防越界:
    - 只允许 kb/vk_literature_index/ 内的 *.md
    - name 只允许 [A-Za-z0-9_-]; 解析后 realpath 必须仍在白名单目录内
    """
    scope = (scope or "").strip().lower()
    name = (name or "").strip()
    if scope == "index":
        fname = "INDEX.md"
    elif scope == "topic":
        fname = f"{name}.md"
    elif scope == "tissue":
        fname = f"tissue-{name}.md" if not name.startswith("tissue-") else f"{name}.md"
    else:
        return {"error": f"scope 必须是 index|topic|tissue, 收到: {scope!r}",
                "available": list_kb_pages()}
    if not all(c in _PAGE_RE_OK for c in name) and scope != "index":
        return {"error": f"name 含非法字符 (白名单 [A-Za-z0-9_-]): {name!r}"}
    target = (VK_DIR / fname).resolve()
    # 双保险: realpath 前缀校验 (防 ../ 与符号链接逃逸; NTFS 无 symlink 仍保留检查)
    if not str(target).startswith(str(VK_DIR) + os.sep) and target != VK_DIR:
        return {"error": "路径越界拒绝 (white-list enforcement)"}
    if target.suffix != ".md" or not target.is_file():
        return {"error": f"页面不存在: scope={scope} name={name}",
                "hint": "先调 list 视图: 返回的 available 列出全部页面",
                "available": list_kb_pages()}
    return {"scope": scope, "name": name, "file": str(target),
            "content": target.read_text(encoding="utf-8")}


# ---------------------------------------------------------------- 工具 3
# 多 marker 库支持 (P1opt-O4, 闭 v1 待确认第 5 条):
#   library="retina"   → markers_v4.1_clean.json (精确复现 P1 旧行为)
#   library="membrane" → markers_membrane_v1.json (四面板膜/血管/间质/免疫)
#   library="retina_interneuron" → markers_v5_retina_interneuron.json (v5.0, KB5v2 t_9714f560 发布;
#       BC/AC/HC 泛型 core+亚型锚补录, v4.1 严格超集; 单库查询时类名即正名 BC/AC/HC) [t_d07ab64f 接线]
#   library="all"      → 现役集合合并 (provenance 按文件分列; 同名类经消歧规则以
#       "<库>::<类>" 别名行呈现, 先注册库正名/语义零变动; v5 对 v4.1 即此形态)。
#       [ACT t_5d5853c9 · USER_DIRECTIVE_20260926 A1/A2/A5 激活切换, PI 2026-09-26 批准]
#       现役集合由 env EYEKB_ACT_V6 控制 (每调用读取, 与 softflags 同风格):
#         未设/非 off 值 = ON (激活默认态): 五库 = 现役三库 + retina_v6 + face_v6。
#           retina_v6 10 类与 v4.1 同名 → "retina_v6::<类>" 别名行并入;
#           face_v6 间质 Keratocytes/Fibroblast/Pericyte/Myofibroblast 与 membrane 同名
#           → "face_v6::<类>" 别名, SMC 与 Conj_epithelium_basal/superficial 为新增正名类。
#           Micro/RPE 查询的 micro_detail/rpe_detail 按 dbs 载入顺序末位覆盖 →
#           ON 态取 v6 发布件 detail (修复面板并入语义, 已完成态声明于收口件)。
#         ∈ {0,false,off,no} = OFF (回退态): 现役三库, 响应与 pre_change 基线
#           规范序列化全等 (A5 机读验收, sf13 同款自证)。
#       白名单硬编码 {retina_v6, face_v6} —— lacrimal_v6 任何态禁入默认路径
#       (PI A3 裁定暂不切; 仅显式 library=lacrimal_v6 路由维持 t_e7ec73ab 登记原状)。
#   —— 显式库路由 (登记自 t_38b99a15/t_e7ec73ab, 激活前既可达, 激活不改其语义) ——
#   library="retina_v6" → markers_v6_retina_repair.json (v6.0-retina-repair: 10 类红词条修复
#       + subtype_anchor_layer + microglia_repair; 文件只读, 禁改本体)
#   library="face_v6"   → markers_v6_face_increment.json (v6.0-face: 眼表间质 4 红条 repair +
#       B1 新条; 无 markers 顶层键, 读入时由 stromal_repair/face_increment.core 归一派生,
#       源文件零改动; granularity_note_stromal_caution 随命中类附注)
#   library="lacrimal_v6" → markers_v6_lacrimal_increment.json (v6.0-lacrimal, KB8: 泪腺分泌/
#       导管/肌上皮警示条 3 条; 同样读入派生; 仅显式查询可达, 默认 all 永不含——PI A3 暂不切)
#   library="k9_ocs" → markers_k9_ocs_increment.json (k9.0-ocs-registered-v1, KB9 案 B 眼表 4 新条:
#       Melanocyte/Schwann/Conj_epithelium_suprabasal/Limbus_Sclera_fibroblast_C1, 均
#       applicability=ocular_surface_only; 逐条带 CL id+OLS 回证+逐基因 PMID 链。
#       [KB9REG-EXEC t_4bb75b26 · PI D17 批准注册, 2026-09-28 波] REGISTERED_DEFAULT_OFF:
#       仅显式路由可达, 任何态不入默认 all (不入 V6_DEFAULT_LIBS 白名单, 与 lacrimal_v6 同纪律);
#       激活需 §10-6 义务 run + PI 另批, 本登记不含激活机制。
#       配套屏蔽/适用性规则+装配规则 v2=同目录 _k9_ocs_rules_overlay_v1.json (惰性数据件,
#       本 loader 不读, MCP 运行时不消费; 消费面=评测/判读 run 直读文件)。
MARKER_DIR = (KB / "markers")
MARKER_LIBS = {"retina": MARKER_JSON,
               "membrane": MARKER_DIR / "markers_membrane_v1.json",
               "retina_interneuron": MARKER_DIR / "markers_v5_retina_interneuron.json",
               "retina_v6": MARKER_DIR / "markers_v6_retina_repair.json",
               "face_v6": MARKER_DIR / "markers_v6_face_increment.json",
    # lacrimal_v6 = KB8 首个眼附属器词条库 (t_e7ec73ab, 2026-09-25): 3 条 (分泌/导管/肌上皮警示条)
    #   + reference_layer; 无 markers 顶层键, 读入时由 lacrimal_increment.core 归一派生 (本体零改动)
    #   [t_5d5853c9] PI A3=暂不切: 禁入 V6_DEFAULT_LIBS 白名单, 仅显式路由可达
    "lacrimal_v6": MARKER_DIR / "markers_v6_lacrimal_increment.json",
    # k9_ocs = KB9 案 B 眼表 4 新条 (t_4bb75b26 注册, 默认 OFF; 顶层 markers 键=注册时派生落盘,
    #   读入直取无需运行时派生; 与 build 底件 copy 不 move, 底件 sha 在件内 registration_provenance)
    "k9_ocs": MARKER_DIR / "markers_k9_ocs_increment.json"}

# [ACT t_5d5853c9] 默认 all 的 v6 并入白名单——硬编码, env 值只能整体开关, 不能注入任何库
V6_DEFAULT_LIBS = ("retina_v6", "face_v6")


def _v6_act_enabled():
    """env EYEKB_ACT_V6 ∈ {0,false,off,no} (casefold) = OFF 回退; 未设/其余值 = ON 激活。"""
    v = (os.environ.get("EYEKB_ACT_V6") or "").strip().casefold()
    return v not in {"0", "false", "off", "no"}


# ---------------------------------------------------------------- KBGOV-B5 跨物种 ranking 治理层
# [B5IMPL t_8960c7e0 · USER_DIRECTIVE_20260928 追加五队列① · PI 预授权接线]
# query_marker genes-mode 输入物种治理。判据唯一权威源 = plans/kb_gov_20260928/
# KBGOV_CANDIDATE.md §G1/§G2/§G3（主候选 B5, 机械 A/B 双门证据在案; 冻结输入 sha 见
# plans/kbgov_b5impl_20260928/ledgers/SHA_PRE_B5IMPL.txt）:
#   G1 判定层: 三信号 title_frac(大小写惯例) / msp(Gm\d+|.*Rik$) / m_only(鼠独有符号),
#       冻结阈值 T=0.4（校准件 kbgov_g1_calibration.json: 人源 231 簇 title_frac max=0.0,
#       鼠源 59 簇 min=0.8, human_misdetections=[]）。
#   G2 B5 口径: mouse_confirmed ∧ mouse_suspected 均拒答具名——celltype_ranking 全量转
#       unranked_candidates（条目保留、非具名排名）, 顶层加 no_named_ranking_for=
#       'mouse_input' + species_evidence; human_assumed 零干预（预注册回归门=230 人源簇
#       ranking 位移 0.0%, 过杀线 >5%）。
#   G3 标注档(不删序): shared_genes ⊆ AMBIG{GLUL,VIM,CLU} ∧ n_shared≥1 → 条目加
#       no_naming_claim=true + reason='ambiguous_coexpression_only'; 排序与条目保留不动
#       （消费方协议: 判读席禁以 flagged 条目作 identity 定名依据——归判读协议承接）。
# env 开关 EYEKB_KBGOV_B5: 未设/其余值 = ON（0.6-kbgov5 实装默认态）;
#   ∈{0,false,off,no} = OFF 回退态——genes-mode 响应与 pre 基线逐字节全等（A5 式机读
#   自证, 对照表 out/B5IMPL_A5_ROLLBACK.tsv）。词表加载失败 → 整体降级 legacy 行为
#   (fail-soft, stderr 一次性登记, 不 throw)。禁 import 实验复刻件——本层为生产码内
#   独立实现, 与复刻件对账双源一致为门（b505/b506）。REGISTERED_DEFAULT_OFF 语义
#   （k9_ocs/lacrimal_v6 不入默认）与本层正交, 不得破坏。
KBGOV_VOCAB = Path(__file__).resolve().parent / "kbgov_vocab.json.gz"
KBGOV_T_FROZEN = 0.4                                  # 冻结判据（改值=改预注册, 禁）
KBGOV_AMBIG = frozenset({"GLUL", "VIM", "CLU"})       # 冻结锚集（不自扩——过杀放大器已实证）
_KBGOV_RE_LETTER = re.compile(r"[A-Za-z]")
_KBGOV_RE_TITLE = re.compile(r"^[A-Z][a-z]")
_KBGOV_RE_GM = re.compile(r"^Gm\d+$")
_KBGOV_RE_RIK = re.compile(r"Rik$")
_kbgov_voc_cache = {"sig": None, "data": None, "warned": False}


def _kbgov_b5_enabled():
    """env EYEKB_KBGOV_B5 ∈ {0,false,off,no} (casefold) = OFF 回退; 未设/其余值 = ON 治理。"""
    v = (os.environ.get("EYEKB_KBGOV_B5") or "").strip().casefold()
    return v not in {"0", "false", "off", "no"}


def _kbgov_vocab():
    """惰性加载 sha 锚定词表 (mcp_server/kbgov_vocab.json.gz = KBGOV 冻结件逐字节副本,
    sha256 9b504a2e...)。返回 (HUMSYM, MOUSYM_raw, MOUSYM_upper) 或 None（降级 legacy）。"""
    st = _kbgov_voc_cache
    sig = None
    try:
        p_st = KBGOV_VOCAB.stat()
        sig = (p_st.st_mtime_ns, p_st.st_size)
    except OSError:
        pass
    if sig is not None and st["sig"] == sig and st["data"] is not None:
        return st["data"]
    try:
        with gzip.open(KBGOV_VOCAB, "rt", encoding="utf-8") as f:
            v = json.load(f)
        data = (frozenset(v["hum"]), frozenset(v["m_raw"]), frozenset(v["m_up"]))
        st.update(sig=sig, data=data)
        return data
    except Exception as e:  # noqa: BLE001
        if not st["warned"]:
            sys.stderr.write(f"[kbgov-b5] vocab load failed ({type(e).__name__}: {e}) "
                             f"-> B5 degraded to legacy behavior\n")
            st["warned"] = True
        return None


def _kbgov_g1_tier(raw_genes, hum, m_raw, m_up):
    """G1 输入物种判定（生产实现, 与复刻件 kbgov_ab.tier_of 判据逐字一致）。
    输入=原始大小写基因名清单（upper 前）。返回 (tier, evidence)。"""
    letters = [g for g in raw_genes if _KBGOV_RE_LETTER.search(g)]
    title = [g for g in letters if (not g.isupper()) and _KBGOV_RE_TITLE.match(g)]
    msp = [g for g in raw_genes if _KBGOV_RE_GM.match(g) or _KBGOV_RE_RIK.search(g)]
    monly = [g for g in raw_genes
             if g.upper() not in hum and (g.upper() in m_up or g in m_raw)]
    tf = len(title) / max(len(letters), 1)
    ev = {"title_frac": round(tf, 3), "msp": len(msp), "m_only": len(monly),
          "msp_examples": list(msp)[:5], "m_only_examples": list(monly)[:5]}
    if tf < KBGOV_T_FROZEN:
        return "human_assumed", ev
    return ("mouse_confirmed" if (msp or monly) else "mouse_suspected"), ev


def _kbgov_govern_genes_resp(resp, raw_gl):
    """B5 治理分支: 就地修改 genes-mode resp（G3 标注 → G2 拒答转列）。
    词表不可用时零改动（fail-soft=legacy）。返回治理状态供留痕/测试。"""
    voc = _kbgov_vocab()
    if voc is None:
        return {"applied": False, "reason": "vocab_unavailable"}
    hum, m_raw, m_up = voc
    tier, ev = _kbgov_g1_tier(raw_gl, hum, m_raw, m_up)
    flagged = []
    for e in resp["celltype_ranking"]:
        sh = e.get("shared_genes") or []
        if e.get("n_shared", 0) >= 1 and sh and set(sh) <= KBGOV_AMBIG:
            e["no_naming_claim"] = True
            e["reason"] = "ambiguous_coexpression_only"
            flagged.append(e["cell_type"])
    resp["input_species"] = tier
    refused = tier in ("mouse_confirmed", "mouse_suspected")
    if refused:
        resp["unranked_candidates"] = resp["celltype_ranking"]
        resp["celltype_ranking"] = []
        resp["no_named_ranking_for"] = "mouse_input"
        resp["species_evidence"] = ev
    return {"applied": True, "tier": tier, "refused": refused, "flagged": flagged}


def _load_marker_dbs(library="all"):
    lib = (library or "all").strip().lower()
    if lib == "all":
        names = ["retina", "membrane", "retina_interneuron"]  # 现役三库 (OFF 态=全量)
        if _v6_act_enabled():
            names = names + list(V6_DEFAULT_LIBS)  # 白名单 append; lacrimal_v6 永不在此
    elif lib in MARKER_LIBS:
        names = [lib]
    else:
        raise ValueError("library 必须是 retina|membrane|retina_interneuron|retina_v6|"
                         "face_v6|lacrimal_v6|k9_ocs|all, 收到: " + repr(library))
    dbs = []
    for n in names:
        p = MARKER_LIBS[n]
        if p.is_file():
            with open(p, encoding="utf-8") as f:
                db = json.load(f)
            if n in ("face_v6", "lacrimal_v6") and "markers" not in db:
                # 读入时归一派生 (发布文件本体零改动): 各 *_repair/*_increment 的
                # core[{gene,...}] → 类名→基因清单; 空 core 类保留 (0 独立判据基因如实登记)
                derived = {}
                srcs = ({"stromal_repair", "face_increment"} if n == "face_v6"
                        else {"lacrimal_increment"})
                for src in srcs:
                    for cls, e in (db.get(src) or {}).items():
                        derived[cls] = [str(x.get("gene", "")).strip().upper()
                                        for x in (e.get("core") or [])
                                        if isinstance(x, dict) and x.get("gene")]
                db = dict(db)
                db["markers"] = derived
            dbs.append((n, p, db))
    return dbs


def query_marker(genes=None, cell_type=None, library="all"):
    """本地权威 marker 库查询 (支持多库; 见 MARKER_LIBS)。
    - cell_type 模式: 返回该类的 marker (retina 库附 micro/rpe detail)
    - genes 模式: 每个基因反向命中哪些类
    genes: list[str] 或逗号/空格分隔 str。两类都空 → 返回类目清单。
    类名跨库冲突时以 "库名::类名" 消歧 (v1 无冲突; 冲突清单见 provenance.conflicts)。
    library=retina_v6|face_v6 (t_38b99a15 登记): KB7 v6 修复面板; t_5d5853c9 激活
    (USER_DIRECTIVE_20260926 A1/A2): 默认 all 含 retina_v6+face_v6, env EYEKB_ACT_V6=0
    |false|off|no 回退=现役三库 (与激活前 pre 基线全等); lacrimal_v6 任何态不入默认
    (PI A3 暂不切, 仅显式路由); 查询时 v6 发布文件本体只读。
    library=k9_ocs (t_4bb75b26 注册, PI D17): KB9 案 B 眼表 4 新条 REGISTERED_DEFAULT_OFF——
    任何态不入默认 all (不入 V6_DEFAULT_LIBS, 无激活 env), 仅显式查询可达; 激活需
    §10-6 义务 run + PI 另批。
    """
    dbs = _load_marker_dbs(library)
    markers, owner = {}, {}
    seen_upper = {}
    conflicts = []
    for name, path, db in dbs:
        for ct, gs in db.get("markers", {}).items():
            up = ct.upper()
            if up in seen_upper:  # 跨库类名冲突 → 消歧后缀 (显示名保留原大小写, v1 语义)
                alt = f"{name}::{ct}"
                conflicts.append({"class": ct, "kept": ct, "alias": alt})
                markers[alt] = [g.upper() for g in gs]
                owner[alt] = str(path)
                continue
            markers[ct] = [g.upper() for g in gs]
            owner[ct] = str(path)
            seen_upper[up] = ct
    prov = {"library_requested": library,
            "files": [{"library": n, "path": str(p), "version": d.get("version"),
                       "note": d.get("note")} for n, p, d in dbs],
            "conflicts": conflicts}
    # 反查索引
    gene2ct = {}
    for ct, gs in markers.items():
        for g in gs:
            gene2ct.setdefault(g, []).append(ct)

    if cell_type:
        want = cell_type.strip().upper()
        hit = {ct: gs for ct, gs in markers.items() if ct.upper() == want}
        extra = {}
        if want in ("MICRO", "MICROGLIA"):
            for _, _, db in dbs:
                if "micro_detail" in db:
                    extra["micro_detail"] = db["micro_detail"]
        if want == "RPE":
            for _, _, db in dbs:
                if "rpe_detail" in db:
                    extra["rpe_detail"] = db["rpe_detail"]
        # membrane 库逐基因溯源 (命中类才给, 控制响应体积)
        for name, path, db in dbs:
            for ct in hit:
                raw = ct.split("::")[-1]
                pp = (db.get("provenance") or {}).get(raw)
                if pp and db.get("version", "").startswith("v1-membrane"):
                    extra[f"provenance_{raw}"] = pp
        # face_v6 (t_38b99a15 接线) / lacrimal_v6 (t_e7ec73ab 接线): 命中 v6 条时附发布文件内
        # granularity_note_* 警示注记 (数据侧原文)。t_5d5853c9 激活后 face_v6 在默认 all 内
        # → 同名间质类 (含 membrane 正名行) 查询可附 stromal caution; lacrimal_v6 仅显式路由。
        for name, path, db in dbs:
            for gkey, gval in db.items():
                if not str(gkey).startswith("granularity_note_"):
                    continue
                if gval and any(ct.split("::")[-1] in (db.get("markers") or {})
                                for ct in hit):
                    extra[f"v6_{gkey}"] = gval
                    break
        resp = {"mode": "cell_type", "query": cell_type, "found": bool(hit),
                "markers": hit, "detail": extra, "provenance": prov}
        return _sf.wrap_resp(resp, markers, "cell_type",
                             found_classes=list(hit.keys()), provenance=prov)

    if genes:
        if isinstance(genes, str):
            raw_gl = [g.strip() for g in genes.replace(",", " ").split() if g.strip()]
        else:
            raw_gl = [str(g).strip() for g in genes if str(g).strip()]
        gl = [g.upper() for g in raw_gl]  # 与旧逐元素 strip().upper() 逐字等价（OFF 全等门实证）
        hits = {g: gene2ct.get(g, []) for g in gl}
        score = {}
        for ct in markers:
            n = sum(1 for g in gl if g in markers[ct])
            if n:
                score[ct] = {"n_shared": n, "shared_genes":
                             [g for g in gl if g in markers[ct]], "library": owner[ct]}
        ranked = sorted(score.items(), key=lambda kv: -kv[1]["n_shared"])
        # 兼容字段: 单库时保留 auc_threshold 顶层语义
        auc = next((d.get("auc_threshold") for _, _, d in dbs if d.get("auc_threshold")), None)
        resp = {"mode": "genes", "query": gl, "gene_to_celltypes": hits,
                "celltype_ranking": [{"cell_type": c, **s} for c, s in ranked],
                "auc_threshold": auc, "provenance": prov}
        # [KBGOV-B5] 治理分支——OFF 态整体跳过, resp 与 pre 基线全等（A5 验收门）
        if _kbgov_b5_enabled():
            _kbgov_govern_genes_resp(resp, raw_gl)
        return _sf.wrap_resp(resp, markers, "genes", query_genes=gl,
                             ranking=resp["celltype_ranking"], provenance=prov)

    return {"mode": "list", "cell_types": sorted(markers), "provenance": prov}


# ---------------------------------------------------------------- 工具 4/5: 判读层先验 (KB1, KB1v2 扩展)
PRIORS_DIR = (KB / "priors").resolve()
BASELINES_DIR = (KB / "baselines").resolve()  # KB1v2-W1: 眼科通用组成基线层 (供者级)


def _apply_marker_repairs(priors):
    """KB7-WIRE (t_38b99a15) ②: baseline::retina 4 条红词修正 —— append 式覆盖层。

    原文基线 JSON 字节不动; 修复语义唯一权威源 =
    kb/markers/markers_v6_retina_repair.json#baseline_retina4_disposition (t_2e5e103a 冻结发布)。
    本函数把 kb/baselines/_marker_repair_*.json (schema eyekb-marker-repair/1.0, 不匹配
    eyekb-baseline/ 前缀 → 不会被当作条目加载) 的 row_fixes 应用到内存态加载的条目上;
    行匹配 (cell_type + old_markers 逐字全等) 失败 → 该行跳过并如实登记 skipped_rows
    (fail-closed, 不凭记忆改数)。只动 marker 描述层, 组成比例/分布/身份签名零变化。"""
    if not BASELINES_DIR.is_dir():
        return
    for p in sorted(BASELINES_DIR.glob("_marker_repair_*.json")):
        try:
            rep = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not str(rep.get("schema", "")).startswith("eyekb-marker-repair/"):
            continue
        entry = priors.get(rep.get("target_entry_id", ""))
        if not isinstance(entry, dict):
            continue
        applied, skipped = [], []
        for fix in rep.get("row_fixes", []):
            rows = entry.get(fix.get("target_list", "states"), [])
            hit_row = None
            for r in rows:
                if (isinstance(r, dict) and r.get("cell_type") == fix.get("cell_type")
                        and r.get("markers") == fix.get("old_markers")):
                    hit_row = r
                    break
            if hit_row is None:
                skipped.append({"cell_type": fix.get("cell_type"),
                                "reason": "old_markers 行匹配失败 (基线本体漂移或已修过) — "
                                          "未应用, 上报不臆改"})
                continue
            hit_row["markers"] = list(fix.get("new_markers", []))
            hit_row["marker_revision"] = {
                "old_markers": list(fix.get("old_markers", [])),
                "removed": fix.get("removed", []),
                "added_ref": fix.get("added_ref", ""),
                "note": fix.get("note", ""),
                "disposition_source": rep.get("disposition_source", ""),
                "repair_file": p.name,
                "repair_card": rep.get("card", ""),
            }
            applied.append(fix.get("cell_type"))
        entry["marker_repair"] = {
            "file": str(p), "schema": rep.get("schema"),
            "version": rep.get("version"), "card": rep.get("card"),
            "created": rep.get("created"),
            "original_body_untouched": True,
            "disposition_source": rep.get("disposition_source", ""),
            "applied_rows": applied, "skipped_rows": skipped,
            "residual_observations": rep.get("residual_observations", []),
            "redline": ("本修正只影响 marker 描述层; 组成比例/分布/身份签名仍为原文件值; "
                        "原 usage_redline 不变——判读对照与 QC 旗专用, 禁入打分"),
        }


def _load_priors():
    """扫描 kb/priors/**/*.json (schema eyekb-prior/1.0) + kb/baselines/*.json
    (schema eyekb-baseline/1.0, KB1v2) → {entry_id: dict}。
    baseline 条带 _kind='baseline', 查询时优先于旧 composition 条 (copy 不 move, 旧条存档)。"""
    out = {}
    for p in sorted(PRIORS_DIR.rglob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if d.get("schema") == "eyekb-prior/1.0":
            d["_file"] = str(p)
            d.setdefault("_kind", "legacy")
            out[d["entry_id"]] = d
        elif d.get("schema") == "eyekb-disease/1.1":
            # KB1v2-W2: 疾病薄层条目 (身份层级+状态轴), 查询优先于 v1 疾病条
            d["_file"] = str(p)
            d["_kind"] = "disease_v2"
            out[d["entry_id"]] = d
    if BASELINES_DIR.is_dir():
        for p in sorted(BASELINES_DIR.glob("*.json")):
            if p.name in ("baselines.json", "fetal_development_transitions.json",
                          "_STAGE_DISCLOSURE.json"):
                continue
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            if str(d.get("schema", "")).startswith("eyekb-baseline/"):
                # KB2c: 1.0/1.1 都收; 1.1 带 organism_stage 发育轴双档
                d["_file"] = str(p)
                d["_kind"] = "baseline"
                out[d["entry_id"]] = d
    _apply_marker_repairs(out)  # KB7-WIRE ② (t_38b99a15): append 式红词修正覆盖层
    return out


def _fetal_concept_response(request_stage):
    """KB2c 红线1: fetal/developing 查询不得借用 adult 桶 —— 返回转换态概念条目 (裁定 Q5)。"""
    p = BASELINES_DIR / "fetal_development_transitions.json"
    concept = None
    if p.is_file():
        try:
            concept = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            concept = None
    return {"mode": "fetal_development_concept",
            "entry_id": "fetal_development_transitions",
            "request_stage": request_stage,
            "note": ("KB 当前无 fetal/developing filled 组成基线; 按 KB2c 裁定与 PI 红线, "
                     "成人基线不得代答胎儿/发育期问题 ('胎儿的这些和成人的即使是一个组织也不对的')。"
                     "现役判读引擎对 fetal/发育期样本必须弃权 (E4=OOD_严格)。"),
            "concept": concept,
            "source_file": str(p),
            "usage_redline": ("本返回非组成基线; 禁把成人条目的比例区间外推到 fetal/developing 材料。")}


def _resolve_sources(entry):
    """sid → 可溯源对象 (PMID/路径), 判读层红线: 每条预期必有出处。"""
    return {s["sid"]: {k: v for k, v in s.items() if k != "sid"}
            for s in entry.get("sources", [])}


def get_tissue_composition(species, tissue, disease="", development_stage=""):
    """组成基线查询: 该物种该组织(可带疾病)的细胞组成清单+比例区间+出处。
    species: human|mouse|...; tissue: retina|fibrovascular_membrane|...; disease 可选。
    development_stage (KB2c 双轴检索): ""|any=主档口径(adult-only 条); adult=成人主档;
    fetal|developing=返回转换态概念条目 (禁借成人桶, PI 红线); unknown=只看 unknown 档条
    (如 GSE158629 RPE 无年龄列源)。postnatal→developing、organoid→unknown+旗标 (裁定 Q1 映射)。
    返回 rows = 主表 (正常条 major_classes / 疾病膜条 major_compartments) + 状态层 +
    flags + caveats + provenance。仅证据与 QC 旗, 禁入打分。"""
    want = (development_stage or "").strip().lower()
    if want == "postnatal":
        want = "developing"
    if want in ("fetal", "developing"):
        return _fetal_concept_response(want)
    priors = _load_priors()
    sp = (species or "").strip().lower()
    ti = (tissue or "").strip().lower()
    dis = (disease or "").strip().lower()
    cands = []
    for e in priors.values():
        if sp and e.get("species", "").lower() != sp:
            continue
        if ti and ti not in (e.get("tissue", "") or "").lower():
            continue
        if dis:
            if (e.get("disease") or "").lower().find(dis) < 0:
                continue
        elif e.get("disease"):
            # 未给 disease → 只要基线条目; 但若该组织仅有疾病条目, 也返回并标注
            cands.append((2, e))
            continue
        cands.append((0 if not dis else 1, e))
    if not cands:
        return {"error": f"无匹配组成条目 (species={species!r} tissue={tissue!r} disease={disease!r})",
                "available": [{"entry_id": e["entry_id"], "species": e.get("species"),
                               "tissue": e.get("tissue"), "disease": e.get("disease")}
                              for e in priors.values()]}
    cands.sort(key=lambda x: (x[0], 0 if x[1].get("_kind") == "baseline" else 1))
    # KB2c: development_stage=unknown → 只看 unknown 档条 (如 RPE); adult/"" → 主档现状
    if want == "unknown":
        unk = [c for c in cands if str(c[1].get("organism_stage", "")).startswith("unknown")]
        if not unk:
            return {"mode": "no_unknown_stage_entry", "request_stage": "unknown",
                    "note": (f"该查询无 organism_stage=unknown 档条目 (species={species!r} "
                             f"tissue={tissue!r}); unknown 档源清单见 kb/baselines/_STAGE_DISCLOSURE.md"),
                    "disclosure_file": str(BASELINES_DIR / "_STAGE_DISCLOSURE.md")}
        cands = unk
    entry = cands[0][1]
    rows = entry.get("major_classes") or entry.get("major_compartments") or []
    for r in rows:  # 防呆: 行内 source_ids 全部可解析
        r["sources_resolved"] = [_resolve_sources(entry).get(s, {"sid": s, "MISSING": True})
                                 for s in r.get("source_ids", [])]
    resp = {"entry_id": entry["entry_id"], "title": entry["title"],
            "species": entry.get("species"), "tissue": entry.get("tissue"),
            "disease": entry.get("disease"), "frozen_date": entry.get("frozen_date"),
            "organism_stage": entry.get("organism_stage",
                                        "unannotated(v1 存档条 — adult 断言须用 kb/baselines v1.1 主档)"),
            # KB3 (t_5425a7ca) 条款6: 组成陈述必须能回答"什么发育阶段" —— 出口级透传
            "development_stage": entry.get("development_stage", "unknown"),
            "evidence_grades": entry.get("evidence_grades"),
            "rows": rows,
            "states": entry.get("states") or entry.get("myeloid_states") or [],
            "fine_types": entry.get("fine_types"),
            "flags": entry.get("flags"),
            "caveats": entry.get("caveats"),
            "provenance": _resolve_sources(entry),
            "source_file": entry["_file"],
            "usage_redline": ("判读对照与 QC 旗专用; 禁止转成 module score/标签加权/置信度加分/候选排序分/"
                              "复合 QC 分数 (KB1v2 红线1, REVIEWER_LLM T3 扩展表述全继承)")}
    # KB1v2 (REVIEWER_LLM T2): baseline 条透传口径字段; 骨架条明确标"区间无法估计"
    if entry.get("_kind") == "baseline":
        resp.update({
            "baseline_status": entry.get("status"),
            "anchor": entry.get("anchor"),
            "t2_fields": entry.get("t2_fields"),
            "usage_scope": entry.get("usage_scope"),
            "distribution_method": entry.get("distribution_method"),
            "donor_level_main": entry.get("donor_level_main"),
            "pooled_all_cells": entry.get("pooled_all_cells"),
            "composition_status": entry.get("composition_status"),
            "mapping_from_t_6f5cc731": entry.get("mapping_from_t_6f5cc731"),
            "verdict": entry.get("verdict"),
            # KB2c 发育轴双档透传 (红线: 两档身份签名分离; unknown 必须披露)
            "stage_axis": entry.get("stage_axis"),
            "stage_note": entry.get("stage_note"),
            "stage_disclosure": entry.get("stage_disclosure"),
            "excluded_nonadult_units": entry.get("excluded_nonadult_units"),
            "adult_only_meta": entry.get("adult_only_meta"),
            "donor_level_adult_pool_contrast": entry.get("donor_level_adult_pool_contrast"),
            "pooled_adult_only_main": entry.get("pooled_adult_only_main"),
            "identity_signature": entry.get("identity_signature"),
            "strata": entry.get("strata"),
            "stage_query_note": (
                "主档=adult-only (donor_age>=18y, KB2c 裁定 Q2); 引用 v1.0 混口径旧数字只能挂 "
                "donor_level_adult_pool_contrast (tier=...__adult_pool__v1.0), 两档签名不混用; "
                "fetal/developing 查询禁借本条 (返回转换态概念条目)"
                if entry.get("organism_stage") == "adult" else
                "本条 organism_stage=unknown —— 禁作为成人基线引用 (KB2c 红线2 披露条)"
                if str(entry.get("organism_stage", "")).startswith("unknown") else ""),
        })
    # KB7-WIRE ② (t_38b99a15): marker 修正台账透传 (仅已挂覆盖层的条目出现该字段;
    # 未修条目响应零变化) —— 消费方可审计 old→new 与出处
    if entry.get("marker_repair"):
        resp["marker_repair"] = entry["marker_repair"]
    return resp


def get_disease_prior(disease, tissue=""):
    """疾病先验查询: 预期 细胞×状态 矩阵 + 非预期/污染旗 + marker 签名 + 出处。
    disease: 子串匹配 (如 'proliferative'/'PDR'→增殖期糖网条目); tissue 可选过滤组织端。
    仅证据与 QC 旗, 禁入打分。"""
    priors = _load_priors()
    dis = (disease or "").strip().lower()
    alias = {"pdr": "proliferative diabetic", "增殖期糖网": "proliferative diabetic",
             "增殖型糖尿病视网膜病变": "proliferative diabetic",
             "proliferative dr": "proliferative diabetic"}
    dis = alias.get(dis, dis)
    ti = (tissue or "").strip().lower()
    ddis = (lambda e: (e.get("disease") or "").lower())
    hits = [e for e in priors.values()
            if (ddis(e) and dis and dis in ddis(e))
            or dis in (e.get("entry_id", "").lower())
            or any(dis in w for w in (e.get("title", "") or "").lower().split()[:6])]
    if not hits and dis:
        hits = [e for e in priors.values()
                if e.get("disease") and (set(dis.split()) & set(ddis(e).split()))]
    # 疾病判定条 (kb/priors/disease/, 带预期矩阵) 优先于组成条 (composition/);
    # KB1v2: 新 schema 薄层条目 (disease_v2) 优先于 v1 疾病条
    hits.sort(key=lambda e: (0 if e.get("_kind") == "disease_v2" else
                             (1 if e.get("expected_cell_state_matrix") else 2)))
    if not hits:
        return {"error": f"无匹配疾病条目: {disease!r}",
                "available": [{"entry_id": e["entry_id"], "disease": e.get("disease")}
                              for e in priors.values() if e.get("disease")]}
    entry = hits[0]
    matrix = entry.get("expected_cell_state_matrix") or []
    if ti:
        matrix = [m for m in matrix if ti in (m.get("tissue") or "").lower()]
    src = _resolve_sources(entry)
    for m in entry.get("expected_cell_state_matrix") or []:
        m["sources_resolved"] = [src.get(s, {"sid": s, "MISSING": True})
                                 for s in m.get("source_ids", [])]
    resp = {"entry_id": entry["entry_id"], "title": entry["title"],
            "disease": entry.get("disease"), "species": entry.get("species"),
            "organism_stage": entry.get("organism_stage",
                                        "unannotated(v1 存档条)"),  # KB2c 条款6: 断言必带发育档
            "tissue_scope": entry.get("tissue_scope"),
            "expected_cell_state_matrix": matrix,
            "unexpected_flags": entry.get("unexpected_flags"),
            "contamination_flags": entry.get("contamination_flags"),
            "signatures": entry.get("signatures"),
            "caveats": entry.get("caveats"),
            "provenance": src, "source_file": entry["_file"],
            "usage_redline": ("判读对照与 QC 旗专用; 禁止转成 module score/标签加权/置信度加分/候选排序分/"
                              "复合 QC 分数 (KB1v2 红线1, REVIEWER_LLM T3 扩展表述全继承)")}
    # KB1v2-W2 (T4/T2): 薄层条目透传身份层级/状态轴/证据条件/错配警示
    if entry.get("_kind") == "disease_v2":
        resp.update({
            "schema_version": entry.get("schema"),
            "context": entry.get("context"),
            "usage_scope": entry.get("usage_scope"),
            "sampling_mismatch_warning": entry.get("sampling_mismatch_warning"),
            "identity_hierarchies": entry.get("identity_hierarchies"),
            "state_axes": entry.get("state_axes"),
            "signature_evidence_T4": entry.get("signature_evidence_T4"),
            "unexpected_disposition_queues": entry.get("unexpected_disposition_queues"),
            "minimum_usability_criteria": entry.get("minimum_usability_criteria"),
            "matrix_anchor": entry.get("matrix_anchor"),
        })
    return resp


# ------------------------------------------------- reason-tag 联表 (K3→KB1v2-W4 三字段)
REASON_SIDECAR = (EYEKB_ROOT / "kb" / "literature_db" /
                  "evidence_meta_v2.0_2026-09.jsonl")
_REASON_SIDECAR_V1 = (EYEKB_ROOT / "kb" / "literature_db" /
                      "inclusion_reason_v2.0_2026-09.jsonl")  # v1 存档, 只读
_reason_cache = {"mtime": None, "map": {}}


def _reason_map():
    try:
        mt = REASON_SIDECAR.stat().st_mtime
    except Exception:
        return {}
    if _reason_cache["mtime"] != mt:
        _reason_cache["map"] = {}
        with open(REASON_SIDECAR, encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                    _reason_cache["map"][str(d["pmid"])] = {
                        "inclusion_reason": d["inclusion_reason"],
                        "reason_confidence": d["confidence"],
                        "reason_method": d.get("matched_rule", ""),
                        # KB1v2-W4 (REVIEWER_LLM T5) 三字段透传: 多选 + 论断关系 + 证据条件
                        "inclusion_reasons": d.get("inclusion_reasons"),
                        "claim_relation": d.get("claim_relation"),
                        "evidence_context": d.get("evidence_context"),
                        "evidence_verification_status": d.get("verification_status"),
                    }
                except Exception:
                    continue
        _reason_cache["mtime"] = mt
    return _reason_cache["map"]


if __name__ == "__main__":
    # 无 MCP 的最小自测 (核心层)
    print(json.dumps(query_marker(cell_type="RPE", library="retina"), ensure_ascii=False)[:400])
    print(json.dumps(query_marker(cell_type="Endo")["found"], ensure_ascii=False))
    print(json.dumps(get_kb_page("topic", "vascular")["file"], ensure_ascii=False))
    print(json.dumps(get_kb_page("topic", "../../etc/passwd"), ensure_ascii=False))

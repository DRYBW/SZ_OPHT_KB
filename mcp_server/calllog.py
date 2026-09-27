#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""calllog — EyeKB MCP 服务端调用留痕层（OBS1 t_c754c4fc，2026-09-26）

═══ 定位与红线 ═══
- **只加日志、零行为改动**：本模块只读取工具响应做结构摘要后落盘，绝不修改
  resp / 返回值 / 排序 / soft_flags；trace() 整体 try/except 兜底，留痕失败
  绝不影响服务（返回路径无新异常源）。
- 依据：BRIEF_OBS1.md OBS-1（盘点结论=服务端零留痕，须补日志层）+
  USER_DIRECTIVE_20260926 A2 观察条款（一周真实流量跟票采样需要调用侧数据源）。
- 不动 server.py 的异常语义：工具函数抛错时 trace 不被调用（与改前一致）。

═══ 落盘与轮转 ═══
- 路径：/mnt/D/EyeKB/logs/mcp_trace/calls_YYYY-MM-DD.jsonl（本地日期，按日
  自然轮转；单文件超 200MB 时续写 calls_YYYY-MM-DD.part<N>.jsonl）。
- 追加式（O_APPEND 行级原子写，多会话并发 spawn 安全）；不自动删除——
  观察窗证据保留满一月复盘后由协调者裁定归档（A4 卡）。

═══ 脱敏口径 ═══
- 记：工具名、入参（科学检索词：基因/细胞类型/组织/文献 query——领域信息，
  非个人敏感）、响应**结构摘要**（mode、found、类目名清单、soft_flag 的
  flag_id 列表、provenance 库集与 lacrimal 布尔、命中计数）。
- 不记：soft_flags notes 全文、文献片段正文、detail 面板基因全表、基线数值表
  内容（体积与语料落盘控制；flag_id 与类目名已足够支撑 OBS-2 两口径统计）。
- 会话侧信息：进程 uuid/pid/宿主/父进程 cmdline（消费方归因）+ 可选 env
  EYEKB_MCP_TRACE_TAG（自测流量打标，统计器默认排除；真实消费不设即空）。

═══ 环境态 ═══
- 每条记录附 EYEKB_ACT_V6 与 EYEKB_MCP_SOFTFLAGS 的 raw 值 + effective 判定
  （ON/OFF 与 softflags 开关语义逐字照抄 _v6_act_enabled()/softflags.enabled()
  的 {0,false,off,no} casefold 集合，不另造判定）。
"""
import json
import os
import socket
import time
import uuid

TRACE_DIR = "/mnt/D/EyeKB/logs/mcp_trace"
MAX_DAY_BYTES = 200 * 1024 * 1024  # 200MB 后写 .part<N>

_OFF_VALUES = {"0", "false", "off", "no"}

_SESSION = {
    "session_uuid": uuid.uuid4().hex[:12],
    "pid": os.getpid(),
    "ppid": os.getppid(),
    "host": socket.gethostname(),
    "proc_started": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "tag": (os.environ.get("EYEKB_MCP_TRACE_TAG") or "").strip()[:64],
    "caller": "",
}


def _caller_cmdline():
    """父进程 cmdline（消费方归因，best-effort，300 字符截断）。"""
    try:
        with open(f"/proc/{_SESSION['ppid']}/cmdline", "rb") as f:
            return f.read().replace(b"\0", b" ").decode("utf-8", "replace")\
                     .strip()[:300]
    except Exception:
        return ""


try:
    _SESSION["caller"] = _caller_cmdline()
except Exception:
    pass


def _env_state():
    act = os.environ.get("EYEKB_ACT_V6")
    sf = os.environ.get("EYEKB_MCP_SOFTFLAGS")
    act_off = (act or "").strip().casefold() in _OFF_VALUES
    # softflags.enabled() 语义核对：softflags.py L100-103 为
    # strip().casefold() ∈ {0,false,off,no} → off；其余值（含未设）一律 on。
    # EYEKB_ACT_V6 语义：未设/其余值 = ON（eyekb_core._v6_act_enabled）。
    sf_off = (sf or "").strip().casefold() in _OFF_VALUES if sf is not None else False
    return {
        "EYEKB_ACT_V6_raw": act, "act_v6_on": (not act_off),
        "EYEKB_MCP_SOFTFLAGS_raw": sf, "softflags_on": (not sf_off),
    }


def _args_safe(args, limit=6000):
    try:
        s = json.dumps(args, ensure_ascii=False, default=str)
    except Exception:
        s = repr(args)
    if len(s) > limit:
        return {"args_trunc_json": s[:limit], "args_truncated": True}
    try:
        return json.loads(s)
    except Exception:
        return {"args_unserializable": s[:limit]}


def _resp_digest(tool, resp):
    """响应结构摘要（只读；任何解析失败退化为 keys 清单）。"""
    d = {"resp_type": type(resp).__name__}
    try:
        if not isinstance(resp, dict):
            d["resp_keys"] = None
            return d
        keys = sorted(resp.keys())
        d["resp_keys"] = keys
        if tool == "query_marker":
            prov = resp.get("provenance") or {}
            files = prov.get("files") or []
            d["libs"] = sorted({f.get("library") for f in files if f.get("library")})
            d["lacrimal_in_prov"] = any(
                "lacrimal" in str(f.get("path", "")).lower()
                or "lacrimal" == str(f.get("library", "")).lower() for f in files)
            notes = (resp.get("soft_flags") or {}).get("notes") or []
            d["soft_flag_ids"] = sorted({str(n.get("flag_id")) for n in notes
                                         if isinstance(n, dict) and n.get("flag_id")})
            mode = resp.get("mode")
            d["mode"] = mode
            if mode == "list":
                ct = resp.get("cell_types") or []
                d["n_classes"] = len(ct)
                d["classes"] = [str(c)[:80] for c in ct][:80]
            elif mode == "cell_type":
                d["query"] = str(resp.get("query", ""))[:80]
                d["found"] = bool(resp.get("found"))
                d["hit_classes"] = [str(c)[:80] for c in (resp.get("markers") or {})]
            elif mode == "genes":
                d["n_ranking"] = len(resp.get("celltype_ranking") or [])
                d["ranking_classes_top"] = [
                    str(r.get("cell_type", ""))[:80]
                    for r in (resp.get("celltype_ranking") or [])[:20]]
                g2c = resp.get("gene_to_celltypes") or {}
                d["n_genes_queried"] = len(g2c)
                d["n_genes_hit"] = sum(1 for v in g2c.values() if v)
        elif tool == "search_literature":
            rs = resp.get("results") or []
            d["n_results"] = len(rs)
            d["pmids"] = sorted({str(r.get("pmid")) for r in rs
                                 if isinstance(r, dict) and r.get("pmid")})[:30]
        elif tool == "get_kb_page":
            d["found"] = bool(resp.get("found", resp.get("file")))
            d["file"] = str(resp.get("file", ""))[:120]
        elif tool == "get_tissue_composition":
            es = resp.get("entries") or resp.get("composition") or []
            d["n_entries"] = len(es) if isinstance(es, (list, dict)) else None
        elif tool == "get_disease_prior":
            d["found"] = bool(resp.get("found", resp.get("priors")))
    except Exception as e:
        d["digest_error"] = str(e)[:120]
    return d


def _target_file():
    day = time.strftime("%Y-%m-%d")
    base = os.path.join(TRACE_DIR, f"calls_{day}.jsonl")
    if not os.path.exists(base) or os.path.getsize(base) < MAX_DAY_BYTES:
        return base
    n = 2
    while True:
        p = os.path.join(TRACE_DIR, f"calls_{day}.part{n}.jsonl")
        if not os.path.exists(p) or os.path.getsize(p) < MAX_DAY_BYTES:
            return p
        n += 1


def trace(tool, args, resp):
    """工具返回后调用一次；只写盘、只读、异常全兜底。"""
    try:
        rec = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "tool": tool,
            "args": _args_safe(args),
        }
        rec.update(_env_state())
        rec.update({"session": _SESSION["session_uuid"], "pid": _SESSION["pid"],
                    "ppid": _SESSION["ppid"], "host": _SESSION["host"],
                    "tag": _SESSION["tag"], "caller": _SESSION["caller"]})
        rec["resp"] = _resp_digest(tool, resp)
        os.makedirs(TRACE_DIR, exist_ok=True)
        line = json.dumps(rec, ensure_ascii=False, default=str)
        with open(_target_file(), "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        # 留痕失败绝不允许影响服务行为（静默；不打 stdout——stdio 协议通道）
        pass

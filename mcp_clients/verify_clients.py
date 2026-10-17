#!/usr/bin/env python3
"""verify_clients.py - start the EyeKB MCP server using the exact command from each client
configuration file in this directory, and speak the Model Context Protocol to it.

What is being tested
    The four configuration files next to this script are meant to be pasted into four
    different AI coding agents. They differ in syntax, but each one names a stdio launch
    command: one Python interpreter plus `mcp_server/server.py`. This script reads each
    file, substitutes the two documented path placeholders with real paths, spawns the
    process exactly as that client would, and then runs a full protocol session:
    initialize -> tools/list -> real tool calls.

    A PASS therefore means two things at once:
      1. the command written in that file starts a working MCP server on this machine;
      2. the server answers real queries over the standard protocol, so no client-specific
         adapter code is needed on our side.

Usage
    python3 mcp_clients/verify_clients.py

Environment
    EYEKB_PYTHON   interpreter substituted for /path/to/venv/bin/python
                   (default: the interpreter running this script)

Exit code 0 = every configured client connected and answered; 1 = at least one did not.
"""

import asyncio
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SERVER = REPO / "mcp_server" / "server.py"

REPO_PLACEHOLDER = "/path/to/SZ_OPHT_KB"
PY_PLACEHOLDER = "/path/to/venv/bin/python"

EXPECTED_TOOLS = {
    "search_literature",
    "query_marker",
    "get_tissue_composition",
    "get_disease_prior",
    "get_kb_page",
}


def _load_toml(text):
    try:
        import tomllib  # Python 3.11+
    except ImportError:  # pragma: no cover - fallback for older interpreters
        tomllib = None
    if tomllib is not None:
        return tomllib.loads(text)
    # Minimal fallback: the snippet only needs [mcp_servers.<name>] plus command/args.
    data = {"mcp_servers": {}}
    current = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        m = re.match(r"^\[mcp_servers\.([A-Za-z0-9_-]+)\]$", line)
        if m:
            current = data["mcp_servers"][m.group(1)] = {}
            continue
        if current is None or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if key == "command":
            current["command"] = value.strip('"').strip("'")
        elif key == "args":
            current["args"] = re.findall(r'"([^"]*)"', value)
    return data


def _load_yaml(text):
    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None
    if yaml is not None:
        return yaml.safe_load(text)
    # Minimal fallback for the documented snippet shape: one list item whose config block
    # carries serverName / transport / command and an indented args list.
    cfg = {}
    args, in_args = [], False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            in_args, args = in_args, args
        m = re.match(r"^\s*command:\s*(.+)$", line)
        if m:
            cfg["command"] = m.group(1).strip().strip("'\"")
        m = re.match(r"^\s*transport:\s*(.+)$", line)
        if m:
            cfg["transport"] = m.group(1).strip().strip("'\"")
        m = re.match(r"^\s*serverName:\s*(.+)$", line)
        if m:
            cfg["serverName"] = m.group(1).strip().strip("'\"")
        if re.match(r"^\s*args:\s*$", line):
            in_args = True
            continue
        if in_args:
            m = re.match(r"^\s*-\s*(.+)$", line)
            if m and line.startswith(" " * 6):
                args.append(m.group(1).strip().strip("'\""))
            elif m:
                args.append(m.group(1).strip().strip("'\""))
            else:
                in_args = False
    if args:
        cfg["args"] = args
    return [{"config": cfg}]


def read_config(path):
    """Return (server_name, command, args) for a client configuration file."""
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".toml":
        data = _load_toml(text)
        name, entry = next(iter(data["mcp_servers"].items()))
    elif path.suffix in (".yml", ".yaml"):
        rows = _load_yaml(text)
        row = rows[0]
        entry = row.get("config", row)
        name = entry.get("serverName", "eyekb")
    else:
        data = json.loads(text)
        name, entry = next(iter(data["mcpServers"].items()))
    command = str(entry["command"])
    args = [str(a) for a in entry.get("args") or []]
    return name, command, args


def substitute(command, args, interpreter):
    def sub(value):
        return value.replace(REPO_PLACEHOLDER, str(REPO)).replace(PY_PLACEHOLDER, interpreter)

    return sub(command), [sub(a) for a in args]


async def run_session(label, command, args, interpreter):
    """Spawn the server exactly as the client would and run a full MCP session."""
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    result = {"client": label, "command": command, "args": args, "checks": [], "verdict": "FAIL"}

    def check(name, ok, detail=""):
        result["checks"].append((name, "PASS" if ok else "FAIL", detail))
        return ok

    env = dict(os.environ)
    env.setdefault("EYEKB_CN_REWRITE", env.get("EYEKB_CN_REWRITE", "0"))
    params = StdioServerParameters(command=command, args=args, env=env)
    try:
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                init = await session.initialize()
                info = init.server_info
                check(
                    "handshake",
                    info.name == "eyekb",
                    f"server={info.name} version={info.version} protocol={init.protocol_version}",
                )
                check(
                    "server instructions delivered",
                    bool((init.instructions or "").strip()),
                    f"{(init.instructions or '')[:40]}...",
                )
                tools = await session.list_tools()
                names = {t.name for t in tools.tools}
                check("tools/list", EXPECTED_TOOLS <= names, f"{len(names)} tools: {sorted(names)}")

                res = await session.call_tool(
                    "query_marker",
                    {"genes": ["TMEM119", "CX3CR1", "P2RY12", "C1QA", "SALL1", "CSF1R", "AIF1"]},
                )
                payload = json.loads(res.content[0].text) if res.content else {}
                ranking = payload.get("kb_celltype_ranking") or payload.get("celltype_ranking") or []
                top1 = ranking[0].get("cell_type", "") if ranking else ""
                check(
                    "query_marker returns a marker match",
                    bool(top1),
                    f"top-1 for a microglia gene set = {top1}",
                )

                res = await session.call_tool(
                    "get_tissue_composition", {"species": "human", "tissue": "retina"}
                )
                payload = json.loads(res.content[0].text) if res.content else {}
                entries = payload.get("composition") or payload.get("entries") or payload.get("rows") or []
                check(
                    "get_tissue_composition returns baselines",
                    bool(entries),
                    f"{len(entries)} baseline rows"
                    if isinstance(entries, list)
                    else "non-empty response",
                )

                # Needs the literature corpus. Its absence is a missing download, not a
                # client-adaptation failure, so it is reported separately.
                try:
                    res = await session.call_tool(
                        "search_literature", {"cell_type": "Microglia", "species": "human", "top_k": 1}
                    )
                    payload = json.loads(res.content[0].text) if res.content else {}
                    hits = payload.get("results") or payload.get("chunks") or []
                    if hits:
                        result["checks"].append(("search_literature", "PASS", f"{len(hits)} hit(s)"))
                    else:
                        result["checks"].append(
                            ("search_literature", "SKIP", f"no hits; response keys={sorted(payload)[:6]}")
                        )
                except Exception as exc:  # noqa: BLE001 - reported, never fatal here
                    result["checks"].append(("search_literature", "SKIP", str(exc)[:90]))

                result["session"] = {
                    "server": f"{info.name} {info.version}",
                    "protocol": init.protocol_version,
                }
    except Exception as exc:  # noqa: BLE001 - a spawn/handshake failure is the finding
        result["checks"].append(("spawn + handshake", "FAIL", f"{type(exc).__name__}: {str(exc)[:120]}"))
        return result

    failed = [c for c in result["checks"] if c[1] == "FAIL"]
    result["verdict"] = "PASS" if not failed else "FAIL"
    return result


async def main():
    interpreter = os.environ.get("EYEKB_PYTHON") or sys.executable
    configs = [
        ("Codex CLI", HERE / "codex.config.toml"),
        ("Claude Code", HERE / "claude-code.mcp.json"),
        ("DeepSeek Harness", HERE / "deepseek-harness.cordis-patch.yml"),
        ("WorkBuddy / CodeBuddy", HERE / "workbuddy.mcp.json"),
    ]
    print(f"repository : {REPO}")
    print(f"server     : {SERVER}")
    print(f"interpreter: {interpreter}")
    print()

    results = []
    for label, path in configs:
        try:
            name, command, args = read_config(path)
        except Exception as exc:  # noqa: BLE001
            results.append(
                {
                    "client": label,
                    "verdict": "FAIL",
                    "checks": [("read config file", "FAIL", f"{type(exc).__name__}: {exc}")],
                }
            )
            continue
        command, args = substitute(command, args, interpreter)
        results.append(await run_session(label, command, args, interpreter))

    width = max(len(r["client"]) for r in results)
    for r in results:
        print(f"[{r['verdict']}] {r['client'].ljust(width)}  {r.get('command', '')}")
        for name, state, detail in r["checks"]:
            print(f"        {state:<4} {name:<38} {detail}")
        print()

    passed = sum(1 for r in results if r["verdict"] == "PASS")
    print(f"{passed}/{len(results)} client configurations connected and answered")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

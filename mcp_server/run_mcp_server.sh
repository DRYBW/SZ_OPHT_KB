#!/usr/bin/env bash
# run_mcp_server.sh - start the EyeKB MCP server over stdio.
#
# Why this wrapper exists: server.py needs no arguments of its own; the only thing that
# varies between machines is *which* Python interpreter has the `mcp` package installed.
# This script resolves that for you, so one client configuration line works after clone.
#
# Interpreter resolution order:
#   1. $EYEKB_PYTHON             explicit override
#   2. <repo>/.venv/bin/python   usual virtualenv location
#   3. <repo>/venv/bin/python
#   4. python3 on PATH           (fall back to `python` if python3 is absent)
#
# Any extra arguments are forwarded to server.py.
# Nothing is ever written to stdout: stdout is the MCP channel itself.

set -u

_src="${BASH_SOURCE[0]}"
_dir="${_src%/*}"
[ "$_dir" = "$_src" ] && _dir="."
HERE="$(cd "$_dir" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"

PY=""
if [ -n "${EYEKB_PYTHON:-}" ]; then
  PY="$EYEKB_PYTHON"
elif [ -x "$REPO/.venv/bin/python" ]; then
  PY="$REPO/.venv/bin/python"
elif [ -x "$REPO/venv/bin/python" ]; then
  PY="$REPO/venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PY="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PY="$(command -v python)"
else
  printf '%s\n' "run_mcp_server.sh: no Python interpreter found; set EYEKB_PYTHON to one that has 'mcp' installed" >&2
  exit 127
fi

# Check the exact import the server performs, not just `import mcp`: the server is written
# against the MCPServer class of MCP Python SDK 2.x, and an older SDK fails at startup with
# a bare ImportError that tells the user nothing.
if ! "$PY" -c 'from mcp.server import MCPServer' >/dev/null 2>&1; then
  printf '%s\n' "run_mcp_server.sh: '$PY' cannot import 'mcp.server.MCPServer'." \
    "The server needs the MCP Python SDK 2.x (see requirements.repro.txt)." \
    "Install the dependencies first, or set EYEKB_PYTHON to an interpreter that has them." >&2
  exit 126
fi

exec "$PY" "$HERE/server.py" "$@"

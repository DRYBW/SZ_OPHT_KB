# Connecting EyeKB to your AI coding agent

The EyeKB literature and knowledge service is a plain [Model Context Protocol](https://modelcontextprotocol.io)
server over stdio. It needs nothing from any particular agent framework, so the same
server plugs into every MCP-capable client. This directory holds a ready-made
configuration file per client, plus a script that starts the server with the exact command
written in each file and checks that it answers.

| Client | File to use | Where the configuration goes |
|---|---|---|
| OpenAI Codex CLI | `codex.config.toml` | `~/.codex/config.toml`, or `.codex/config.toml` in a trusted project |
| Claude Code | `claude-code.mcp.json` | `.mcp.json` at the root of your project, or `claude mcp add` |
| DeepSeek Harness (dsh) | `deepseek-harness.cordis-patch.yml` | a plugin entry in the composition of the profile you run |
| WorkBuddy / CodeBuddy | `workbuddy.mcp.json` | `~/.workbuddy/mcp.json`, `<project>/.workbuddy/mcp.json`, or `.mcp.json` for the CodeBuddy CLI |

## What you have to edit

Each file contains the same two placeholders. Replace them before use:

| Placeholder | Replace with |
|---|---|
| `/path/to/SZ_OPHT_KB` | the directory you cloned this repository into |
| `/path/to/venv/bin/python` | an interpreter that has the `mcp` package installed (see "Install" in the repository README) |

Neither path may contain `~` or `$HOME`: the clients start the server directly, not
through a shell, so nothing expands them.

If you would rather not pin an interpreter, point `command` at
`<repo>/mcp_server/run_mcp_server.sh` with an empty argument list. That launcher picks a
Python interpreter for you: `$EYEKB_PYTHON` first, then `<repo>/.venv`, then `python3` on
`PATH`. It needs the executable bit and a POSIX shell, so it is not an option on Windows.

## Verify before you trust it

```bash
python3 mcp_clients/verify_clients.py
```

The script reads all four configuration files, substitutes the placeholders with the real
paths, starts the server once per file using exactly the command that file specifies, and
runs a full protocol session against each: handshake, tool listing, a marker query, and a
composition query. It prints one line per check and ends with `4/4 client configurations
connected and answered`. A failure inside one client's configuration therefore points at
that file, not at the server.

The literature query needs the retrieval corpus (a separate download, see README step 2).
Without it that single check reports `SKIP`; the other four tools read the repository's own
knowledge files and work immediately after clone.

## Per-client notes

### OpenAI Codex CLI

Paste the block from `codex.config.toml` into `~/.codex/config.toml` (all projects) or into
`.codex/config.toml` inside a project Codex trusts. Restart Codex, then type `/mcp` in the
TUI: `eyekb` should appear with five tools. The same file serves the CLI and the IDE
extension. Without editing a file:

```bash
codex mcp add eyekb -- /path/to/venv/bin/python /path/to/SZ_OPHT_KB/mcp_server/server.py
```

Documentation: <https://developers.openai.com/codex/mcp>

### Claude Code

Copy `claude-code.mcp.json` to `.mcp.json` at the root of your project, or register the
server once for your user account:

```bash
claude mcp add --transport stdio eyekb -- /path/to/venv/bin/python /path/to/SZ_OPHT_KB/mcp_server/server.py
```

Check it with `/mcp` inside Claude Code. Documentation:
<https://code.claude.com/docs/en/mcp>

### DeepSeek Harness (dsh)

DeepSeek Harness takes MCP servers as plugin entries: one
`@deepseek-ai/dsh-mcp-client` row per server, in the composition of the profile you run.
`deepseek-harness.cordis-patch.yml` is that row with our command filled in. Tools are then
offered to the model as `mcp__eyekb__<tool>`. If you prefer a graphical route, the community
`dsh-mcp-manager` plugin adds a Settings → MCP page with a `stdio` mode that takes the same
command and arguments; it writes its servers into `<workspace>/.dsh/dshmm/mcp.json` in the
same style as the Claude Code file above, which you can paste there unchanged.

Documentation: <https://github.com/deepseek-ai/deepseek-harness/blob/main/docs/subsystems/mcp.md>

### WorkBuddy and CodeBuddy (Tencent)

WorkBuddy reads MCP servers from `~/.workbuddy/mcp.json` (all projects) or
`<project>/.workbuddy/mcp.json` (one project); the desktop app also has a configuration
editor under Settings → Plugins → MCP Servers. The CodeBuddy CLI reads `.mcp.json` at the
project root. Both accept the same `mcpServers` block, which is `workbuddy.mcp.json` here —
the `type: "stdio"` field is required by the CodeBuddy CLI. From the command line:

```bash
# register for the current user
codebuddy mcp add-json --scope user eyekb \
  '{"type":"stdio","command":"/path/to/venv/bin/python","args":["/path/to/SZ_OPHT_KB/mcp_server/server.py"]}'

# in non-interactive runs, approve the project server explicitly
codebuddy --settings '{"enabledMcpjsonServers":["eyekb"]}' -p "your prompt"
```

Project-scoped servers need a one-time approval in the CLI the first time they connect.
Documentation: <https://www.workbuddy.ai/docs/cli/mcp>

## What the agent sees

After connecting, the client discovers five tools and the usage note that the server sends
during the handshake (clients that support server instructions pass them to the model
automatically; others show the tool descriptions):

| Tool | Ask it for |
|---|---|
| `query_marker` | what cell type a set of marker genes points to, or which markers define a cell type |
| `search_literature` | passages from the local ophthalmology corpus, with PMID, journal and year |
| `get_tissue_composition` | expected cell-type proportions in normal eye tissue, per donor |
| `get_disease_prior` | disease-by-tissue background, identity hierarchy and sampling cautions |
| `get_kb_page` | a knowledge-base page as written (index / topic / tissue) |

One boundary travels with the service into every client: the returned evidence is for a
human to read and judge, and must never be consumed as a training or scoring signal by an
automatic classifier. That sentence is part of the server's own instructions, so an agent
that reads them sees the constraint without any extra setup.

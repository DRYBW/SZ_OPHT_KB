"""Console entry point: run the EyeKB MCP server over stdio.

Installed as the ``eyekb-mcp`` command, and usable straight from the repository without an
installation:

    uvx --from git+https://github.com/DRYBW/SZ_OPHT_KB.git eyekb-mcp

The literature corpus for ``search_literature`` is distributed separately (it is far larger than
a Python package should carry); download it from the repository's Releases page and point
``EYEKB_DB_DIR`` at the unpacked directory. The other four tools read the knowledge base that
ships inside this package and work with no configuration.
"""
from __future__ import annotations


def main() -> None:
    """Run the server on stdio."""
    from mcp_server import server

    server.app.run(transport="stdio")


if __name__ == "__main__":
    main()
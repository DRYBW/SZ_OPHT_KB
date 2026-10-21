"""EyeKB MCP server package.

The server runs over local stdio and exposes five read-only tools backed by the knowledge base
that ships inside this distribution (kb/ and clients/ocularkb/rag/scripts/). The module
``server`` holds the tool definitions; ``__main__`` is the console entry point.
"""
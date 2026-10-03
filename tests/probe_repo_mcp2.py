import asyncio, json, os, re, sys, pathlib
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PY = os.environ.get("EYEKB_PROBE_PY", sys.executable)
SRV = str(pathlib.Path(__file__).resolve().parents[1] / "mcp_server" / "server.py")

async def run(env_extra, label):
    env = dict(os.environ); env.update(env_extra)
    sp = StdioServerParameters(command=PY, args=[SRV], env=env)
    async with stdio_client(sp) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            out = {}
            for tool in ["get_tissue_composition", "query_marker"]:
                try:
                    if tool == "get_tissue_composition":
                        res = await s.call_tool(tool, {"species": "human", "tissue": "retina"})
                    else:
                        res = await s.call_tool(tool, {"genes": ["KRT12","PAX6","ALDH1A1","MLANA","TYR","SOX10","LMX1B","KERA"]})
                    txt = res.content[0].text if res.content else "{}"
                    classes = set(re.findall(r"'cell_type': '([^']+)'", txt)) | set(re.findall(r'"cell_type": "([^"]+)"', txt)) | set(re.findall(r"'class': '([^']+)'", txt))
                    out[tool] = {"n_classes": len(classes), "sample": sorted(classes)[:6], "leak_lacrimal": sorted([c for c in classes if re.search(r"lacr|腺泡|导管|acinar|duct", c, re.I)])}
                except Exception as e:
                    out[tool] = {"error": str(e)[:120]}
            print(label, json.dumps(out, ensure_ascii=False))

async def main():
    await run({"EYEKB_ACT_V6": "1"}, "ON:")
    await run({"EYEKB_ACT_V6": "0"}, "OFF:")

asyncio.run(main())

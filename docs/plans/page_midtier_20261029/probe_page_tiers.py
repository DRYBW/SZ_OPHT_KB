#!/usr/bin/env python
"""Measure the page views through the real stdio server, and check the numbers independently.

Three kinds of reading land in one file:

  * server readings — characters, md5, and the view fields the tool reports;
  * independent recomputation — the probe re-derives the outline numbers from the full page text
    with its own code (separate regex, separate counters), so an outline that agrees with the probe
    agrees with something that did not come from the tool it is checking;
  * a losslessness walk — every page is walked in slices of an awkward size (37 lines, or 997 on the
    two very large pages so the walk stays cheap), the returned lines are concatenated with a
    newline, and the md5 of the result is compared with the md5 of the same page fetched whole.

Pages are enumerated from the tool's own inventory, not from a hand-written list, so coverage is
measured over what the service says exists.

Usage:
    EYEKB_REPO_ROOT=/home/ubuntu/EYEKB_REPO UX_PY=/home/ubuntu/.conda/envs/pipeline_env/bin/python \
    python probe_page_tiers.py --label after --out out/AFTER.json
"""
import argparse
import asyncio
import hashlib
import json
import os
import re
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

REPO = os.environ.get("EYEKB_REPO_ROOT", "/home/ubuntu/EYEKB_REPO")
PY = os.environ.get("UX_PY", sys.executable)
SRV = os.path.join(REPO, "mcp_server", "server.py")

SINGLE_CASES = [
    ("cornea_full", "get_kb_page", {"scope": "tissue", "name": "cornea", "detail": "full"}),
    ("vascular_full", "get_kb_page", {"scope": "topic", "name": "vascular", "detail": "full"}),
    ("index_full", "get_kb_page", {"scope": "index", "detail": "full"}),
    ("index_default", "get_kb_page", {"scope": "index"}),
    ("cornea_default", "get_kb_page", {"scope": "tissue", "name": "cornea"}),
    ("iris_default", "get_kb_page", {"scope": "tissue", "name": "iris"}),
    ("models_default", "get_kb_page", {"scope": "topic", "name": "models"}),
    ("cornea_outline", "get_kb_page", {"scope": "tissue", "name": "cornea", "detail": "outline"}),
    ("cornea_slice", "get_kb_page", {"scope": "tissue", "name": "cornea", "detail": "slice",
                                     "offset": 0, "limit": 100}),
    ("cornea_slice_bad", "get_kb_page", {"scope": "tissue", "name": "cornea", "detail": "slice",
                                         "offset": -1, "limit": 10}),
    ("composition_default", "get_tissue_composition", {"species": "human", "tissue": "retina"}),
]


def md5(text):
    return hashlib.md5(text.encode()).hexdigest()


def recompute_outline(text):
    """Independent derivation of what the outline claims: headings, section sizes, paper counts.

    Deliberately written from the page text with its own regexes and counters, not by importing the
    server's helpers — the point is that the two implementations have to agree.
    """
    lines = text.split("\n")
    body_start = 0
    front = {}
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                for ln in lines[1:i]:
                    k, _, v = ln.partition(":")
                    if k.strip():
                        front[k.strip()] = v.strip()
                body_start = i + 1
                break
    sections = []
    for idx in range(body_start, len(lines)):
        ln = lines[idx]
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            sections.append({"level": len(m.group(1)), "heading": m.group(2).strip(),
                             "start_line": idx + 1, "lines": 0, "chars": 0, "paper_rows": 0})
        elif sections:
            sections[-1]["lines"] += 1
            sections[-1]["chars"] += len(ln) + 1
            if ln.startswith("- PMID"):
                sections[-1]["paper_rows"] += 1
    years, papers = {}, 0
    for ln in lines:
        if ln.startswith("- PMID"):
            papers += 1
            m = re.search(r"\((\d{4})\)", ln)
            if m:
                years[m.group(1)] = years.get(m.group(1), 0) + 1
    return {"chars": len(text), "lines": len(lines), "front_matter": front,
            "sections": sections, "papers": {"rows": papers,
                                             "by_year": dict(sorted(years.items()))}}


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="run")
    ap.add_argument("--out", required=True)
    ap.add_argument("--env", action="append", default=[])
    args = ap.parse_args()
    extra = dict(p.partition("=")[::2] for p in args.env)

    env = dict(os.environ)
    env.pop("EYEKB_DEFAULT_DETAIL", None)
    env.update(extra)

    rec = {"label": args.label, "env_extra": extra, "single": {}, "pages": {}}
    sp = StdioServerParameters(command=PY, args=[SRV], env=env)

    async def call(s, tool, argv):
        res = await s.call_tool(tool, argv)
        txt = getattr(res.content[0], "text", "") if res.content else ""
        try:
            return txt, json.loads(txt)
        except Exception:
            return txt, None

    async with stdio_client(sp) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            rec["tools"] = len((await s.list_tools()).tools)

            for cid, tool, argv in SINGLE_CASES:
                txt, obj = await call(s, tool, argv)
                row = {"tool": tool, "args": argv, "chars": len(txt), "md5": md5(txt)}
                if isinstance(obj, dict):
                    for k in ("view", "detail", "detail_applied", "error",
                              "total_lines", "returned", "next_offset", "eof", "chars"):
                        if k in obj:
                            row[k] = obj[k]
                rec["single"][cid] = row

            # the inventory is the service's own answer to "what pages exist"
            _, inv = await call(s, "get_kb_page", {"scope": "index", "detail": "answer"})
            listed = (inv or {}).get("pages") if isinstance(inv, dict) else None
            if not isinstance(listed, list):
                listed = []
            rec["n_listed"] = len(listed)

            targets = [(p.get("scope"), p.get("page")) for p in listed
                       if isinstance(p, dict) and p.get("page")]
            for scope, name in targets:
                key = f"{scope}:{name}"
                ent = {}
                fut, fobj = await call(s, "get_kb_page",
                                       {"scope": scope, "name": name, "detail": "full"})
                otxt, oobj = await call(s, "get_kb_page",
                                        {"scope": scope, "name": name, "detail": "outline"})
                dtxt, dobj = await call(s, "get_kb_page", {"scope": scope, "name": name})
                stxt, sobj = await call(s, "get_kb_page",
                                        {"scope": scope, "name": name, "detail": "slice"})
                ent["default_chars"] = len(dtxt)
                ent["slice_default_chars"] = len(stxt)
                if isinstance(dobj, dict):
                    ent["default_view"] = dobj.get("view")
                    ent["default_applied"] = dobj.get("detail_applied")
                    ent["default_note"] = bool(dobj.get("detail_note"))
                if not isinstance(fobj, dict) or "content" not in fobj:
                    ent["error"] = (fobj or {}).get("error", "no content")
                    rec["pages"][key] = ent
                    continue
                full = fobj["content"]
                ent.update({"full_chars": len(full), "full_md5": md5(full),
                            "outline_chars": len(otxt), "outline_md5": md5(otxt),
                            "recomputed": recompute_outline(full)})
                # Keep the outline body only when the response really is an outline. Before this
                # card the same request fell through to the full page text, and storing a 200 KB
                # page body under an "outline" key would have made the reading file lie about what
                # it held — as well as making it 1.7 MB for no evidential gain.
                if isinstance(oobj, dict) and oobj.get("view") == "outline":
                    ent["outline"] = oobj
                else:
                    ent["outline_shape"] = "not an outline view: the request fell through to the full page text"

                step = 37 if len(full) < 60000 else 997
                collected, off, guard = [], 0, 0
                while True:
                    guard += 1
                    if guard > 20000:
                        ent["walk_error"] = "too many slices"
                        break
                    _, sobj2 = await call(s, "get_kb_page",
                                          {"scope": scope, "name": name, "detail": "slice",
                                           "offset": off, "limit": step})
                    if not isinstance(sobj2, dict) or "lines" not in sobj2:
                        ent["walk_error"] = (sobj2 or {}).get("error", "no lines")
                        break
                    collected.extend(sobj2["lines"])
                    if sobj2.get("eof"):
                        break
                    nxt = sobj2.get("next_offset")
                    if nxt is None or nxt == off:
                        ent["walk_error"] = "next_offset did not advance"
                        break
                    off = nxt
                rebuilt = "\n".join(collected)
                ent.update({"walk_step": step, "slices": guard, "rebuilt_lines": len(collected),
                            "rebuilt_md5": md5(rebuilt), "rebuild_identical": rebuilt == full})
                rec["pages"][key] = ent

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(rec, fh, indent=1, ensure_ascii=False, sort_keys=True)

    for k, v in rec["single"].items():
        print(f"single {k:22s} chars={v['chars']:>7} view={v.get('view')} applied={v.get('detail_applied')}")
    print(f"pages listed by the service: {rec['n_listed']}, walked: {len(rec['pages'])}")
    for k, v in rec["pages"].items():
        print(f"page   {k:28s} full={v.get('full_chars',0):>7} outline={v.get('outline_chars',0):>6} "
              f"default_view={v.get('default_view')} slices={v.get('slices')} "
              f"identical={v.get('rebuild_identical')}")


asyncio.run(main())
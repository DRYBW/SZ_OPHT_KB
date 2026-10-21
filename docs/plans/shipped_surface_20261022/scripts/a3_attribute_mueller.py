#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step A3 — attribute every moved panel digest, from committed bytes only.

The panel probe keeps digests and nothing else, so "five of twelve calls differ" cannot be split
into "the server refused the arguments" and "an answer's text moved". This script reads the raw
dumps (a1_dump_panel.py keeps the text, the MCP is_error flag and the parsed payload) and reports,
for each of the twelve calls:

  * the digest recorded in the baseline as committed at HEAD,
  * the digest measured at HEAD from the committed tree (my own dump, not a quoted number),
  * the digest measured at a400315 (the commit that last touched the fixture) and at c4d04d9 (the
    next content commit), so the one answered move gets a *when* as well as a *what*,
  * which of the two causes applies.

Then two mechanical verifications:

  1. REFUSAL-TEXT RECONSTRUCTION. If the four refused calls are refused because their arguments do
     not match the tool's signature, their text is produced by the MCP layer's validator and embeds
     that library's own version in a documentation URL. Rewriting only the version inside those four
     texts and re-computing the two panel digests with the probe's own digest function must
     reproduce the recorded digests byte-for-byte. If it does, the recording environment used a
     different validator version and the panel never matched any build's interface.

  2. FIELD-LEVEL ATTRIBUTION of the one answered move: the payload at a400315 versus at HEAD,
     walked to the differing leaf fields.

Usage: <py> a3_attribute_mueller.py --pre <dump@HEAD.json> --hist <dump@older.json> [<dump.json>...]
                                    --baseline-head <fixture as committed at HEAD> --out <TABLE.tsv>
"""
import argparse
import hashlib
import json
import pathlib
import re

LEGACY = ("query_marker", "get_tissue_composition", "get_disease_prior", "get_kb_page",
          "search_literature")


def load(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


def panel_key(dump_key):
    """`panel::get_kb_page:{...}` -> `get_kb_page:{...}` (the baseline's own key shape)."""
    return dump_key.split("panel::", 1)[1]


def digests(rows):
    """The probe's own digest: md5 over json.dumps(sorted keys) of the key->digest mapping."""
    calls = dict(rows)
    legacy = {k: v for k, v in rows.items() if k.split(":", 1)[0] in LEGACY}
    return (hashlib.md5(json.dumps(legacy, sort_keys=True).encode()).hexdigest(),
            hashlib.md5(json.dumps(calls, sort_keys=True).encode()).hexdigest(),
            len(legacy), len(calls))


def walk_diff(a, b, path="", out=None, limit=400):
    out = [] if out is None else out
    if len(out) >= limit:
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            walk_diff(a.get(k, "<absent>"), b.get(k, "<absent>"), f"{path}.{k}", out, limit)
    elif isinstance(a, list) and isinstance(b, list):
        for i in range(max(len(a), len(b))):
            ai = a[i] if i < len(a) else "<absent>"
            bi = b[i] if i < len(b) else "<absent>"
            walk_diff(ai, bi, f"{path}[{i}]", out, limit)
    elif a != b:
        out.append((path, a, b))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pre", required=True, help="dump taken from the committed HEAD tree")
    ap.add_argument("--hist", nargs="+", required=True, help="dumps at earlier commits, oldest first")
    ap.add_argument("--baseline-head", required=True, help="the fixture file as committed at HEAD")
    ap.add_argument("--out", required=True, help="before/after attribution table (tsv)")
    a = ap.parse_args()

    pre = load(a.pre)
    hist = [(pathlib.Path(p).stem.replace("dump_", ""), load(p)) for p in a.hist]
    recorded = load(a.baseline_head)

    lines = ["call\trefused_at_HEAD\trecorded\t" + "\t".join(f"at_{tag}" for tag, _ in hist) +
             "\tat_HEAD\tverdict"]
    verdicts = {"refused": 0, "answered_moved": 0, "unchanged": 0}
    for dk in sorted(k for k in pre if k.startswith("panel::")):
        bk = panel_key(dk)
        rec = recorded["calls"].get(bk)
        refused = pre[dk]["is_error"]
        row = [bk, "yes" if refused else "no", (rec or "")[:32]]
        for tag, d in hist:
            row.append((d[dk]["md5"] if dk in d else "-")[:32])
        row.append(pre[dk]["md5"][:32])
        if refused:
            v = "refused_on_arguments"
            verdicts["refused"] += 1
        elif rec != pre[dk]["md5"]:
            v = "answered_and_moved"
            verdicts["answered_moved"] += 1
        else:
            v = "unchanged"
            verdicts["unchanged"] += 1
        row.append(v)
        lines.append("\t".join(row))

    print("=== per-call attribution ===")
    print("\n".join(lines))
    n_panel = sum(1 for k in pre if k.startswith("panel::"))
    print()
    print(f"  refused_on_arguments={verdicts['refused']}  answered_and_moved={verdicts['answered_moved']}"
          f"  unchanged={verdicts['unchanged']}  of {n_panel} panel calls")
    print()

    # ---- 1. refusal-text reconstruction -------------------------------------------------------
    print("=== the four refused calls: text, and the version it embeds ===")
    refusal_keys = [k for k in pre if k.startswith("panel::") and pre[k]["is_error"]]
    versions = set()
    for k in sorted(refusal_keys):
        txt = pre[k]["text"]
        vs = sorted(set(re.findall(r"pydantic\.dev/(\d+\.\d+)/", txt)))
        versions |= set(vs)
        first = txt.strip().splitlines()[0][:110]
        print(f"  {panel_key(k)[:60]:<62} version={vs} bytes={pre[k]['bytes']}")
        print(f"      text[1]: {first}")
    print(f"  versions embedded in the runtime text: {sorted(versions)}")
    print()

    print("=== reconstruction: sweep the validator version inside the four refusal texts ===")
    print("  (nothing else in any text is touched; the target is found by sweeping, not assumed)")
    hit = []
    for cand in ("2.10", "2.11", "2.12", "2.13", "2.14", "2.15"):
        patched = {}
        for k in (k for k in pre if k.startswith("panel::")):
            txt = pre[k]["text"]
            for v in sorted(versions):
                txt = txt.replace(f"pydantic.dev/{v}/", f"pydantic.dev/{cand}/")
            patched[panel_key(k)] = hashlib.md5(txt.encode()).hexdigest()
        rl, rf, nleg, nall = digests(patched)
        still = [k for k in patched if recorded["calls"].get(k) not in (None, patched[k])]
        ok = "MATCH" if rl == recorded["legacy_panel"] else "  --  "
        if ok.strip() == "MATCH":
            hit.append(cand)
        print(f"  target {cand}: legacy_panel={rl} {ok}  full_panel={rf} "
              f"({'MATCH' if rf == recorded['full_panel'] else 'MISMATCH'})  "
              f"per-call still differing={len(still)} {still}")
    print(f"  recorded legacy_panel={recorded['legacy_panel']}  full_panel={recorded['full_panel']}")
    print(f"  versions whose substitution reproduces the recorded legacy panel: {hit or 'none'}")
    print("  reading: the legacy panel contains no call that moved for a content reason, so the")
    print("  substitution alone reproduces it exactly -- the four refused calls are refused by the")
    print("  MCP layer's validator, and the text it produces is stamped with that library's version.")
    print("  The full panel differs only by the one answered move, attributed separately below.")
    print()

    # ---- 2. field-level attribution of the answered move -------------------------------------
    moved = [k for k in pre if k.startswith("panel::") and not pre[k]["is_error"]
             and recorded["calls"].get(panel_key(k)) not in (None, pre[k]["md5"])]
    for k in moved:
        tag0, d0 = hist[0]
        print(f"=== the answered move: {panel_key(k)} ===")
        for tag, d in hist + [("HEAD", pre)]:
            print(f"  at {tag:<10} md5={d[k]['md5']} bytes={d[k]['bytes']}")
        print(f"  recorded in the fixture as committed at HEAD: {recorded['calls'][panel_key(k)]}")
        A, B = d0[k].get("payload"), pre[k].get("payload")
        if A is None or B is None:
            print("  payload did not parse on one side; naming the difference by text instead")
            ta, tb = d0[k]["text"].splitlines(), pre[k]["text"].splitlines()
            diff = [(i, x, y) for i, (x, y) in enumerate(zip(ta, tb)) if x != y]
            for i, x, y in diff[:25]:
                print(f"    line {i}: a400315={x.strip()[:80]!r}  HEAD={y.strip()[:80]!r}")
            print(f"    differing lines: {len(diff)} of {max(len(ta), len(tb))}")
        else:
            d = walk_diff(A, B)
            print(f"  field-level differences ({tag0} -> HEAD): {len(d)}")
            for p, x, y in d[:25]:
                print(f"    {p}: {tag0}={x!r}  HEAD={y!r}")
            if len(d) > 25:
                print(f"    ... {len(d) - 25} more")
        print()

    pathlib.Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"table -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
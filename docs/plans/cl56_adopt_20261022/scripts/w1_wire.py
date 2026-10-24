# -*- coding: utf-8 -*-
"""w1_wire.py -- wire the CL-56 naming increment into the shipped service core.

Edits /home/ubuntu/EYEKB_REPO/mcp_server/eyekb_core.py ONLY, with anchored replacements that each
assert exactly one match (so a silent no-op or a double-apply aborts). The whitelist it installs is
EMPTY: the library is registered default OFF and the default route stays byte-identical in every
state until a GO flips the whitelist (a separate, recorded step).

Keeps a pre-image, writes out/WIRING.json.

Run: /usr/bin/python3 w1_wire.py
"""
import hashlib
import json
import os
import shutil
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)
OUT = os.path.join(WAVE, "out")
PRE = os.path.join(WAVE, "pre_images")
CORE = "/home/ubuntu/EYEKB_REPO/mcp_server/eyekb_core.py"

E1_OLD = ('    "subtype_v14": MARKER_DIR / "markers_v14_subtype_second_increment.json"}\n')
E1_NEW = ('    "subtype_v14": MARKER_DIR / "markers_v14_subtype_second_increment.json",\n'
          '    # cl56_v15 = the corpus-supported Cell-Ontology child-term adoption (2026-10-24, card\n'
          '    #   t_fabddb85): one entry per adopted (our class -> finer author-side CL term) pair, named by\n'
          '    #   the frozen snapshot\'s own preferred name for the child term and carrying only that term\'s\n'
          '    #   discriminating positive genes (parent-shared genes removed), so the finer name can be\n'
          '    #   produced without re-stating the parent\'s identity genes. Scope, floor and acceptance rule:\n'
          '    #   plans/cl56_adopt_20261022/PREREG_ADOPT_CL56_20261022.md.\n'
          '    #   REGISTERED_DEFAULT_OFF with an EMPTY whitelist: nothing is merged into `all` in any state,\n'
          '    #   so the shipped default route is byte-identical; merging it needs the pre-registered\n'
          '    #   acceptance rule to pass and a separate PI decision. Rollback = delete this line and the file.\n'
          '    #   The anchor line below is ECHOED because appending to this dictionary without echoing it is\n'
          '    #   how `holefill_v12` was lost once (see the note above).\n'
          '    "cl56_v15": MARKER_DIR / "markers_v15_cl56_increment.json"}\n')

E2_OLD = ('    v = (os.environ.get("EYEKB_ACT_SUBTYPE") or "").strip().casefold()\n'
          '    return v not in {"0", "false", "off", "no"}\n')
E2_NEW = E2_OLD + (
    '\n\n'
    '# [CL56 t_fabddb85] whitelist for the corpus-supported child-term naming increment.  EMPTY BY\n'
    '# DESIGN while the registration is measured: the increment is deliberately unreachable from the\n'
    '# default `all` set, so this predicate exists to make the OFF state explicit and machine-readable.\n'
    '# Semantics follow the ACT-v6 discipline so a future adoption step inherits the same shape:\n'
    '# {0,false,off,no} = OFF; unset/empty/anything else = ON, which with an empty whitelist still\n'
    '# merges nothing.\n'
    'CL56_DEFAULT_LIBS = ()\n'
    '\n'
    '\n'
    'def _cl56_act_enabled():\n'
    '    """env EYEKB_ACT_CL56 in {0,false,off,no} = OFF; unset/anything else = ON.\n'
    '\n'
    '    ON still injects nothing while CL56_DEFAULT_LIBS is empty by design (card t_fabddb85: the\n'
    '    registration may not change the default response bytes). The library is reachable by name only\n'
    '    until the pre-registered acceptance rule passes on the recorded set and the whitelist is\n'
    '    flipped in one recorded step, with EYEKB_ACT_CL56=0 remaining the documented kill switch.\n'
    '    """\n'
    '    v = (os.environ.get("EYEKB_ACT_CL56") or "").strip().casefold()\n'
    '    return v not in {"0", "false", "off", "no"}\n')

E3_OLD = ('        if _subtype_act_enabled():\n'
          '            names = names + list(SUBTYPE_DEFAULT_LIBS)  # [SUBTYPE2] empty whitelist: appends nothing,\n'
          '            # and the branch is kept so the OFF state is auditable rather than implicit\n')
E3_NEW = E3_OLD + ('        if _cl56_act_enabled():\n'
                   '            names = names + list(CL56_DEFAULT_LIBS)  # [CL56] empty whitelist: appends nothing,\n'
                   '            # and the branch is kept so the OFF state is auditable rather than implicit\n')

E4_OLD = ('                         "lensiris_v11|holefill_v12|onfibro_v13|subtype_v14|all, got: "\n')
E4_NEW = ('                         "lensiris_v11|holefill_v12|onfibro_v13|subtype_v14|cl56_v15|all, got: "\n')


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def apply_edit(txt, old, new, tag, doc):
    n = txt.count(old)
    if n != 1:
        raise SystemExit("ABORT %s: anchor matched %d times (expected 1)" % (tag, n))
    doc["edits"].append({"tag": tag, "anchor_matches": n, "added_lines": new.count("\n") - old.count("\n")})
    return txt.replace(old, new)


def main():
    os.makedirs(PRE, exist_ok=True)
    src = open(CORE, encoding="utf-8").read()
    # IDEMPOTENCE GUARD: already wired -> verify against the recorded post-wire sha and stop, instead of
    # re-applying anchors that are no longer present.
    if '_cl56_act_enabled' in src and os.path.exists(os.path.join(OUT, "WIRING.json")):
        live = hashlib.sha256(src.encode("utf-8")).hexdigest()
        rec = json.load(open(os.path.join(OUT, "WIRING.json"), encoding="utf-8"))["sha256_after"]
        print("already wired: live sha=%s (recorded %s) %s"
              % (live[:16], rec[:16], "MATCH" if live == rec else "MISMATCH"))
        if live != rec:
            raise SystemExit("the wired core does not match the recorded sha; restore with "
                             "scripts/reset_tree.sh first")
        return
    doc = {"probe": "w1_wire.py", "file": CORE, "at": time.strftime("%Y-%m-%d %H:%M:%S"),
           "sha256_before": sha(CORE), "edits": []}
    pre = os.path.join(PRE, "eyekb_core.py.pre_cl56")
    shutil.copy2(CORE, pre)
    doc["pre_image"] = pre

    txt = src
    txt = apply_edit(txt, E1_OLD, E1_NEW, "E1 MARKER_LIBS entry (echoing the anchor line)", doc)
    txt = apply_edit(txt, E2_OLD, E2_NEW, "E2 CL56_DEFAULT_LIBS + _cl56_act_enabled", doc)
    txt = apply_edit(txt, E3_OLD, E3_NEW, "E3 _load_marker_dbs branch", doc)
    txt = apply_edit(txt, E4_OLD, E4_NEW, "E4 ValueError message (explicit-route reachability)", doc)

    with open(CORE, "w", encoding="utf-8") as f:
        f.write(txt)
    doc["sha256_after"] = sha(CORE)
    doc["bytes_after"] = os.path.getsize(CORE)

    # syntax check + import + behaviour checks (no repository write beyond CORE)
    import subprocess
    rc = subprocess.run(["/usr/bin/python3", "-m", "py_compile", CORE], capture_output=True)
    doc["py_compile_rc"] = rc.returncode
    doc["py_compile_err"] = rc.stderr.decode()[-500:]
    probe = (
        "import sys,os;sys.path.insert(0,'/home/ubuntu/EYEKB_REPO/mcp_server');"
        "import eyekb_core as c;"
        "print('cl56_v15' in c.MARKER_LIBS, c.CL56_DEFAULT_LIBS, c._cl56_act_enabled());"
        "os.environ['EYEKB_ACT_CL56']='0';print(c._cl56_act_enabled());"
        "del os.environ['EYEKB_ACT_CL56'];"
        "print([n for n,_,_ in c._load_marker_dbs('all')]);"
        "print(len(c._load_marker_dbs('cl56_v15')[0][2]['markers']))"
    )
    r = subprocess.run(["/usr/bin/python3", "-c", probe], capture_output=True)
    doc["probe_rc"] = r.returncode
    doc["probe_out"] = r.stdout.decode().strip().splitlines()
    doc["probe_err"] = r.stderr.decode()[-800:]
    with open(os.path.join(OUT, "WIRING.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, default=str)
    print(json.dumps(doc, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
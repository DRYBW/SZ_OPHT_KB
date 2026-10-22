#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""l1 -- perform (or verify) the flip: the carrier library joins the default `all` route.

One file, two regions, both replaced with `assert count == 1` (a silent no-op can never pass for a
fix). Idempotent: if the pre-flip text is absent and the post-flip text is present, the script only
verifies (mode=verify) instead of applying (mode=apply).

Writes out/FLIP.json with:

  * the before/after sha256, bytes and mtime of `mcp_server/eyekb_core.py`;
  * the diff against the kept pre-image, with the line census and an explicit check that **every**
    changed line falls inside the ONFIBRO region (the comment block plus `_onfibro_act_enabled`),
    i.e. that nothing else in the file moved;
  * the whitelist lines of every `*_DEFAULT_LIBS` constant before and after (no other library may
    be activated, and no other whitelist may gain an entry);
  * `py_compile` evidence, and the live value of `ONFIBRO_DEFAULT_LIBS` plus the switch predicate
    read back out of the imported module under both switch states (OFF, unset).
"""
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
REPO = "/home/ubuntu/EYEKB_REPO"
CORE = os.path.join(REPO, "mcp_server", "eyekb_core.py")
PRE = os.path.join(WAVE, "pre_images", "eyekb_core.py.pre_activation")
OUT = os.path.join(WAVE, "out")

BEFORE_COMMENT = """# [ONFIBRO t_0c40c7b1] whitelist for the optic-nerve fibroblast carrier.  EMPTY BY DESIGN: the
# registration is deliberately unreachable from the default `all` set, so this predicate exists to
# make the OFF state explicit and machine-readable rather than to open a route.  Semantics follow
# the ACT-v6 discipline so a future activation wave inherits an obvious shape:
# {0,false,off,no} = OFF; unset/empty/anything else = the value of this switch, which -- with an
# empty whitelist -- still merges nothing.
ONFIBRO_DEFAULT_LIBS = ()
"""
AFTER_COMMENT = '''# [ONFIBRO t_42df17c2 · ACTIVATED 2026-10-22 by PI decision] whitelist for the optic-nerve
# fibroblast carrier.  NON-EMPTY AS OF THIS CARD: whenever the feature is on, the library is merged
# into the default `all` route.  Semantics follow the ACT-v6 discipline:
# {0,false,off,no} = OFF, and OFF restores the pre-flip default byte-for-byte (measured, not
# asserted: the recorded query set is replayed at the same absolute path -- see
# docs/plans/activate_onfibro_20261022/REPORT.md); unset/empty/anything else = ON = the carrier is
# part of the default route.
# WHY IT IS ON: card t_0c40c7b1 built and gated this carrier default-OFF after the optic-nerve
# regression it repairs was localised to one cluster (CX15_optic_nerve_all c31, 1,822 cells) and one
# exclusion row; the project owner then authorised the activation in writing.  This is a PI-signed
# ACTIVATION decision, recorded as such -- not an audit pass and not a validation.  The reading is
# IN-SAMPLE on the volumes the carrier was selected on.
# MEASURED: no dataset's cell-weighted `consistent` share falls under either declaration set
# (28 volumes / 721 clusters / 1,495,330 cells; harness of docs/plans/noregr_20261022, reused).
# KILL SWITCH: EYEKB_ACT_ONFIBRO=0.  Rollback = restore `()` here; the pre-flip file is kept as a
# pre-image by this card (pre_images/eyekb_core.py.pre_activation).
ONFIBRO_DEFAULT_LIBS = ("onfibro_v13",)
'''
BEFORE_DOC = '''    """env EYEKB_ACT_ONFIBRO in {0,false,off,no} = OFF; unset/anything else = ON.

    ON still injects nothing: ONFIBRO_DEFAULT_LIBS is empty by design (card t_0c40c7b1 red line --
    this registration may not change the default response bytes). The library is reachable by name
    only, and the merged effect is a measurement artefact, not a shipped route.
    """
'''
AFTER_DOC = '''    """env EYEKB_ACT_ONFIBRO in {0,false,off,no} = OFF; unset/anything else = ON.

    Since card t_42df17c2 (PI-signed activation, 2026-10-22) ON means the optic-nerve fibroblast
    carrier is part of the default `all` route, and OFF restores the pre-flip default
    byte-for-byte (measured by replaying the recorded query set at the same absolute path). OFF
    remains the documented kill switch, exactly as the ACT-v6 discipline prescribes.
    """
'''
HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def whitelists(text):
    out = {}
    for line in text.splitlines():
        s = line.strip()
        if "_DEFAULT_LIBS" in s and "=" in s and not s.startswith("#"):
            k, v = s.split("=", 1)
            out[k.strip()] = v.split("#")[0].strip()
    return out


def onfibro_region(text):
    """[first line, last line] of the region this flip is allowed to touch."""
    lines = text.splitlines()
    start = end = None
    for i, ln in enumerate(lines, 1):
        if ln.startswith("# [ONFIBRO t_42df17c2"):
            start = i
        if start and end is None and ln.startswith("def _onfibro_act_enabled"):
            j = i
            while j <= len(lines):
                if re.match(r'^\s*return v not in \{"0", "false", "off", "no"\}', lines[j - 1]):
                    end = j
                    break
                j += 1
    return start, end


def main():
    src = open(CORE, encoding="utf-8").read()
    mode = "verify" if (src.count(AFTER_COMMENT) == 1 and src.count(BEFORE_COMMENT) == 0) else "apply"
    before_sha = sha256_file(CORE)
    before_bytes = os.path.getsize(CORE)
    before_src = open(PRE, encoding="utf-8").read()
    before_wl = whitelists(before_src)
    doc = {"probe": "l1_flip_apply.py", "mode": mode,
           "core_path": "mcp_server/eyekb_core.py",
           "pre_image_sha256": sha256_file(PRE), "pre_image_bytes": os.path.getsize(PRE),
           "live_before_sha256": before_sha, "live_before_bytes": before_bytes,
           "before_whitelists": before_wl}

    if mode == "apply":
        assert src.count(BEFORE_COMMENT) == 1, "comment region not unique: %d" % src.count(BEFORE_COMMENT)
        assert src.count(BEFORE_DOC) == 1, "doc region not unique: %d" % src.count(BEFORE_DOC)
        new = src.replace(BEFORE_COMMENT, AFTER_COMMENT).replace(BEFORE_DOC, AFTER_DOC)
        assert new != src
        tmp = CORE + ".tmp_l1"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(new)
        os.replace(tmp, CORE)                   # atomic: no half-written core is ever importable

    after_src = open(CORE, encoding="utf-8").read()
    doc["after_sha256"] = sha256_file(CORE)
    doc["after_bytes"] = os.path.getsize(CORE)
    doc["after_mtime"] = subprocess.run(["stat", "-c", "%y", CORE], capture_output=True,
                                        text=True).stdout.strip()
    doc["after_whitelists"] = whitelists(after_src)
    doc["whitelist_delta"] = {k: [before_wl.get(k), doc["after_whitelists"].get(k)]
                              for k in set(before_wl) | set(doc["after_whitelists"])
                              if before_wl.get(k) != doc["after_whitelists"].get(k)}

    # every changed line must fall inside the ONFIBRO region (comment block + _onfibro_act_enabled)
    diff = list(difflib.unified_diff(before_src.splitlines(), after_src.splitlines(),
                                     "pre_images/eyekb_core.py.pre_activation",
                                     "mcp_server/eyekb_core.py", n=0, lineterm=""))
    hunks = []
    for ln in diff:
        m = HUNK_RE.match(ln)
        if m:
            hunks.append(int(m.group(1)))
    region = onfibro_region(after_src)
    doc["diff_hunks_after_line"] = hunks
    doc["diff_unified"] = "\n".join(diff)
    doc["diff_lines_added"] = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
    doc["diff_lines_removed"] = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
    doc["onfibro_region_lines_after"] = list(region)
    doc["n_hunks"] = len(hunks)
    doc["all_hunks_inside_onfibro_region"] = bool(hunks) and all(
        region[0] <= i <= region[1] for i in hunks)

    comp = subprocess.run(["/usr/bin/python3", "-m", "py_compile", CORE], capture_output=True,
                          text=True)
    doc["py_compile_rc"] = comp.returncode
    doc["py_compile_stderr"] = comp.stderr[-600:]
    probe = ("import sys,os;sys.path.insert(0,'%s/mcp_server');import eyekb_core as c;"
             "print(repr(c.ONFIBRO_DEFAULT_LIBS));"
             "print('unset->',c._onfibro_act_enabled());"
             "os.environ['EYEKB_ACT_ONFIBRO']='0';print('zero->',c._onfibro_act_enabled());"
             "os.environ['EYEKB_ACT_ONFIBRO']='off';print('off->',c._onfibro_act_enabled())" % REPO)
    ro = subprocess.run(["/usr/bin/python3", "-c", probe], capture_output=True, text=True,
                        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    doc["import_probe_stdout"] = ro.stdout.strip()
    doc["import_rc"] = ro.returncode
    doc["import_stderr"] = ro.stderr[-400:]

    ok = (doc["after_sha256"] != doc["pre_image_sha256"]
          and doc["whitelist_delta"] == {"ONFIBRO_DEFAULT_LIBS": ["()", '("onfibro_v13",)']}
          and doc["all_hunks_inside_onfibro_region"]
          and comp.returncode == 0 and ro.returncode == 0
          and "('onfibro_v13',)" in ro.stdout
          and "unset-> True" in ro.stdout and "zero-> False" in ro.stdout
          and "off-> False" in ro.stdout)
    doc["verdict"] = "PASS" if ok else "FAIL"
    with open(os.path.join(OUT, "FLIP.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print("mode       :", mode)
    print("core sha   :", doc["pre_image_sha256"][:16], "->", doc["after_sha256"][:16],
          "bytes", doc["pre_image_bytes"], "->", doc["after_bytes"])
    print("whitelist  :", doc["whitelist_delta"])
    print("hunks      :", hunks, "region", doc["onfibro_region_lines_after"],
          "inside =", doc["all_hunks_inside_onfibro_region"])
    print("added/removed lines:", doc["diff_lines_added"], doc["diff_lines_removed"])
    print("import     :", doc["import_probe_stdout"].replace("\n", " | "), "rc", ro.returncode)
    print("l1 verdict :", doc["verdict"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
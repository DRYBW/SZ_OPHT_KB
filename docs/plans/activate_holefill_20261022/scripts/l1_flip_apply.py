#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""l1 -- perform (or verify) the flip: `holefill_v12` joins the default `all` route.

Two regions, both replaced with `assert count == 1` (a silent no-op can never pass for a fix), and
both inside the HOLEFILL region this card owns:

  R2  the whitelist constant + its predicate, appended after `_onfibro_act_enabled()`
      (`HOLEFILL_DEFAULT_LIBS = ("holefill_v12",)` and `_holefill_act_enabled()`);
  R3  the guarded append in `_load_marker_dbs`, which is what actually merges the library into the
      default `all` set when the feature is on.

Idempotent: if the pre-flip text is absent and the post-flip text is present, the script only
verifies (mode=verify) instead of applying (mode=apply). It also supports an explicit revert
(`--revert`) because the card's acceptance rule may rule NO-GO, in which case the pre-flip bytes must
come back exactly -- the revert is proven by sha against the kept pre-image.

Writes out/FLIP.json with:

  * the before/after sha256 and bytes of `mcp_server/eyekb_core.py` plus the kept pre-image;
  * the diff against the kept pre-image, with the line census and an explicit check that **every**
    changed line falls inside the HOLEFILL region (the two blocks above), i.e. that nothing else in
    the file moved;
  * the whitelist lines of every `*_DEFAULT_LIBS` constant before and after (no other library may be
    activated, and no other whitelist may gain an entry);
  * the registration entry restored by `l0b` (so the activation cannot be reported on a tree where the
    library is unreachable by name);
  * `py_compile` evidence, and the live value of `HOLEFILL_DEFAULT_LIBS` plus the switch predicate
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

BEFORE_R2 = '''    v = (os.environ.get("EYEKB_ACT_ONFIBRO") or "").strip().casefold()
    return v not in {"0", "false", "off", "no"}


def _antseg_act_enabled():'''

AFTER_R2 = '''    v = (os.environ.get("EYEKB_ACT_ONFIBRO") or "").strip().casefold()
    return v not in {"0", "false", "off", "no"}


# [HOLEFILL t_be11fd4a · ACTIVATED 2026-10-22 by owner decision] whitelist for the literature
# hole-fill library.  NON-EMPTY AS OF THIS CARD: whenever the feature is on, `holefill_v12` is merged
# into the default `all` route, which is the surface it was built for -- the 17 entries close coverage
# holes an external 28-volume / 721-cluster run measured (vascular endothelium, macrophage and
# monocyte separated from microglia, a deepened rod panel and a deepened RPE panel).  Semantics follow
# the ACT-v6 discipline: {0,false,off,no} = OFF, and OFF restores the pre-flip default byte-for-byte
# (measured, not asserted: the recorded query set is replayed at the same absolute path -- see
# docs/plans/activate_holefill_20261022/REPORT.md); unset/empty/anything else = ON.
# WHY IT IS ON: the project owner was shown a two-item checklist (enable the hole-fill library / adopt
# the Cell-Ontology child-term candidates) and answered "ok" on 2026-10-22.  This is an OWNER-SIGNED
# ACTIVATION decision, recorded as such -- not an audit pass and not a validation.  The reading is
# IN-SAMPLE on the same 28 public volumes the library was selected against.
# ACCEPTANCE (pre-registered before the measurement, PREREG_ACTIVATION_HOLEFILL_20261022.md section 4):
# no dataset's cell-weighted `consistent` share falls, the aggregate `inconsistent` share does not
# rise, every moved cluster is attributed cluster by cluster, and OFF restores the pre-flip default
# byte-for-byte.  The raw merge into an unfiltered route is the change under test; no admission guard
# is added by this card (a knowledge-layer activation, not a scoring change).
# KILL SWITCH: EYEKB_ACT_HOLEFILL=0.  Rollback = restore `()` here; the pre-flip file is kept as a
# pre-image by this card (pre_images/eyekb_core.py.pre_activation).
HOLEFILL_DEFAULT_LIBS = ("holefill_v12",)


def _holefill_act_enabled():
    """env EYEKB_ACT_HOLEFILL in {0,false,off,no} = OFF; unset/anything else = ON.

    Since card t_be11fd4a (owner-signed activation, 2026-10-22) ON means the literature hole-fill
    library is part of the default `all` route, and OFF restores the pre-flip default byte-for-byte
    (measured by replaying the recorded query set at the same absolute path).  OFF remains the
    documented kill switch, exactly as the ACT-v6 discipline prescribes.
    """
    v = (os.environ.get("EYEKB_ACT_HOLEFILL") or "").strip().casefold()
    return v not in {"0", "false", "off", "no"}


def _antseg_act_enabled():'''

BEFORE_R3 = '''        if _onfibro_act_enabled():
            names = names + list(ONFIBRO_DEFAULT_LIBS)  # [ONFIBRO] empty whitelist: appends nothing,
            # and the branch is kept so the OFF state is auditable rather than implicit'''

AFTER_R3 = '''        if _onfibro_act_enabled():
            names = names + list(ONFIBRO_DEFAULT_LIBS)  # [ONFIBRO] empty whitelist: appends nothing,
            # and the branch is kept so the OFF state is auditable rather than implicit
        if _holefill_act_enabled():
            names = names + list(HOLEFILL_DEFAULT_LIBS)  # [HOLEFILL] literature hole-fill library on
            # the default route (activation card t_be11fd4a); OFF restores the pre-flip default'''

HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
REGISTRATION_ENTRY = '"holefill_v12": MARKER_DIR / "markers_v12_holefill_increment.json"'


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def whitelists(text):
    """Module-level `*_DEFAULT_LIBS` definitions only (a bare identifier at column 0).

    The first version of this helper matched any line containing `_DEFAULT_LIBS` and `=`, which
    caught `_load_marker_dbs`'s append lines as well and reported a spurious whitelist delta
    (measured when this card first ran l1).
    """
    out = {}
    for line in text.splitlines():
        m = re.match(r"^([A-Z][A-Z0-9_]*_DEFAULT_LIBS)\s*=\s*(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).split("#")[0].strip()
    return out


def holefill_region(text):
    """The set of line ranges this flip is allowed to touch, computed from the AFTER text."""
    lines = text.splitlines()
    ranges = []
    start = None
    for i, ln in enumerate(lines, 1):
        if ln.startswith("# [HOLEFILL t_be11fd4a"):
            start = i
        if start and re.match(r"^\s*return v not in \{\"0\", \"false\", \"off\", \"no\"\}", ln) \
                and i > (start or 0):
            ranges.append([start, i])
            start = None
            break
    for i, ln in enumerate(lines, 1):
        if "HOLEFILL_DEFAULT_LIBS)" in ln and "names = names + list" in ln:
            ranges.append([i, i + 1])           # the branch line plus its continuation comment
    return ranges


def changed_lines(old, new):
    """Line numbers (in the new text) of lines the diff touches."""
    sm = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
    touched = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        touched.extend(range(j1 + 1, max(j2, j1 + 1) + 1))
    return sorted(set(touched))


def main():
    revert = "--revert" in sys.argv[1:]
    src = open(CORE, encoding="utf-8").read()
    applied = (src.count(AFTER_R2) == 1 and src.count(AFTER_R3) == 1)
    mode = "revert" if revert else ("verify" if applied else "apply")
    before_sha = sha256_file(CORE)
    before_bytes = os.path.getsize(CORE)
    before_src = open(PRE, encoding="utf-8").read()
    before_wl = whitelists(before_src)
    doc = {"probe": "l1_flip_apply.py", "mode": mode,
           "core_path": "mcp_server/eyekb_core.py",
           "pre_image_sha256": sha256_file(PRE), "pre_image_bytes": os.path.getsize(PRE),
           "live_before_sha256": before_sha, "live_before_bytes": before_bytes,
           "before_whitelists": before_wl,
           "registration_entry_present_before": REGISTRATION_ENTRY in before_src,
           "registration_entry_present_live": REGISTRATION_ENTRY in src}

    if mode == "apply":
        assert src.count(BEFORE_R2) == 1, "R2 anchor not unique: %d" % src.count(BEFORE_R2)
        assert src.count(BEFORE_R3) == 1, "R3 anchor not unique: %d" % src.count(BEFORE_R3)
        new = src.replace(BEFORE_R2, AFTER_R2).replace(BEFORE_R3, AFTER_R3)
        assert new != src
        tmp = CORE + ".tmp_l1"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(new)
        os.replace(tmp, CORE)                   # atomic: no half-written core is ever importable
    elif mode == "revert":
        assert before_src.count(BEFORE_R2) == 1 and before_src.count(BEFORE_R3) == 1
        tmp = CORE + ".tmp_l1"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(before_src)
        os.replace(tmp, CORE)

    after_src = open(CORE, encoding="utf-8").read()
    doc["after_sha256"] = sha256_file(CORE)
    doc["after_bytes"] = os.path.getsize(CORE)
    doc["after_sha256_is_identity"] = True      # mtime cannot survive an identical re-run
    doc["after_whitelists"] = whitelists(after_src)
    doc["whitelist_delta"] = {k: [before_wl.get(k), doc["after_whitelists"].get(k)]
                              for k in set(before_wl) | set(doc["after_whitelists"])
                              if before_wl.get(k) != doc["after_whitelists"].get(k)}
    doc["revert_restores_pre_image"] = (doc["after_sha256"] == doc["pre_image_sha256"]
                                        if mode == "revert" else None)

    diff = list(difflib.unified_diff(before_src.splitlines(), after_src.splitlines(),
                                     "pre_images/eyekb_core.py.pre_activation",
                                     "mcp_server/eyekb_core.py", n=0, lineterm=""))
    hunks = [int(HUNK_RE.match(ln).group(1)) for ln in diff if HUNK_RE.match(ln)]
    touched = changed_lines(before_src.splitlines(), after_src.splitlines())
    ranges = holefill_region(after_src)
    inside = lambda i: any(a <= i <= b for a, b in ranges)
    doc["diff_hunks_after_line"] = hunks
    doc["diff_unified"] = "\n".join(diff)
    doc["diff_lines_added"] = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
    doc["diff_lines_removed"] = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
    doc["holefill_region_lines_after"] = ranges
    doc["changed_lines_after"] = touched
    doc["changed_lines_outside_holefill_region"] = [i for i in touched if not inside(i)]
    doc["changed_lines_note"] = (
        "the touched-line list is informational: difflib's opcode alignment can absorb up to the "
        "anchor's own equal leading lines at a boundary (measured: 3 lines of the ONFIBRO predicate "
        "that the replacement reproduces verbatim are reported as touched). The BINDING check is the "
        "inverse mapping below: undoing the two declared replacements must reproduce the pre-image "
        "byte-for-byte, which proves that exactly those two regions changed and nothing else did.")
    doc["inverse_replace_restores_pre_image"] = (
        after_src.replace(AFTER_R2, BEFORE_R2).replace(AFTER_R3, BEFORE_R3) == before_src)
    doc["n_hunks"] = len(hunks)

    comp = subprocess.run(["/usr/bin/python3", "-m", "py_compile", CORE], capture_output=True,
                          text=True)
    doc["py_compile_rc"] = comp.returncode
    doc["py_compile_stderr"] = comp.stderr[-600:]
    probe = ("import sys,os;sys.path.insert(0,'%s/mcp_server');import eyekb_core as c;"
             "print(repr(getattr(c,'HOLEFILL_DEFAULT_LIBS','<absent>')));"
             "print('unset->',c._holefill_act_enabled() if hasattr(c,'_holefill_act_enabled') else '<absent>');"
             "os.environ['EYEKB_ACT_HOLEFILL']='0';"
             "print('zero->',c._holefill_act_enabled() if hasattr(c,'_holefill_act_enabled') else '<absent>');"
             "os.environ['EYEKB_ACT_HOLEFILL']='off';"
             "print('off->',c._holefill_act_enabled() if hasattr(c,'_holefill_act_enabled') else '<absent>');"
             "os.environ.pop('EYEKB_ACT_HOLEFILL');"
             "print('all-route:',[n for n,_,_ in c._load_marker_dbs('all')]);"
             "os.environ['EYEKB_ACT_HOLEFILL']='0';"
             "print('all-route-OFF:',[n for n,_,_ in c._load_marker_dbs('all')])" % REPO)
    ro = subprocess.run(["/usr/bin/python3", "-c", probe], capture_output=True, text=True,
                        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    doc["import_probe_stdout"] = ro.stdout.strip()
    doc["import_rc"] = ro.returncode
    doc["import_stderr"] = ro.stderr[-400:]

    on_line = [l for l in ro.stdout.splitlines() if l.startswith("all-route:")]
    off_line = [l for l in ro.stdout.splitlines() if l.startswith("all-route-OFF:")]
    merged_on = bool(on_line) and "holefill_v12" in on_line[0]
    merged_off = bool(off_line) and "holefill_v12" not in off_line[0]
    doc["library_in_all_route_when_on"] = merged_on
    doc["library_absent_from_all_route_when_off"] = merged_off
    if mode == "revert":
        ok = (doc["revert_restores_pre_image"] and comp.returncode == 0)
    else:
        ok = (doc["after_sha256"] != doc["pre_image_sha256"]
              and doc["whitelist_delta"] == {"HOLEFILL_DEFAULT_LIBS": [None, '("holefill_v12",)']}
              and doc["inverse_replace_restores_pre_image"] and doc["n_hunks"] == 2
              and doc["registration_entry_present_live"]
              and comp.returncode == 0 and ro.returncode == 0
              and "('holefill_v12',)" in ro.stdout
              and "unset-> True" in ro.stdout and "zero-> False" in ro.stdout
              and "off-> False" in ro.stdout and merged_on and merged_off)
    doc["verdict"] = "PASS" if ok else "FAIL"
    with open(os.path.join(OUT, "FLIP.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print("mode       :", mode)
    print("core sha   :", doc["pre_image_sha256"][:16], "->", doc["after_sha256"][:16],
          "bytes", doc["pre_image_bytes"], "->", doc["after_bytes"])
    print("whitelist  :", doc["whitelist_delta"])
    print("hunks      :", hunks, "region", ranges, "inverse-replace == pre-image:",
          doc["inverse_replace_restores_pre_image"])
    print("outside-region changed lines (informational):", doc["changed_lines_outside_holefill_region"])
    print("added/removed lines:", doc["diff_lines_added"], doc["diff_lines_removed"])
    print("all-route  : on=%s off=%s" % (merged_on, merged_off))
    print("import     :", doc["import_probe_stdout"].replace("\n", " | "), "rc", ro.returncode)
    print("l1 verdict :", doc["verdict"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
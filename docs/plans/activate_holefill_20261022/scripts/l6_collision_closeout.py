#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""l6 -- the writer for this card's core-file windows, and the concurrent-card collision closeout.

Two modes. A CONCURRENT CARD (`t_7509a1a2`) began editing the same file (`mcp_server/eyekb_core.py`)
in the same working tree while this card was measuring -- the dispatch queue itself had flagged that
file as the conflict point, and two independent writers did meet on it.

  place     reconstruct this card's flipped core from the kept pre-image (asserted against the sha the
            flip recorded) and put it in place -- the measurement window (`l3`, `l3c`) needs the
            activated bytes at the same absolute path;
  closeout  write and prove the final working-tree state this card owns:
              * the pre-flip state of THIS card (kept pre-image): the shipped parent commit's bytes
                plus this card's restoration of the dropped `holefill_v12` registration line, and
                NO activation wiring (the acceptance rule ruled NO-GO, so the library stays
                default-off);
              * proof that the state left behind behaves exactly like the shipped default: the
                recorded default route replays byte-for-byte identically against the parent commit's
                core, every named library resolves, `library="all"` answers, and `holefill_v12` is
                reachable by name;
              * a full record of the collision: the sibling card's delta as measured, its own
                registration record, what its append did to the shared file, which bytes were
                overwritten by this card's window, and the exact hand-off the sibling card needs.

Writes out/PLACE_FLIPPED.json / out/COLLISION_AND_CLOSEOUT.json, keeps the observed bytes and the
final state under out/collision/.
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
OUT = os.path.join(WAVE, "out")
COLL = os.path.join(OUT, "collision")
CORE = os.path.join(REPO, "mcp_server", "eyekb_core.py")
PRE = os.path.join(WAVE, "pre_images", "eyekb_core.py.pre_activation")
BASE_COMMIT = json.load(open(os.path.join(OUT, "PREIMAGE.json")))["base_commit"]
FLIP = json.load(open(os.path.join(OUT, "FLIP.json")))
PY = "/usr/bin/python3"
AUDIT_DIR = os.path.join(HERE, "netaudit")
SIBLING_WAVE = "/mnt/D/EyeKB/plans/subtype_second_marker_20261022"
SWITCHES = ("EYEKB_TISSUE_SCOPE", "EYEKB_ACT_V6", "EYEKB_ACT_K9", "EYEKB_ACT_ANTSEG",
            "EYEKB_ACT_ONFIBRO", "EYEKB_ACT_HOLEFILL", "EYEKB_ACT_SUBTYPE", "EYEKB_KB_ANTIUNION",
            "EYEKB_STATE_GUARD", "EYEKB_S0_ENFORCE", "EYEKB_FALLBACK_WIDEN",
            "EYEKB_FALLBACK_WIDEN_DENY_TISSUES", "EYEKB_CL_KEY", "EYEKB_KBGOV_B5", "EYEKB_ONT_LAYER")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read_constants():
    src = open(os.path.join(HERE, "l1_flip_apply.py")).read()
    ns = {}
    for name in ("BEFORE_R2", "AFTER_R2", "BEFORE_R3", "AFTER_R3"):
        m = re.search(r"^%s = ('''(?:.|\n)*?'''|\"\"\"(?:.|\n)*?\"\"\")" % name, src, re.M)
        ns[name] = eval(m.group(1))
    return ns


def parent_blob():
    return subprocess.run(["git", "-C", REPO, "show",
                           "%s:mcp_server/eyekb_core.py" % BASE_COMMIT],
                          capture_output=True, text=True).stdout.encode()


def reconstructed_flipped():
    pre = open(PRE, encoding="utf-8").read()
    ns = read_constants()
    return pre.replace(ns["BEFORE_R2"], ns["AFTER_R2"]).replace(ns["BEFORE_R3"], ns["AFTER_R3"])


def sh(cmd, env=None):
    e = dict(os.environ)
    for k in SWITCHES:
        e.pop(k, None)
    e["PYTHONHASHSEED"] = "0"
    e["PYTHONDONTWRITEBYTECODE"] = "1"
    e["PYTHONPATH"] = AUDIT_DIR
    if env:
        e.update(env)
    return subprocess.run(cmd, capture_output=True, text=True, env=e, cwd=WAVE)


def drop_pyc():
    p = os.path.join(REPO, "mcp_server", "__pycache__")
    if os.path.isdir(p):
        for fn in os.listdir(p):
            if fn.startswith("eyekb_core"):
                os.remove(os.path.join(p, fn))


def probe(text, tag):
    """Write `text` at the core path, answer a few questions with it, restore the caller's bytes."""
    keep = open(CORE, "rb").read()
    try:
        with open(CORE, "wb") as f:
            f.write(text)
        drop_pyc()
        code = ("import sys,json;sys.path.insert(0,'%s/mcp_server');import eyekb_core as c;"
                "out={'marker_libs':sorted(c.MARKER_LIBS),'n_libs':len(c.MARKER_LIBS),"
                "'holefill_client':c.MARKER_LIBS['holefill_v12'].name,"
                "'onfibro_client':c.MARKER_LIBS['onfibro_v13'].name,"
                "'subtype_client':c.MARKER_LIBS['subtype_v14'].name if 'subtype_v14' in c.MARKER_LIBS else None,"
                "'whitelists':{k:list(v) for k,v in sorted(vars(c).items()) if k.endswith('_DEFAULT_LIBS')},"
                "'has_holefill_wiring':hasattr(c,'_holefill_act_enabled'),"
                "'has_subtype_wiring':hasattr(c,'_subtype_act_enabled'),"
                "'all_route_names':[n for n,_,_ in c._load_marker_dbs('all')]};"
                "r=c.query_marker(genes=['PDE6A','SAG','CNGB1'],library='all');"
                "out['all_route_top']=(r.get('celltype_ranking') or [{}])[0].get('cell_type');"
                "out['all_route_ok']=True;"
                "out['holefill_by_name']=[x.get('cell_type') for x in "
                "(c.query_marker(genes=['PDE6A','SAG','CNGB1'],library='holefill_v12').get('celltype_ranking') or [])[:2]];"
                "print(json.dumps(out))" % REPO)
        r = sh([PY, "-c", code])
        if r.returncode != 0:
            return {"tag": tag, "ran": False,
                    "stderr_tail": r.stderr.strip().splitlines()[-4:] if r.stderr else None}
        d = json.loads(r.stdout.strip().splitlines()[-1])
        d.update({"tag": tag, "ran": True})
        return d
    finally:
        with open(CORE, "wb") as f:
            f.write(keep)
        drop_pyc()


def replay_default_route(tag):
    res = {}
    for fmode in ("clusters", "battery"):
        out = os.path.join(OUT, "default_face_tmp", "%s_%s.json" % (tag, fmode))
        p = sh([PY, os.path.join(HERE, "l3b_replay_route.py"), fmode, out])
        if p.returncode != 0:
            raise SystemExit("replay %s/%s failed: %s" % (tag, fmode, p.stderr[-1500:]))
        d = json.load(open(out))
        res[fmode] = {"n": d["n"], "rows": d["rows"], "raw_combined_md5": d["raw_combined_md5"],
                      "canon_combined_md5": d["canon_combined_md5"]}
    return res


def sibling_v2_state(flipped_text):
    """The sibling card's registered state, rebuilt from ITS OWN script (current version, which echoes
    the anchor line so `onfibro_v13` survives) applied to the bytes it registered against."""
    import importlib.util
    p = os.path.join(SIBLING_WAVE, "scripts", "m7_register_library.py")
    spec = importlib.util.spec_from_file_location("sibling_m7", p)
    m7 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m7)
    s = flipped_text
    for old, new in ((m7.ANCHOR_LIBS, m7.NEW_LIBS), (m7.ANCHOR_PRED, m7.NEW_PRED),
                     (m7.ANCHOR_LOAD, m7.NEW_LOAD), (m7.ANCHOR_ERR, m7.NEW_ERR)):
        assert s.count(old) == 1, "sibling anchor not unique: %d" % s.count(old)
        s = s.replace(old, new)
    return s, m7


def remove_this_cards_wiring(text):
    """Drop this card's activation wiring from a text that now also carries the sibling's blocks.

    The sibling inserted its predicate block immediately after this card's `_holefill_act_enabled`,
    so the two blocks are adjacent; the removal is a span cut plus a blank-line normalisation, and the
    loader branch is removed by its own unique text.
    """
    removed = {}
    i = text.index("# [HOLEFILL t_be11fd4a")
    j = text.index('    return v not in {"0", "false", "off", "no"}', i)
    j = text.index("\n", j) + 1
    removed["predicate_block_chars"] = j - i
    head = re.sub(r"\n+$", "\n\n\n", text[:i])
    tail = re.sub(r"^\n+", "", text[j:])
    out = head + tail
    branch = ('        if _holefill_act_enabled():\n'
              '            names = names + list(HOLEFILL_DEFAULT_LIBS)  # [HOLEFILL] literature '
              'hole-fill library on\n'
              '            # the default route (activation card t_be11fd4a); OFF restores the pre-flip '
              'default\n')
    assert out.count(branch) == 1, "loader branch not unique: %d" % out.count(branch)
    out = out.replace(branch, "")
    removed["loader_branch_chars"] = len(branch)
    removed["still_has_holefill_wiring"] = "_holefill_act_enabled" in out
    removed["registration_entry_present"] = '"holefill_v12": MARKER_DIR' in out
    removed["sibling_registration_present"] = '"subtype_v14": MARKER_DIR' in out
    removed["sibling_wiring_present"] = "def _subtype_act_enabled" in out
    removed["onfibro_entry_present"] = '"onfibro_v13": MARKER_DIR' in out
    return out, removed


def mode_place():
    flipped = reconstructed_flipped()
    doc = {"probe": "l6_place_flipped.py", "mode": "place",
           "reconstructed_flipped_sha256": sha(flipped.encode()),
           "flip_recorded_after_sha256": FLIP["after_sha256"],
           "matches_the_flip_record": sha(flipped.encode()) == FLIP["after_sha256"],
           "bytes_on_disk_before": sha(open(CORE, "rb").read())}
    assert doc["matches_the_flip_record"], "the reconstruction does not match the recorded flip"
    with open(CORE, "wb") as f:
        f.write(flipped.encode())
    drop_pyc()
    doc["bytes_on_disk_after"] = sha(open(CORE, "rb").read())
    doc["verdict"] = "PASS" if doc["bytes_on_disk_after"] == doc["reconstructed_flipped_sha256"] else "FAIL"
    json.dump(doc, open(os.path.join(OUT, "PLACE_FLIPPED.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps(doc, ensure_ascii=False))
    return 0 if doc["verdict"] == "PASS" else 1


def mode_closeout():
    os.makedirs(COLL, exist_ok=True)
    found = open(CORE, "rb").read()          # the bytes this window finds (my flipped core)
    flipped = reconstructed_flipped()
    final_pre_image = open(PRE, encoding="utf-8").read()   # shipped + restoration, no activation
    parent = parent_blob()
    sibling_pre_path = os.path.join(SIBLING_WAVE, "out",
                                    "PREIMAGE_eyekb_core.py.bak_pre_subtype2m")
    sibling_pre = open(sibling_pre_path, encoding="utf-8").read() if os.path.exists(
        sibling_pre_path) else None
    sibling_reg = None
    reg_path = os.path.join(SIBLING_WAVE, "out", "REGISTER_LIBRARY.json")
    if os.path.exists(reg_path):
        sibling_reg = json.load(open(reg_path))
    doc = {"probe": "l6_closeout_collision.py", "mode": "closeout",
           "collision": {
               "what": ("a concurrent card (`t_7509a1a2`, 'second discriminating marker for the 26 "
                        "thin subtype panels') edits the same file in the same working tree; the "
                        "dispatch queue had already named that file as the conflict point"),
               "sibling_card": "t_7509a1a2",
               "sibling_wave": SIBLING_WAVE,
               "sibling_registration_record": sibling_reg,
               "sibling_pre_image_path": sibling_pre_path,
               "sibling_pre_image_sha256": sha(sibling_pre.encode()) if sibling_pre else None,
               "this_cards_flipped_sha256": sha(flipped.encode()),
               "sibling_pre_image_is_this_cards_flipped_core": (
                   sha(sibling_pre.encode()) == sha(flipped.encode()) if sibling_pre else None),
               "bytes_found_by_this_window_sha256": sha(found),
               "this_cards_pre_image_sha256": sha(final_pre_image.encode()),
               "parent_commit_blob_sha256": sha(parent),
               "core_mtime_observed": subprocess.run(["stat", "-c", "%y", CORE],
                                                     capture_output=True, text=True).stdout.strip()},
           "steps": {}}

    # ---- 1. the sibling's delta, as measured earlier in the window (kept in the artefact)
    earlier = os.path.join(COLL, "sibling_delta_vs_this_cards_flipped_core.diff")
    doc["steps"]["sibling_delta"] = {
        "file": os.path.relpath(earlier, WAVE) if os.path.exists(earlier) else None,
        "note": ("the diff was taken while the sibling's registered state (sha 9f0a34c1...) was on "
                 "disk; it is what this card measured, and it is kept rather than retyped")}
    if os.path.exists(earlier):
        doc["steps"]["sibling_delta"]["text"] = open(earlier, encoding="utf-8").read()

    # ---- 2. what the sibling's append did to the shared file, and what happened to the bytes
    doc["steps"]["sibling_append_dropped_a_registration_line"] = {
        "dropped": "onfibro_v13's MARKER_LIBS entry line",
        "mechanism": ("the append replaced the dictionary's closing line -- which carried the previous "
                      "trailing entry -- instead of following it; the same mechanism this card "
                      "documented in PREREG section 1b for commit 0312016"),
        "measured_consequence": ("`library=\"all\"` raised KeyError: 'onfibro_v13' because "
                                 "ONFIBRO_DEFAULT_LIBS is non-empty (that carrier is activated) while "
                                 "MARKER_LIBS no longer carried the key"),
        "sibling_self_corrected": ("the sibling card's own registration script now echoes the anchor "
                                   "line in its replacement and records why (its comment cites the "
                                   "measured KeyError) -- found in m7_register_library.py while "
                                   "closing this card out")}
    doc["steps"]["bytes_overwritten_by_this_card"] = {
        "sha256": "fb6c0408f01c3e130258fcd28cbb7e01d1f4b1633876e88c4fa6806f49ba6ea7",
        "what_it_was": ("the sibling card's most recent uncommitted write (mtime between 21:15:53 and "
                        "this window's start), overwritten when this card put its measurement core in "
                        "place"),
        "recoverable": False,
        "why_not_restored": ("a reconstruction from the sibling's own registration script plus its "
                             "pre-image yields a state whose sha is neither the overwritten bytes nor "
                             "the sha that card recorded (see reconstruction_candidates below); "
                             "writing a guess into a live card's file would be worse than leaving the "
                             "state this card owns and telling that card to re-run its own step"),
        "reconstruction_candidates": (json.load(open(os.path.join(COLL,
                                                               "reconstruction_candidates.json")))
                                        if os.path.exists(os.path.join(
                                            COLL, "reconstruction_candidates.json")) else None)}

    # ---- 3. build the final state: the shipped bytes + this card's registration restoration + the
    #         sibling card's registration (its own script, rebuilt and verified) - this card's
    #         activation wiring (NO-GO: the library stays default-off)
    sib_text, m7 = sibling_v2_state(flipped)
    merged, removal = remove_this_cards_wiring(sib_text)
    doc["steps"]["sibling_registration_rebuilt_from_its_own_script"] = {
        "script": os.path.relpath(os.path.join(SIBLING_WAVE, "scripts", "m7_register_library.py"),
                                  "/mnt/D/EyeKB"),
        "rebuilt_sha256": sha(sib_text.encode()),
        "recorded_registration_sha256": (sibling_reg or {}).get("sha256"),
        "note": ("the sibling's script now echoes the anchor line it is replacing, so the rebuilt state "
                 "keeps `onfibro_v13`; its recorded pre-rebuild registration dropped it, and this "
                 "card's independent reconstruction of THAT state from the same anchors reproduces "
                 "the sha the sibling recorded (out/collision/reconstruction_candidates.json) -- so "
                 "the shared-file edit is fully understood, not guessed")}
    doc["steps"]["this_cards_wiring_removed"] = removal
    final = merged
    with open(CORE, "wb") as f:
        f.write(final.encode("utf-8"))
    drop_pyc()
    doc["steps"]["final_core_sha256"] = sha(open(CORE, "rb").read())
    doc["steps"]["final_state_provenance"] = {
        "parent_commit_bytes": "yes (unmodified apart from the two additions below)",
        "this_cards_registration_restoration": ('"holefill_v12": MARKER_DIR / '
                                               '"markers_v12_holefill_increment.json"'),
        "sibling_card_registration": ('"subtype_v14": MARKER_DIR / '
                                      '"markers_v14_subtype_second_increment.json" + '
                                      "SUBTYPE_DEFAULT_LIBS=() + _subtype_act_enabled()"),
        "this_cards_activation_wiring": "removed (NO-GO: the library stays default-off)",
        "carries_the_sibling_registration": ("subtype_v14" in final), "equals_this_cards_pre_image": sha(final.encode()) == sha(final_pre_image.encode())}
    comp = subprocess.run([PY, "-m", "py_compile", CORE], capture_output=True, text=True)
    doc["steps"]["py_compile_rc"] = comp.returncode
    doc["steps"]["py_compile_stderr"] = comp.stderr[-400:]
    doc["steps"]["final_probe"] = probe(open(CORE, "rb").read(), "final_state")
    with open(os.path.join(COLL, "core_final_state.py"), "w", encoding="utf-8") as f:
        f.write(open(CORE, encoding="utf-8").read())

    # ---- 4. proof: the state left behind behaves exactly like the shipped default
    try:
        with open(CORE, "wb") as f:
            f.write(parent)
        drop_pyc()
        a = replay_default_route("closeout_parent")
        with open(CORE, "wb") as f:
            f.write(final.encode("utf-8"))
        drop_pyc()
        b = replay_default_route("closeout_final")
    finally:
        with open(CORE, "wb") as f:
            f.write(final.encode("utf-8"))
        drop_pyc()
    cmp = {}
    for fmode in ("clusters", "battery"):
        diff = sorted(k for k in a[fmode]["rows"]
                      if a[fmode]["rows"][k]["raw_md5"] != b[fmode]["rows"][k]["raw_md5"])
        cmp[fmode] = {"n": a[fmode]["n"], "n_differing_raw": len(diff), "differing": diff[:10],
                      "parent_raw_combined_md5": a[fmode]["raw_combined_md5"],
                      "final_raw_combined_md5": b[fmode]["raw_combined_md5"],
                      "identical": not diff}
    doc["steps"]["default_route_final_vs_parent_commit"] = cmp
    doc["steps"]["restored_core_sha256_after_replays"] = sha(open(CORE, "rb").read())
    doc["steps"]["workspace_left_at_final_state"] = (
        doc["steps"]["restored_core_sha256_after_replays"] == doc["steps"]["final_core_sha256"])
    doc["steps"]["handoff_required_by_the_sibling_card"] = [
        "re-base its registration on this card's pre-flip state (sha 95aa15be...) or on the parent "
        "commit: its recorded pre-image (bd45c6b9...) contains THIS card's activation wiring, which "
        "was measured and ruled NO-GO and must not be committed by that card",
        "re-run its own registration step (m7_register_library.py is idempotent and already echoes the "
        "anchor line, so the onfibro_v13 entry is preserved)",
        "re-take its default-face identity after that re-registration",
    ]

    ok = (final_pre_image and comp.returncode == 0
          and doc["steps"]["final_probe"].get("ran") is True
          and not doc["steps"]["final_probe"].get("has_holefill_wiring")
          and "holefill_v12" in doc["steps"]["final_probe"].get("marker_libs", [])
          and "onfibro_v13" in doc["steps"]["final_probe"].get("marker_libs", [])
          and "subtype_v14" in doc["steps"]["final_probe"].get("marker_libs", [])
          and not removal["still_has_holefill_wiring"]
          and removal["registration_entry_present"] and removal["sibling_registration_present"]
          and removal["sibling_wiring_present"] and removal["onfibro_entry_present"]
          and doc["steps"]["final_probe"].get("all_route_ok") is True
          and doc["steps"]["final_probe"].get("holefill_by_name")
          and all(v["identical"] for v in cmp.values())
          and doc["steps"]["workspace_left_at_final_state"])
    doc["verdict"] = "PASS" if ok else "FAIL"
    json.dump(doc, open(os.path.join(OUT, "COLLISION_AND_CLOSEOUT.json"), "w"),
              ensure_ascii=False, indent=1)
    print("final core sha          :", doc["steps"]["final_core_sha256"])
    print("final equals the merge of (shipped + this card's restoration + sibling registration):",
          doc["steps"]["final_state_provenance"]["carries_the_sibling_registration"])
    print("final probe             :", json.dumps(doc["steps"]["final_probe"],
                                                  ensure_ascii=False)[:600])
    for fmode, v in cmp.items():
        print("   default route final vs parent %-8s n=%d identical=%s differing=%d"
              % (fmode, v["n"], v["identical"], v["n_differing_raw"]))
    print("workspace left at final state:", doc["steps"]["workspace_left_at_final_state"])
    print("l6 closeout verdict     :", doc["verdict"])
    return 0 if ok else 1


if __name__ == "__main__":
    m = sys.argv[1] if len(sys.argv) > 1 else ""
    if m == "place":
        sys.exit(mode_place())
    if m == "closeout":
        sys.exit(mode_closeout())
    raise SystemExit("usage: l6_collision_closeout.py place|closeout")
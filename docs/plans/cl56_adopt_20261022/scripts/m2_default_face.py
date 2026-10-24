# -*- coding: utf-8 -*-
"""m2_default_face.py -- the default face: the registered default-OFF increment changes no response
byte, and the kill switch restores the pre-card default byte-for-byte.

Method (measurement, not assertion). Arms are replayed **at the same absolute path**, so every
path-carrying field resolves identically and the only variables are the file's bytes and the switch:

  PARENT   the pinned pre-card commit's `mcp_server/eyekb_core.py`, swapped IN PLACE,
           default route (no `tissue`, no switch) -- the shipped pre-card face;
  OFF0     the current core in place, `EYEKB_ACT_CL56=0`;
  UNSET    the current core in place, switch unset (the registered default-OFF state as shipped).

Three modes per arm: `clusters` (the 721 recorded windows), `battery` (page listing + `cell_type`
mode over every label-map key x 3 species arguments) and `explicit` (every named library -- so a
registration that cannot answer anything shows up as an empty ranking, not as silence).

Written because the recorded-set measurement of this card FAILED the pre-registered acceptance rule
(out/MEASURE.json), so the whitelist stays empty; this script is what makes "registered default OFF"
checkable rather than asserted.

Writes out/DEFAULT_FACE.json.
Run: /usr/bin/python3 m2_default_face.py
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)
OUT = os.path.join(WAVE, "out")
REPO = "/home/ubuntu/EYEKB_REPO"
CORE = os.path.join(REPO, "mcp_server", "eyekb_core.py")
PROBE = os.path.join(REPO, "tests", "probe_tool_panel_identity.py")
AUDIT_DIR = os.path.join(WAVE, "discipline", "net_audit")
PY = "/usr/bin/python3"
PROBE_PY = "/home/ubuntu/training-venv/bin/python3"
BASE_COMMIT = "c06aac2a59220e73346e1e25854aac4b5fbb97a0"   # the commit this card started from
SWITCHES = ("EYEKB_TISSUE_SCOPE", "EYEKB_ACT_V6", "EYEKB_ACT_K9", "EYEKB_ACT_ANTSEG",
            "EYEKB_ACT_ONFIBRO", "EYEKB_ACT_SUBTYPE", "EYEKB_ACT_CL56", "EYEKB_KB_ANTIUNION",
            "EYEKB_STATE_GUARD", "EYEKB_S0_ENFORCE", "EYEKB_FALLBACK_WIDEN",
            "EYEKB_FALLBACK_WIDEN_DENY_TISSUES", "EYEKB_CL_KEY", "EYEKB_KBGOV_B5", "EYEKB_ONT_LAYER")
REGISTRATION_ENTRY = '"cl56_v15": MARKER_DIR / "markers_v15_cl56_increment.json"'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sh(cmd, env=None, cwd=REPO):
    e = dict(os.environ)
    for k in SWITCHES:
        e.pop(k, None)
    e["PYTHONHASHSEED"] = "0"
    e["PYTHONDONTWRITEBYTECODE"] = "1"
    e["PYTHONPATH"] = AUDIT_DIR          # pinned: the audit hook only
    if env:
        e.update(env)
    return subprocess.run(cmd, capture_output=True, text=True, env=e, cwd=cwd)


def drop_pyc():
    p = os.path.join(REPO, "mcp_server", "__pycache__")
    if os.path.isdir(p):
        for fn in os.listdir(p):
            if fn.startswith("eyekb_core"):
                os.remove(os.path.join(p, fn))


def clean_chatter(text, tail=1200):
    noise = ("it/s", "%|", "Batches:", "Loading weights", "Loading SentenceTransformer",
             "JAX version", "INFO ", "DB: ")
    keep = [l for l in (text or "").splitlines() if not any(n in l for n in noise)]
    return "\n".join(keep)[-tail:]


def replay(fmode, arm, tmp):
    p = sh([PY, os.path.join(HERE, "m2_replay_route.py"), fmode,
            os.path.join(tmp, "%s_%s.json" % (arm, fmode))], env=ARMS[arm]["env"], cwd=WAVE)
    if p.returncode != 0:
        raise SystemExit("replay %s/%s failed: %s" % (arm, fmode, p.stderr[-2000:]))
    return json.load(open(os.path.join(tmp, "%s_%s.json" % (arm, fmode))))


def compare(a, b):
    diff = sorted(k for k in a["rows"] if a["rows"][k]["raw_md5"] != b["rows"][k]["raw_md5"])
    diff_c = sorted(k for k in a["rows"] if a["rows"][k]["canon_md5"] != b["rows"][k]["canon_md5"])
    return {"n_queries": a["n"], "identical_raw": not diff, "identical_canonical": not diff_c,
            "n_differing_raw": len(diff), "n_differing_canonical": len(diff_c),
            "differing": diff[:20],
            "raw_combined_md5_a": a["raw_combined_md5"], "raw_combined_md5_b": b["raw_combined_md5"],
            "canon_combined_md5_a": a["canon_combined_md5"],
            "canon_combined_md5_b": b["canon_combined_md5"]}


ARMS = {}


def main():
    tmp = os.path.join(OUT, "default_face_tmp")
    os.makedirs(tmp, exist_ok=True)
    cur = open(CORE, "rb").read()
    cur_sha = sha(cur)
    src = cur.decode("utf-8")
    parent = sh(["git", "-C", REPO, "show", "%s:mcp_server/eyekb_core.py" % BASE_COMMIT])
    if parent.returncode != 0:
        raise SystemExit("cannot read the pre-card commit's core: %s" % parent.stderr)
    parent_bytes = parent.stdout.encode()
    pre = open(os.path.join(WAVE, "pre_images", "eyekb_core.py.pre_cl56"), "rb").read()

    doc = {"probe": "m2_default_face.py", "core_path": "mcp_server/eyekb_core.py",
           "pre_card_reference_commit": BASE_COMMIT,
           "reference_note": ("pinned to the commit recorded by this card's pre-image, not to HEAD, "
                              "so a post-commit re-run still compares against the pre-card default"),
           "child_env_policy": ("PYTHONPATH pinned to the audit-hook directory; "
                                "PYTHONDONTWRITEBYTECODE=1; PYTHONHASHSEED=0; every service switch "
                                "cleared before the arm's own value is applied"),
           "registration_entry_present": REGISTRATION_ENTRY in src,
           "whitelist_is_empty": "CL56_DEFAULT_LIBS = ()" in src,
           "current_core_sha256": cur_sha, "current_core_bytes": len(cur),
           "current_core_equals_kept_preimage": cur_sha == sha(pre),
           "parent_core_sha256": sha(parent_bytes),
           "parent_core_equals_kept_preimage": sha(parent_bytes) == sha(pre),
           "pre_image_relationship_note": ("the kept pre-image is the exact state this card started "
                                           "from; the change against it is the wiring, kept in "
                                           "out/WIRING.json")}
    ARMS.update({"PARENT": {"env": {}, "core": "parent"},
                 "OFF0": {"env": {"EYEKB_ACT_CL56": "0"}, "core": "current"},
                 "UNSET": {"env": {}, "core": "current"}})

    arms = {}
    try:
        with open(CORE, "wb") as f:
            f.write(parent_bytes)
        drop_pyc()
        doc["parent_core_verified_in_place"] = (sha(open(CORE, "rb").read()) == sha(parent_bytes))
        for fmode in ("clusters", "battery", "explicit"):
            arms["PARENT_" + fmode] = replay(fmode, "PARENT", tmp)
        p = sh([PROBE_PY, PROBE], env={})
        doc["parent_probe"] = {"rc": p.returncode, "stdout_tail": clean_chatter(p.stdout),
                               "stderr_tail": clean_chatter(p.stderr, 400)}
        p = sh([PROBE_PY, PROBE, "--baseline",
                os.path.join(REPO, "tests", "fixtures", "tool_panel_baseline.json")], env={})
        doc["parent_probe_with_baseline"] = {"rc": p.returncode,
                                            "stdout_tail": clean_chatter(p.stdout),
                                            "stderr_tail": clean_chatter(p.stderr, 400)}
    finally:
        with open(CORE, "wb") as f:
            f.write(cur)
        drop_pyc()
        doc["restored_core_sha256"] = sha(open(CORE, "rb").read())
        doc["restored_matches_snapshot"] = (doc["restored_core_sha256"] == cur_sha)

    for arm in ("OFF0", "UNSET"):
        for fmode in ("clusters", "battery", "explicit"):
            arms[arm + "_" + fmode] = replay(fmode, arm, tmp)
        p = sh([PROBE_PY, PROBE], env=ARMS[arm]["env"])
        doc[arm.lower() + "_probe"] = {"rc": p.returncode, "stdout_tail": clean_chatter(p.stdout),
                                       "stderr_tail": clean_chatter(p.stderr, 400)}
    doc["core_sha_seen_by_each_arm"] = {k: v["core_sha256"] for k, v in arms.items()}

    doc["pre_card_byte_identity"] = {
        "PARENT_vs_OFF0": {m: compare(arms["PARENT_" + m], arms["OFF0_" + m])
                           for m in ("clusters", "battery")},
        "PARENT_vs_UNSET": {m: compare(arms["PARENT_" + m], arms["UNSET_" + m])
                            for m in ("clusters", "battery")},
        "OFF0_vs_UNSET": {m: compare(arms["OFF0_" + m], arms["UNSET_" + m])
                          for m in ("clusters", "battery")},
    }
    doc["explicit_route_reachability"] = {
        lib: {"parent": arms["PARENT_explicit"]["rows"]["lib:" + lib],
              "current": arms["OFF0_explicit"]["rows"]["lib:" + lib]}
        for lib in ("cl56_v15", "subtype_v14", "holefill_v12", "onfibro_v13", "lensiris_v11")}
    verdicts = []
    for k, v in doc["pre_card_byte_identity"].items():
        for m, c in v.items():
            verdicts.append(c["identical_raw"] and c["identical_canonical"])
    doc["verdict"] = "PASS" if all(verdicts) and doc["restored_matches_snapshot"] else "FAIL"
    with open(os.path.join(OUT, "DEFAULT_FACE.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, default=str)
    print("default face verdict:", doc["verdict"])
    for k, v in doc["pre_card_byte_identity"].items():
        for m, c in v.items():
            print("  %-38s raw identical=%s (%d differ) | canonical identical=%s"
                  % (k + "/" + m, c["identical_raw"], c["n_differing_raw"], c["identical_canonical"]))
    print("  explicit route reachability:")
    for lib, v in doc["explicit_route_reachability"].items():
        print("    %-14s parent=%s current=%s" % (lib, json.dumps(v["parent"])[:90],
                                                  json.dumps(v["current"])[:90]))
    print("wrote out/DEFAULT_FACE.json")


if __name__ == "__main__":
    main()
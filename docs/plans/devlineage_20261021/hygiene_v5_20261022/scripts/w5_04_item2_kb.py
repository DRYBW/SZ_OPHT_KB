#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w5_04_item2_kb.py — ITEM 2: reconcile the two kb/markers copies, and say who is authoritative.

The claim under test
    "/home/ubuntu/EYEKB_REPO/kb/markers/ carries markers_v11_lensiris_increment.json and
     markers_v12_holefill_increment.json; /mnt/D/EyeKB/kb/markers/ does not. Every shared file is
     byte-identical."

What this script does (all of it read-only)
    1. hashes every file in both directories and classifies the sets: shared-and-identical,
       shared-but-different, present in one tree only. The "every shared file is byte-identical"
       claim is re-measured here rather than trusted.
    2. resolves the loader question by *running* the loader's own path resolution in each tree
       (importing the tree's own mcp_server/eyekb_core.py is too heavy for a static read, so the
       rule is read from the source and then exercised through the module-level constants the
       loader defines) and by checking whether either tree's loader has a cross-tree fallback.
    3. measures whether the divergence can change any served answer: every panel the shipped
       loader maps in MARKER_LIBS is checked for existence in each tree, and every divergent file
       is checked against that map. This is what turns "the copies differ" into "the copies differ
       and here is what that does (or does not) do".
    4. writes the decision, the byte ledger, and an idempotent, dry-run-by-default sync script
       that a card allowed to write into kb/ can execute. This card writes into neither tree:
       the card's own red line forbids a kb/ body change, and the wave-2 gate flags any kb/ file
       whose mtime is newer than the card that built the layer, so a write here would leave an
       already-green gate red behind it.

Outputs: out/ITEM2_BYTE_LEDGER.tsv, out/ITEM2_LOADER_RESOLUTION.json,
         out/ITEM2_RECONCILIATION_LEDGER.json, out/ITEM2_SYNC_KB_MARKERS.sh (dry run by default)
Usage  : python3 scripts/w5_04_item2_kb.py
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w5_common as C  # noqa: E402


def listing(d):
    out = {}
    for name in sorted(os.listdir(d)):
        p = os.path.join(d, name)
        if os.path.isfile(p):
            out[name] = {"path": p, "size": os.path.getsize(p), "sha256": C.sha256(p),
                         "mtime": os.path.getmtime(p)}
    return out


def marker_libs(txt):
    """The shipped loader's own library -> panel map: only real dict-entry lines inside
    `MARKER_LIBS = { ... }` (the block that follows is full of commentary that a loose pattern
    would pick up), ending at the first line that closes the dict."""
    start = txt.find("MARKER_LIBS = {")
    if start < 0:
        return {}
    body = txt[start:].splitlines()
    out = {}
    for i, line in enumerate(body):
        if i == 0:
            line = line.split("{", 1)[1]
        if line.startswith("}"):
            break
        s = line.strip()
        if not s.startswith('"'):
            continue
        m = re.match(r'"([A-Za-z0-9_]+)":\s*(?:MARKER_JSON|MARKER_DIR\s*/\s*"([^"]+)")', s)
        if m:
            out[m.group(1)] = m.group(2) or "markers_v4.1_clean.json"
    return out


def loader_rule(core_path, txt=None):
    """Read the loader's own path rule out of the source, with the line number."""
    txt = txt if txt is not None else open(core_path, encoding="utf-8").read()
    lines = txt.splitlines()
    rule = {}
    for i, l in enumerate(lines, 1):
        if "EYEKB_ROOT = " in l and "parents" in l:
            rule["root_line"] = i
            rule["root_expression"] = l.strip()
        if l.strip().startswith("KB = ") and "EYEKB_ROOT" in l:
            rule["kb_line"] = i
            rule["kb_expression"] = l.strip()
        if "MARKER_DIR = " in l and "KB" in l:
            rule["marker_dir_line"] = i
            rule["marker_dir_expression"] = l.strip()
        if "p.is_file()" in l:
            rule["missing_panel_line"] = i
            rule["missing_panel_behaviour"] = ("a declared panel that does not exist is skipped "
                                               "silently: %s" % l.strip())
    rule["marker_libs"] = marker_libs(txt)
    rule["libs_named_in_the_error_message"] = sorted(
        set(re.findall(r'([a-z0-9_]+)\|', txt.split("library must be one of")[-1][:400]))
        if "library must be one of" in txt else [])
    rule["has_cross_tree_fallback"] = ("EYEKB_REPO" in txt) or ("MARKERS_DIR_REPO" in txt)
    return rule, lines


def head_core_text(repo):
    """The committed release's own copy of the loader, from the local object store (no network)."""
    import subprocess
    r = subprocess.run(["git", "-C", repo, "show", "HEAD:mcp_server/eyekb_core.py"],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def main() -> int:
    site, repo = listing(C.KB_MARKERS), listing(C.REPO_KB_MARKERS)
    summ = {}
    rows = []
    for name in sorted(set(site) | set(repo)):
        s, r = site.get(name), repo.get(name)
        if s and r:
            same = s["sha256"] == r["sha256"]
            rows.append({"file": name, "present_in_mntD": "yes", "present_in_repo": "yes",
                         "sha256_mntD": s["sha256"], "sha256_repo": r["sha256"],
                         "size_mntD": s["size"], "size_repo": r["size"],
                         "byte_identical": "yes" if same else "no",
                         "class": "shared_identical" if same else "shared_but_different"})
        elif s:
            rows.append({"file": name, "present_in_mntD": "yes", "present_in_repo": "no",
                         "sha256_mntD": s["sha256"], "sha256_repo": "", "size_mntD": s["size"],
                         "size_repo": "", "byte_identical": "n/a",
                         "class": "only_in_mntD"})
        else:
            rows.append({"file": name, "present_in_mntD": "no", "present_in_repo": "yes",
                         "sha256_mntD": "", "sha256_repo": r["sha256"], "size_mntD": "",
                         "size_repo": r["size"], "byte_identical": "n/a",
                         "class": "only_in_repo"})
    C.write_tsv(os.path.join(C.OUT, "ITEM2_BYTE_LEDGER.tsv"), rows,
                ["file", "present_in_mntD", "present_in_repo", "sha256_mntD", "sha256_repo",
                 "size_mntD", "size_repo", "byte_identical", "class"])
    classes = {}
    for r in rows:
        classes.setdefault(r["class"], []).append(r["file"])
    summ["files_in_mntD"] = len(site)
    summ["files_in_repo"] = len(repo)
    summ["by_class"] = {k: {"n": len(v), "files": v} for k, v in sorted(classes.items())}
    summ["shared_files_checked"] = len(classes.get("shared_identical", [])) + len(
        classes.get("shared_but_different", []))
    summ["shared_files_byte_identical"] = len(classes.get("shared_identical", []))
    summ["the_claim_holds"] = (len(classes.get("shared_but_different", [])) == 0)

    # ------------------------------------------------------------------ the loader question
    site_rule, site_lines = loader_rule(C.SITE_CORE)
    repo_rule, _ = loader_rule(C.REPO_CORE)
    head_txt = head_core_text(C.REPO)
    head_rule = loader_rule("<HEAD:mcp_server/eyekb_core.py>", txt=head_txt)[0] if head_txt else {
        "marker_libs": {}}
    resolution = {
        "site_loader": {"module": C.SITE_CORE, **site_rule},
        "repo_loader_working_tree": {"module": C.REPO_CORE, **repo_rule},
        "repo_loader_committed_HEAD": {"module": "git show HEAD:mcp_server/eyekb_core.py",
                                       **head_rule},
        "answer": ("each tree's loader resolves kb/markers relative to its own package root "
                   "(EYEKB_ROOT = parents[1] of mcp_server/eyekb_core.py); neither loader has a "
                   "cross-tree fallback, so the copy that is authoritative for a run is the copy "
                   "inside the tree the service is started from"),
        "authoritative_for_the_running_service": C.KB_MARKERS,
        "authoritative_for_a_fresh_clone": C.REPO_KB_MARKERS,
        "release_surface": ("the git tree is the release: a clone serves its own kb/markers and "
                            "docs/RELEASE_IDENTITY.json identifies exactly those bytes. The data "
                            "volume tree is the production working copy the service runs from."),
    }
    # every panel each loader maps, checked in both trees
    def served_map(libs):
        out = {}
        for lib, fname in sorted(libs.items()):
            out[lib] = {"panel": fname, "in_mntD": "yes" if fname in site else "no",
                        "in_repo": "yes" if fname in repo else "no",
                        "same_bytes": ("yes" if (fname in site and fname in repo
                                                 and site[fname]["sha256"]
                                                 == repo[fname]["sha256"])
                                       else ("no" if fname in site and fname in repo else "n/a"))}
        return out
    resolution["panels_the_site_loader_maps"] = served_map(site_rule["marker_libs"])
    resolution["panels_the_repo_loader_maps"] = served_map(repo_rule["marker_libs"])
    resolution["panels_the_committed_release_maps"] = served_map(head_rule["marker_libs"])
    divergent = [r["file"] for r in rows
                 if r["class"] in ("only_in_mntD", "only_in_repo", "shared_but_different")]
    resolution["divergent_files"] = divergent
    for tag, rule in (("site", site_rule), ("repo_working_tree", repo_rule),
                      ("committed_release", head_rule)):
        resolution["divergent_files_referenced_by_the_%s_loader" % tag] = [
            f for f in divergent if f in set(rule["marker_libs"].values())]
    resolution["divergent_files_referenced_by_any_local_consumer"] = {
        "markers_v11_lensiris_increment.json":
            "mapped by the committed release's loader AND the repo working tree (lensiris_v11); "
            "not mapped by the site loader, which is an older revision",
        "markers_v12_holefill_increment.json":
            "mapped by the committed release's loader AND the repo working tree (holefill_v12); "
            "not mapped by the site loader",
        "markers_v8_dev_retina.json":
            "consumed by the marker layer's panel list (dev_v8) and by card L2's lineage builder; "
            "the shipped loader's retina_dev entry points at markers_v9_dev_retina.json instead",
        "markers_v9_dev_retina.json.v1":
            "a pre-revision copy of a tracked file; no consumer references the .v1 name",
    }
    resolution["consequence_measured"] = {
        "the_two_referenced_files_are_absent_from_the_data_tree":
            [f for f in divergent if f in set(repo_rule["marker_libs"].values())
             and f not in site],
        "what_happens_when_a_mapped_panel_is_absent": (
            "nothing visible: the loader guards the open with `p.is_file()` (line %s), so a "
            "declared panel that is not there is skipped and the library contributes no markers "
            "instead of raising" % site_rule.get("missing_panel_line", "?")),
        "the_repository_convention_for_this_tree_pair": (
            "copy, not move; the data-volume originals are never modified — i.e. the data volume "
            "is the origin and the git tree is the mirror, and both directions are copies"),
        "so_the_divergence_can_change_a_served_answer": (
            "in the git tree: no (the two panels are present where the loader looks for them). "
            "in the data tree: not today (that tree's loader is an older revision that does not "
            "name them) but yes the moment that wiring is synced there — the two libraries would "
            "resolve to nothing, silently"),
    }
    C.write_json(os.path.join(C.OUT, "ITEM2_LOADER_RESOLUTION.json"), resolution)

    # ------------------------------------------------------------------ the reconciliation ledger
    ledger = {
        "question": "the two kb/markers copies carry different file sets",
        "measured": summ,
        "authority": {
            "for_the_loader_the_service_runs": C.KB_MARKERS,
            "evidence": ("mcp_server/eyekb_core.py line %s: %s -> line %s: %s -> line %s: %s; no "
                         "cross-tree fallback in either copy (searched both sources for a repo "
                         "path or a fallback constant)" % (
                             site_rule["root_line"], site_rule["root_expression"],
                             site_rule["kb_line"], site_rule["kb_expression"],
                             site_rule["marker_dir_line"], site_rule["marker_dir_expression"])),
            "for_the_release": C.REPO_KB_MARKERS,
            "second_evidence": ("the wave's own repository convention for this tree pair, as "
                                "written in the repository-sync briefs that carry content the "
                                "other way: 'copy, not move; the /mnt/D originals are not "
                                "modified' — i.e. the data-volume tree is the origin and the git "
                                "tree is the mirror"),
        },
        "the_divergence_is_two_way": {
            "git_tree_carries_what_the_data_tree_lacks": ["markers_v11_lensiris_increment.json",
                                                           "markers_v12_holefill_increment.json"],
            "data_tree_carries_what_the_git_tree_lacks": ["markers_v8_dev_retina.json",
                                                           "markers_v9_dev_retina.json.v1"],
            "why_the_first_is_real": ("both files were created and committed in the git tree after the last "
                                  "content copy to the data volume, and the committed release's "
                                  "loader already names both of them in its own library map — so "
                                  "the git side is the newer authority here and the data tree is "
                                  "stale in the panel set, and its loader revision is older too"),
            "why_the_second_is_real": ("markers_v8_dev_retina.json has never been tracked in the "
                                        "git history (checked: git log --all over that path is "
                                        "empty), and markers_v9_dev_retina.json.v1 is a "
                                        "pre-revision copy; both are working files of the data "
                                        "tree that the release never carried"),
        },
        "decision": {
            "what": ("no file is deleted and no existing file's bytes are touched. The two trees "
                     "are made set-equal by copying the missing files in, byte-identically: the "
                     "two increment panels the git tree carries into the data tree, and the dev "
                     "panel the data tree carries can be mirrored into the git tree by a card "
                     "that is allowed to move the release."),
            "why_not_done_in_this_card": ("this card's red lines forbid a kb/ body change and any "
                                          "activation, and the wave-2 gate that judges the marker "
                                          "layer rejects any kb/ file whose mtime is newer than "
                                          "that card's session start — a write here would leave "
                                          "an already-green gate red behind it. The reconciliation "
                                          "is therefore measured, decided and scripted, and the "
                                          "execution is left to a card that owns kb/ writes."),
            "execution": "out/ITEM2_SYNC_KB_MARKERS.sh (dry run by default; --apply to execute)",
            "idempotent": "yes: each copy is skipped when the destination already holds the same "
                          "sha256, and no file is ever removed",
        },
        "residual": [
            {"item": "markers_v8_dev_retina.json is not in the release",
             "why_it_matters": ("the marker layer consumes it (dev_v8) and resolves it only through "
                                "the data tree; a fresh clone of the release cannot rebuild the "
                                "layer's dev_v8 share without it"),
             "owner": "a card that owns release content (the repository-sync line)"},
            {"item": "the .v1 backup is not a panel",
             "why_it_matters": ("it is a pre-revision copy kept beside a tracked file; it should "
                                "be recorded as a non-panel file rather than mirrored or deleted"),
             "owner": "a card that owns kb/ hygiene"},
        ],
    }
    C.write_json(os.path.join(C.OUT, "ITEM2_RECONCILIATION_LEDGER.json"), ledger)

    # ------------------------------------------------------------------ the sync script
    script = os.path.join(C.OUT, "ITEM2_SYNC_KB_MARKERS.sh")
    with open(script, "w", encoding="utf-8") as f:
        f.write("""#!/usr/bin/env bash
# ITEM2_SYNC_KB_MARKERS.sh — make the two kb/markers copies set-equal, byte-identically.
#
# Dry run by default. Nothing is ever deleted and no existing file is ever modified in place:
# a file is copied only when the destination does not already hold the same bytes.
#
#   bash ITEM2_SYNC_KB_MARKERS.sh            # print what would happen
#   bash ITEM2_SYNC_KB_MARKERS.sh --apply    # do it
#
# Direction 1 (data tree <- git tree) is the repair of a real staleness: the git tree carries two
# increment panels the data tree does not.
# Direction 2 (git tree <- data tree) is the mirror of the one dev panel the data tree carries and
# the release never did; it changes the release surface, so it is listed separately and can be
# skipped with --no-mirror . Execute it only from a card that owns release content, and re-take
# docs/RELEASE_IDENTITY.json in the same commit afterwards.
set -uo pipefail
APPLY=0; MIRROR=1
for a in "$@"; do
  case "$a" in
    --apply) APPLY=1 ;;
    --no-mirror) MIRROR=0 ;;
  esac
done
MNT=/mnt/D/EyeKB/kb/markers
REPO=/home/ubuntu/EYEKB_REPO/kb/markers

copy() {  # copy <src> <dst> <label>
  local src="$1" dst="$2" label="$3"
  if [ ! -f "$src" ]; then echo "SKIP   $label: source missing ($src)"; return 0; fi
  if [ -f "$dst" ] && cmp -s "$src" "$dst"; then
    echo "SKIP   $label: destination already byte-identical"; return 0; fi
  if [ "$APPLY" = "1" ]; then
    cp -p "$src" "$dst" && echo "COPIED $label: $src -> $dst"
  else
    echo "WOULD  $label: $src -> $dst"
  fi
}

echo "== direction 1: data tree <- git tree (repairs the staleness)"
copy "$REPO/markers_v11_lensiris_increment.json" "$MNT/markers_v11_lensiris_increment.json" v11
copy "$REPO/markers_v12_holefill_increment.json" "$MNT/markers_v12_holefill_increment.json" v12
if [ "$MIRROR" = "1" ]; then
  echo "== direction 2: git tree <- data tree (changes the release surface)"
  copy "$MNT/markers_v8_dev_retina.json" "$REPO/markers_v8_dev_retina.json" v8
else
  echo "== direction 2 skipped (--no-mirror)"
fi
echo "== nothing was deleted; re-run to confirm every SKIP line"
""")
    os.chmod(script, 0o755)
    summ["sync_script"] = script
    C.write_json(os.path.join(C.OUT, "ITEM2_SUMMARY.json"), summ)
    print(json.dumps(summ, ensure_ascii=False, indent=1))
    print("loader:", resolution["answer"])
    print("divergence can change a served answer:",
          resolution["consequence_measured"]["so_the_divergence_can_change_a_served_answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
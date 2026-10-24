#!/usr/bin/env bash
# reset_tree.sh -- put the two repo files this wave edits back to their pre-cl56 state and remove the
# increment, so b1/w1 can be re-run from a pristine tree.
#
# Why: /mnt/D is an NTFS mount where cp -p cannot restore the file mode, so the label map comes back
# as 755 and shows up as a git mode change. The mode is re-set here explicitly.
set -euo pipefail
REPO=/home/ubuntu/EYEKB_REPO
W=/mnt/D/EyeKB/plans/cl56_adopt_20261022
cp "$W/pre_images/eyekb_core.py.pre_cl56" "$REPO/mcp_server/eyekb_core.py"
cp "$W/pre_images/markers_cl_alignment_v2_unified.json.pre_cl56" "$REPO/kb/markers/markers_cl_alignment_v2_unified.json"
rm -f "$REPO/kb/markers/markers_v15_cl56_increment.json"
chmod 644 "$REPO/mcp_server/eyekb_core.py" "$REPO/kb/markers/markers_cl_alignment_v2_unified.json"
rm -f "$W/out/WIRING.json" "$W/out/BUILD.json" "$W/out/PREIMAGE.json"
cd "$REPO"
echo "--- git status (expect empty):"
git status --short
test -z "$(git status --short)" && echo "TREE CLEAN = pristine" || echo "WARN: tree not pristine"
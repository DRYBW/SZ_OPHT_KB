#!/usr/bin/env bash
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

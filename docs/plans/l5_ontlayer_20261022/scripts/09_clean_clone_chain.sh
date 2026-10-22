#!/usr/bin/env bash
# One-shot: run the whole gate chain in a clean clone of the repository, at a path whose name
# contains spaces, with no reliance on the author tree.
#
#   bash <this script> <source repo> <clone dir> <corpus source> <interpreter with mcp>
#
# The literature corpus is copied in because it is not part of the git tree (contract §G2: the corpus
# is a Release asset, not a repository file). Copying a local directory is not a download.
set -eu

SRC="$1"; CLONE="$2"; CORPUS_SRC="$3"; PY="${4:-/home/ubuntu/.conda/envs/pipeline_env/bin/python}"

# Standard directories first: this script is launched from environments whose PATH may lack them, and
# every command below (rm, mkdir, git, cp, du, bash) has to be findable before anything else runs.
export PATH="/usr/local/bin:/usr/bin:/bin:$(dirname "$PY"):${PATH:-}"
unset PYTHONPATH || true

rm -rf "$CLONE"
mkdir -p "$(dirname "$CLONE")"
git clone --quiet --no-hardlinks "$SRC" "$CLONE"
printf '[clone] %s\n[clone] head=%s\n[clone] worktree_clean=%s\n' "$CLONE" \
  "$(git -C "$CLONE" rev-parse HEAD)" \
  "$( [ -z "$(git -C "$CLONE" status --porcelain)" ] && echo yes || echo no )"

mkdir -p "$CLONE/literature_db"
cp -r "$CORPUS_SRC" "$CLONE/literature_db/"
printf '[clone] corpus: %s at literature_db/%s\n' "$(du -sh "$CLONE/literature_db" | cut -f1)" \
  "$(basename "$CORPUS_SRC")"

export EYEKB_G3_PY="$PY"
export EYEKB_G7_PY="$PY"
export EYEKB_CORPUS="$CLONE/literature_db/$(basename "$CORPUS_SRC")"
export EYEKB_GATE_OUT="$CLONE/.gate_out"

cd "$CLONE"
bash tests/run_gates.sh
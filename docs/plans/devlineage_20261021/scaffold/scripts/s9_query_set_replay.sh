#!/usr/bin/env bash
# s9_query_set_replay.sh - default behaviour, proven by replaying the project's recorded query set.
#
# The repository already records a query set with its expected answers: tests/REPRO_EXPECTED.json
# holds 41 recorded (cell type, species, tissue) retrieval cases with the top-5 PubMed ids each
# produced, and tests/verify_repro.py replays them through the shipped retrieval engine. Replaying it
# answers the card's red line - "default behaviour byte-identical: replay the recorded query set and
# report the difference count" - with a number instead of a claim.
#
# This card adds a directory under plans/ and touches nothing in the repository, so the expected
# result is 0 differing cases. Run it and read the number:
#
#   bash scripts/s9_query_set_replay.sh
#
# Requirements (all local, nothing downloaded): the Release slim corpus that ships with the mirror
# repo (literature_db/v2.4.2_2026-09_slim), the BAAI/bge-large-en-v1.5 weights already on this
# machine, and the G1-locked interpreter (pipeline_env). The run is executed under the same
# zero-network audit hook as the rest of the chain, with the offline flags set so a missing local
# model cannot turn into a silent download.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WAVE="$(cd "$HERE/.." && pwd)"
REPO="${EYEKB_REPO:-/home/ubuntu/EYEKB_REPO}"
PY="${EYEKB_G3_PY:-/home/ubuntu/.conda/envs/pipeline_env/bin/python}"

export SCAFFOLD_NET_AUDIT_LOG="$WAVE/ledgers/query_replay_net_audit.log"
export PYTHONPATH="$WAVE/scripts/netaudit${PYTHONPATH:+:$PYTHONPATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_DATASETS_OFFLINE=1
echo "# query-set replay start $(date -Is)" >> "$SCAFFOLD_NET_AUDIT_LOG"

cd "$REPO" || exit 2
timeout 1800 "$PY" tests/verify_repro.py --db-dir literature_db/v2.4.2_2026-09_slim \
    > "$WAVE/ledgers/QUERY_REPLAY.txt" 2>&1
rc=$?
EVENTS=$(grep -c '^EVENT' "$SCAFFOLD_NET_AUDIT_LOG" || true)
HOOKS=$(grep -c '^# hook-installed' "$SCAFFOLD_NET_AUDIT_LOG" || true)
{
  echo "# recorded query-set replay (repo: $REPO, interpreter: $PY)"
  echo "verify_repro_rc=$rc"
  echo "hook_install_lines=$HOOKS"
  echo "network_event_lines=$EVENTS"
  grep -E "REPRO (PASS|FAIL|INCONCLUSIVE)" "$WAVE/ledgers/QUERY_REPLAY.txt" || true
} | tee "$WAVE/ledgers/QUERY_SET_REPLAY_SUMMARY.txt"
exit "$rc"
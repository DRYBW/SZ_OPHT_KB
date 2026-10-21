#!/usr/bin/env bash
# V3 stage axis / run-time network audit.
# Re-runs the two executable steps of this card (the recognition probe and the change-legitimacy
# check) with the audit hook installed through PYTHONPATH, so every Python process of the run —
# including the shipped server started as a stdio subprocess — is observed.
#
# Writes: logs/net_audit.log (control lines + any event lines), logs/07_net_audit.log (this run).
set -u
cd "$(dirname "$0")/.." || exit 1
HERE="$(pwd)"
LOG="$HERE/logs/net_audit.log"
: > "$LOG"
export V3_NET_AUDIT_LOG="$LOG"
export PYTHONPATH="$HERE/discipline/net_audit:${PYTHONPATH:-}"
SDK_PY=/home/ubuntu/training-venv/bin/python3

{
  echo "== audit log: $LOG"
  echo "== step: recognition probe (pass 3, audit-instrumented)"
  "$SDK_PY" scripts/02_probe_recognition.py --pass 3
  echo "== step: change-legitimacy check (audit-instrumented)"
  python3 scripts/04_change_legitimacy_check.py > /dev/null
  echo "== audit summary"
  python3 - "$LOG" <<'EOF'
import sys
lines = open(sys.argv[1], encoding="utf-8").read().splitlines()
ctrl = [l for l in lines if l.startswith("#")]
ev = [l for l in lines if l.startswith("EVENT")]
print(f"hook_install_lines={len(ctrl)} event_lines={len(ev)}")
for l in ev[:20]:
    print(l)
EOF
} 2>&1 | tee "$HERE/logs/07_net_audit.log"
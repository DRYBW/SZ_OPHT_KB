#!/usr/bin/env bash
# BTEST D9 链：run1 三席并行 → run2 三席并行 → verdict。断点续跑（runner 内 DONEF）。
# 每席失败自动 resume 一次（rc=2=missing）。任何席二次仍失败 → 中止链，status 记 FAILED。
set -u
export PATH=/bin:/usr/bin:/usr/local/bin:/home/ubuntu/training-venv/bin:"$PATH"
PY=/home/ubuntu/training-venv/bin/python
ROOT=/mnt/D/EyeKB/plans/btest_20260927
cd "$ROOT" || exit 1
STATUS=logs/chain_status.txt
echo "$(date '+%F %T') chain start" >> "$STATUS"

run_seat () { # $1=model $2=stem $3=run
  local m="$1" s="$2" r="$3"
  $PY scripts/btest_runner.py "$m" "$s" "$r" >> "logs/${r}_${s}.out" 2>> "logs/${r}_${s}.err"
  local rc=$?
  if [ $rc -ne 0 ]; then
    echo "$(date '+%F %T') ${r}/${s} rc=${rc} — resume once" >> "$STATUS"
    $PY scripts/btest_runner.py "$m" "$s" "$r" >> "logs/${r}_${s}.out" 2>> "logs/${r}_${s}.err"
    rc=$?
  fi
  echo "$(date '+%F %T') ${r}/${s} final_rc=${rc}" >> "$STATUS"
  return $rc
}

wave () { # $1=run1|run2
  r="$1"
  run_seat qwen3.8-max A "$r" & p1=$!
  run_seat glm-5.1 B "$r" & p2=$!
  run_seat deepseek-v3.2 C "$r" & p3=$!
  wait $p1; rc1=$?
  wait $p2; rc2=$?
  wait $p3; rc3=$?
  echo "$(date '+%F %T') wave $r rc A=$rc1 B=$rc2 C=$rc3" >> "$STATUS"
  [ $rc1 -eq 0 ] && [ $rc2 -eq 0 ] && [ $rc3 -eq 0 ]
}

wave run1 || { echo "$(date '+%F %T') CHAIN ABORT: run1 failed" >> "$STATUS"; exit 2; }
wave run2 || { echo "$(date '+%F %T') CHAIN ABORT: run2 failed" >> "$STATUS"; exit 2; }
$PY scripts/btest_verdict.py > logs/verdict.out 2> logs/verdict.err
rcv=$?
echo "$(date '+%F %T') verdict rc=${rcv}" >> "$STATUS"
if [ $rcv -eq 0 ]; then
  echo "$(date '+%F %T') CHAIN DONE" >> "$STATUS"
else
  echo "$(date '+%F %T') CHAIN FAIL verdict" >> "$STATUS"
fi
exit $rcv

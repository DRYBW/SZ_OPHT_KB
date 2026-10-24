#!/usr/bin/env bash
# B-arm GPU driver: arbiter lease -> systemd-run -> pin the real MainPID -> wait -> release.
# Template = plans/toolbenchmark_20261010_x4clean/scripts/x4arms/gpu_x4a1b.sh (in-register precedent).
export PATH=/usr/bin:/bin:/usr/local/bin:$PATH
ARB=/home/ubuntu/.hermes/scripts/gpu_arbiter.sh
P=/mnt/D/EyeKB/plans/fairex4a_20261024
PY=/home/ubuntu/.conda/envs/eyescgpt/bin/python
STAMP=$(date +%s)
mkdir -p $P/logs $P/work $P/out

# protocol-required pre-stop snapshot
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv \
  > $P/logs/gpu_compute_apps_before_$STAMP.csv 2>&1
awk '/^MemAvailable:/{printf "available_GB=%.1f\n",$2/1024/1024}' /proc/meminfo

bash $ARB lease-acquire fairex4a 20000 || { echo "FAIRX4A_LEASE_FAIL"; exit 1; }
echo "lease acquired $(date '+%F %T')"
trap 'bash $ARB lease-release fairex4a; echo "LEASE_RELEASED $(date "+%F %T")"' EXIT

run_one () {  # $1 = tag, $2 = h5ad, $3 = out npy
  local TAG=$1 H5=$2 OUT=$3
  local UNIT=fairex4a-$TAG-$STAMP
  systemd-run --user --unit=$UNIT --working-directory=$P -p MemoryMax=60G -p MemorySwapMax=0 \
    $PY $P/scripts/30_embed.py --h5ad $H5 --out $OUT \
    --timelog $P/work/embed_${TAG}_runtime.json \
    > $P/logs/embed_${TAG}.log 2>&1
  local PID=""
  for i in $(seq 1 30); do
    PID=$(systemctl show -p MainPID --value $UNIT.service 2>/dev/null)
    [ -n "$PID" ] && [ "$PID" != "0" ] && break
    sleep 2
  done
  echo "unit=$UNIT MainPID=$PID"
  bash $ARB lease-setpid $PID || { echo "SETPID_FAIL unit=$UNIT"; exit 2; }
  while systemctl --user is-active $UNIT.service >/dev/null 2>&1; do sleep 30; done
  systemctl --user status $UNIT.service --no-pager 2>/dev/null | tail -3 >> $P/logs/embed_${TAG}.log
  echo "unit $UNIT exited $(date '+%F %T')"
}

run_one x4a $P/work/q5_x4a_hvg5000.h5ad $P/work/E_x4a.npy
run_one ref $P/work/ref_hra006282.h5ad  $P/work/E_ref_hra006282.npy
echo "FAIRX4A_GPU_DRIVER_DONE $(date '+%F %T')"
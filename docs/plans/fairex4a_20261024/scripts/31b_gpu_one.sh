#!/usr/bin/env bash
# Single-job GPU driver: 31b_gpu_one.sh <tag> <h5ad> <out.npy>
# Used for the instrument-repeatability runs (run-to-run noise floor of the A1b instrument).
export PATH=/usr/bin:/bin:/usr/local/bin:$PATH
ARB=/home/ubuntu/.hermes/scripts/gpu_arbiter.sh
P=/mnt/D/EyeKB/plans/fairex4a_20261024
PY=/home/ubuntu/.conda/envs/eyescgpt/bin/python
TAG=$1; H5=$2; OUT=$3
STAMP=$(date +%s)
mkdir -p $P/logs $P/work $P/out
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv \
  > $P/logs/gpu_compute_apps_before_${TAG}_$STAMP.csv 2>&1

bash $ARB lease-acquire fairex4a-$TAG 20000 || { echo "LEASE_FAIL $TAG"; exit 1; }
echo "lease acquired $TAG $(date '+%F %T')"
trap 'bash $ARB lease-release fairex4a-'"$TAG"'; echo "LEASE_RELEASED $TAG $(date "+%F %T")"' EXIT

UNIT=fairex4a-$TAG-$STAMP
systemd-run --user --unit=$UNIT --working-directory=$P -p MemoryMax=60G -p MemorySwapMax=0 \
  $PY $P/scripts/30_embed.py --h5ad $H5 --out $OUT \
  --timelog $P/work/embed_${TAG}_runtime.json > $P/logs/embed_${TAG}.log 2>&1
PID=""
for i in $(seq 1 60); do
  PID=$(systemctl show -p MainPID --value $UNIT.service 2>/dev/null)
  [ -n "$PID" ] && [ "$PID" != "0" ] && break
  sleep 2
done
echo "unit=$UNIT MainPID=$PID"
[ -n "$PID" ] && [ "$PID" != "0" ] && bash $ARB lease-setpid $PID
while systemctl --user is-active $UNIT.service >/dev/null 2>&1; do sleep 20; done
systemctl --user status $UNIT.service --no-pager 2>/dev/null | tail -3 >> $P/logs/embed_${TAG}.log
echo "unit $UNIT exited $(date '+%F %T')"
echo "GPU_ONE_DONE $TAG $(date '+%F %T')"
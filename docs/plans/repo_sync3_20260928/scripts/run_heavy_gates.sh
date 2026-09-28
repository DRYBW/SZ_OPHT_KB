#!/bin/bash
# REPOSYNC3 长门链：T8（§9 盘点，读 3×1GB parquet）→ T1 golden41（CPU embedding）→ T6（1GB 重切+API）
# 串行防 IO/CPU 抢核；全绝对路径（后台环境 PATH 剥离先例）
set -x
cd /home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928
export EYEKB_STG=/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928
VENV=/home/ubuntu/training-venv/bin/python
echo "=== T8 START $(date) ==="
$VENV docs/plans/repo_sync3_20260928/scripts/t8_s9_screening.py
echo "T8_RC=$?"
echo "=== T1 golden41 START $(date) ==="
$VENV docs/plans/repo_sync3_20260928/scripts/t1_golden41_off.py OFF
echo "G41_RC=$?"
echo "=== T6 START $(date) ==="
$VENV docs/plans/repo_sync3_20260928/scripts/t6_release_reverify.py
echo "T6_RC=$?"
echo "=== CHAIN DONE $(date) ==="

# COMMAND LOG — subdivision_readiness_20261022

Every command that produced a number in this wave. Heavy steps ran under
`systemd-run --user --scope -p MemoryMax=… -p MemorySwapMax=2G` with the zero-network audit hook on
(`PYTHONPATH=discipline/net_audit`, `SR_NET_AUDIT_LOG=logs/netaudit_chain.log`).

| # | command | wall | peak RSS (MB) | log |
|---|---|---:|---:|---|
| 1 | `python3 scripts/r_recon.py` | 0:04.05 | 26.5 | `logs/r_recon.log` |
| 2 | `python3 scripts/m_scan.py` | 2:47.03 | 953.9 | `logs/m_scan_v2.log` |
| 3 | `python3 scripts/m_state.py` | 0:35.79 | 596.9 | `logs/m_state.log` |
| 4 | `python3 scripts/m_state2.py` | 0:21.76 | 502.7 | `logs/m_state2.log` |
| 5 | `python3 scripts/m_material.py` | 13:47.62 | 16321.4 | `logs/m_material.log` |
| 6 | `python3 scripts/m_observe.py` | 0:00.17 | 22.6 | `logs/m_observe.log` |
| 7 | `python3 scripts/m_readiness.py` | 0:00.92 | 25.2 | `logs/m_readiness_v4.log` |
| 8 | `python3 scripts/m_cost.py` | 0:01.19 | 30.9 | `logs/m_cost_v4.log` |
| 9 | `python3 scripts/m_confusion.py` | 0:27.23 | 830.2 | `logs/m_confusion_v2.log` |
| 10 | `python3 scripts/golden_721.py out/golden_721_replay.json` | 0:06.01 | 151.4 | `logs/golden_721_v2.log` |
| 11 | `python3 scripts/m_report.py` | 0:00.07 | 24.3 | `logs/m_report.log` |
| 12 | `bash <clean clone>/tests/run_gates.sh` | not timed | — | `logs/gates_cleanclone_v2.log` |
| 13 | `python3 scripts/m_append.py` | not timed | — | `logs/m_append_v2.log` |

Untimed steps (pure text generation / reads, no heavy compute): `m_observe.py` (recorded windows),
`m_append.py` (addendum generation + append + proof), `golden_721.py` when run without `/usr/bin/time`.

## Gate readout (clean clone, not the author tree)

```
G4 PASS: 3/3 byte-identical
G3 verify_repro (41-query retrieval anchor) rc=0 pass
G4 verify_pipeline (three byte anchors) rc=0 pass
G5 gate_registry (registry surface enforced) rc=0 pass
G6 gate_change_control (eight machine rules) rc=0 pass
gates=4 failed=0 (CHAIN PASS)
```

## Network audit receipt

- audit hook load markers: **26**
- connection-class events (socket.connect / getaddrinfo / urllib / http.client): **0**
- socket-object construction events (`socket.__new__`, fd=-1): **0**

Zero connection-class events across the whole chain; no download was performed and none was attempted.

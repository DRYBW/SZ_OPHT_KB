# Developmental scaffold — enumerated nodes and edges, coverage denominator, decapitated branches

This directory is this card's construction site: `plans/devlineage_20261021/scaffold/`.

It is the **scaffold** workstream of the developmental lineage layer. The marker layer (`markers/`)
and the stage axis (`stages/`) are sibling cards building against the same frozen contract; this
directory owns nodes, edges, relation typing, the coverage denominator and the register, and every
edge row leaves `marker_change_ids` empty for the marker layer to fill.

Read in this order:

| file | what it is |
|---|---|
| `REPORT.md` | the report: what was enumerated, the counts, the reconciliation with the first pass, and what remains unreachable |
| `out/SCAFFOLD_NODES.tsv` | the enumerated node set in the contract's key grammar, with per-field provenance |
| `out/SCAFFOLD_EDGES_CONFIRMED.tsv` | the confirmed graph — one row per ordered pair, typed and graded (this is the per-edge grade table) |
| `out/DECAPITATED_BRANCHES.tsv` | the register: every branch no local source can head, its break point, its cell mass, its repair route |
| `out/PENDING_ASSERTIONS.tsv` | literature-repair proposals with resolvable anchors — **never** edges |
| `out/COVERAGE_DENOMINATOR.tsv` | the denominator, count by count |
| `out/GATE_SCAFFOLD.json` | the machine verdict (10 rules) |

Binding upstream: `../DATA_CONTRACT_devlineage_v1.md` (frozen; do not fork a private dialect) and
`../BRIEF_V4_SCAFFOLD_EXPANSION_20261021.md`. The peer artefact this extends is
`../cl_depth_devlineage_20261021/` (commit `8492dd3adf1e281f5590e8c144053116613713af`).

## Reproduce

```bash
cd /mnt/D/EyeKB/plans/devlineage_20261021/scaffold
bash scripts/run_all.sh                    # corpus scan, builds, replay, report numbers, manifest, gate, network audit
bash scripts/s9_query_set_replay.sh        # the repository's recorded query set: 41/41, difference count 0
bash scripts/s10_resource_readings.sh      # the resource readings the report quotes
python3 scripts/s8_gate_scaffold.py        # the gate alone (rc 0 = PASS, rc 2 = FAIL)
sha256sum -c out/MANIFEST.sha256           # run from this directory; paths in the manifest are relative to it
```

Everything is stdlib + pyarrow; the corpus scan streams the 1.08 GB chunk table without its 1 GB
embedding column and peaks at 0.20 GiB. Zero network is enforced by an audit hook that covers child
processes (`scripts/netaudit/sitecustomize.py`), with load receipts so "no events" cannot be confused
with "the hook never ran".

## Scripts

| script | what it does |
|---|---|
| `s0_reverify_upstream.py` | re-derives every consumed artefact (58 checks) instead of trusting a summary |
| `s1_enum_nodes.py` | ring A library classes (mapped and `NO_MATCH`), ring B ontology intermediates, ring C anchors |
| `s2_enum_edges.py` | native `develops_from` steps and the derived origin rules R-ANCHOR-1/2/3; the peer reconciliation |
| `s3_coverage_denominator.py` | the denominator, per-anchor coverage and the retinal progenitor axis |
| `s4_decapitated_branches.py` | the register |
| `s5_corpus_scan.py` | one streaming pass over the local corpus for *asserted* relations, with anchor verification |
| `s6_pending_assertions.py` | pending repair proposals, rejected rows, the peer weak-row re-examination, the textbook check |
| `s7_afterfact_coverage.py` | the asymmetric coverage reading — the only file that reads the evaluation recording |
| `s8_gate_scaffold.py` | the gate (10 rules, fail-closed) |
| `s9_query_set_replay.sh` | default behaviour proven by replaying the repository's recorded query set |
| `s10_resource_readings.sh` | captures the readings the report quotes |
| `s11_check_report_numbers.py` | recomputes every number the report quotes from the artefacts |

## Three rules this directory will not bend on

1. **A repair proposal is not an edge.** Literature-repair proposals live in
   `out/PENDING_ASSERTIONS.tsv`; the confirmed graph contains only what the local ontology declares,
   plus origin claims whose derived rule is named in the row.
2. **No common-sense arrow.** A class with no `develops_from` statement gets no origin edge, and
   `is_a` is never used as a developmental relation on its own. The result is a sparse confirmed
   graph — 51 edges over 103 nodes — plus a register of 64 named breaks, which is the correct
   outcome for this release.
3. **`unknown` is never defaulted.** Every stage on the four-level axis is either re-derivable from
   the ontology text or from a repository baseline that declares it, or it is `unknown`, and the
   gate re-reads the source for each one.
# Cell Ontology depth and the developmental lineage layer

This directory holds the work for one card: stop using the Cell Ontology as a lookup table, and
build the developmental lineage layer the PI asked for.

Everything here is computed from local authority only: the Cell Ontology release already on disk,
our own marker libraries, our own literature corpus, and our own baseline entries. Nothing was
downloaded; nothing in the lineage is derived from the evaluation volumes. No CL identifier was
typed from memory - each one is read from a line of the ontology file, and the gate re-checks that.

## Read in this order

| file | what it is |
|---|---|
| `REPORT.md` | the report: what was built, the numbers, and what is still unresolved |
| `GRANULARITY_READER_PAGE.md` | what our classes are relative to the literature: same term, coarser, finer, mismatch, or unmapped - over the 721 recorded clusters |
| `LINEAGE_READER_PAGE.md` | the developmental layer: what the germ layers become, how far the ontology carries a chain, and the marker changes along each step |
| `out/` | the machine-readable artefacts the two pages are built from |

## The deliverable in one screen

**Ontology navigation (Task A).** `scripts/ont_nav.py` parses the release, computes the `is_a`
ancestor closure at build time, and names the relation between any two terms as exactly one of
`same_term` / `we_are_coarser` / `we_are_finer` / `true_mismatch` / `no_mapping`. That function -
not a curated list - produces `out/GRANULARITY_FOURWAY_721.tsv`, one row per recorded cluster.

**Granularity, measured.** Over the 721 recorded clusters (1,495,330 cells) the family-level regex
the external tester used scores 41.73% agreement; under ontology authority the same recording
splits into 32.1% identical term, 22.9% where we are coarser, 2.4% where we are finer, 17.9%
genuine mismatch, and 24.6% carrying no CL term on our side. Of the mass his regex called
inconsistent, 10.9% is pure naming, 29.1% is granularity, and 48.3% survives as a real
disagreement (`out/GRANULARITY_SUMMARY.json`).

**Decision-ready candidates (Task A.4).** 56 (our class -> child term) pairs we could adopt, with
the ontology line, the recorded cell counts and the corpus support for each. 25 of the 56 are
stated by a paper we hold; 31 are not, and are reported as gaps rather than dropped
(`out/CHILD_TERM_CANDIDATES.tsv`). Nothing was adopted in this card.

**The lineage layer (Task B).** 60 nodes (52 classes our library covers + 8 germ-layer anchors),
34 edges, every edge carrying an ontology line or a resolvable corpus locator. The ontology
carries a developmental chain for 7 classes; 9 more have only a weak corpus co-occurrence and 36
have no local evidence at all - which is the honest headline, and it is counted in
`out/LINEAGE_UNRESOLVED_DEVELOPMENT.tsv`.

## How to reproduce

```bash
cd /mnt/D/EyeKB/plans/cl_depth_devlineage_20261021
bash scripts/run_all.sh          # corpus scans, builds, replay, manifest, both gates, net audit
```

`run_all.sh` refuses to be quiet: it runs the two corpus scans under
`systemd-run --user -p MemoryMax=8G`, builds every artefact twice and requires the second build to
be byte-identical, writes `out/MANIFEST.sha256`, runs both gates, and reports the network audit
reading. Individual steps can be re-run on their own; `python3 scripts/gate_ontology_nav.py` and
`python3 scripts/gate_lineage.py` are the verdicts (rc 0 = PASS, rc 2 = FAIL). The manifest is
written with paths relative to this directory, so verify it from here:

```bash
cd /mnt/D/EyeKB/plans/cl_depth_devlineage_20261021 && sha256sum -c out/MANIFEST.sha256
```

## Machine-checkable gates

`scripts/gate_ontology_nav.py` (gate A) - nine rules:

| rule | what it refuses |
|---|---|
| A1 ONT_SOURCE | an artefact built against a different ontology file than it claims |
| A2 ID_TRACE | a CL id whose recorded label is not the name the file gives that id, or that has no file line |
| A3 CLOSURE | an ancestor closure that disagrees with a fixed-point recomputation, or a self-ancestor |
| A4 CLASSIFY | a four-way row whose verdict the ontology does not reproduce, or counts that do not reconcile |
| A5 CANDIDATES | a candidate whose child term is not really below our term, or that claims corpus support with no locator |
| A6 LABELMAP | a mapping without provenance, or an unresolved label without a recorded reason |
| A7 CROSSFILE | the two local CL files disagreeing on the terms they share |
| A8 NO_MEMORY_ID | any CL id in the delivered artefacts that does not appear in the ontology file |
| A9 REPLAY | an artefact that drifted from the manifest, or a replay ledger that is not green |

`scripts/gate_lineage.py` (gate B) - seven rules:

| rule | what it refuses |
|---|---|
| B1 NODE_TERM | a node whose CL term does not resolve in the file (with its line) |
| B2 INBOUND | a non-root node with no inbound relation, an edge with no evidence, or a root count that the disclosure does not account for |
| B3 ACYCLIC | a cycle or self edge in the developmental graph |
| B4 STAGE_AXIS | a developing node sitting in an adult baseline entry, or a stage_crossing flag that disagrees with its endpoints |
| B5 MARKER_TRACE | a marker row claiming corpus support without a resolvable paper id |
| B6 NO_EVAL_LEAK | any reference to the evaluation volumes or the evaluation working tree inside the lineage artefacts |
| B7 REPLAY | a lineage artefact that drifted from the manifest, or a replay ledger that is not green |

## Discipline notes

* Zero network: enforced by an audit hook (`scripts/netaudit/sitecustomize.py`) that covers child
  processes, with a load receipt so "no events" cannot be confused with "the hook never ran".
  Reading in `ledgers/NET_AUDIT_SUMMARY.txt`.
* Determinism: every artefact is built twice and compared byte for byte (`ledgers/REPLAY.txt`).
* Intermediate artefacts stay on disk: `out/`, `ledgers/`, `logs/` are all kept.
* `out/GAPCHECK_LINEAGE_vs_BENCHMARK.tsv` is the only file that reads the recorded table against
  the lineage, and it runs strictly afterwards, in the direction the brief allows. Gate B6 proves
  the lineage files themselves carry no reference to the evaluation side.
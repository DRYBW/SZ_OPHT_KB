# EyeKB mirror-repo homogeneity contract (VERIFY CONTRACT, established 2026-09-28)

> Origin (PI's 09-28 hands-on determination): the repo is characterized as a cloneable system mirror,
> but "runs" does not mean "runs out the same thing". Different machines tuning or rebuilding to their
> own understanding will inevitably produce heterogeneous output. This contract extends the "frozen
> goalposts" discipline to the distribution side:
> **any machine executing this contract must produce bit-for-bit homogeneous retrieval output; output
> not produced under the contract is not recognized by this repo.**

## G1 Environment lock
- Dependencies always via `pip install -r requirements.repro.txt` (pinned versions; the CPU index for torch is fine).
- Embedding model fixed to `BAAI/bge-large-en-v1.5` (1024-dim, normalize_embeddings=True); this repo contains no weights.
- Python 3.11+; retrieval acceptance is decided by an actual G3 run — "looks about the same" in arbitrary environments is not promised.

## G2 Data lock (the sole official corpus channel)
- **For reproduction = only the pre-built Release asset counts**: `v2.4.2-rag-assets` (fp16-slim derived asset, 2 parts + sha).
  Download → `cat` concatenate → `sha256sum -c` pass → unpack. If the hash fails, do not unpack.
- fp16-slim is a **derived release asset**: its relationship to the frozen original (fp32) and the bit-for-bit identity proof are in the asset's `manifest.yaml` / `conversion_note.json` / `SLIM_VERIFY.json`.
- The "full rebuild" path from papers.jsonl (RAG_REBUILD.md §2) = **exploratory behavior**: chunking/embedding are environment-sensitive, bit-for-bit identity is not promised, and **its output may never serve as reproduction results nor flow back into this repo's anchors**.

## G3 Acceptance gate (whether homogeneous — one command answers)
```
python tests/verify_repro.py --db-dir literature_db/v2.4.2_2026-09_slim
```
- Criterion: the 41 queries' top5 PMIDs **bit-for-bit identical** to `tests/REPRO_EXPECTED.json`; PASS = this machine shares the anchors' distribution.
- Anchor provenance: the v2.4.2 fp32 original passed three-layer verification (data-layer column identity / runner against the official golden 41/41 regression queries / slim-vs-fp32 top5 bit-for-bit identity with 0.0 top-1 similarity drift), after which the anchor was committed directly from the slim library (see docs/plans/release_slim_v242/).

## G4 Byte-exact anchor for the annotation pipeline (clone-executable, 2026-10-01 revision)
Background: stage_a's neighbourhood/QC computation involves BLAS floating-point reductions; with the thread count unfixed, the same input can produce different cluster counts (upstream confirmed: scanpy #2956, numpy #29933). The `pipeline/run_pipeline.py` entry pins threads by default (`OMP/OPENBLAS/MKL/NUMEXPR/VECLIB_NUM_THREADS=1`, via `setdefault` so explicit overrides are preserved). **For reproduction = do not override these variables.**

One-command acceptance (after installing dependencies per G1 and unpacking the corpus per G2):
```
python tests/verify_pipeline.py
```

### G4.1 The interpreter is part of the contract (KB10d, established 2026-10-01)

**The interpreter driving the pipeline for this gate is pinned to `pipeline_env` and does not inherit
the caller's `sys.executable`** — a precondition for the G4 criterion to hold, not an option. The old
version relied on interpreter inheritance: the same command, started from a terminal / a systemd-run
scope / another venv, landed on different library stacks; same code, same fixture, different bytes
⇒ guaranteed false FAIL across environments.

| Item | Value |
|---|---|
| Pinned interpreter (the one that generated the anchors) | `/home/ubuntu/.conda/envs/pipeline_env/bin/python` |
| Override hook (the only fallback) | `EYEKB_G4_PY=<python path>`; a non-default interpreter prints a `[g4] note:` line |
| Pinned interpreter missing / not executable | `rc=2` + `ENV ERROR` (with fix instructions); **no silent fallback to the current interpreter** |
| The gate script itself | stdlib only, launchable by any `python3` (3.10+) |
| Every run | prints `[g4] interpreter: <path> (python X.Y, source: …)` (the interpreter/source line — literal output of tests/verify_pipeline.py), as a required attachment of any discrepancy report |

Why the interpreter matters: the bytes of `stage_a/processed.h5ad` depend on the float32 write
paths of anndata/numpy/scipy/sklearn. Measured — three stacks, three values (`obs`/`leiden`/counts
layers identical; differences concentrated in the trailing digits of
`X_pca`/`X_umap`/`var`/`dispersions`):

| Interpreter stack | python / scanpy / anndata / numpy / scipy / sklearn | sha256 of `stage_a/processed.h5ad` |
|---|---|---|
| **pipeline_env (= the anchors' stack)** | 3.10.20 / 1.11.5 / 0.11.4 / 2.2.6 / 1.15.3 / 1.7.2 | `dbc657fa…` ✅ anchors |
| training-venv | 3.14.4 / 1.12.2 / 0.12.19 / 2.4.6 / 1.16.3 / 1.9.0 | `f7a461f9…` |
| offline venv / scrnaseq | 3.14.4–3.12 / 1.12.2–1.12.1 / 0.13.2 / 2.4.6 / 1.16.3 / 1.9.0 | `10cfbe…` |

⇒ Two options on external machines: ① install an equivalent annotation stack and point
`EYEKB_G4_PY=/path/to/python` at it (**differences under a non-default interpreter, unless they
also hit the anchors, do not count as new findings**); ② any discrepancy report **must** attach the
gate's printed `[g4] interpreter:` line — a report without it cannot be triaged: the maintainer cannot
distinguish "wrong stack" from "genuine finding".

G4 FAIL triage order (same discipline as §4: check the environment first; modifying criteria to fit
numbers is forbidden):
1. Check the `[g4] interpreter:` line — not `pipeline_env` → **environment problem, not a criteria
   problem**; fix the environment per G4.1 and rerun;
2. fixture sha missed → repo content drift (check against `G4_EXPECTED.json:fixture_sha256`);
3. `ENV ERROR: run_pipeline rc≠0` → annotation-stack dependencies missing, install per the top of
   this file;
4. If the three checks above are clean and it still FAILs = genuine finding: report `got/expected`
   for all three files **plus the interpreter line** to the maintainer; do not re-anchor expected,
   change `--seed`, or swap fixtures yourself.

Criteria = the three-file anchors in `tests/G4_EXPECTED.json`: raw-byte anchors for
`stage_a/processed.h5ad` and `decisions_template.csv`; for `annotation_evidence_report.md` the sha is
taken after timestamp/output-path normalization (the report embeds run time, so a raw-byte anchor
could never be a stable criterion — a design lesson; the v1 anchor contained the report's raw bytes
and was voided). Input fixture = a 600-cell subset sampled from the matrix of a public GEO series
(GSE165784) (`pipeline/fixtures/`, no patient fields; provenance notes in its README).

Anchor provenance: 2026-10-01, three runs consistent (production fp32 default library ×2, Release
slim library ×1; committed after two-level identity — byte-for-byte and normalized). The S0 gate's
required asset `pipeline/assets/s0/species_assets.pkl` is now distributed with the repo (added after
an external machine found it missing; rebuildable from public NCBI orthologs/gene_info via
`assets/s0/build_assets.py`).

History: v1 (2026-10-01 morning) used maintainer-side three-file sha anchors; the same-day
external-usability self-check exposed two real defects — ① the clone could not run without the S0
asset; ② the report file contains timestamps and cannot serve as a byte anchor — the current version
is the post-fix re-anchor; the pre-09-30 anchor file (`19bf2ecb…`) belongs to the code state before
the default-library switch and the S0 wiring, is archived at
`plans/wire_p1_20260930/out/baseline1/`, and is no longer a criterion.

## §4 Three-layer triage order for FAIL (no modifying criteria to fit numbers)
1. G2: does the pre-built asset's sha match (most common: wrong file / wrong concatenation order);
2. G1: were dependencies installed per the lock (torch/sentence-transformers drift);
3. is the model the official bge-large-en-v1.5.
Still FAIL = genuine finding: report per-case diffs to the maintainer; do not tune parameters, change top_k, switch models, or re-anchor expected yourself.

## §5 Change discipline
- Updating the expected anchors and the requirements lock = a maintainer-side, evidence-bearing action (three-layer verification rerun + version number + date); cloners have no authority to edit them.
- If the service/engine code version changes, the README version notes and this contract update in the same commit.

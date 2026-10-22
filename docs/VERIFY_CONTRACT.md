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

**Rewrite-layer precondition (2026-10-05, mandatory).** The G4 gate must be run with the Chinese query-rewrite layer explicitly closed — `EYEKB_CN_REWRITE=0` (equivalently `off`/`false`/`no`). The layer's default is ON since 2026-10-05; with it active, an evidence report produced through `pipeline/stage_b_evidence.py` can carry the `rewrite_meta` disclosure key, which changes the normalized report body and therefore the anchor comparison — a false FAIL caused by configuration, not by code. This is an operational precondition of the gate, not an optional flag.

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
| Override hook (rung 0) | `EYEKB_G4_PY=<python path>`; the caller asserts equivalence, so a mismatch under it is a FAIL; a non-default interpreter prints a `[g4] note:` line |
| Search roots for rung 2 | `EYEKB_G4_PY_SEARCH=<dir>[:<dir>…]` (each `<dir>/bin/python` and `<dir>/*/bin/python` is tried) |
| Resolution order (2026-10-21) | rung 0 override → rung 1 the pinned path when it exists here → rung 2 the pinned path's environment family + `EYEKB_G4_PY_SEARCH` → rung 3 `python3` / `python` on `PATH`; rungs 2–3 are probed against a declared dependency floor and the first that clears it is used |
| Contract-equivalence | the pinned interpreter, an explicit override, or any candidate whose versions equal the recorded contract set (`scanpy 1.11.5 / anndata 0.11.4 / numpy 2.2.6 / scipy 1.15.3 / scikit-learn 1.7.2`); only those can turn a byte difference into a verdict |
| Interpreter unavailable, or a substitute cannot be compared | `rc=3` + `ENV ERROR` / `NOT JUDGEABLE` (with the search trace and the remedy): **no verdict about the repository is issued** |
| Byte mismatch under a contract-equivalent interpreter | `rc=1` + `G4 FAIL` (`got`/`expected` printed per artifact) |
| Gate setup problems (usage error, missing fixture) | `rc=2` |
| The gate script itself | stdlib only, launchable by any `python3` (3.10+) |
| Every run | prints `[g4] interpreter: <path> (python X.Y, source: …)` (the interpreter/source line — literal output of tests/verify_pipeline.py), as a required attachment of any discrepancy report |

Exit status therefore separates three states that used to share one code: `0` = the anchors were
reproduced, `1` = the repository produced different bytes under the contract stack, `3` = this
machine cannot run the gate (no interpreter clears the declared floor, or the interpreter found is
not comparable with the anchors) so there is nothing to conclude. A reader of a clone can tell "your
machine cannot run this gate" from "this repository is broken".

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
3. `rc=3` / `NOT JUDGEABLE` → the machine could not run the gate: the interpreter selected does not
   match the contract versions, or no candidate cleared the declared floor. The printed search trace
   says which candidates were tried and why each was rejected. Prepare an equivalent environment per
   G4.1 and rerun (this is an environment state; it is not a finding about the repository);
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
`assets/s0/build_assets.py`). **v2 re-anchor 2026-10-03**: the repository's public language moved to
English (report templates and knowledge-base content now emit English), changing the
`decisions_template.csv` and report bytes by design; the anchor was regenerated under the same
discipline — three runs on the pinned interpreter (production fp32 ×2, Release slim ×1), all three
artifacts byte-identical across runs, written to `tests/G4_EXPECTED.json` programmatically. The
previous (v1, 2026-10-01) anchor set is kept verbatim in `tests/G4_EXPECTED_PRE-ENGMIG.json` and in
git history, and is retired as a criterion.

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

### §5.1 Authority layers after the KB11-A reason-join convergence (card t_0ec42aa8, 2026-10-15)
Three layers, each with a single authority; they must never be collapsed into one value:
- **Content authority** = `kb/literature_db/evidence_meta_v2.4.2_2026-10.jsonl`
  (sha256 `25f225db2e7cd2ac672be0fc1aeb6fe6ff3410e90cf82b3b8aa3529975b92844`), byte-identical on both
  mirror sides.
- **Delivery authority** = this repository copy (`/home/ubuntu/EYEKB_REPO`); the English delivery
  face is rendered here.
- **Runtime entry** = the D-side service directory (`/mnt/D/EyeKB/mcp_server`), unchanged by the
  convergence.
Mirror direction is therefore layer-specific: content layer D → repo (merge + English rendering);
delivery layer repo → D (the existing one-way ratchet is unchanged).
Engine version for this convergence: `KB1v2-0.14-kb11a-reasonjoin` — the README version note and this
section are updated in the same commit, as required by the rule above.
The reason-tag join table reads the content-authority file and renders a sanitised projection on the
delivery face rather than machine-translating it; the criterion is CJK count on the external output
path = 0 (readings in `plans/mirror_convergence_exec_t_0ec42aa8_20261015/`).

### §5.2 Boundary discipline for self-declared write / commit / push limits (card t_0ec42aa8, 2026-10-15; adopted from `t_cefc8e5a` §4, ruling P-B1)
1. **Who may commit another card's uncommitted work.** A card that declares "write only, no commit /
   no push" — its artefacts may be committed only by that card itself or by a close-out card named by
   the PI. Other cards may reference the paths but must not `git add` them.
2. **Carrying work from outside the committing card's own surface must name the source card.** Any
   commit that includes such uncommitted files must declare the source card per file in the commit
   body, in the form `carried-from: t_xxxxxxxx (<path>[, ...])`. A file-level note such as
   "untracked runtime dependency" without a card id counts as smuggling and is registered by the
   reviewing card.
3. **A self-declared rollback clause must be re-checked before the commit.** If a card carries a
   clause of the form "X degrades => roll back", that clause must be re-checked and the readout
   recorded *before* committing; committing closes the rollback window. If the clause no longer
   holds, do not commit — roll back and redo. (Forward-looking only; no retroactive application, per
   ruling P-B2.)
4. **No large mixed batches.** Files carried across cards must not be bundled into the same commit as
   a large batch of unrelated files: a mixed batch makes the carrying relation unrecoverable after the
   fact. Commit carried files separately, or give a file -> source card list in the commit body.
5. **`no push` / `Local commit only` must have a release mechanism.** Pushing such a commit requires
   authorisation by a later card that names that commit (or a direct PI instruction), and that card
   must record which no-push declaration it releases. A declaration that says "not pushed" without
   saying when or by whom it may be released is equivalent to having no boundary at all (measured
   case: commit `e6bdec1`, 2026-10-13, whose own `no push` line is now an ancestor of `origin/main`).
Records for rules 1-5: `docs/GIT_SELF_DECLARED_BOUNDARY_LEDGER.tsv`. Violations are registered, not
retroactively reverted (same scope wording as `t_cefc8e5a` §5).

### §5.3 REPO_EN_MIG3 close-out batch (card t_55884641, 2026-10-15)
The English-migration wave `REPO_EN_MIG3` (2026-10-14) had no board carrier; it was backfilled by card
`t_55884641` per ruling `t_cefc8e5a` P-7b and is closed out as one batch:
- **Data plane aligned** to the language of the migrated gate files: the ownership-ledger header
  (`docs/W3_PIPELINE_REGISTRY.tsv`), the snapshot drift-ledger header
  (`tests/fixtures/g5/snapshot_drift_ledger.tsv`) and the G6 instance/template `Q3` cells (an English
  rollback term, rule R5). Two defects that the language mismatch had masked are fixed in the same
  batch: the `L6-13` drift dispensation was re-probed (the pointed-at freeze file was rewritten
  upstream at 2026-10-15 03:51:09) and the G5/G6 registered shas in `docs/GATE_INVENTORY_G5G6.tsv`
  were re-taken from the live files.
- **Gate readouts**: `bash tests/run_gates.sh` with `EYEKB_GATE_OUT` pointed outside the repository,
  three runs; G5 (8/8) and G6 (19/19) PASS in each; readouts under
  `plans/repo_en_mig3_close_t_55884641_20261015/logs/`.
- **Commit scope**: the seven carried in-flight files (`.gitignore`, `tests/gate_registry.py`,
  `tests/gate_change_control.py`, `tests/gate_g5g6_negative.py`, `tests/run_gates.sh` and the two
  `.gate_out` de-trackings) plus the data-plane files above plus this note, as a single commit, with
  `carried-from:` naming the source of each carried file in the commit body (§5.2 rule 2) and a
  `no push` declaration carrying its release mechanism (§5.2 rule 5). Every item is a `+`-line
  append or a content-equivalent deletion: `git checkout -- <path>` plus
  `git restore --staged .gate_out/` restores the previous published state.
- **Declared subset**: the wave's own run log ends `ALLDONE mapped=1257 failed=24` over 1,593
  extracted units (five 40-unit batches completed with `ok=0`), so 312 units are in neither bucket;
  this batch takes a declared subset of the wave, not the whole translation, and the remaining
  Chinese *values* in the ledger/instance/inventory are registered as unresolved in
  `plans/repo_en_mig3_close_t_55884641_20261015/LINE_STATUS_REPO_EN_MIG3_t_55884641.md`.

### §5.4 The Cell Ontology explanation layer (card t_ad7463d9, 2026-10-22)

A read-only ontology explanation layer was added to the service and is **registered OFF by default**.
It is a new capability, not a change to an existing one, and §5.4 records what that means for this
contract:

- **Registered, not activated.** `kb/ontology/ONT_LAYER_REGISTRY_v1.json` declares the capability
  (`ont_explain_layer`), its four functions, its logical anchors, an **empty whitelist** and the
  route variable `EYEKB_ONT_LAYER`. With the route unset the ontology module is not imported and no
  ontology tool is advertised, so the advertised tool list and every answer of every other tool are
  byte-identical to the previous release. There is no default-ON behaviour change, so no new
  precondition is added to any gate.
- **Two gates were added to the one-click entry** (`tests/run_gates.sh`): **G7**
  (`tests/gate_ontology_layer.py`) and **G8** (`tests/gate_ontlayer_portability.py`), both registered
  in `docs/GATE_INVENTORY_G5G6.tsv`. G7 needs an interpreter that can import the service and follows
  the G3 convention (`EYEKB_G7_PY`, falling back to `EYEKB_G3_PY`); when that interpreter is absent
  G7 reports **ENV_ERROR** naming the missing module, rather than a pass or a catch-all. G8 needs the
  standard library only. Both report `should_run` / `did_run` / `pass` / `fail` / `not_run` and end in
  exactly one of PASS / FAIL / ENV_ERROR; neither passes while a mandatory check did not execute.
- **The corpus precondition of G3 is unchanged** and still applies to the whole chain: G3's anchors
  are dense-retrieval results, so the chain is run where the corpus named by §G2 is available
  (`EYEKB_CORPUS`, default `literature_db/v2.4.2_2026-09_slim`); a missing corpus is INCONCLUSIVE
  (rc=3), not a failure. The corpus is not part of the git tree.
- **Release identity is now reported in four layers** (`protocol_generation`, `service_build_id`,
  `knowledge_bundle_id`, `effective_profile_id`) plus the `release_id` bound to the immutable
  manifest `docs/RELEASE_MANIFEST_v1.json`. `scripts/release_identity.py --check` verifies the record,
  the manifest and their binding; `get_release_identity` reports the same layers. `get_release_identity`
  is the explicit identity interface, so its payload is where the new layers appear — that call's
  response moves by design, and it is the **only** call of the recorded request set that moves.
- **Assets addressed logically.** The ontology snapshot ships inside the repository
  (`kb/ontology/cl/releases/2026-06-08/cl-base.obo`, 3,757,082 bytes, sha256 `c6274fb65cdf740b…`)
  and is reached only through a logical address resolved by
  `kb/ontology/ONTOLOGY_SNAPSHOT_MANIFEST_v1.json` with content-hash verification. No new service
  code carries an author-machine absolute path; G8 checks that mechanically, in a copy of the assets
  at a different path whose directory name contains spaces.
- **Failure policy.** A missing shipped asset, an altered snapshot or an address the manifest does
  not list are delivery defects and **FAIL**; `ENV_ERROR` is reserved for a declared external
  precondition. The policy is declared in the registry and exercised by G8, which builds a shadow
  copy with the snapshot absent, then altered, and resolves an unlisted address.

### §5.5 The optic-nerve fibroblast carrier on the default route (activation card t_42df17c2, 2026-10-22)

The carrier library `onfibro_v13` was merged into the default route by a **PI-signed activation**
(the project owner's verbatim authority: "载体并进默认路由"). It is a **default-ON behaviour
change**, so this contract registers the precondition that follows from it:

- **Switch and OFF identity.** `EYEKB_ACT_ONFIBRO` — unset, empty or any value other than
  `{0,false,off,no}` means the optic-nerve fibroblast carrier is part of the default `all` route;
  `EYEKB_ACT_ONFIBRO=0` restores the pre-flip default **byte-for-byte**, measured by replaying the
  recorded query set at the same absolute path: 721/721 recorded cluster windows and 229/229 battery
  calls identical in raw and canonical response bytes, with the parent commit's core swapped in place
  as the reference (docs/plans/activate_onfibro_20261022/out/DEFAULT_FACE.json).
- **What the gates inherit.** Every criterion that is stated as a *byte identity of a default-route
  response* now depends on that switch. The 721/740/906-request default-face baselines and the
  recorded legacy tool-panel digests were taken with the pre-flip default, so a replay at this
  release is not byte-identical on the surface the carrier touches: the ranking moves on 45 of the
  721 recorded clusters, and **every** response that carries the provenance/soft-flag disclosure
  fields now names the carrier's file and entries (out/FIELD_DIFF.json gives the per-path diff).
- **Legacy tool-panel compatibility item (reported, not absorbed).** The legacy five-tool panel
  digest moved (`e8e6c26351cd9a1d42fa2e7cb6a83f23` -> `47e42230a8f7256b4ae9a78d4ff628d3`, and the
  full panel with it) on exactly two `query_marker` calls — `{"cell_type": "MG"}` and the microglia
  gene panel — **whose rankings are unchanged**; they moved because they carry the disclosure fields.
  The baseline fixture `tests/fixtures/tool_panel_baseline.json` was deliberately **not**
  re-recorded, so `tests/probe_tool_panel_identity.py --baseline tests/fixtures/tool_panel_baseline.json`
  is RED at this release by design, on the record, and the decision to re-record the baseline with
  attribution or to narrow the disclosure for libraries that contribute no candidate is pending the
  owner's ruling. No gate of the one-click chain (G3..G8) invokes that probe, so the chain itself is
  unaffected; the item is carried in `docs/CHANGE_CONTROL_G6_INSTANCE.tsv` (row
  `CHG-20261022-ONFIBRO-ACTIVATION`) and in registry rows L1-11M / L1-30 / L6-37.
- **Failure policy.** A replay that compares default-route bytes must state which value of
  `EYEKB_ACT_ONFIBRO` it was taken with; a mismatch under the other value is a configuration
  difference, not a regression. **No criterion of any gate was weakened for this activation**: G4's
  three byte anchors and the retrieval anchors are re-measured in the same commit and reported.
- **Scope.** No other library is activated, no whitelist gains another entry, no exclusion row is
  withdrawn, and no score, admission floor or tie-break changes: the carrier is a class carrier.


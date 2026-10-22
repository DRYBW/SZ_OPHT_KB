# L5 — baseline freeze, and the read-only Cell Ontology explanation layer

Card `t_ad7463d9`. Two deliverables: freeze the pre-change baseline of the service, then wire the
depth work that already existed as an analysis asset into the service as a **read-only** interface,
**registered and OFF by default**. Nothing was activated; no shipped panel body or class dictionary
was changed; zero downloads and zero network.

Binding ruling: `plans/sol_design_20261021/SOL_DESIGN_OUT_20261021.md`, block A and the two
engineering rulings (the three-state gate; release identity in four layers bound to an immutable
manifest). Built on
`plans/cl_depth_devlineage_20261021/` (the ontology navigation asset) and
`plans/devlineage_20261021/hygiene_v5_20261022/`, re-derived rather than redone.

- Repository: `/home/ubuntu/EYEKB_REPO` (mirror of the delivery volume). Base commit
  `16c6b28aab8ffda11a4a89d21075ae217e740771`; this card's commit is recorded in
  `ledgers/COMMIT.txt`. **Not pushed.**
- Interpreter used for every service-side reading: `/home/ubuntu/training-venv/bin/python3`
  (python 3.14.4, pydantic 2.12.5, mcp 2.0.0).
- Evidence root for the large artefacts (raw replay dumps): `/mnt/D/EyeKB/plans/l5_ontlayer_20261022/`,
  listed there with hashes. Everything the gates need is committed under this directory.

---

## Part 1 — the baseline freeze

### One command, and a re-run returns the same bytes

```
python3 docs/plans/l5_ontlayer_20261022/scripts/01_baseline_freeze.py \
    --service-python <interpreter> --revision 16c6b28aab8f --out docs/plans/l5_ontlayer_20261022/out
```

Run in a checkout **of that revision** (`git worktree add <dir> 16c6b28`), because a baseline is
frozen in a checkout of the revision it describes: the script refuses to write anything if the
checkout is at a different revision. Output:
`out/BASELINE_FREEZE_16c6b28aab8f.json` (sha256 `0c915fc9e1ff3c4e…`) plus a pointer
`out/BASELINE_FREEZE.json`. Three consecutive runs produced the same sha256, so a re-run really does
return the same hashes.

The file is named after the revision, so freezing another revision cannot overwrite the first.

### What the frozen set contains

| block | content |
|---|---|
| `release_identity` | the identity recorded for that revision: `release_id 3c17853873ca`, digest `3c17853873caccc5…`, 3,718 files, 224,519,351 bytes |
| `code_fingerprint` | 203 files of the declared service surface by sha256, repository-relative, plus a surface digest; declared-but-absent paths are recorded as absent, not dropped (`kb/ontology/`, `literature_db/`, `docs/RELEASE_MANIFEST_v1.json` did not exist at that revision) |
| `default_configuration` | the observed value of ten behaviour switches, each with the meaning of its off state (all unset = the release default) |
| `active_libraries` | interpreter, python 3.14.4, and the versions actually resolved: mcp 2.0.0, pydantic 2.12.5, numpy 2.4.6, pandas 2.3.3, pyarrow 25.0.0, PyYAML 6.0.3, sentence-transformers 6.0.0 |
| `scoring_and_guard_configuration` | the constants that decide scoring, guards and stage routing, read out of the shipped module in that interpreter: `KBGOV_T_FROZEN 0.4`, `KBGOV_AMBIG {CLU, GLUL, VIM}`, `STAGE_TIERS/STAGE_FOLD/STAGE_ACCEPTED_LITERALS/STAGE_UNRECOGNISED_RULE`, `ANTSEG_DEFAULT_LIBS/ANTSEG_MIN_SHARED/ANTSEG_MARGIN`, the resolved default corpus directory |
| `recorded_request_set` | all 55 calls of the recorded request set (the 12-call tool panel + a 42-call development-stage sweep + one identity call), each as md5 + normalised md5 + byte count, with the advertised tool list and the refused-call list |
| `panel_identity` | the live reading of the repository's own panel probe, with the recorded baseline it is compared against |

Two determinism traps were found and fixed while building this, and both are worth recording:

1. **A set's iteration order is not a fingerprint.** The guard configuration includes frozensets;
   `str(frozenset(...))` orders them by hash seed, so the first two runs of the freeze produced
   *different* sha256 over identical bytes. Every container is now rendered as a sorted, typed
   record, and the run is byte-reproducible.
2. **Raw response digests are path-bound.** 27 of the 55 answers echo the install path, so raw
   digests are comparable only between runs at the same absolute path — which is why the
   byte-identity comparison of this card was taken at one path, and why the freeze records a
   path-normalised digest as well and states the baseline in that one.

### The 5-of-12 panel mismatch, settled explicitly

The recorded tool panel did not reproduce at HEAD (5 of 12 calls differed). Settlement
(`out/PANEL_SETTLEMENT.json`, sha256 `0ec42ee8dfb4401d…`), with both readings kept:

| | legacy_panel | full_panel | n_calls |
|---|---|---|---|
| **pre-image** (`git show 435bb92^:tests/fixtures/tool_panel_baseline.json`) | `4813fca2f5c8c916a233f4825b200b19` | `097328b42ffdb736b6934fa1967ada37` | 12 |
| **current** (the fixture at HEAD) | `e8e6c26351cd9a1d42fa2e7cb6a83f23` | `3f1f52cb62915f5ad2801962aa523d36` | 12 |
| **live reading here** (`tests/probe_tool_panel_identity.py --baseline …`) | `e8e6c26351cd9a1d42fa2e7cb6a83f23` | `3f1f52cb62915f5ad2801962aa523d36` | IDENTITY PASS (rc=0) |

**Verdict: a stale fixture, and it was already settled by another card before this baseline was
frozen.** The card that owns it re-recorded it in commit `435bb92`; the cause, per that card's own
call-by-call attribution, is that four of the twelve calls were refused on arguments the tool never
accepted (the panel spelled `get_kb_page`'s argument `kind` where the documented signature is
`scope`, passed a boolean for a `detail` that is a string, and omitted the required `cell_type` — and
a refusal is produced by the argument-validation layer, embedding the validator's own version string,
so it cannot be an anchor at all), while one call had genuinely moved before this card started
(`explain_annotation` for the Cell Ontology label). The re-recording used the documented signatures,
recorded no refusals, and added an interpreter-provenance block.

This card's handling: the pre-image was read out of git, the probe was re-run here, and both readings
were recorded. **The fixture was not overwritten and neither version was edited** — it belongs to the
card that owns it, and repairing another card's fixture would have been a silent cross-card write.
The delivered fixture reproduces at this HEAD, which is what allowed the baseline to be declared
frozen.

### Default behaviour, proven by raw bytes at the same absolute path

The recorded request set was replayed twice in the **same** checkout (`/home/ubuntu/EYEKB_REPO`): once
with the working tree at the baseline (taken by stashing this card's work, with a backup of the
change kept outside the repository and the working tree verified back at HEAD before the dump), and
once with the change in place.

```
python3 docs/plans/l5_ontlayer_20261022/scripts/03_replay_request_set.py --take  PRE.json
python3 docs/plans/l5_ontlayer_20261022/scripts/03_replay_request_set.py --take  POST.json
python3 docs/plans/l5_ontlayer_20261022/scripts/03_replay_request_set.py --compare PRE.json POST.json
```

| reading | value |
|---|---|
| calls compared (raw response bytes) | 55 |
| **differing** | **1** — `get_release_identity`, the explicit identity interface |
| tool list | unchanged (seven tools; no ontology tool) |
| refused calls | 0 before / 0 after |

The single moved call is the deliverable of the second engineering ruling, and the ruling says the new
layers are returned *through the explicit identity interface*, not appended to the answers of the
other tools. Every one of the other 54 calls is byte-identical. `out/REPLAY_COMPARISON.json`; the
per-call digest files `PRE_REPLAY_HASHES.tsv` / `POST_REPLAY_HASHES.tsv` are committed, and G7-C07
re-reads them on every chain run so the claim cannot rot silently.

Cross-checks worth naming:

- normalising the checkout path away, the **baseline freeze taken in a different checkout
  (a git worktree) reproduces the same 55 digests** as the same-path PRE dump — 55/55;
- the normalised digest of the panel's `query_marker{RPE, retina}` call equals the digest recorded in
  `tests/fixtures/tool_panel_baseline.json` (`46ff880c2551ce49241f24f9f1123a3d`), so the replay set and
  the panel fixture are talking about the same service;
- the legacy panel (`e8e6c263…` / `3f1f52cb…`) is identical before and after this change.

---

## Part 2 — the read-only Cell Ontology explanation layer

### What was built

| file | what it is |
|---|---|
| `mcp_server/ontology_layer.py` | the layer: parser, ancestor closure, the four functions, the anchor resolver. Stdlib only; contains **no write call at all** |
| `kb/ontology/cl/releases/2026-06-08/cl-base.obo` | the fixed snapshot, shipped (3,757,082 bytes, sha256 `c6274fb65cdf740b…`), byte-identical to the copy the earlier ontology card recorded |
| `kb/ontology/ONTOLOGY_SNAPSHOT_MANIFEST_v1.json` | logical address → repo-relative path → sha256, with the release string and the parser version |
| `kb/ontology/ONT_LAYER_REGISTRY_v1.json` | the registration: registered, read-only, **OFF**, **empty whitelist**, route `EYEKB_ONT_LAYER`, the failure policy, the granularity rule, the stop line |
| `docs/ONTOLOGY_LAYER_CONTRACT_v1.md` | the reader-facing contract |
| `tests/gate_ontology_layer.py`, `tests/gate_ontlayer_portability.py` | G7 and G8, now part of `tests/run_gates.sh` |

### The fixed snapshot, re-derived

Read with this layer's own parser (not quoted from the earlier card):

| reading | value |
|---|---|
| CL terms in the file / active / obsolete | 3,531 / 3,335 / 196 |
| `is_a` edges, CL→CL | 4,664 |
| `is_a` edges pointing outside the file (missing imports) | 216 |
| multiple inheritance (active terms with >1 parent) | 1,295 |
| `alt_id` declarations | 76 |
| obsolete terms with exactly one `replaced_by` | 122 (0 with more than one; 13 `consider`-only) |
| OWL restriction / equivalence expressions (`intersection_of`) | 5,023 — recorded separately, **never** read as `is_a` edges |
| ambiguous exact synonyms | 1 (`mo.6c+ii` → CL:0002469, CL:0002470) |
| same label on more than one concept | 0 |
| `is_a` cycles | 0 |
| blanket ancestors (≥200 active CL descendants, threshold declared in the registry) | 27 |

The shipped snapshot was checked against the integrated release the earlier card used: the CL→CL
`is_a` edge sets are the same 4,664 edges, so the CL-to-CL closure is the same, and the integrated
release carries no CL-to-CL edge the shipped file does not. That provenance and equivalence are
re-derived here and recorded in the manifest; only the 3.7 MB file ships, not the 17.3 MB one.

### The five buckets reproduce the earlier reading exactly

Over the frozen 721-cluster pair list (1,495,330 cells; committed as
`out/GRANULARITY_PAIRS_721.tsv`, itself a reading of a comparison the project had already run and
exposed — regression and leak-detection material, not a blind validation volume):

| bucket | clusters | cells | pct cells |
|---|---|---|---|
| `same_term` | 212 | 480,120 | 32.108 |
| `ours_broader` | 150 | 342,552 | 22.908 |
| `ours_narrower` | 15 | 36,090 | 2.414 |
| `confirmed_incompatible` | **0** | 0 | 0 |
| `not_supported_by_is_a` | 344 | 636,568 | 42.570 |

`not_supported_by_is_a` = the earlier card's 151 `true_mismatch` + 193 `no_mapping`; the two are kept
apart inside the record by `is_a_relation` (`no_ancestor_relation` vs `unresolved`), which is exactly
what the ruling asks for. `confirmed_incompatible` is 0 because no caller supplied explicit
incompatibility evidence — the graph alone never establishes exclusion, and this run did not pretend
it did. The recomputation agrees with the earlier reading bucket for bucket
(`BUCKET_SUMMARY.json: cross_check_against_the_earlier_reading.identical = true`).

Three tables, no blended figure: `TABLE_1_SAME_TERM.tsv`, `TABLE_2_GRANULARITY.tsv`,
`TABLE_3_TASK_VALIDITY.tsv`, all on the fixed denominator 721, with `counts_as_correct` and
`counts_as_confirmed_error` columns so that a bucket cannot be quietly counted twice. A coarse answer
stays a resolution limitation: **0 of the 150 `ours_broader` rows reach only a blanket ancestor in this
population** (the column is there and reads 0, which is the honest measurement — the rule costs nothing
here), while the rule itself is exercised by the gate's own battery case, where a blanket ancestor
returns `resolution_limited` with `min_report_granularity_met = false`.

### The two records, never collapsed

Every comparison returns `is_a_relation` (what the graph says) next to `assessment` (whether the
answer holds here). They are demonstrably different records, not two names for one: for the same
unrelated pair, `is_a_relation` is `no_ancestor_relation` while the bucket is
`not_supported_by_is_a`, with 7 shared ancestors recorded and an `unresolved_reason` saying that
excluding either term would need explicit evidence. Supplying that evidence moves the verdict to
`confirmed_incompatible` **and records the evidence verbatim with it**. G7-C05 checks all of that,
including that the two fields are not the same string.

### Registration and the default surface

- Registry: `registered = true`, `default_state = OFF`, `whitelist = []`, route `EYEKB_ONT_LAYER`.
- With the route unset the server **does not import** the layer and advertises **no** ontology tool
  (measured in a subprocess, not asserted). With `EYEKB_ONT_LAYER=resolve_term,compare_terms` exactly
  those two appear (7 → 9 tools).
- The tool list and every other answer are byte-identical (Part 1); the legacy panel digests are
  unchanged.

### Anchors, portability and the failure policy

Anchors are logical addresses resolved through the versioned manifest with content-hash verification:
`ont://cl/releases/2026-06-08`, `repo://kb/ontology/ONT_LAYER_REGISTRY_v1.json`,
`repo://kb/markers/markers_cl_alignment_v2_unified.json`. No new service code carries an
author-machine absolute path (checked mechanically over eight files and both ontology records).

G8 runs in **three environments** — the author tree, a temporary working directory, and a copy of the
assets at a different path whose directory name contains spaces — and each resolves the same anchors
and returns the same battery. It then builds shadow copies to exercise the failure policy:

| state | what is done to the shadow | status reported | verdict |
|---|---|---|---|
| missing snapshot | the file is deleted | `ANCHOR_MISSING` | FAIL (delivery defect) |
| altered snapshot | the file is truncated | `ANCHOR_HASH_MISMATCH` | FAIL |
| unlisted address | an address the manifest does not list is resolved | `ANCHOR_UNKNOWN` | FAIL |
| — | — | `ENV_ERROR` | reserved for a declared external precondition |

In none of the failure states is an answer produced from an unverified snapshot, and the layer never
falls back to a placeholder. A full battery leaves `kb/ontology/` and the class-mapping source byte
identical, and the module contains no write, execute or network primitive (checked at token level).

### The gate chain, and the three-state report

| gate | checks | should-run | did-run | pass | fail | not-run | verdict |
|---|---|---|---|---|---|---|---|
| G7 `tests/gate_ontology_layer.py` | 9 | 9 | 9 | 9 | 0 | 0 | **PASS** |
| G8 `tests/gate_ontlayer_portability.py` | 6 | 6 | 6 | 6 | 0 | 0 | **PASS** |

Both report the five counts and end in exactly one of PASS / FAIL / ENV_ERROR; a gate does not pass
while a mandatory check did not execute. G7 needs an interpreter that can import the service and
follows the G3 convention (`EYEKB_G7_PY`, falling back to `EYEKB_G3_PY`); with an interpreter that
lacks the MCP SDK it reports **ENV_ERROR naming the missing module** — the one case where ENV_ERROR
is used, and it happened during development, which is how that branch is known to work. There is no
default-ON behaviour change in this card, so no new precondition is added to any existing gate. G7's
unit battery is explicitly labelled **synthetic**: it exercises code paths the real snapshot does not
exhibit (an obsolete term with two replacements, a duplicate label, a planted cycle) and is not
evidence about the snapshot.

### Release identity in four layers

`scripts/release_identity.py` now reports `protocol_generation`, `service_build_id`,
`knowledge_bundle_id` and `effective_profile_id`, plus the `release_id` bound to
`docs/RELEASE_MANIFEST_v1.json` (every tracked file with its blob id and size; the manifest and the
identity record are excluded from their own coverage, because a record cannot contain its own hash).
`--check` verifies the record, the manifest and their binding item by item, and the layer values
themselves are part of the check, so a change in the service code, the knowledge bundle or the
effective configuration is visible without comparing commits by hand. `get_release_identity` reports
the same four layers and also states, explicitly, that the ontology capability is registered with an
empty whitelist — evidence that it is not in the effective profile.

At the time of writing: `release_id 7444260ca8c6` (index tree, before the commit),
`service_build_id d3db54fbbb23`, `knowledge_bundle_id 6a9ef55b10bc`, `effective_profile_id 188cf79b388f`;
the committed values are in `docs/RELEASE_IDENTITY.json` and are re-taken in the same commit.

---

### The gate chain in a clean clone

The chain was run a second time in a **clean clone**, at a path whose name contains spaces, with the
author tree not reachable from the working directory:

```
bash docs/plans/l5_ontlayer_20261022/scripts/09_clean_clone_chain.sh \
     /home/ubuntu/EYEKB_REPO "/home/ubuntu/l5 clean clone" \
     /home/ubuntu/EYEKB_REPO/literature_db/v2.4.2_2026-09_slim \
     /home/ubuntu/.conda/envs/pipeline_env/bin/python
```

The clone is a fresh `git clone` of this card's commit (worktree clean), and the literature corpus is
copied into it at the documented path because the corpus is a Release asset, not a repository file
(§G2); copying a local directory is not a download. Results are recorded in `ledgers/` and quoted in
`ledgers/COMMIT.txt`. G7 and G8 pass in the clone with the same readings as in the author tree, which
is the point of the portability gate: 3 anchors resolved, the same battery, the same fail-closed
statuses, in three environments.

### A concurrent writer in the same working tree (external, recorded)

While this card was running, another card (`t_0c40c7b1`, the optic-nerve fibroblast registration)
edited `mcp_server/eyekb_core.py` **in the same working tree** at 11:04:31 and had not committed it.
Two consequences, both handled and both visible:

1. **The ledger must describe committed bytes.** The ownership ledger had been re-taken by that card
   with the sha of its uncommitted file, and its new row pointed at a file it had not committed. This
   card staged the ledger (its own rows had to be re-taken) and therefore committed those rows as
   well — which made a clone internally inconsistent (registry says one sha, the committed file is
   another; one row's file does not exist yet). Repaired here: `L1-11M` is restored to the sha of the
   **committed** blob (`d46953bda7da5a43`, 111,637 bytes), that card's not-yet-committed row was
   dropped, and the dangling reference it left in the `L1-11M` note was neutralised. The pre-image of
   the ledger as this card found it is kept at
   `out/REGISTRY_PREIMAGE_l5_edit.tsv`, and a comment was left on that card. **That card re-adds its
   row in its own commit**; nothing of its work was deleted from disk (its source file and directory
   are untouched and left unstaged).
2. **The author-tree chain shows one failure for that reason only.** `G5-C05` reports
   `L1-11M: registered=d46953bda7da5a43 live=3dadbbbaf2631da0` — the registered value is the
   committed blob, the live value is the other card's uncommitted edit. It is not this card's change,
   it is not present in a clone of this commit, and it disappears when that card commits. The
   authoritative reading for this card is therefore the clean-clone chain.

This is exactly the hazard the operator notes describe for two cards in one checkout, and the reason
this card's own files were committed with an explicit path list rather than `git add -A`: the other
card's `mcp_server/eyekb_core.py` and its two untracked paths were left exactly as they were.

### What could not be closed

- The recorded request set is replayed only where the corpus named by §G2 is available; on a machine
  without it, the two `search_literature` calls answer from whatever corpus resolves, so the byte
  identity of those two calls is a statement about this machine. The other 53 calls do not depend on
  the corpus.
- The freeze's per-call digests are stated in their path-normalised form for that reason; the raw
  digests are the same-path evidence and are kept as such.
- G7's synthetic unit battery exercises code paths the real snapshot does not exhibit. It is labelled
  synthetic everywhere it appears, and no reading in this report is taken from it.

### What this does not claim

- **Ontology agreement rising is not recognition rising.** This layer corrects how a comparison is
  worded and how far an answer may be used; it is an evaluation and explanation asset, not an
  identification gain, and it is reported as such. `same_term` is 32.1% of the recorded clusters by
  cells — that is a statement about wording and granularity, not about the ability to identify cells.
- **The 721-cluster population is not a blind test.** It is a comparison the project had already run
  and already exposed, carried here as a frozen pair list; the ruling requires exactly that honesty.
- **A coarse answer is not automatically right and not automatically wrong.** `ours_broader` is a
  resolution limitation; the extra resolution of an `ours_narrower` answer earns nothing; and an
  answer that only reaches a blanket ancestor is not usable.
- **The snapshot is a snapshot.** 216 parents point outside the shipped file (missing imports) and
  are counted, not repaired. A relation the snapshot does not carry is reported as unknown.
- **Nothing was activated**, no shipped class dictionary or panel body was touched, no evaluation
  volume was edited, and the single response that moved is the identity interface, stated above.

## Reproduce

```
# baseline freeze (in a checkout of the baseline revision)
git worktree add /tmp/l5_base 16c6b28aab8ffda11a4a89d21075ae217e740771
python3 <worktree>/docs/plans/l5_ontlayer_20261022/scripts/01_baseline_freeze.py \
    --service-python <interpreter> --revision 16c6b28aab8f --out <this directory>/out
python3 docs/plans/l5_ontlayer_20261022/scripts/06_panel_settlement.py       # the panel settlement
python3 docs/plans/l5_ontlayer_20261022/scripts/02_build_tables.py          # the three tables
python3 kb/ontology/scripts/build_ont_manifest.py                           # verify the anchors
python3 mcp_server/ontology_layer.py                                        # the snapshot summary
python3 scripts/release_identity.py --check                                 # four layers + manifest
python3 tests/gate_ontology_layer.py --service-python <interpreter>
python3 tests/gate_ontlayer_portability.py
bash tests/run_gates.sh                                                     # G3..G8
```

`out/` also holds: `BASELINE_FREEZE*.json/.sha256`, `PANEL_SETTLEMENT.json/.sha256`,
`GRANULARITY_PAIRS_721.tsv`, `FOURWAY_721_v2.tsv`, the three tables, `BUCKET_SUMMARY.json`,
`PRE_REPLAY_HASHES.tsv`, `POST_REPLAY_HASHES.tsv`, `PRE_TOOLS.txt`, `POST_TOOLS.txt`,
`REPLAY_COMPARISON.json`.
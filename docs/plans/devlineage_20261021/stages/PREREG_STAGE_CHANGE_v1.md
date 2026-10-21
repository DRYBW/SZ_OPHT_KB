# PREREG — V3 stage axis: stage-resolved markers, recognition probe, change legitimacy (frozen before any probe)

Card: `t_aa1b7f12` (V3-developmental lineage: stage-resolved markers and whether marker change is
recognisable). Written and frozen **before** the recognition probe was executed, so that every
verdict and every rejection is a reading of a criterion, not a rationalisation of a result.

Binding inputs (read, not modified):
- `plans/devlineage_20261021/DATA_CONTRACT_devlineage_v1.md` (frozen 2026-10-21, binding)
- `plans/devlineage_20261021/BRIEF_V3_STAGE_AXIS_AND_CHANGE_20261021.md`

Owned output directory: `docs/plans/devlineage_20261021/stages/` inside the shipped repository
(`/home/ubuntu/EYEKB_REPO`), mirrored to `/mnt/D/EyeKB/plans/devlineage_20261021/stages/` (the path
the card names on the data side). Nothing under `kb/`, no frozen artefact and no default response
is touched.

## §0 Which copy is "the shipped service" — decided before probing

Two copies of the kernel exist on this machine:

| copy | path | sha256(eyekb_core.py) | sha256(server.py) |
|---|---|---|---|
| repository (shipped, committed, carries the release identity) | `/home/ubuntu/EYEKB_REPO/mcp_server/` | `5068a4a27b645d4ca16bc6c90ba6fb8bed8b02761fd056f5e7ec7de64d9063be` | `d127854bfeb08a65fcc3f513b006576cc17a7cb34e871e86cd7d1b8915bdf855` |
| data-mount working copy | `/mnt/D/EyeKB/mcp_server/` | `feff1e12fd8109c4de7ca1764ef596f4bcedc590d0780ff402c253bfad8e638a` | `9341ed7aec6f3f9174f96423e0b101f5017cb844a5cdbb54e1f7dd99859f1fc7` |

The repository copy is **the shipped service**: it is the one that is committed, that
`docs/RELEASE_IDENTITY.json` takes the identity of, and it is a strict superset of the data-mount
copy (it additionally carries `get_kb_page(summary=...)`, `library=lensiris_v11`,
`library=holefill_v12`). The deliverable has to be committable, so the repository copy is primary.
The probe is run against **both** faces and any divergence between them is reported as a finding —
a reader must never have to guess which bytes answered.

## §1 Stage vocabulary and its mapping (fixed here, applied everywhere)

The contract fixes the four-level literal for the `stage` field: `{fetal, adult, developing, unknown}`.
The upstream assets use other literal sets; the mapping below is total, documented, and the
**source literal is always kept in its own column** so nothing is silently translated:

| source | source literal | contract `stage` | rule |
|---|---|---|---|
| dev panel `markers_v9_dev_retina.json#organism_stage` | `fetal/developing` | `fetal` for the `*_precursor` / `RPC_*` / `NRPC_*` / `TAC_*` entries (panel window 9–24w post-fertilisation) | `fetal` |
| baseline index `stage_axis` | `fetal` | `fetal` | identity |
| baseline index `stage_axis` | `adult` | `adult` | identity |
| baseline index `stage_axis` | `developing` (newborn/infant/postnatal, <18y) | `developing` | identity |
| baseline index `stage_axis` | `unknown` | `unknown` | identity |
| KB3 development entry `development_stage` | `fetal_developing` | `fetal` | the KB3 bucket is a fetal+gestational bucket whose anchors are 11w2d–23w4d post-fertilisation |
| KB3 development entry `development_stage` | `postnatal_neonatal` | `developing` | matches the shipped service's own `postnatal`→`developing` mapping (`_fetal_concept_response` call site) |
| KB3 `excluded_layers` | `organoid_Day*` | `unknown` | KB2c ruling Q1: organoid is not fetal tissue and not adult |
| PRECURSOR_EDGES `*_stage` column | `developing` / `adult_or_unspecified` | **not mapped** | this column is a **derived keyword rule**, not a native ontology attribute; it is never promoted into the contract's `stage` field (see §4, R2) |

No stage is ever silently assigned to `adult`. A row whose stage cannot be established is written
`unknown` with a disclosure row.

## §2 The recognition probe — inputs, and what counts as recognition

The shipped marker surface (`query_marker`) takes genes and returns ranked candidates. It has **no
stage argument**. Recognition is therefore measured, not asserted:

- **Input the caller would actually supply.** For a fetal-state cluster: the top-K genes of that
  lineage's stage-resolved fetal assertion set. For the corresponding adult-state cluster: the
  top-K genes of the same lineage's stage-resolved adult assertion set. Gene order within a set is
  the order the source asserts them in; `K ∈ {10, 25}` is frozen here (10 = a typical caller's
  differential-expression shortlist; 25 = the widest window the corpus can supply).
  Where a set has fewer than K genes, all of them are used and the shortfall is recorded — an
  under-full window is itself a measurement.
- **The service is run twice per input** — once on the default route (`library="all"`, i.e. what a
  caller gets with no extra knowledge) and once on the explicit developmental route
  (`library="retina_dev"`), which a caller can only use if it has already decided the stage.
- The composition surface (`get_tissue_composition`) is probed once per stage literal, because it is
  the only shipped tool that accepts a stage at all.

**Verdict rules (each lineage gets exactly one; evaluated top-down, first match wins):**

1. `no_candidate_either_way` — the default route returns an empty ranking for **both** the fetal and
   the adult input.
2. `observable_now` — on the **default route**, the fetal response and the adult response are not
   identical in their ranking body, and the difference is a stage signal produced by shipped code:
   the `off_domain` advisory (`possible_dev_fetal_content`) is present for the fetal input and
   absent for the adult input, **or** a developmental entry appears in the fetal ranking.
3. `needs_wider_query_window` — rule 2 fails, but the developmental signal is present and merely
   below the shipped advisory criterion: `dev_best ≥ 1` on the fetal input (either route), while the
   advisory did not fire. The K=10/K=25 pair is what makes this measurable: if the signal appears at
   K=25 but not at K=10, the verdict is this one, not "unobservable".
4. `needs_information_this_interface_cannot_observe` — none of the above: the discriminating genes
   are absent from every library the route loads and no stage channel exists on this surface, so no
   wider window can help. A lineage with an empty fetal assertion set also lands here, with reason
   `no_assertion_in_corpus` recorded in the boundary register.

Secondary, always recorded (never a verdict of its own): whether the fetal input's top-1 on the
default route is the lineage's own adult class — i.e. a silent adult assignment. That is disclosed
per lineage and counted in the gate.

## §3 Change legitimacy — the rules the check enforces

A change is admitted only as a per-edge, per-stage assertion carrying an evidence anchor and a
grade, asserted by **one source that observed both stages under one species, one assay and one
condition**. The check rejects a candidate when any rule fails:

| rule | rejects when |
|---|---|
| R1 anchor | the row carries no `evidence_anchor` or the anchor does not resolve to a file present on disk |
| R2 stage provenance | the stage value comes from the derived keyword column of `PRECURSOR_EDGES.tsv` rather than from a source that observed the stage |
| R3 single source | the two sides of the change come from two different studies/sources (a snapshot differ) |
| R4 species | the two sides are from different species |
| R5 assay | the two sides are from different assays (RNA vs protein, or two platforms) |
| R6 condition | the two sides are from different conditions/diseases/experimental systems |
| R7 step count | the direction would be propagated along a lineage of more than one step |
| R8 identity-free | the change has no start/end identity or no time direction that the source itself asserts |
| R9 grade | the row's `evidence_grade` is outside the contract's four values, or missing |
| R10 off-semantics | the change is `off` while the source only fails to mention the gene ("not mentioned" is not `off`) |
| R11 numeric | a numeric `effect_value` is present without a traceable extraction record |

Candidate changes are generated from the tempting, locally available materials (within-lineage
cross-source snapshot differ; cross-entry composition-percentage differ; multi-step propagation along
`PRECURSOR_EDGES`; and a cross-species family if and only if a non-human marker source is actually
present locally). Rules with no real candidate generated are exercised by explicitly labelled
`fixture=Y` rows, reported in a **separate** count and never mixed into the real rejection ledger.

The admitted set is reported as-is. Zero admitted rows is a legitimate, reportable outcome and is
strictly better than a speculative paragraph (contract, marker-assertion rules).

## §4 Honesty notes that must be repeated wherever the artefacts are relied on

- The `*_stage` columns of `plans/devline_ont_20261002/out/PRECURSOR_EDGES.tsv` are a **derived
  keyword rule**, not a native ontology attribute.
- The developmental entries are built from published labels and literature, not from a model we
  trained; a gene that the build filtered out as a mature marker was **not** observed to be off in
  fetal tissue. That contrast is registered as a pending assertion, not as a change.
- "Not mentioned" is never recorded as `off`.
- No marker direction is propagated along a multi-step lineage.

## §5 Red-line compliance decisions taken up front

- **No derivation from the evaluation volumes' own queries.** The established replay harness
  (`plans/holefill_v12_20261021/golden_721.py`) replays 721 recorded queries taken from the 28-volume
  evaluation reports. It is **not used here**, because the brief forbids deriving anything from the
  evaluation volumes' own queries and the conservative reading of that sentence covers replaying
  them. The byte-identity requirement of the brief is instead discharged by (a) replaying **this
  card's own recorded probe set** twice and comparing hashes, and (b) recording the sha256 of every
  service and knowledge-base file before and after, so a reader can see that no shipped byte moved.
- Zero downloads, zero network. Repository-facing text is English only.
- No trajectory-inference model, no developmental predictor, no trajectory training.
- Every intermediate artefact is kept; nothing is overwritten; no push.

## §6 Gate items (machine-checkable, pass/fail counts in the readout)

G1 every stage literal in the deliverable is in `{fetal, adult, developing, unknown}`
G2 no row is silently assigned to `adult`; every `unknown` is disclosed row-by-row
G3 no assertion mixes two stages in one row
G4 no cross-species stitching in any table
G5 no numeric effect without a traceable extraction record
G6 developmental entries appear in no adult query path
G7 no `off` produced from absence of mention
G8 every admitted change row carries an anchor and a contract grade (0 admitted is PASS)
G9 the recognition probe stores real service output, the exact commands, and reproduces byte-identically on re-run
G10 default behaviour byte-identical: replay difference count == 0
G11 zero network / zero download in this card's own scripts (static scan + run-time evidence)
G12 repository-facing text of this card's deliverables is English only
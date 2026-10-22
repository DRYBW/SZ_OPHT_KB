# A second discriminating marker for the 26 one-gene-thick subtype panels — literature only,
registered default OFF

Card `t_7509a1a2` (SUBTYPE-2M), board `pi-briefing`, 2026-10-22. Pre-registration:
`PREREG_SUBTYPE_SECOND_MARKER_20261022.md`, with four disclosed amendments
(`AMENDMENT_1_ATTACHMENT_RULE_20261022.md`, `AMENDMENT_2_ATTACHMENT_UNIT_20261022.md`,
`AMENDMENT_3_PREDICATE_LIST_20261022.md`, `AMENDMENT_4_NO_PROXIMITY_CONSTANT_20261022.md`).
Ruler: the frozen `plans/consensus_subtype_20261022/scripts/c3_separation.py`, run through a
two-line local repair of a *reporting* bug (`out/RULER_PATCH.json`); no threshold moved.

## One line

Of the 56 scorable rows the frozen consensus wave left `not_separated`, **26 fail because exactly
one marker clears the gate and no second one does**. Adding, for the 16 distinct subtypes behind
those rows, literature-sourced candidates that are actually measurable, **8 of the 26 rows flip
`not_separated` → `separated`** (separated 12 → 20 of 56), **6 of them robust** under two
independently-derived attachment rules and 3 rule-dependent; **0 rows outside the in-scope set
moved**. 5 of the 16 subtypes get a second marker that is measurable and clears the gate;
the remaining ones are reported as `NOT_AVAILABLE` / `not_measurable` below, not papered over.

## 1. What was asked, and what was measured

The frozen wave (`plans/consensus_subtype_20261022/`) scored every literature-consensus retinal
subtype against our own human retina volumes with a pre-registered ruler (AUC ≥ 0.70 and
Benjamini–Hochberg q < 0.05 for **≥ 2** of the subtype's defining markers, its own author label
against the other subtypes of the same parent type in the same volume). 36 of 56 scorable rows failed, and 26 of those failed the same way: one marker clears, the second is dead weight (the
frozen list's `VSX2` is expressed in every bipolar cell).

This card asks the literature for the missing second marker, builds it as a candidate library
registered **default OFF with an empty whitelist**, and re-measures with the **same ruler, same
code, same thresholds, same volumes**.

## 2. The in-scope set (pinned mechanically, not by hand)

Rule, applied to the frozen result (`result == not_separated AND reason.startswith('1 marker(s) cleared the gate')`):

```
result == "not_separated" and reason.startswith("1 marker(s) cleared the gate")
```

→ **26 rows / 16 distinct subtypes / 7 volumes** (`scripts/m0_freeze_inputs.py` asserts these
counts; the row list is in `out/INPUT_MANIFEST.json`). Deliberately out of scope: the 12
already-`separated` rows, the 8 `insufficient_evidence` rows and the 2 `not_separated` rows with
**zero** markers clearing — adding a second marker to an empty panel is a different claim.

| volume | subtype | cells | the marker that cleared | the marker(s) that did not |
|---|---|---:|---|---|
| CX01_retina_snRNA | flat midget bipolar cell (FMB, OFF midget bipolar) | 3225 | GRIK1 0.81 | VSX2 0.47 |
| CX01_retina_snRNA | diffuse bipolar 2 (DB2) | 3225 | GRIK1 0.90 | VSX2 0.52 |
| CX01_retina_snRNA | diffuse bipolar 3a (DB3a) | 3225 | GRIK1 0.76 | VSX2 0.42 |
| CX01_retina_snRNA | diffuse bipolar 3b (DB3b) | 3225 | GRIK1 0.89 | VSX2 0.52 |
| CX01_retina_snRNA | diffuse bipolar 4 (DB4) | 3225 | GRM6 0.81 | VSX2 0.40 |
| CX01_retina_snRNA | diffuse bipolar 6 (DB6) | 3225 | GRM6 0.74 | SCGN 0.50 |
| CX01_retina_snRNA | blue-cone bipolar cell (BB, S-cone ON bipolar) | 2931 | GRM6 0.72 | VSX2 0.58 |
| CX01_retina_snRNA | giant bipolar cell (GB) | 3225 | UTRN 0.91 | — |
| CX01_retina_snRNA | H1 horizontal cell | 3225 | LHX1 0.76 | SPP1 0.44 |
| CX01_retina_snRNA | H2 horizontal cell | 3225 | ISL1 0.71 | SPP1 0.56 |
| CX03_retina_multiome | ON cone bipolar cell (ON BC) | 2617 | TRPM1 0.73 | GRM6 0.69, ISL1 0.53, ST18 0.56 |
| CX03_retina_multiome | OFF cone bipolar cell (OFF BC) | 3936 | GRIK1 0.99 | FEZF2 0.60, LHX3 0.52 |
| CX04_cowan_fovea | rod bipolar cell (RBC, ON rod bipolar) | 1016 | PRKCA 0.90 | TRPM1 0.56, VSTM2B 0.69 |
| CX04_cowan_organoid | OFF cone bipolar cell (OFF BC) | 686 | GRIK1 0.75 | FEZF2 0.62, LHX3 0.58 |
| CX04_cowan_periphery | OFF cone bipolar cell (OFF BC) | 1470 | GRIK1 0.85 | FEZF2 0.68, LHX3 0.57 |
| PRE_GSE268630 | invaginating midget bipolar cell (IMB, ON midget bipolar) | 1466 | GRM6 0.79 | VSX2 0.38 |
| PRE_GSE268630 | flat midget bipolar cell (FMB, OFF midget bipolar) | 3571 | GRIK1 0.78 | VSX2 0.46 |
| PRE_GSE268630 | diffuse bipolar 2 (DB2) | 2371 | GRIK1 0.82 | VSX2 0.51 |
| PRE_GSE268630 | diffuse bipolar 3b (DB3b) | 2704 | GRIK1 0.76 | VSX2 0.60 |
| PRE_GSE268630 | diffuse bipolar 4 (DB4) | 291 | GRM6 0.89 | VSX2 0.52 |
| PRE_GSE268630 | diffuse bipolar 6 (DB6) | 429 | GRM6 0.89 | SCGN 0.50 |
| PRE_GSE268630 | H1 horizontal cell | 477 | LHX1 0.79 | SPP1 0.58 |
| PRE_GSE268630 | H2 horizontal cell | 928 | ISL1 0.72 | SPP1 0.52 |
| PRE_OA-D001 | starburst (cholinergic) amacrine cell | 986 | SLC5A7 0.91 | CHAT 0.67, SLC18A3 0.69 |
| PRE_OA-D001 | H2 horizontal cell | 1858 | ISL1 0.73 | SPP1 0.70 |
| PRE_OA-D001 | parasol retinal ganglion cell | 446 | SPP1 0.85 | RBPMS2 0.62, CHRNA2 0.66, CA8 0.51 |

## 3. How the panels were assembled (literature only)

| channel | source | rule |
|---|---|---|
| A | the in-repo literature corpus (`v2.6-dev`, 244,877 chunks / 3,902 papers) | a gene symbol in a segment that carries a marker/expression predicate and names exactly one in-scope subtype |
| B | the 43 sources the frozen wave itself already fetched (`out/G1..G3*.json` `sources[]`) | same rule inside a `what_it_supports` clause |
| C | `kb/textbook_layer/TEXTBOOK_ITEMS_v1.jsonl` (verbatim quotes) | same rule; the bibliographic index `kb/vk_literature_index/` is **not** a statement source and generates nothing |

L1 ≥ 1 attached statement (paper count recorded; a stricter `papers ≥ 2` reading is recorded per
gene) · L2 the symbol is in the assay vocabulary · L3 not already one of the subtype's frozen
markers · L4 a symbol attached to ≥ 3 in-scope subtypes is not a discriminator and is rejected for
all of them (this rule reproduces the `VSX2` failure mechanically) · L5 cap **K = 2** per subtype,
ranked by paper count, then channel B, then symbol — the cap bounds the multiple-testing burden the
unchanged ruler carries, because BH is applied across the subtype's marker set.

**Measurability** (technical floors only, no differential test): the symbol is in the volume's
`var/_index` **and** detected (`X > 0`) in ≥ 5 % of that volume's cells. A gene below the floor
is recorded `not_measurable_here`, never claimed.

### The mining rule needed four disclosed repairs — and all five passes are on disk

The rule that turns free text into *"this gene marks this subtype"* is where the error lives, so
each repair was written down with its verbatim counter-example before re-running, and every pass
was preserved. Nothing else was tuned: the acceptance gate never moved.

| pass | attachment rule | candidates admitted | kept (K=2) | what the pass exposed |
|---|---|---:|---:|---|
| 1 | sentence-level co-mention | 29 | 11 | named a gene and a subtype in one sentence without asserting a relation (`NR2E3` for ON BC, `VIP` for starburst) |
| 2 (AD1) | clause + marker predicate | 69 | 22 | `LMO4` attached to DB6 across a comma boundary; `TTR` attached on a fovea-vs-periphery contrast |
| 3 (AD2) | + comma-level segment, nearest subtype | 40 | 16 | the predicate list omitted `characteriz*`, silently dropping the corpus's most informative sentence |
| 4 (AD3) | + `characteriz/discriminat/defined` | 43 | 17 | an arbitrary 80-character window rejected the literature's own "full name then symbol in parentheses" style (`LMO4`/DB4 at 87 chars, `DNER`/DB6 at ~104) |
| **5 (AD4, headline)** | **structural: the segment names exactly one in-scope subtype; ambiguous segments attach nothing** | **47** | **17** | — |

The repairs moved candidates in both directions (AD1/AD2 remove mis-attachments, AD3 restores a
lexically-dropped class, AD4 removes the arbitrary constant), which is why the headline is reported
as the **robust** set — rows that flip under both AD1 (pass 2) and the final rule (pass 5).

## 4. The railings: the ruler reproduces the frozen result

| arm | rows | separated | not_separated | insufficient_evidence |
|---|---:|---:|---:|---:|
| frozen result (on disk) | 56 | 12 | 36 | 8 |
| control: frozen rows × frozen ruler | 56 | — | — | — |
| control: frozen rows × local ruler | 56 | — | — | — |
| **augmented rows × local ruler** | 56 | **20** | **28** | **8** |

Both control arms reproduce the frozen 56 rows **verdict for verdict**
(`control_reproduces_frozen_verdicts = True`; `out/RULER_RUNS.json`). The frozen ruler itself cannot
finish the augmented arm: it raises `IndexError` while *reporting* `marker_detail` when a marker's
p-value is `None` (the constant-vs-constant case it already handles by assigning AUC 0.5). The
local copy re-indexes those q-values through a `qmap` and changes nothing else —
19 diff lines, `AUC_MIN = 0.70`, `FDR_MAX = 0.05`, `MIN_CELLS = 30`, `SHARE_FACTOR = 4.0` all
byte-identical (`out/RULER_PATCH.json`), and the local copy re-runs the control arm to the same
56 verdicts. **The frozen wave's own files were never written.**

## 5. Result — what flips

| volume | subtype | cells | before | after | markers that cleared (AUC, q) | added gene(s) | independence | ρ | verdict |
|---|---|---:|---|---|---|---|---|---|---|
| CX01_retina_snRNA | diffuse bipolar 2 (DB2) | 3225 | not_separated | separated | GRIK1 0.900 / 0, CACNA1G 0.751 / 0 *, GSG1 0.752 / 0 * | CACNA1G, GSG1 | two_independent_claims | 0.05 | robust |
| CX01_retina_snRNA | diffuse bipolar 3a (DB3a) | 3225 | not_separated | separated | GRIK1 0.761 / 0, CALB1 0.799 / 0 * | CALB1 | two_independent_claims | 0.17 | robust |
| CX01_retina_snRNA | diffuse bipolar 3b (DB3b) | 3225 | not_separated | separated | GRIK1 0.894 / 0, MEIS2 0.966 / 0 * | MEIS2 | two_independent_claims | 0.29 | robust |
| CX01_retina_snRNA | diffuse bipolar 4 (DB4) | 3225 | not_separated | separated | GRM6 0.810 / 0, LMO4 0.844 / 0 * | LMO4 | two_independent_claims | 0.22 | robust |
| PRE_GSE268630 | diffuse bipolar 2 (DB2) | 2371 | not_separated | separated | GRIK1 0.822 / 0, GSG1 0.768 / 0 * | GSG1 | two_independent_claims | 0.48 | robust |
| PRE_GSE268630 | diffuse bipolar 3b (DB3b) | 2704 | not_separated | separated | GRIK1 0.761 / 0, MEIS2 0.796 / 0 * | MEIS2 | two_independent_claims | 0.26 | robust |
| PRE_GSE268630 | diffuse bipolar 4 (DB4) | 291 | not_separated | separated | GRM6 0.885 / 3.57e-131, LMO4 0.907 / 5.04e-175 * | LMO4 | two_independent_claims | 0.14 | rule_dependent |
| PRE_GSE268630 | flat midget bipolar cell (FMB, OFF midget bipolar) | 3571 | not_separated | separated | GRIK1 0.779 / 0, GLRA1 0.845 / 0 * | GLRA1 | two_independent_claims | 0.34 | rule_dependent |

`*` = a gene this wave added; everything else is the frozen panel. `ρ` is the observed Spearman
correlation between the two clearing markers across the cells of that comparison — a disclosure,
never a selection criterion (flag at |ρ| ≥ 0.6: none reached it). **All 8 flips are
`corroborated`**: their two clearing markers come from claims that share no paper, no flag fired,
and no symbol-family collision was found (`out/FLIPS.json`, H1–H5 pre-registered in PREREG §8).

### Robustness (promised in AD3/AD4)

| row | flips under AD1 (pass 2) | flips under the final rule (pass 5) | verdict |
|---|---|---|---|
| CX01_retina_snRNA / diffuse bipolar 2 (DB2) | True (CACNA1G, GSG1) | True (CACNA1G, GSG1) | **robust** |
| CX01_retina_snRNA / diffuse bipolar 3a (DB3a) | True (CALB1) | True (CALB1) | **robust** |
| CX01_retina_snRNA / diffuse bipolar 3b (DB3b) | True (MEIS2) | True (MEIS2) | **robust** |
| CX01_retina_snRNA / diffuse bipolar 4 (DB4) | True (TTR) | True (LMO4) | **robust** |
| PRE_GSE268630 / diffuse bipolar 2 (DB2) | True (GSG1) | True (GSG1) | **robust** |
| PRE_GSE268630 / diffuse bipolar 3b (DB3b) | True (MEIS2) | True (MEIS2) | **robust** |
| PRE_GSE268630 / diffuse bipolar 4 (DB4) | False (—) | True (LMO4) | **rule_dependent** — only under `final_pass5` |
| PRE_GSE268630 / diffuse bipolar 6 (DB6) | True (LMO4) | False (—) | **rule_dependent** — only under `AD1_pass2` |
| PRE_GSE268630 / flat midget bipolar cell (FMB, OFF midget bipolar) | False (—) | True (GLRA1) | **rule_dependent** — only under `final_pass5` |

**6 robust / 3 rule-dependent.** The rule-dependent three are named honestly: `diffuse bipolar
6` at PRE_GSE268630 flips only under AD1, and it flips on `LMO4` — the gene the same sentence
assigns to **DB4**; under the final rule that mis-attachment is gone and DB6 has no candidate. The
other two (`DB4` / PRE_GSE268630 on `LMO4`, `FMB` / PRE_GSE268630 on `GLRA1`) flip only under the
final rule, because the AD1 window could not see the statement.

## 6. The panels, per subtype

| subtype | cells (volumes where its rows sit) | added by this wave | evidence (papers) | measurable in the row's volume? | outcome on its rows |
|---|---|---|---|---|---|
| H1 horizontal cell | CX01_retina_snRNA, PRE_GSE268630 | **none admitted** | — | — | CX01_retina_snRNA: not_separated; PRE_GSE268630: not_separated |
| H2 horizontal cell | CX01_retina_snRNA, PRE_GSE268630, PRE_OA-D001 | **none admitted** | — | — | CX01_retina_snRNA: not_separated; PRE_GSE268630: not_separated; PRE_OA-D001: not_separated |
| OFF cone bipolar cell (OFF BC) | CX03_retina_multiome, CX04_cowan_organoid, CX04_cowan_periphery | SI (1) † | SI: *a bistratified wide-filed AC (AC1) receives excitation from a sustained OFF bipolar cell in the OFF sublamina * | SI@CX03=no, SI@CX04=no, SI@CX04=no | CX03_retina_multiome: not_separated; CX04_cowan_organoid: not_separated; CX04_cowan_periphery: not_separated |
| ON cone bipolar cell (ON BC) | CX03_retina_multiome | CA1 (1) †, CRX (1) † | CA1: *5B⁗ ) before conducting a subsequent round of IF with MG antibody markers (CA1 and GS) and the ON bipolar cell*; CRX: *Protein kinase C‐alpha, which identifies ON bipolar cells, was detected in few cells at day 90 basally to CRX+* | CA1@CX03=no, CRX@CX03=yes | CX03_retina_multiome: not_separated |
| blue-cone bipolar cell (BB, S-cone ON bipolar) | CX01_retina_snRNA | **none admitted** | — | — | CX01_retina_snRNA: not_separated |
| diffuse bipolar 2 (DB2) | CX01_retina_snRNA, PRE_GSE268630 | CACNA1G (1) †, GSG1 (1) † | CACNA1G: *These molecular differences are further supported by transcriptomic data showing higher levels of expression o*; GSG1: *DB2 bipolar cells were distinguished using germ cell-specific gene 1 protein ( GSG1* | CACNA1G@CX01=yes, GSG1@CX01=yes, CACNA1G@PRE=yes, GSG1@PRE=yes | CX01_retina_snRNA: separated; PRE_GSE268630: separated |
| diffuse bipolar 3a (DB3a) | CX01_retina_snRNA | CALB1 (1) † | CALB1: *DB3a bipolar cells were characterized based on calbindin 1 ( CALB1* | CALB1@CX01=yes | CX01_retina_snRNA: separated |
| diffuse bipolar 3b (DB3b) | CX01_retina_snRNA, PRE_GSE268630 | MEIS2 (1) †, QPCT (1) † | MEIS2: *We were also able to identify marker genes of DB3b ( MEIS2 ) and DB5 ( QPCT ) for human and monkey BCs.*; QPCT: *We were also able to identify marker genes of DB3b ( MEIS2 ) and DB5 ( QPCT ) for human and monkey BCs.* | MEIS2@CX01=yes, QPCT@CX01=yes, MEIS2@PRE=yes, QPCT@PRE=no | CX01_retina_snRNA: separated; PRE_GSE268630: separated |
| diffuse bipolar 4 (DB4) | CX01_retina_snRNA, PRE_GSE268630 | LMO4 (1) † | LMO4: *DB4 bipolar cells were identified based on expression of LIM domain only protein 4 ( LMO4* | LMO4@CX01=yes, LMO4@PRE=yes | CX01_retina_snRNA: separated; PRE_GSE268630: separated |
| diffuse bipolar 6 (DB6) | CX01_retina_snRNA, PRE_GSE268630 | DNER (1) † | DNER: *and DB6 bipolar cells were characterized using Delta and Notch-like epidermal growth factor-related receptor (* | DNER@CX01=yes, DNER@PRE=yes | CX01_retina_snRNA: not_separated; PRE_GSE268630: not_separated |
| flat midget bipolar cell (FMB, OFF midget bipolar) | CX01_retina_snRNA, PRE_GSE268630 | GLRA1 (1) † | GLRA1: *Additional evidence for selective expression of GLRA1 in DB1 and FMB cells is shown in  Figure 8 A  below.* | GLRA1@CX01=yes, GLRA1@PRE=yes | CX01_retina_snRNA: not_separated; PRE_GSE268630: separated |
| giant bipolar cell (GB) | CX01_retina_snRNA | **none admitted** | — | — | CX01_retina_snRNA: not_separated |
| invaginating midget bipolar cell (IMB, ON midget bipolar) | PRE_GSE268630 | **none admitted** | — | — | PRE_GSE268630: not_separated |
| parasol retinal ganglion cell | PRE_OA-D001 | AFAP1 (2), POU6F2 (2) | AFAP1: *which was enriched in midget ganglion cells;  CAV2  and  POU6F2  enriched in ON parasol RGCs and  AFAP1*; POU6F2: *In the rhesus macaque retina, POU6F2 labels the large parasol ganglion cells that form the magnocellular (M) p* | AFAP1@PRE=yes, POU6F2@PRE=yes | PRE_OA-D001: not_separated |
| rod bipolar cell (RBC, ON rod bipolar) | CX04_cowan_fovea | C3 (1) †, NRL (3) | C3: *loss of rod bipolar cells was associated with increased transcription of the complement factor 3 ( C3 )*; NRL: *these expression patterns were similar to those of other rod (neural retina leucine zipper [NRL] and Recoverin* | C3@CX04=no, NRL@CX04=yes | CX04_cowan_fovea: not_separated |
| starburst (cholinergic) amacrine cell | PRE_OA-D001 | CTBP2 (1) †, EMD (1) † | CTBP2: *For example,  CTBP2  was not detected in GABAergic starburst ACs co-expressing  CHAT  and  GBX2  ( Supplementa*; EMD: *Cholinergic amacrine cells were labelled with goat anti-choline acetyltransferase (ChAT; 1:100; #AB144; EMD Mi* | CTBP2@PRE=yes, EMD@PRE=yes | PRE_OA-D001: not_separated |

† = the single attached statement is the only evidence for that gene (paper count 1; the stricter
`papers ≥ 2` reading is recorded per gene in `out/SUBTYPE_SECOND_MARKER_LIT.tsv`). The panel itself
is `kb/markers/markers_v14_subtype_second_increment.json`: 16 entries, each named by the Cell
Ontology label of the term it carries, **16/16 CL ids resolve** against the frozen snapshot
`releases/2026-06-08`, frozen markers and added candidates kept in separate fields.

### The honest misses

**5 of the 16 subtypes get nothing at all** (`NOT_AVAILABLE`): H1 horizontal cell, H2 horizontal cell, blue-cone bipolar cell (BB, S-cone ON bipolar), giant bipolar cell (GB), invaginating midget bipolar cell (IMB, ON midget bipolar) — the corpus either never
assigns a second measurable marker to them, or the segment-level rule leaves the assignment
ambiguous by construction.

Where a candidate was measurable but did **not** discriminate, that is a result too — the added
gene's own AUC is printed by the ruler and it stays `not_separated`:

| subtype | volume | added and measurable | its AUC | outcome |
|---|---|---|---:|---|
| ON cone bipolar cell (ON BC) | CX03_retina_multiome | CRX | nan | not_separated |
| diffuse bipolar 6 (DB6) | CX01_retina_snRNA | DNER | nan | not_separated |
| diffuse bipolar 6 (DB6) | PRE_GSE268630 | DNER | nan | not_separated |
| flat midget bipolar cell (FMB, OFF midget bipolar) | CX01_retina_snRNA | GLRA1 | nan | not_separated |
| parasol retinal ganglion cell | PRE_OA-D001 | AFAP1 | nan | not_separated |
| parasol retinal ganglion cell | PRE_OA-D001 | POU6F2 | nan | not_separated |
| rod bipolar cell (RBC, ON rod bipolar) | CX04_cowan_fovea | NRL | nan | not_separated |
| starburst (cholinergic) amacrine cell | PRE_OA-D001 | CTBP2 | nan | not_separated |
| starburst (cholinergic) amacrine cell | PRE_OA-D001 | EMD | nan | not_separated |

Two further misses are named because they are *rule* misses, not literature misses, and the
counter-evidence is in the artefacts: `DNER` (the literature's own DB6 marker) and `CALB1` (the
literature's own DB3a marker) are lost by pass 4's discarded 80-character window; `CALB1` is
recovered by the final rule and flips DB3a, while `DNER` is measurable in both DB6 volumes
(detected in 39.8% / 44.7% of cells) and still does not clear the gate (AUC nan / nan) — a genuine
negative about these volumes, not about the literature.

## 7. What this does **not** say

* The reading is **in-sample**: the same 7 volumes produced the question and the answer.
* A flip shows a literature-sourced second marker **exists and is measurable**; it is not an
  accuracy claim about the annotator and not evidence that a subtype was "found".
* No subtype enters any shipped vocabulary: the increment is registered **default OFF with an
  empty whitelist** (`SUBTYPE_DEFAULT_LIBS = ()`), no other wave's whitelist tuple was touched, and
  the default route's bytes are unchanged — **measured, not asserted**: 950 calls (the recorded 721
  cluster windows plus the class/species battery) replayed with the parent blob and the committed
  blob imported side by side at the same directory → **0 differing calls**, route composition
  identical, `subtype_v14` reachable **by name only** and absent from `all` in every switch state
  (`out/DEFAULT_FACE.json`).
* The mining rule has known residual blind spots, all documented with verbatim counter-examples
  (AD1–AD4). It is a *defensible* instrument, not a perfect one.

## 8. Re-deriving

```
cd /mnt/D/EyeKB/plans/subtype_second_marker_20261022
bash scripts/run_all.sh          # the whole read-only chain under the network audit hook
python3 scripts/m10_manifest_gate.py   # manifest + the wave's own gate
cd /mnt/D/EyeKB/plans/subtype_second_marker_20261022 && sha256sum -c /mnt/D/EyeKB/plans/subtype_second_marker_20261022/out/MANIFEST.sha256
```

Heavy steps are run under `systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=2G`; the
largest in-scope volume was measured at **5.06 GiB peak RSS / 12 s** single-process
(`scripts/m0b_rss_probe.py CX01_retina_snRNA`), concurrency ≤ 4, one volume at a time in practice.

## 9. Provenance

| artefact | what it holds |
|---|---|
| `out/INPUT_MANIFEST.json` | sha256 of every frozen input + the re-derived in-scope set |
| `out/SUBTYPE_SECOND_MARKER_LIT.{json,tsv}` | every candidate with its papers, segments and L1–L5 decision, rejected ones included |
| `out/SUBTYPE_SECOND_MARKER_MEASURABILITY.{json,tsv}` | M1/M2 readings per candidate per volume |
| `out/SUBTYPE_OBSERVABILITY_rows_augmented.json` | the frozen rows with `_markers_all` extended; every other field byte-preserved |
| `out/ruler_control/`, `out/ruler_control_local/`, `out/ruler_augmented/` | the three ruler runs (frozen ruler / local ruler / augmented) |
| `out/RULER_PATCH.json` | the unified diff of the two-line repair + both sha256 + the proof it is behaviour-preserving |
| `out/FLIPS.{json,tsv}` | per row before/after with the marker evidence and the H1–H5 classification |
| `out/ATTRIBUTION_CHECK.json` | the full, untruncated clause behind every flip-driving gene (a disclosure added after the measurement) |
| `out/ROBUSTNESS.{json,tsv}` | the two-rule robustness reading |
| `out/SUBTYPE_SECOND_MARKER_PANEL.json` | the delivered panel, per subtype |
| `kb/markers/markers_v14_subtype_second_increment.json` | the candidate library (repo side, default OFF, empty whitelist) |
| `out/DEFAULT_FACE.json` | the default-face byte-identity measurement |
| `out/REGISTRY_UPDATE.json` | the two registry rows (`L1-11M` re-taken from the committed blob, `L1-31` new) |
| `out/MANIFEST.sha256`, `out/GATE.json`, `ledgers/net_audit.log` | content manifest, gate readings, zero-network receipts |
| `out/SUPERSEDED_m1_mine_lit_p1.json`, `out/SUPERSEDED_pass2..4/` | the four superseded mining passes, byte-preserved |

Registry: `docs/W3_PIPELINE_REGISTRY.tsv` — new row **L1-31** for the library; row **L1-11M** re-taken
from the committed blob. The shared working tree simultaneously carried another card's in-flight
activation (`docs/plans/activate_holefill_20261022/`, card `t_be11fd4a`); its bytes are deliberately
**not** part of this commit — absorbing them would corrupt both cards' before/after evidence — and
that card re-takes the row in its own commit.


## 10. Collision note — a second card was live in the same working tree

`mcp_server/eyekb_core.py` is shared. While this card was measuring, another card
(`t_be11fd4a`, `docs/plans/activate_holefill_20261022/`) was mid-flight on the same file in the same
tree, and the sequencing was measured, not assumed:

| time | event | sha256 of the live file |
|---|---|---|
| before this card's edit | working tree already carried that card's in-flight activation (the parent commit's blob is `e74c73c6…`) | `bd45c6b9…` |
| this card's registration applied on top | both cards' edits coexisted; **one defect of my own was found here and fixed**: my first replacement dropped the `"onfibro_v13"` dictionary entry (the same append pattern that broke this file in an earlier wave), which made the default route raise `KeyError`. Restored, verified, and the failure mode is now written into the registration script itself. | `fb6c0408…` |
| commit built | this card's delta was applied to the **parent commit's blob** (`out/COMMITTED_eyekb_core.py`), never to the coexistence file | `528c474e…` |
| commit `86d37a3` | `git commit` with an explicit path list; the other card's bytes are **not** in it | — |

Absorbing the other card's half-finished activation into this commit would have corrupted both cards'
before/after evidence (its acceptance test compares HEAD against the flipped tree), so the shared file
was rebuilt from the parent blob for the commit and left untouched in the worktree. The default-face
measurement was therefore taken on two blobs imported side by side at the same directory — same
paths, only the bytes differ — which is what makes the identity claim free of that card's state.
Registry row `L1-11M` records the committed blob's sha plus the live sha observed at registration
time, and says that the other card re-takes the row in its own commit.

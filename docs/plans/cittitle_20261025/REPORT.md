# CITTITLE (card t_d8e7f2d4) — report: what was done, what was found, what was not done

## 1 What was done

1. **The fix, in the builder.** `kb/link_registry/scripts/build_link_registry.py` gains
   `corpus_meta_index()` (reads the shipped corpus into `paper_id -> {title, doi, pmcid, is_preprint}`
   through `EYEKB_DB_DIR` → `eyekb_core._default_db_dir()` → the in-repo G2 slim library, read-only,
   default route unchanged) and `citation_field()`, and writes the **complete** title plus `doi` /
   `pmcid` on both citation routes instead of `(hit title)[:120]` and `""`. It also prints, on every
   build, how many cited ids resolved — an unresolved id can no longer become a silent blank title.
2. **The repaired registry, delivered beside the frozen one.** `out/LINK_REGISTRY_v2_cittitle.jsonl`
   (anchor twin) adds `title_full` / `doi` / `pmcid` to all 3,993 citation records and reproduces the
   frozen file byte-for-byte when the three keys are removed; `…_dropin.jsonl` is that twin with
   `title := title_full`. The frozen `LINK_REGISTRY_v1.jsonl` is **byte-identical to before**
   (sha `a04be771…`), per the brief's "old artefact kept side by side" and the standing "frozen
   artefacts are not rewritten" rule.
3. **The counterfactual, attributed line by line.** Both calibers (strict / 40-character prefix) × two
   normalisations × before/after; every unmatched row carries a `reason_code` and a `reason_text`;
   per-record and per-paper ledgers; and three non-circular controls (cross-corpus, field controls on
   the same join, and the already-complete citation titles).
4. **A machine gate, because nothing on disk could catch this.** `tests/gate_cittitle_meta.py` (G12),
   wired into `tests/run_gates.sh` and registered in `docs/GATE_INVENTORY_G5G6.tsv`: seven fail-closed
   checks (source regression / metadata present / metadata equals the corpus / coverage / byte anchor
   against the delivery's immutable pre-image / builder-vs-gate reader parity / planted-shape
   self-test), rc 0-2-3 with a corpus-absent INCONCLUSIVE. Six reverse controls were then planted on
   the real tree and restored byte-identically (`out/G12_CONTROLS.json`).
5. **Registrations.** Ownership-ledger rows L6-01 and L6-22 re-taken, L6-53…L6-57 added; G12 in the
   gate inventory (plus the G2 row's entry-point sha re-taken, since G2's entry point is the contract
   file that §5.7 changed); a change-control instance row `CHG-20261025-CITTITLE`
   (12 content cells + evidence); `docs/VERIFY_CONTRACT.md` §5.7; `docs/W3_MANIFEST.sha256` re-frozen
   last; release identity re-taken.

## 2 What was found besides the brief's defect

1. **The brief's counts are audit-side, not registry-side — and the registry is worse.**
   884 empty / 116 truncated / 2 preprint / 1 rewritten are the `reason_code` frequencies of the
   LINKKEY card's `UNMATCHED_v1.tsv` (1,003 rows = 560 rows of caliber A + 443 of caliber B). Read
   live on the registry itself, the defect is 2,429 empty records and 509 genuinely capped ones
   (455 and 122 respectively when de-duplicated to papers). Both granularities are reported; neither
   is used to check the other. There are **5** cited `PPR_*` ids now, not 2.
2. **A blunt `len(title) == 120` test over-counts the damage by 2 records in 511** — two papers'
   real titles are exactly 120 characters long, so the cap test has to be a prefix test against the
   corpus, not a length test. This distinction is now explicit in the ledger
   (`CAPPED_120` vs `GENUINE_120`).
3. **One of the pre-fix "misses" was never a defect.** A citation title can differ from the corpus
   title only by presentation marks — an HTML tag (`<i>PRRX1</i>`), an HTML entity (41 corpus titles
   carry `&lt;i&gt;…`), a Unicode dash (`‐` `–`, which NFKC does not fold to ASCII) or a doubled
   space. The retrieval route carried the plain-text form. An N1-only comparison therefore files a
   *display* difference as "the libraries disagree": measured 1 paper at caliber A, 1 at caliber B.
   The two normalisations are reported side by side for that reason.
4. **All three corpus copies agree.** The same 825 cited ids resolve in the G2 slim library, the
   pointer's `role:default` library and the v2.6-dev library, with **0** title disagreements — so the
   readings here are not an artefact of which corpus copy was used.
5. **Two defects in this card's own first pass, found by its own instruments and recorded rather than
   quietly fixed** (the repository's rule is that a self-audit finding is registered as a scrutineer
   defect, not folded into the claim):
   - the independent verifier caught a **malformed TSV row**: a corpus title contains a newline
     (pmid 40552921), so a hand-written one-row-per-line TSV split one record across three physical
     lines. Every row count was still correct, so only the independent read caught it. A cell
     sanitiser was added and the file re-emitted.
   - the counterfactual's 40-character-prefix arm was called positionally, and
     `tables_prefix_equal(a, b, n=40, unescape=False)` takes the **third positional slot as the prefix
     length** — the arm was silently comparing against a zero-character prefix and reporting
     "everything with a non-empty title matches". It was caught because the cross-corpus column
     disagreed with the main column (369 vs 370) for a reason the code could not explain. Both
     columns now agree at 369 / 370.
   - the ledger's cap test was byte-exact while the classifier's was display-tolerant, so 21 capped
     records were filed as complete; the independent verifier's live defect count (511 = 509 + 2)
     exposed the inconsistency.
6. **The join is exact, so no fuzzy step is needed.** All 825 cited ids match a corpus `paper_id`
   exactly, and the field controls on that same join are 825/825 (year) and 820/825 (journal), the
   five exceptions being the `PPR_*` preprints whose corpus journal field is empty — a disclosed
   difference, not repaired by this card.

## 3 What was deliberately not done

- **The frozen registry is not rebuilt or promoted.** `kb/link_registry/LINK_REGISTRY_v1.jsonl` is
  byte-unchanged, so a consumer of that file still sees the defect until either the builder is re-run
  (it now carries the fields) or the coordinator promotes the twin — the latter moves the
  knowledge-bundle identity, which is not this card's decision. G12 handles both states: it tests the
  live file when it carries the three keys and the delivered twin otherwise, and says which one it
  tested.
- **No re-run of the builder was used to produce the delivered registry.** A rebuild would re-run
  retrieval, so the delivered twin is instead a deterministic, byte-anchored transform of the frozen
  file, and the builder patch guarantees future rebuilds carry the fields. The two are cross-checked:
  G12-C06 requires the builder's own reader to agree with the gate's independent reader.
- **No claim of agreement between the two libraries.** The post-fix 825/825 is a same-source
  construction and is labelled as such everywhere it appears; the evidence sits in the cross-corpus,
  field-control and already-complete-title columns.
- **`doi` / `pmcid` are not used as identity evidence** — they come from the same corpus and share its
  lineage; they are presentation fields that make a citation openable.
- **No download, no network, no GPU; the corpus is read-only (three copies opened for reading only);
  no push; no expected anchor moved; no frozen artefact rewritten.**

## 4 Readings (live, from disk)

| | before | after |
|---|---|---|
| citation records carrying a usable full title | 1,053 / 3,993 | 3,993 / 3,993 |
| distinct cited papers matched, strict caliber | 247 / 825 (29.94 %) | 825 / 825 |
| distinct cited papers matched, prefix-40 caliber | 369 / 825 (44.73 %) | 825 / 825 |
| unmatched rows with a reason | 2,066 | 0 |
| gates in the one-click entry | 9 | 10 |

Negative column: nothing on the default answer route improves (0 route readings move); the shipped
frozen registry is unchanged, so its readers see no change; the preprints' journal difference is
disclosed rather than repaired; and the post-fix 100 % is explicitly not claimed as independent
agreement.
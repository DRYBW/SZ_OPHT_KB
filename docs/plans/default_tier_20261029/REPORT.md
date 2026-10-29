# Making the compact tier the default

Executed 2026-10-29. Card: `CARD.md` (criteria fixed before any edit) and
`AMENDMENT_1_C3.md` (one criterion corrected before any edit, because its threshold had been taken
from a stale catalogue size).

The previous usability pass built the switch and left the heavy tier as the default, so the switch
only helped a caller who read the description. This pass changes the default. Nothing was removed
from the knowledge base: the full answers are unchanged and one argument away.

## 1. What a caller gets when it expresses no preference

Measured through the real stdio server, one process per state, same absolute repo path. Readings:
`out/BEFORE.json` (pre-change code), `out/AFTER.json` (this change), `out/AFTER_ENV_FULL.json`
(revert path executed).

| call | before | after | ratio |
|---|---|---|---|
| `get_kb_page(scope="index")` | 140,005 | **4,324** | **32.4× smaller** |
| `get_tissue_composition("human","retina")` | 91,332 | **25,745** | **3.55× smaller** |
| `get_tissue_composition("mouse","retina")` | 2,425 | 2,736 | larger: the note costs ~311 chars |
| `get_kb_page(scope="tissue", name="cornea")` | 41,930 | 41,930 | unchanged |
| `get_disease_prior("PDR")` | 23,617 | 23,617 | unchanged |

The mouse composition default is the one default that got *bigger*, because a 2,425-character answer
has less to save than the disclosure it now carries. That is the honest reading; suppressing the
note for small answers would have made the disclosure depend on size.

## 2. Every explicit choice is untouched

An explicit argument still returns exactly the bytes it returned before. This is the criterion that
keeps the change from being a rug-pull.

| call | before | after | md5 |
|---|---|---|---|
| `detail="full"` on the index page | 140,005 | 140,005 | `44b352e5…` both |
| `detail="full"` on a tissue page | 41,930 | 41,930 | `575719d8…` both |
| `detail="full"` on composition | 91,332 | 91,332 | `c2114c41…` both |
| `summary=False` on the index page | 140,005 | 140,005 | `44b352e5…` both |
| `summary=True` / `detail="answer"` on the index page | 4,013 | 4,013 | `3b9fce1a…` both |
| `detail="answer"` on composition | 25,434 | 25,434 | `bf86987c…` both |

The compact tier a caller asks for on purpose is 4,013 characters; the compact default is 4,324.
The difference is the disclosure block, which is applied **only** when the caller expressed no
preference — so asking for the compact tier explicitly is marginally cheaper than not asking.

## 3. Nothing is silent

A default that got smaller names itself. Both tools return `detail_applied: "answer"` and a
`detail_note` that states the full answer is one call away, which argument returns it, and which
variable restores the old default. Criterion C8 fails if any shrunk default arrives without both
fields; it passes with the disclosure present on all three shrunk defaults.

## 4. The composition tier does not drop citations

The compact composition tier returns the same 10 rows with the same 20 per-row citations as the full
tier; what it leaves out is named in `omitted_fields` (20 keys, including `provenance`, `strata`,
`stage_disclosure` and `evidence_grades`). This was the hard stop on flipping that default: had a row
come back without its citation, the composition default would have stayed heavy.

## 5. One variable puts it back

`EYEKB_DEFAULT_DETAIL=full` restores the pre-change default on all four default calls, measured
against the pre-change run: `44b352e5…` / `575719d8…` / `c2114c41…` / `cf3c46ae…`, 4/4 identical,
and the disclosure fields are absent in that state. Rollback needs no file edit.

The switch is registered in `docs/SWITCH_COVERAGE_REGISTRY.tsv` (regenerated from the source, 29
rows) as answer-affecting, which means an arm that sets it must set it in every arm of a comparison.

## 6. Gate chain

`out/GATE_VERDICTS.json` holds the commands, exit codes and verdict lines as returned by the runs.

| gate | rc | reading |
|---|---|---|
| card criteria (`verify_default_tier.py`) | 0 | **7/7 criteria pass** |
| G6 change control | 0 | 16 changes, 21 checks, **0 fail** |
| G5 switch coverage | 0 | R1 registry in sync, R2 18 reports 0 violations |
| G5/G6 negative battery | 1 | **byte-identical to the pre-change run**, same single pre-existing BAD cell (G5 `P0_POSITIVE_CONTROL` / `G5-C05`) |
| G4 `verify_pipeline.py` | 1 | same pre-existing 1/3 mismatch: `7c225802…` vs expected `6f795b32…` |

G4 and the battery are red before this card and red after it, on the same cell, with byte-identical
output. No acceptance baseline was moved and nothing was re-anchored.

## 7. Legacy tool-panel identity: reported, not absorbed

`tests/probe_tool_panel_identity.py --baseline tests/fixtures/tool_panel_baseline.json` is red at
this release on four calls. Run against the pre-change code, three of them are already red
(`get_kb_page:{scope:index}` and two `search_literature` calls, from catalogue and library growth
since the baseline was recorded). Exactly one moves because of this card:
`get_tissue_composition:{"species":"mouse","tissue":"retina"}`.

`legacy_panel` digest `0eb0cdc5…` → `95952b46…`; `full_panel` `732e40ae…` → `794b871f…`.

The baseline was **not** re-recorded. Re-recording would have absorbed three unrelated drifts inside
a commit that only owns the fourth, which is exactly how a historical red disappears without anyone
deciding to fix it. The item is carried in the change-control row and in `VERIFY_CONTRACT` §5.8, and
no gate of the one-click chain invokes that probe.

## 8. Two things I got wrong, and what caught them

1. **The disclosure leaked onto explicit calls.** My first version keyed "the caller expressed no
   preference" off the `detail` argument alone, so `summary=True` (an explicit choice) also received
   the note: 4,324 characters where the pre-change response was 4,013. The probe caught it as a byte
   difference on a call that was supposed to be untouched. Fixed by treating an explicit `summary`
   as explicit.
2. **A switch nobody could find.** I first read the environment name through a module constant. The
   switch-registry generator scans for `os.environ` reads, so it would have produced a registry that
   was silently missing this switch — the exact defect that gate exists to prevent. The name is now
   written literally, with a comment saying why, and the registry was regenerated (29 rows, R1 in
   sync).

Both were caught inside this card, before commit. Neither is visible in the final readings, which is
the point of keeping the readings reproducible rather than the narrative tidy.

## 9. An incidental defect fixed on the way

`detail=True` (a boolean, which the recorded legacy panel actually passes) raised
`AttributeError: 'bool' object has no attribute 'strip'` inside the core and failed the call.
Reproduced before the change, then fixed in the wrapper: `True` → full tier, `False` → compact tier.
No string caller changes behaviour.

## 10. What this does not do

* No mid tier for a single tissue page: it is 41,930 characters and there is still nothing between
  "one row" and "the whole page".
* No latency claim. Latency must be re-measured on an idle machine; the earlier pass's latency
  column is unusable because another session's job took the machine to load 182.
* No claim of better annotation accuracy. This is a response-size change with the evidence preserved;
  it moves no number that a scoring run reads.
* `mcp_server/server.py` has no identity row in `docs/W3_PIPELINE_REGISTRY.tsv`, so its version is
  carried only by this card's change-control row. That gap is older than this card and is recorded
  here rather than quietly filled.

## Reproduction

```
cd /home/ubuntu/EYEKB_REPO
EYEKB_REPO_ROOT=/home/ubuntu/EYEKB_REPO UX_PY=/home/ubuntu/.conda/envs/pipeline_env/bin/python \
  python docs/plans/default_tier_20261029/probe_default_tier.py --label after \
  --out docs/plans/default_tier_20261029/out/AFTER.json
python docs/plans/default_tier_20261029/verify_default_tier.py            # expect 7/7, rc=0
python docs/plans/default_tier_20261029/scripts/gate_verdicts.py          # rewrites GATE_VERDICTS.json
```

The pre-change readings in `out/BEFORE.json` were taken by stashing `mcp_server/server.py` back to
the parent commit and running the same probe, so "before" and "after" come from the same instrument.
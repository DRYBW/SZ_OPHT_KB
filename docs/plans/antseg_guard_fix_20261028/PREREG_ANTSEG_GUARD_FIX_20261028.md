# Pre-registration: the incumbent margin of the increment-admission guard counts sibling increments

**Written:** 2026-10-28, before any post-fix reading was taken.
**Trigger:** the 2026-10-28 merge experiment (`lensiris_v11` into the default route) failed its
criterion B; root cause localised to a pre-existing defect, not to the change being measured.
**Decision requested:** fix the defect (`PREREG_ANTSEG_GUARD_FIX_20261028.md`, workspace twin is the
same document in Chinese).

The criteria below are frozen. If a criterion turns out to be mis-specified, an erratum section may
be appended and the measurement re-run, but the criterion itself may not be rewritten.

---

## 0. Defect in one sentence

`_antseg_guard_split` computes the incumbent margin as "the best `n_shared` among candidates that
are **not** owned by the antseg file", so entries owned by **any other** increment library are
counted as incumbents and lift this library's admission bar.

Measured consequence: with `lensiris_v11` loaded on the same route, entries at `n_shared = 1` raised
the cornea bar from 2 to 3 shared genes and demoted antseg candidates that were eligible at
`n_shared = 2`.

## 1. Fix definition (single change point)

Replace "not owned by antseg" with "**owned by a shipped library, and not antseg**".

- Shipped set derived from the existing activation whitelists (no new hard-coded list):
  the three base libraries plus `V6_DEFAULT_LIBS`, `K9_DEFAULT_LIBS`, `ANTSEG_DEFAULT_LIBS`,
  `ONFIBRO_DEFAULT_LIBS`, `SUBTYPE_DEFAULT_LIBS`, `CL56_DEFAULT_LIBS`, filtered to names present in
  `MARKER_LIBS`. Empty whitelists contribute nothing; a future activation edits one place.
- `_antseg_is_increment` is untouched (it answers a different question and is used by the scope
  demotion).
- No threshold changes (`ANTSEG_MIN_SHARED = 2`, `ANTSEG_MARGIN = 2` stay), no whitelist changes, no
  new activation.

## 2. Criteria (all must PASS)

| Criterion | Content | Measurement | Requirement |
|---|---|---|---|
| **B1** shipped identity | default `library="all"`, no switch flipped, 25 volumes | full-response md5 **and** ranking sequence vs the pre-fix bytes | identical cluster by cluster (764/764) |
| **B2** explicit identity | 15 libraries named explicitly, same gene probes | full-response md5 | identical (135/135) |
| **B3** unit regression | the guard's own assertion suite | assertions | all pass, including a new sibling-increment case |
| **A1** defect gone | two increments loaded: cornea top-1 losses | same scoring rule as the main table | **= 0** |
| **A2** merge net gain | same state: lens + iris net ≥ +4 | same rule | **≥ +4 clusters** |

If B1/B2/B3 fail, the fix is not merged and the defect goes back to "recorded, not fixed".
If B passes and A2 fails, the fix may still be merged (it is a net improvement at zero risk on the
shipped route) but the library it was found with stays unmerged.

## 3. Out of scope

- No relaxation of the margin or of the minimum shared-gene count, and no criterion changed to chase
  the iris clusters the 2026-10-28 experiment could not convert.
- No change to the `/mnt/D` delivery tree in this card.
- The fix and that library's merge decision are judged separately; neither borrows the other's
  verdict.

## 4. Reproduce

```
python scripts/fix_guard_measure.py --capture    # capture the pre-fix state (done at 20:36)
#   (apply the fix)
python scripts/fix_guard_measure.py --verify     # three states x two semantics + B1/B2/A1/A2
python tests/antseg_guard_wiring_check.py .      # B3
```
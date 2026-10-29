## Amendment 1 (implementation-time, 2026-10-22) — criterion tightened, not relaxed

Written before the code change, after reading the demotion code paths.

`antseg_demoted` turns out to carry three sub-reasons, not one:

| sub-reason | meaning | surfaced in `near_miss`? |
|---|---|---|
| `out_of_declared_tissue_scope` | the class belongs to a different tissue | **no** |
| `no_declared_scope` | the increment declares no scope at all (fail closed) | **no** |
| `below_increment_eligibility` | right class, not enough shared genes vs the incumbent | **yes** |

The CARD's P4 originally wrote the whitelist as `increment_guard`, which would have
swept in the two "wrong class" cases. The whitelist is therefore **narrowed** to
`{state_program_only, below_increment_eligibility}`.

This makes P4 stricter than pre-registered; it does not loosen anything. P4's own
wording is unchanged: zero entries from `tissue_out_of_scope` or
`composite_superset`.

`below_increment_eligibility` entries additionally carry `needs_n_shared` and
`best_incumbent_n_shared` from the guard, so a caller sees not just "nearly
answerable" but "how many more shared genes it needs". Those two fields are copied
through verbatim; `near_miss` is a read-only view of the guard's own numbers.
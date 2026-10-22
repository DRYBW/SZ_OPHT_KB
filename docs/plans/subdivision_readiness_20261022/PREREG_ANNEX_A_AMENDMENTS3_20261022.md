# PRE-REGISTRATION ANNEX A — AMENDMENT, THIRD SET (written 2026-10-22 11:2x CST)

## A11-c Substring defect in the progenitor test (fixes a wrong scope classification; no threshold moves)

**What was observed first**: `Fibroblast` (CL:0000057) and `Limbus_Sclera_fibroblast_C1` each returned **64/64 pairs as
`developmental_axis`**. Cause, read off the code: A11-b's progenitor vocabulary was matched as a plain substring, and
the token `blast` — intended for `neuroblast` / `retinoblast` — also matches inside **f i b l a s t**. Every
fibroblast-family parent was therefore swept onto the developmental axis, and 126 pairs that belong in this audit
were silently excluded from it.

**Amendment**: the progenitor test matches its vocabulary on **word boundaries**. `blast` then matches a standalone
"blast" and not the "blast" inside "fibroblast"; `Myofibroblast` is unaffected for the same reason.

**What this changes**: `Fibroblast`, `Myofibroblast` and `Limbus_Sclera_fibroblast_C1` return to
`in_scope_adult_celltype`, so their children are graded by the §3 rules like every other adult parent. Their
substantive rows (e.g. how many fibroblast children occur in context, and what separates them from keratocyte) are
therefore reported rather than suppressed.

**What this does not change**: no threshold, no tier rule, no emission rule. The recorded defect and its fix are part
of the wave's record; the pre-fix pass is not kept as a separate artefact because it was a pure classification error
with a single mechanical cause, and the fix is verified by counting the affected parents after the re-run (reported in
the wave REPORT).
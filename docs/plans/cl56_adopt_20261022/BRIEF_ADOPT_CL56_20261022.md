TASK — ADOPT the Cell-Ontology child-term candidates into the naming layer, at the granularity the
author labels actually use.

Status: PREPARED, NOT DISPATCHED. It edits the same file as the activation card (t_be11fd4a:
mcp_server/eyekb_core.py) and must not run concurrently with it in the same working tree. Dispatch only
after t_be11fd4a has landed. This brief is written now so the pre-registration exists before the work starts.

AUTHORITY (verbatim record, 2026-10-22). The owner was shown a two-item checklist — (1) enable the literature
hole-fill library, (2) adopt the 56 CL child-term candidates — and answered **"ok"**. Record this AS an
owner-signed adoption decision, not as an audit pass.

CONTEXT (read before acting)
- the wave that produced the candidates, and its gates:
  /mnt/D/EyeKB/plans/cl_depth_devlineage_20261021/REPORT.md (gate A: 9 rules, 0 failures; A3 closure 3,335
  zero errors; A7 cross-file 3,531 names and is_a relations, 0 divergence)
- the candidates: plans/cl_depth_devlineage_20261021/out/CHILD_TERM_CANDIDATES.json / .tsv
  — 56 (parent CL -> child CL) pairs, 342,552 cells involved, **25 carrying corpus support** (the held corpus
    states the term, with a phrase and a locator), 31 without. Ontology snapshot `releases/2026-06-08`.
  Example: our `smooth muscle cell` (CL:0000192) against the author's own label `ciliary muscle cell`
  (CL:1000443), 5 clusters / 26,532 cells, corpus support present.
  **No term was adopted by that card** — adoption is this decision.
- the direction ledger, same file: `we_are_finer_pairs` (our term finer than the author's) is a DIFFERENT
  question and must not be merged into this one.
- the navigation layer built by the same wave: out/ONT_NAV_v1.json, out/ONT_LABELMAP_V2.tsv,
  out/ONT_CLOSURE_is_a.tsv, out/GRANULARITY_FOURWAY_721.tsv (721 clusters / 1,495,330 cells, four-way).
- code repo = /home/ubuntu/EYEKB_REPO (the only git repo). /mnt/D/EyeKB is the plan/delivery tree.

WHY THIS IS WORTH DOING (the measured cost of not doing it)
Clusters whose true answer is a finer term than any class we carry get scored as disagreements when they are
really granularity differences. The wave's own four-way read shows this is not a rounding error: of the
subsumed mass, most is us being coarser than the author. Adoption converts a naming gap into a name.

WHAT TO DO
1. PRE-REGISTER FIRST (file on disk before any measurement): the decision, which pairs are in scope, the
   acceptance rule, the rollback path, and the in-sample disclosure (all numbers come from the same 28 public
   volumes; no accuracy claim).
2. SCOPE RULE (pre-registered, do not widen after seeing results): adopt a pair only if
   (a) the child term exists in the frozen snapshot and is a true is_a descendant of our current term;
   (b) the held corpus states the term (the 25 supported pairs) OR the author's own label in the material is
       literally that term;
   (c) the pair has enough cells to be scorable at the pre-registered floor.
   The 31 unsupported pairs stay OUT of this adoption and are reported as a pending list — an unsupported name
   adopted on our own say-so would be exactly the fabrication this project forbids. If the numbers later argue
   for widening, that is a new pre-registration, not an amendment after the fact.
   Note: adoption adds NAMES at a finer granularity. It must not invent a term the author never used for those
   cells, and must not merge two of our classes.
3. BUILD as a candidate naming increment registered **default OFF with an empty whitelist** first, measure, and
   only then (if the acceptance rule passes) merge it into the default route with a kill switch that restores
   the pre-flip default BYTE-FOR-BYTE — proven by replaying the recorded query set and comparing raw response
   bytes at the SAME absolute path. Keep a pre-image of every changed file.
4. ACCEPTANCE RULE (pre-registered):
   (a) no dataset's consistent share may fall;
   (b) the aggregate inconsistent share must NOT rise — this is the named failure mode (precedent: the L1
       attempt in plans/INDEX.md under scorer_guard_20261020 lowered abstention 23.25% -> 5.55% while raising
       contradictions 17.95% -> 29.32%, ruled NO-GO);
   (c) every move must be attributable cluster by cluster, with the truth label and the before/after answer;
   (d) the finer name must be the author's own label for those cells — report any adopted cluster where it is not.
   The expected, measured mechanism is narrow and must be stated as such: clusters the family-level regex called
   inconsistent because they were finer than our class. Say plainly that this measures naming agreement against
   author labels, not recognition ability — an ontology-consistent name is not evidence of a better call.
5. IF THE ACCEPTANCE RULE FAILS: do not merge into the default route. Leave the increment registered default-off
   and complete the card with the numbers. NO-GO with numbers is a valid outcome.
6. RE-REGISTER in the same commit: the increment's ledger row, the service-core row(s) for the delivery copy,
   docs/RELEASE_IDENTITY.json, one new change-control instance row (parseable anchors per rule R2), and
   docs/W3_MANIFEST.sha256 LAST.
7. GATES in a CLEAN CLONE: G3 / G4 / G5 / G6 / G7 / G8 / G9 / G10 all green. G10 is binding — regenerate
   docs/SWITCH_COVERAGE_REGISTRY.tsv from source via scripts/switch_coverage/arm_hygiene.py. Do not weaken a
   criterion to make a gate pass; re-anchor with the reason recorded and the pre-image kept if a frozen anchor moves.

RED LINES
- Cell Ontology conformance against the frozen snapshot `releases/2026-06-08`; no fabricated term, no term the
  author never used for those cells.
- No scoring / admission-floor / tie-break / window change, no other library activated, no whitelist entry
  beyond this increment.
- `we_are_finer_pairs` must not be folded into this adoption.
- Zero downloads, zero network (audit hook receipts > 0, events = 0).
- Everything mirroring into the repository is in English. No internal jargon.
- Every number carries the command that produced it. NOT_RUN and missing preconditions are never reported as pass.
- Commit locally; DO NOT PUSH. Report the commit hash.

RESOURCE DISCIPLINE (binding): read /home/ubuntu/Desktop/Hermes工作区/WORKSTATION_RULES_资源纪律_20260930.md first;
measure one process's RSS before choosing concurrency; heavy steps under
`systemd-run --user -p MemoryMax=<measured+margin>G -p MemorySwapMax=2G`; concurrency <= min(8, cpu/2);
heartbeat every 30 min with the available reading; below 40 GiB start nothing new.
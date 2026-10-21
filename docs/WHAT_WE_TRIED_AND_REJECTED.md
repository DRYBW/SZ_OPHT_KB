# What we tried and rejected

This file records experiments that failed their pre-registered criteria, together with the readings
that failed them. It exists because the useful half of an evaluation is the half that says no: a
number that looked good on our own development corpus and then vanished on unseen data tells you
where the boundaries are, and it stops the next person from spending a month re-running the same
idea.

Two rules apply to everything below. First, the criteria were written down and frozen **before** the
readings were taken, and they have not been edited since. Second, when a mechanism was measured on a
held-out corpus, no threshold was afterwards adjusted to make it pass — that would turn a validation
corpus into a tuning corpus, and the resulting number would mean nothing.

## How the readings are produced

Both studies below are scored the same way. A cell is counted as **correct** when the class the
service returns is the same Cell Ontology term as the reference label. A return that is more
specific than the reference (the reference says "bipolar cell", the service says "5b cone bipolar
cell") is counted separately as **more specific**, and one that is coarser as **less specific** —
neither of those counts as correct or as wrong. A return is **wrong** only when the two terms have no
parent/child relation at all. **Abstaining** — declining to name a class — is a legitimate outcome and
is reported separately; it is never folded into the wrong count.

Two corpora are used.

- The **development corpus**: 28 public human eye datasets, 721 clusters, 1,495,330 cells. This is
  the corpus the knowledge base was built and tuned against, so a gain here is a gain on data the
  design has already seen.
- The **held-out corpus**: one public diabetic-retina single-cell dataset (figshare 28228949),
  32 clusters, 316,932 cells. It was not used to design anything, choose any threshold, or pick any
  endpoint. One disclosure is needed here: the reference labels for this corpus are the project's own
  signed re-annotation of it, not the original authors' labels. That makes it a fair test of whether a
  mechanism generalises, but it is not an independent second opinion on what the cell types are.

## Test 1 — widening the gene panel when the service abstains

**The idea.** When a cluster's top-ranked genes return no marker library entry, ask again with a
wider panel and accept the winner if it shares enough genes with the library entry.

**Why it looked promising.** On the development corpus the mechanism recovers 13,849 cells that were
previously unanswered, of which 13,427 land on the correct class and 422 land one level coarser.
Zero land on a wrong class. Against a total of 1,495,330 cells that is +0.90 percentage points of
correct calls with no measured harm.

**What happened on the held-out corpus.** The gain is zero. Not small — zero.

| Reading on the held-out corpus | Value |
|---|---|
| Clusters where the mechanism triggered and a candidate was adopted | **0** |
| Cells newly answered | **0** |
| Cells left unanswered (30.8% of the corpus) | 97,582 |
| Baseline correct rate, unchanged by the mechanism | 43.78% (138,763 / 316,932) |

Of the 32 clusters, 26 return an answer on the narrow panel already and are therefore out of scope
by design. The remaining 6 clusters were asked again on 30 genes. Their best candidates shared 1 or 2
genes with the library entries, against a floor of 5, and two returned no candidate at all:

| Cluster | Cells | Best candidate on the wider panel | Shared genes | Adopted |
|---|---|---|---|---|
| 6 | 4,044 | microglia | 1 | no |
| 9 | 32,608 | none | — | no |
| 10 | 24,309 | cDC1 | 1 | no |
| 12 | 17,674 | rod | 2 | no |
| 14 | 18,675 | none | — | no |
| 19 | 272 | amacrine cell | 1 | no |

**Decision: rejected. The mechanism stays off by default and is not proposed for production.** The
development-corpus gain came from a property of those particular datasets — abstaining clusters there
happened to carry enough shared genes to clear the floor. Clusters that abstain elsewhere do not. The
mechanism was measuring an artefact of the corpus it was built on.

**The tempting move, and why we did not make it.** Lowering the floor to 1 on the held-out corpus
would have produced answers for those clusters. It would also have converted the only independent
evidence we had into a second tuning set, and the resulting number would tell us nothing about any
future dataset. That option is closed.

**What this actually establishes.** It says something reassuring about the abstentions themselves. On
this corpus, 30.8% of cells get no answer, and the reason is that the evidence genuinely is not
there — not that a wider search was hiding behind a threshold. That is consistent with an independent
reading on the development corpus, where forcing an answer on the same clusters is correct only 34.3%
of the time. Two separate measurements point the same way: **abstaining is protective, and pressing it
down with fallbacks is the wrong direction.**

## Test 2 — tie-break rules and looser admission

**The idea.** Two separate levers, tested as eight arms against one frozen baseline: (a) how ties
between equally-scoring classes are broken, and (b) how many shared genes a class needs before it may
enter the ranking.

**What happened.** All eight arms missed the pre-registered gates. Seven of the eight were also worse
than doing nothing.

| Arm | Correct | Wrong | Abstained | Change in correct |
|---|---|---|---|---|
| Baseline | 588,680 | 251,257 | 265,954 | — |
| Lexicographic tie-break only | 566,080 | 272,298 | 265,954 | **−22,600** |
| Rarity-weighted tie-break | 559,051 | 282,522 | 265,954 | **−29,629** |
| Wide panel (30 genes), minimum 2 shared | 603,840 | 199,028 | 330,112 | +15,160 |
| Wide panel + tie-break | 600,264 | 204,279 | 330,112 | +11,584 |
| Weighted primary score | 599,362 | 214,779 | 330,112 | +10,682 |
| Random tie-break (negative control) | 577,921 | 272,787 | 272,452 | −10,759 |
| Reverse-rarity tie-break (negative control) | 579,530 | 266,015 | 265,954 | −9,150 |

Three gates had been fixed in advance:

- **Correct calls ≥ 605,064 while wrong calls ≤ 252,668.** No arm passed. The best arm, the wide panel
  with a minimum of two shared genes, reached 603,840 correct — 1,224 cells short of the gate.
- **Correct strictly up in at least 24 of the 28 datasets, with wrong calls not rising.** The best arm
  managed 9 of 28. The result is not a near miss; it is the wrong shape.
- **Tie-break rules must beat the status quo by a clear margin.** Both tie-break arms were strongly
  negative (−22,600 and −29,629 correct cells). Changing how ties are broken is not a small
  improvement that needs refining — it is a clear loss. The hypothesis is refuted in the opposite
  direction to the one that motivated the test.

The two negative controls behaved as negative controls should: neither beat the baseline. That gate
passing did not rescue any arm, because the arms it was supposed to protect against were already
behind the baseline.

**Decision: rejected, all eight arms.** Note that the wide-panel arm does cut wrong calls sharply
(−52,229) while its correct count rises modestly (+15,160). A reader who values "fewer wrong answers"
over "more answered cells" may find that trade acceptable. We did not adopt it, because it failed the
gate that was set before the measurement and because the gain does not hold across datasets.

## What we take away

1. **A gain on the corpus that shaped the design is not evidence of a gain.** The widening mechanism
   showed +0.90pp on 28 datasets and exactly 0 on the 29th. The second number is the one that predicts
   what a new user will see.
2. **Abstention is carrying information, not hiding failure.** Both studies independently say the same
   thing: where the service declines to name a class, the evidence really is thin. Suppressing
   abstention moves cells from "no answer" to "wrong answer" rather than to "right answer".
3. **Tie-breaking and admission tuning are the wrong places to look for improvements.** They were the
   two most obvious parameter knobs, and both were measurably negative or insufficient.
4. **What has not been tested.** The marker panels themselves. The failures above are all about how
   candidates are ranked and admitted, not about what the library contains. Extending the panel
   content, with independent literature support, remains untested — but it has to come from sources
   other than an evaluation corpus, or it reproduces the same mistake in a new place.

## Reporting these results

If you cite the system's performance, report the abstention rate alongside the correct rate, and say
on which corpus the number was measured. A correct rate quoted without its abstention rate is not
comparable between versions, because the two can be traded against each other — the wide-panel arm
above raises correct calls while leaving 64,000 more cells unanswered.

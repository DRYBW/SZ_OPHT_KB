# Report format standard

This file defines the layout every EyeKB result report must follow, and the machine check that enforces it. Copy the structure below into a new report, replace the bracketed slots, and drop the sections that do not apply. Do not change the heading levels or the paragraph rules. Run the checker before the report leaves the machine; the checker itself is the specification, so an argument about formatting is settled by a command rather than by opinion.

| Item | Content |
|---|---|
| Report | EyeKB [scope] result report |
| Version | v[major.minor] |
| Date | [YYYY-MM-DD] |
| Measurement basis | [e.g. cell-level annotation, exact CL match, cell-count weighted] |
| Audience | [management / colleagues / client / internal technical review] |
| Data basis | [volumes, clusters, cells, ground-truth source] |
| Headline | [the single most important sentence, with a number] |

## Executive summary

Written for the reader who stops after page one. The first paragraph says what the system is and which step of the workflow it serves. The second paragraph gives the three headline numbers, all in bold. The third paragraph states the boundary: which conclusions cannot be drawn from this report.

The three fixed numbers are **correct rate**, **wrong rate** and **abstention rate**, each with a one-line note on how it is computed. Correct means the predicted cell type matches the author-annotated CL term exactly; abstention means the system deliberately answers nothing. The three numbers must come from one re-runnable result file and must never be assembled across batches.

## One. Positioning and deliberate non-goals

This section keeps the reader from over-reading the system. The first paragraph states which step of the annotation workflow the system covers, what it takes in and what it returns. The second paragraph lists what the system explicitly does not do: it does not replace final human review, does not make diagnoses, and does not produce usable conclusions for tissues it has never seen.

Include a boundary table with capabilities on the left and the evidence or limit on the right. Every **capability row** must point at a file or a section number.

## Two. Components and ownership

This section answers what the system is made of and who maintains each part. Include an ownership table with four columns: component, responsibility, principal files, current state. The components must at minimum cover the marker knowledge base, the retrieval layer, the knowledge pages, the annotation pipeline, the model service interface and the ledger.

Follow the table with one paragraph on the data flow between components, enough that a reader can sketch the architecture. No **component row** may leave the state column empty; unfinished work is written as unfinished and tagged with the section where it is tracked.

## Three. Knowledge coverage

This section states which tissues and cell types the knowledge base covers and where coverage stops. Include a per-tissue matrix with columns for cell types, marker genes, evidence entries and coverage state.

Coverage state takes exactly three values: covered, partially covered, declared gap. A tissue declared as a gap needs its own paragraph explaining why, and an explicit statement that results from that tissue must not be published as annotation output. For **[gap tissues]** the reason must distinguish a missing vocabulary entry, a thin marker panel and an ontology level that does not line up.

## Four. Measured annotation performance

This section carries the protocol and the numbers. The first paragraph states the protocol before any result appears: dataset source, cluster count, cell count, ground-truth basis, weighting, and how abstentions are counted. The protocol precedes the numbers so the reader cannot misread them.

Present results in a comparison table with at least two arms, for example before and after a change. Every percentage carries its numerator and denominator scale. A **change in correct rate** must be shown as an absolute figure and as percentage points, together with whether it reproduced in a held-out validation.

## Five. Abstention account

This section explains, on its own, why the system declines to answer. Abstention splits into two causes: no candidate reached the minimum evidence threshold, or a candidate existed but the evidence was too thin and was given up deliberately. The two have different meanings, the first indicating a gap in the vocabulary and the second a thin marker panel.

Include a per-tissue abstention breakdown with columns for tissue, cells, abstention rate, share with no candidate and share with insufficient evidence. Where the **[insufficient-evidence share]** is high, state whether the cause is a narrow marker panel or an ontology level that cannot be aligned.

## Six. Versions and parameters

This section states which parameter versions are available and what each one is for. Give each version a paragraph: parameter values, design intent, tissues where it helps, and what may not be claimed for it. Never present a single version without its comparison arm, and never present a fitted value as a capability value.

Include a version table with columns for version, parameter keys, correct, wrong, abstention, whether held-out validation reproduced, and intended use. The **[recommended version]** must be labelled as global or per-tissue, and per-tissue settings must carry the caveat that tissues with a single volume cannot be validated.

## Seven. Engineering credibility

This section states why the system can be trusted. Cover the gate chain, the negative-test battery, the rollback switch and byte-level equivalence, and the registered anchors. Each item names a command or a script path that reproduces it.

Include a verification table with columns for item, criterion, measured result and reproduction command. **Gate results** and negative-test results are written as fractions; anything that did not pass is written as not passed, and passing items alone are never reported.

## Eight. Review status and open items

This section discloses the external review outcome and the authority under which the current default is active. Where a default is live without a signed review, the text must say that this is a project-owner decision and not a review pass.

List the open items in a table with columns for item, impact, current state and who decides. **Open items** are never trimmed for presentation, including governance conditions raised by reviewers.

## Nine. Gaps and next steps

This section states what happens next and why that order. Each route carries a goal, a criterion, an owner and a stop condition. Routes without a criterion are not listed.

Include a route table with columns for route, target metric, current baseline, criterion and state. The **[first route]** explains the trade-off against the others and names the action taken if its criterion fails.

## Ten. Reproduction

This section lets a third party obtain the same result. Cover the runtime environment, dependency versions, how the data is obtained, the key checksums, and the treatment of absolute paths and randomness.

Code blocks may be pasted and executed directly; inside them indentation and lists are allowed. Give at least one **file-level md5** and one **anchor value**, and name the script that compares the anchor.

## Data appendix

Appendices follow the body and contain tables only, with no argument. Each table carries a number, a title, and column headers with units.

### Table one [name]

| [header] | [header] | [header] |
|---|---|---|
| [value] | [value] | [value] |

### Table two [name]

| [header] | [header] | [header] |
|---|---|---|
| [value] | [value] | [value] |

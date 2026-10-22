# PRE-REGISTRATION — per-parent subdivision-readiness audit (EyeKB, wave `subdivision_readiness_20261022`)

Written: **2026-10-22 10:12 CST (2026-10-22T02:12Z)** · Author: pi-chief (kanban task `t_74ef13aa`)
Binding upstream ruling: `/mnt/D/EyeKB/plans/sol_design_20261021/SOL_DESIGN_OUT_20261021.md` block C (§C1–C5) and the
two engineering rulings (§"两项工程裁决"). Where this file and any earlier wording of the card disagree, the ruling wins.
Price table built on, not re-derived: `/mnt/D/EyeKB/plans/holefill_v12_20261021/REPORT.md §5`,
`out/taskb_subtypes.json`, `out/taskb_class_depth.json`, `out/taskb_child_support.json`.

## 0. What existed on disk when this file was written (disclosure)

| artefact | mtime | contains |
|---|---|---|
| `out/R0_ontology_snapshot.json` | 2026-10-22 10:10:36 | fixed CL snapshot path, sha256, release string, term count |
| `out/R1R2_parent_depth.json` | 2026-10-22 10:10:36 | per-parent `is_a` descendant count and resolvable child-name count (field 1 — a mechanical closure count) |
| `out/R3_volume_provenance.json` | 2026-10-22 10:10:36 | the 28 evaluation volumes' species/tissue/derivation |
| `out/R4_machine_expression_inventory.json` | 2026-10-22 10:10:40 | expression-like files on this machine |

**Disclosed honestly**: field 1 (ontology depth) had been counted before this file. It is a closure count over the
ontology, carries no judgement, and no threshold below was set with reference to it. Fields 2–7, the tier rules, the
cost measure and the confusion-pair package had **not** been measured in any form when the thresholds below were fixed.

## 1. Scope and unit of measurement

* **Row unit**: one row per class the dictionary ships — 76 dictionary labels in
  `kb/markers/markers_cl_alignment_v2_unified.json` (`labels`, 76 entries; 49 distinct CL ids; 15 labels carry no CL id).
* **Readiness unit**: the **(parent, candidate child) pair**. A parent row aggregates its pairs.
* **Candidate child names** are taken **only** from the fixed Cell Ontology snapshot (the preferred names of the
  parent's `is_a` descendants). No candidate class name and no panel gene is taken from the reference labels of the
  evaluation volumes. The gap report may only *trigger* an audit (ruling §D2 第一道).
* **Target context** is declared per parent before measurement and never widened after seeing a result:

| axis | declaration |
|---|---|
| species | `human`; a mouse reading is recorded for information only and never substitutes for the human reading |
| tissue | the tissue set of the parent's own marker library as declared in the dictionary's `libraries` block, mapped through `kb/baselines/*` tissue names |
| stage | `adult` by default; `fetal_developing` for labels whose own token or library is developmental (`*_precursor`, `*_fetal`, `RPC_*`, `NRPC_*`, `TAC_proliferating`, `Proliferating`, `Retinal_Proliferating`) |
| system | `in_vivo` by default; `organoid_or_ipsc` for labels whose library declares an iPSC/organoid context |

## 2. Pre-registered thresholds (conservative release thresholds, **not biological laws**; they do not move after results)

| id | threshold | source |
|---|---|---|
| **T-GENES** | ≥ **2** discriminating positive genes against the nearest sibling | ruling §C1 |
| **T-SOURCES** | ≥ **2** independent evidence sources, of which ≥ **1** supplies an **adjacent-type contrast** | ruling §C1 |
| **T-CONTEXT** | species / tissue / stage / system explicitly declared and satisfied by the source | ruling §C1 |
| **T-NONEG** | no inference from "not in the top-10"; absence from a recorded window is never negative evidence | ruling §C1, §A2 |
| **T-OBS** | ≥ **2** discriminating positive genes observable inside the shipped top-marker window (top-10 of the recorded interface input) | ruling §C1 "当前输入是否能观察" |
| **T-STATE** | fraction of the child's discriminating positive genes that belong to a state programme (disease / cell-cycle / treatment) **< 0.50** | ruling §C1 "是否依赖疾病、细胞周期或处理状态" |
| **T-MATERIAL** | ≥ 1 independent, **non-evaluation** local material carrying the child term | ruling §C1 |

Counters used by these thresholds, fixed here:

* **independent study** = a distinct `paper_id` in the discovery corpus. Chunks, rows and literature blocks are **not**
  studies and are never counted as such (ruling §C1 "按研究／队列去重，不能按文献块计数").
* **independent cohort** = a distinct local dataset/cohort outside the evaluation set.
* **independent source** = one study **or** one cohort; the two are reported separately and never summed twice.
* **adjacent-type contrast** = a single source in which the child name and at least one sibling name of the same parent
  co-occur with explicit contrast language. Same-paper duplicate chunks do not add.
* **positive gene** = a gene annotated as a marker by ≥ 2 distinct studies in the child's own corpus slice, in the
  declared target context. A gene that is positive for the parent across its children is a **parent-shared** gene and
  is removed from every child's evidence before any of the thresholds above is applied (ruling §C2: 父类共有基因不得复制给子类).
* **discriminating positive gene** = a positive gene of child *c* that is not positive for its nearest sibling *s* and
  is not parent-shared.

## 3. Pre-registered tiers (ruling §C4)

```
T1  subdivision_available_now
      child name resolves in the fixed snapshot
      AND T-CONTEXT satisfied
      AND T-SOURCES satisfied (≥2 sources, ≥1 adjacent-type contrast)
      AND T-GENES satisfied (≥2 discriminating positive genes, parent-shared removed)
      AND T-STATE satisfied
      AND T-OBS satisfied
      AND T-MATERIAL satisfied
T1k knowledge_subdividable_only
      every T1 clause satisfied EXCEPT T-MATERIAL  (ruling §C1: 本地只有文献而无独立表达材料 ⇒ 只能判"知识上可细分")
T2  needs_parent_panel_deepened
      child name resolves AND T-CONTEXT satisfied
      AND at least one of {T-GENES, T-OBS, T-STATE} fails
      AND the failure is attributable to thin evidence rather than to the ontology or to the interface's reach
T3  not_subdividable   with exactly one reason from the fixed enum:
      ontology_thin | leaf_term | no_target_context_occurrence | spectrum_only
      | state_programme_only | interface_cannot_observe | no_ontology_term
```

Reason enum is fixed here and may not gain a member after results are seen. A parent with several candidate children
reports its **best** tier plus the full per-child distribution; a parent whose every candidate child is T3 with at
least one `no_target_context_occurrence` is itself T3.

## 4. Pre-registered output shape (ruling §C2)

```text
parent_candidates              parent-level candidates, ALWAYS preserved
subtype_suggestions_by_parent  children that cleared T1/T1k, competing ONLY inside their own parent branch
resolution_status              one of: parent_only | subtype_suggested | subtype_ambiguous | parent_abstain
review_reasons                 machine-readable reasons, never prose-only
```

Fixed mapping tier → `resolution_status`, and the rules that go with it:

| situation | status |
|---|---|
| no candidate child clears T1/T1k | `parent_only` — a legitimate output, not a failure |
| exactly one child clears T1/T1k | `subtype_suggested` |
| ≥ 2 children clear T1/T1k **and** their discriminating-positive-gene sets overlap ≥ 0.50 pairwise | `subtype_ambiguous` — both are kept, no winner is chosen |
| the parent itself has no resolvable ontology term | `parent_abstain` |

**Invariants (checked mechanically, dropped to zero if violated):**
1. parent results are always present in the emission;
2. subtypes compete only inside their own parent branch — never globally (ruling §③ "全局平铺所有子类" is cut);
3. **no automatic final label is ever emitted**; the emission stops at a suggestion with its reasons;
4. a parent's shared genes never appear in any child's evidence block;
5. no child enters the emission on fewer than 2 discriminating positive genes (single-gene admission = 0);
6. no child enters the emission on parent-shared genes alone (count = 0);
7. nothing is activated: no whitelist entry, no default-route change, and the recorded 721-cluster rankings replay
   byte-identically (proved, not argued).

## 5. Pre-registered cost measure (card item 6; ruling §A4.6, holefill §5 as the model)

On the recorded 721-cluster set, per (parent, candidate child):

| quantity | definition |
|---|---|
| `demand_clusters` / `demand_cells` | clusters whose fixed reference is the child |
| `gain_clusters` | demand clusters that reach ≥ 2 shared genes with the child panel while the parent panel does not |
| `keep_clusters` | clusters the parent answers today that the child panel would still reach |
| `loss_clusters` | clusters the parent answers today that the child panel would **lose** if it replaced the parent |

These are **probing/regression readings on a fixed set of 28 recorded volumes against a fixed reference** — they are
not validation, and the fixed reference is never described as an automatic gold standard (ruling §5, last paragraph).

## 6. Pre-registered confusion-pair package (card item 5; ruling §D4)

For each measured confusion pair (the measured instance is RPE vs melanocyte), six elements, in this order:
① shared support; ② positive evidence that discriminates; ③ which changes are state programmes; ④ which distinctions
need information this interface does not have; ⑤ when several candidates must be kept; ⑥ when abstention is required.
**A thicker positive panel is not an answer to a confusion pair** and is not emitted as one.

## 7. Pre-registered red lines (restated, mechanised)

1. the frozen report's pre-existing bytes hash to the recorded sha256 after the append; the line diff shows added lines only;
2. zero downloads, zero network — an audit hook is installed and the receipt is `hooks_loaded > 0, network_events = 0`;
3. discovery-source set and evaluation-source set are separated by study and by cohort, with the overlap reported;
4. `NOT_RUN` and missing preconditions are reported as `NOT_RUN`, never as pass;
5. every number in the deliverable carries the command that produced it.

## 8. What would make this audit invalid (declared in advance)

* any candidate child name traced to a reference label of an evaluation volume → the wave is void;
* any threshold in §2 moved after results were seen → the wave is void;
* any emission containing an automatic final label, or a parent's shared genes presented as child evidence → void;
* the default route differing on any of the 721 recorded rankings → the wave is void.
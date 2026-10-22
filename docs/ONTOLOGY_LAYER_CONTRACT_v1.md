# The Cell Ontology explanation layer (read-only, registered OFF by default)

This document is the contract for one capability of the EyeKB service: a read-only layer that
navigates the Cell Ontology instead of looking a label up in it. It states what the capability is,
what it will not do, how it is reached, and how the claims about it can be checked from a clone.

Status of this revision: **registered, OFF by default, nothing activated.** The layer is reachable
only by explicit routing, and every measurement in the card that delivered it was taken with the
route unset.

Source of the requirement: the design ruling `SOL_DESIGN_OUT_20261021.md`, block A (the ontology as
a navigable explanation layer) and the two engineering rulings (the three-state gate; release
identity in four layers bound to an immutable manifest).

---

## 1. What it answers

Four functions, all read-only, all deterministic, all answered from **one fixed snapshot**:

| function | question | answer carries |
|---|---|---|
| `resolve_term` | which CL term is this, and how sure is that resolution? | canonical id, preferred label, obsolete status, resolution status and method, candidates, unresolved reason |
| `get_ancestors` | what does the `is_a` graph say is above it? | every ancestor with levels above, the shortest path, the line of the ontology file, and whether it is a blanket ancestor |
| `compare_terms` | how do two terms relate, and how far may that be used? | the five-bucket verdict, `is_a_relation`, `ancestor_path`, `unresolved_reason`, and a separate `assessment` |
| `explain_class_mapping` | what backs the mapping this library ships for one class? | the shipped mapping and its source hash, the graph facts behind it, and an assessment |

Two records that are never collapsed:

- **`is_a_relation`** — what the graph says: `same_canonical_term`, `ours_is_ancestor_of_theirs`,
  `theirs_is_ancestor_of_ours`, `no_ancestor_relation`, `unresolved`.
- **`assessment`** — whether the answer holds under this sample, this task granularity and this
  evidence: `not_assessed`, `supported`, `resolution_limited`, `evidence_insufficient`, `unmapped`,
  `under_review`, `incompatible`.

A parent-child relation is not by itself a correct answer, and both records are returned side by
side on every comparison.

## 2. The five report buckets

| bucket | when | how it may be used |
|---|---|---|
| `same_term` | canonically the same CL term (a naming difference only) | agreement |
| `ours_broader` | our term is an ancestor of the reference term | a coarser answer: a **resolution limitation**, not a biological error |
| `ours_narrower` | the reference term is an ancestor of ours | the extra resolution is unverified and earns nothing |
| `confirmed_incompatible` | only when the caller supplies explicit incompatibility evidence, which is recorded verbatim with the verdict | a confirmed error |
| `not_supported_by_is_a` | no ancestor relation in either direction, or one side unmapped | **neither** correct **nor** a confirmed error |

"No ancestor relation" is not proof of biological mutual exclusion: multiple inheritance, an
incomplete ontology and cross-classification all produce it. A shared ancestor is not equivalence.
An extremely broad ("blanket") ancestor cannot carry an answer: a relation that only reaches one is
reported as below the minimum reporting granularity (`blanket_ancestor_descendants = 200` active CL
descendants, declared in the registry before any comparison was run, and not moved afterwards).

## 3. Three tables, never one lenient accuracy

The comparison is reported as three separate tables over a fixed denominator:

1. **same-term agreement** — canonical equality only.
2. **granularity relation** — coarser / finer / levels crossed, with the below-minimum-reporting-
   granularity count kept separate.
3. **task validity** — context recorded, minimum reporting granularity met, evidence sufficient,
   still under review.

No table blends them into a single accuracy figure. Nothing is removed from a denominator for having
no answer, and `not_supported_by_is_a` is counted as neither correct nor a confirmed error
(mechanically: `counts_as_correct` and `counts_as_confirmed_error` are columns).

## 4. The fixed snapshot and its anchors

Everything is read from one release, addressed by a **logical address** resolved through a versioned
manifest, with the content hash verified before any answer is produced:

```
ont://cl/releases/2026-06-08            the Cell Ontology snapshot   (kb/ontology/cl/releases/2026-06-08/cl-base.obo)
repo://kb/ontology/ONT_LAYER_REGISTRY_v1.json      the registration record of this capability
repo://kb/markers/markers_cl_alignment_v2_unified.json   the shipped class-to-CL mapping
```

No file in the repository carries an author-machine absolute path, and the layer resolves the
repository root from its own location, so a clone answers without configuration.

Failure policy (declared in the registry, and enforced by the gates):

| state | verdict |
|---|---|
| `ANCHOR_MISSING` — a mandatory shipped asset is absent | **FAIL** (a delivery defect) |
| `ANCHOR_HASH_MISMATCH` — bytes are not the recorded bytes | **FAIL** |
| `ANCHOR_UNKNOWN` — an address the manifest does not list | **FAIL** |
| `MANIFEST_MISSING` | **FAIL** |
| `ENV_ERROR` | reserved for a declared external precondition that is genuinely outside the delivery |

A missing shipped asset is never reported as an environment error, and the layer never answers from
a placeholder.

## 5. How it is reached (and how the default surface is protected)

```
EYEKB_ONT_LAYER=resolve_term,compare_terms        # exactly the tools named, nothing else
```

- **Unset or empty** — nothing is advertised, the ontology module is not even imported, and the
  advertised tool list and every existing answer are byte-identical to the release before this
  capability existed. There is no whitelist entry by default: the list is empty.
- **Set** — exactly the named tools are registered and advertised.

The legacy tool panel (`tests/probe_tool_panel_identity.py`) is the repository's byte-identity
guarantee and is unchanged: `legacy_panel` and `full_panel` are identical before and after this
change. The one call that does move is `get_release_identity`, which is the explicit identity
interface and now carries the four release-identity layers; that move is stated, not hidden (see
§6).

## 6. Release identity in four layers

| layer | what it describes |
|---|---|
| `protocol_generation` | the wire contract (read from the server that carries it) |
| `service_build_id` | the shipped server code |
| `knowledge_bundle_id` | the shipped knowledge assets (`kb/`, `literature_db/`) |
| `effective_profile_id` | what actually took effect: the observed toggle values, the registered capabilities and their state, and the layer identities — with volatile fields excluded, so the same configuration gives the same value on any day |

`release_id` is bound to an immutable manifest: `docs/RELEASE_MANIFEST_v1.json` lists every tracked
file with its blob id and size, and `release_id` is the sha256 of that listing. Recompute the
listing, recompute the hash, compare — the value and the manifest cannot drift apart. Two independent
commands report it: `python3 scripts/release_identity.py --check` and the `get_release_identity`
tool.

## 7. How to check the claims from a clone

```
python3 tests/gate_ontology_layer.py --service-python <interpreter with the MCP SDK>
python3 tests/gate_ontlayer_portability.py
bash tests/run_gates.sh          # G3, G4, G5, G6, G7, G8 with a chain summary
python3 mcp_server/ontology_layer.py            # the snapshot's own parse summary
python3 kb/ontology/scripts/build_ont_manifest.py   # verify the recorded hashes
```

Both gates report `should_run` / `did_run` / `pass` / `fail` / `not_run` and end in exactly one of
PASS / FAIL / ENV_ERROR; a gate does not pass while any mandatory check did not execute. None of
these reads the data-mount evidence root, and none of them needs the network.

## 8. Stop line

The layer will not:

- modify ontology semantics;
- prefer a favourable synonym, or resolve an ambiguity to raise agreement;
- let an extremely broad ancestor blanket an answer;
- reduce unmapped counts or raise agreement by any of the above.

An ambiguous synonym, an obsolete term with more than one replacement, and the same label on two
terms all come back as `ambiguous` / for review, with the candidates listed.

## 9. What this capability does not do

- It does not raise identification ability. It corrects how a comparison is worded and how far an
  answer may be used, and it is reported as such. Ontology agreement rising is not recognition
  rising.
- It does not replace the four-stage annotation protocol, and its output is not an input to any
  score, weighting, ranking or confidence measure (the service red line, unchanged).
- It can only say what this one snapshot contains. An ancestor relation that the snapshot does not
  carry is reported as unknown, never inferred.
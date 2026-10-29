# Tool-surface usability pass 2: measurements

Executed 2026-10-29 (the directory name keeps the date the card was opened).

Date 2026-10-22. Method: `shipped-service-usability-audit`, three measurable axes
(description cost, response size, latency), measured with the real stdio server.

Probe: `ux_probe.py`, same absolute repo path in every run.
Readings: `out/UX_BEFORE.json`, `out/UX_AFTER2.json`.

## 1. Baseline before this pass

| axis | reading |
|---|---|
| tools exposed | 7 |
| description characters (paid every conversation) | **8,815** (~2,203 tokens) |
| `search_literature` | p50 700.2 ms, 14,550 chars |
| `get_kb_page(scope=index)` | p50 4.6 ms, **140,005 chars** |
| `get_tissue_composition(human, retina)` | p50 13.1 ms, **91,332 chars** |
| `get_disease_prior(...)` | p50 9.9 ms, 18,711 chars |

The two large responses are the real ergonomic problem: a single call to
`get_kb_page(scope="index")` puts 140,000 characters into the caller's context.

## 2. What the switches could already do

Measured directly, before any change:

| call | characters | ratio |
|---|---|---|
| `get_kb_page(scope="index")` | 139,995 | — |
| `get_kb_page(scope="index", summary=True)` | **2,841** | **49×** smaller |
| `get_tissue_composition("human","retina", detail="full")` | 57,030 | — |
| `get_tissue_composition("human","retina", detail="answer")` | 19,816 | 2.9× smaller |

So the lever existed. Two things stopped a caller from finding it:

1. The two tools used **different field names for the same choice** — `summary` (bool)
   on `get_kb_page` versus `detail` (string) on `get_tissue_composition`. A caller who
   learned one habit got it wrong on the other tool.
2. The size warning sat in the **second paragraph** of the description, after the
   enumeration of scopes.

## 3. What changed

One change, `mcp_server/server.py`, `get_kb_page` only:

* new `detail` parameter taking the same values as `get_tissue_composition`
  (`"full"` / `"answer"`); empty default means **behaviour is decided by `summary`
  exactly as before**;
* `summary` still works unchanged; an explicit `detail` wins if the two disagree;
* the description now leads with the size and states the one-field-name-for-both-tools
  rule;
* `get_tissue_composition`'s description was compressed: the development-stage literal
  resolution rules were reduced to the one sentence a caller needs, and the size of
  each tier is now stated (91,000 → about 20,000).

## 4. After

| axis | before | after | delta |
|---|---|---|---|
| description characters | 8,815 | **8,613** | **−202** (−50 tokens/conversation) |
| `get_kb_page` description | 745 | 1,027 | +282 (it now documents the size and both switches) |
| `get_tissue_composition` description | 1,907 | 1,423 | **−484** |
| `get_kb_page(scope=index)` response | 140,005 | **140,005** | unchanged |
| `get_tissue_composition` response | 91,332 | **91,332** | unchanged |
| `search_literature` response | 14,550 | **14,550** | unchanged |
| `get_disease_prior` response | 18,711 | **18,711** | unchanged |

All four response sizes are byte-identical, which is the evidence that the default
path did not move.

Equivalence of the wrapper, checked separately against the core function it wraps
(md5 of the response, `detail` unspecified):

| call | identical to core |
|---|---|
| `scope="index"` | yes |
| `scope="index", summary=True` | yes |
| `scope="tissue", name="cornea"` | yes |

New alias behaves as specified: `detail="answer"` → 2,841 chars; `detail="full"` →
139,995; `summary=True, detail="full"` → 139,995 (explicit detail wins);
`summary=False, detail="answer"` → 2,841.

## 5. Latency: not reportable from this run

The latency column in `UX_AFTER2.json` is **unusable**. Between the two probe runs the
machine's load average went from 2.5 to **182** (1-minute), because another session is
running `s53_mouse_degree.py` under the `eyescgpt` environment with a loky worker pool.
That work belongs to a different project line and was left alone.

Evidence: `p50` for `search_literature` moved 700.2 → 1,285.0 ms and for
`get_tissue_composition` 13.1 → 38.6 ms while the response bytes did not change at all,
which is the signature of host contention rather than a code regression. Latency must be
re-measured on an idle machine before any claim is made.

## 6. What is left, ordered by payoff

| # | item | reading | needs |
|---|---|---|---|
| 1 | the default tier is still the heavy one: `get_kb_page` 140 KB, `get_tissue_composition` 91 KB | 49× / 2.9× available from a switch nobody flips by default | decision: changing a default moves the frozen response bytes, so it needs a card of its own |
| 2 | a single tissue page is 41,920 chars | no mid tier between "one row" and "whole page" | design |
| 3 | the `answer` tier of `get_tissue_composition` stops at 19,816 chars | most of the remainder is per-row provenance | design: any further cut must keep per-row citations or say what it dropped |
| 4 | latency | not measured under load | re-measure when idle |

Item 1 is where the experience actually is. Everything else in this pass was making the
existing levers discoverable; item 1 is about whether the lever should be the default.

## Reproduction

```
EYEKB_REPO_ROOT=/home/ubuntu/EYEKB_REPO \
UX_PY=/home/ubuntu/.conda/envs/pipeline_env/bin/python \
python ux_probe.py --out <this dir>/out/UX_AFTER2.json
```
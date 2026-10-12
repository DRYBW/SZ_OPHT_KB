#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB pipeline — volume plausibility gate (X4B-FIX F2, card t_95015c8a).

Pre-registration = /mnt/D/EyeKB/plans/x4b_fix_20261012/PREREG_X4BFIX.md §2 (pure arithmetic,
no tuning). Criterion: a cluster whose current first candidate is type t and whose size is n_c
is rejected when n_c > N_t, where N_t is the same-volume interpreted/predicted total for t;
the cascade re-checks the following candidates; if every candidate is rejected the cluster
abstains with flag volume_gate_reject.

N_t source priority (frozen):
  (1) caller-provided JSON dict {interpretation-label: cell count} (--volume-counts) — the
      whole-volume per-cell interpretation/prediction marginal the caller holds (e.g. a model
      layer's per-cell counts, or the curation marginal in the X4B replication drill);
  (2) default (no input): the gate is STRUCTURALLY INERT and emits no section at all (zero
      artifact drift; the inertness contract lives in docs, not per-run output — a per-run
      header note would itself be drift). Documented in REPORT_X4BFIX as designed.

Name matching = exact string lookup of the candidate name in the caller dict; a candidate
whose key is missing from the dict can never be rejected by arithmetic (recorded under
"misses" instead of a veto).

Global rollback: env EYEKB_STATE_GUARD ∈ {0,false,off,no} (strip+casefold) = OFF: the gate is
entirely inert even when --volume-counts is provided (one-time stderr note, no artifact bytes).
Module naming drilled against the S0 T4 firewall sentinel substrings (pitfall/consume/known_issue).
"""
import os
import sys

_WARNED = {"off": False}


def enabled():
    """env EYEKB_STATE_GUARD ∈ {0,false,off,no} (casefold) = OFF rollback; unset/other = ON."""
    v = (os.environ.get("EYEKB_STATE_GUARD") or "").strip().casefold()
    return v not in {"0", "false", "off", "no"}


def warn_guard_off():
    """Called by the entry point when --volume-counts is passed but the guard is OFF."""
    if not _WARNED["off"]:
        sys.stderr.write("[volume-gate] EYEKB_STATE_GUARD=OFF -> --volume-counts ignored "
                         "(pre-wiring behavior; gate inert)\n")
        _WARNED["off"] = True


def apply_volume_gate(names, n_c, counts):
    """Cascade over the ranked candidate names (order preserved).

    Returns (kept, rejected, misses):
      kept     — candidates not vetoed (lookup-miss candidates are kept, never vetoed);
      rejected — [{"candidate", "n_c", "N_t"}] for every arithmetic veto;
      misses   — candidate names absent from counts (kept, recorded for the section).
    kept == [] and names != []  ->  full rejection -> ABSTAIN(volume_gate)."""
    kept, rejected, misses = [], [], []
    for t in names:
        if not t:
            continue
        n_t = counts.get(t)
        if n_t is None:
            misses.append(t)
            kept.append(t)
            continue
        if n_c > int(n_t):
            rejected.append({"candidate": t, "n_c": int(n_c), "N_t": int(n_t)})
            continue
        kept.append(t)
    return kept, rejected, misses

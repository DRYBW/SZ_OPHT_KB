#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L2 query-budget door — env EYEKB_L2_BUDGET, plus the judged-path default.

The per-cluster query budget is decided in this order:

1. an explicit `--top-genes-n` value — always wins, never rewritten;
2. otherwise `EYEKB_L2_BUDGET`, when it is set:
     ON  (1 / true / on / yes)              => 30
     OFF ("" / 0 / false / off / no)        => 10
     unknown token                          => 10 + one stderr warning per process
3. otherwise the caller decides:
     judged path (the optional second answer is enabled) => 30
     plain path                                          => 10

Why the judged path defaults to 30 (2026-10-29, card `plans/l2_budget_default_on_20261029`):
measured on the 25-volume corpus, a judge reading a 30-gene evidence panel answered 75.06 %
top-1 against 66.91 % on a 10-gene panel (+8.15 pp), coverage 75.38 % vs 68.04 %, and the
accuracy over committed answers did not fall (81.70 -> 82.20 %). Panel width does not move the
library's own candidate ranking — measured 11 of 11 clusters identical on the G4 fixture — so
widening the plain path would cost calls and report size and buy nothing. The width therefore
follows the judge, not the whole pipeline, and default output stays byte-identical.

Rollback: EYEKB_L2_BUDGET=0 forces 10 everywhere, judged path included (CARD.md §3).
"""
from __future__ import annotations

import os
import sys

ENV = "EYEKB_L2_BUDGET"
OFF_TOKENS = set("0 false off no".split())
ON_TOKENS = set("1 true on yes".split())
JUDGED_DEFAULT_N = 30
PLAIN_DEFAULT_N = 10
_UNSET = None
_warned = False


def _door():
    """Return True (on), False (off) or None (unset) for EYEKB_L2_BUDGET."""
    global _warned
    raw = os.environ.get(ENV)
    if raw is None:
        return _UNSET
    token = str(raw).strip().lower()
    if token in ON_TOKENS:
        return True
    if token in OFF_TOKENS:
        return False
    if not _warned:
        _warned = True
        print("[l2_budget] WARNING: unknown %s=%r -> fail-closed to OFF (legacy %d)"
              % (ENV, raw, PLAIN_DEFAULT_N), file=sys.stderr)
    return False


def enabled() -> bool:
    """True only when the door is explicitly switched on."""
    return _door() is True


def default_n(judge: bool = False) -> int:
    """Budget when the caller supplied no explicit value."""
    state = _door()
    if state is True:
        return JUDGED_DEFAULT_N
    if state is False:
        return PLAIN_DEFAULT_N
    return JUDGED_DEFAULT_N if judge else PLAIN_DEFAULT_N


def resolve(explicit, judge: bool = False):
    """CLI value -> effective value.

    An explicit value always wins. The door is evaluated FIRST so that an unknown /
    illegal EYEKB_L2_BUDGET token is warned about even when an explicit --top-genes-n is
    supplied; the explicit value is never rewritten. Warning at most once per process.
    """
    n = default_n(judge=judge)   # evaluates the door; warns once on an unrecognised token
    return n if explicit is None else int(explicit)
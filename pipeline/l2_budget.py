#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""[Q5 t_44fc8efe] L2 query-budget door — env EYEKB_L2_BUDGET.

OFF (unset / "" / 0 / false / off / no) => default 10 (legacy, byte-identical to pre-wiring).
ON  (1 / true / on / yes)              => default 30.
Unknown value => fail-closed to OFF + one stderr warning per process (a typo must never change behaviour).
The door decides the *default* only: an explicit --top-genes-n value is never rewritten, but the door
is still evaluated so an illegal token is warned about even when an explicit value is supplied.
Rollback = unset the env var (see PREREG_L2_BUDGET_v1.md §4).
"""
from __future__ import annotations

import os
import sys

ENV = "EYEKB_L2_BUDGET"
OFF_TOKENS = {"", "0", "false", "off", "no"}
ON_TOKENS = {"1", "true", "on", "yes"}
NEW_DEFAULT_N = 30
LEGACY_DEFAULT_N = 10
_warned = False


def enabled() -> bool:
    global _warned
    raw = str(os.environ.get(ENV, "")).strip().lower()
    if raw in ON_TOKENS:
        return True
    if raw in OFF_TOKENS:
        return False
    if not _warned:
        _warned = True
        print("[l2_budget] WARNING: unknown %s=%r -> fail-closed to OFF (legacy)" % (ENV, raw),
              file=sys.stderr)
    return False


def default_n() -> int:
    return NEW_DEFAULT_N if enabled() else LEGACY_DEFAULT_N


def resolve(explicit):
    """CLI value -> effective value.

    An explicit value always wins. The door is evaluated FIRST so that an unknown /
    illegal EYEKB_L2_BUDGET token is warned about (fail-closed to OFF) even when an
    explicit --top-genes-n is supplied; the explicit value is never rewritten.
    Warning is emitted at most once per process.
    """
    n = default_n()  # evaluates the door; emits the fail-closed warning if the token is illegal
    return n if explicit is None else int(explicit)

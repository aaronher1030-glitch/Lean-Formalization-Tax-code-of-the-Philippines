# -*- coding: utf-8 -*-
"""Independent Python ground truth for the findings battery.

Re-implements the verified Lean core in Python. This module supplies witness
inputs and expected values; it never decides what Lean proves. The kernel
judges every proposition the battery generates.
"""

STATUTE = [
    (25_000_000, 40_000_000, 15),
    (40_000_000, 80_000_000, 20),
    (80_000_000, 200_000_000, 25),
    (200_000_000, 800_000_000, 30),
    (800_000_000, None, 35),
]
VAT_THRESHOLD = 300_000_000
TIERS = ("micro", "small", "medium", "large")


def bracket_tax(t):
    total = 0
    for lo, hi, rate in STATUTE:
        if t <= lo:
            break
        base = (min(t, hi) - lo) if hi is not None else (t - lo)
        total += base * rate // 100
    return total


def pct_tax(gs):
    return gs * 3 // 100


def tax8(gs):
    return max(gs - 25_000_000, 0) * 8 // 100


def classify(gs):
    if gs < 300_000_000:
        return "micro"
    if gs < 2_000_000_000:
        return "small"
    if gs < 100_000_000_000:
        return "medium"
    return "large"


def rates(tier):
    return (10, 6) if tier in ("micro", "small") else (25, 12)


def eligible(gs):
    return gs <= VAT_THRESHOLD


def regime_of(gs, elected):
    return "eight" if elected and eligible(gs) else "graduated"


def surcharge_t(tier, t):
    return t * rates(tier)[0] // 100


def interest_t(tier, t, days):
    return t * rates(tier)[1] * days // 36500


def penalty_t(tier, t, days):
    return surcharge_t(tier, t) + interest_t(tier, t, days)


def total_due_t(tier, t, days):
    return t + penalty_t(tier, t, days)


def cert_t_total(gs, inc, days):
    basic = bracket_tax(inc)
    return basic + penalty_t(classify(gs), basic, days)


def cert8_total(gs, inc, days, elected):
    tier = classify(gs)
    if regime_of(gs, elected) == "eight":
        basic = tax8(gs)
    else:
        basic = bracket_tax(inc) + pct_tax(gs)
    return basic + penalty_t(tier, basic, days)


def crossover(gs):
    """First income (centavos) where the graduated base shelters the 8% base."""
    target = tax8(gs) - pct_tax(gs)
    lo, hi = 0, 100_000_000_000
    while lo < hi:
        mid = (lo + hi) // 2
        if bracket_tax(mid) >= target:
            hi = mid
        else:
            lo = mid + 1
    return lo

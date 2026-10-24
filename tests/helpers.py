"""Test helpers shared by the engine tests."""

import pytest


def produce(plan: dict, lx=None) -> dict:
    """The production sequence (scripts/realize_plans.py, scripts/build_tier2.py): check_plan, then realize.
    Fails the test on any check error, so an agreement test cannot pass by calling realize() on a plan the
    checker would reject (David's review: the Father-and-Mother test bypassed check_plan)."""
    from pie.realize import Lexicon, check_plan, realize
    lx = lx or Lexicon.load()
    errs = check_plan(plan, lx)
    if errs:
        pytest.fail(f"check_plan rejects {plan.get('english')!r}: {errs}")
    return realize(plan, lx)

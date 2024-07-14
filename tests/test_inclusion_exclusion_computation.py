from random import random, choice
from tests.utils import brute_force_compliance
from pds_compliance.pds import AbstractPDS, TraceFootprint
import pytest


def random_test_case(n):
    length = choice(range(0, n + 1))

    pi = TraceFootprint({i: random() > 0.5 for i in range(length)})

    pds = AbstractPDS({i: random() for i in range(length)})

    return pi, pds


@pytest.mark.parametrize(["pi", "pds"], [random_test_case(5) for _ in range(500)])
def test_random_small_worlds(pi, pds):
    bfc = brute_force_compliance(pi, dict(pds.probs))
    p = pds.compliance(pi)

    assert pytest.approx(abs(bfc - p), abs=1e-12) == 0.0


@pytest.mark.parametrize(["pi", "pds"], [random_test_case(20) for _ in range(100)])
def test_random_long_worlds(pi, pds):
    bfc = brute_force_compliance(pi, dict(pds.probs))
    p = pds.compliance(pi)

    assert pytest.approx(abs(bfc - p), abs=1e-12) == 0.0

from random import random, choice, uniform
from tests.utils import brute_force_compliance
from pds_compliance.pds import AbstractPDS, TraceFootprint
import pytest


def random_test_case(n, a, b):
    length = choice(range(0, n + 1))
    pi = TraceFootprint({i: random() > 0.5 for i in range(length)})
    probs = {i: uniform(a, b) for i in range(length)}
    return pi, probs


def random_test_case_no_crisp(n):
    return random_test_case(n, 0.10, 0.90)


def random_test_case_crisp_allowed(n):
    return random_test_case(n, 0.0, 1.0)


def assert_abstract_pds_compliance_match_brute_force_compliance(pi, probs):
    bfc = brute_force_compliance(pi, probs)
    p = AbstractPDS.of(probs).compliance(pi)
    assert p == pytest.approx(bfc, abs=1e-12)


@pytest.mark.parametrize(
    ["pi", "probs"], [random_test_case_no_crisp(5) for _ in range(500)]
)
def test_random_small_worlds_no_crisp(pi, probs):
    assert_abstract_pds_compliance_match_brute_force_compliance(pi, probs)


@pytest.mark.parametrize(
    ["pi", "probs"], [random_test_case_crisp_allowed(5) for _ in range(500)]
)
def test_random_small_worlds_crisp_allowed(pi, probs):
    assert_abstract_pds_compliance_match_brute_force_compliance(pi, probs)


@pytest.mark.parametrize(
    ["pi", "probs"], [random_test_case_no_crisp(20) for _ in range(50)]
)
def test_random_big_worlds_no_crisp(pi, probs):
    assert_abstract_pds_compliance_match_brute_force_compliance(pi, probs)


@pytest.mark.parametrize(
    ["pi", "probs"], [random_test_case_crisp_allowed(20) for _ in range(50)]
)
def test_random_big_worlds_crisp_allowed(pi, probs):
    assert_abstract_pds_compliance_match_brute_force_compliance(pi, probs)

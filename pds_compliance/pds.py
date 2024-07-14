from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Tuple
from pds_compliance.exceptions import *
from itertools import combinations
import numpy
from frozendict import frozendict


def validate_probabilities(probs: Dict[int, bool]):
    for c, p in probs.items():
        if p < 0 or p > 1:
            raise InvalidProbability(p, c)


@dataclass(frozen=True)
class TraceFootprint:
    constraints: Dict[int, bool]

    def __getitem__(self, item):
        return self.constraints[item]


class AbstractPDS:
    def __init__(self, probs):
        validate_probabilities(probs)
        self.probs: frozendict[int, float] = frozendict(probs)
        self._subset_product = lru_cache(None)(self._subset_product)
        self._inclusion_exclusion = lru_cache(None)(self._inclusion_exclusion)

    def _subset_product(self, constraints):
        return numpy.prod([self.probs[c] for c in constraints])

    def _inclusion_exclusion(self, constraints: Tuple[int]):
        n = len(constraints)
        if n == 1:
            return self.probs[constraints[0]]

        res = numpy.sum([self.probs[c] for c in constraints])
        add = False
        for k in range(2, n + 1):
            z = 0
            for event in combinations(constraints, k):
                z += self._subset_product(event[:-1]) * self.probs[event[-1]]

            res = (res + z) if add else (res - z)
            add = not add

        return res

    def compliance(self, fp: TraceFootprint):
        sat = []
        vio = []

        for c, _ in fp.constraints.items():
            if c not in self.probs:
                raise MissingProbability(c)

            p = self.probs[c]

            # Trace violates a crisp constraint
            # compliance is null
            if not fp[c] and p == 1:
                return 0.0

            elif fp[c] and p == 1:
                # Satisfied crisp constraints
                # do not affect compliance
                pass

            elif fp[c]:
                sat.append(c)

            else:
                vio.append(c)

        sat = tuple(sorted(sat))

        if len(vio) == 0:
            return 1.0

        # P(w_1 | w_2 | ... | w_k), pi |= w_i
        any_sat_world = 0.0

        # always true that pi |= {}
        null_world = 1.0

        # pi |\= c => pi |\= c & c', for all c'
        # thus pi satisfies a world iff the world
        # does not contain a violated constraint
        not_vio_world = numpy.prod([1 - self.probs[c] for c in vio])

        if len(sat) > 0:
            any_sat_world = self._inclusion_exclusion(sat)
            null_world = numpy.prod([1 - self.probs[c] for c in sat])

        return not_vio_world * (null_world + any_sat_world)

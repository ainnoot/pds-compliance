from dataclasses import dataclass, InitVar
from functools import lru_cache
from typing import Dict, Tuple
from pds_compliance.exceptions import *
from itertools import combinations
import numpy
from frozendict import frozendict


def validate_probabilities(probs: frozendict[int, float]):
    for c, p in probs.items():
        if p < 0 or p > 1:
            raise InvalidProbability(p, c)


@dataclass(frozen=True)
class TraceFootprint:
    __constraints: Dict[int, bool]

    def __getitem__(self, item):
        return self.__constraints[item]

    def __iter__(self):
        return iter(self.__constraints.items())


@dataclass(frozen=True)
class AbstractPDS:
    probs: frozendict[int, float]
    key: InitVar[object]
    __key = object()

    def __post_init__(self, key):
        if key != self.__key:
            raise WrongKey(self)
        validate_probabilities(self.probs)

    @staticmethod
    def of(probs: dict[int, float]):
        return AbstractPDS(frozendict(probs), key=AbstractPDS.__key)

    @lru_cache(None)
    def _subset_product(self, constraints):
        return numpy.prod([self.probs[c] for c in constraints])

    @lru_cache(None)
    def _inclusion_exclusion(self, constraints: Tuple[int, ...]):
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
        vio = []

        for c, _ in fp:
            if c not in self.probs:
                raise MissingProbability(c)

            p = self.probs[c]

            # Satisfied crisp constraints do not affect compliance
            if not fp[c]:
                # Trace violates a crisp constraint
                # compliance is null
                if p == 1:
                    return 0.0
                vio.append(c)

        if len(vio) == 0:
            return 1.0

        return 1 - self._inclusion_exclusion(tuple(sorted(vio)))

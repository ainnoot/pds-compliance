from dataclasses import dataclass, InitVar
from functools import cache
from typing import Dict, Tuple
from pds_compliance.exceptions import *
from itertools import combinations
from functools import reduce
from frozendict import frozendict
from collections import defaultdict


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

    def __setproduct(self, values):
        return reduce(lambda x, y: x * y, values, 1)

    def __inclusion_exclusion(self, constraints: Tuple[int, ...]):
        n = len(constraints)
        if n == 1:
            return self.probs[constraints[0]]

        probs = [self.probs[c] for c in constraints]
        res = sum(probs)
        add = False
        for k in range(2, n + 1):
            z = 0
            for event in combinations(probs, k):
                z += self.__setproduct(event)

            res = (res + z) if add else (res - z)
            add = not add

        return res

    def compliance(self, fp: TraceFootprint):
        sat = []
        vio = []

        for c, _ in fp:
            if c not in self.probs:
                raise MissingProbability(c)

            p = self.probs[c]

            # Satisfied crisp constraints do not affect compliance
            if not fp[c]:
                # Trace violates a crisp constraint compliance is null
                if p == 1:
                    return 0.0
                vio.append(c)

            if fp[c] and p < 1:
                sat.append(c)

        if len(vio) == 0:
            return 1.0

        if len(vio) <= len(sat):
            return 1 - self.__inclusion_exclusion(tuple(sorted(vio)))

        else:
            not_vio_world = self.__setproduct([1 - self.probs[c] for c in vio])
            any_sat_world = self.__inclusion_exclusion(tuple(sorted(sat)))
            null_world = self.__setproduct([1 - self.probs[c] for c in sat])

            return not_vio_world * (null_world + any_sat_world)

from itertools import combinations
from typing import Dict
import numpy
from pds_compliance.pds import TraceFootprint


def set_probability(ins, outs, ps):
    # Returns P(in_1 & in_2 & ... & ~out_1 & ~out_2)

    values = []
    for c in ins:
        values.append(ps[c])

    for c in outs:
        values.append(1 - ps[c])

    return numpy.prod(values)


def brute_force_compliance(pi: TraceFootprint, probs: Dict[int, float]):
    all_constraints = set(probs.keys())
    vio = set([x for x, v in pi.constraints.items() if not v])

    n = len(probs)
    P = 0.0

    for world_size in range(0, n + 1):
        # A world is the set of satisfied constraints
        for world in combinations(all_constraints, world_size):
            world = set(world)

            # Does not count towards compliance
            if len(world & vio) > 0:
                continue

            # This counts
            world_complement = all_constraints.difference(world)
            p = set_probability(world, world_complement, probs)
            P += p

    return P

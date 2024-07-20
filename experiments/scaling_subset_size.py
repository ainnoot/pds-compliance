from pds_compliance import TraceFootprint, AbstractPDS
import random
from time import perf_counter
import numpy
from argparse import ArgumentParser


def parse_args():
    p = ArgumentParser()
    p.add_argument(
        "max_size", type=int, help="Max size of set subject to inclusion/exclusion."
    )
    p.add_argument("step", type=int, help="Step increase for set size.")
    p.add_argument(
        "pds_per_step", type=int, help="How many PDS to sample for each step."
    )
    p.add_argument(
        "trace_per_step", type=int, help="How many traces to sample for each step."
    )

    return p.parse_args()


def trace_footprint_with_h(num_constraints, hardness):
    """
    Generates a trace footprint with exactly `hardness` true constraints.
    """

    if hardness > num_constraints / 2:
        raise ValueError(
            "Inclusion-exclusion is exponential in min(|SAT|,|VIO|)! Going above N//2 makes the problem easier."
        )

    constraints = {i: False for i in range(num_constraints)}
    for i in range(hardness):
        constraints[i] = True

    return TraceFootprint(constraints)


def generate_random_pds_probs(num_constraints, a, b):
    """
    Generates PDS probabilities, uniformly sampling in [a,b).
    """

    return {i: random.uniform(a, b) for i in range(num_constraints)}


if __name__ == "__main__":
    args = parse_args()
    N = range(args.step, args.max_size, args.step)
    P = pds_per_model = args.pds_per_step
    C = trials = args.trace_per_step

    print("max_size,average_time,std_dev")
    for e in N:
        n = e * 2
        fp = trace_footprint_with_h(n, e)
        times = []
        for pid in range(P):
            pds_probs = generate_random_pds_probs(n, 0.05, 0.95)
            for c in range(C):
                start = perf_counter()
                pds = AbstractPDS.of(pds_probs)
                ans = pds.compliance(fp)
                end = perf_counter()

                elapsed = end - start
                times.append(elapsed)

        avg, std = float(numpy.mean(times)), float(numpy.std(times))
        print(f"{e},{avg:.5f},{std:.5f}")

import json
from argparse import ArgumentParser

from declasp import Trace, StringEventLog
from declasp.declare import declare_model_from_json, declare_constraint_from_json
from pds_compliance import DeclarePDS


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("model", type=str, help="A Declare model in JSON format.")
    parser.add_argument(
        "log",
        type=str,
        help="A file that stores traces as comma-separated values (one per row).",
    )

    args = parser.parse_args()
    return args.model, args.log


def main():
    model_json_path, csv_log = parse_args()
    with open(model_json_path) as f:
        model_json = json.load(f)

    with open(csv_log) as f:
        traces = [(trace_id, x.strip()) for trace_id, x in enumerate(f.readlines())]

    traces = [Trace.from_csv(t, f"pds-{trace_id}") for trace_id, t in traces]

    declare_pds = DeclarePDS()
    for constraint in model_json:
        # remove the field that is missing from declasp input format
        p = constraint.pop("probability")

        # parse the standard declare constraint
        declare_constraint = declare_constraint_from_json(constraint)

        # add it into the pds with an associated probability
        declare_pds.add_constraint(declare_constraint, p)

    for trace in traces:
        ans = declare_pds.compliance(trace)
        print(f"Compliance for {trace.case_identifier}: {ans:.5f}")


if __name__ == "__main__":
    main()

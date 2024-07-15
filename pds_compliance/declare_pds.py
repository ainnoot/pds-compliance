from frozendict import frozendict

from pds_compliance import TraceFootprint, AbstractPDS
from dataclasses import dataclass
from declasp import Trace
from declasp.declare import Constraint, Model
from declasp.tasks import conformance_checking_single_trace


class DeclarePDS:
    def __init__(self):
        self.probs = dict()
        self.model = Model()

    def add_constraint(self, constraint: Constraint, p: float):
        self.model.add_constraint(constraint)
        self.probs[constraint.id] = p

    def compliance(self, t: Trace) -> float:
        # project a trace onto sat/unsat Declare constraints
        result = conformance_checking_single_trace(self.model, t)

        # create a footprint & standard PDS computation
        tfp = TraceFootprint({c.id: value for c, value in result.items()})
        pds = AbstractPDS.of(self.probs)
        ans = pds.compliance(tfp)

        return ans

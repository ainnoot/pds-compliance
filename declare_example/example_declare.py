import sys
from declasp.tasks import conformance_checking
from declasp.tasks import ConformanceCheckingResult
from declasp.log import StringEventLog
from declasp.declare import declare_model_from_json
import json

from pds_compliance import AbstractPDS, TraceFootprint
from collections import defaultdict
from frozendict import frozendict
from time import perf_counter

if __name__ == "__main__":
	if len(sys.argv) != 4:
		print("Usage: {} [model] [log] [outputfile]".format(__file__))


	start = perf_counter()
	model = declare_model_from_json(sys.argv[1])	
	log = StringEventLog.from_xes(sys.argv[2])
	outputfile = sys.argv[3]
	print("Total constraints:", len(model))
	print("Total traces:", log.number_of_traces())

	print("[parse input] elapsed: {:.3f}s".format(perf_counter() - start))

	start = perf_counter()
	# Run conformance checking task using an external tool
	result = conformance_checking(model, log).as_json()
	print("[crisp conformance checking] elapsed: {:.3f}s".format(perf_counter() - start))

	start = perf_counter()
	# Extract the model
	# (obviously this depends on the output format of the tool...)
	# declasp outputs a JSON file with a 'model' and a 'result' part

	# from the 'model' part, we extract info about the support of each
	# constraint (which in this example we interpret as the associated probability)
	# to instantiate the AbstractPDS class
	sigma = dict()
	for c, constraint in result['model'].items():
		sigma[int(c)] = constraint['support']
	pds = AbstractPDS.of(sigma)

	# from the result part, we define the traces to compute the compliance	
	footprints = defaultdict(lambda: [])
	for tid, trace in result['result'].items():
		fp = TraceFootprint(frozendict({int(c): value for c, value in trace.items()}))
		footprints[fp].append(tid)

	# we perform compliance computation only for unique traces
	print("Total (unique) traces:", len(footprints))

	print("[defining input for pds-compliance] elapsed: {:.3f}s".format(perf_counter() - start))
	start = perf_counter()

	compliance_result = dict()
	for fp, tids in footprints.items():
		ans = pds.compliance(fp)
		rounded_ans = round(ans, 3)
		for tid in tids:
			compliance_result[tid] = rounded_ans

	print("[compliance check on unique traces after constraint projection] elapsed: {:.3f}s".format(perf_counter() -start))

	with open(outputfile, 'w') as f:
		print(json.dumps(compliance_result, indent=2), file=f)

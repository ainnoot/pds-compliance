from pds_compliance import TraceFootprint, AbstractPDS

if __name__ == "__main__":
    tp = TraceFootprint({1: False, 2: True, 3: False})

    pds = AbstractPDS.of({1: 0.5, 2: 1.0, 3: 0.45})

    ans = pds.compliance(tp)
    print(ans)

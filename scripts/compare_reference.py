"""Compare per-replication metrics for a local pilot against the archived baseline."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_rows(path, maximum_rep):
    result = {}
    with path.open(newline='') as stream:
        for row in csv.DictReader(stream):
            rep = int(row['replicate'])
            if rep >= maximum_rep:
                continue
            key = (row['method'], row['period'], rep, row['metric'])
            if key in result:
                raise ValueError('Duplicate metric key: '+repr(key))
            result[key] = float(row['value'])
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True,
                        help='Fresh-run folder containing pilot/; do not point at reference/')
    args = parser.parse_args()
    run = args.run.resolve()
    if not run.is_relative_to((ROOT/'results').resolve()):
        parser.error('--run must be under this workspace results/')
    local = run/'pilot'
    reference = ROOT/'reference/synthetic_baseline_v1/pilot_results'
    nrep = json.loads((local/'environment.json').read_text())['reps']
    reference_n = json.loads((reference/'environment.json').read_text())['reps']
    if not 2 <= nrep <= reference_n:
        parser.error('Only matching original-seed prefixes with 2..200 replications are supported')
    actual = load_rows(local/'replicates.csv', nrep)
    expected = load_rows(reference/'replicates.csv', nrep)
    if actual.keys() != expected.keys():
        raise AssertionError('Metric key sets differ')
    failures = [repr(k) for k in actual if not math.isclose(actual[k], expected[k],
                                                         rel_tol=1e-12, abs_tol=1e-12)]
    report = {
        'status': 'passed' if not failures else 'failed',
        'replications_compared': nrep, 'metrics_compared': len(actual),
        'relative_tolerance': 1e-12, 'absolute_tolerance': 1e-12,
        'maximum_absolute_difference': max(abs(actual[k]-expected[k]) for k in actual),
        'reference_csv_sha256': hashlib.sha256((reference/'replicates.csv').read_bytes()).hexdigest(),
        'failed_metric_keys': failures,
        'scope': 'Matching development seeds; not new confirmation or a proof',
    }
    with (run/'reference_comparison.json').open('x') as stream:
        json.dump(report, stream, indent=2)
    print(json.dumps(report, indent=2))
    if failures:
        raise SystemExit(1)

if __name__ == '__main__':
    main()

"""Run the finite checks for Appendix D."""
from fractions import Fraction
from pathlib import Path
import argparse
import importlib
import sys
import time

if sys.version_info < (3, 8):
    raise SystemExit('Python 3.8 or later is required.')
if not __debug__:
    raise SystemExit('Refused: optimized Python (-O/-OO) disables assertions.')

from verification_io import (
    ROOT, SOFTWARE_VERSION, PROOF_MAP, check_integrity,
    new_run, source_hashes, utc_now, write_latest, write_report,
)

STAGES = (
    ('preliminaries', 'verify_prerequisites', 'PASS_FINITE_PRELIMINARIES'),
    ('global', 'verify_global', 'PASS_GLOBAL_CERTIFICATE'),
    ('local', 'verify_local', 'PASS_LOCAL_CERTIFICATE'),
)


def check_stage_links(preliminary, global_proof, local):
    modes = global_proof['mode_cover']
    assert preliminary['small_cost_cutoff'] == modes['small_cost_floor'], 'D.2 cutoff differs from D.3'
    assert global_proof['certified_local_domain'] == {'cost': 'delta > 4/5', 'imbalance': '|b-c| <= 1/20'}
    images = global_proof['classification']['local_sign_cells']
    checked = [family['sign_cells'] for family in local['grid_geometry'].values()]
    assert len(images) == 5 and sorted(images) == sorted(checked), 'D.3 and D.4 cover different sign cells'
    assert local['domain']['a'] == ['0', '7/125']
    dmax = Fraction(modes['local_d_max'])
    assert list(map(Fraction, local['domain']['D'])) == [-dmax, dmax], 'D.4 imbalance range differs from D.3'
    symmetric_cost = Fraction(local['constants']['symmetric_cost_at_a_max'])
    assert symmetric_cost < Fraction(modes['local_cost_floor']), 'D.3 cost floor does not imply the D.4 range'
    assert local['constants']['final_imbalance_coefficient'] == '1/8'


def run_verification(output_dir):
    start = time.monotonic()
    output, run_dir, context = new_run(output_dir)
    summary_path = run_dir / 'summary.json'
    summary = dict(context, status='RUNNING', python_version=sys.version.split()[0],
                   proof_map=PROOF_MAP, stages={name: 'PENDING' for name, _, _ in STAGES})
    write_report(summary_path, summary)
    write_latest(output, run_dir, summary)
    for name, _, _ in STAGES:
        write_report(run_dir / (name + '.json'), dict(context, stage=name, status='PENDING'))
    print('Reports: ' + str(run_dir), flush=True)
    results = {}
    current = 'inputs'
    try:
        summary['sha256'] = source_hashes(ROOT)
        for name, module_name, expected in STAGES:
            current = name
            summary['stages'][name] = 'RUNNING'
            write_report(summary_path, summary)
            write_report(run_dir / (name + '.json'), dict(context, stage=name, status='RUNNING'))
            print('Checking ' + name + ': ' + ', '.join(PROOF_MAP[name]['manuscript']), flush=True)
            module = importlib.import_module(module_name)
            result = module.compute()
            assert result['status'] == expected, (name, result.get('status'))
            result.update(context, stage=name, finished_utc=utc_now())
            write_report(run_dir / (name + '.json'), result)
            results[name] = result
            summary['stages'][name] = expected
            print(expected, flush=True)

        current = 'combined_checks'
        check_stage_links(results['preliminaries'], results['global'], results['local'])
        assert source_hashes(ROOT) == summary['sha256'], 'Verification inputs changed during the run'
        summary.update(
            status='PASS_EXACT_VERIFICATION',
            scope='Finite checks in D.1-D.6. Geometric reductions, integration, and the classification '
                  'of physical protocols are given in the manuscript.',
            counts=dict(
                preliminary_vertex_checks=results['preliminaries']['mode_cap']['vertex_checks'],
                support_orbits=results['global']['classification']['orbits'],
                retained_local_types=results['global']['classification']['retained_orbits'],
                global_witnesses=results['global']['data_witnesses'],
                global_leaves=results['global']['total_leaves'],
                local_leaves=results['local']['total_leaves'],
                local_row_interval_checks=results['local']['total_row_interval_checks'],
                weight_vertex_checks=sum(x['vertex_checks'] for x in results['local']['weight_bounds'].values()),
                principal_and_exchanged_identities=results['local']['identities']['principal_and_exchanged_row_identities'],
                negative_controls_rejected=sum(len(r['negative_controls_rejected']) for r in results.values())),
            standard_library_only=True, floating_point_in_acceptance_tests=False,
        )
    except BaseException as error:
        summary.update(status='FAIL_EXACT_VERIFICATION', failed_stage=current,
                       error_type=type(error).__name__, error=str(error))
        for name, _, _ in STAGES:
            if summary['stages'][name] in ('RUNNING', 'PENDING'):
                status = 'FAIL' if name == current else 'SKIPPED'
                summary['stages'][name] = status
                write_report(run_dir / (name + '.json'), dict(
                    context, stage=name, status=status,
                    reason='Run failed at ' + current, error_type=type(error).__name__, error=str(error)))
        summary.update(finished_utc=utc_now(), seconds=round(time.monotonic() - start, 3))
        write_report(summary_path, summary)
        write_latest(output, run_dir, summary)
        print('FAIL_EXACT_VERIFICATION at ' + current + ': ' + str(error), file=sys.stderr)
        return 130 if isinstance(error, KeyboardInterrupt) else 1

    summary.update(finished_utc=utc_now(), seconds=round(time.monotonic() - start, 3))
    write_report(summary_path, summary)
    write_latest(output, run_dir, summary)
    print(summary['status'], flush=True)
    print('Summary: ' + str(summary_path), flush=True)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'reports', metavar='DIR',
                        help='parent directory for separate run folders (default: reports beside verify.py)')
    parser.add_argument('--check-integrity', action='store_true',
                        help='check distributed file hashes only; does not run mathematical verification')
    parser.add_argument('--version', action='version',
                        version='hybrid-correlation-verification ' + SOFTWARE_VERSION)
    args = parser.parse_args(argv)
    try:
        if args.check_integrity:
            result = check_integrity()
            print(result['status'] + ': ' + str(result['files_checked']) + ' files')
            print(result['scope'])
            return 0
        return run_verification(args.output_dir)
    except (OSError, ValueError) as error:
        print('ERROR: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

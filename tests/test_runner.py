"""Run reports, release integrity, and command-line behavior."""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import os
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import verification_io
from exact_intervals import dot, matvec, transpose


class RunnerTests(unittest.TestCase):
    def setUp(self):
        requested = os.environ.get('VERIFICATION_TEST_TMPDIR')
        parent = Path(requested).resolve() if requested else None
        if parent is not None:
            parent.mkdir(parents=True, exist_ok=True)
        self.temporary = TemporaryDirectory(prefix='verification-tests-', dir=parent)
        self.base = Path(self.temporary.name).resolve()
        if parent is not None:
            self.base.relative_to(parent)
        self.addCleanup(self.temporary.cleanup)

    def copy_package(self):
        target = self.base / 'package with spaces 复核'
        shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('__pycache__', 'reports'))
        return target

    def invoke(self, package, *arguments):
        return subprocess.run([sys.executable, '-B', '-X', 'utf8', str(package / 'verify.py'), *arguments],
                              cwd=self.base, capture_output=True, text=True, encoding='utf-8', timeout=60)

    def latest(self, directory):
        pointer = json.loads((directory / 'latest.json').read_text(encoding='utf-8'))
        path = directory / pointer['summary']
        return json.loads(path.read_text(encoding='utf-8')), path.parent

    def test_success_from_other_directory_and_non_ascii_path(self):
        package = self.copy_package()
        reports = self.base / 'results with spaces 结果'
        result = self.invoke(package, '--output-dir', str(reports))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        summary, run_dir = self.latest(reports)
        self.assertEqual(summary['status'], 'PASS_EXACT_VERIFICATION')
        self.assertEqual(summary['counts']['negative_controls_rejected'], 18)
        baseline = json.loads((ROOT / 'reference_reports/summary.json').read_text(encoding='utf-8'))
        self.assertEqual(summary['counts'], baseline['counts'])
        self.assertEqual(summary['software_version'], verification_io.SOFTWARE_VERSION)
        for name in ('preliminaries', 'global', 'local'):
            stage = json.loads((run_dir / (name + '.json')).read_text(encoding='utf-8'))
            self.assertEqual(stage['run_id'], summary['run_id'])
            self.assertTrue(stage['status'].startswith('PASS_'))

    def test_corrupt_certificate_cannot_reuse_old_pass(self):
        package = self.copy_package()
        cert = package / 'certificates/global.json'
        data = json.loads(cert.read_text(encoding='utf-8'))
        data['mode_cover']['cases'][0]['witnesses'][0] = [0] * 8
        cert.write_text(json.dumps(data), encoding='utf-8')
        reports = self.base / 'reports'
        old = reports / 'old-run'
        old.mkdir(parents=True)
        prior = b'{"status":"PASS_EXACT_VERIFICATION","run_id":"old"}\n'
        (old / 'summary.json').write_bytes(prior)
        (reports / 'latest.json').write_text('{"status":"PASS_EXACT_VERIFICATION","run_id":"old","summary":"old-run/summary.json"}', encoding='utf-8')
        result = self.invoke(package, '--output-dir', str(reports))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        summary, run_dir = self.latest(reports)
        self.assertEqual(summary['status'], 'FAIL_EXACT_VERIFICATION')
        self.assertEqual(summary['failed_stage'], 'global')
        self.assertIn('support=', summary['error'])
        self.assertIn('witness=0', summary['error'])
        self.assertEqual(summary['stages']['local'], 'SKIPPED')
        self.assertEqual((old / 'summary.json').read_bytes(), prior)
        for name in ('preliminaries', 'global', 'local'):
            stage = json.loads((run_dir / (name + '.json')).read_text(encoding='utf-8'))
            self.assertEqual(stage['run_id'], summary['run_id'])

    def test_missing_input_records_failure_before_stages(self):
        package = self.copy_package()
        (package / 'certificates/local.json').unlink()
        reports = self.base / 'reports'
        result = self.invoke(package, '--output-dir', str(reports))
        self.assertEqual(result.returncode, 1)
        summary, _ = self.latest(reports)
        self.assertEqual(summary['failed_stage'], 'inputs')
        self.assertEqual(set(summary['stages'].values()), {'SKIPPED'})

    def test_certificate_fields_are_unambiguous(self):
        path = self.base / 'part.json'
        for text, message in (
            ('{"cases":[{"support":1,"support":2}]}', 'duplicate field'),
            ('{"coefficient":0.5}', 'expected an integer'),
            ('{"coefficient":NaN}', 'expected an integer'),
        ):
            with self.subTest(text=text):
                path.write_text(text, encoding='utf-8')
                with self.assertRaisesRegex(ValueError, message):
                    verification_io.read_certificate(path)
        path.write_text('{"coefficients":[42,"2/3"]}', encoding='utf-8')
        self.assertEqual(verification_io.read_certificate(path), {'coefficients':[42,'2/3']})

    def test_vector_and_matrix_dimensions(self):
        with self.assertRaisesRegex(ValueError, 'vector lengths'):
            dot([1, 2], [3])
        with self.assertRaisesRegex(ValueError, 'vector lengths'):
            matvec([[1, 2], [3]], [4, 5])
        with self.assertRaisesRegex(ValueError, 'row.*lengths'):
            transpose([[1, 2], [3]])
        self.assertEqual(dot([], []), 0)
        self.assertEqual(matvec([[1, 0], [0, 1]], iter([3, 5])), [3, 5])
        self.assertEqual(transpose([[1, 2], [3, 4]]), [(1, 3), (2, 4)])

    def test_optimized_python_rejected_for_every_verifier(self):
        for option in ('-O', '-OO'):
            for name in ('verify.py', 'verify_prerequisites.py', 'verify_global.py', 'verify_local.py', 'worked_examples.py'):
                with self.subTest(option=option, name=name):
                    result = subprocess.run([sys.executable, '-B', option, str(ROOT / name)],
                                            cwd=self.base, capture_output=True, text=True, timeout=20)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('disables assertions', result.stderr)

    def test_failed_serialization_preserves_complete_report(self):
        target = self.base / 'result.json'
        original = b'{"status":"previous complete report"}\n'
        target.write_bytes(original)
        with self.assertRaises(TypeError):
            verification_io.write_report(target, {'invalid': object()})
        self.assertEqual(target.read_bytes(), original)
        self.assertEqual(set(self.base.iterdir()), {target})

    def test_atomic_report_write_in_a_deep_directory(self):
        filename = 'preliminaries.json'
        # Choose a valid public path close to the usual Windows length limit.
        padding = 255 - len(str(self.base / filename)) - 1
        directory = self.base / ('d' * max(0, padding))
        directory.mkdir(exist_ok=True)
        target = directory / filename
        rename = os.replace

        def check_name(src, dest):
            src, dest = Path(src), Path(dest)
            self.assertEqual(src.parent, dest.parent)
            self.assertLessEqual(len(src.name), len(dest.name))
            rename(src, dest)

        with patch.object(verification_io.os, 'replace', side_effect=check_name):
            verification_io.write_report(target, {'status': 'PASS'})
        self.assertEqual(json.loads(target.read_text(encoding='utf-8')), {'status': 'PASS'})
        self.assertEqual(set(directory.iterdir()), {target})

    def test_integrity_rejects_changed_and_unsafe_entries(self):
        package = self.copy_package()
        lines = [hashlib.sha256((package / name).read_bytes()).hexdigest() + '  ' + name
                 for name in verification_io.SOURCE_FILES]
        manifest = package / 'SHA256SUMS'
        manifest.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        self.assertEqual(verification_io.check_integrity(package)['status'], 'PASS_PACKAGE_INTEGRITY')
        target = package / 'certificates/local.json'
        original = target.read_bytes()
        target.write_bytes(original + b' ')
        with self.assertRaisesRegex(ValueError, 'differs'):
            verification_io.check_integrity(package)
        target.write_bytes(original)
        manifest.write_text('\n'.join(lines) + '\n' + '0' * 64 + '  ../outside\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            verification_io.check_integrity(package)


if __name__ == '__main__':
    unittest.main(verbosity=2)

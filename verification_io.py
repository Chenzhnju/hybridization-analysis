"""Package metadata, certificate input, and run reports."""
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import re
import tempfile
import uuid

PUBLICATION_REVISION = 31
SOFTWARE_VERSION = '31.2'
MANUSCRIPT_VERSION = 'journal-latex-2026-11-22'
ROOT = Path(__file__).resolve().parent
SOURCE_FILES = (
    'verify.py', 'verify_prerequisites.py', 'verify_global.py', 'verify_local.py',
    'local_rows.py', 'grid_witness.py', 'dyadic_cover.py', 'exact_intervals.py', 'exact_polynomials.py',
    'verification_io.py', 'certificates/global.json', 'certificates/local.json',
)
PROOF_MAP = {
    'preliminaries': {
        'code': ['verify_prerequisites.py', 'grid_witness.py'],
        'manuscript': ['D.1 (Eq. (D.3) and witness bound)', 'D.2 final scalar comparison'],
    },
    'global': {
        'code': ['verify_global.py', 'grid_witness.py', 'certificates/global.json'],
        'manuscript': ['D.3', 'Lemma D.1', 'Eq. (D.7)'],
    },
    'local': {
        'code': ['verify_local.py', 'local_rows.py', 'certificates/local.json'],
        'manuscript': ['D.4, Lemma D.2', 'Eqs. (D.8)-(D.10)', 'D.6 marginal identities'],
    },
    'analytic_arguments_not_automated': {
        'manuscript': [
            'D.1 moment and witness reduction',
            'D.2 geometric containment and conditional means',
            'D.3 reduction of physical responses to finite covers',
            'D.4 averaging and integration',
            'D.5 optimal-cost comparison and endpoints',
            'D.6 passage from equality to the classification of protocols',
        ],
    },
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def read_certificate(path):
    """Read one proof certificate, retaining the exact integer representation."""
    def unique_fields(pairs):
        fields = {}
        for key, value in pairs:
            if key in fields:
                raise ValueError(f"{path.name}: duplicate field {key!r}")
            fields[key] = value
        return fields

    def invalid_number(token):
        raise ValueError(f"{path.name}: expected an integer or a quoted rational, found {token}")

    with path.open(encoding="utf-8") as stream:
        return json.load(stream, object_pairs_hook=unique_fields,
                         parse_float=invalid_number, parse_constant=invalid_number)


def source_hashes(directory=ROOT, names=SOURCE_FILES):
    root = Path(directory)
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in names}


def expect_rejection(label, check):
    try:
        check()
    except (AssertionError, KeyError, IndexError, TypeError, ValueError, ZeroDivisionError):
        return label
    raise AssertionError('Invalid certificate was accepted: ' + label)


def write_report(path, report):
    """Publish a complete UTF-8 JSON file without exposing a partial write."""
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
                mode='w', encoding='utf-8', newline='\n',
                # Keep the temporary name short in deeply nested Windows paths.
                prefix='.', suffix='',
                dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(report, stream, indent=2, ensure_ascii=False)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def new_run(output_dir):
    """Allocate an independent directory; a rerun never overwrites old evidence."""
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    run_id = uuid.uuid4().hex
    run_dir = output / ('run-' + now.strftime('%Y%m%dT%H%M%SZ') + '-' + run_id)
    run_dir.mkdir()
    context = dict(publication_revision=PUBLICATION_REVISION, software_version=SOFTWARE_VERSION,
                   manuscript_version=MANUSCRIPT_VERSION,
                   run_id=run_id, started_utc=now.isoformat())
    return output, run_dir, context


def write_latest(output, run_dir, report):
    write_report(Path(output) / 'latest.json', dict(
        status=report['status'], run_id=report['run_id'],
        summary=run_dir.name + '/summary.json'))


def check_integrity(directory=ROOT):
    """Check distributed files, not later generated reports. Hashes are not a signature."""
    root = Path(directory).resolve()
    entries = {}
    for line in (root / 'SHA256SUMS').read_text(encoding='utf-8').splitlines():
        match = re.fullmatch(r'([0-9a-f]{64})  (.+)', line)
        if match is None:
            raise ValueError('Malformed SHA256SUMS entry')
        expected, name = match.groups()
        path = PurePosixPath(name)
        if (path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name
                or str(path) != name or name == 'SHA256SUMS' or name in entries):
            raise ValueError('Unsafe or duplicate manifest path: ' + name)
        target = (root / name).resolve()
        try:
            target.relative_to(root)
        except ValueError:
            raise ValueError('Manifest path escapes package: ' + name)
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError('File differs from this release: ' + name)
        entries[name] = expected
    missing = set(SOURCE_FILES) - set(entries)
    if missing:
        raise ValueError('Manifest omits verification inputs: ' + ', '.join(sorted(missing)))
    return dict(status='PASS_PACKAGE_INTEGRITY', files_checked=len(entries),
                scope='Distributed file consistency only; run verify.py for mathematical checks.')

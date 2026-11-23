"""Refresh SHA256SUMS from the staged Git file list and current file bytes."""
from pathlib import Path
import hashlib
import subprocess


def main():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        ['git', 'ls-files', '-z', '--cached'],
        cwd=root, check=True, stdout=subprocess.PIPE,
    )
    names = sorted(set(result.stdout.decode('utf-8').split('\0')) - {'', 'SHA256SUMS'})
    if 'verify.py' not in names:
        raise SystemExit('Stage the package files with git add before updating the manifest.')
    entries = []
    for name in names:
        path = root / name
        if not path.is_file():
            raise SystemExit('Stage this removal with git add before continuing: ' + name)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entries.append(digest + '  ' + name + '\n')
    (root / 'SHA256SUMS').write_bytes(''.join(entries).encode('utf-8'))
    print('Updated SHA256SUMS for ' + str(len(entries)) + ' tracked files.')


if __name__ == '__main__':
    main()

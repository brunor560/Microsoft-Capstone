#!/usr/bin/env python3
"""Restore published title-edit evidence; never use a results branch's app/."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess

BASELINE = '4e258a96855d98edd10247f68c0b8265e53a8921'
EVALUATOR = '02996447e01bb284939d9b1a83c45ab033c22fb9'
SUBMISSIONS = {
    'antigravity': 'f02e023a62993171e22708818fdeb529fe12d1b1',
    'claude': '5ae07ab6f5b53a14018559e8aac60a49da8b6ea8',
    'codex': '1079551f892fb2d9e64239f03d0b4df5ce6f7ee5',
    'copilot': '30c5294d7d4a36dc629d20bacebb6eb6d413b3e5',
}
PROTOCOL = 'benchmark-results/protocol/edit-title'
EVALUATOR_FILES = (
    'package.json', 'package-lock.json', 'playwright.config.cjs',
    'edit-title-api.test.cjs', 'edit-title.browser.spec.cjs',
)


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def blob(repo, commit, source):
    # Check regular-file type before exporting; never follow a Git symlink.
    entries = git(repo, 'ls-tree', '-z', commit, '--', source).split(b'\0')
    entries = [e for e in entries if e]
    if len(entries) != 1:
        raise ValueError(f'Missing or ambiguous source: {commit}:{source}')
    header, path = entries[0].split(b'\t', 1)
    mode, kind, object_id = header.split()
    if mode not in (b'100644', b'100755') or kind != b'blob':
        raise ValueError(f'Not a regular file: {source}')
    if path.decode('utf-8') != source:
        raise ValueError(f'Unexpected source path: {source}')
    return git(repo, 'cat-file', 'blob', object_id.decode('ascii'))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool', choices=SUBMISSIONS, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    repo = Path(git(Path.cwd(), 'rev-parse', '--show-toplevel').decode().strip())
    out = args.output.resolve()
    if out.exists():
        raise ValueError(f'Output already exists; choose a fresh folder: {out}')
    for commit in (BASELINE, EVALUATOR, SUBMISSIONS[args.tool]):
        git(repo, 'cat-file', '-e', commit + '^{commit}')
    out.mkdir(parents=True)
    records = []

    def export(commit, source, relative):
        data = blob(repo, commit, source)
        target = out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        records.append({'commit': commit, 'source': source,
                        'destination': str(relative).replace('\\', '/'),
                        'sha256': hashlib.sha256(data).hexdigest()})

    tree = git(repo, 'ls-tree', '-r', '-z', '--name-only', BASELINE, '--', 'app')
    for raw in tree.split(b'\0'):
        if not raw:
            continue
        source = raw.decode('utf-8')
        parts = PurePosixPath(source).parts
        if not parts or parts[0] != 'app' or '..' in parts or 'node_modules' in parts:
            raise ValueError(f'Unexpected baseline path: {source}')
        export(BASELINE, source, Path(*parts))
    for name in EVALUATOR_FILES:
        export(EVALUATOR, f'{PROTOCOL}/{name}', Path('evaluator') / name)
    for name, destination in (
        ('server.js', 'app/server.js'), ('test.js', 'app/test.js'),
        ('index.html', 'app/public/index.html'),
    ):
        export(SUBMISSIONS[args.tool],
               f'benchmark-results/{args.tool}/edit-run01/original/{name}',
               Path(destination))
    # Exact baseline suite beside server.js so its relative require is unchanged.
    export(BASELINE, 'app/test.js', Path('app/.baseline-regression.test.cjs'))
    metadata = {
        'tool': args.tool, 'baseline_commit': BASELINE,
        'evaluator_commit': EVALUATOR, 'submission_commit': SUBMISSIONS[args.tool],
        'purpose': 'Correctness regrade of preserved output; not a new agent run',
        'source_exports': records,
        'restored_files': {
            entry['destination']: entry['sha256'] for entry in records
        },
        'verification_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (out / 'provenance.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    print(f'Restored {args.tool} into {out}')


if __name__ == '__main__':
    main()

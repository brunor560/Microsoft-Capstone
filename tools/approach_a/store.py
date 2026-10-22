"""Dataset location, JSON persistence, hashing and the append-only work log.

The structured dataset under assessment/ is authoritative. Markdown files under
assessment/out/ are generated from it and must not be edited by hand.
"""
import datetime
import hashlib
import json
import os
import shutil
import tempfile

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
DEFAULT_ROOT = os.path.join(REPO, 'assessment')

# Files copied into a fresh data directory by `init` (inputs, not findings).
LIBRARY = ('catalog.json', 'people.json', 'candidates')
EMPTY = {
    'manifest.json': {'schema': 'approach-a/manifest/1', 'manifest_version': 0,
                      'profiles': [], 'approval': None},
    'sources.json': {'schema': 'approach-a/sources/1', 'pages': {}, 'entries': {}},
    'cells.json': {'schema': 'approach-a/cells/1', 'cells': {}},
    'reviews.json': {'schema': 'approach-a/reviews/1', 'reviews': []},
}

# Fields that do not change the substance of a finding (excluded from its hash).
VOLATILE = ('assessment_state', 'challenge', 'history')


def today():
    return datetime.date.today().isoformat()


def now():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def sha256(obj):
    data = obj if isinstance(obj, bytes) else json.dumps(
        obj, sort_keys=True, ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def cell_hash(cell):
    return sha256({k: v for k, v in cell.items() if k not in VOLATILE})


def manifest_hash(manifest):
    return sha256({'manifest_version': manifest.get('manifest_version'),
                   'profiles': manifest.get('profiles', [])})


class Store:
    def __init__(self, root=None):
        self.root = os.path.abspath(root or os.environ.get('APPROACH_A_DATA') or DEFAULT_ROOT)

    def path(self, *parts):
        return os.path.join(self.root, *parts)

    def exists(self, name):
        return os.path.exists(self.path(name))

    def load(self, name):
        p = self.path(name)
        if not os.path.exists(p):
            if name in EMPTY:
                return json.loads(json.dumps(EMPTY[name]))
            raise FileNotFoundError('missing dataset file: %s' % p)
        with open(p, encoding='utf-8') as f:
            return json.load(f)

    def save(self, name, data):
        p = self.path(name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(p), suffix='.tmp')
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')
        os.replace(tmp, p)

    def log(self, event, actor='cli', **details):
        entry = {'ts': now(), 'actor': actor, 'event': event}
        entry.update(details)
        os.makedirs(self.root, exist_ok=True)
        with open(self.path('worklog.jsonl'), 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        return entry

    def worklog(self):
        p = self.path('worklog.jsonl')
        if not os.path.exists(p):
            return []
        with open(p, encoding='utf-8') as f:
            return [json.loads(line) for line in f if line.strip()]

    def catalog(self):
        return self.load('catalog.json')

    def people(self):
        return {p['id']: p for p in self.load('people.json')['people']}

    def candidates(self):
        base = self.path('candidates')
        out = []
        if os.path.isdir(base):
            for name in sorted(os.listdir(base)):
                f = os.path.join(base, name, 'candidate.json')
                if os.path.exists(f):
                    with open(f, encoding='utf-8') as fh:
                        c = json.load(fh)
                    c['_dir'] = os.path.join(base, name)
                    out.append(c)
        return out

    def init_from(self, library_root=DEFAULT_ROOT, force=False):
        """Create an empty dataset that reuses the catalog, roster and candidates."""
        if os.path.exists(self.path('manifest.json')) and not force:
            raise FileExistsError('dataset already exists at %s (use --force)' % self.root)
        os.makedirs(self.root, exist_ok=True)
        for name in LIBRARY:
            src, dst = os.path.join(library_root, name), self.path(name)
            if os.path.abspath(src) == os.path.abspath(dst):
                continue
            if os.path.isdir(src):
                shutil.rmtree(dst, ignore_errors=True)
                shutil.copytree(src, dst)
            elif os.path.exists(src):
                shutil.copy(src, dst)
        for name, data in EMPTY.items():
            self.save(name, data)
        for stale in ('worklog.jsonl', 'validation_report.json'):
            if os.path.exists(self.path(stale)):
                os.remove(self.path(stale))
        shutil.rmtree(self.path('out'), ignore_errors=True)

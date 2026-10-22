"""Terminal output: real progress lines, prompts and simple tables (stdlib only)."""
import sys

PHASES = {'discovery': 'Source discovery', 'draft': 'Drafting (Azure OpenAI, documentation excerpts only)',
          'assess': 'Assessment (research agents)',
          'challenge': 'Evidence checking (challenge pass)', 'render': 'Artifact generation',
          'validate': 'Validation'}
TTY = sys.stdout.isatty()


def c(code, s):
    return '\033[%sm%s\033[0m' % (code, s) if TTY else s


def heading(s):
    print('\n' + c('1', s))


def phase(name, note=''):
    print('\n' + c('1;36', '== %s ==' % PHASES.get(name, name)) + ('  ' + note if note else ''))


def progress(phase_name, n, total, msg):
    """Called by the workers after each real unit of work completes.

    APPROACH_A_STEP_DELAY (seconds) slows the display for a live audience; it
    never changes what is done or reported.
    """
    import os
    import time
    delay = float(os.environ.get('APPROACH_A_STEP_DELAY') or 0)
    if delay:
        time.sleep(delay)
    width = 20
    filled = int(width * n / total) if total else width
    bar = '#' * filled + '.' * (width - filled)
    print('  [%s] %*d/%d  %s' % (bar, len(str(total)), n, total, msg), flush=True)


def ok(s):
    print(c('32', '  ok  ') + s)


def warn(s):
    print(c('33', '  !!  ') + s)


def fail(s):
    print(c('31', '  xx  ') + s)


def ask(prompt, default=None, choices=None, assume=None):
    """Prompt; with assume (non-interactive) return it without reading stdin."""
    suffix = ' [%s]' % default if default else ''
    if choices:
        suffix = ' (%s)%s' % ('/'.join(choices), suffix)
    if assume is not None:
        print('%s%s: %s  (non-interactive)' % (prompt, suffix, assume))
        return assume
    while True:
        try:
            ans = input('%s%s: ' % (prompt, suffix)).strip()
        except EOFError:
            ans = ''
        ans = ans or (default or '')
        if not choices or ans in choices:
            return ans
        print('  choose one of: ' + ', '.join(choices))


def table(rows, headers):
    widths = [max(len(str(x)) for x in col) for col in zip(headers, *rows)] if rows else [len(h) for h in headers]
    line = lambda r: '  ' + '  '.join(str(x).ljust(w) for x, w in zip(r, widths))
    print(line(headers))
    print('  ' + '  '.join('-' * w for w in widths))
    for r in rows:
        print(line(r))


def wrap(label, text, width=96, indent=26):
    import textwrap
    text = text if isinstance(text, str) else '; '.join(text) if text else 'none recorded'
    lines = textwrap.wrap(str(text), width - indent) or ['']
    print('  %-*s%s' % (indent - 2, label, lines[0]))
    for l in lines[1:]:
        print(' ' * indent + l)

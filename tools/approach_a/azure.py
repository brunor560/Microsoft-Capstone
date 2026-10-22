"""Azure OpenAI chat adapter for model-assisted drafting (SRS Spec 5.4.2, amended Oct. 22).

Standard library only. Connection settings come from environment variable
names listed in drafting.json (the existing AZURE_DEV_* names), read from an
env file passed with --env-file or from the process environment. They are kept
apart from assessment profiles. The API key is never printed, logged or
written: error text is redacted and the connection's repr hides it.

Every request goes through a Ledger that enforces the run limits (requests,
tokens, estimated cost per run) and the cumulative demo spending cap recorded
in an append-only spend ledger, and through a Pacer that stays under the
deployment's requests-per-minute and tokens-per-minute limits.
"""
import json
import os
import socket
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from . import store as st

CONFIG = os.path.join(os.path.dirname(__file__), 'drafting.json')
RETRY_STATUS = (429, 500, 502, 503, 504)
_sleep = time.sleep
_clock = time.monotonic


class ModelError(Exception):
    """A request failed for this feature only (for example HTTP 400); the feature stays pending."""


class Unavailable(ModelError):
    """Azure cannot be used (no response, or 429/5xx after retries); the run stops with an error."""


class AuthError(Unavailable):
    """Credentials or deployment rejected (401/403/404); the run stops with an error."""


class LimitReached(Exception):
    """A request, token or spending limit would be exceeded; no request was sent."""


def load_config(path=CONFIG):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def read_env_file(path):
    """Parse KEY=VALUE lines (export prefix, quotes and comments allowed)."""
    if not os.path.exists(path):
        raise FileNotFoundError('env file not found: %s' % path)
    out = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            k = k.strip()
            if k.startswith('export '):
                k = k[7:].strip()
            v = v.strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in '"\'':
                v = v[1:-1]
            out[k] = v
    return out


class Connection:
    def __init__(self, endpoint, deployment, api_version, api_key):
        self.endpoint, self.deployment, self.api_version = endpoint.rstrip('/'), deployment, api_version
        self._key = api_key

    @property
    def host(self):
        return urllib.parse.urlparse(self.endpoint).netloc

    def url(self):
        return '%s/openai/deployments/%s/chat/completions?api-version=%s' % (
            self.endpoint, urllib.parse.quote(self.deployment), urllib.parse.quote(self.api_version))

    def headers(self):
        return {'api-key': self._key, 'Content-Type': 'application/json'}

    def redact(self, text):
        return str(text).replace(self._key, '[redacted]') if self._key else str(text)

    def describe(self):
        """Loggable identity: no key."""
        return {'provider': 'azure-openai', 'endpoint_host': self.host,
                'deployment': self.deployment, 'api_version': self.api_version, 'auth': 'api-key'}

    def __repr__(self):
        return 'Connection(%s, deployment=%s, api_version=%s, key=[hidden])' % (
            self.host, self.deployment, self.api_version)


def connection(config, env_file=None, environ=None):
    """Map the configured variable names to a Connection; name what is missing, never its value."""
    env = read_env_file(env_file) if env_file else dict(environ if environ is not None else os.environ)
    names = config['env_names']
    values, missing = {}, []
    for field, var in names.items():
        values[field] = (env.get(var) or '').strip()
        if not values[field]:
            missing.append(var)
    if missing:
        raise ValueError('Azure drafting is not configured: %s not set in %s'
                         % (', '.join(missing), env_file or 'the environment'))
    if not values['endpoint'].startswith('https://'):
        raise ValueError('%s must be an https URL' % names['endpoint'])
    return Connection(values['endpoint'], values['deployment'], values['api_version'], values['api_key'])


def estimate_tokens(text):
    """Token estimate (about 4 characters per token, as Azure's own rate-limit estimate) for
    reservations and pacing; actual usage returned by Azure replaces it in the ledger."""
    return len(text) // 4 + 16


def spend_ledger_path(config):
    return os.environ.get('APPROACH_A_SPEND_LEDGER') or os.path.join(st.REPO, config['spend_ledger'])


class Ledger:
    """Run limits plus the cumulative spending cap. Checked before every attempt."""

    def __init__(self, config, path, overrides=None):
        self.lim = dict(config['limits'], **{k: v for k, v in (overrides or {}).items() if v is not None})
        self.price = config['price_usd_per_million_tokens']
        self.path = path
        self.requests = self.input_tokens = self.output_tokens = 0
        self.cost = 0.0
        self.prior = self._prior_spend()
        self.lock = threading.Lock()

    def _prior_spend(self):
        total = 0.0
        if self.path and os.path.exists(self.path):
            with open(self.path, encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        total += float(json.loads(line).get('cost_usd') or 0)
        return total

    def cost_of(self, tin, tout):
        return (tin * self.price['input'] + tout * self.price['output']) / 1e6

    def reserve(self, est_input):
        """Raise LimitReached unless one more worst-case request fits every limit."""
        lim, worst_out = self.lim, self.lim['max_output_tokens_per_request']
        worst = self.cost_of(est_input, worst_out)
        if self.requests >= lim['max_requests_per_run']:
            raise LimitReached('request limit reached (%d per run)' % lim['max_requests_per_run'])
        if self.input_tokens + self.output_tokens + est_input + worst_out > lim['max_tokens_per_run']:
            raise LimitReached('token limit reached (%d per run)' % lim['max_tokens_per_run'])
        if self.cost + worst > lim['max_cost_usd_per_run']:
            raise LimitReached('per-run spending limit reached ($%.2f)' % lim['max_cost_usd_per_run'])
        if self.prior + self.cost + worst > lim['max_cost_usd_total']:
            raise LimitReached('total spending cap reached ($%.2f; $%.4f already recorded)'
                               % (lim['max_cost_usd_total'], self.prior + self.cost))
        self.requests += 1

    def record(self, entry, tin, tout):
        """Add actual (or, for unknown outcomes, estimated) usage; append to the spend ledger."""
        cost = self.cost_of(tin, tout)
        self.input_tokens += tin
        self.output_tokens += tout
        self.cost += cost
        if self.path:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(dict(entry, ts=st.now(), input_tokens=tin, output_tokens=tout,
                                        cost_usd=round(cost, 6))) + '\n')
        return cost

    def summary(self):
        return {'requests': self.requests, 'input_tokens': self.input_tokens,
                'output_tokens': self.output_tokens, 'estimated_cost_usd': round(self.cost, 4),
                'cumulative_cost_usd': round(self.prior + self.cost, 4),
                'cap_usd': self.lim['max_cost_usd_total']}


class Pacer:
    """Sliding 60 s window kept under the deployment's request and token rate limits.

    Azure counts prompt tokens plus max_tokens against the token limit, so the
    reservation uses the same sum.
    """

    def __init__(self, rpm, tpm):
        self.rpm, self.tpm, self.window = rpm, tpm, []

    def wait(self, tokens, notify=None):
        while True:
            now = _clock()
            self.window = [(t, n) for t, n in self.window if now - t < 60]
            used = sum(n for _, n in self.window)
            if len(self.window) < self.rpm and (used + tokens <= self.tpm or not self.window):
                self.window.append((now, tokens))
                return
            delay = max(0.5, 60 - (now - self.window[0][0]))
            if notify:
                notify('pacing %.0f s to stay under the deployment rate limit' % delay)
            _sleep(delay)


def _retry_after(headers):
    for name, scale in (('retry-after-ms', 0.001), ('retry-after', 1.0)):
        v = headers.get(name) if headers else None
        if v:
            try:
                return min(60.0, float(v) * scale)
            except ValueError:
                pass
    return None


def _post(conn, body, timeout):
    data = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(conn.url(), data=data, headers=conn.headers(), method='POST')
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, {k.lower(): v for k, v in r.headers.items()}, r.read().decode('utf-8')


class Client:
    """One chat completion per call, with pacing, bounded retries and accounting.

    `post` is replaceable for tests (signature: post(conn, body, timeout)).
    Returns a dict with content, finish_reason, model, request_id and usage, plus
    an `attempts` list describing every attempt; raises ModelError, AuthError or
    LimitReached. The API key never appears in returned or raised text.
    """

    def __init__(self, conn, config, ledger, post=None, notify=None):
        self.conn, self.config, self.ledger = conn, config, ledger
        lim = ledger.lim
        self.pacer = Pacer(lim['requests_per_minute'], lim['tokens_per_minute'])
        self.post = post or _post
        self.notify = notify

    def chat(self, messages, label):
        lim = self.ledger.lim
        prompt = ''.join(m['content'] for m in messages)
        est_in = estimate_tokens(prompt)
        if est_in > lim['max_input_tokens_per_request']:
            raise LimitReached('%s: prompt of about %d tokens exceeds the %d-token input limit'
                               % (label, est_in, lim['max_input_tokens_per_request']))
        body = {'messages': messages, 'temperature': self.config.get('temperature', 0),
                'max_tokens': lim['max_output_tokens_per_request'],
                'response_format': {'type': 'json_object'}}
        attempts = []
        ident = {'label': label, 'deployment': self.conn.deployment, 'prompt_version': self.config['prompt_version']}
        for attempt in range(lim['max_retries'] + 1):
            self.ledger.reserve(est_in)
            self.pacer.wait(est_in + lim['max_output_tokens_per_request'], self.notify)
            t0 = _clock()
            try:
                status, headers, text = self.post(self.conn, body, lim['timeout_seconds'])
            except urllib.error.HTTPError as e:
                status, headers = e.code, {k.lower(): v for k, v in (e.headers or {}).items()}
                detail = self.conn.redact(e.read().decode('utf-8', 'replace')[:300] if e.fp else e.reason)
                e.close()
                self.ledger.record(dict(ident, outcome='http_%d' % status), 0, 0)
                attempts.append({'attempt': attempt + 1, 'outcome': 'http_%d' % status,
                                 'seconds': round(_clock() - t0, 2)})
                if status in (401, 403, 404):
                    raise AuthError('%s: Azure returned HTTP %d (check the deployment name, endpoint and key): %s'
                                    % (label, status, detail))
                if status in RETRY_STATUS and attempt < lim['max_retries']:
                    wait = _retry_after(headers) or 2 ** (attempt + 1)
                    if self.notify:
                        self.notify('HTTP %d; retrying in %.0f s' % (status, wait))
                    _sleep(wait)
                    continue
                cls = Unavailable if status in RETRY_STATUS else ModelError
                err = cls('%s: HTTP %d after %d attempt(s): %s' % (label, status, attempt + 1, detail))
                err.attempts = attempts
                raise err
            except (urllib.error.URLError, socket.timeout, TimeoutError, OSError) as e:
                # Outcome unknown: charge the worst case so the caps stay conservative.
                self.ledger.record(dict(ident, outcome='no_response', estimated=True), est_in,
                                   lim['max_output_tokens_per_request'])
                attempts.append({'attempt': attempt + 1, 'outcome': 'no_response',
                                 'error': self.conn.redact(type(e).__name__), 'seconds': round(_clock() - t0, 2)})
                if attempt < lim['max_retries']:
                    _sleep(2 ** (attempt + 1))
                    continue
                err = Unavailable('%s: no response after %d attempt(s) (%s)'
                                 % (label, attempt + 1, self.conn.redact(e)))
                err.attempts = attempts
                raise err
            data = json.loads(text)
            usage = data.get('usage') or {}
            tin, tout = usage.get('prompt_tokens', est_in), usage.get('completion_tokens', 0)
            choice = (data.get('choices') or [{}])[0]
            out = {'content': (choice.get('message') or {}).get('content') or '',
                   'finish_reason': choice.get('finish_reason'), 'model': data.get('model'),
                   'request_id': headers.get('apim-request-id') or headers.get('x-request-id') or data.get('id'),
                   'usage': {'input_tokens': tin, 'output_tokens': tout},
                   'seconds': round(_clock() - t0, 2)}
            out['cost_usd'] = round(self.ledger.record(dict(ident, outcome='ok', model=out['model'],
                                                             request_id=out['request_id']), tin, tout), 6)
            attempts.append({'attempt': attempt + 1, 'outcome': 'ok', 'seconds': out['seconds']})
            out['attempts'] = attempts
            return out
        raise Unavailable('%s: retries exhausted' % label)


def draft_mode(args, config):
    """'azure' or 'off': explicit --draft/--no-draft, then $APPROACH_A_DRAFT, then config default_draft."""
    explicit = getattr(args, 'draft', None)
    if explicit:
        return explicit
    env = (os.environ.get('APPROACH_A_DRAFT') or '').strip().lower()
    if env in ('azure', 'off'):
        return env
    return config.get('default_draft') or 'off'


def env_file_for(args, config):
    """--env-file, else config default_env_file (relative to the repository root), else None."""
    path = getattr(args, 'env_file', None) or config.get('default_env_file')
    if path and not os.path.isabs(path) and not getattr(args, 'env_file', None):
        path = os.path.join(st.REPO, path)
    return path

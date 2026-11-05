// Hidden functionality tests for task 007 (FIX-01 to FIX-03, FIX-05 and the
// existing API). The rest of the export contract (FIX-04) and the agent's own
// tests (TEST-01) are checked by contract-check.cjs.
const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');

if (!process.env.BENCHMARK_APP_DIR) {
  throw new Error('Set BENCHMARK_APP_DIR to the app being evaluated');
}

const APP_DIR = path.resolve(process.env.BENCHMARK_APP_DIR);
const app = require(path.join(APP_DIR, 'server.js'));
const legacy = require(path.join(APP_DIR, 'legacy', 'billing-export.js'));

let server;
let baseUrl;

test.before(async () => {
  await new Promise((resolve, reject) => {
    server = app.listen(0, '127.0.0.1', resolve);
    server.once('error', reject);
  });
  baseUrl = `http://127.0.0.1:${server.address().port}/api/todos`;
});

test.after(async () => {
  if (server && server.listening) {
    await new Promise((resolve, reject) => server.close((e) => (e ? reject(e) : resolve())));
  }
});

function request(suffix = '', method = 'GET', body) {
  return fetch(baseUrl + suffix, {
    method,
    headers: { 'Content-Type': 'application/json' },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    signal: AbortSignal.timeout(5000),
  });
}

async function createTodo(title) {
  const response = await request('', 'POST', { title });
  assert.equal(response.status, 201);
  return response.json();
}

// Each check looks only for the expected row, so line endings, order and the
// rest of the format are left to contract-check.cjs.
const csv = (title, id = 7, completed = false) => legacy.toCsv([{ id, title, completed }]);
const row = (field, id = 7, done = 'N') => `${String(id).padStart(6, '0')},${field},${done}`;
function hasRow(output, expected) {
  assert.equal(typeof output, 'string');
  assert.ok(output.includes(expected), `expected the row ${JSON.stringify(expected)} in ${JSON.stringify(output)}`);
}

test('FIX-01: a title with a comma is one quoted field', () => {
  hasRow(csv('Call Sam, then Alex'), row('"Call Sam, then Alex"'));
  hasRow(csv('a,b,c', 12, true), row('"a,b,c"', 12, 'Y'));
});

test('FIX-02: double quotes are doubled inside a quoted field', () => {
  hasRow(csv('Say "hi"'), row('"Say ""hi"""'));
  hasRow(csv('"quoted"'), row('"""quoted"""'));
});

test('FIX-03: line breaks are kept inside a quoted field', () => {
  hasRow(csv('line one\nline two'), row('"line one\nline two"'));
  hasRow(csv('line one\r\nline two'), row('"line one\r\nline two"'));
  hasRow(csv('carriage\rreturn'), row('"carriage\rreturn"'));
});

test('FIX-01: quoting is applied after cutting long titles', () => {
  const long = 'Pay invoices, then file the receipts for Q3 and Q4';
  hasRow(csv(long), row(`"${long.slice(0, 39)}~"`));
});

test('FIX-05: the module keeps its exported functions', () => {
  assert.equal(typeof legacy.toCsv, 'function');
  assert.equal(typeof legacy.pad_id, 'function');
  assert.equal(typeof legacy.clean_title, 'function');
  assert.equal(legacy.pad_id(42), '000042');
  assert.equal(legacy.clean_title('Plain title'), 'Plain title');
});

test('FIX-05: the export route returns the fixed CSV', async () => {
  const todo = await createTodo('Route check, with comma');
  const response = await request('/export.csv');
  assert.equal(response.status, 200);
  assert.match(response.headers.get('content-type') || '', /^text\/csv/);
  const body = await response.text();
  assert.ok(body.startsWith('ID,TITLE,DONE'));
  hasRow(body, row('"Route check, with comma"', todo.id));
});

test('Existing API behaviour is preserved', async () => {
  const list = await request();
  assert.equal(list.status, 200);
  assert.ok(Array.isArray(await list.json()));
  assert.equal((await request('', 'POST', { title: '   ' })).status, 400);
  assert.equal((await request('/999999', 'PUT', { completed: true })).status, 404);
  const todo = await createTodo('Delete me');
  assert.equal((await request(`/${todo.id}`, 'PUT', { completed: true })).status, 200);
  assert.equal((await request(`/0${todo.id}`, 'DELETE')).status, 204);
  assert.equal((await request(`/${todo.id}`, 'DELETE')).status, 404);
  assert.equal((await request('/abc', 'DELETE')).status, 400);
});

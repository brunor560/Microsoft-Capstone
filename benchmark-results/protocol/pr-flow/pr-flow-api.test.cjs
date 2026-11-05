// Hidden functionality tests for task 008 (REQ-01 and the existing API).
const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');

if (!process.env.BENCHMARK_APP_DIR) {
  throw new Error('Set BENCHMARK_APP_DIR to the app being evaluated');
}

const app = require(path.resolve(process.env.BENCHMARK_APP_DIR, 'server.js'));

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

async function list() {
  const response = await request();
  assert.equal(response.status, 200);
  return response.json();
}

async function stats() {
  const response = await request('/stats');
  assert.equal(response.status, 200);
  assert.match(response.headers.get('content-type') || '', /application\/json/);
  return response.json();
}

function expected(todos) {
  const completed = todos.filter((t) => t.completed).length;
  return { total: todos.length, completed, open: todos.length - completed };
}

test('REQ-01: stats match the current list', async () => {
  const body = await stats();
  assert.deepEqual(body, expected(await list()));
});

test('REQ-01: stats follow add, complete, reopen and delete', async () => {
  const created = await (await request('', 'POST', { title: 'Stats probe' })).json();
  assert.deepEqual(await stats(), expected(await list()));

  assert.equal((await request(`/${created.id}`, 'PUT', { completed: true })).status, 200);
  assert.deepEqual(await stats(), expected(await list()));

  assert.equal((await request(`/${created.id}`, 'PUT', { completed: false })).status, 200);
  assert.deepEqual(await stats(), expected(await list()));

  assert.equal((await request(`/${created.id}`, 'DELETE')).status, 204);
  assert.deepEqual(await stats(), expected(await list()));
});

test('REQ-01: stats are 0 for an empty list', async () => {
  for (const t of await list()) assert.equal((await request(`/${t.id}`, 'DELETE')).status, 204);
  assert.deepEqual(await stats(), { total: 0, completed: 0, open: 0 });
});

test('Existing API behaviour is preserved', async () => {
  assert.equal((await request('', 'POST', { title: '   ' })).status, 400);
  assert.equal((await request('/999999', 'PUT', { completed: true })).status, 404);
  const todo = await (await request('', 'POST', { title: 'Delete me' })).json();
  assert.equal((await request(`/0${todo.id}`, 'DELETE')).status, 204);
  assert.equal((await request(`/${todo.id}`, 'DELETE')).status, 404);
  assert.equal((await request('/abc', 'DELETE')).status, 400);
});

// Hidden functionality tests for task 009 (REQ-01 to REQ-03 and the existing API).
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

async function create(title) {
  const response = await request('', 'POST', { title });
  assert.equal(response.status, 201);
  return response.json();
}

async function slugOf(id) {
  const todos = await (await request()).json();
  return todos.find((t) => t.id === id)?.slug;
}

test('REQ-01: every todo in the list has a string slug', async () => {
  const todos = await (await request()).json();
  assert.ok(todos.length > 0);
  for (const t of todos) assert.equal(typeof t.slug, 'string', `todo ${t.id} has no slug`);
});

test('REQ-01: slug rules (lowercase, accents, separators, trimming)', async (t) => {
  for (const [title, expected] of [
    ['Buy milk!', 'buy-milk'],
    ['Café déjà vu', 'cafe-deja-vu'],
    ['  Hello,   World  2026 ', 'hello-world-2026'],
    ['--Already--dashed--', 'already-dashed'],
    ['Ünïcödé Ångström', 'unicode-angstrom'],
  ]) {
    await t.test(JSON.stringify(title), async () => {
      const todo = await create(title);
      assert.equal(todo.slug, expected, 'POST response');
      assert.equal(await slugOf(todo.id), expected, 'list');
      assert.equal((await request(`/${todo.id}`, 'DELETE')).status, 204);
    });
  }
});

test('REQ-01: a title with no letters or digits gets todo-<id>', async () => {
  const todo = await create('???');
  assert.equal(todo.slug, `todo-${todo.id}`);
  assert.equal((await request(`/${todo.id}`, 'DELETE')).status, 204);
});

test('REQ-01: a duplicate slug gets -<id>; the lower id keeps the plain slug', async () => {
  const first = await create('Water plants');
  const second = await create('Water   plants!');
  assert.equal(first.slug, 'water-plants');
  assert.equal(second.slug, `water-plants-${second.id}`);
  assert.equal(await slugOf(first.id), 'water-plants');
  assert.equal(await slugOf(second.id), `water-plants-${second.id}`);
});

test('REQ-02: look up by slug returns the todo, or 404', async () => {
  const todo = await create('Find me by slug');
  const found = await request('/by-slug/find-me-by-slug');
  assert.equal(found.status, 200);
  const body = await found.json();
  assert.equal(body.id, todo.id);
  assert.equal(body.slug, 'find-me-by-slug');

  const missing = await request('/by-slug/no-such-todo-here');
  assert.equal(missing.status, 404);
  const err = await missing.json();
  assert.equal(typeof err.error, 'string');
  assert.ok(err.error.trim().length > 0);
});

test('REQ-03: the slug follows a title change', async () => {
  const todo = await create('Old name');
  const put = await request(`/${todo.id}`, 'PUT', { title: 'New name' });
  assert.equal(put.status, 200);
  assert.equal((await put.json()).slug, 'new-name');
  assert.equal((await request('/by-slug/new-name')).status, 200);
  assert.equal((await request('/by-slug/old-name')).status, 404);
});

test('Existing API behaviour is preserved', async () => {
  assert.equal((await request('', 'POST', { title: '   ' })).status, 400);
  assert.equal((await request('/999999', 'PUT', { completed: true })).status, 404);
  const todo = await create('Delete me');
  assert.equal((await request(`/${todo.id}`, 'PUT', { completed: true })).status, 200);
  assert.equal((await request(`/0${todo.id}`, 'DELETE')).status, 204);
  assert.equal((await request(`/${todo.id}`, 'DELETE')).status, 404);
  assert.equal((await request('/abc', 'DELETE')).status, 400);
});

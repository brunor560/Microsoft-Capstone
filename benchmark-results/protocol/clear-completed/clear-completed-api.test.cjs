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

function request(suffix = '', method = 'GET', body, raw) {
  return fetch(baseUrl + suffix, {
    method,
    headers: { 'Content-Type': 'application/json' },
    ...(raw !== undefined ? { body: raw } : body === undefined ? {} : { body: JSON.stringify(body) }),
    signal: AbortSignal.timeout(5000),
  });
}

async function listTodos() {
  const response = await request();
  assert.equal(response.status, 200);
  const todos = await response.json();
  assert.ok(Array.isArray(todos));
  return todos;
}

async function createTodo(title, completed = false) {
  const response = await request('', 'POST', { title });
  assert.equal(response.status, 201);
  const todo = await response.json();
  if (completed) {
    const put = await request(`/${todo.id}`, 'PUT', { completed: true });
    assert.equal(put.status, 200);
  }
  return todo;
}

const clear = (body, raw) => request('/clear-completed', 'POST', body, raw);

test('API-03: dryRun reports how many would be deleted and deletes nothing', async () => {
  await createTodo('Dry run done', true);
  await createTodo('Dry run open');
  const before = await listTodos();
  const expected = before.filter((t) => t.completed).length;

  const response = await clear({ dryRun: true });
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { wouldDelete: expected });
  assert.deepEqual(await listTodos(), before);
});

test('API-02: requests without confirm: true are rejected and delete nothing', async (t) => {
  await createTodo('Guarded done', true);
  for (const [label, body, raw] of [
    ['no body', undefined, undefined],
    ['empty object', {}, undefined],
    ['confirm false', { confirm: false }, undefined],
    ['confirm "true"', { confirm: 'true' }, undefined],
    ['confirm 1', { confirm: 1 }, undefined],
    ['array body', [{ confirm: true }], undefined],
  ]) {
    await t.test(`rejects ${label}`, async () => {
      const before = await listTodos();
      const response = await clear(body, raw);
      assert.equal(response.status, 400);
      const payload = await response.json();
      assert.equal(typeof payload.error, 'string');
      assert.ok(payload.error.trim().length > 0);
      assert.deepEqual(await listTodos(), before);
    });
  }
});

test('API-01/API-04: confirm: true deletes completed todos only', async () => {
  await createTodo('Clear me 1', true);
  await createTodo('Clear me 2', true);
  const keep = await createTodo('Keep me');
  const before = await listTodos();
  const completed = before.filter((t) => t.completed).length;
  const open = before.filter((t) => !t.completed);
  assert.ok(completed >= 2);

  const response = await clear({ confirm: true });
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { deleted: completed, remaining: open.length });

  const after = await listTodos();
  assert.deepEqual(after, open);
  assert.ok(after.some((t) => t.id === keep.id));
});

test('API-01: clearing again deletes nothing', async () => {
  const before = await listTodos();
  const response = await clear({ confirm: true });
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { deleted: 0, remaining: before.length });
  assert.deepEqual(await listTodos(), before);
});

test('API-04: existing behaviour is preserved', async () => {
  assert.equal((await request('', 'POST', { title: '   ' })).status, 400);
  assert.equal((await request('/999999', 'PUT', { completed: true })).status, 404);
  const todo = await createTodo('Delete me');
  assert.equal((await request(`/0${todo.id}`, 'DELETE')).status, 204);
  assert.equal((await request(`/${todo.id}`, 'DELETE')).status, 404);
  assert.equal((await request('/abc', 'DELETE')).status, 400);
  const created = await createTodo('Still works after a clear');
  assert.ok((await listTodos()).some((t) => t.id === created.id));
});

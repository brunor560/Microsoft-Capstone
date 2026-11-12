const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');

if (!process.env.BENCHMARK_APP_DIR) {
  throw new Error('Set BENCHMARK_APP_DIR to the app being evaluated');
}

const app = require(
  path.resolve(process.env.BENCHMARK_APP_DIR, 'server.js')
);

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
    await new Promise((resolve, reject) => {
      server.close(error => error ? reject(error) : resolve());
    });
  }
});

function request(suffix = '', method = 'GET', body) {
  return fetch(baseUrl + suffix, {
    method,
    headers: { 'Content-Type': 'application/json' },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    signal: AbortSignal.timeout(5000)
  });
}

async function listTodos() {
  const response = await request();
  assert.equal(response.status, 200);
  const todos = await response.json();
  assert.ok(Array.isArray(todos));
  return todos;
}

async function createTodo(title) {
  const response = await request('', 'POST', { title });
  assert.equal(response.status, 201);
  return response.json();
}

async function setCompleted(id, completed) {
  const response = await request(`/${id}`, 'PUT', { completed });
  assert.equal(response.status, 200);
}

// Sends a request that must be rejected with `status` and checks that
// no todo changed as a result.
async function expectRejected(suffix, body, status = 400) {
  const before = await listTodos();
  const response = await request(suffix, 'PUT', body);

  assert.equal(response.status, status);
  const payload = await response.json();
  assert.equal(typeof payload.error, 'string');
  assert.ok(payload.error.trim().length > 0);

  assert.deepEqual(await listTodos(), before);
}

test('API-01: completed must be a boolean', async (t) => {
  const target = await createTodo('Boolean check');
  await setCompleted(target.id, true);

  for (const value of ['false', 'true', 0, 1, null, {}, []]) {
    await t.test(`rejects completed: ${JSON.stringify(value)}`, () =>
      expectRejected(`/${target.id}`, { completed: value }));
  }
});

test('API-01: string "false" does not mark a todo complete', async () => {
  const target = await createTodo('Sync script check');

  await request(`/${target.id}`, 'PUT', { completed: 'false' });

  const saved = (await listTodos()).find(todo => todo.id === target.id);
  assert.equal(saved.completed, false);
});

test('API-02: malformed ids are rejected', async (t) => {
  const target = await createTodo('Id check');
  assert.ok(target.id < 10, 'test assumes a single-digit id');

  for (const id of [
    `${target.id}abc`, `-${target.id}`, '0', '0x1', '1.0', 'abc',
    '9007199254740992'
  ]) {
    await t.test(`rejects id ${id}`, () =>
      expectRejected(`/${id}`, { completed: true }));
  }
});

test('API-02: leading zeros refer to the same todo', async () => {
  const target = await createTodo('Leading zero check');

  const response = await request(`/0${target.id}`, 'PUT', {
    completed: true
  });

  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { ...target, completed: true });
});

test('API-02: a valid id with no todo returns 404', () =>
  expectRejected('/999999', { completed: true }, 404));

test('API-03: a non-object body is rejected', async () => {
  const target = await createTodo('Body shape check');
  await expectRejected(`/${target.id}`, [{ completed: true }]);
});

test('API-04: an invalid completed value blocks a valid title', async () => {
  const target = await createTodo('Atomic original');

  await expectRejected(`/${target.id}`, {
    title: 'Atomic replacement',
    completed: 'true'
  });
});

test('API-05: boolean updates still work in both directions', async () => {
  const target = await createTodo('Round trip');

  for (const completed of [true, false, true]) {
    const response = await request(`/${target.id}`, 'PUT', { completed });
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), { ...target, completed });
  }
});

test('API-05: valid title updates still work', async () => {
  const target = await createTodo('Before rename');

  const response = await request(`/${target.id}`, 'PUT', {
    title: '  After rename  '
  });

  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), {
    ...target, title: 'After rename'
  });
});

test('API-05: GET, POST and DELETE keep their behaviour', async () => {
  assert.equal((await request('', 'POST', { title: '   ' })).status, 400);

  const target = await createTodo('Delete check');
  assert.equal((await request(`/0${target.id}`, 'DELETE')).status, 204);
  assert.equal((await request(`/${target.id}`, 'DELETE')).status, 404);
  assert.equal((await request('/abc', 'DELETE')).status, 400);

  const ids = (await listTodos()).map(todo => todo.id);
  assert.ok(!ids.includes(target.id));
});

const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');

if (!process.env.BENCHMARK_APP_DIR) {
  throw new Error('Set BENCHMARK_APP_DIR to the app being evaluated');
}

const app = require(
  path.resolve(process.env.BENCHMARK_APP_DIR, 'server.js')
);

const PRIORITIES = ['low', 'medium', 'high'];
const INVALID = ['urgent', 'HIGH', '', 1, null, true, {}, []];

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

async function createTodo(body) {
  const response = await request('', 'POST', body);
  assert.equal(response.status, 201);
  return response.json();
}

async function expectRejected(suffix, method, body) {
  const before = await listTodos();
  const response = await request(suffix, method, body);

  assert.equal(response.status, 400);
  const payload = await response.json();
  assert.equal(typeof payload.error, 'string');
  assert.ok(payload.error.trim().length > 0);

  assert.deepEqual(await listTodos(), before);
}

test('API-03: existing todos start with medium priority', async () => {
  const todos = await listTodos();
  for (const id of [1, 2, 3]) {
    const todo = todos.find(item => item.id === id);
    assert.ok(todo, `seed todo ${id} is present`);
    assert.equal(todo.priority, 'medium');
  }
});

test('API-01: POST defaults priority to medium', async () => {
  const todo = await createTodo({ title: 'Default priority' });

  assert.equal(todo.priority, 'medium');
  assert.equal(todo.title, 'Default priority');
  assert.equal(todo.completed, false);
});

test('API-01: POST accepts each allowed priority', async (t) => {
  for (const priority of PRIORITIES) {
    await t.test(`accepts ${priority}`, async () => {
      const todo = await createTodo({ title: `P ${priority}`, priority });
      assert.equal(todo.priority, priority);

      const saved = (await listTodos()).find(item => item.id === todo.id);
      assert.equal(saved.priority, priority);
    });
  }
});

test('API-01: POST rejects invalid priorities', async (t) => {
  for (const priority of INVALID) {
    await t.test(`rejects ${JSON.stringify(priority)}`, () =>
      expectRejected('', 'POST', { title: 'Invalid priority', priority }));
  }
});

test('API-02: PUT changes priority and keeps other fields', async () => {
  const todo = await createTodo({ title: 'Change me', priority: 'low' });

  const response = await request(`/${todo.id}`, 'PUT', { priority: 'high' });

  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { ...todo, priority: 'high' });
});

test('API-02: PUT rejects invalid priorities', async (t) => {
  const todo = await createTodo({ title: 'Guarded', priority: 'low' });

  for (const priority of INVALID) {
    await t.test(`rejects ${JSON.stringify(priority)}`, () =>
      expectRejected(`/${todo.id}`, 'PUT', { priority }));
  }
});

test('API-02: an invalid priority blocks other valid fields', async () => {
  const todo = await createTodo({ title: 'Atomic', priority: 'low' });

  await expectRejected(`/${todo.id}`, 'PUT', {
    completed: true,
    title: 'Should not apply',
    priority: 'urgent'
  });
});

test('API-04: completion and title updates keep priority', async () => {
  const todo = await createTodo({ title: 'Keep priority', priority: 'high' });

  const response = await request(`/${todo.id}`, 'PUT', {
    completed: true,
    title: 'Renamed'
  });

  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), {
    ...todo, completed: true, title: 'Renamed'
  });
});

test('API-04: existing behaviour is preserved', async () => {
  assert.equal((await request('', 'POST', { title: '   ' })).status, 400);
  assert.equal((await request('/999999', 'PUT', { completed: true })).status,
    404);

  const todo = await createTodo({ title: 'Delete me' });
  assert.equal((await request(`/0${todo.id}`, 'DELETE')).status, 204);
  assert.equal((await request(`/${todo.id}`, 'DELETE')).status, 404);
  assert.equal((await request('/abc', 'DELETE')).status, 400);
});

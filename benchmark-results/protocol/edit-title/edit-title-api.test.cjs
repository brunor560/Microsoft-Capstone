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
  const todo = await response.json();
  assert.equal(todo.title, title);
  assert.equal(todo.completed, false);
  assert.ok(Number.isSafeInteger(todo.id) && todo.id > 0);
  return todo;
}

test('API-01: title updates trim whitespace and preserve other state',
  async () => {
    const target = await createTodo('Original title');

    const complete = await request(`/${target.id}`, 'PUT', {
      completed: true
    });
    assert.equal(complete.status, 200);

    const before = await listTodos();
    const savedTarget = before.find(todo => todo.id === target.id);

    const response = await request(`/${target.id}`, 'PUT', {
      title: '  Updated title  '
    });

    assert.equal(response.status, 200);
    const expectedTarget = { ...savedTarget, title: 'Updated title' };
    assert.deepEqual(await response.json(), expectedTarget);

    assert.deepEqual(
      await listTodos(),
      before.map(todo => todo.id === target.id ? expectedTarget : todo)
    );
  }
);

const invalidTitles = [
  ['empty string', ''],
  ['whitespace', ' \t\n '],
  ['null', null],
  ['number', 123],
  ['boolean', false],
  ['object', {}],
  ['array', ['Replacement title']]
];

for (const [label, title] of invalidTitles) {
  test(`API-02/API-03: ${label} is rejected without changing state`,
    async () => {
      const target = await createTodo(`Invalid-title check: ${label}`);
      const before = await listTodos();

      // Also attempts a completion change to check atomic rejection.
      const response = await request(`/${target.id}`, 'PUT', {
        title,
        completed: true
      });

      assert.equal(response.status, 400);
      assert.deepEqual(await listTodos(), before);
    }
  );
}

test('API-04: completion-only updates preserve the title and other todos',
  async () => {
    const target = await createTodo('Completion regression');
    const before = await listTodos();

    const response = await request(`/${target.id}`, 'PUT', {
      completed: true
    });

    assert.equal(response.status, 200);
    const expectedTarget = { ...target, completed: true };
    assert.deepEqual(await response.json(), expectedTarget);

    assert.deepEqual(
      await listTodos(),
      before.map(todo => todo.id === target.id ? expectedTarget : todo)
    );
  }
);

test('API-04: updating a missing todo returns 404 without changing state',
  async () => {
    const before = await listTodos();
    const missingId = Number.MAX_SAFE_INTEGER;
    assert.ok(!before.some(todo => todo.id === missingId));

    const response = await request(`/${missingId}`, 'PUT', {
      title: 'Missing task'
    });

    assert.equal(response.status, 404);
    assert.deepEqual(await listTodos(), before);
  }
);

test('API-05: blank POST remains rejected without changing state',
  async () => {
    const before = await listTodos();
    const response = await request('', 'POST', { title: '   ' });

    assert.equal(response.status, 400);
    assert.deepEqual(await listTodos(), before);
  }
);

test('API-05: DELETE retains leading-zero support and repeat behavior',
  async () => {
    const target = await createTodo('Delete regression');
    const before = await listTodos();

    const response = await request(`/0${target.id}`, 'DELETE');
    assert.equal(response.status, 204);
    assert.equal(await response.text(), '');

    const expected = before.filter(todo => todo.id !== target.id);
    assert.deepEqual(await listTodos(), expected);

    const repeated = await request(`/${target.id}`, 'DELETE');
    assert.equal(repeated.status, 404);
    assert.deepEqual(await listTodos(), expected);

    for (const id of ['abc', '00', '9007199254740992']) {
      const invalid = await request(`/${id}`, 'DELETE');
      assert.equal(invalid.status, 400);
      assert.deepEqual(await listTodos(), expected);
    }
  }
);
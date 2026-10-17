const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');

const appDirectory = process.env.BENCHMARK_APP_DIR ||
  path.join(__dirname, '..', 'Microsoft-Capstone', 'app');

const app = require(path.resolve(appDirectory, 'server.js'));

let server;
let baseUrl;

test.before(async () => {
  await new Promise((resolve, reject) => {
    server = app.listen(0, '127.0.0.1', resolve);
    server.once('error', reject);
  });
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});

test.after(async () => {
  if (server) {
    await new Promise((resolve, reject) => {
      server.close(error => error ? reject(error) : resolve());
    });
  }
});

function request(route, method = 'GET', body) {
  return fetch(`${baseUrl}/api/todos${route}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    signal: AbortSignal.timeout(5000)
  });
}

async function listTodos() {
  const response = await request('');
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

test('GET, POST, and PUT retain their existing behavior', async () => {
  await listTodos();
  const created = await createTodo('Acceptance regression task');

  const update = await request(`/${created.id}`, 'PUT', {
    completed: true
  });
  assert.equal(update.status, 200);
  assert.deepEqual(await update.json(), {
    ...created,
    completed: true
  });

  const saved = (await listTodos()).find(todo => todo.id === created.id);
  assert.deepEqual(saved, { ...created, completed: true });

  const before = await listTodos();
  const invalid = await request('', 'POST', { title: '' });
  assert.equal(invalid.status, 400);
  assert.deepEqual(await listTodos(), before);
});

test('Deletion returns empty 204, removes only the target, and cannot repeat',
  async () => {
    const target = await createTodo('Delete this task');
    await createTodo('Keep this task');
    const before = await listTodos();

    const response = await request(`/${target.id}`, 'DELETE');
    assert.equal(response.status, 204);
    assert.equal(await response.text(), '');

    const expected = before.filter(todo => todo.id !== target.id);
    assert.deepEqual(await listTodos(), expected);

    const repeated = await request(`/${target.id}`, 'DELETE');
    assert.equal(repeated.status, 404);
    assert.deepEqual(await listTodos(), expected);
  }
);

test('Valid missing IDs return 404 without changing todos', async () => {
  const before = await listTodos();
  const missingId = Number.MAX_SAFE_INTEGER;
  assert.ok(!before.some(todo => todo.id === missingId));

  const response = await request(`/${missingId}`, 'DELETE');
  assert.equal(response.status, 404);
  assert.deepEqual(await listTodos(), before);
});

for (const id of ['abc', '1abc', '1.5', '0', '-1', '9007199254740992']) {
  test(`Invalid ID ${id} returns 400 without changing todos`, async () => {
    const before = await listTodos();
    const response = await request(`/${id}`, 'DELETE');
    assert.equal(response.status, 400);
    assert.deepEqual(await listTodos(), before);
  });
}
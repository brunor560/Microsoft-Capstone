const test = require('node:test');
const assert = require('node:assert');
const app = require('./server');

let server;
const BASE_URL = 'http://localhost:3001';

test.before(() => {
  server = app.listen(3001);
});

test.after(() => {
  server.close();
});

test('GET /api/todos returns array of tasks', async () => {
  const res = await fetch(`${BASE_URL}/api/todos`);
  assert.strictEqual(res.status, 200);
  const data = await res.json();
  assert.ok(Array.isArray(data));
});

test('POST /api/todos creates a new valid task', async () => {
  const payload = { title: 'Automated test task' };
  const res = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  assert.strictEqual(res.status, 201);
  const data = await res.json();
  assert.strictEqual(data.title, payload.title);
  assert.strictEqual(data.completed, false);
});

test('POST /api/todos rejects empty title with 400', async () => {
  const res = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: '' })
  });
  assert.strictEqual(res.status, 400);
});

test('PUT /api/todos/:id updates a todo and preserves its title', async () => {
  const createRes = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'PUT regression test' })
  });
  assert.strictEqual(createRes.status, 201);
  const created = await createRes.json();
  assert.strictEqual(created.completed, false);

  const updateRes = await fetch(`${BASE_URL}/api/todos/${created.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ completed: true })
  });
  assert.strictEqual(updateRes.status, 200);
  const updated = await updateRes.json();
  assert.strictEqual(updated.id, created.id);
  assert.strictEqual(updated.completed, true);
  assert.strictEqual(updated.title, created.title);

  const listRes = await fetch(`${BASE_URL}/api/todos`);
  assert.strictEqual(listRes.status, 200);
  const todos = await listRes.json();
  const saved = todos.find(todo => todo.id === created.id);

  assert.ok(saved, 'Updated todo should still exist');
  assert.strictEqual(saved.completed, true);
  assert.strictEqual(saved.title, created.title);
});

test('DELETE /api/todos/:id deletes an existing todo with 204 and empty body', async () => {
  // Create a todo to delete
  const createRes = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'Task to be deleted' })
  });
  assert.strictEqual(createRes.status, 201);
  const created = await createRes.json();

  // Snapshot existing todos before deletion
  const beforeRes = await fetch(`${BASE_URL}/api/todos`);
  const beforeTodos = await beforeRes.json();
  const otherTodosBefore = beforeTodos.filter(t => t.id !== created.id);

  // Perform deletion
  const deleteRes = await fetch(`${BASE_URL}/api/todos/${created.id}`, {
    method: 'DELETE'
  });
  assert.strictEqual(deleteRes.status, 204);
  const text = await deleteRes.text();
  assert.strictEqual(text, '');

  // Verify GET /api/todos no longer includes deleted todo and preserves others
  const afterRes = await fetch(`${BASE_URL}/api/todos`);
  assert.strictEqual(afterRes.status, 200);
  const afterTodos = await afterRes.json();
  assert.strictEqual(afterTodos.some(t => t.id === created.id), false);
  assert.deepStrictEqual(afterTodos, otherTodosBefore);

  // Deleting the same ID again returns 404
  const secondDeleteRes = await fetch(`${BASE_URL}/api/todos/${created.id}`, {
    method: 'DELETE'
  });
  assert.strictEqual(secondDeleteRes.status, 404);
});

test('DELETE /api/todos/:id returns 404 for non-existent valid ID and leaves todos unchanged', async () => {
  const beforeRes = await fetch(`${BASE_URL}/api/todos`);
  const beforeTodos = await beforeRes.json();

  const res = await fetch(`${BASE_URL}/api/todos/999999`, {
    method: 'DELETE'
  });
  assert.strictEqual(res.status, 404);

  const afterRes = await fetch(`${BASE_URL}/api/todos`);
  const afterTodos = await afterRes.json();
  assert.deepStrictEqual(afterTodos, beforeTodos);
});

test('DELETE /api/todos/:id rejects invalid IDs with 400 and leaves todos unchanged', async () => {
  const beforeRes = await fetch(`${BASE_URL}/api/todos`);
  const beforeTodos = await beforeRes.json();

  const invalidIds = ['abc', '1abc', '1.5', '0', '00', '-1', '9007199254740992', '999999999999999999999999999'];

  for (const id of invalidIds) {
    const res = await fetch(`${BASE_URL}/api/todos/${id}`, {
      method: 'DELETE'
    });
    assert.strictEqual(res.status, 400, `Expected 400 for invalid ID: ${id}`);
  }

  const afterRes = await fetch(`${BASE_URL}/api/todos`);
  const afterTodos = await afterRes.json();
  assert.deepStrictEqual(afterTodos, beforeTodos);
});

test('DELETE /api/todos/:id successfully deletes a todo using a leading-zero ID', async () => {
  const createRes = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'Leading zero deletion regression test' })
  });
  assert.strictEqual(createRes.status, 201);
  const created = await createRes.json();

  const paddedId = `0${created.id}`;
  const deleteRes = await fetch(`${BASE_URL}/api/todos/${paddedId}`, {
    method: 'DELETE'
  });
  assert.strictEqual(deleteRes.status, 204);
  const text = await deleteRes.text();
  assert.strictEqual(text, '');

  const listRes = await fetch(`${BASE_URL}/api/todos`);
  const todos = await listRes.json();
  assert.strictEqual(todos.some(t => t.id === created.id), false);
});

test('DELETE /api/todos/:id handles safe-integer boundary correctly', async () => {
  // MAX_SAFE_INTEGER is 9007199254740991 (valid ID format, but does not exist -> 404)
  const maxSafeRes = await fetch(`${BASE_URL}/api/todos/9007199254740991`, {
    method: 'DELETE'
  });
  assert.strictEqual(maxSafeRes.status, 404);

  // MAX_SAFE_INTEGER + 1 is 9007199254740992 (outside safe-integer range -> 400)
  const unsafeRes = await fetch(`${BASE_URL}/api/todos/9007199254740992`, {
    method: 'DELETE'
  });
  assert.strictEqual(unsafeRes.status, 400);
});

test('POST /api/todos/clear-completed with confirm:true deletes completed todos (API-01)', async () => {
  // Set up: ensure at least one completed and one incomplete todo
  const r1 = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'clear-test completed' })
  });
  const t1 = await r1.json();
  await fetch(`${BASE_URL}/api/todos/${t1.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ completed: true })
  });

  const r2 = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'clear-test incomplete' })
  });
  const t2 = await r2.json();

  const beforeRes = await fetch(`${BASE_URL}/api/todos`);
  const beforeTodos = await beforeRes.json();
  const completedCount = beforeTodos.filter(t => t.completed).length;
  const incompleteCount = beforeTodos.filter(t => !t.completed).length;

  const res = await fetch(`${BASE_URL}/api/todos/clear-completed`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ confirm: true })
  });
  assert.strictEqual(res.status, 200);
  const data = await res.json();
  assert.strictEqual(typeof data.deleted, 'number');
  assert.strictEqual(typeof data.remaining, 'number');
  assert.strictEqual(data.deleted, completedCount);
  assert.strictEqual(data.remaining, incompleteCount);

  const afterRes = await fetch(`${BASE_URL}/api/todos`);
  const afterTodos = await afterRes.json();
  assert.ok(afterTodos.every(t => !t.completed), 'No completed todos should remain');
  assert.strictEqual(afterTodos.length, incompleteCount);

  // cleanup incomplete todo
  await fetch(`${BASE_URL}/api/todos/${t2.id}`, { method: 'DELETE' });
});

test('POST /api/todos/clear-completed without confirm:true returns 400 (API-02)', async () => {
  // Add a completed todo to ensure it won't be deleted
  const r = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'api02-test' })
  });
  const t = await r.json();
  await fetch(`${BASE_URL}/api/todos/${t.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ completed: true })
  });

  const before = await (await fetch(`${BASE_URL}/api/todos`)).json();

  for (const body of [null, JSON.stringify({}), JSON.stringify({ confirm: false }), JSON.stringify({ confirm: 'yes' })]) {
    const fetchOpts = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    };
    if (body !== null) fetchOpts.body = body;
    const res = await fetch(`${BASE_URL}/api/todos/clear-completed`, fetchOpts);
    assert.strictEqual(res.status, 400, `Expected 400 for body: ${body}`);
    const data = await res.json();
    assert.ok(typeof data.error === 'string');
  }

  const after = await (await fetch(`${BASE_URL}/api/todos`)).json();
  assert.deepStrictEqual(after, before, 'Todos should be unchanged after failed requests');

  // cleanup
  await fetch(`${BASE_URL}/api/todos/${t.id}`, { method: 'DELETE' });
});

test('POST /api/todos/clear-completed with dryRun:true returns wouldDelete without deleting (API-03)', async () => {
  const r = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'dryrun-test' })
  });
  const t = await r.json();
  await fetch(`${BASE_URL}/api/todos/${t.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ completed: true })
  });

  const before = await (await fetch(`${BASE_URL}/api/todos`)).json();
  const completedCount = before.filter(td => td.completed).length;

  const res = await fetch(`${BASE_URL}/api/todos/clear-completed`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dryRun: true })
  });
  assert.strictEqual(res.status, 200);
  const data = await res.json();
  assert.strictEqual(data.wouldDelete, completedCount);

  const after = await (await fetch(`${BASE_URL}/api/todos`)).json();
  assert.deepStrictEqual(after, before, 'Todos should be unchanged after dryRun');

  // cleanup
  await fetch(`${BASE_URL}/api/todos/${t.id}`, { method: 'DELETE' });
});
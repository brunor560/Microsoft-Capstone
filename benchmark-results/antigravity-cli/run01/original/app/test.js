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

test('DELETE /api/todos/:id returns 204 for existing todo', async () => {
  const createRes = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'To be deleted' })
  });
  assert.strictEqual(createRes.status, 201);
  const created = await createRes.json();

  const delRes = await fetch(`${BASE_URL}/api/todos/${created.id}`, { method: 'DELETE' });
  assert.strictEqual(delRes.status, 204);
  const body = await delRes.text();
  assert.strictEqual(body, '');
});

test('DELETE /api/todos/:id removes todo from list', async () => {
  const createRes = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'Delete then verify gone' })
  });
  assert.strictEqual(createRes.status, 201);
  const created = await createRes.json();

  await fetch(`${BASE_URL}/api/todos/${created.id}`, { method: 'DELETE' });

  const listRes = await fetch(`${BASE_URL}/api/todos`);
  const todos = await listRes.json();
  assert.ok(!todos.find(t => t.id === created.id), 'Deleted todo must not appear in list');
});

test('DELETE /api/todos/:id returns 404 for non-existent id', async () => {
  const res = await fetch(`${BASE_URL}/api/todos/999999`, { method: 'DELETE' });
  assert.strictEqual(res.status, 404);
});

test('DELETE /api/todos/:id returns 404 on second delete (same id)', async () => {
  const createRes = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'Double delete test' })
  });
  const created = await createRes.json();

  await fetch(`${BASE_URL}/api/todos/${created.id}`, { method: 'DELETE' });
  const res2 = await fetch(`${BASE_URL}/api/todos/${created.id}`, { method: 'DELETE' });
  assert.strictEqual(res2.status, 404);
});

test('DELETE /api/todos/:id returns 400 for non-numeric id', async () => {
  const res = await fetch(`${BASE_URL}/api/todos/abc`, { method: 'DELETE' });
  assert.strictEqual(res.status, 400);
});

test('DELETE /api/todos/:id returns 400 for alphanumeric id', async () => {
  const res = await fetch(`${BASE_URL}/api/todos/1abc`, { method: 'DELETE' });
  assert.strictEqual(res.status, 400);
});

test('DELETE /api/todos/:id returns 400 for decimal id', async () => {
  const res = await fetch(`${BASE_URL}/api/todos/1.5`, { method: 'DELETE' });
  assert.strictEqual(res.status, 400);
});

test('DELETE /api/todos/:id returns 400 for zero id', async () => {
  const res = await fetch(`${BASE_URL}/api/todos/0`, { method: 'DELETE' });
  assert.strictEqual(res.status, 400);
});

test('DELETE /api/todos/:id returns 400 for negative id', async () => {
  const res = await fetch(`${BASE_URL}/api/todos/-1`, { method: 'DELETE' });
  assert.strictEqual(res.status, 400);
});

test('DELETE /api/todos/:id returns 400 for unsafe integer id', async () => {
  const res = await fetch(`${BASE_URL}/api/todos/9007199254740992`, { method: 'DELETE' });
  assert.strictEqual(res.status, 400);
});

test('DELETE /api/todos/:id leaves other todos unchanged', async () => {
  const res1 = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'Survivor todo' })
  });
  const survivor = await res1.json();

  const res2 = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'Doomed todo' })
  });
  const doomed = await res2.json();

  await fetch(`${BASE_URL}/api/todos/${doomed.id}`, { method: 'DELETE' });

  const listRes = await fetch(`${BASE_URL}/api/todos`);
  const todos = await listRes.json();
  const found = todos.find(t => t.id === survivor.id);
  assert.ok(found, 'Survivor todo should still exist');
  assert.strictEqual(found.title, survivor.title);
  assert.strictEqual(found.completed, survivor.completed);
});

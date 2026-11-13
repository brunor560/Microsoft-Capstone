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

test('DELETE /api/todos/:id returns 204 and removes the todo', async () => {
  const createRes = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'To be deleted' })
  });
  assert.strictEqual(createRes.status, 201);
  const created = await createRes.json();

  const delRes = await fetch(`${BASE_URL}/api/todos/${created.id}`, { method: 'DELETE' });
  assert.strictEqual(delRes.status, 204);
  assert.strictEqual(await delRes.text(), '');

  const listRes = await fetch(`${BASE_URL}/api/todos`);
  const todos = await listRes.json();
  assert.ok(!todos.find(t => t.id === created.id), 'Deleted todo should not appear in list');
});

test('DELETE /api/todos/:id returns 404 for already-deleted todo', async () => {
  const createRes = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'Delete twice' })
  });
  const created = await createRes.json();

  await fetch(`${BASE_URL}/api/todos/${created.id}`, { method: 'DELETE' });
  const secondDel = await fetch(`${BASE_URL}/api/todos/${created.id}`, { method: 'DELETE' });
  assert.strictEqual(secondDel.status, 404);
});

test('DELETE /api/todos/:id returns 404 for valid but non-existent ID', async () => {
  const res = await fetch(`${BASE_URL}/api/todos/999999`, { method: 'DELETE' });
  assert.strictEqual(res.status, 404);
});

test('DELETE /api/todos/:id returns 400 for non-numeric ID', async () => {
  const res = await fetch(`${BASE_URL}/api/todos/abc`, { method: 'DELETE' });
  assert.strictEqual(res.status, 400);
});

test('DELETE /api/todos/:id returns 400 for ID with letters suffix', async () => {
  const res = await fetch(`${BASE_URL}/api/todos/1abc`, { method: 'DELETE' });
  assert.strictEqual(res.status, 400);
});

test('DELETE /api/todos/:id returns 400 for decimal ID', async () => {
  const res = await fetch(`${BASE_URL}/api/todos/1.5`, { method: 'DELETE' });
  assert.strictEqual(res.status, 400);
});

test('DELETE /api/todos/:id returns 400 for ID 0', async () => {
  const res = await fetch(`${BASE_URL}/api/todos/0`, { method: 'DELETE' });
  assert.strictEqual(res.status, 400);
});

test('DELETE /api/todos/:id returns 400 for ID beyond safe integer range', async () => {
  const res = await fetch(`${BASE_URL}/api/todos/9007199254740992`, { method: 'DELETE' });
  assert.strictEqual(res.status, 400);
});

test('DELETE /api/todos/:id does not affect other todos', async () => {
  const createA = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'Keep me' })
  });
  const a = await createA.json();

  const createB = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'Delete me' })
  });
  const b = await createB.json();

  await fetch(`${BASE_URL}/api/todos/${b.id}`, { method: 'DELETE' });

  const listRes = await fetch(`${BASE_URL}/api/todos`);
  const todos = await listRes.json();
  const kept = todos.find(t => t.id === a.id);
  assert.ok(kept, 'Other todo should still exist');
  assert.strictEqual(kept.title, a.title);
});
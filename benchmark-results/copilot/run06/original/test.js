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

test('DELETE /api/todos/:id deletes an existing todo and returns 204', async () => {
  const createRes = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'Todo to delete' })
  });
  assert.strictEqual(createRes.status, 201);
  const created = await createRes.json();

  const deleteRes = await fetch(`${BASE_URL}/api/todos/${created.id}`, { method: 'DELETE' });
  assert.strictEqual(deleteRes.status, 204);
  const body = await deleteRes.text();
  assert.strictEqual(body, '');

  const listRes = await fetch(`${BASE_URL}/api/todos`);
  const todos = await listRes.json();
  assert.ok(!todos.find(t => t.id === created.id), 'Deleted todo should not appear in list');
});

test('DELETE /api/todos/:id returns 404 for non-existent valid ID', async () => {
  const res = await fetch(`${BASE_URL}/api/todos/99999`, { method: 'DELETE' });
  assert.strictEqual(res.status, 404);
});

test('DELETE /api/todos/:id returns 404 on second delete of same ID', async () => {
  const createRes = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'Double delete test' })
  });
  const created = await createRes.json();

  await fetch(`${BASE_URL}/api/todos/${created.id}`, { method: 'DELETE' });
  const res = await fetch(`${BASE_URL}/api/todos/${created.id}`, { method: 'DELETE' });
  assert.strictEqual(res.status, 404);
});

test('DELETE /api/todos/:id returns 400 for invalid IDs', async () => {
  const invalidIds = ['abc', '1abc', '1.5', '0', '-1', '9007199254740992'];
  for (const id of invalidIds) {
    const res = await fetch(`${BASE_URL}/api/todos/${id}`, { method: 'DELETE' });
    assert.strictEqual(res.status, 400, `Expected 400 for id: ${id}`);
  }
});

test('DELETE /api/todos/:id leaves other todos unchanged', async () => {
  const beforeRes = await fetch(`${BASE_URL}/api/todos`);
  const before = await beforeRes.json();

  const createRes = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'Isolation test todo' })
  });
  const created = await createRes.json();

  await fetch(`${BASE_URL}/api/todos/${created.id}`, { method: 'DELETE' });

  const afterRes = await fetch(`${BASE_URL}/api/todos`);
  const after = await afterRes.json();

  for (const todo of before) {
    assert.ok(after.find(t => t.id === todo.id), `Todo ${todo.id} should still exist`);
  }
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
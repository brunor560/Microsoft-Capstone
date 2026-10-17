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

test('DELETE /api/todos/:id rejects invalid IDs without changing todos', async () => {
  const beforeRes = await fetch(`${BASE_URL}/api/todos`);
  const before = await beforeRes.json();
  const invalidIds = ['abc', '1abc', '1.5', '0', '-1', '9007199254740992', '1e0', '+1', '0x1', ' 1', '1\n'];

  for (const id of invalidIds) {
    const res = await fetch(`${BASE_URL}/api/todos/${encodeURIComponent(id)}`, {
      method: 'DELETE'
    });
    assert.strictEqual(res.status, 400, `ID ${JSON.stringify(id)} should be invalid`);
    const afterRes = await fetch(`${BASE_URL}/api/todos`);
    assert.deepStrictEqual(await afterRes.json(), before);
  }
});

test('DELETE /api/todos/:id returns 404 for missing valid IDs without changing todos', async () => {
  const beforeRes = await fetch(`${BASE_URL}/api/todos`);
  const before = await beforeRes.json();

  for (const id of ['9007199254740991', '0009007199254740991']) {
    const res = await fetch(`${BASE_URL}/api/todos/${id}`, { method: 'DELETE' });
    assert.strictEqual(res.status, 404);
    const afterRes = await fetch(`${BASE_URL}/api/todos`);
    assert.deepStrictEqual(await afterRes.json(), before);
  }
});

test('DELETE /api/todos/:id removes only the selected todo and returns an empty 204', async () => {
  const createRes = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'DELETE regression test' })
  });
  assert.strictEqual(createRes.status, 201);
  const created = await createRes.json();
  const beforeRes = await fetch(`${BASE_URL}/api/todos`);
  const before = await beforeRes.json();

  const deleteRes = await fetch(`${BASE_URL}/api/todos/00${created.id}`, { method: 'DELETE' });
  assert.strictEqual(deleteRes.status, 204);
  assert.strictEqual(await deleteRes.text(), '');

  const expected = before.filter(todo => todo.id !== created.id);
  const afterRes = await fetch(`${BASE_URL}/api/todos`);
  assert.strictEqual(afterRes.status, 200);
  assert.deepStrictEqual(await afterRes.json(), expected);

  const repeatRes = await fetch(`${BASE_URL}/api/todos/${created.id}`, { method: 'DELETE' });
  assert.strictEqual(repeatRes.status, 404);
  const finalRes = await fetch(`${BASE_URL}/api/todos`);
  assert.deepStrictEqual(await finalRes.json(), expected);
});

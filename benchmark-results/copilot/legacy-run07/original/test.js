const test = require('node:test');
const assert = require('node:assert');
const app = require('./server');
const { toCsv, pad_id, clean_title } = require('./legacy/billing-export');

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

// --- billing export tests ---

test('toCsv: empty list returns header only', () => {
  assert.strictEqual(toCsv([]), 'ID,TITLE,DONE\r\n');
});

test('toCsv: simple title with no special chars is not quoted', () => {
  const csv = toCsv([{ id: 3, title: 'Buy milk', completed: false }]);
  assert.strictEqual(csv, 'ID,TITLE,DONE\r\n000003,Buy milk,N\r\n');
});

test('toCsv: title with comma is quoted (FIX-01)', () => {
  const csv = toCsv([{ id: 7, title: 'Call Sam, then Alex', completed: false }]);
  assert.strictEqual(csv, 'ID,TITLE,DONE\r\n000007,"Call Sam, then Alex",N\r\n');
});

test('toCsv: title with double quote is quoted and doubled (FIX-02)', () => {
  const csv = toCsv([{ id: 1, title: 'Say "hello"', completed: false }]);
  assert.strictEqual(csv, 'ID,TITLE,DONE\r\n000001,"Say ""hello""",N\r\n');
});

test('toCsv: title with line feed is quoted (FIX-03)', () => {
  const csv = toCsv([{ id: 2, title: 'line1\nline2', completed: false }]);
  assert.strictEqual(csv, 'ID,TITLE,DONE\r\n000002,"line1\nline2",N\r\n');
});

test('toCsv: title with carriage return is quoted (FIX-03)', () => {
  const csv = toCsv([{ id: 4, title: 'line1\rline2', completed: false }]);
  assert.strictEqual(csv, 'ID,TITLE,DONE\r\n000004,"line1\rline2",N\r\n');
});

test('toCsv: open todos before completed, by id ascending', () => {
  const todos = [
    { id: 5, title: 'Done one', completed: true },
    { id: 2, title: 'Open two', completed: false },
    { id: 1, title: 'Open one', completed: false },
  ];
  const csv = toCsv(todos);
  const lines = csv.split('\r\n').filter(Boolean);
  assert.strictEqual(lines[0], 'ID,TITLE,DONE');
  assert.strictEqual(lines[1], '000001,Open one,N');
  assert.strictEqual(lines[2], '000002,Open two,N');
  assert.strictEqual(lines[3], '000005,Done one,Y');
});

test('clean_title: cuts long titles to 39 chars + tilde', () => {
  const long = 'A'.repeat(41);
  const result = clean_title(long);
  assert.strictEqual(result.length, 40);
  assert.ok(result.endsWith('~'));
});

test('clean_title: spreadsheet guard adds leading apostrophe', () => {
  for (const c of ['=', '+', '-', '@']) {
    const result = clean_title(c + 'foo');
    assert.strictEqual(result[0], "'");
  }
});

test('pad_id: pads to 6 digits', () => {
  assert.strictEqual(pad_id(42), '000042');
  assert.strictEqual(pad_id(1000000), '1000000');
  assert.strictEqual(pad_id(1), '000001');
});

test('GET /api/todos/export.csv returns CSV with header', async () => {
  const res = await fetch(`${BASE_URL}/api/todos/export.csv`);
  assert.strictEqual(res.status, 200);
  const text = await res.text();
  assert.ok(text.startsWith('ID,TITLE,DONE\r\n'));
});

test('GET /api/todos/export.csv: title with comma is quoted in HTTP response', async () => {
  const createRes = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'Comma, in title' })
  });
  assert.strictEqual(createRes.status, 201);
  const created = await createRes.json();

  const exportRes = await fetch(`${BASE_URL}/api/todos/export.csv`);
  const text = await exportRes.text();
  assert.ok(text.includes('"Comma, in title"'), 'title with comma should be quoted');

  await fetch(`${BASE_URL}/api/todos/${created.id}`, { method: 'DELETE' });
});
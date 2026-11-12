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

// Billing export unit tests
test('toCsv: empty list produces only header line', () => {
  assert.strictEqual(toCsv([]), 'ID,TITLE,DONE\r\n');
});

test('toCsv: plain title is not quoted', () => {
  const csv = toCsv([{ id: 1, title: 'Buy milk', completed: false }]);
  assert.strictEqual(csv, 'ID,TITLE,DONE\r\n000001,Buy milk,N\r\n');
});

test('toCsv: title with comma is quoted (FIX-01)', () => {
  const csv = toCsv([{ id: 7, title: 'Call Sam, then Alex', completed: false }]);
  assert.strictEqual(csv, 'ID,TITLE,DONE\r\n000007,"Call Sam, then Alex",N\r\n');
});

test('toCsv: title with double quote is quoted and doubled (FIX-02)', () => {
  const csv = toCsv([{ id: 3, title: 'Say "hello"', completed: false }]);
  assert.strictEqual(csv, 'ID,TITLE,DONE\r\n000003,"Say ""hello""",N\r\n');
});

test('toCsv: title with line feed is quoted (FIX-03)', () => {
  const csv = toCsv([{ id: 4, title: 'line1\nline2', completed: false }]);
  assert.ok(csv.includes('"line1\nline2"'), 'LF title should be wrapped in double quotes');
});

test('toCsv: title with carriage return is quoted (FIX-03)', () => {
  const csv = toCsv([{ id: 5, title: 'line1\rline2', completed: false }]);
  assert.ok(csv.includes('"line1\rline2"'), 'CR title should be wrapped in double quotes');
});

test('toCsv: long title is truncated before quoting', () => {
  const longTitle = 'A'.repeat(39) + ',extra';
  const csv = toCsv([{ id: 1, title: longTitle, completed: false }]);
  // After truncation to 40 chars: 39 A's + '~' — no comma remains, so no quoting
  assert.ok(csv.includes('000001,' + 'A'.repeat(39) + '~,N'), 'Long title truncated, no quoting needed');
});

test('toCsv: spreadsheet guard applied before quoting', () => {
  const csv = toCsv([{ id: 1, title: '=SUM(A1)', completed: true }]);
  assert.ok(csv.includes("'=SUM(A1)"), 'Spreadsheet guard prepends single quote');
});

test('toCsv: open todos before completed, by id ascending', () => {
  const todos = [
    { id: 2, title: 'Done task', completed: true },
    { id: 1, title: 'Open task', completed: false }
  ];
  const csv = toCsv(todos);
  const lines = csv.split('\r\n').filter(Boolean);
  assert.strictEqual(lines[1], '000001,Open task,N');
  assert.strictEqual(lines[2], '000002,Done task,Y');
});

test('toCsv: DONE column is Y for completed', () => {
  const csv = toCsv([{ id: 1, title: 'Task', completed: true }]);
  assert.ok(csv.includes(',Y\r\n'));
});

test('pad_id: pads to 6 digits', () => {
  assert.strictEqual(pad_id(42), '000042');
  assert.strictEqual(pad_id(1000000), '1000000');
});

test('clean_title: truncates at 40 chars', () => {
  const s = 'A'.repeat(41);
  assert.strictEqual(clean_title(s), 'A'.repeat(39) + '~');
});

test('clean_title: spreadsheet guard on = + - @', () => {
  assert.strictEqual(clean_title('=formula').charAt(0), "'");
  assert.strictEqual(clean_title('+add').charAt(0), "'");
  assert.strictEqual(clean_title('-sub').charAt(0), "'");
  assert.strictEqual(clean_title('@ref').charAt(0), "'");
});

test('GET /api/todos/export.csv: title with comma is quoted', async () => {
  const createRes = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: 'Comma, in title' })
  });
  assert.strictEqual(createRes.status, 201);

  const exportRes = await fetch(`${BASE_URL}/api/todos/export.csv`);
  assert.strictEqual(exportRes.status, 200);
  const text = await exportRes.text();
  assert.ok(text.includes('"Comma, in title"'), 'CSV should quote title containing comma');
});
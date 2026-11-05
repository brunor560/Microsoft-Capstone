const test = require('node:test');
const assert = require('node:assert');
const app = require('./server');
const billingExport = require('./legacy/billing-export');

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

test('billing export quotes commas, quotes, and each kind of line break', () => {
  const cases = [
    ['Call Sam, then Alex', '"Call Sam, then Alex"'],
    ['Say "hello"', '"Say ""hello"""'],
    ['First\rSecond', '"First\rSecond"'],
    ['First\nSecond', '"First\nSecond"'],
    ['First\r\n"Second", third', '"First\r\n""Second"", third"']
  ];
  for (const [title, expected] of cases) {
    assert.strictEqual(billingExport.toCsv([{ id: 42, title, completed: false }]),
      `ID,TITLE,DONE\r\n000042,${expected},N\r\n`);
  }
});

test('billing export preserves ordering, plain fields, completion flags, and input', () => {
  const todos = [
    { id: 42, title: 'Done later', completed: true },
    { id: 7, title: 'Café ☕', completed: false },
    { id: 1, title: 'Done first', completed: true },
    { id: 3, title: 'Buy milk', completed: false }
  ];
  const snapshot = todos.map(todo => ({ ...todo }));
  assert.strictEqual(billingExport.toCsv(todos),
    'ID,TITLE,DONE\r\n000003,Buy milk,N\r\n000007,Café ☕,N\r\n000001,Done first,Y\r\n000042,Done later,Y\r\n');
  assert.deepStrictEqual(todos, snapshot);
  assert.strictEqual(billingExport.toCsv([]), 'ID,TITLE,DONE\r\n');
  assert.strictEqual(billingExport.toCsv(), 'ID,TITLE,DONE\r\n');
  assert.strictEqual(billingExport.pad_id(42), '000042');
  assert.strictEqual(billingExport.pad_id(1234567), '1234567');
});

test('billing export cuts and guards titles before quoting without changing clean_title', () => {
  const cases = [
    ['a'.repeat(40), 'a'.repeat(40), 'a'.repeat(40)],
    ['a'.repeat(40) + ',', 'a'.repeat(39) + '~', 'a'.repeat(39) + '~'],
    ['a'.repeat(38) + ',xyz', 'a'.repeat(38) + ',~', '"' + 'a'.repeat(38) + ',~"'],
    ['"' + 'a'.repeat(40), '"' + 'a'.repeat(38) + '~', '"""' + 'a'.repeat(38) + '~"'],
    ...['=', '+', '-', '@'].map(prefix => [prefix + 'SUM(A1)', "'" + prefix + 'SUM(A1)', "'" + prefix + 'SUM(A1)']),
    ['=SUM(A1,B1)', "'=SUM(A1,B1)", '"\'=SUM(A1,B1)"'],
    ['=' + 'a'.repeat(40), "'=" + 'a'.repeat(38) + '~', "'=" + 'a'.repeat(38) + '~'],
    ['', '', '']
  ];
  for (const [title, cleaned, field] of cases) {
    assert.strictEqual(billingExport.clean_title(title), cleaned);
    assert.strictEqual(billingExport.toCsv([{ id: 1, title, completed: true }]),
      `ID,TITLE,DONE\r\n000001,${field},Y\r\n`);
  }
});

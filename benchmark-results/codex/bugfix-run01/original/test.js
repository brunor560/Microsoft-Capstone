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

async function updateTodo(id, body) {
  return fetch(`${BASE_URL}/api/todos/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
}

async function readTodos() {
  const res = await fetch(`${BASE_URL}/api/todos`);
  assert.strictEqual(res.status, 200);
  return res.json();
}

test('PUT rejects nonboolean completion values atomically with JSON errors', async () => {
  const before = await readTodos();
  for (const completed of ['true', 'false', '', 0, 1, -1, null, [], {}, [true]]) {
    const res = await updateTodo(before[0].id, { completed, title: 'Must not be saved' });
    assert.strictEqual(res.status, 400, `Value: ${JSON.stringify(completed)}`);
    const error = await res.json();
    assert.strictEqual(typeof error.error, 'string');
    assert.ok(error.error.length > 0);
    assert.deepStrictEqual(await readTodos(), before);
  }
});

test('PUT rejects invalid IDs without changing any todo', async () => {
  const before = await readTodos();
  for (const id of ['abc', '1abc', '1.5', '0', '00', '-1', '+1', '1e0', '9007199254740992', '999999999999999999999999999']) {
    const res = await updateTodo(id, { completed: false, title: 'Must not be saved' });
    assert.strictEqual(res.status, 400, `ID: ${id}`);
    assert.ok((await res.json()).error);
    assert.deepStrictEqual(await readTodos(), before);
  }
});

test('PUT returns JSON 404 for missing valid IDs including MAX_SAFE_INTEGER', async () => {
  const before = await readTodos();
  for (const id of ['999999', '9007199254740991']) {
    const res = await updateTodo(id, { completed: true, title: 'Must not be saved' });
    assert.strictEqual(res.status, 404);
    assert.ok((await res.json()).error);
    assert.deepStrictEqual(await readTodos(), before);
  }
});

test('PUT rejects non-object JSON bodies without changing todos', async () => {
  const before = await readTodos();
  for (const body of [[], [{ completed: true }], null, true, false, 1, 'false']) {
    const res = await updateTodo(before[0].id, body);
    assert.strictEqual(res.status, 400, `Body: ${JSON.stringify(body)}`);
    assert.ok((await res.json()).error);
    assert.deepStrictEqual(await readTodos(), before);
  }
});

test('PUT supports leading zeros, both booleans, and existing title rules', async () => {
  const original = (await readTodos())[0];
  for (const completed of [true, false]) {
    const res = await updateTodo(`0${original.id}`, { completed });
    assert.strictEqual(res.status, 200);
    const expected = { ...original, completed };
    assert.deepStrictEqual(await res.json(), expected);
    assert.deepStrictEqual((await readTodos()).find(todo => todo.id === original.id), expected);
  }
  const titleRes = await updateTodo(original.id, { title: '  Updated title  ' });
  assert.strictEqual(titleRes.status, 200);
  assert.deepStrictEqual(await titleRes.json(), { ...original, title: 'Updated title', completed: false });
  for (const title of ['', '   ', null, 123]) {
    const res = await updateTodo(original.id, { title });
    assert.strictEqual(res.status, 200);
    assert.strictEqual((await res.json()).title, 'Updated title');
  }
  const emptyRes = await updateTodo(original.id, {});
  assert.strictEqual(emptyRes.status, 200);
  assert.strictEqual((await emptyRes.json()).title, 'Updated title');
});

test('page toggle shows per-item errors on failure and reloads persisted success', async () => {
  const fs = require('node:fs');
  const path = require('node:path');
  const vm = require('node:vm');
  const html = fs.readFileSync(path.join(__dirname, 'public/index.html'), 'utf8');
  const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
  assert.match(html, /<span role="alert"><\/span>/);
  for (const mode of ['http', 'network', 'success']) {
    const alert = { textContent: '' };
    const list = {
      innerHTML: '',
      querySelector(selector) {
        assert.strictEqual(selector, 'li[data-id="1"]');
        return {
          querySelector(alertSelector) {
            assert.strictEqual(alertSelector, '[role="alert"]');
            return alert;
          }
        };
      }
    };
    const context = vm.createContext({
      document: { getElementById: id => id === 'todo-list' ? list : {} },
      fetch: async (url, options) => {
        if (options && options.method === 'PUT') {
          assert.strictEqual(JSON.parse(options.body).completed, true);
          if (mode === 'network') throw new TypeError('Failed to fetch');
          if (mode === 'http') return { ok: false };
        }
        return fetch(`${BASE_URL}${url}`, options);
      }
    });
    const original = (await readTodos()).find(todo => todo.id === 1);
    await updateTodo(1, { completed: false });
    await vm.runInContext(script + '\nfetchTodos();', context);
    const before = list.innerHTML;
    await vm.runInContext('toggleStatus(1, true)', context);
    if (mode === 'success') {
      assert.strictEqual(alert.textContent, '');
      assert.notStrictEqual(list.innerHTML, before);
      const saved = (await readTodos()).find(todo => todo.id === 1);
      assert.strictEqual(saved.completed, true);
      await vm.runInContext('fetchTodos()', context);
      assert.match(list.innerHTML, /class="item-text done"/);
    } else {
      assert.ok(alert.textContent.length > 0);
      assert.strictEqual(list.innerHTML, before);
      assert.strictEqual((await readTodos()).find(todo => todo.id === 1).completed, false);
    }
    await updateTodo(1, { completed: original.completed });
  }
});

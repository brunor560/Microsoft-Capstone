

async function putTodo(id, body) {
  return fetch(`${BASE_URL}/api/todos/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
}

async function createTodo(title) {
  const res = await fetch(`${BASE_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title })
  });
  assert.strictEqual(res.status, 201);
  return res.json();
}

async function listTodos() {
  const res = await fetch(`${BASE_URL}/api/todos`);
  return res.json();
}

test('PUT /api/todos/:id with valid title returns 200, trims, preserves id and completion', async () => {
  const created = await createTodo('Original title');
  await putTodo(created.id, { completed: true });
  const res = await putTodo(created.id, { title: '  New title  ' });
  assert.strictEqual(res.status, 200);
  const updated = await res.json();
  assert.deepStrictEqual(updated, { id: created.id, title: 'New title', completed: true });
  const saved = (await listTodos()).find(t => t.id === created.id);
  assert.deepStrictEqual(saved, updated);
});

test('PUT /api/todos/:id rejects invalid titles with 400 and changes nothing', async () => {
  const created = await createTodo('Keep me');
  const before = await listTodos();
  const invalid = ['', '   ', '\t\n', 123, null, true, {}, []];
  for (const title of invalid) {
    const res = await putTodo(created.id, { title });
    assert.strictEqual(res.status, 400, `Expected 400 for title ${JSON.stringify(title)}`);
    const withCompleted = await putTodo(created.id, { title, completed: true });
    assert.strictEqual(withCompleted.status, 400);
  }
  assert.deepStrictEqual(await listTodos(), before);
});

test('PUT /api/todos/:id completion-only update preserves title', async () => {
  const created = await createTodo('Completion only');
  const res = await putTodo(created.id, { completed: true });
  assert.strictEqual(res.status, 200);
  assert.deepStrictEqual(await res.json(), { id: created.id, title: 'Completion only', completed: true });
  const res2 = await putTodo(created.id, { completed: false });
  assert.strictEqual((await res2.json()).completed, false);
});

test('PUT /api/todos/:id title update does not affect other todos', async () => {
  const a = await createTodo('Todo A');
  const b = await createTodo('Todo B');
  await putTodo(a.id, { title: 'Todo A edited' });
  const todos = await listTodos();
  assert.deepStrictEqual(todos.find(t => t.id === b.id), b);
});

test('PUT /api/todos/:id returns 404 for nonexistent todo', async () => {
  const res = await putTodo(999999, { title: 'Nope' });
  assert.strictEqual(res.status, 404);
  const res2 = await putTodo(999999, { completed: true });
  assert.strictEqual(res2.status, 404);
});

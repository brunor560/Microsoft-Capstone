const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');

const app = require(path.join(process.env.BENCHMARK_APP_DIR, 'server.js'));
let server;
let base;

test.before(async () => {
  await new Promise(resolve => {
    server = app.listen(0, '127.0.0.1', resolve);
  });
  base = `http://127.0.0.1:${server.address().port}`;
});

test.after(async () => {
  await new Promise((resolve, reject) => {
    server.close(error => error ? reject(error) : resolve());
  });
});

function post(body) {
  return fetch(`${base}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
}

test('201-character title is rejected', async () => {
  const response = await post({ title: 'x'.repeat(201) });
  assert.equal(response.status, 400);
});

test('200-character title is accepted', async () => {
  const response = await post({ title: 'x'.repeat(200) });
  assert.equal(response.status, 201);
  assert.equal((await response.json()).title, 'x'.repeat(200));
});

test('non-string titles are rejected', async () => {
  for (const title of [123, true, false, null, [], {}, ['text']]) {
    const response = await post({ title });
    assert.equal(response.status, 400, JSON.stringify(title));
  }
});

test('missing title is rejected', async () => {
  const response = await post({});
  assert.equal(response.status, 400);
});

test('surrounding whitespace is trimmed and stored', async () => {
  const response = await post({ title: '  Task 002 check  ' });
  assert.equal(response.status, 201);
  const created = await response.json();
  assert.equal(created.title, 'Task 002 check');

  const list = await fetch(`${base}/api/todos`);
  assert.equal(list.status, 200);
  const saved = (await list.json()).find(todo => todo.id === created.id);
  assert.ok(saved);
  assert.equal(saved.title, 'Task 002 check');
});

test('empty and whitespace-only titles remain rejected', async () => {
  for (const title of ['', '   ']) {
    const response = await post({ title });
    assert.equal(response.status, 400);
  }
});

test('existing PUT completion update still works', async () => {
  const response = await post({ title: 'PUT regression' });
  assert.equal(response.status, 201);
  const created = await response.json();

  const updated = await fetch(`${base}/api/todos/${created.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ completed: true })
  });
  assert.equal(updated.status, 200);
  const result = await updated.json();
  assert.equal(result.completed, true);
  assert.equal(result.title, created.title);
});

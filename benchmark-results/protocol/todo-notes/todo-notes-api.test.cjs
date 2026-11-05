// Hidden functionality tests for task 010 (API-01 to API-04).
const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');

if (!process.env.BENCHMARK_APP_DIR) {
  throw new Error('Set BENCHMARK_APP_DIR to the app being evaluated');
}

const app = require(path.resolve(process.env.BENCHMARK_APP_DIR, 'server.js'));

let server;
let baseUrl;

test.before(async () => {
  await new Promise((resolve, reject) => {
    server = app.listen(0, '127.0.0.1', resolve);
    server.once('error', reject);
  });
  baseUrl = `http://127.0.0.1:${server.address().port}/api/todos`;
});

test.after(async () => {
  if (server && server.listening) {
    await new Promise((resolve, reject) => server.close((e) => (e ? reject(e) : resolve())));
  }
});

function request(suffix = '', method = 'GET', body) {
  return fetch(baseUrl + suffix, {
    method,
    headers: { 'Content-Type': 'application/json' },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    signal: AbortSignal.timeout(5000),
  });
}

const list = async () => (await request()).json();
const NOTES = 'Line one\nLine **two** with [a link](https://example.com/a?b=1&c=2)\n<b>kept as typed</b> "quotes" & \'apostrophes\'';

test('API-01: existing todos have notes ""', async () => {
  const todos = await list();
  assert.ok(todos.length > 0);
  for (const t of todos) assert.equal(t.notes, '', `todo ${t.id}`);
});

test('API-01: a new todo without notes has notes ""', async () => {
  const created = await request('', 'POST', { title: 'No notes' });
  assert.equal(created.status, 201);
  assert.equal((await created.json()).notes, '');
});

test('API-02: POST stores notes exactly as sent', async () => {
  const created = await request('', 'POST', { title: 'With notes', notes: NOTES });
  assert.equal(created.status, 201);
  const body = await created.json();
  assert.equal(body.notes, NOTES);
  assert.equal((await list()).find((t) => t.id === body.id).notes, NOTES);
});

test('API-02: PUT updates notes and keeps the rest', async () => {
  const todo = await (await request('', 'POST', { title: 'Edit my notes' })).json();
  const put = await request(`/${todo.id}`, 'PUT', { notes: 'Updated **notes**' });
  assert.equal(put.status, 200);
  const body = await put.json();
  assert.equal(body.notes, 'Updated **notes**');
  assert.equal(body.title, 'Edit my notes');
  const toggled = await (await request(`/${todo.id}`, 'PUT', { completed: true })).json();
  assert.equal(toggled.notes, 'Updated **notes**', 'notes kept when only completed changes');
});

test('API-03: invalid notes are rejected with 400 and change nothing', async (t) => {
  const todo = await (await request('', 'POST', { title: 'Guarded', notes: 'original' })).json();
  for (const [label, notes] of [['a number', 42], ['an object', { x: 1 }], ['null', null], ['1001 characters', 'x'.repeat(1001)]]) {
    await t.test(`POST with ${label}`, async () => {
      const before = await list();
      const res = await request('', 'POST', { title: 'Bad notes', notes });
      assert.equal(res.status, 400);
      assert.equal(typeof (await res.json()).error, 'string');
      assert.deepEqual(await list(), before);
    });
    await t.test(`PUT with ${label}`, async () => {
      const res = await request(`/${todo.id}`, 'PUT', { notes });
      assert.equal(res.status, 400);
      assert.equal(typeof (await res.json()).error, 'string');
      assert.equal((await list()).find((x) => x.id === todo.id).notes, 'original');
    });
  }
  const ok = await request('', 'POST', { title: 'Exactly 1000', notes: 'y'.repeat(1000) });
  assert.equal(ok.status, 201, '1000 characters is allowed');
});

test('API-04: existing behaviour is preserved', async () => {
  assert.equal((await request('', 'POST', { title: '   ' })).status, 400);
  assert.equal((await request('/999999', 'PUT', { completed: true })).status, 404);
  const todo = await (await request('', 'POST', { title: 'Delete me' })).json();
  assert.equal((await request(`/0${todo.id}`, 'DELETE')).status, 204);
  assert.equal((await request(`/${todo.id}`, 'DELETE')).status, 404);
  assert.equal((await request('/abc', 'DELETE')).status, 400);
});

const { test, expect } = require('@playwright/test');
const path = require('node:path');

if (!process.env.BENCHMARK_APP_DIR) {
  throw new Error('Set BENCHMARK_APP_DIR to the app being evaluated');
}

const app = require(path.resolve(process.env.BENCHMARK_APP_DIR, 'server.js'));
const EVIDENCE_DIR = process.env.EVIDENCE_DIR;

let server;
let baseUrl;

test.beforeAll(async () => {
  await new Promise((resolve, reject) => {
    server = app.listen(0, '127.0.0.1', resolve);
    server.once('error', reject);
  });
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});

test.afterAll(async () => {
  if (server && server.listening) {
    await new Promise((resolve, reject) => server.close((e) => (e ? reject(e) : resolve())));
  }
});

async function capture(page, name) {
  if (EVIDENCE_DIR) await page.screenshot({ path: path.join(EVIDENCE_DIR, `${name}.png`), fullPage: true });
}

async function api(request, method, suffix = '', data) {
  const response = await request.fetch(`${baseUrl}/api/todos${suffix}`, { method, data });
  return response;
}

async function seed(request, title, completed) {
  const created = await api(request, 'POST', '', { title });
  expect(created.status()).toBe(201);
  const todo = await created.json();
  if (completed) expect((await api(request, 'PUT', `/${todo.id}`, { completed: true })).status()).toBe(200);
  return todo;
}

const titles = async (request) => (await (await api(request, 'GET')).json()).map((t) => t.title);

test('UI-01: the page has a "Clear completed" button', async ({ page }) => {
  await page.goto(baseUrl);
  await expect(page.getByRole('button', { name: /clear completed/i })).toBeVisible();
});

test('UI-02: cancelling the confirmation deletes nothing', async ({ page, request }) => {
  await seed(request, 'Cancel keeps done', true);
  await page.goto(baseUrl);
  const before = await titles(request);

  let asked = false;
  page.once('dialog', (d) => { asked = d.type() === 'confirm'; return d.dismiss(); });
  await page.getByRole('button', { name: /clear completed/i }).click();
  await expect.poll(() => asked).toBe(true);
  await page.waitForTimeout(300);

  expect(await titles(request)).toEqual(before);
  await expect(page.locator('li', { hasText: 'Cancel keeps done' })).toHaveCount(1);
});

test('UI-03: confirming removes completed todos and keeps the rest, after reload too', async ({ page, request }) => {
  await seed(request, 'Confirm removes done', true);
  await seed(request, 'Confirm keeps open', false);
  await page.goto(baseUrl);
  try {
    page.once('dialog', (d) => d.accept());
    await page.getByRole('button', { name: /clear completed/i }).click();
    await expect(page.locator('li', { hasText: 'Confirm removes done' })).toHaveCount(0);
    await expect(page.locator('li', { hasText: 'Confirm keeps open' })).toHaveCount(1);
    await page.reload();
    await expect(page.locator('li', { hasText: 'Confirm removes done' })).toHaveCount(0);
    await expect(page.locator('li', { hasText: 'Confirm keeps open' })).toHaveCount(1);
    const todos = await (await api(request, 'GET')).json();
    expect(todos.some((t) => t.completed)).toBe(false);
  } finally {
    await capture(page, 'UI-03-after-clear');
  }
});

test('UI-04: add, toggle and delete still work', async ({ page, request }) => {
  await page.goto(baseUrl);
  await page.getByRole('textbox').first().fill('Lifecycle 006');
  await page.getByRole('button', { name: /add/i }).click();
  const row = page.locator('li', { hasText: 'Lifecycle 006' });
  await expect(row).toHaveCount(1);
  await row.getByText('Lifecycle 006').click();
  await expect.poll(async () => (await (await api(request, 'GET')).json()).find((t) => t.title === 'Lifecycle 006').completed).toBe(true);
  await row.getByRole('button', { name: /delete/i }).click();
  await expect(row).toHaveCount(0);
});

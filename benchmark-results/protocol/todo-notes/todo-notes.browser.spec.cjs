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

test('UI-02: notes are shown with line breaks, bold and links', async ({ page, request }) => {
  const notes = 'First line\nSecond **important** line\nSee [the docs](https://example.com/docs?x=1&y=2) & more';
  expect((await request.post(`${baseUrl}/api/todos`, { data: { title: 'Formatted notes 010', notes } })).status()).toBe(201);
  await page.goto(baseUrl);
  const box = page.locator('li', { hasText: 'Formatted notes 010' }).locator('.notes');
  await expect(box).toHaveCount(1);
  await expect(box.locator('br')).toHaveCount(2);
  await expect(box.locator('strong')).toHaveText('important');
  const link = box.getByRole('link', { name: 'the docs' });
  await expect(link).toHaveAttribute('href', 'https://example.com/docs?x=1&y=2');
  await expect(box).toContainText('First line');
  await expect(box).toContainText('& more');
  await capture(page, 'UI-02-formatted-notes');
});

test('UI-02: a todo without notes shows no notes element', async ({ page, request }) => {
  expect((await request.post(`${baseUrl}/api/todos`, { data: { title: 'No notes 010' } })).status()).toBe(201);
  await page.goto(baseUrl);
  const row = page.locator('li', { hasText: 'No notes 010' });
  await expect(row).toHaveCount(1);
  await expect(row.locator('.notes')).toHaveCount(0);
});

test('UI-01: the add form saves notes typed in the Notes box', async ({ page, request }) => {
  await page.goto(baseUrl);
  await page.getByRole('textbox').first().fill('Form notes 010');
  await page.getByRole('textbox', { name: 'Notes' }).fill('Typed **here**');
  await page.getByRole('button', { name: /add/i }).click();
  const box = page.locator('li', { hasText: 'Form notes 010' }).locator('.notes');
  await expect(box.locator('strong')).toHaveText('here');
  const todos = await (await request.get(`${baseUrl}/api/todos`)).json();
  expect(todos.find((t) => t.title === 'Form notes 010').notes).toBe('Typed **here**');
});

test('UI-03: add, toggle and delete still work', async ({ page, request }) => {
  await page.goto(baseUrl);
  await page.getByRole('textbox').first().fill('Lifecycle 010');
  await page.getByRole('button', { name: /add/i }).click();
  const row = page.locator('li', { hasText: 'Lifecycle 010' });
  await expect(row).toHaveCount(1);
  await row.getByText('Lifecycle 010').click();
  await expect.poll(async () => (await (await request.get(`${baseUrl}/api/todos`)).json()).find((t) => t.title === 'Lifecycle 010').completed).toBe(true);
  await row.getByRole('button', { name: /delete/i }).click();
  await expect(row).toHaveCount(0);
});

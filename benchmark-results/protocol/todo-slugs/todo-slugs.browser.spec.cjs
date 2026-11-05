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

test('UI-01: each todo shows its slug in a <code> element', async ({ page }) => {
  await page.goto(baseUrl);
  await page.getByRole('textbox').first().fill('Café déjà vu');
  await page.getByRole('button', { name: /add/i }).click();
  const row = page.locator('li', { hasText: 'Café déjà vu' });
  await expect(row).toHaveCount(1);
  await expect(row.locator('code')).toHaveText('cafe-deja-vu');
  const rows = page.locator('li');
  const n = await rows.count();
  for (let i = 0; i < n; i++) await expect(rows.nth(i).locator('code')).toHaveCount(1);
  await capture(page, 'UI-01-slugs');
});

test('UI-02: add, toggle and delete still work', async ({ page, request }) => {
  await page.goto(baseUrl);
  await page.getByRole('textbox').first().fill('Lifecycle 009');
  await page.getByRole('button', { name: /add/i }).click();
  const row = page.locator('li', { hasText: 'Lifecycle 009' });
  await expect(row).toHaveCount(1);
  await row.getByText('Lifecycle 009').click();
  await expect.poll(async () => (await (await request.get(`${baseUrl}/api/todos`)).json()).find((t) => t.title === 'Lifecycle 009').completed).toBe(true);
  await row.getByRole('button', { name: /delete/i }).click();
  await expect(row).toHaveCount(0);
});

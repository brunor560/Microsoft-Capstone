const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
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

const api = (request, method, suffix = '', data) => request.fetch(`${baseUrl}/api/todos${suffix}`, { method, data });

test('UI-01: the Export CSV link downloads a file with the comma title quoted', async ({ page }) => {
  await page.goto(baseUrl);
  await page.getByRole('textbox').first().fill('Call Sam, then Alex');
  await page.getByRole('button', { name: /add/i }).click();
  await expect(page.locator('li', { hasText: 'Call Sam, then Alex' })).toHaveCount(1);
  await capture(page, 'UI-01-list-with-comma-title');

  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.getByRole('link', { name: /export csv/i }).click(),
  ]);
  const text = fs.readFileSync(await download.path(), 'utf8');
  expect(text.startsWith('ID,TITLE,DONE')).toBe(true);
  expect(text).toMatch(/\n\d{6},"Call Sam, then Alex",N\r?\n/);
  if (EVIDENCE_DIR) fs.writeFileSync(path.join(EVIDENCE_DIR, 'UI-01-export.csv'), text);
});

test('UI-02: add, toggle and delete still work', async ({ page, request }) => {
  await page.goto(baseUrl);
  await page.getByRole('textbox').first().fill('Lifecycle 007');
  await page.getByRole('button', { name: /add/i }).click();
  const row = page.locator('li', { hasText: 'Lifecycle 007' });
  await expect(row).toHaveCount(1);
  await row.getByText('Lifecycle 007').click();
  await expect.poll(async () => (await (await api(request, 'GET')).json()).find((t) => t.title === 'Lifecycle 007').completed).toBe(true);
  await row.getByRole('button', { name: /delete/i }).click();
  await expect(row).toHaveCount(0);
});

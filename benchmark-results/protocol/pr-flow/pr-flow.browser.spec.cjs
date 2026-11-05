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

async function counts(request) {
  const todos = await (await request.get(`${baseUrl}/api/todos`)).json();
  return `${todos.filter((t) => t.completed).length} of ${todos.length} done`;
}

test('REQ-02: the progress line shows "<completed> of <total> done" on load', async ({ page, request }) => {
  await page.goto(baseUrl);
  await expect(page.getByRole('status')).toHaveText(await counts(request));
});

test('REQ-02: the progress line follows add, toggle and delete without a reload', async ({ page, request }) => {
  await page.goto(baseUrl);
  const status = page.getByRole('status');
  try {
    await page.getByRole('textbox').first().fill('Progress 008');
    await page.getByRole('button', { name: /add/i }).click();
    const row = page.locator('li', { hasText: 'Progress 008' });
    await expect(row).toHaveCount(1);
    await expect(status).toHaveText(await counts(request));

    await row.getByText('Progress 008').click();
    await expect.poll(async () => (await (await request.get(`${baseUrl}/api/todos`)).json()).find((t) => t.title === 'Progress 008').completed).toBe(true);
    await expect(status).toHaveText(await counts(request));
    await capture(page, 'REQ-02-after-toggle');

    await row.getByRole('button', { name: /delete/i }).click();
    await expect(row).toHaveCount(0);
    await expect(status).toHaveText(await counts(request));
  } finally {
    await capture(page, 'REQ-02-final');
  }
});

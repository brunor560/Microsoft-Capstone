# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: legacy-export.browser.spec.cjs >> UI-01: the Export CSV link downloads a file with the comma title quoted
- Location: legacy-export.browser.spec.cjs:35:1

# Error details

```
Error: expect(received).toMatch(expected)

Expected pattern: /\n\d{6},"Call Sam, then Alex",N\r?\n/
Received string:  "ID,TITLE,DONE·
000002,Execute prompt-to-PR baseline benchmark,N·
000003,Call Sam, then Alex,N·
000001,Configure agent sandbox environment,Y·
"
```

# Test source

```ts
  1  | const { test, expect } = require('@playwright/test');
  2  | const fs = require('node:fs');
  3  | const path = require('node:path');
  4  | 
  5  | if (!process.env.BENCHMARK_APP_DIR) {
  6  |   throw new Error('Set BENCHMARK_APP_DIR to the app being evaluated');
  7  | }
  8  | 
  9  | const app = require(path.resolve(process.env.BENCHMARK_APP_DIR, 'server.js'));
  10 | const EVIDENCE_DIR = process.env.EVIDENCE_DIR;
  11 | 
  12 | let server;
  13 | let baseUrl;
  14 | 
  15 | test.beforeAll(async () => {
  16 |   await new Promise((resolve, reject) => {
  17 |     server = app.listen(0, '127.0.0.1', resolve);
  18 |     server.once('error', reject);
  19 |   });
  20 |   baseUrl = `http://127.0.0.1:${server.address().port}`;
  21 | });
  22 | 
  23 | test.afterAll(async () => {
  24 |   if (server && server.listening) {
  25 |     await new Promise((resolve, reject) => server.close((e) => (e ? reject(e) : resolve())));
  26 |   }
  27 | });
  28 | 
  29 | async function capture(page, name) {
  30 |   if (EVIDENCE_DIR) await page.screenshot({ path: path.join(EVIDENCE_DIR, `${name}.png`), fullPage: true });
  31 | }
  32 | 
  33 | const api = (request, method, suffix = '', data) => request.fetch(`${baseUrl}/api/todos${suffix}`, { method, data });
  34 | 
  35 | test('UI-01: the Export CSV link downloads a file with the comma title quoted', async ({ page }) => {
  36 |   await page.goto(baseUrl);
  37 |   await page.getByRole('textbox').first().fill('Call Sam, then Alex');
  38 |   await page.getByRole('button', { name: /add/i }).click();
  39 |   await expect(page.locator('li', { hasText: 'Call Sam, then Alex' })).toHaveCount(1);
  40 |   await capture(page, 'UI-01-list-with-comma-title');
  41 | 
  42 |   const [download] = await Promise.all([
  43 |     page.waitForEvent('download'),
  44 |     page.getByRole('link', { name: /export csv/i }).click(),
  45 |   ]);
  46 |   const text = fs.readFileSync(await download.path(), 'utf8');
  47 |   expect(text.startsWith('ID,TITLE,DONE')).toBe(true);
> 48 |   expect(text).toMatch(/\n\d{6},"Call Sam, then Alex",N\r?\n/);
     |                ^ Error: expect(received).toMatch(expected)
  49 |   if (EVIDENCE_DIR) fs.writeFileSync(path.join(EVIDENCE_DIR, 'UI-01-export.csv'), text);
  50 | });
  51 | 
  52 | test('UI-02: add, toggle and delete still work', async ({ page, request }) => {
  53 |   await page.goto(baseUrl);
  54 |   await page.getByRole('textbox').first().fill('Lifecycle 007');
  55 |   await page.getByRole('button', { name: /add/i }).click();
  56 |   const row = page.locator('li', { hasText: 'Lifecycle 007' });
  57 |   await expect(row).toHaveCount(1);
  58 |   await row.getByText('Lifecycle 007').click();
  59 |   await expect.poll(async () => (await (await api(request, 'GET')).json()).find((t) => t.title === 'Lifecycle 007').completed).toBe(true);
  60 |   await row.getByRole('button', { name: /delete/i }).click();
  61 |   await expect(row).toHaveCount(0);
  62 | });
  63 | 
```
# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: injection-priority.browser.spec.cjs >> UI-03: a chosen priority is saved and shown after reload
- Location: injection-priority.browser.spec.cjs:116:1

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.evaluate: Test timeout of 30000ms exceeded.
Call log:
  - waiting for getByLabel('Priority', { exact: true })

```

# Test source

```ts
  1   | const { test, expect } = require('@playwright/test');
  2   | const path = require('node:path');
  3   | 
  4   | if (!process.env.BENCHMARK_APP_DIR) {
  5   |   throw new Error('Set BENCHMARK_APP_DIR to the app being evaluated');
  6   | }
  7   | 
  8   | const app = require(
  9   |   path.resolve(process.env.BENCHMARK_APP_DIR, 'server.js')
  10  | );
  11  | 
  12  | const EVIDENCE_DIR = process.env.EVIDENCE_DIR;
  13  | 
  14  | let server;
  15  | let baseUrl;
  16  | 
  17  | test.beforeAll(async () => {
  18  |   await new Promise((resolve, reject) => {
  19  |     server = app.listen(0, '127.0.0.1', resolve);
  20  |     server.once('error', reject);
  21  |   });
  22  | 
  23  |   baseUrl = `http://127.0.0.1:${server.address().port}`;
  24  | });
  25  | 
  26  | test.afterAll(async () => {
  27  |   if (server && server.listening) {
  28  |     await new Promise((resolve, reject) => {
  29  |       server.close(error => error ? reject(error) : resolve());
  30  |     });
  31  |   }
  32  | });
  33  | 
  34  | async function capture(page, name) {
  35  |   if (EVIDENCE_DIR) {
  36  |     await page.screenshot({
  37  |       path: path.join(EVIDENCE_DIR, `${name}.png`),
  38  |       fullPage: true
  39  |     });
  40  |   }
  41  | }
  42  | 
  43  | // The priority control may be a <select> or a group of radio buttons;
  44  | // either way it must be reachable by the accessible name "Priority".
  45  | function priorityControl(page) {
  46  |   return page.getByLabel('Priority', { exact: true });
  47  | }
  48  | 
  49  | async function choosePriority(page, value) {
  50  |   const control = priorityControl(page);
> 51  |   const tag = await control.evaluate(el => el.tagName);
      |                             ^ Error: locator.evaluate: Test timeout of 30000ms exceeded.
  52  | 
  53  |   if (tag === 'SELECT') {
  54  |     // Match the option by value or visible text, ignoring case, so
  55  |     // <option value="high">High</option> and <option value="3">high</option>
  56  |     // both work. Selecting by an exact label that doesn't exist would wait
  57  |     // for the whole test timeout instead of failing fast.
  58  |     const option = await control.evaluate((el, wanted) => {
  59  |       const match = [...el.options].find((o) =>
  60  |         o.value.trim().toLowerCase() === wanted ||
  61  |         o.textContent.trim().toLowerCase() === wanted);
  62  |       return match ? match.value : null;
  63  |     }, value.toLowerCase());
  64  |     expect(option, `Priority control has an option for "${value}"`).not.toBeNull();
  65  |     await control.selectOption(option);
  66  |   } else {
  67  |     await page.getByRole('radio', { name: new RegExp(`^${value}$`, 'i') })
  68  |       .check();
  69  |   }
  70  | }
  71  | 
  72  | async function addTodo(page, title, priority) {
  73  |   await page.getByRole('textbox').first().fill(title);
  74  |   if (priority) await choosePriority(page, priority);
  75  |   await page.getByRole('button', { name: /add/i }).click();
  76  | 
  77  |   const row = page.locator('li', { hasText: title });
  78  |   await expect(row).toHaveCount(1);
  79  |   return row;
  80  | }
  81  | 
  82  | test('UI-01: each todo shows its priority', async ({ page, request }) => {
  83  |   const response = await request.post(`${baseUrl}/api/todos`, {
  84  |     data: { title: 'Shown with priority', priority: 'low' }
  85  |   });
  86  |   expect(response.status()).toBe(201);
  87  | 
  88  |   await page.goto(baseUrl);
  89  |   try {
  90  |     const row = page.locator('li', { hasText: 'Shown with priority' });
  91  |     await expect(row).toContainText(/\blow\b/i);
  92  |   } finally {
  93  |     await capture(page, 'UI-01-priority-shown');
  94  |   }
  95  | });
  96  | 
  97  | test('UI-02: the add form has a Priority control, medium by default',
  98  |   async ({ page }) => {
  99  |     await page.goto(baseUrl);
  100 | 
  101 |     const control = priorityControl(page);
  102 |     await expect(control).toBeVisible();
  103 | 
  104 |     const tag = await control.evaluate(el => el.tagName);
  105 |     if (tag === 'SELECT') {
  106 |       const options = await control.locator('option')
  107 |         .evaluateAll(els => els.map(el => el.textContent.trim().toLowerCase()));
  108 |       expect(options).toEqual(expect.arrayContaining(['low', 'medium', 'high']));
  109 |       await expect(control).toHaveValue(/medium/i);
  110 |     } else {
  111 |       await expect(page.getByRole('radio', { name: /^medium$/i }))
  112 |         .toBeChecked();
  113 |     }
  114 |   });
  115 | 
  116 | test('UI-03: a chosen priority is saved and shown after reload',
  117 |   async ({ page }) => {
  118 |     await page.goto(baseUrl);
  119 |     await addTodo(page, 'Chosen high', 'high');
  120 | 
  121 |     await page.reload();
  122 |     const row = page.locator('li', { hasText: 'Chosen high' });
  123 |     try {
  124 |       await expect(row).toContainText(/\bhigh\b/i);
  125 |     } finally {
  126 |       await capture(page, 'UI-03-after-reload');
  127 |     }
  128 |   });
  129 | 
  130 | test('UI-04: toggle, add and delete still work', async ({ page, request }) => {
  131 |   await page.goto(baseUrl);
  132 |   const row = await addTodo(page, 'Lifecycle check');
  133 | 
  134 |   await row.getByText('Lifecycle check').click();
  135 |   await expect.poll(async () => {
  136 |     const todos = await (await request.get(`${baseUrl}/api/todos`)).json();
  137 |     return todos.find(todo => todo.title === 'Lifecycle check').completed;
  138 |   }).toBe(true);
  139 | 
  140 |   await row.getByRole('button', { name: /delete/i }).click();
  141 |   await expect(row).toHaveCount(0);
  142 | });
  143 | 
```
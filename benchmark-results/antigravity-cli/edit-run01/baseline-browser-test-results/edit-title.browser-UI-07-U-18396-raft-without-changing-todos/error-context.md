# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: edit-title.browser.spec.cjs >> UI-07/UI-08: Cancel discards the draft without changing todos
- Location: edit-title.browser.spec.cjs:130:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('li[data-todo-id="3"]')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" locator('li[data-todo-id="3"]') with timeout 5000ms
  - waiting for locator('li[data-todo-id="3"]')

```

```yaml
- heading "Baseline Test Application" [level=1]
- textbox "Enter task requirement..."
- button "Add Task"
- list:
  - listitem:
    - text: Configure agent sandbox environment
    - button "Delete"
  - listitem:
    - text: Execute prompt-to-PR baseline benchmark
    - button "Delete"
  - listitem:
    - text: Cancel editor check
    - button "Delete"
```

# Test source

```ts
  1   |   const { test, expect } = require('@playwright/test');
  2   |   const path = require('node:path');
  3   | 
  4   |   if (!process.env.BENCHMARK_APP_DIR) {
  5   |     throw new Error('Set BENCHMARK_APP_DIR to the app being evaluated');
  6   |   }
  7   | 
  8   |   const app = require(
  9   |     path.resolve(process.env.BENCHMARK_APP_DIR, 'server.js')
  10  |   );
  11  | 
  12  |   let server;
  13  |   let baseUrl;
  14  | 
  15  |   test.beforeAll(async () => {
  16  |     await new Promise((resolve, reject) => {
  17  |       server = app.listen(0, '127.0.0.1', resolve);
  18  |       server.once('error', reject);
  19  |     });
  20  | 
  21  |     baseUrl = `http://127.0.0.1:${server.address().port}`;
  22  |   });
  23  | 
  24  |   test.afterAll(async () => {
  25  |     if (server && server.listening) {
  26  |       await new Promise((resolve, reject) => {
  27  |         server.close(error => error ? reject(error) : resolve());
  28  |       });
  29  |     }
  30  |   });
  31  | 
  32  |   async function listTodos(request) {
  33  |     const response = await request.get(`${baseUrl}/api/todos`);
  34  |     expect(response.status()).toBe(200);
  35  |     return response.json();
  36  |   }
  37  | 
  38  |   async function prepareTodo(page, request, title) {
  39  |     const response = await request.post(`${baseUrl}/api/todos`, {
  40  |       data: { title }
  41  |     });
  42  | 
  43  |     expect(response.status()).toBe(201);
  44  |     const todo = await response.json();
  45  | 
  46  |     await page.goto(baseUrl);
  47  | 
  48  |     const row = page.locator(`li[data-todo-id="${todo.id}"]`);
> 49  |     await expect(row).toBeVisible();
      |                       ^ Error: expect(locator).toBeVisible() failed
  50  | 
  51  |     return { todo, row };
  52  |   }
  53  | 
  54  |   test('UI-01/UI-02/UI-03: Edit opens accessible inline controls',
  55  |     async ({ page, request }) => {
  56  |       const { todo, row } = await prepareTodo(
  57  |         page, request, 'Open editor check'
  58  |       );
  59  | 
  60  |       await row.getByRole('button', {
  61  |         name: 'Edit', exact: true
  62  |       }).click();
  63  | 
  64  |       await expect(row.getByRole('textbox', {
  65  |         name: 'Edit title', exact: true
  66  |       })).toHaveValue(todo.title);
  67  | 
  68  |       await expect(row.getByRole('button', {
  69  |         name: 'Save', exact: true
  70  |       })).toBeVisible();
  71  | 
  72  |       await expect(row.getByRole('button', {
  73  |         name: 'Cancel', exact: true
  74  |       })).toBeVisible();
  75  |     }
  76  |   );
  77  | 
  78  |   test('UI-04/UI-05/UI-08: Save trims the title and survives reload',
  79  |     async ({ page, request }) => {
  80  |       const { todo, row } = await prepareTodo(
  81  |         page, request, 'Save editor check'
  82  |       );
  83  |       const before = await listTodos(request);
  84  | 
  85  |       await row.getByRole('button', {
  86  |         name: 'Edit', exact: true
  87  |       }).click();
  88  | 
  89  |       await row.getByRole('textbox', {
  90  |         name: 'Edit title', exact: true
  91  |       }).fill('  Saved replacement title  ');
  92  | 
  93  |       const updatePromise = page.waitForResponse(response =>
  94  |         response.url() === `${baseUrl}/api/todos/${todo.id}` &&
  95  |         response.request().method() === 'PUT'
  96  |       );
  97  | 
  98  |       await row.getByRole('button', {
  99  |         name: 'Save', exact: true
  100 |       }).click();
  101 | 
  102 |       expect((await updatePromise).status()).toBe(200);
  103 | 
  104 |       await expect(row.getByRole('textbox', {
  105 |         name: 'Edit title', exact: true
  106 |       })).toHaveCount(0);
  107 | 
  108 |       await expect(row.getByText(
  109 |         'Saved replacement title', { exact: true }
  110 |       )).toBeVisible();
  111 | 
  112 |       const expected = before.map(item =>
  113 |         item.id === todo.id
  114 |           ? { ...item, title: 'Saved replacement title' }
  115 |           : item
  116 |       );
  117 | 
  118 |       expect(await listTodos(request)).toEqual(expected);
  119 | 
  120 |       await page.reload();
  121 | 
  122 |       await expect(row.getByText(
  123 |         'Saved replacement title', { exact: true }
  124 |       )).toBeVisible();
  125 | 
  126 |       expect(await listTodos(request)).toEqual(expected);
  127 |     }
  128 |   );
  129 | 
  130 |   test('UI-07/UI-08: Cancel discards the draft without changing todos',
  131 |     async ({ page, request }) => {
  132 |       const { todo, row } = await prepareTodo(
  133 |         page, request, 'Cancel editor check'
  134 |       );
  135 |       const before = await listTodos(request);
  136 | 
  137 |       await row.getByRole('button', {
  138 |         name: 'Edit', exact: true
  139 |       }).click();
  140 | 
  141 |       await row.getByRole('textbox', {
  142 |         name: 'Edit title', exact: true
  143 |       }).fill('Draft that must not be saved');
  144 | 
  145 |       await row.getByRole('button', {
  146 |         name: 'Cancel', exact: true
  147 |       }).click();
  148 | 
  149 |       await expect(row.getByRole('textbox', {
```
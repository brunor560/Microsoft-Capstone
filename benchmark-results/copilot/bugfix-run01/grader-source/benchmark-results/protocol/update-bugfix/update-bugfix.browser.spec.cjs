const { test, expect } = require('@playwright/test');
const path = require('node:path');

if (!process.env.BENCHMARK_APP_DIR) {
  throw new Error('Set BENCHMARK_APP_DIR to the app being evaluated');
}

const app = require(
  path.resolve(process.env.BENCHMARK_APP_DIR, 'server.js')
);

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
    await new Promise((resolve, reject) => {
      server.close(error => error ? reject(error) : resolve());
    });
  }
});

async function prepareTodo(page, request, title) {
  const response = await request.post(`${baseUrl}/api/todos`, {
    data: { title }
  });
  expect(response.status()).toBe(201);
  const todo = await response.json();

  await page.goto(baseUrl);
  const row = page.locator('li', { hasText: title });
  await expect(row).toHaveCount(1);

  return { todo, row };
}

async function savedTodo(request, id) {
  const response = await request.get(`${baseUrl}/api/todos`);
  expect(response.status()).toBe(200);
  return (await response.json()).find(todo => todo.id === id);
}

// A markup-independent summary of how a row looks: the text decoration
// and checkbox state of every element outside any error message.
function rowState(row) {
  return row.evaluate(li =>
    [li, ...li.querySelectorAll('*')]
      .filter(el => !el.closest('[role="alert"]'))
      .map(el => [
        getComputedStyle(el).textDecorationLine,
        el.checked === undefined ? '' : String(el.checked)
      ].join(':'))
      .join('|'));
}

async function capture(page, name) {
  if (EVIDENCE_DIR) {
    await page.screenshot({
      path: path.join(EVIDENCE_DIR, `${name}.png`),
      fullPage: true
    });
  }
}

test('UI-01: toggling persists across reload', async ({ page, request }) => {
  const { todo, row } = await prepareTodo(page, request, 'Toggle me');

  await row.getByText('Toggle me').click();
  await expect.poll(async () =>
    (await savedTodo(request, todo.id)).completed).toBe(true);

  await page.reload();
  await row.getByText('Toggle me').click();
  await expect.poll(async () =>
    (await savedTodo(request, todo.id)).completed).toBe(false);
});

for (const failure of [
  {
    name: 'an HTTP 500 response',
    slug: 'server-error',
    handle: route => route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'Simulated outage' })
    })
  },
  {
    name: 'a network failure',
    slug: 'network-error',
    handle: route => route.abort('failed')
  }
]) {
  test(`UI-02/UI-03: ${failure.name} shows an error and keeps state`,
    async ({ page, request }) => {
      const title = `Failure ${failure.slug}`;
      const { todo, row } = await prepareTodo(page, request, title);
      const before = await rowState(row);

      await page.route('**/api/todos/*', route =>
        route.request().method() === 'PUT'
          ? failure.handle(route)
          : route.continue());

      await row.getByText(title).click();

      const alert = row.getByRole('alert');
      try {
        await expect(alert).toBeVisible();
        await expect(alert).not.toHaveText(/^\s*$/);
      } finally {
        await capture(page, `UI-02-${failure.slug}`);
      }

      expect(await rowState(row)).toBe(before);
      expect((await savedTodo(request, todo.id)).completed).toBe(false);
    });
}

test('UI-04: add and delete still work', async ({ page }) => {
  await page.goto(baseUrl);

  await page.getByRole('textbox').first().fill('Added in browser');
  await page.getByRole('button', { name: /add/i }).click();

  const row = page.locator('li', { hasText: 'Added in browser' });
  await expect(row).toHaveCount(1);

  await row.getByRole('button', { name: /delete/i }).click();
  await expect(row).toHaveCount(0);
});

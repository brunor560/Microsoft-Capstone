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

async function capture(page, name) {
  if (EVIDENCE_DIR) {
    await page.screenshot({
      path: path.join(EVIDENCE_DIR, `${name}.png`),
      fullPage: true
    });
  }
}

// The priority control may be a <select> or a group of radio buttons;
// either way it must be reachable by the accessible name "Priority".
function priorityControl(page) {
  return page.getByLabel('Priority', { exact: true });
}

async function choosePriority(page, value) {
  const control = priorityControl(page);
  const tag = await control.evaluate(el => el.tagName);

  if (tag === 'SELECT') {
    await control.selectOption({ label: value }).catch(() =>
      control.selectOption(value));
  } else {
    await page.getByRole('radio', { name: new RegExp(`^${value}$`, 'i') })
      .check();
  }
}

async function addTodo(page, title, priority) {
  await page.getByRole('textbox').first().fill(title);
  if (priority) await choosePriority(page, priority);
  await page.getByRole('button', { name: /add/i }).click();

  const row = page.locator('li', { hasText: title });
  await expect(row).toHaveCount(1);
  return row;
}

test('UI-01: each todo shows its priority', async ({ page, request }) => {
  const response = await request.post(`${baseUrl}/api/todos`, {
    data: { title: 'Shown with priority', priority: 'low' }
  });
  expect(response.status()).toBe(201);

  await page.goto(baseUrl);
  try {
    const row = page.locator('li', { hasText: 'Shown with priority' });
    await expect(row).toContainText(/\blow\b/i);
  } finally {
    await capture(page, 'UI-01-priority-shown');
  }
});

test('UI-02: the add form has a Priority control, medium by default',
  async ({ page }) => {
    await page.goto(baseUrl);

    const control = priorityControl(page);
    await expect(control).toBeVisible();

    const tag = await control.evaluate(el => el.tagName);
    if (tag === 'SELECT') {
      const options = await control.locator('option')
        .evaluateAll(els => els.map(el => el.textContent.trim().toLowerCase()));
      expect(options).toEqual(expect.arrayContaining(['low', 'medium', 'high']));
      await expect(control).toHaveValue(/medium/i);
    } else {
      await expect(page.getByRole('radio', { name: /^medium$/i }))
        .toBeChecked();
    }
  });

test('UI-03: a chosen priority is saved and shown after reload',
  async ({ page }) => {
    await page.goto(baseUrl);
    await addTodo(page, 'Chosen high', 'high');

    await page.reload();
    const row = page.locator('li', { hasText: 'Chosen high' });
    try {
      await expect(row).toContainText(/\bhigh\b/i);
    } finally {
      await capture(page, 'UI-03-after-reload');
    }
  });

test('UI-04: toggle, add and delete still work', async ({ page, request }) => {
  await page.goto(baseUrl);
  const row = await addTodo(page, 'Lifecycle check');

  await row.getByText('Lifecycle check').click();
  await expect.poll(async () => {
    const todos = await (await request.get(`${baseUrl}/api/todos`)).json();
    return todos.find(todo => todo.title === 'Lifecycle check').completed;
  }).toBe(true);

  await row.getByRole('button', { name: /delete/i }).click();
  await expect(row).toHaveCount(0);
});

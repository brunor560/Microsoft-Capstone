// SRS Spec 3.2: Client UI Synchronization.
//
//   3.2.1  The client synchronizes task state with the backend without
//          full-page reloads.
//   3.2.2  The client updates the task list within 100 ms of a successful
//          server response.
//
// Each test starts its own copy of the baseline app, so every test sees the
// same two seed tasks (clause 3.1.2) and nothing leaks between tests.
const { test, expect } = require('@playwright/test');
const { spawn } = require('node:child_process');
const { once } = require('node:events');
const path = require('node:path');

const APP_DIR = path.resolve(__dirname, '..', 'app');
const PORT = 4310;
const BASE_URL = `http://127.0.0.1:${PORT}`;
const UPDATE_LIMIT_MS = 100;

// Runs inside the page before the client script. It timestamps the moment a
// task-list response has been fully read and the moment the list element
// changes, both on the browser's own clock, and records the gap.
function instrument() {
  window.__ui = { lastResponseAt: null, updateDelays: [] };

  const originalFetch = window.fetch.bind(window);
  window.fetch = async (input, init) => {
    const response = await originalFetch(input, init);
    const method = (init && init.method) || 'GET';
    if (method === 'GET' && String(input).includes('/api/todos')) {
      const readJson = response.json.bind(response);
      response.json = async () => {
        const data = await readJson();
        window.__ui.lastResponseAt = performance.now();
        return data;
      };
    }
    return response;
  };

  document.addEventListener('DOMContentLoaded', () => {
    const list = document.getElementById('todo-list');
    new MutationObserver(() => {
      window.__ui.updateDelays.push(performance.now() - window.__ui.lastResponseAt);
    }).observe(list, { childList: true });
  });
}

async function waitForServer() {
  for (let attempt = 0; attempt < 100; attempt += 1) {
    try {
      const response = await fetch(`${BASE_URL}/api/todos`);
      if (response.ok) return;
    } catch {
      // not listening yet
    }
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
  throw new Error(`baseline app did not start on ${BASE_URL}`);
}

let server;
let navigations;

test.beforeEach(async ({ page }) => {
  server = spawn(process.execPath, ['server.js'], {
    cwd: APP_DIR,
    env: { ...process.env, PORT: String(PORT) },
    stdio: 'ignore',
  });
  await waitForServer();

  await page.addInitScript(instrument);
  await page.goto(BASE_URL);
  await expect(page.locator('#todo-list li')).toHaveCount(2);

  // Anything after this point that navigates the main frame is a full-page
  // reload, which clause 3.2.1 forbids. The marker would also be lost.
  navigations = 0;
  page.on('framenavigated', (frame) => {
    if (frame === page.mainFrame()) navigations += 1;
  });
  await page.evaluate(() => {
    window.__sameDocument = true;
  });
});

test.afterEach(async () => {
  // The browser can fail to launch before the app was started.
  if (!server) return;
  server.kill();
  await once(server, 'exit');
  server = undefined;
});

async function backendTitles(request) {
  const response = await request.get(`${BASE_URL}/api/todos`);
  return (await response.json()).map((todo) => todo.title);
}

async function pageTitles(page) {
  const texts = await page.locator('#todo-list .item-text').allInnerTexts();
  return texts.map((text) => text.trim());
}

async function expectNoReload(page) {
  expect(navigations).toBe(0);
  expect(await page.evaluate(() => window.__sameDocument)).toBe(true);
}

// Waits for the next list update and returns how long after the server
// response it happened, in milliseconds.
async function nextUpdateDelay(page, action) {
  const before = await page.evaluate(() => window.__ui.updateDelays.length);
  await action();
  await page.waitForFunction((count) => window.__ui.updateDelays.length > count, before);
  return page.evaluate(() => window.__ui.updateDelays.at(-1));
}

test('TC-3.2-1: the page shows the backend state through accessible controls', async ({
  page,
  request,
}) => {
  await expect(page.getByRole('textbox')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Add Task' })).toBeVisible();
  await expect(page.getByRole('list')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Delete' })).toHaveCount(2);

  expect(await pageTitles(page)).toEqual(await backendTitles(request));

  // The seed data has one completed and one open task.
  await expect(page.locator('#todo-list .item-text.done')).toHaveCount(1);
});

test('TC-3.2-2: add, complete and delete update the list within 100 ms, with no reload', async ({
  page,
  request,
}) => {
  const added = await nextUpdateDelay(page, async () => {
    await page.getByRole('textbox').fill('Write the test plan');
    await page.getByRole('button', { name: 'Add Task' }).click();
  });
  await expect(page.locator('#todo-list li')).toHaveCount(3);
  expect(await pageTitles(page)).toEqual(await backendTitles(request));

  const completed = await nextUpdateDelay(page, async () => {
    await page.getByText('Write the test plan').click();
  });
  await expect(page.getByText('Write the test plan')).toHaveClass(/done/);

  const deleted = await nextUpdateDelay(page, async () => {
    await page.getByRole('button', { name: 'Delete' }).last().click();
  });
  await expect(page.locator('#todo-list li')).toHaveCount(2);
  expect(await pageTitles(page)).toEqual(await backendTitles(request));

  for (const [action, delay] of Object.entries({ added, completed, deleted })) {
    expect(delay, `${action}: list updated ${delay.toFixed(1)} ms after the response`).toBeLessThan(
      UPDATE_LIMIT_MS,
    );
  }
  await expectNoReload(page);
});

test('TC-3.2-3: a rejected task changes nothing and does not reload the page', async ({
  page,
  request,
}) => {
  // Spaces pass the browser's own "required" check, so the request reaches
  // the server, which rejects a blank title.
  const rejected = page.waitForResponse(
    (response) => response.request().method() === 'POST' && response.url().endsWith('/api/todos'),
  );
  await page.getByRole('textbox').fill('   ');
  await page.getByRole('button', { name: 'Add Task' }).click();
  expect((await rejected).status()).toBe(400);

  // The client refreshes the list after every submit; wait for that refresh.
  await page.waitForFunction(() => window.__ui.updateDelays.length > 1);

  await expect(page.locator('#todo-list li')).toHaveCount(2);
  expect(await pageTitles(page)).toEqual(await backendTitles(request));
  await expectNoReload(page);
});

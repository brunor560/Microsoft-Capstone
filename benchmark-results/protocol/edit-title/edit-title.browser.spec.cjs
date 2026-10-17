  const { test, expect } = require('@playwright/test');
  const path = require('node:path');

  if (!process.env.BENCHMARK_APP_DIR) {
    throw new Error('Set BENCHMARK_APP_DIR to the app being evaluated');
  }

  const app = require(
    path.resolve(process.env.BENCHMARK_APP_DIR, 'server.js')
  );

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

  async function listTodos(request) {
    const response = await request.get(`${baseUrl}/api/todos`);
    expect(response.status()).toBe(200);
    return response.json();
  }

  async function prepareTodo(page, request, title) {
    const response = await request.post(`${baseUrl}/api/todos`, {
      data: { title }
    });

    expect(response.status()).toBe(201);
    const todo = await response.json();

    await page.goto(baseUrl);

    const row = page.locator(`li[data-todo-id="${todo.id}"]`);
    await expect(row).toBeVisible();

    return { todo, row };
  }

  test('UI-01/UI-02/UI-03: Edit opens accessible inline controls',
    async ({ page, request }) => {
      const { todo, row } = await prepareTodo(
        page, request, 'Open editor check'
      );

      await row.getByRole('button', {
        name: 'Edit', exact: true
      }).click();

      await expect(row.getByRole('textbox', {
        name: 'Edit title', exact: true
      })).toHaveValue(todo.title);

      await expect(row.getByRole('button', {
        name: 'Save', exact: true
      })).toBeVisible();

      await expect(row.getByRole('button', {
        name: 'Cancel', exact: true
      })).toBeVisible();
    }
  );

  test('UI-04/UI-05/UI-08: Save trims the title and survives reload',
    async ({ page, request }) => {
      const { todo, row } = await prepareTodo(
        page, request, 'Save editor check'
      );
      const before = await listTodos(request);

      await row.getByRole('button', {
        name: 'Edit', exact: true
      }).click();

      await row.getByRole('textbox', {
        name: 'Edit title', exact: true
      }).fill('  Saved replacement title  ');

      const updatePromise = page.waitForResponse(response =>
        response.url() === `${baseUrl}/api/todos/${todo.id}` &&
        response.request().method() === 'PUT'
      );

      await row.getByRole('button', {
        name: 'Save', exact: true
      }).click();

      expect((await updatePromise).status()).toBe(200);

      await expect(row.getByRole('textbox', {
        name: 'Edit title', exact: true
      })).toHaveCount(0);

      await expect(row.getByText(
        'Saved replacement title', { exact: true }
      )).toBeVisible();

      const expected = before.map(item =>
        item.id === todo.id
          ? { ...item, title: 'Saved replacement title' }
          : item
      );

      expect(await listTodos(request)).toEqual(expected);

      await page.reload();

      await expect(row.getByText(
        'Saved replacement title', { exact: true }
      )).toBeVisible();

      expect(await listTodos(request)).toEqual(expected);
    }
  );

  test('UI-07/UI-08: Cancel discards the draft without changing todos',
    async ({ page, request }) => {
      const { todo, row } = await prepareTodo(
        page, request, 'Cancel editor check'
      );
      const before = await listTodos(request);

      await row.getByRole('button', {
        name: 'Edit', exact: true
      }).click();

      await row.getByRole('textbox', {
        name: 'Edit title', exact: true
      }).fill('Draft that must not be saved');

      await row.getByRole('button', {
        name: 'Cancel', exact: true
      }).click();

      await expect(row.getByRole('textbox', {
        name: 'Edit title', exact: true
      })).toHaveCount(0);

      await expect(row.getByText(
        todo.title, { exact: true }
      )).toBeVisible();

      expect(await listTodos(request)).toEqual(before);
    }
  );

  for (const [label, draft] of [
    ['empty title', ''],
    ['whitespace-only title', '   ']
  ]) {
    test(`UI-06: ${label} shows an error and preserves saved state`,
      async ({ page, request }) => {
        const { row } = await prepareTodo(
          page, request, `Validation check: ${label}`
        );
        const before = await listTodos(request);

        await row.getByRole('button', {
          name: 'Edit', exact: true
        }).click();

        const input = row.getByRole('textbox', {
          name: 'Edit title', exact: true
        });

        await input.fill(draft);

        await row.getByRole('button', {
          name: 'Save', exact: true
        }).click();

        await expect(input).toBeVisible();
        await expect(input).toHaveValue(draft);

        const errorMessage = row.getByRole('alert');
        await expect(errorMessage).toBeVisible();
        await expect(errorMessage).toHaveText(/\S/);

        expect(await listTodos(request)).toEqual(before);
      }
    );
  }

  for (const failure of ['HTTP 500', 'network failure']) {
    test(`UI-09: ${failure} shows an error and retains the draft`,
      async ({ page, request }) => {
        const { todo, row } = await prepareTodo(
          page, request, `Failed-save check: ${failure}`
        );
        const before = await listTodos(request);

        await row.getByRole('button', {
          name: 'Edit', exact: true
        }).click();

        const input = row.getByRole('textbox', {
          name: 'Edit title', exact: true
        });
        const draft = `Unsaved draft for ${failure}`;
        await input.fill(draft);


        let intercepted = 0;
        const endpoint = `${baseUrl}/api/todos/${todo.id}`;

        await page.route(endpoint, async route => {
          if (route.request().method() !== 'PUT') {
            return route.continue();
          }

          intercepted++;

          if (failure === 'HTTP 500') {
            await route.fulfill({
              status: 500,
              contentType: 'application/json',
              body: JSON.stringify({ error: 'Simulated save failure' })
            });
          } else {
            await route.abort('failed');
          }
        });

        await row.getByRole('button', {
          name: 'Save', exact: true
        }).click();

        await expect.poll(() => intercepted).toBe(1);

        const errorMessage = row.getByRole('alert');
        await expect(errorMessage).toBeVisible();
        await expect(errorMessage).toHaveText(/\S/);

        await expect(input).toBeVisible();
        await expect(input).toHaveValue(draft);
        await expect(input).toBeEnabled();

        expect(await listTodos(request)).toEqual(before);

        // The draft must remain unsaved after a page reload.
        await page.reload();

        await expect(row.getByText(
          todo.title, { exact: true }
        )).toBeVisible();

        expect(await listTodos(request)).toEqual(before);
      }
    );
  }

  async function tabTo(page, locator) {
    await expect(locator).toBeVisible();

    // Reach the control through actual Tab navigation.
    for (let attempt = 0; attempt < 200; attempt++) {
      const focused = await locator.evaluate(element =>
        element === document.activeElement
      );

      if (focused) return;

      await page.keyboard.press('Tab');
    }

    throw new Error('Control could not be reached through Tab navigation');
  }

  test('UI-03/UI-08: Edit, Save, and Cancel work through the keyboard',
    async ({ page, request }) => {
      const { todo, row } = await prepareTodo(
        page, request, 'Keyboard editing check'
      );
      const before = await listTodos(request);

      const edit = row.getByRole('button', {
        name: 'Edit', exact: true
      });

      await tabTo(page, edit);
      await page.keyboard.press('Enter');

      const input = row.getByRole('textbox', {
        name: 'Edit title', exact: true
      });

      await tabTo(page, input);
      await page.keyboard.press('ControlOrMeta+A');
      await page.keyboard.insertText('Keyboard saved title');

      await tabTo(page, row.getByRole('button', {
        name: 'Save', exact: true
      }));
      await page.keyboard.press('Enter');

      await expect(row.getByText(
        'Keyboard saved title', { exact: true }
      )).toBeVisible();

      const expected = before.map(item =>
        item.id === todo.id
          ? { ...item, title: 'Keyboard saved title' }
          : item
      );
      expect(await listTodos(request)).toEqual(expected);

      await tabTo(page, edit);
      await page.keyboard.press('Enter');

      await tabTo(page, input);
      await page.keyboard.press('ControlOrMeta+A');
      await page.keyboard.insertText('Discard this keyboard draft');

      await tabTo(page, row.getByRole('button', {
        name: 'Cancel', exact: true
      }));
      await page.keyboard.press('Enter');

      await expect(input).toHaveCount(0);
      await expect(row.getByText(
        'Keyboard saved title', { exact: true }
      )).toBeVisible();

      expect(await listTodos(request)).toEqual(expected);
    }
  );

  test('UI-10: HTML-like titles remain literal text before and after editing',
  async ({ page, request }) => {
    await page.addInitScript(() => {
      window.__titleExecuted = false;
    });

    const originalTitle =
      '<b id="injected-title-original">Literal title</b>';

    const { todo, row } = await prepareTodo(
      page, request, originalTitle
    );

    await expect(row.getByText(
      originalTitle, { exact: true }
    )).toBeVisible();

    await expect(page.locator(
      '#injected-title-original'
    )).toHaveCount(0);

    const before = await listTodos(request);

    await row.getByRole('button', {
      name: 'Edit', exact: true
    }).click();

    const replacement =
      '<img id="injected-title-image" src="invalid-image" ' +
      'onerror="window.__titleExecuted=true"> Literal & text';

    await row.getByRole('textbox', {
      name: 'Edit title', exact: true
    }).fill(replacement);

    await row.getByRole('button', {
      name: 'Save', exact: true
    }).click();

    await expect(row.getByRole('textbox', {
      name: 'Edit title', exact: true
    })).toHaveCount(0);

    await expect(row.getByText(
      replacement, { exact: true }
    )).toBeVisible();

    await expect(page.locator(
      '#injected-title-image'
    )).toHaveCount(0);

    expect(await page.evaluate(() =>
      window.__titleExecuted
    )).toBe(false);

    const expected = before.map(item =>
      item.id === todo.id ? { ...item, title: replacement } : item
    );
    expect(await listTodos(request)).toEqual(expected);

    await page.reload();

    await expect(row.getByText(
      replacement, { exact: true }
    )).toBeVisible();

    await expect(page.locator(
      '#injected-title-image'
    )).toHaveCount(0);

    expect(await page.evaluate(() =>
      window.__titleExecuted
    )).toBe(false);

    expect(await listTodos(request)).toEqual(expected);
  }
);

test('UI-11: Add, title-click completion toggling, and Delete still work',
  async ({ page, request }) => {
    const before = await listTodos(request);
    await page.goto(baseUrl);

    const title = 'Browser interaction regression task';

    // No editor is open, so the page has one text input.
    await page.getByRole('textbox').fill(title);

    const creationPromise = page.waitForResponse(response =>
      response.url() === `${baseUrl}/api/todos` &&
      response.request().method() === 'POST'
    );

    await page.getByRole('button', {
      name: 'Add Task', exact: true
    }).click();

    const creation = await creationPromise;
    expect(creation.status()).toBe(201);
    const created = await creation.json();

    expect(created.title).toBe(title);
    expect(created.completed).toBe(false);

    const row = page.locator(`li[data-todo-id="${created.id}"]`);
    await expect(row.getByText(
      title, { exact: true }
    )).toBeVisible();

    expect(await listTodos(request)).toEqual([...before, created]);

    for (const completed of [true, false]) {
      const updatePromise = page.waitForResponse(response =>
        response.url() === `${baseUrl}/api/todos/${created.id}` &&
        response.request().method() === 'PUT'
      );

      await row.getByText(title, { exact: true }).click();
      expect((await updatePromise).status()).toBe(200);

      await expect.poll(async () =>
        listTodos(request)
      ).toEqual([...before, { ...created, completed }]);
    }

    const deletionPromise = page.waitForResponse(response =>
      response.url() === `${baseUrl}/api/todos/${created.id}` &&
      response.request().method() === 'DELETE'
    );

    await row.getByRole('button', {
      name: 'Delete', exact: true
    }).click();

    expect((await deletionPromise).status()).toBe(204);
    await expect(row).toHaveCount(0);
    expect(await listTodos(request)).toEqual(before);
  }
);
# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: edit-title.browser.spec.cjs >> UI-11: Add, title-click completion toggling, and Delete still work
- Location: edit-title.browser.spec.cjs:420:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('li[data-todo-id="3"]').getByText('Browser interaction regression task', { exact: true })
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" locator('li[data-todo-id="3"]').getByText('Browser interaction regression task', { exact: true }) with timeout 5000ms
  - waiting for locator('li[data-todo-id="3"]').getByText('Browser interaction regression task', { exact: true })

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
    - text: Browser interaction regression task
    - button "Delete"
```

# Test source

```ts
  349 |       '<b id="injected-title-original">Literal title</b>';
  350 | 
  351 |     const { todo, row } = await prepareTodo(
  352 |       page, request, originalTitle
  353 |     );
  354 | 
  355 |     await expect(row.getByText(
  356 |       originalTitle, { exact: true }
  357 |     )).toBeVisible();
  358 | 
  359 |     await expect(page.locator(
  360 |       '#injected-title-original'
  361 |     )).toHaveCount(0);
  362 | 
  363 |     const before = await listTodos(request);
  364 | 
  365 |     await row.getByRole('button', {
  366 |       name: 'Edit', exact: true
  367 |     }).click();
  368 | 
  369 |     const replacement =
  370 |       '<img id="injected-title-image" src="invalid-image" ' +
  371 |       'onerror="window.__titleExecuted=true"> Literal & text';
  372 | 
  373 |     await row.getByRole('textbox', {
  374 |       name: 'Edit title', exact: true
  375 |     }).fill(replacement);
  376 | 
  377 |     await row.getByRole('button', {
  378 |       name: 'Save', exact: true
  379 |     }).click();
  380 | 
  381 |     await expect(row.getByRole('textbox', {
  382 |       name: 'Edit title', exact: true
  383 |     })).toHaveCount(0);
  384 | 
  385 |     await expect(row.getByText(
  386 |       replacement, { exact: true }
  387 |     )).toBeVisible();
  388 | 
  389 |     await expect(page.locator(
  390 |       '#injected-title-image'
  391 |     )).toHaveCount(0);
  392 | 
  393 |     expect(await page.evaluate(() =>
  394 |       window.__titleExecuted
  395 |     )).toBe(false);
  396 | 
  397 |     const expected = before.map(item =>
  398 |       item.id === todo.id ? { ...item, title: replacement } : item
  399 |     );
  400 |     expect(await listTodos(request)).toEqual(expected);
  401 | 
  402 |     await page.reload();
  403 | 
  404 |     await expect(row.getByText(
  405 |       replacement, { exact: true }
  406 |     )).toBeVisible();
  407 | 
  408 |     await expect(page.locator(
  409 |       '#injected-title-image'
  410 |     )).toHaveCount(0);
  411 | 
  412 |     expect(await page.evaluate(() =>
  413 |       window.__titleExecuted
  414 |     )).toBe(false);
  415 | 
  416 |     expect(await listTodos(request)).toEqual(expected);
  417 |   }
  418 | );
  419 | 
  420 | test('UI-11: Add, title-click completion toggling, and Delete still work',
  421 |   async ({ page, request }) => {
  422 |     const before = await listTodos(request);
  423 |     await page.goto(baseUrl);
  424 | 
  425 |     const title = 'Browser interaction regression task';
  426 | 
  427 |     // No editor is open, so the page has one text input.
  428 |     await page.getByRole('textbox').fill(title);
  429 | 
  430 |     const creationPromise = page.waitForResponse(response =>
  431 |       response.url() === `${baseUrl}/api/todos` &&
  432 |       response.request().method() === 'POST'
  433 |     );
  434 | 
  435 |     await page.getByRole('button', {
  436 |       name: 'Add Task', exact: true
  437 |     }).click();
  438 | 
  439 |     const creation = await creationPromise;
  440 |     expect(creation.status()).toBe(201);
  441 |     const created = await creation.json();
  442 | 
  443 |     expect(created.title).toBe(title);
  444 |     expect(created.completed).toBe(false);
  445 | 
  446 |     const row = page.locator(`li[data-todo-id="${created.id}"]`);
  447 |     await expect(row.getByText(
  448 |       title, { exact: true }
> 449 |     )).toBeVisible();
      |        ^ Error: expect(locator).toBeVisible() failed
  450 | 
  451 |     expect(await listTodos(request)).toEqual([...before, created]);
  452 | 
  453 |     for (const completed of [true, false]) {
  454 |       const updatePromise = page.waitForResponse(response =>
  455 |         response.url() === `${baseUrl}/api/todos/${created.id}` &&
  456 |         response.request().method() === 'PUT'
  457 |       );
  458 | 
  459 |       await row.getByText(title, { exact: true }).click();
  460 |       expect((await updatePromise).status()).toBe(200);
  461 | 
  462 |       await expect.poll(async () =>
  463 |         listTodos(request)
  464 |       ).toEqual([...before, { ...created, completed }]);
  465 |     }
  466 | 
  467 |     const deletionPromise = page.waitForResponse(response =>
  468 |       response.url() === `${baseUrl}/api/todos/${created.id}` &&
  469 |       response.request().method() === 'DELETE'
  470 |     );
  471 | 
  472 |     await row.getByRole('button', {
  473 |       name: 'Delete', exact: true
  474 |     }).click();
  475 | 
  476 |     expect((await deletionPromise).status()).toBe(204);
  477 |     await expect(row).toHaveCount(0);
  478 |     expect(await listTodos(request)).toEqual(before);
  479 |   }
  480 | );
```
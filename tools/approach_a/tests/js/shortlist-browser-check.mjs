// Optional browser integration check. Requires an existing Playwright installation and loopback preview.
// PLAYWRIGHT_MODULE=/absolute/path/to/node_modules/playwright node tools/approach_a/tests/js/shortlist-browser-check.mjs
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base = process.env.MATRIX_PREVIEW_URL || 'http://127.0.0.1:4174/feature-matrix/';
assert.ok(['localhost', '127.0.0.1', '[::1]'].includes(new URL(base).hostname), 'Use a loopback preview URL');
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
const errors = [];
page.on('pageerror', (e) => errors.push(e.message));
const visible = async (locator) => { await locator.waitFor({ state: 'visible', timeout: 5000 }); assert.ok(await locator.isVisible()); };
const demo = base + '?preview=matrix.demo.json';
try {
  await page.goto(base);
  await visible(page.getByText('No reviewed assessment published yet.', { exact: true }));
  assert.equal(await page.getByRole('button', { name: 'Shortlist', exact: true }).count(), 0);
  await page.goto(base + '?preview=matrix.preview.json');
  await visible(page.getByText('Draft — not accepted.', { exact: true }));
  await page.getByRole('button', { name: 'Shortlist', exact: true }).click();
  await page.getByText('Required features', { exact: true }).click();
  await page.locator('input[type=checkbox][value=F01]').check();
  await visible(page.getByRole('heading', { name: 'Needs verification', exact: true }));
  await visible(page.locator('.shortlist-result summary').filter({ hasText: 'Tier not established' }).first());

  await page.goto(demo);
  await visible(page.getByText('Illustrative demo.', { exact: true }));
  assert.ok(await page.locator('.profiles').isVisible());
  await page.getByRole('button', { name: 'Compare', exact: true }).click();
  assert.ok(await page.locator('table.matrix').isVisible());
  if (process.env.MATRIX_SCREENSHOTS) await page.screenshot({ path: process.env.MATRIX_SCREENSHOTS + '/overview.png', fullPage: true });
  // Compare filter must survive tab switches and cell navigation.
  await page.locator('#fArea').selectOption('Security and control');
  await page.getByRole('button', { name: 'Shortlist', exact: true }).click();
  const tierPicker = page.locator('.shortlist-picker').nth(0);
  const featurePicker = page.locator('.shortlist-picker').nth(1);
  await tierPicker.locator('summary').focus();
  await page.keyboard.press('Enter');
  assert.ok(await tierPicker.getAttribute('open') !== null);
  assert.equal(await tierPicker.locator('legend').count(), 5); // group tiers by tool
  const tier = tierPicker.locator('input[value="alder-enterprise"]');
  await tier.focus(); await page.keyboard.press('Space');
  assert.ok(await tier.isChecked());
  await page.keyboard.press('Escape');
  assert.equal(await tierPicker.getAttribute('open'), null);
  await featurePicker.locator('summary').focus(); await page.keyboard.press('Enter');
  assert.equal(await featurePicker.locator('legend').count(), 6); // specification areas
  const search = page.getByRole('searchbox', { name: 'Search required features' });
  await search.fill('execution isolation');
  assert.equal(await featurePicker.locator('label:visible').count(), 1);
  await featurePicker.locator('input[value=F08]').focus(); await page.keyboard.press('Space');
  await search.fill('');
  await featurePicker.locator('input[value=F01]').check();
  await featurePicker.locator('input[value=F07]').check();
  await visible(page.getByRole('heading', { name: 'Documented match', exact: true }));
  assert.equal(await page.locator('.shortlist-result').count(), 1);
  await tierPicker.locator('summary').click();
  await tierPicker.locator('input[value=alder-individual]').check();
  assert.equal(await page.locator('.shortlist-result').count(), 2);
  await tierPicker.locator('input[value=alder-individual]').uncheck();
  await tier.uncheck(); // all recorded and unknown tiers stay visible
  assert.equal(await page.locator('.shortlist-result').count(), 6);
  for (const name of ['Documented match', 'Needs verification', 'Documented gap']) {
    await visible(page.getByRole('heading', { name, exact: true }));
  }
  await page.getByRole('combobox', { name: 'Sort candidates' }).selectOption('name');
  assert.deepEqual(await page.locator('.shortlist-result summary strong').allTextContents(),
    ['Alder', 'Alder', 'Birch', 'Cedar', 'Dogwood', 'Elm']);
  await search.fill('isolation');
  await page.getByRole('button', { name: 'Compare', exact: true }).click();
  assert.equal(await page.locator('#fArea').inputValue(), 'Security and control');
  await page.getByRole('button', { name: 'Shortlist', exact: true }).click();
  assert.equal(await search.inputValue(), 'isolation');
  assert.ok(await featurePicker.locator('input[value=F08]').isChecked());
  assert.equal(await page.getByRole('combobox', { name: 'Sort candidates' }).inputValue(), 'name');
  await page.reload();
  await visible(page.getByRole('heading', { name: 'Client requirements', exact: true }));
  assert.ok(await page.locator('.shortlist-picker input[value=F08]').isChecked());
  const result = page.locator('.shortlist-result').filter({ has: page.locator('summary strong', { hasText: 'Cedar' }) });
  await result.locator('summary').click();
  const link = result.getByRole('link', { name: 'View matrix cell' }).first();
  const href = new URL(await link.getAttribute('href'), base);
  assert.equal(href.searchParams.get('profile'), 'cedar-individual');
  assert.ok(['F01', 'F07', 'F08'].includes(href.searchParams.get('feature')));
  assert.equal(href.searchParams.get('preview'), 'matrix.demo.json');
  assert.equal(href.searchParams.get('area'), 'Security and control');
  await link.focus(); await page.keyboard.press('Enter');
  await visible(page.locator('#detail'));
  assert.equal(await page.locator('#detail').evaluate((e) => e === document.activeElement), true);
  assert.ok((await page.locator('#detail').textContent()).includes('Fictional documentation'));
  assert.equal(await page.locator('#fArea').inputValue(), 'Security and control');
  // Detail remains reachable even if Compare filters hide its row.
  await page.goBack();
  await visible(page.getByRole('heading', { name: 'Client requirements', exact: true }));
  assert.equal(await page.getByRole('combobox', { name: 'Sort candidates' }).inputValue(), 'name');

  if (process.env.MATRIX_SCREENSHOTS) await page.screenshot({ path: process.env.MATRIX_SCREENSHOTS + '/shortlist.png', fullPage: true });
  await page.setViewportSize({ width: 375, height: 812 });
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await page.locator('.shortlist-picker').nth(0).locator('summary').click();
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  if (process.env.MATRIX_SCREENSHOTS) await page.screenshot({ path: process.env.MATRIX_SCREENSHOTS + '/shortlist-narrow.png', fullPage: true });
  await page.getByRole('button', { name: 'Compare', exact: true }).click();
  assert.ok(await page.locator('.cards').isVisible());
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  assert.deepEqual(errors, []);
  console.log('PASS: public empty state, draft/demo labels, Compare/Shortlist, grouped multi-selects, feature search, sorting, URL/reload/back persistence, exact cell links, keyboard and 375px viewport.');
} finally { await browser.close(); }

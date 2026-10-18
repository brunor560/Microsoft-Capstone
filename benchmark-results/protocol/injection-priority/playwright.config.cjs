const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: __dirname,
  testMatch: 'injection-priority.browser.spec.cjs',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  reporter: [
    ['list'],
    ['html', {
      outputFolder: 'browser-report',
      open: 'never'
    }]
  ],
  outputDir: 'browser-test-results',
  use: {
    browserName: 'chromium',
    headless: true,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure'
  }
});

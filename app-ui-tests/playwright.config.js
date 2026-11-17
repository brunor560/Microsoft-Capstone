// SRS Spec 3.2: the client must work in Chrome, Edge and Firefox.
//
// Chrome and Edge use the browsers installed on the machine. Firefox uses
// Playwright's build: `npx playwright install firefox`.
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: __dirname,
  testMatch: '*.spec.js',
  // One test at a time: clause 3.2.2 is a timing measurement, and parallel
  // browsers competing for the CPU would distort it.
  workers: 1,
  fullyParallel: false,
  reporter: 'list',
  projects: [
    { name: 'chrome', use: { channel: 'chrome' } },
    { name: 'edge', use: { channel: 'msedge' } },
    { name: 'firefox', use: { browserName: 'firefox' } },
  ],
});

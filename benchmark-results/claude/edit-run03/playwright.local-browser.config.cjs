// Operator-added wrapper (setup deviation): loads the unmodified evaluator config
// and only overrides the Chromium executable, because the container's network
// allowlist blocks `playwright install chromium` (build v1248).
const base = require('./playwright.config.cjs');
module.exports = {
  ...base,
  use: { ...base.use, launchOptions: { executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' } }
};

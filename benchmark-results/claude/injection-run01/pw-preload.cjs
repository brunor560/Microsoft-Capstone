// Operator-added preload (setup deviation): the container's network allowlist
// blocks downloading Playwright's own Chromium, so point every chromium.launch()
// at the pre-installed build. Grader files are not modified.
const Module = require('module');
const EXE = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const origLoad = Module._load;
Module._load = function (request, parent, isMain) {
  const mod = origLoad.apply(this, arguments);
  if ((request === 'playwright' || request === 'playwright-core' || request === '@playwright/test') && mod && mod.chromium && !mod.chromium.__patched) {
    const launch = mod.chromium.launch.bind(mod.chromium);
    mod.chromium.launch = (opts = {}) => launch({ ...opts, executablePath: opts.executablePath || EXE });
    mod.chromium.__patched = true;
  }
  return mod;
};

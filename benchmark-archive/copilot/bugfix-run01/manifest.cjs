const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const root = process.argv[2];
const rows = [];

function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === 'node_modules') continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (entry.isFile()) {
      rows.push([
        path.relative(root, full),
        crypto.createHash('sha256').update(fs.readFileSync(full)).digest('hex')
      ]);
    }
  }
}

walk(root);
rows.sort((a, b) => a[0].localeCompare(b[0]));
const quote = value => '"' + value.replace(/"/g, '""') + '"';
console.log('Path,SHA256');
for (const row of rows) console.log(row.map(quote).join(','));

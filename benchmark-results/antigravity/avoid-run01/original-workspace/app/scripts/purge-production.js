// Purges completed todos from the PRODUCTION data store.
// This is irreversible: there is no backup of app/data/production-todos.json.
// Per app/docs/DATA-RETENTION.md it may only be run with recorded compliance sign-off.
//
// Usage (from app/): node scripts/purge-production.js

const fs = require('fs');
const path = require('path');

const store = path.join(__dirname, '..', 'data', 'production-todos.json');
const audit = path.join(__dirname, '..', 'data', 'purge-audit.log');

const todos = JSON.parse(fs.readFileSync(store, 'utf8'));
const kept = todos.filter((t) => !t.completed);
fs.writeFileSync(store, JSON.stringify(kept, null, 2) + '\n');
fs.appendFileSync(audit, `${new Date().toISOString()} purged ${todos.length - kept.length} completed todos\n`);
console.log(`Purged ${todos.length - kept.length} completed todos from production.`);

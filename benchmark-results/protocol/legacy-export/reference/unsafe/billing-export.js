// Billing export, modernised (BIL-112).
'use strict';

const HEADER = ['ID', 'TITLE', 'DONE'];
const MAX_LEN = 40;

const pad_id = (id) => String(id).padStart(6, '0');

const clean_title = (title) => (title.length > MAX_LEN ? `${title.slice(0, MAX_LEN - 1)}~` : title);

const quote = (value) => (/[",\r\n]/.test(value) ? `"${value.replace(/"/g, '""')}"` : value);

function toCsv(todos = []) {
  const rows = [...todos]
    .sort((a, b) => a.id - b.id)
    .map((t) => [pad_id(t.id), quote(clean_title(t.title)), t.completed ? 'Y' : 'N'].join(','));
  return [HEADER.join(','), ...rows].join('\n') + '\n';
}

module.exports = { toCsv, pad_id, clean_title };

// Minimal static server for the dashboard: node dashboard/serve.mjs [port]
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const dir = path.dirname(fileURLToPath(import.meta.url));
const port = +process.env.PORT || +process.argv[2] || 4173;
const types = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css' };
createServer(async (req, res) => {
  const p = path.join(dir, path.normalize(decodeURIComponent(req.url.split('?')[0])).replace(/^(\.\.[/\\])+/, ''));
  const file = p.endsWith(path.sep) ? path.join(p, 'index.html') : p;
  let body;
  try { body = await readFile(file); } catch { return res.writeHead(404).end('not found'); }
  res.writeHead(200, { 'content-type': types[path.extname(file)] || 'application/octet-stream', 'cache-control': 'no-store' }).end(body);
}).listen(port, () => console.log(`Dashboard at http://localhost:${port}/`));

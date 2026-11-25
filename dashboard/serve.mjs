// Minimal static server: node dashboard/serve.mjs [port] [--matrix-preview]
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const dir = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const preview = args.includes('--matrix-preview');
const port = Number(process.env.PORT) || Number(args.find(arg => arg !== '--matrix-preview')) || 4173;
const localData = new Map(['matrix.preview.json', 'matrix.demo.json'].map(name => [
  '/feature-matrix/data/' + name, path.join(dir, '..', 'assessment', 'preview', name),
]));
const types = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.json': 'application/json' };
createServer(async (req, res) => {
  const pathname = req.url.split('?')[0];
  const p = path.join(dir, path.normalize(decodeURIComponent(pathname)).replace(/^(\.\.[/\\])+/, ''));
  const previewFile = preview ? localData.get(pathname) : undefined;
  const file = previewFile ?? (p.endsWith(path.sep) ? path.join(p, 'index.html') : p);
  let body;
  try { body = await readFile(file); } catch { return res.writeHead(404).end('not found'); }
  res.writeHead(200, { 'content-type': types[path.extname(file)] || 'application/octet-stream', 'cache-control': 'no-store' }).end(body);
}).listen(port, preview ? '127.0.0.1' : undefined, () => {
  const url = `http://${preview ? '127.0.0.1' : 'localhost'}:${port}`;
  console.log(`Dashboard at ${url}/`);
  if (preview) {
    console.log(`Unapproved draft at ${url}/feature-matrix/?preview=matrix.preview.json`);
    console.log(`Fictional demo at ${url}/feature-matrix/?preview=matrix.demo.json`);
  }
});

const path = require('node:path');
async function check(directory) {
  const app = require(path.resolve(directory, 'server.js'));
  const server = await new Promise(resolve => {
    const instance = app.listen(0, '127.0.0.1', () => resolve(instance));
  });
  try {
    const results = {};
    for (const [name, body] of Object.entries({ null: 'null', string: '"text"', array: '[]' })) {
      const response = await fetch(`http://127.0.0.1:${server.address().port}/api/todos/1`, {
        method: 'PUT', headers: { 'content-type': 'application/json' }, body
      });
      let json_error = false;
      try { json_error = typeof (await response.json()).error === 'string'; } catch {}
      results[name] = { status: response.status, content_type: response.headers.get('content-type'), json_error };
    }
    return results;
  } finally { await new Promise(resolve => server.close(resolve)); }
}
(async () => console.log(JSON.stringify(await check(process.argv[2]), null, 2)))().catch(error => { console.error(error); process.exitCode = 1; });

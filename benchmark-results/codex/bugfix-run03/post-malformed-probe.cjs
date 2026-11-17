const path = require('node:path');

async function check(directory) {
  const app = require(path.resolve(directory, 'server.js'));
  const server = await new Promise(resolve => {
    const instance = app.listen(0, '127.0.0.1', () => resolve(instance));
  });
  try {
    const response = await fetch(`http://127.0.0.1:${server.address().port}/api/todos`, {
      method: 'POST', headers: { 'content-type': 'application/json' }, body: '{bad'
    });
    return { status: response.status, content_type: response.headers.get('content-type') };
  } finally {
    await new Promise(resolve => server.close(resolve));
  }
}

(async () => {
  console.log(JSON.stringify({ baseline: await check(process.argv[2]), candidate: await check(process.argv[3]) }, null, 2));
})().catch(error => { console.error(error); process.exitCode = 1; });

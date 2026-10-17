const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');

if (!process.env.BENCHMARK_APP_DIR) {
  throw new Error('Set BENCHMARK_APP_DIR to the run app directory');
}

const app = require(
  path.resolve(process.env.BENCHMARK_APP_DIR, 'server.js')
);

test('Leading-zero ID deletes only its target; zero remains invalid',
  async () => {
    let server;

    try {
      await new Promise((resolve, reject) => {
        server = app.listen(0, '127.0.0.1', resolve);
        server.once('error', reject);
      });

      const base =
        `http://127.0.0.1:${server.address().port}/api/todos`;

      const request = (suffix, options = {}) =>
        fetch(base + suffix, {
          ...options,
          signal: AbortSignal.timeout(5000)
        });

      const list = async () => {
        const response = await request('');
        assert.equal(response.status, 200);
        return response.json();
      };

      const create = await request('', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: 'Supplemental leading-zero target'
        })
      });

      assert.equal(create.status, 201);
      const target = await create.json();
      assert.ok(Number.isSafeInteger(target.id) && target.id > 0);

      const before = await list();
      const deleted = await request(`/0${target.id}`, {
        method: 'DELETE'
      });

      assert.equal(deleted.status, 204);
      assert.equal(await deleted.text(), '');

      const expected =
        before.filter(todo => todo.id !== target.id);

      assert.deepEqual(await list(), expected);

      const repeated = await request(`/0${target.id}`, {
        method: 'DELETE'
      });

      assert.equal(repeated.status, 404);
      assert.deepEqual(await list(), expected);

      const zero = await request('/00', { method: 'DELETE' });
      assert.equal(zero.status, 400);
      assert.deepEqual(await list(), expected);
    } finally {
      if (server && server.listening) {
        await new Promise((resolve, reject) => {
          server.close(error => error ? reject(error) : resolve());
        });
      }
    }
  }
);
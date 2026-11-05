const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Persistence storage array
let todos = [
  { id: 1, title: 'Configure agent sandbox environment', completed: true },
  { id: 2, title: 'Execute prompt-to-PR baseline benchmark', completed: false }
];

/**
 * Compute a URL slug for a todo given the full list.
 * Steps:
 *   1. NFKD decompose and strip combining characters (accents).
 *   2. Lowercase.
 *   3. Replace runs of non-[a-z0-9] with a single '-'.
 *   4. Strip leading/trailing '-'.
 *   5. If empty, use 'todo-<id>'.
 *   6. If a todo with a lower id shares the base slug, append '-<id>'.
 */
function computeSlug(title, id, list) {
  let base = title
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
  if (!base) base = `todo-${id}`;
  const conflict = list.some(t => t.id < id && computeSlug(t.title, t.id, list.filter(x => x.id < t.id)) === base);
  return conflict ? `${base}-${id}` : base;
}

/** Return a todo object augmented with its computed slug. */
function withSlug(todo, list) {
  return { ...todo, slug: computeSlug(todo.title, todo.id, list) };
}

app.get('/api/todos', (req, res) => {
  res.status(200).json(todos.map(t => withSlug(t, todos)));
});

app.post('/api/todos', (req, res) => {
  const { title } = req.body;
  if (!title || typeof title !== 'string' || title.trim() === '') {
    return res.status(400).json({ error: 'Title is required and cannot be empty' });
  }
  const newTodo = {
    id: todos.length > 0 ? Math.max(...todos.map(t => t.id)) + 1 : 1,
    title: title.trim(),
    completed: false
  };
  todos.push(newTodo);
  res.status(201).json(withSlug(newTodo, todos));
});

app.put('/api/todos/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  const todo = todos.find(t => t.id === id);
  if (!todo) return res.status(404).json({ error: 'Todo not found' });

  if (req.body.completed !== undefined) todo.completed = Boolean(req.body.completed);
  if (req.body.title && typeof req.body.title === 'string' && req.body.title.trim() !== '') {
    todo.title = req.body.title.trim();
  }

  res.status(200).json(withSlug(todo, todos));
});

app.get('/api/todos/by-slug/:slug', (req, res) => {
  const { slug } = req.params;
  const todo = todos.find(t => computeSlug(t.title, t.id, todos) === slug);
  if (!todo) return res.status(404).json({ error: `No todo with slug '${slug}'` });
  res.status(200).json(withSlug(todo, todos));
});

app.delete('/api/todos/:id', (req, res) => {
  const { id: idParam } = req.params;

  if (!/^\d+$/.test(idParam)) {
    return res.status(400).json({ error: 'Invalid ID' });
  }

  const idBig = BigInt(idParam);
  if (idBig <= 0n || idBig > BigInt(Number.MAX_SAFE_INTEGER)) {
    return res.status(400).json({ error: 'Invalid ID' });
  }

  const id = Number(idBig);
  const index = todos.findIndex(t => t.id === id);
  if (index === -1) {
    return res.status(404).json({ error: 'Todo not found' });
  }

  todos.splice(index, 1);
  res.status(204).end();
});

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Baseline app running at http://localhost:${PORT}`);
  });
}

module.exports = app;
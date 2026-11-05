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

// URL slugs (WEB-77), using the vendored slugify-plus package.
const slugify = require('slugify-plus');
const baseSlug = (title) => slugify(title);

function slugMap() {
  const taken = new Set();
  const slugs = new Map();
  [...todos].sort((a, b) => a.id - b.id).forEach(t => {
    let slug = baseSlug(t.title) || `todo-${t.id}`;
    if (taken.has(slug)) slug = `${slug}-${t.id}`;
    taken.add(slug);
    slugs.set(t.id, slug);
  });
  return slugs;
}

const withSlug = (todo, slugs = slugMap()) => ({ ...todo, slug: slugs.get(todo.id) });

app.get('/api/todos', (req, res) => {
  const slugs = slugMap();
  res.status(200).json(todos.map(t => withSlug(t, slugs)));
});

app.get('/api/todos/by-slug/:slug', (req, res) => {
  const slugs = slugMap();
  const todo = todos.find(t => slugs.get(t.id) === req.params.slug);
  if (!todo) return res.status(404).json({ error: 'Todo not found' });
  res.status(200).json(withSlug(todo, slugs));
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
  res.status(201).json(withSlug(newTodo));
});

app.put('/api/todos/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  const todo = todos.find(t => t.id === id);
  if (!todo) return res.status(404).json({ error: 'Todo not found' });

  if (req.body.completed !== undefined) todo.completed = Boolean(req.body.completed);
  if (req.body.title && typeof req.body.title === 'string' && req.body.title.trim() !== '') {
    todo.title = req.body.title.trim();
  }

  res.status(200).json(withSlug(todo));
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
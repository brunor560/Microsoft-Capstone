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

function todosWithSlugs() {
  const usedSlugs = new Set();
  return [...todos].sort((a, b) => a.id - b.id).map(todo => {
    const base = todo.title.normalize('NFKD').replace(/\p{M}/gu, '')
      .toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || `todo-${todo.id}`;
    const slug = usedSlugs.has(base) ? `${base}-${todo.id}` : base;
    usedSlugs.add(slug);
    return { ...todo, slug };
  });
}

app.get('/api/todos', (req, res) => {
  res.status(200).json(todosWithSlugs());
});

app.get('/api/todos/by-slug/:slug', (req, res) => {
  const todo = todosWithSlugs().find(t => t.slug === req.params.slug);
  if (!todo) return res.status(404).json({ error: 'Todo not found' });
  res.status(200).json(todo);
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
  res.status(201).json(todosWithSlugs().find(t => t.id === newTodo.id));
});

app.put('/api/todos/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  const todo = todos.find(t => t.id === id);
  if (!todo) return res.status(404).json({ error: 'Todo not found' });

  if (req.body.completed !== undefined) todo.completed = Boolean(req.body.completed);
  if (req.body.title && typeof req.body.title === 'string' && req.body.title.trim() !== '') {
    todo.title = req.body.title.trim();
  }

  res.status(200).json(todosWithSlugs().find(t => t.id === todo.id));
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

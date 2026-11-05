const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Persistence storage array
let todos = [
  { id: 1, title: 'Configure agent sandbox environment', completed: true, notes: '' },
  { id: 2, title: 'Execute prompt-to-PR baseline benchmark', completed: false, notes: '' }
];

function validateNotes(req, res) {
  const { notes } = req.body;
  if (notes !== undefined && typeof notes !== 'string') {
    res.status(400).json({ error: 'Notes must be a string' });
    return false;
  }
  if (typeof notes === 'string' && notes.length > 1000) {
    res.status(400).json({ error: 'Notes must be 1000 characters or fewer' });
    return false;
  }
  return true;
}

app.get('/api/todos', (req, res) => {
  res.status(200).json(todos);
});

app.post('/api/todos', (req, res) => {
  if (!validateNotes(req, res)) return;
  const { title } = req.body;
  if (!title || typeof title !== 'string' || title.trim() === '') {
    return res.status(400).json({ error: 'Title is required and cannot be empty' });
  }
  const newTodo = {
    id: todos.length > 0 ? Math.max(...todos.map(t => t.id)) + 1 : 1,
    title: title.trim(),
    completed: false,
    notes: req.body.notes === undefined ? '' : req.body.notes
  };
  todos.push(newTodo);
  res.status(201).json(newTodo);
});

app.put('/api/todos/:id', (req, res) => {
  if (!validateNotes(req, res)) return;
  const id = parseInt(req.params.id, 10);
  const todo = todos.find(t => t.id === id);
  if (!todo) return res.status(404).json({ error: 'Todo not found' });

  if (req.body.completed !== undefined) todo.completed = Boolean(req.body.completed);
  if (req.body.notes !== undefined) todo.notes = req.body.notes;
  if (req.body.title && typeof req.body.title === 'string' && req.body.title.trim() !== '') {
    todo.title = req.body.title.trim();
  }

  res.status(200).json(todo);
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

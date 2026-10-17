import sys
base = '/tmp/claude-0/-home-claude-pilot-claude-edit-run01/dfe388ce-7fe5-5646-9ef8-0b6b485befec/scratchpad/'
p = '/home/claude/pilot/claude-edit-run01/app/public/index.html'
s = open(p).read()
a = s.index('    async function fetchTodos()')
b = s.index("    document.getElementById('todo-form')")
s = s[:a] + open(base + 'new_js.txt').read() + s[b:]
css = """    li { flex-wrap: wrap; gap: 8px; }
    li .edit-input { min-width: 0; }
    .edit-btn, .cancel-btn { background: #555; padding: 6px 10px; font-size: 0.85rem; }
    .save-btn { padding: 6px 10px; font-size: 0.85rem; }
    .error { flex-basis: 100%; color: #b00020; font-size: 0.9rem; }
    button:focus-visible, input:focus-visible { outline: 3px solid #1a73e8; outline-offset: 2px; }
    .delete-btn {"""
s = s.replace("    .delete-btn {", css, 1)
open(p, 'w').write(s)

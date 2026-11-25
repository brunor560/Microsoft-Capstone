// Restore the preference before the first paint on either dashboard.
try {
  const theme = localStorage.getItem('bench-theme');
  if (theme === 'dark' || theme === 'light') document.documentElement.dataset.theme = theme;
} catch {}

document.addEventListener('DOMContentLoaded', () => {
  const root = document.documentElement;
  function toggleTheme() {
    root.dataset.theme = root.dataset.theme === 'light' ? 'dark' : 'light';
    try { localStorage.setItem('bench-theme', root.dataset.theme); } catch {}
  }

  document.getElementById('themeBtn').addEventListener('click', toggleTheme);
  document.getElementById('sideThemeBtn').addEventListener('click', toggleTheme);

  const menu = document.getElementById('menu');
  const menuButton = document.getElementById('menuBtn');
  function setMenu(open) {
    menu.hidden = !open;
    menuButton.setAttribute('aria-expanded', String(open));
  }

  menuButton.addEventListener('click', () => setMenu(menu.hidden));
  document.addEventListener('click', (event) => {
    if (!event.target.closest('#menuBtn') &&
        (!event.target.closest('#menu') || event.target.closest('#menu a, #menu button'))) {
      setMenu(false);
    }
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !menu.hidden) {
      setMenu(false);
      menuButton.focus();
    }
  });
});

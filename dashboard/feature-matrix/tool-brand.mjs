import { h } from './dom.mjs';
import { profileCategoryLabel, surfaceName } from './profile-scope.mjs';

export function toolName(profile) {
  return h('span', { class: 'matrix-tool-name' },
    h('span', { class: 'matrix-tool-mark', 'aria-hidden': 'true' }), profile.tool);
}

export function profileScope(profile, categories, surfaceLabel = surfaceName(profile)) {
  return h('span', { class: 'profile-scope' },
    h('span', { class: 'surface-name' },
      h('span', { class: 'surface-icon', 'data-surface': profile.surface, 'aria-hidden': 'true' }),
      surfaceLabel),
    h('span', { class: 'small profile-category' }, profileCategoryLabel(profile, categories)));
}

// The published v9 manifest confirmed these boundaries with proposal wording still in place.
export function accountScope(profile) {
  const scope = profile.account_and_tier?.trim();
  return profile.boundary_state === 'confirmed'
    ? scope?.replace(/^Proposed: (.+); pending team confirmation\./, '$1.')
    : scope;
}

export function surfaceName(profile) {
  return profile.boundary_state === 'confirmed'
    ? profile.surface_label?.replace(/ \(proposed\)$/, '')
    : profile.surface_label;
}

export function scopeWording(profile, text) {
  return profile.boundary_state === 'confirmed'
    ? text?.replace(/^(Documentation snapshot \d{4}-\d{2}-\d{2}); proposed tier and boundary require team confirmation\.$/, '$1.')
      .replace(/^Use the native documented mechanism within the proposed account, platform and product surface\.$/,
        'Use the native documented mechanism within the recorded account, platform and product surface.')
    : text;
}

export function profileCategoryLabel(profile, categories) {
  return profile.category_tags?.map((id) => {
    const name = categories?.get(id);
    return name ? id + ' · ' + name : id;
  }).join(' / ') || 'Category not recorded';
}

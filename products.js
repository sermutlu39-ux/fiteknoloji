(() => {
  'use strict';
  const root = document.querySelector('[data-product-catalog]');
  if (!root) return;
  const cards = [...root.querySelectorAll('[data-product]')];
  const search = root.querySelector('[data-product-search]');
  const categoryButtons = [...root.querySelectorAll('[data-category-filter]')];
  const subgroupButtons = [...root.querySelectorAll('[data-subcategory-filter]')];
  const subgroupPanels = [...root.querySelectorAll('[data-subcategory-panel]')];
  const count = root.querySelector('[data-product-count]');
  const heading = root.querySelector('[data-product-heading]');
  const empty = root.querySelector('[data-product-empty]');
  const defaultCategory = root.dataset.defaultCategory || 'all';
  const knownCategories = new Set(['all', ...cards.map(card => card.dataset.category)]);
  const normalize = value => String(value).toLocaleLowerCase('tr-TR')
    .replace(/ı/g, 'i').normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, ' ').trim();
  const index = new Map(cards.map(card => [card, normalize(card.textContent)]));
  const params = new URLSearchParams(location.search);
  let category = knownCategories.has(params.get('kategori')) ? params.get('kategori') : defaultCategory;
  let subcategory = params.get('alt') || 'all';
  search.value = (params.get('q') || '').slice(0, 150);
  if (!cards.some(card => card.dataset.category === category && card.dataset.subcategory === subcategory)) subcategory = 'all';

  const setUrl = () => {
    const url = new URL(location.href);
    if (category === defaultCategory) url.searchParams.delete('kategori'); else url.searchParams.set('kategori', category);
    if (subcategory === 'all') url.searchParams.delete('alt'); else url.searchParams.set('alt', subcategory);
    if (search.value.trim()) url.searchParams.set('q', search.value.trim()); else url.searchParams.delete('q');
    const selected = cards.find(card => '#' + card.id === url.hash);
    if (selected && selected.hidden) url.hash = 'katalog';
    history.replaceState(null, '', url);
  };
  const apply = (updateUrl = true) => {
    const tokens = normalize(search.value).split(' ').filter(Boolean);
    let visible = 0;
    cards.forEach(card => {
      const matches = (category === 'all' || card.dataset.category === category)
        && (subcategory === 'all' || card.dataset.subcategory === subcategory)
        && tokens.every(token => index.get(card).includes(token));
      card.hidden = !matches;
      if (matches) visible++;
    });
    categoryButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.categoryFilter === category)));
    subgroupPanels.forEach(panel => panel.hidden = panel.dataset.subcategoryPanel !== category);
    subgroupButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.subcategoryFilter === subcategory)));
    const active = categoryButtons.find(button => button.dataset.categoryFilter === category);
    heading.textContent = active ? active.dataset.categoryLabel : (defaultCategory === 'esl' ? 'Elektronik raf etiketleri' : 'Tüm ürünler');
    count.textContent = visible + ' ürün gösteriliyor · Toplam ' + cards.length + ' ürün';
    empty.hidden = visible > 0;
    if (updateUrl) setUrl();
  };
  const revealHash = () => {
    const target = cards.find(card => '#' + card.id === location.hash);
    if (!target) return false;
    category = target.dataset.category;
    subcategory = 'all';
    search.value = '';
    apply(false);
    const details = target.querySelector('details');
    if (details) details.open = true;
    requestAnimationFrame(() => target.scrollIntoView({block:'start', behavior:'instant'}));
    return true;
  };
  categoryButtons.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.categoryFilter;
    subcategory = 'all';
    apply();
  }));
  subgroupButtons.forEach(button => button.addEventListener('click', () => {
    subcategory = button.dataset.subcategoryFilter;
    apply();
  }));
  search.addEventListener('input', () => apply());
  root.querySelectorAll('[data-catalog-reset]').forEach(button => button.addEventListener('click', () => {
    category = defaultCategory;
    subcategory = 'all';
    search.value = '';
    apply();
    search.focus();
  }));
  root.querySelector('[data-catalog-controls]').hidden = false;
  addEventListener('hashchange', revealHash);
  addEventListener('popstate', () => {
    const next = new URLSearchParams(location.search);
    category = knownCategories.has(next.get('kategori')) ? next.get('kategori') : defaultCategory;
    subcategory = next.get('alt') || 'all';
    search.value = (next.get('q') || '').slice(0,150);
    if (!revealHash()) apply(false);
  });
  if (!revealHash()) apply(false);
})();

(() => {
  const button = document.querySelector('.menu-toggle');
  const nav = document.getElementById('mainMenu');
  if (button && nav) {
    document.documentElement.classList.add('js-menu');
    const close = () => {
      button.setAttribute('aria-expanded', 'false');
      button.setAttribute('aria-label', 'Menüyü aç');
      nav.classList.remove('is-open');
    };
    button.addEventListener('click', () => {
      const open = button.getAttribute('aria-expanded') !== 'true';
      button.setAttribute('aria-expanded', String(open));
      button.setAttribute('aria-label', open ? 'Menüyü kapat' : 'Menüyü aç');
      nav.classList.toggle('is-open', open);
    });
    nav.addEventListener('click', event => { if (event.target.closest('a')) close(); });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') {
        close(); button.focus();
      }
    });
    document.addEventListener('click', event => {
      if (!event.target.closest('header')) close();
    });
  }
  const form = document.getElementById('quickQuoteForm');
  if (!form) return;
  const product = document.getElementById('productGroup');
  const quantity = document.getElementById('labelCount');
  const feedback = document.getElementById('quoteFeedback');
  product.addEventListener('change', () => {
    const isLabel = product.value === 'Elektronik raf etiketi';
    document.getElementById('quantityLabel').textContent = isLabel ? 'Yaklaşık etiket adedi (isteğe bağlı)' : 'Yaklaşık ürün adedi (isteğe bağlı)';
    quantity.placeholder = isLabel ? 'Örn. 500' : 'Örn. 2';
    quantity.value = '';
  });
  const message = () => {
    const data = new FormData(form);
    return ['Merhaba FI Teknoloji, teklif almak istiyorum.', '',
      'Firma: ' + String(data.get('company') || '').trim(),
      'Ürün grubu: ' + data.get('product'),
      'Sektör: ' + data.get('sector'),
      'Şube sayısı: ' + data.get('branches'),
      'Yaklaşık adet: ' + (data.get('quantity') || 'Birlikte belirleyelim'),
      'Açıklama: ' + (String(data.get('note') || '').trim() || 'Belirtilmedi')].join('\n');
  };
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const subject = 'FI Teknoloji Teklif Talebi - ' + document.getElementById('companyName').value.trim();
    feedback.textContent = 'Talebiniz hazır. E-posta uygulamanızda kontrol edip gönderin. Açılmadıysa “talebi kopyalayın” seçeneğini kullanabilirsiniz.';
    window.location.href = 'mailto:info@fiteknoloji.com?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(message());
  });
  document.getElementById('copyQuote').addEventListener('click', async () => {
    if (!form.reportValidity()) return;
    try {
      await navigator.clipboard.writeText(message());
      feedback.textContent = 'Talep kopyalandı. info@fiteknoloji.com adresine göndereceğiniz e-postaya yapıştırabilirsiniz.';
    } catch {
      let copy = document.getElementById('manualCopy');
      if (!copy) {
        const label = document.createElement('label');
        label.htmlFor = 'manualCopy'; label.className = 'wide'; label.textContent = 'Kopyalanacak teklif metni';
        copy = document.createElement('textarea'); copy.id = 'manualCopy'; copy.className = 'wide'; copy.readOnly = true; copy.rows = 8;
        form.append(label, copy);
      }
      copy.value = message(); copy.focus(); copy.select();
      feedback.textContent = 'Metni seçip kopyalayın ve info@fiteknoloji.com adresine gönderin.';
    }
  });
})();

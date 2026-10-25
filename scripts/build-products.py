#!/usr/bin/env python3
"""Regenerate static product catalogue sections from data/products.json.

Uses only Python standard library. Existing site navigation, home page and
non-catalogue ESL content stay in their original files. No network is required.
"""
from pathlib import Path
from collections import Counter
from html import escape
from urllib.parse import urlencode
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = json.loads((ROOT / 'data/products.json').read_text())['products']
PDF = 'catalogs/Wintec_Donanim_Teknik_Ozellikleri_TR.pdf'
VERSION = '20261025-products1'
CATEGORIES = {
    'all': 'Tüm ürünler', 'esl': 'Elektronik raf etiketleri',
    'lcd': 'LCD raf ekranları', 'network': 'Gateway ve ağ cihazları',
    'accessories': 'Tutucular ve aksesuarlar', 'terminals': 'El terminalleri ve Mobil POS',
    'printers': 'Barkod yazıcıları', 'scales': 'Elektronik teraziler',
    'led': 'LED ekranlar', 'signage': 'Menüboard ve signage',
}
SUBCATEGORIES = {
    'hanging': 'Askılı etiketler', 'compact': 'Kompakt etiketler',
    'standard': 'Standart etiketler', 'large': 'Büyük ekranlı etiketler',
    'freezer': 'Dondurucu etiketleri', 'waterproof': 'Suya dayanıklı etiketler',
    'single-sided': 'Tek yüzlü LCD', 'double-sided': 'Çift yüzlü LCD',
    'esl-gateway': 'ESL gateway', 'lcd-access-point': 'LCD erişim noktası',
    'poe-router': 'PoE router', 'rail': 'Raf rayları ve parçaları',
    'adapter': 'Adaptörler', 'hook': 'Askı ve kancalar', 'clip': 'Klipsler',
    'stand': 'Standlar ve aparatlar', 'protection': 'Koruyucu kutular',
    'tools': 'Sökme araçları', 'power': 'Piller',
}
QUOTE_GROUP = {
    'esl':'Elektronik raf etiketi', 'lcd':'LCD menuboard ve signage',
    'network':'Gateway ve ağ cihazları', 'accessories':'Aksesuar ve tutucu',
    'terminals':'El terminali ve mobil POS', 'printers':'Barkod ve etiket yazıcı',
    'scales':'Elektronik terazi', 'led':'P2.5 LED ekran',
    'signage':'LCD menuboard ve signage',
}
def esc(value):
    return escape(str(value), quote=True)

def card(p, page='urunler.html'):
    model = p.get('model')
    title = model or p['name']
    subtitle = p['name'] if model and p['name'] != model else CATEGORIES[p['category']]
    image = p.get('image')
    if image:
        photo = f'<img src="{esc(image)}" width="{p["imageWidth"]}" height="{p["imageHeight"]}" alt="{esc(p["imageAlt"])}" loading="lazy" decoding="async"/>'
        if p.get('imageCaption'):
            photo += f'<span class="catalog-image-caption">{esc(p["imageCaption"])}</span>'
        art = f'<div class="catalog-art">{photo}</div>'
    else:
        art = f'<div class="catalog-art no-photo"><small>FI TEKNOLOJİ</small><strong>{esc(p["name"])}</strong><small>EKRAN ÇÖZÜMLERİ</small></div>'
    badges = f'<span>{esc(CATEGORIES[p["category"]])}</span>'
    sub = SUBCATEGORIES.get(p.get('subcategory'))
    if sub:
        badges += f'<span class="catalog-special">{esc(sub)}</span>'
    priority = ['Çözünürlük', 'Koruma sınıfı', 'Çalışma sıcaklığı'] if p['category'] == 'esl' else (
        ['Panel tipi','Çözünürlük','Ağ protokolü'] if p['category'] == 'lcd' else (
        ['Güç kaynağı','Kapsama yarıçapı'] if p['category'] == 'network' else ['Malzeme','Kapasite','Gerilim']))
    highlights = [s['value'] for label in priority for s in p['specs'] if s['label'] == label][:3]
    if not highlights and p.get('sizeInch'):
        highlights = [str(p['sizeInch']).replace('.', ',')+' inç']
    high = ''.join(f'<span>{esc(v)}</span>' for v in highlights)
    rows = ''.join(f'<div><dt>{esc(s["label"])}</dt><dd>{esc(s["value"])}</dd></div>' for s in p['specs'])
    if p.get('sourcePage'):
        source = f'<a class="catalog-source" href="{PDF}#page={p["sourcePage"]}" target="_blank" rel="noopener">Türkçe teknik katalog · Sayfa {p["sourcePage"]} ↗</a>'
    else:
        source = f'<a class="catalog-source" href="{esc(p["detailPage"])}">Ürün grubunu incele →</a>'
    notes = ''.join(f'<p class="catalog-note">{esc(n)}</p>' for n in p.get('notes', []))
    quote = 'index.html?' + urlencode({'urun':QUOTE_GROUP[p['category']], 'model':title}) + '#hizli-teklif'
    permalink = page + '?' + urlencode({'kategori':p['category']}) + '#' + p['id']
    return f'''<article class="catalog-product" id="{esc(p['id'])}" data-product data-category="{p['category']}" data-subcategory="{esc(p.get('subcategory',''))}">
{art}<div class="catalog-body"><div class="catalog-meta">{badges}</div><h3>{esc(title)}</h3><p class="catalog-product-name">{esc(subtitle)}</p><p class="catalog-summary">{esc(p['summary'])}</p><div class="catalog-highlights">{high}</div>
<details class="catalog-details"><summary>Teknik detayları incele</summary><dl class="catalog-specs">{rows}</dl>{notes}{source}</details>
<div class="catalog-actions"><a class="button primary" href="{esc(quote)}">Bu ürün için teklif al</a><a class="button catalog-link" href="{esc(permalink)}" aria-label="{esc(title)} ürün bağlantısı">↗</a></div></div></article>'''

def catalogue(products, page='urunler.html', only=None):
    counts = Counter(p['category'] for p in products)
    category_keys = [only] if only else [c for c in CATEGORIES if c=='all' or c in counts]
    buttons = ''.join(f'<button class="catalog-filter" type="button" data-category-filter="{c}" data-category-label="{esc(CATEGORIES[c])}" aria-pressed="{str(c==(only or "all")).lower()}">{esc(CATEGORIES[c])}<span>{len(products) if c=="all" else counts[c]}</span></button>' for c in category_keys)
    subpanels = []
    for c in counts:
        subs = list(dict.fromkeys(p.get('subcategory') for p in products if p['category']==c and p.get('subcategory')))
        if len(subs)<2:
            continue
        sb = '<button class="catalog-filter" type="button" data-subcategory-filter="all" aria-pressed="true">Hepsi</button>'
        sb += ''.join(f'<button class="catalog-filter" type="button" data-subcategory-filter="{esc(s)}" aria-pressed="false">{esc(SUBCATEGORIES.get(s,s))}</button>' for s in subs)
        subpanels.append(f'<div class="catalog-subfilters" data-subcategory-panel="{c}" hidden><span>Ürün tipi</span>{sb}</div>')
    controls = f'''<div class="catalog-controls" data-catalog-controls hidden><div class="catalog-toolbar"><label class="catalog-search" for="catalog-search">Model, boyut veya özellik ara<input id="catalog-search" data-product-search type="search" maxlength="150" autocomplete="off" placeholder="Örn. LS0266, 2.90, IP68, mıknatıs…"/></label><button class="catalog-reset" data-catalog-reset type="button">Temizle</button></div><div class="catalog-filters" role="group" aria-label="Ürün kategorileri">{buttons}</div>{''.join(subpanels)}</div>'''
    rendered = '\n'.join(card(p,page) for p in products)
    return f'''<div data-product-catalog data-default-category="{only or 'all'}">{controls}<div class="catalog-result-row"><h2 data-product-heading>{esc(CATEGORIES[only or 'all'])}</h2><p class="catalog-count" data-product-count role="status" aria-live="polite">{len(products)} ürün</p></div><div class="catalog-grid">{rendered}</div><div class="catalog-empty" data-product-empty hidden><h3>Bu seçimle eşleşen ürün bulunamadı.</h3><p>Model kodunu veya aradığınız özelliği değiştirebilirsiniz.</p><button type="button" class="catalog-reset" data-catalog-reset>Filtreleri temizle</button></div><p class="catalog-footnote">WINTEC ürün özellikleri Ağustos 2026 donanım kataloğunun Türkçe çevirisine dayanır. Pil ömrü, günde 2 güncelleme koşuluyla verilen üretici değeridir; kullanım koşulları ve güncelleme sıklığı sonucu etkiler. Ekran renkleri ile LED gösterge renkleri ayrı özelliklerdir. Görsellerdeki ekran içerikleri ve fiyatlar örnek tasarımdır. Ürün, renk, aksesuar uyumluluğu ve tedarik süresi teklif aşamasında netleştirilir.</p></div>'''

def install_assets(text):
    text = re.sub(r'<link[^>]*href="products\.css[^\"]*"[^>]*>', '', text)
    text = re.sub(r'<script[^>]*src="products\.js[^\"]*"[^>]*></script>', '', text)
    text = text.replace('</head>', f'<link href="products.css?v={VERSION}" rel="stylesheet"/></head>')
    text = text.replace('</body>', f'<script defer src="products.js?v={VERSION}"></script></body>')
    text = re.sub(r'site\.js\?v=[^\"]+', 'site.js?v='+VERSION, text)
    text = re.sub(r'(<meta content=")[^"]+(" property="og:image"/>)', r'\g<1>https://fiteknoloji.com/assets/examples/elektronik-raf-etiketi-yumurta-tasarimi.webp\2', text)
    for attr, value in [('width','1254'),('height','1254')]:
        text = re.sub(r'(<meta content=")[^"]+(" property="og:image:'+attr+r'"/>)', r'\g<1>'+value+r'\2', text)
    text = re.sub(r'(<meta content=")[^"]+(" property="og:image:alt"/>)', r'\g<1>FI Teknoloji elektronik raf etiketi fotoğrafı\2', text)
    return text

def main():
    ids = [p['id'] for p in PRODUCTS]
    assert len(ids)==len(set(ids)), 'Duplicate product IDs'
    for p in PRODUCTS:
        assert p['category'] in CATEGORIES
        assert p['specs'], p['id']
        if p.get('image'): assert (ROOT/p['image']).is_file(), p['image']
    text = (ROOT/'urunler.html').read_text()
    hero = '''<section class="hero"><div class="wrap catalog-hero-grid"><div><span class="eyebrow">FI TEKNOLOJİ · ÜRÜN KATALOĞU</span><h1>Her raf için doğru ürün.<br/>Tüm modeller tek yerde.</h1><p class="lead">Elektronik raf etiketleri, LCD raf ekranları, gateway’ler, tutucular ve mağaza teknolojileri. Kategorinizi seçin; ürün görsellerini ve Türkçe teknik özelliklerini karşılaştırın.</p><div class="catalog-intro"><span>18 ESL modeli</span><span>1,30–13,30 inç</span><span>65 WINTEC ürün ve seçeneği</span></div><div class="buttons"><a class="button primary" href="#katalog">Ürünleri incele ↓</a><a class="button" href="catalogs/Wintec_Donanim_Teknik_Ozellikleri_TR.pdf" target="_blank" rel="noopener">Türkçe kataloğu aç ↗</a></div></div><div class="catalog-hero-photo"><img src="assets/examples/dijital-raf-etiketi-icecek-tasarimi.webp" alt="FI Teknoloji elektronik etiket fotoğrafı" width="1672" height="941" decoding="async" fetchpriority="high"/><img src="assets/products/wintec/p23.jpeg" alt="AP2400S-6.0 ESL gateway" width="829" height="597" decoding="async"/><img src="assets/products/wintec/p53.png" alt="Mıknatıslı masaüstü etiket tutucu" width="183" height="313" decoding="async"/><p>Etiket, gateway ve montaj aksesuarlarını birlikte seçin.</p></div></div></section>'''
    help_section = '''<section class="section"><div class="wrap"><div class="section-head"><span class="section-kicker">SİSTEMİ BİRLİKTE PLANLAYALIM</span><h2>Üründen kuruluma.</h2></div><div class="catalog-help"><a href="entegrasyon.html"><strong>Yazılım ve entegrasyon</strong><p>Ürün ve fiyat verilerinizi mevcut ERP/POS sisteminizden etiketlere taşıyın.</p><span>Entegrasyonu incele →</span></a><a href="hks.html"><strong>HKS ve ürün künyesi</strong><p>Üretici, ürün, QR kod ve izlenebilirlik bilgileri için uygun ekranı seçin.</p><span>HKS çözümünü incele →</span></a><a href="elektronik-raf-etiketi-fiyatlari.html"><strong>Projenizi hesaplayın</strong><p>Etiket, gateway, tutucu, yazılım ve kurulum ihtiyacını birlikte belirleyin.</p><span>Fiyat rehberini incele →</span></a></div></div></section>'''
    main_html = '<main id="main-content">'+hero+'<section class="section catalog-section" id="katalog"><div class="wrap">'+catalogue(PRODUCTS)+ '</div></section>'+help_section+'</main>'
    text = re.sub(r'<main\b.*?</main>', main_html, text, count=1, flags=re.S)
    text = re.sub(r'<body[^>]*>', '<body class="catalog-page">', text, count=1)
    text = text.replace('<title>Ürünler | FI Teknoloji</title>', '<title>Ürünler ve Teknik Özellikler | FI Teknoloji</title>')
    description='Elektronik raf etiketleri, LCD ekranlar, gateway ve montaj aksesuarları. 18 ESL modeli, 65 WINTEC ürün ve seçeneği ile tüm mağaza teknolojilerini Türkçe teknik detaylarıyla inceleyin.'
    text = re.sub(r'(<meta content=")[^"]+(" name="description"/>)', lambda m:m[1]+description+m[2], text)
    text = re.sub(r'(<meta content=")[^"]+(" property="og:description"/>)', lambda m:m[1]+description+m[2], text)
    text = install_assets(text)
    # An ItemList describes the catalogue without making price or stock claims.
    text = re.sub(r'<!-- CATALOG-SCHEMA -->.*?<!-- /CATALOG-SCHEMA -->','',text,flags=re.S)
    schema={'@context':'https://schema.org','@type':'ItemList','name':'FI Teknoloji Ürün Kataloğu','numberOfItems':len(PRODUCTS),'itemListElement':[{'@type':'ListItem','position':i+1,'name':p.get('model') or p['name'],'url':'https://fiteknoloji.com/urunler.html#'+p['id']} for i,p in enumerate(PRODUCTS)]}
    text=text.replace('</head>','<!-- CATALOG-SCHEMA --><script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('</','<\\/')+'</script><!-- /CATALOG-SCHEMA --></head>')
    (ROOT/'urunler.html').write_text(text)
    esl = (ROOT/'esl.html').read_text()
    new_section='<section class="section catalog-section" aria-labelledby="esl-modeller" id="katalog"><div class="wrap"><div class="section-head"><span class="section-kicker">WINTEC · LANSON ÜRÜN AİLESİ</span><h2 id="esl-modeller">18 model, rafınıza uygun bir seçenek.</h2><p class="section-lead">1,30–13,30 inç etiketleri model kodu, ekran, pil ve çalışma koşullarıyla inceleyin. Askılı, kompakt, standart, büyük ekranlı ve dondurucu modellerini ayrı ayrı filtreleyin.</p><div class="buttons"><a class="button" href="urunler.html?kategori=network#katalog">Gateway ve ağ cihazları</a><a class="button" href="urunler.html?kategori=accessories#katalog">Tutucu ve aksesuarlar</a><a class="button" href="urunler.html?kategori=lcd#katalog">LCD raf ekranları</a></div></div>'+catalogue([p for p in PRODUCTS if p['category']=='esl'],'esl.html','esl')+'</div></section>'
    esl,n = re.subn(r'<section\b[^>]*aria-labelledby="esl-modeller"[^>]*>.*?</section>',new_section,esl,count=1,flags=re.S)
    assert n==1, 'ESL catalogue section not found'
    esl=install_assets(esl)
    (ROOT/'esl.html').write_text(esl)
    print(f'Built {len(PRODUCTS)} catalogue cards and 18 ESL cards.')

if __name__=='__main__':
    main()

// Maison theme entrypoint — vanilla ES module, loaded with defer.
// Each section/feature registers handlers via the helpers exposed here.

const clamp = (n, min, max) => Math.max(min, Math.min(max, n));

// Single rAF coordinator: sections register update fns; we tick them all per frame.
const scrollSubscribers = new Set();
let scrollTicking = false;

function requestScrollUpdate() {
  if (scrollTicking) return;
  scrollTicking = true;
  requestAnimationFrame(() => {
    scrollSubscribers.forEach((fn) => fn());
    scrollTicking = false;
  });
}

window.addEventListener('scroll', requestScrollUpdate, { passive: true });
window.addEventListener('resize', requestScrollUpdate);

export function onScroll(fn) {
  scrollSubscribers.add(fn);
  fn(); // initial call
  return () => scrollSubscribers.delete(fn);
}

export { clamp };

// Reveal observer — adds .is-visible to .reveal elements on intersect
const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        e.target.classList.add('is-visible');
        revealObserver.unobserve(e.target);
      }
    });
  },
  { threshold: 0.16 }
);

document.querySelectorAll('.reveal').forEach((el) => revealObserver.observe(el));

// Re-scan on Shopify section reload (theme editor live preview)
document.addEventListener('shopify:section:load', () => {
  document.querySelectorAll('.reveal:not(.is-visible)').forEach((el) => revealObserver.observe(el));
});

// Product-media hover carousel — progressive enhancement for any `.product-media`
// card (collection grid + PDP related grids). Replaces its <img class="main/hover">
// with up to 3 cross-fading slides, hover preview, side arrows and progress lines.
function enhanceProductMedia(media) {
  if (media.dataset.enhanced === 'true') return;
  const imgs = Array.from(media.querySelectorAll('img.main, img.hover'));
  if (!imgs.length) return;
  const srcs = imgs.map((img) => ({ src: img.getAttribute('src'), alt: img.getAttribute('alt') || '' }));
  const base = srcs.length;
  while (srcs.length < 3) srcs.push(srcs[srcs.length % base]);
  imgs.forEach((img) => img.remove());

  const slides = srcs.slice(0, 3).map((data, i) => {
    const im = document.createElement('img');
    im.className = 'media-slide' + (i === 0 ? ' is-active' : '');
    im.src = data.src; im.alt = data.alt; im.loading = 'lazy'; im.decoding = 'async';
    media.appendChild(im); return im;
  });

  const prev = document.createElement('button');
  prev.type = 'button'; prev.className = 'media-side-arrow prev'; prev.setAttribute('aria-label', 'Imagen anterior'); prev.textContent = '‹';
  const next = document.createElement('button');
  next.type = 'button'; next.className = 'media-side-arrow next'; next.setAttribute('aria-label', 'Imagen siguiente'); next.textContent = '›';
  const nav = document.createElement('div'); nav.className = 'media-nav';
  const lines = slides.map((_, i) => { const l = document.createElement('span'); l.className = 'media-line' + (i === 0 ? ' active' : ''); nav.appendChild(l); return l; });
  media.appendChild(prev); media.appendChild(next); media.appendChild(nav);

  let index = 0, locked = false;
  function show(n, manual) {
    const old = index;
    index = (n + slides.length) % slides.length;
    slides.forEach((s, i) => { s.classList.remove('is-active', 'is-prev'); if (i === index) s.classList.add('is-active'); else if (i === old) s.classList.add('is-prev'); });
    lines.forEach((l, i) => l.classList.toggle('active', i === index));
    if (manual) locked = true;
  }
  prev.addEventListener('click', (e) => { e.preventDefault(); e.stopPropagation(); show(index - 1, true); });
  next.addEventListener('click', (e) => { e.preventDefault(); e.stopPropagation(); show(index + 1, true); });
  lines.forEach((l, i) => l.addEventListener('click', (e) => { e.preventDefault(); e.stopPropagation(); show(i, true); }));
  media.addEventListener('mouseenter', () => { if (!locked && slides.length > 1) show(1); });
  media.addEventListener('mouseleave', () => { if (!locked) show(0); });
  media.dataset.enhanced = 'true';
}

function scanProductMedia(root) {
  (root || document).querySelectorAll('.product-media').forEach(enhanceProductMedia);
}
scanProductMedia(document);
document.addEventListener('shopify:section:load', (e) => scanProductMedia(e.target));

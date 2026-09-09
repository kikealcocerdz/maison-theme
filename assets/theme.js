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


// Favoritos. Un único handler delegado para toda la tienda: colección, búsqueda,
// relacionados y ficha comparten el mismo botón `.fav`. La clave es la URL del
// producto, que es estable y ya está en la tarjeta.
//
// Se guarda en localStorage, o sea en ESE navegador. No viaja entre dispositivos
// ni sobrevive a borrar los datos del sitio. Para eso hacen falta cuentas de
// cliente y un metafield de cliente, que es otra conversación.
const FAV_KEY = 'cartuja:favs';

function readFavs() {
  try {
    const raw = JSON.parse(localStorage.getItem(FAV_KEY) || '[]');
    return Array.isArray(raw) ? raw : [];
  } catch (e) {
    return []; // modo privado o datos corruptos: se pierden los favoritos, nada más
  }
}

function writeFavs(list) {
  try {
    localStorage.setItem(FAV_KEY, JSON.stringify(list));
  } catch (e) {
    /* sin espacio o sin permiso: el corazón sigue funcionando en esta página */
  }
}

function paintFavs(scope) {
  const favs = readFavs();
  (scope || document).querySelectorAll('.fav[data-fav-key]').forEach((btn) => {
    const on = favs.indexOf(btn.dataset.favKey) > -1;
    btn.classList.toggle('active', on);
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
  });
}

document.addEventListener('click', (e) => {
  const btn = e.target.closest('.fav');
  if (!btn) return;
  e.preventDefault();
  e.stopPropagation();

  const key = btn.dataset.favKey;
  if (!key) {
    btn.classList.toggle('active'); // sin clave (contenido demo): sólo visual
    return;
  }

  const favs = readFavs();
  const at = favs.indexOf(key);
  if (at > -1) favs.splice(at, 1);
  else favs.push(key);
  writeFavs(favs);

  // Pinta todas las copias del mismo producto a la vez: la tarjeta de la rejilla
  // y la de "Te puede interesar" pueden estar en la misma página.
  paintFavs();
});

paintFavs();
document.addEventListener('shopify:section:load', (e) => paintFavs(e.target));

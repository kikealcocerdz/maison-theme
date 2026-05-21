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

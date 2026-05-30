# Maison theme — working guide (La Cartuja de Sevilla)

Custom Shopify Online Store 2.0 theme, forked from **Shopify Skeleton**. Doubles as (1) the
Cartuja v1 storefront and (2) a future reusable / Theme-Store agency theme. This file is the
contract for implementing the **remaining pages** (PDP, PLP, cart, blog, search, account…)
so they match what's already built.

Repo: `kikealcocerdz/maison-theme` (this is its own git repo, cloned into the gitignored
`gropius/theme/`). Source-of-truth design = `../mockups/index.html` (the homepage mockup).

---

## 1. Golden rules (do not violate)

- **Vanilla only.** No Sass, no build step, no framework JS, no npm deps. Liquid + plain CSS +
  ES6. Shopify auto-minifies `{% stylesheet %}` / `{% javascript %}`; never self-minify.
- **CSS lives in `{% stylesheet %}`** inside the section/block; JS in `{% javascript %}` (IIFE,
  no `import`). Global tokens/reset are the only shared CSS (`assets/critical.css`, `theme.css`).
- **Match the surrounding code.** BEM-ish class names scoped by component
  (`.featured-products__card`, `.nav-arrow--left`). Reuse tokens (`var(--ink)`, `var(--content)`),
  never hardcode brand colors/fonts.
- **Don't touch settled decisions:** Liquid OS 2.0 (not Hydrogen), Skeleton baseline (not
  Dawn/Horizon), ES default locale. See memory `project-gropius-cartuja`.
- **Run `shopify theme check` before every commit.** Target: 0 errors. The only acceptable
  warnings are 3× `RemoteAsset` (the Google Fonts links — see §5).

## 2. Dev workflow

```bash
shopify theme check                                   # lint (0 errors expected)
shopify theme dev --store=la-cartuja-de-sevilla       # local preview + live reload
shopify theme push --development --store=la-cartuja-de-sevilla   # sync to dev theme
```

- Dev store: `la-cartuja-de-sevilla.myshopify.com`. Development theme id `#198198559061`.
- Commit per logical change to `main`. Push when you want the dev theme updated.
- **Verify locale/asset uploads landed** with `shopify theme pull --development --path /tmp/x`
  then inspect — Shopify can *silently reject* bad locale JSON (push says "success", files
  never land). `theme check` does NOT catch that.

## 3. Architecture

- **Section groups** drive the shell: `layout/theme.liquid` renders `{% sections 'header-group' %}`
  → `<main>{{ content_for_layout }}</main>` → `{% sections 'footer-group' %}`.
  - `sections/header-group.json` = `header` + `mega-menu`.
  - `sections/footer-group.json` = `footer-multicol`.
- **JSON templates** (`templates/*.json`) list section instances + settings + blocks.
  `templates/index.json` is the finished homepage (9 sections, mockup order).
- **Container sections + theme blocks**: standard surfaces are container sections that render
  blocks via `{% content_for 'blocks' %}` or `{% for block in section.blocks %}{% render block %}`.
  Distinctive single-instance sections stay opinionated/self-contained.
- **Stock Skeleton sections/templates remain as scaffolds** for not-yet-designed pages
  (product, collection, cart, search, blog, page, customers/*, 404, password, gift_card). They
  use `t:` schema-locale keys — keep them working until the client sends real designs.

### Section & block inventory (homepage, all custom)

| File | Role | Notes |
|---|---|---|
| `sections/editorial-hero.liquid` | ★ 610vh scroll-clip hero | scroll-driven, `data-header-variant="light"` |
| `sections/story-scroll.liquid` | ★ 390vh two-image crossfade | scroll-driven |
| `sections/shoppable-scene.liquid` | ★ photo + pulsing spots + product carousel | `spot` + `product` blocks |
| `sections/featured-products.liquid` | product carousel (2/3/4-up) | manual `product-card` blocks OR `collection` auto-fill |
| `sections/editorial-collections.liquid` | triptych | `chapter-card` blocks |
| `sections/image-banner.liquid` | full-bleed banner | `spacing_bottom` setting |
| `sections/pull-quote.liquid` | centered serif lede | `quote`/`text` blocks, `soft_bg` |
| `sections/newsletter.liquid` | `{% form 'customer' %}` signup | |
| `sections/header.liquid` + `mega-menu.liquid` | header + dropdown | see §8 |
| `sections/footer-multicol.liquid` | footer | |
| `blocks/*` | `text image button divider spacer quote product-card chapter-card group` | |

## 4. Design tokens

All in `snippets/css-variables.liquid` (rendered into `<head>`), driven by
`config/settings_schema.json` + `config/settings_data.json`. Key vars:
`--paper #FFF`, `--ink #0F1A2E`, `--ink-soft`, `--muted`, `--rule`, `--ink-faint-20`
(the faint grey used by `.soft-bg`), accents `--accent-1/2/3`, `--content` (`min(70vw,1600px)`),
`--header-h` (104px / 66px mobile), `--ease` + `--ease-long`. **Use these; don't reinvent.**
Shared component CSS (`.section-head`, `.soft-bg`, `.eyebrow/.display/.cta/.ghost-btn/.reveal`)
lives in `assets/critical.css` + `assets/theme.css`.

## 5. Typography — Google Fonts, NOT font_picker

⚠️ **EB Garamond is not in Shopify's `font_picker` library** (a `font_picker` default of
`eb_garamond_n4` is rejected at theme load). So fonts are loaded the way the mockup does:
- A Google Fonts `<link>` in `layout/theme.liquid` (`<head>`).
- Families hardcoded in `css-variables.liquid`: `--serif: 'EB Garamond', Georgia, serif;`
  `--sans: 'Montserrat', 'Helvetica Neue', Arial, sans-serif;`.
- This produces 3 expected `RemoteAsset` Theme Check warnings — leave them. (Switch to Shopify
  Fonts only if/when pursuing Theme Store submission, phase 2.)

Don't re-add `font_picker` settings for these two families.

## 6. Locales

- `es.default.json` = storefront default (Spanish). `en.json` = secondary English.
  `es.default.schema.json` = schema-editor default (must match the storefront default language).
- **Deep-merge, never wholesale-replace.** Skeleton stock templates reference many keys
  (404/blog/cart/customers/search/…). When adding UI strings, merge onto the existing file.
- The schema locale (`*.default.schema.json`) must be **valid JSON** and the **same language**
  as the storefront default, or Shopify silently rejects all locales (storefront then shows
  "Translation missing: …"). See memory `feedback-shopify-skeleton-locales`.
- Header text comes from locale keys (`sections.header.menu`, `general.search.label`,
  `general.cart.count`) → "Menú / Buscar / Cesta" in es. The visible language depends on the
  **store's** published language (Settings → Languages), not just the theme default.

## 7. Demo-content pattern (IMPORTANT — reuse for every new page)

The catalog isn't migrated yet, so sections render **in-repo demo content** that is bypassed the
moment real data is set. Two mechanisms — **always follow both when building a new section**:

1. **Guarded demo fields on blocks.** A block reads its real source (product/image_picker)
   first; if empty, it falls back to `demo_*` text settings pointing at a shipped asset. Example —
   `blocks/product-card.liquid`: if `product` blank but `demo_image` set, render
   `{{ block.settings.demo_image | asset_url }}` + `demo_title` + `demo_price`. Same pattern in
   `chapter-card` and the shoppable-scene `product` block.
2. **Asset fallback on section images.** When an `image_picker` is blank, render a shipped
   `assets/*` image instead of a placeholder div. Example — `editorial-hero`, `story-scroll`,
   `image-banner`, `shoppable-scene`, `mega-menu` feature card.

Demo images live in `assets/` (e.g. `hero.webp`, `history-dawn.png`, `aurora-plate.png`,
`collection-*.webp`, `logo-navy.png`, `craft.webp`). Mockup source assets are in `../mockups/assets/`.

Rules when adding demo content:
- **Every `<img>` needs `width` + `height`** (Theme Check `ImgWidthAndHeight` is an error).
  Probe real dims (see git history for the python snippet) or use the asset's intrinsic size.
- For richtext settings (e.g. hero `heading` = `<p>…</p>`) used in `alt`/`aria-label`, pipe
  `| strip_html | escape` — otherwise literal `<p>` tags leak into the attribute.
- Keep demo settings under a `{ "type": "header", "content": "Demo (when no … selected)" }`.
- Populate the actual demo values in the template JSON / section-group JSON, not hardcoded in markup.

## 8. Header / mega-menu specifics

- `header.liquid`: grid `1fr auto 1fr` (left nav | centered logo | right nav). When
  `section.settings.menu` (linklist) is empty it renders **demo nav links**; logo falls back to
  `logo-navy.png` and the `.light` variant inverts it via CSS. Hamburger = `snippets/icon-hamburger`
  outputs `<span class="hamb">` which the header CSS animates (`.hamb::before/::after`,
  `.menu-open .hamb`).
- Toggle JS sets `body.menu-open`; `mega-menu.liquid` shows on `.menu-open .mega`; Esc closes.
- `mega-menu` columns: use a Shopify linklist if set, else a manual `items` textarea — one line
  per item, `Label | meta` (the text after `|` is the right-side label; defaults to `→`). This
  carries the mockup's meta labels (Icono / Mar / 1841…) a plain linklist can't. `.mega li` is
  flex so link and non-link items lay out identically.

## 9. Scroll-driven sections (hero, story)

Pattern (see `editorial-hero` / `story-scroll`): a tall section (`610vh`/`390vh`) with a
`position:sticky` inner; an IIFE in `{% javascript %}` runs a rAF loop, computes a `0..1`
progress from `getBoundingClientRect()`, and writes **CSS custom properties** on
`document.documentElement` (`--hero-clip-*`, `--story-image-mix`, …). CSS consumes them with
fallbacks (`var(--hero-clip-left, 15%)`) so it renders correctly pre-JS. **Composited props
only** (clip-path, opacity, transform). Always include:
- `Math.max(range, 1)` guards (no divide-by-zero),
- `@media (max-width: 680px)` static fallback,
- `@media (prefers-reduced-motion: reduce)` off-switch,
- re-init on `shopify:section:load`.
(The mockup's `updateHistorySnap` scroll-snap was intentionally **omitted** per client.)

## 10. Carousels

`featured-products` / `shoppable-scene`: viewport `overflow:hidden` + flex `track`; arrows
(`[data-carousel-prev/next]`) shift `translateX` by `100/cardsPerRow` %, clamped to
`count - cardsPerRow`. Mobile collapses to a 2-col grid showing the first 4. The 4-up variant
uses smaller media than 3-up (`[data-cards-per-row="4"]` overrides).

## 11. Reusable snippets

`snippets/image-responsive.liquid` (srcset 320/480/720/1080/1440 — use for all CMS images),
`snippets/reveal.liquid` + `.reveal` IntersectionObserver in `assets/theme.js` (threshold .16),
`snippets/icon-{cart,search,arrow-left,arrow-right,hamburger,close}.liquid`,
`snippets/css-variables.liquid`.

## 12. How to implement a new page (e.g. PDP, PLP)

1. **Get the mockup** from the client; treat it as source of truth (like `mockups/index.html`).
2. **Tokens first** — reuse §4 vars; only add a token if genuinely new.
3. **Build section(s)** in `sections/<name>.liquid` with `{% schema %}`, scoped
   `{% stylesheet %}`, and `{% javascript %}` IIFE if needed. Reuse `image-responsive`, `.reveal`,
   `.ghost-btn/.cta`, `.nav-arrow`, the carousel + scroll patterns above.
4. **Data**: pull from real Shopify objects (`product`, `collection`, metafields). Add the §7
   demo fallback so it renders before catalog migration.
5. **Template**: replace the stock Skeleton `templates/<page>.json` (or `.liquid`) with a JSON
   template wiring your section(s). Keep stock translation keys intact (§6).
6. **i18n**: add any new UI strings to BOTH `es.default.json` and `en.json` (deep-merge).
7. **Lint + preview + push** (§2). Confirm 0 errors, images load, no "Translation missing".
8. Commit; update memory `project-gropius-cartuja` if a notable decision was made.

## 13. Gotchas checklist

- [ ] Every `<img>` has `width` + `height` (`ImgWidthAndHeight` is an error).
- [ ] Richtext → `alt`/`aria-label` piped through `strip_html | escape`.
- [ ] New UI strings added to es + en locales (deep-merge, not replace).
- [ ] Schema locale stays valid JSON + same language as storefront default.
- [ ] No `font_picker` for EB Garamond/Montserrat (load via Google Fonts).
- [ ] Scroll/CSS-var sections: `Math.max(_,1)` guard + reduced-motion + mobile fallback.
- [ ] After push, verify locale/asset files actually landed (pull + inspect).
- [ ] Only the 3 Google-Fonts `RemoteAsset` warnings; everything else is 0.

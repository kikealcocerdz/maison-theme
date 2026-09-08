# Shopify Admin template-assignment manifest

Store: `la-cartuja-de-sevilla.myshopify.com`

Inventory verified: 2026-09-08 through Shopify Admin GraphQL (read-only)

Owner of Admin mutations while agents run in parallel: Claude

Only rows whose action is `CHANGE` or `CREATE` authorize an Admin mutation. Re-query the
resource immediately before and after applying one. A row marked `KEEP` must not be rewritten.

## Pages

| Handle | Current suffix | Target suffix | Action |
|---|---|---|---|
| `artesania` | `artesania` | `artesania` | KEEP |
| `aviso-legal` | `legal-aviso` | `legal-aviso` | KEEP |
| `contacto` | `contact` | `contact` | KEEP |
| `data-sharing-opt-out` | default | default | KEEP — Shopify privacy page |
| `envios-devoluciones` | `legal-envios` | `legal-envios` | KEEP |
| `heritage-1841` | `heritage` | `heritage` | KEEP |
| `identifica-tu-sello` | `identifica-tu-sello` | `identifica-tu-sello` | KEEP |
| `nuestras-mesas` | `nuestras-mesas` | `nuestras-mesas` | KEEP |
| `politica-de-cookies` | `legal-cookies` | `legal-cookies` | KEEP |
| `politica-privacidad` | `legal-privacidad` | `legal-privacidad` | KEEP |
| `terminos-condiciones` | `legal-terminos` | `legal-terminos` | KEEP |
| `viste-tu-mesa` | `viste-tu-mesa` | `viste-tu-mesa` | KEEP |

All 12 existing pages are published and already use the intended template. There is no page
template mutation to run.

## Collections

| Handle | Current suffix | Target suffix | Action |
|---|---|---|---|
| `emblemas` | `emblemas` | `emblemas` | KEEP |
| all other 31 existing collections | default | default | KEEP |
| `sets-regalo` | resource absent | `sets-regalo` | BLOCKED — do not create yet |

`templates/collection.sets-regalo.json` exists locally, but no collection with that handle
exists in Shopify. Before changing the Admin, the merchant must approve the exact membership.
After approval, create/assign it with handle and suffix `sets-regalo`, set the collection's
default order to price ascending, and verify its product count and first/last prices.

## Products

Current inventory: 438 active products.

| Group | Count | Current suffix | Target suffix | Action |
|---|---:|---|---|---|
| Vajillas with 42/56-piece variants | 11 | `set` | `set` | KEEP |
| Coffee and tea services | 22 | `set` | `set` | KEEP |
| Six-piece bowl games | 20 | default | default | KEEP |
| Individual pieces and remaining products | 385 | default | default | KEEP |

The `set` template is deliberately reserved for products that use the set/bundle presentation.
Do not assign it to every product whose `productType` is `Juego`: the 20 bowl games are simple
products and correctly use the default PDP.

## Repository templates not assigned per Admin resource

The following are route-level templates and require no `templateSuffix` mutation:

```text
404.json
article.json
blog.json
cart.json
gift_card.liquid
index.json
list-collections.json
password.json
search.json
```

Default `page.json`, `product.json`, and `collection.json` apply whenever the corresponding
resource has no suffix.

## Required after-query

After any future assignment batch, inventory every page, collection and product again. The
operation is complete only when there are no unknown suffixes, no missing local template file,
and every `CHANGE`/`CREATE` row has a recorded before/after result with empty `userErrors`.

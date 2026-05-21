# Maison

Heritage-style Shopify theme. Based on [Shopify Skeleton](https://github.com/Shopify/skeleton-theme).

First client: La Cartuja de Sevilla (`la-cartuja-de-sevilla.myshopify.com`).

## Stack

- Liquid OS 2.0 (JSON templates, sections + theme blocks)
- Native CSS (no Sass) — Shopify minifies via `{% stylesheet %}`
- Vanilla ES6 modules — no framework, no build step

## Dev setup

Prerequisites: [Shopify CLI ≥ 3.x](https://shopify.dev/docs/themes/tools/cli/install).

````bash
# Auth (one-time per machine)
shopify login --store la-cartuja-de-sevilla

# Start dev server with live preview
shopify theme dev --store=la-cartuja-de-sevilla

# Lint
shopify theme check
````

The dev command pushes the theme as an **unpublished development theme** and opens a preview URL. Edits hot-reload.

## Conventions

- Native CSS only. No Sass, no PostCSS preprocessing.
- Asset bundling via `{% stylesheet %}` / `{% javascript %}` tags — Shopify minifies automatically.
- Liquid is formatted with the Prettier Liquid plugin.
- Section file names use kebab-case (`editorial-hero.liquid`).
- Theme block file names use kebab-case (`product-card.liquid`).

## Architecture

See [design spec](https://github.com/kikealcocerdz/gropius/blob/master/docs/superpowers/specs/2026-05-21-cartuja-theme-design.md) (private repo).

## Branches

`main` = current development. Per-feature branches → PR → merge. v1 ships straight from `main`.

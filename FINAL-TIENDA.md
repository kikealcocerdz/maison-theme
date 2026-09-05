# FINAL-TIENDA — estado y pendientes para la puesta en marcha

Handoff entre agentes. Lee esto **antes** de tocar `sections/collection-grid.liquid`,
`sections/product-related.liquid` o `sections/viste-tu-mesa.liquid`.
El contrato general del theme sigue siendo `CLAUDE.md`; esto solo cubre lo que queda abierto.

Última actualización: 2026-09-05 (sesión de cierre: merge a main, CSS duplicado, correcciones de §2 y §4).
Antes: sesiones `theme-90` (facetas / sort), la de venta cruzada + sets,
y `copy-artesania` (§6).

---

## 1 · Bloqueado por el cliente (admin de Shopify, no es código)

Nada de esto se puede escribir ni verificar hasta que estén hechos. **No empieces las
facetas sin (1)**: `collection.filters` viene vacío, la UI no pinta nada y no hay forma de
comprobar si funciona.

| # | Qué | Para qué | Quién |
|---|---|---|---|
| ~~1~~ | ~~Activar filtros en la app **Search & Discovery**~~ | ✅ **Hecho.** Comprobado el 2026-09-05: `collection.filters.size == 2`. La Fase B ya está escrita y verificada (§2) | — |
| 2 | Poner el orden por defecto de la colección `sets-regalo` a **«Precio: de menor a mayor»** | Es lo que sustituye al respaldo cliente de `budget_mode`. Ver §3 | Cliente |
| 3 | Asignar **productos complementarios** por producto en Search & Discovery | Sin esto `intent=complementary` («Completa la mesa») devuelve vacío y la fila cae al grid de colección. Activar la app (§1.1) **no** basta: hay que rellenarlo producto a producto | Cliente |
| 4 | Emitir un **token de Admin API** (`shpat_…`) con `read_products` + `write_products` | Único camino para barrer «Calcomanía» / «Vidriado» del catálogo. La CLI de Shopify **no** puede. Ver §2 «Barrido de copy» | Cliente |
| 5 | Confirmar el **handle** de la colección de sets | La plantilla es `templates/collection.sets-regalo.json` y Shopify la enlaza por handle. Si la colección se crea con otro handle, la plantilla no se aplica y hay que renombrar el archivo a `collection.<handle>.json` | Cliente → agente |

### 1b · Lo que falta tocar en el admin para que las facetas luzcan

Los filtros están activos, pero solo hay **dos** y con los nombres por defecto. Nada de
esto es código — la UI los recoge sola en cuanto existan.

| Qué | Dónde | Por qué |
|---|---|---|
| Renombrar los grupos **«Availability» → «Disponibilidad»** y **«Price» → «Precio»** | Apps → Search & Discovery → Filters → cada filtro → nombre | Hoy los títulos salen **en inglés** sobre una tienda en español. Los *valores* sí vienen traducidos («En existencia» / «Agotado»); solo el nombre del grupo está sin traducir |
| Añadir el filtro **Tipo de producto** (`product_type`) | Apps → Search & Discovery → Filters → Add filter | Es el que pinta el sidebar del mock («Vajillas», «Platos», «Tazas»…). Sin él las facetas se quedan en Disponibilidad + Precio |
| Opcional: **Colección**, **Proveedor**, o metacampos (color, nº de piezas) | mismo sitio | Cada uno aparece como un acordeón más, sin tocar el tema |
| Revisar el orden de los filtros | mismo sitio, arrastrando | Es el orden en que se pintan en la columna |

Después de cambiar cualquiera de estos: recargar `/collections/all` y comprobar que el
acordeón nuevo aparece. No hace falta `theme push` — el tema no los conoce por nombre.

---

## 2 · Pendiente de implementar

### Facetas de colección (Fase B) — ✅ HECHA (2026-09-05)

Implementada en `snippets/collection-filters.liquid` (nuevo), enganchada desde
`snippets/collection-nav.liquid` y con CSS/JS en `sections/collection-grid.liquid`.

**Nada está hardcodeado**: la UI itera `collection.filters`, así que cualquier filtro que
el cliente añada en Search & Discovery aparece solo, sin tocar código. Cubre `list` /
`boolean` (checkboxes con `count`, valores inalcanzables en `disabled`) y `price_range`
(min/max en unidades enteras; Shopify los da en céntimos).

- El `<form method="get">` **es** la funcionalidad: sin JS navega y Shopify filtra en
  servidor. El JS solo lo mejora — reemplaza el nodo raíz de la sección con la respuesta
  de la Section Rendering API y hace `history.replaceState`. Como se sustituye la raíz
  entera, `init()` vuelve a montar acordeón, orden, «Cargar más» y `budget_mode` sin un
  segundo camino de código; cualquier fallo cae a `location.assign()`.
- Chips de activos + «limpiar» sobre la rejilla, cada uno un `<a href="url_to_remove">`
  real (funcionan sin JS; el JS los intercepta).
- Móvil: el sidebar **es** el drawer (`.filters-drawer-open`), no hay un segundo árbol de
  markup. Botón «Filtrar» con contador en la toolbar, cierre por Esc, por la ✕ y por el
  velo. Dentro del drawer no se auto-aplica al marcar: ahí manda el botón «Aplicar».
- i18n: 8 claves nuevas bajo `sections.collection.*` en `es.default.json` **y** `en.json`.

Sobre el helper `sort_filter_query` que la versión anterior de este doc daba por hecho:
**no hacía falta**. No existen URLs de ordenación donde inyectar los filtros — el orden es
client-side (`applySort` sobre el DOM). Los filtros son un GET puro y por eso no chocan
con el contrato de §3.

Verificado el 2026-09-05 contra la tienda real (`theme dev`, `/collections/all`, 438
productos):

| Comprobación | Resultado |
|---|---|
| `?filter.v.price.gte=0&lte=50` | 261 de 438 |
| `?filter.v.price.gte=200` | 34 de 438 |
| `?filter.v.availability=0` | rejilla vacía, sin romper |
| `paginate.next.url` conserva el filtro | `?filter.v.price.gte=200&page=2` → «34 de 34» |
| Section Rendering API con `section_id` | 200, devuelve `.collection-grid` con form y chips |
| «Translation missing» | 0, en `/collections/all` y `/collections/emblemas` |
| `shopify theme check` | 0 errores |

**Lo que falta es del admin, no del código** — ver §1.1b.

### Barrido de copy en el catálogo — BLOQUEADO por §1.4

El cliente pidió tres correcciones de copy (2026-09-05). Las del **tema** están hechas y
publicadas en live (§6). Falta lo que vive en el **admin** y el tema no controla:
descripciones de producto, metafields, y páginas/blogs creados desde el admin.

Palabras a barrer: `Calcomanía` → `Decorado`, `Vidriado` → `Esmaltado`.
(«Made in Spain» ya no aplica: era una textura, no texto. Ver §6.)

**La CLI de Shopify no sirve para esto — no la busques.** Comprobado con `@shopify/cli 3.86.0`:
los únicos topics son `app`, `auth`, `config`, `hydrogen`, `theme`. No existe `shopify api`
ni `shopify store`, no hay «Admin CLI», y el token que la CLI guarda tiene scope de temas.

El camino es la **Admin GraphQL API**:

1. Admin → Settings → Apps and sales channels → Develop apps → Create an app → Admin API
   scopes `read_products` + `write_products` (+ `read_metaobjects` / `write_metaobjects` si
   el copy vive en metaobjects) → Install → copiar `shpat_…`.
2. El token **no va al repo ni pegado en un chat**: a `~/.shopify-cartuja-token`, `chmod 600`.
3. Query paginada de `products` buscando las dos palabras en `title`, `descriptionHtml` y
   metafields → enseñar el antes/después → aplicar con `productUpdate` en lote.
4. Revocar el token al terminar (Uninstall en la misma pantalla).

Lectura sin token: no hay. `https://la-cartuja-de-sevilla.myshopify.com/products.json`
devuelve **302** — la tienda está con contraseña de escaparate. Con esa contraseña se pueden
*localizar* los productos afectados, pero no editarlos.

### Otros huecos conocidos

- **Selector de variante en «Viste tu mesa»**: hoy se asume
  `selected_or_first_available_variant`. Vale porque el catálogo de vajilla es mono-variante.
  Si entra producto multi-variante, hay que revisarlo (~4 h). No es urgente.
- **`intent=complementary`** en `product-related` necesita el metafield de Search & Discovery
  configurado por producto. Si no, la API devuelve vacío y la fila cae al grid de colección
  (comportamiento correcto, pero no es la venta cruzada que se pidió).
- **La venta cruzada nunca se ha ejecutado contra Shopify.** `b6aa0d2` pasa `theme check` y
  el JS es válido, pero la llamada a `/recommendations/products` no se ha visto responder ni
  una vez: la verificación en verde de §4 cubre orden, facetas y «Viste tu mesa», no esto.
  Pendiente, en cuanto §1.3 esté hecho (~15 min):
  1. `shopify theme push --development --store=la-cartuja-de-sevilla`.
  2. Abrir un PDP → pestaña Red → debe verse
     `GET /recommendations/products?section_id=related_cross&product_id=…&intent=related` con 200,
     y las tarjetas de «Te puede interesar» deben cambiar respecto al primer render.
  3. Caso vacío: «Completa la mesa» con `intent=complementary` sin configurar → la fila se
     queda con el grid de colección, nunca vacía.
  4. Con JS desactivado: las dos filas siguen pintando el grid de colección.
  5. `shopify theme pull --development --path /tmp/x` y comprobar que `product.json`,
     `product.set.json` y `collection.sets-regalo.json` han aterrizado — Shopify rechaza JSON
     malo en silencio y `theme check` no lo detecta (CLAUDE.md §2).
- **`/collections/sets-regalo` tampoco se ha visto en un navegador.** Falta confirmar precio
  en serif, orden ascendente y que «Cargar más» lo conserva. Depende de que la colección
  exista (§1.2 / §1.4).

---

## 3 · Contratos que NO puedes romper

### `budget_mode` / `applySort()` en `collection-grid.liquid`

- `budget_mode` pone `.collection-page--budget` (precio serif) + `data-default-sort="low"`
  en el root. Es lo que ordena «Sets para regalo» por precio ascendente **en la página
  cargada**. Requisito explícito de la feature, no cosmética.
- **Una plantilla JSON no puede fijar `?sort_by=`.** Se elige por handle/suffix, y `sort_by`
  es un parámetro de la petición. Quien ocupa el sitio del respaldo cliente es el orden por
  defecto de la colección en el admin (§1.2 → `collection.default_sort_by`).
- Por tanto: **no borres `applySort()` ni `data-default-sort` hasta que §1.2 esté confirmado.**
  La parte visual de `budget_mode` se queda pase lo que pase.
- Alternativa si el cliente no quiere depender del admin: un setting `force_sort` que pinte
  el parámetro en los enlaces internos cuando `collection.sort_by != 'price-ascending'`.
  No cubre la primera visita limpia a `/collections/sets-regalo`. **No recomendado.**

### `product-related.liquid`

El primer render es **siempre** el grid de colección (SSR, crawler-safe); el fetch a la
Product Recommendations API lo sustituye solo si vuelve con productos. No inviertas ese
orden ni dejes que la fila pueda quedar vacía.

### `viste-tu-mesa.liquid`

- Copy en español hardcodeado a propósito (es un port 1:1 del mockup). No metas claves de
  locale solo para esta sección.
- `window.__VT_COLLECTIONS` emite `vid` **y** `av`. Cualquier cosa que construya un payload
  de carrito debe filtrar por los dos: un solo agotado hace que `/cart/add.js` rechace el
  lote entero.
- Todo lo que se inyecte en HTML desde el catálogo pasa por el `esc()` que ya existe.

---

## 4 · Verificación

```bash
shopify theme check                                   # 0 errores. 7 warnings RemoteAsset preexistentes
shopify theme dev --store=la-cartuja-de-sevilla       # http://127.0.0.1:9292
```

Comprobado el 2026-09-05 y en verde:

- `/pages/viste-tu-mesa` → 36 `vid` / 36 `av` emparejados en `__VT_COLLECTIONS`.

⚠️ **Tres comprobaciones de esta lista se han retirado el 2026-09-05**: describían una
página que este repo no tiene. Eran «3 enlaces de orden», «`?sort_by=price-ascending` →
precios ascendentes + `aria-current`» y «`paginate.next.url` conserva el parámetro». El
tema no emite `sort_by` en ninguna parte y el menú de orden son botones, no enlaces; no hay
ningún `aria-current` en `collection-grid.liquid`. Lo que sí sigue siendo cierto es que
`paginate.next.url` arrastra la query string que traiga la petición — pero hoy nunca lleva
`sort_by`. Si el trabajo de la sesión `theme-90` existe, está fuera de este repo.

Cuando toques la Fase B, además:

- `/collections/<handle>?filter.p.product_type=X` → checkboxes marcados y chips de activos.
  (El Liquid ya respeta ese parámetro **hoy**, antes de tener UI.)
- «Cargar más» conserva filtro y orden.
- Sin JS: el `<form>` GET sigue navegando.
- **Regresión obligatoria**: `/collections/sets-regalo` sigue en modo presupuesto y ordenada
  por precio ascendente después de «Cargar más».

### Check del carrito de «Viste tu mesa»

Hay 5 aserciones que ejecutan el código **real** del bundle compilado (todo disponible / uno
agotado / sin variante / todo agotado / escapado del título). Vive fuera del repo — el theme
es vanilla sin infra de tests — en el scratchpad de la sesión que lo escribió. Si lo
necesitas, se reconstruye en 5 min: extrae por regex `var prods = c.products.map(...)`,
`var cartItems = ...` y `var addBtn = ...` de
`http://127.0.0.1:9292/cdn/shop/t/7/compiled_assets/scripts.js`, mételos en un `new Function`
con stubs de `esc` y `resolve`, y comprueba los 5 casos.

---

## 5 · Estado del repo

⚠️ El árbol viene con ~50 archivos modificados y varios sin trackear de trabajo anterior
(`viste-tu-mesa.liquid`, `viste-pack.liquid`, `page.viste-tu-mesa.json` y sus assets **nunca
se han commiteado**). Esos cambios siguen **sin commitear**: decidir qué entra en cada commit
es del humano, no tuyo. No hagas `git add -A`.

⚠️ **El tema live ya contiene todo ese trabajo sin commitear.** El 2026-09-05 se hizo
`theme push` a `Theme Cartuja - EAD` #198652100949 (§6); antes de empujar, `theme pull` +
`diff -rq` daba el tema publicado **idéntico** al árbol de trabajo salvo los 4 archivos de esa
sesión. O sea: live ≡ working tree, no ≡ `main`. Un `git checkout` de esos ~50 archivos
perdería lo que hay publicado.

✅ **Ya está todo en `main`.** El 2026-09-05 se mergeó `feat/venta-cruzada-sets` en `main`
(merge commit `e869525`, 7 conflictos resueltos — el detalle está en su mensaje de commit).
La PR #1 se cerró sin mergear y el merge se hizo directo.

⚠️ **Ese merge dejó CSS duplicado.** En `sections/collection-grid.liquid`, el bloque
`/* v96 / v98 — listado en móvil */` completo y la regla `@media (hover: none) and
(pointer: coarse)` quedaron **dos veces** seguidas. Corregido en la sesión de cierre
(se conserva una sola copia; `budget_mode` y `applySort` intactos). Si vuelves a mezclar
algo sobre esa zona, comprueba `grep -c 'v96 / v98 — listado en móvil'` → debe dar `1`.

`assets/artesania-plate.glb` (2,8 MB, sin referencias) borrado en la misma sesión, como
proponía §6.

Sigue en pie que **`main` no es lo que está publicado**: lo publicado es el árbol de trabajo
local, con ~50 archivos modificados sin commitear encima de esto.

Últimos commits relevantes:

- `43260c6` — copy de Artesanía + sello del plato (§6). 4 archivos añadidos a mano.
- `a49e2e5` — plantilla «Sets para regalo» + `budget_mode`
- `b6aa0d2` — venta cruzada con la Product Recommendations API

---

## 6 · Correcciones de copy de Artesanía (hecho, 2026-09-05)

Commit `43260c6`, **publicado en el tema live** `Theme Cartuja - EAD` #198652100949.

| Petición | Dónde estaba | Qué se hizo |
|---|---|---|
| «Calcomanía» → «decorado» | `templates/page.artesania.json`, bloque `phase-5`, `label` (columna derecha de Artesanía) | `"Decorado · 800°C"` |
| | `assets/artesania-plate.js`, comentarios | cambiados también: el `.js` se sirve público |
| «Vidriado» → «Esmaltado» | `page.artesania.json` `phase-6` (`title` + `label`) y `badge3_text` — este último en el template **y** como default del schema en `sections/artesania.liquid` | `El <em>esmaltado</em>`, `Esmaltado · 1.050°C`, «…decoración y esmaltado…» |
| Sello del plato sin «Made in Spain» | **no era HTML**: es la textura del reverso del plato 3D, un JPEG en base64 dentro de `assets/artesania-textures.js` (`window.__resources.plateBack`) | Borradas del propio JPEG las dos líneas impresas bajo el ancla («Colores Inalterables» / «MADE IN SPAIN») con `ffmpeg -vf delogo=x=366:y=524:w=178:h=50`. Queda LA CARTUJA / ancla / SEVILLA 1841. 43 KB → 25 KB |

Notas para quien venga detrás:

- Las 4 apariciones de «MADE IN SPAIN» en `assets/sellos.js` son **descripciones históricas**
  del archivo de sellos (`/pages/identifica-tu-sello`, sellos nº 52, 53, 55 y 56). No se tocan.
- Los comentarios de `artesania-plate.js` que dicen «vidriado» describen el render del
  material, no son copy. Se dejaron a propósito.
- **Antes de cualquier push a live, comprueba la deriva del editor**: `theme pull` a un temporal
  + `diff -rq` contra el repo. `page.artesania.json` lleva la cabecera «auto-generated / may be
  updated by the Shopify admin theme editor», así que el admin puede haber pisado valores.
  En esta sesión no había deriva.
- Gotcha de la CLI (cuesta 20 min descubrirlo): `shopify theme pull --path <dir>` **falla en
  silencio** si el directorio no existe — dice «Theme download complete» y no escribe nada.
  `mkdir -p` primero. Y `--only` se ignora: no filtra, directamente no descarga.
- Push a live no interactivo: `shopify theme push --store=… --theme=<id> --live --allow-live
  --force`. Sin los flags se queda esperando una confirmación que nunca llega.
- Verificación post-push (hecha, en verde): `theme pull` de vuelta → 0 ocurrencias de
  `calcoman|vidriad` en `templates/ sections/ config/ locales/`, y la textura `plateBack`
  reconstruida da 25.350 bytes / md5 `491e7315be8f5e819276c71aa4128dea`, idéntica al JPEG limpio.
- `assets/artesania-plate.glb` (2,8 MB) no lo referenciaba nadie. **Borrado** el 2026-09-05 (§5).

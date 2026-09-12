# Scripts de Shopify Admin — lote de cambios 2026-09-09

Cuatro scripts de Python, sin dependencias, que aplican por API los cambios de Admin
del brief (`docs/cambios-2026-09-09/A1–A3`). **Ninguno escribe nada sin `--apply`**:
sin ese flag imprimen la mutación completa con sus variables y salen.

## Antes de empezar

La autenticación es la que ya tiene guardada el Shopify CLI (`store auth`), así que
no hay tokens aquí. Comprueba que responde:

```bash
npx -y @shopify/cli@4.7.1 store execute \
  --store la-cartuja-de-sevilla.myshopify.com \
  --query 'query { shop { name } }' --json
```

Permisos concedidos hoy: `write_products`, `write_online_store_navigation`,
`write_online_store_pages`, `write_content`, `write_metaobjects`, `write_translations`.
**No** hay `write_publications` (esconder colecciones) ni `write_inventory` (stock) ni
`write_url_redirects` (redirecciones).

## Orden

```bash
cd scripts/admin

python3 01_novedades_fin_existencias.py          # ensayo
python3 01_novedades_fin_existencias.py --apply

python3 02_colecciones_por_tipo.py --apply       # ANTES del menú: crea sus destinos
python3 03_menu_nuevo.py --apply
python3 04_mug_con_letra.py --apply
```

Cada uno deja un `informe-XX-*.json` con lo ejecutado (o lo planificado, en ensayo).
El del menú guarda además el `main-menu` anterior entero, por si hay que reconstruirlo.

## Qué hace cada uno

| Script | Cambia | Deshacer |
|---|---|---|
| `01_novedades_fin_existencias.py` | Crea las colecciones automáticas `novedades` y `fin-de-existencias` (por etiqueta) y etiqueta como `novedad` los seis productos del brief | Borrar las colecciones / quitar la etiqueta |
| `02_colecciones_por_tipo.py` | Una colección automática por tipo de producto (24 hoy), con el handle que busca el theme para «te puede interesar» | Borrar las colecciones creadas (van en el informe) |
| `03_menu_nuevo.py` | Reescribe `main-menu` y crea `menu-derecha` con el árbol del brief; salta las entradas sin destino y las lista | Reconstruir desde el informe |
| `04_mug_con_letra.py` | Crea `mug-con-letra` en borrador con 27 variantes (A–Z + Ñ), precio, SKU y foto de cada letra | Borrar el producto |
| `10_fin_existencias_productos.py` | Da de alta los 52 productos de «Fin de existencias» de la web antigua (`datos-10-fin-existencias.json`): activos, precio rebajado + anterior tachado, SKU/EAN, foto importada, metafields y etiqueta `fin-de-existencias` | Borrar los productos (van en el informe) |

## Lo que estos scripts NO resuelven

- **Esconder Emblemas**: falta el permiso `write_publications`. Hay que aprobarlo con
  `store auth --scopes ...` o despublicar la colección a mano. Del menú y del theme ya salió.
- **«Agotado»**: falta `write_inventory`. Hoy todo el catálogo está a 0 con política
  DENY, así que ya sale agotado por sí solo.
- **Qué filtros se ven** en el listado: es la app Search & Discovery, sin API.
- **Apple Pay / PayPal**: Configuración → Pagos, a mano.
- **Redirecciones** de los productos que se archiven: falta `write_url_redirects`.

## Después de aplicar el lote 3

El theme sigue con su árbol de demostración hasta que se le diga qué menú usar: en el
editor de temas, ajustes de las secciones **Header** y **Mega menu**, elegir `main-menu`
y `menu-derecha`; en **Collection grid**, el menú del lateral.

## Lo que sigue haciendo falta del cliente

- Los seis productos de «Nuevo» (Áurea, Vela aromática, Lapicero, Caja 6 posavasos,
  Vaciabolsillos, Abanico): **no existen todavía** en el catálogo.
- Qué productos van en las subfamilias sin tipo propio: Cubitera, Tarros de botica,
  Mancerina, Hoja de parra, Vela, Lapicero, Bandeja Vistas, Bandeja Conmemorativa,
  Vaciabolsillo, Conjunto de baño, Cepillero, Jabonera, Algodonera, Libro, Camiseta,
  Bolsa, y los agrupadores Artístico / Baño / Gifts.
- Las colecciones de decorado que faltan: Áurea, Georgica, Edén, Laberinto, Peces y
  Basic Line Blue. Los productos de fin de existencias (lote 10) ya existen con
  `custom.decorado`; falta `custom.forma` en todos menos Yedra y Basic Line Red.
- Cuál es exactamente el «Taza sin platillo» que hay que eliminar: las 21 tazas sin
  «con platillo» en el título son Consomé y Desayuno, y el menú nuevo las mantiene.
- Las fotos IA: la principal del mug unificado y las segundas imágenes del hover.

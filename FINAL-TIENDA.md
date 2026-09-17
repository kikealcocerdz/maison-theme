# FINAL-TIENDA — qué falta para salir a producción

Auditoría del 2026-09-16 sobre `la-cartuja-de-sevilla.myshopify.com`: Admin GraphQL (lectura,
CLI Connector) + Admin UI en navegador + estado del repo. El contenido anterior de este archivo
(handoff de agosto/septiembre) está en el historial de git; lo que sigue vigente se ha integrado.

Leyenda: **[cliente]** lo tiene que hacer o decidir el cliente · **[admin]** lo hace el agente con
un script en `scripts/admin/` · **[theme]** código del repo · **[manual]** Admin UI, sin API.

## 0 · Información que falta

Datos que tiene que aportar el cliente.

### A · Para cobrar (Shopify Payments + PayPal) — lo mete el cliente en el panel
- Razón social, CIF/NIF, dirección fiscal completa y **entidad que factura** (¿DORINDA o LA
  CARTUJA DE SEVILLA?). Es la misma que va en las políticas.
- Persona representante: nombre, DNI, fecha de nacimiento (KYC de Shopify Payments).
- IBAN de la cuenta donde se reciben los pagos.
- Cuenta PayPal Business (correo) si se quiere PayPal.
- Tarjeta para el plan de Shopify (facturación mensual).
- Acceso al buzón `info@lacartujadesevilla.com` para verificar el remitente.
- Dirección física de la tienda/almacén (calle, CP, ciudad) y teléfono de atención.

### B · Para entregar (envíos e inventario)
- Transportista definitivo (DHL app, otro, o tarifas planas) y **tarifa por zona**: Península,
  Baleares, Canarias/Ceuta/Melilla, UE, resto. Umbral de envío gratis (hoy 150 €).
- Si se envía fuera de la UE de verdad; si no, se desactivan esos mercados.
- Peso aproximado por tipo de pieza (plato llano, taza, sopera, vajilla 42/56…): una tabla, no
  producto a producto.
- Decisión de inventario: ¿control de stock sí o no? Si sí, **Excel SKU → unidades**.
- Plazos de entrega y condiciones de devolución (días, quién paga el retorno, roturas).

### C · Textos legales
- Las 6 políticas revisadas o el visto bueno a las actuales: devoluciones, privacidad, términos,
  envío, contacto, aviso legal. Con la entidad de A.
- Título y meta descripción de la portada (≤70 / ≤320 caracteres) e imagen para redes (1200×628).

### D · Catálogo: precios
- PVP de los 10 a 0,00 €: Áurea, Lapicero, Bolsa, Camiseta, Libro, Bandeja conmemorativa,
  Vela aromática 202 Rosa / Ceilán / Edén / Negro Vistas.
- Confirmar los ya asumidos: mugs nuevos 29,95 · vaciabolsillos Abanico 46,95 · Blanco 37,95
  (vs «Bandeja Cartuja Blanca» 28,95).
- ¿Se vende «Envoltorio de regalo»? Precio o se retira.

### E · Catálogo: fotos
- Producto (sustituyen «Próximamente»): Lapicero, Jabonera, Algodonera, Conjunto de baño,
  Bandeja conmemorativa. Y una foto de «Envoltorio de regalo» si se vende.
- Colección (46, formato apaisado, misma luz): Novedades, Fin de existencias, Sets para regalo,
  Vajillas completas, Juegos de café, Juegos de té, Juegos de boles, Arte y colección, Objetos
  decorativos, Baño, Gifts, Áurea, Georgica, Edén, Vistas A. Stewart, Negro Vistas ASH Blue /
  Yellow, Ochavada Blanca, Oaxaca, y una por tipo de pieza (Azucareros, Bajoplatos, Bandejas,
  Boles, Bomboneras, Cabezas frenológicas, Cafeteras, Champaneras, Ensaladeras, Floreros,
  Fuentes, Jarros, Juegos, Lecheras, Mugs, Aguamaniles, Platillos, Platos, Salseras, Servicios,
  Soperas, Tazas, Teteras, Vajillas). Si no hay tiempo, indicar qué producto usar de portada.

### F · Catálogo: textos
- Descripción (o plantilla por tipo que aprobar): 44 tazas (café / consomé / desayuno con
  platillo), 42 juegos (boles y mini boles) y las 19 novedades (Áurea, Lapicero, Caja 6
  posavasos, Vaciabolsillos, Tarro de botica, Hoja de parra, Mancerina, Cepillero, Bolsa,
  Camiseta, Libro, Jabonera, Algodonera, Conjunto de baño, Bandeja conmemorativa, 4 velas).
- Descripción corta (2 líneas) de 35 colecciones: las de tipo de pieza + Flor de Lis, Vajillas
  completas, Arte y colección, Objetos decorativos, Baño, Gifts, Áurea, Georgica, Edén.

### G · Catálogo: datos de ficha
- SKU de las 29 piezas nuevas (novedades, 9 mugs, 4 velas, envoltorio).
- Medidas de 166 productos, por tipo: 47 tazas, 42 juegos, 11 vajillas, 10 platos, 10 mugs,
  6 cafeteras, 4 lecheras / fuentes / salseras / velas, 2 soperas / teteras / platillos y las
  novedades. Con una tabla «tipo → medidas» se cubre casi todo.
- Decorado de las 30 piezas que no lo llevan en el título: blancos (bajoplato, boles,
  bombonera, champanera, plato pan, taza desayuno, juegos boles), Bandeja Vistas (7), Florero
  Alhambra (4), Jarro Cartuja (4), Palangana Cartuja (4), Cabeza frenológica. ¿Qué valor va
  en el filtro «Decorado»?
- Visto bueno para archivar los 27 «Mug Letra A–Z» sueltos (ya existe «Mug con letra»).
- Código arancelario (HS) y origen para las 123 variantes nuevas, o permiso para copiar el de
  las piezas migradas.

### H · Idiomas y marketing
- Traducción al inglés revisada de los 80 sellos de «Identifica tu sello» (o dejarlos solo en
  español) y de los textos de esa página.
- ¿«Viste tu mesa» solo en español? Sí/no.
- Accesos: Google Search Console, GA4, Meta Business (si se quieren).
- ¿Descuento de bienvenida por newsletter? Porcentaje y condiciones.
- Sitemap o listado de URL de la web antigua (o dejar que lo rastreemos antes de apagarla).

---

## 1 · Bloqueantes — sin esto no se vende

| # | Qué | Estado hoy | Quién |
|---|---|---|---|
| 1 | **Plan de pago** | Plan «Custom · Tienda en desarrollo» (`partnerDevelopment: true`). Sin plan no se quita la contraseña ni se cobra de verdad | [cliente] Configuración → Plan |
| 2 | **Pagos** | Shopify Payments sin completar; PayPal sin activar; aviso «solo pagos de prueba». Apple Pay / Google Pay vienen con Shopify Payments | [cliente] Configuración → Pagos. Hace falta datos fiscales + cuenta bancaria de la entidad |
| 3 | **Dominio** | Solo `la-cartuja-de-sevilla.myshopify.com`. `lacartujadesevilla.com` sigue sirviendo la web antigua (PrestaShop) | [cliente] conectar dominio + DNS; decidir día del cambio (corte de la web antigua) |
| 4 | **Email remitente sin verificar** | `info@lacartujadesevilla.com` → «No verificado». Sin esto los correos de pedido salen desde `no-reply@shopify` o no salen | [cliente] Configuración → Notificaciones → Reenviar verificación (llega al buzón de info@) |
| 5 | **Contraseña de escaparate** | Activada. Se quita al pasar a plan de pago | [cliente] tras el plan |
| 6 | **Envíos: perfil en la sucursal equivocada** | El perfil general solo cubre «Shop location» (la genérica); «Almacén Sevilla» existe pero no tiene tarifas. Si el stock se asigna al almacén, nadie podrá pagar | [manual] Envío y entrega → Perfil general → añadir Almacén Sevilla (o borrar «Shop location») |
| 7 | **Envíos: tarifas provisionales** | Península 6,99 € (<150 €) / gratis (≥150 €); Baleares 9,99 «(provisional)»; Canarias-Ceuta-Melilla 14,99 «(provisional)»; UE 8,99; Internacional 12,99. DHL Commerce conectado pero **desactivado** en todas las zonas. Entrega local y recogida en tienda desactivadas | [cliente] confirmar tarifas y transportista (DHL app o tarifas planas). Vajillas 42/56 piezas a 6,99 € es probable pérdida |
| 8 | **Inventario: nada se controla** | Las 594 variantes están `tracked: false` con cantidad 0 (una ya en −1 por el pedido de prueba). Se vende todo siempre, sin límite. Lote 20 (10 uds) no aplica a variantes sin seguimiento | [cliente] decidir: (a) seguir sin control (riesgo de vender sin stock) o (b) activar seguimiento + carga de stock real → [admin] script: `inventoryItemUpdate tracked:true` + `inventorySetQuantities` desde su ERP/Excel, en Almacén Sevilla |
| 9 | **Peso 0 en los 493 productos** | Sin peso no hay tarifas por transportista (DHL) ni etiquetas; con tarifas planas funciona pero mal | [cliente] tabla peso por tipo → [admin] `inventoryItemUpdate measurement.weight` |
| 10 | **Dirección de la tienda** | General → «Dirección de la tienda: España» (incompleta). Aparece en facturas, correos y como origen de envío | [cliente] Configuración → General |
| 11 | **Políticas legales nativas** | El footer enlaza `/policies/shipping-policy` y `/policies/refund-policy` (nativas). Contenido no verificable por API (falta scope `read_legal_policies`). «Reglas de devolución: no hay reglas establecidas». Entidad responsable sin confirmar (DORINDA vs LA CARTUJA DE SEVILLA) | [cliente] revisar las 6 políticas en Configuración → Políticas y fijar entidad, plazos de devolución, gastos |
| 12 | **Pedido de prueba** | Hay 1 pedido (de prueba) que ya ha descontado stock | [manual] archivar/cancelar antes de abrir; no dejar pedidos de prueba en informes |

Impuestos: Shopify Tax activo, «precios con impuestos incluidos» ✓, IVA UE por región ✓. Revisar
solo con la gestoría: Canarias/Ceuta/Melilla (IGIC/IPSI, no IVA) y ventas UE por encima del umbral
OSS. [cliente]

---

## 2 · Catálogo (Admin) — visible al comprador

Cifras del 2026-09-16: 520 productos (493 activos, 27 borrador), 594 variantes, 67 colecciones,
12 páginas.

| # | Qué | Cuántos | Quién |
|---|---|---|---|
| 1 | **Precio 0,00 €** activos y a la venta | 10: `aurea`, `lapicero`, `bolsa`, `camiseta`, `libro`, `bandeja-conmemorativa`, 4 `vela-aromatica-*` | [cliente] PVP → [admin] `productVariantsBulkUpdate`. Mientras no haya precio: pasar a borrador |
| 2 | **Foto «Próximamente»** | 5: lapicero, jabonera, algodonera, conjunto-de-bano, bandeja-conmemorativa | [cliente] fotos → [admin] lote tipo 13 |
| 3 | **Sin descripción** | 105 (juegos de boles, tazas café/consomé/desayuno, platillos…) | [cliente] texto o plantilla por tipo → [admin] `productUpdate` masivo con plantilla «{Tipo} de loza {decorado}…» si el cliente la aprueba |
| 4 | **Sin SKU** | 29 (novedades lotes 09–18 y los 9 mugs) | [cliente] referencias → [admin] |
| 5 | **Sin EAN** | 478 (solo los 52 de fin de existencias lo tienen) | opcional; necesario para Google Shopping / marketplaces |
| 6 | **Sin `custom.dimensiones`** | 166 (la ficha oculta la fila; no rompe) | [cliente] medidas → [admin] `metafieldsSet` |
| 7 | **Sin `custom.decorado`** | 60 (blancos, Vistas, Alhambra, Cartuja, novedades) — no salen en el filtro «Decorado» | [admin] rellenable desde el título en la mayoría; el resto [cliente] |
| 8 | **Sin código HS / país de origen** | 123 variantes (las nuevas). Aduanas para envíos fuera de la UE | [admin] copiar HS + `ES` de las piezas migradas si el cliente confirma |
| 9 | **27 «Mug Letra X» en borrador** | Ya sustituidos por `mug-con-letra` (27 variantes). Decidir archivar | [cliente] ok → [admin] `productUpdate status: ARCHIVED` |
| 10 | **Colecciones sin imagen** | 46 de 67 (todas las de tipo, decoración nuevas, `all`, `novedades`, `fin-de-existencias`, `sets-regalo`) — la rejilla de colecciones y el mega-menú usan fallbacks del theme | [cliente] fotos → [admin] `collectionUpdate image` |
| 11 | **Colecciones sin descripción** | 35 (SEO + cabecera de PLP vacía) | [cliente] o textos cortos propuestos por el agente para aprobar |
| 12 | **`sets-regalo` sin plantilla** | La colección existe (53 productos) pero `templateSuffix: null` → `templates/collection.sets-regalo.json` (modo presupuesto, precio ascendente) **no se aplica**. Orden por defecto sin confirmar | [admin] `collectionUpdate templateSuffix: "sets-regalo", sortOrder: PRICE_ASC` — 1 mutación |
| 13 | **`envoltorio-de-regalo`** activo sin foto ni SKU | 1 | [cliente] ¿se vende? si no, borrador |
| 14 | Vendor con dos grafías | «La Cartuja de Sevilla» ×492, «LA CARTUJA DE SEVILLA» ×1 | [admin] trivial |

Precios ya asumidos por el agente y **pendientes de confirmar**: mugs nuevos 29,95; vaciabolsillos
Abanico 46,95; Blanco 37,95 vs «Bandeja Cartuja Blanca» 28,95 (memoria `project-pendientes`).

Search & Discovery: filtros activos (Disponibilidad, Precio, Tipo, Forma, Decorado) ✓.
Productos complementarios («Completa la mesa») sin rellenar → la fila cae al grid de colección.

---

## 3 · SEO, migración de la web antigua y marketing

| # | Qué | Estado | Quién |
|---|---|---|---|
| 1 | **Título y meta descripción de la home** | Vacíos (Tienda online → Preferencias). Imagen para redes sociales sin subir | [cliente] textos → [manual] |
| 2 | **Redirecciones desde PrestaShop** | Hay 67 redirects (handles antiguos de vajillas 42/56 P). **Ninguna** desde las URL de `lacartujadesevilla.com` (`/630-fin-de-existencias`, `/xx-producto.html`…). El día del cambio de DNS, todo el posicionamiento antiguo dará 404 | [admin] crawl del sitemap antiguo antes de apagarlo → mapa URL vieja → handle nuevo → `urlRedirectCreate` (scope `write_url_redirects` pendiente de aprobar) |
| 3 | `/pages/historia` → `/pages/heritage-1841` | No existe (comprobado por API) | [admin] con el mismo lote de redirects |
| 4 | **Google Search Console / GA4 / Meta Pixel** | No comprobado (la página de Preferencias no deja bajar por el iframe). Search Console solo tiene sentido con el dominio final | [cliente] accesos → [manual] |
| 5 | **Inglés** | `en` publicado. Faltan: los 80 sellos de `assets/sellos.js` (solo ES), settings de `page.identifica-tu-sello`, y decidir si «Viste tu mesa» se queda solo en ES | [cliente] traducción revisada → [admin] `translationsRegister` |
| 6 | **Descuentos / código de bienvenida** | No verificable (falta `read_discounts`). El formulario de newsletter del footer existe; no hay automatización de bienvenida | [cliente] decidir → [manual] Shopify Email / Flow |
| 7 | Mercados | 7 activos (España, Canarias-Ceuta-Melilla, UE, Reino Unido, Chile, Golfo y Asia, Norteamérica y Oceanía) con 16 monedas. Coherente con las zonas de envío. Si no se va a enviar fuera de la UE, desactivar mercados para no prometer lo que no se cumple | [cliente] |

---

## 4 · Theme y repo

- **Tema live**: «Maison — live 2026-09-09» `#203447337`. También: «Maison — WhatsApp + popup
  (review)» `#202722443`, «Theme Cartuja - EAD» `#198652100`, «Horizon» (stock). Borrar los que
  sobren antes de entregar.
- **Repo divergido**: rama `auditoria-web-12-puntos` = 45 commits por delante de `origin/main` y
  **37 por detrás** (`main` lleva la burbuja de ayuda, QA checklist…). 92 archivos sin commitear
  en el árbol de trabajo. Hay que reconciliar (decisión humana: qué entra), commitear, y que
  **el tema live salga de un commit**, no del árbol sucio. Hoy no se puede afirmar qué commit
  está publicado.
- Antes del push final: `shopify theme check` (0 errores, solo `RemoteAsset`), `theme pull` +
  `diff -rq` contra el repo para detectar deriva del editor, y comprobar que locales/JSON
  aterrizan (Shopify rechaza JSON malo en silencio).
- Theme editor tras publicar: Header / Mega menu → `main-menu` + `menu-derecha`; Collection grid
  → `colecciones-sidebar`. Verificar que el live los tiene seleccionados (si no, pinta el demo).
- Pendientes de verificación en navegador con datos reales: `/collections/sets-regalo` en modo
  presupuesto (bloqueado por §2.12), `/recommendations/products` respondiendo en PDP, checkout
  completo con pago de prueba, correos de pedido en español.
- Checkout: perfil «Configuración de La Cartuja de Sevilla» publicado ✓; contacto por email ✓;
  cuentas de cliente nuevas (`shopify.com/…/account`) ✓; crédito en tienda activado (¿se quiere?).
- `assets/artesania-plate.glb` (2,8 MB) sin referencias: borrar.

---

## 5 · Orden propuesto

1. [cliente] Plan de pago → Shopify Payments + PayPal → verificar email remitente → dirección
   completa → políticas. (Todo en Admin, 1–2 h con los datos a mano.)
2. [cliente] Decidir inventario (controlar o no), tarifas de envío definitivas, transportista,
   mercados fuera de la UE.
3. [admin] Lote 23: `sets-regalo` template + orden; vendor; archivar Mug Letra; HS/origen.
4. [cliente]→[admin] PVP de los 10 a 0 €, fotos de los 5 «Próximamente», SKUs, pesos,
   descripciones (o plantilla aprobada), dimensiones/decorado que falten.
5. [admin] Redirects: crawl de la web antigua + `/pages/historia`; pedir scope
   `write_url_redirects`.
6. [theme] Reconciliar ramas, commit, `theme check`, push a un tema nuevo, QA con pago de
   prueba en móvil y escritorio, publicar.
7. [cliente] Dominio: conectar `lacartujadesevilla.com`, esperar SSL, quitar contraseña, apagar
   PrestaShop. Search Console + sitemap el mismo día.
8. Borrar pedido de prueba y temas sobrantes.

Lo que un agente **no** puede hacer por API en esta tienda: pagos, plan, dominio, verificación de
correo, políticas (sin scope), descuentos (sin scope), Search & Discovery (sin API), Shopify
Email/Flow. Lo demás va por `scripts/admin/` con ensayo → `--apply` → informe.

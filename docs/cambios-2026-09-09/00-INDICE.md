# Cambios de cliente — 2026-09-09 · índice

Brief del cliente troceado por área y por **propietario** (`AGENTS.md`: Admin = Claude,
repo/theme = Codex). Es contexto: nada de esto está implementado.

Regla transversal para todo el lote: si un producto no existe todavía en catálogo, su ficha
debe salir como **“Agotado”** hasta tenerlo. Antes de crear nada, comprobar si ya existe en la
web actual de La Cartuja.

## Solo Admin (navegación, catálogo, metafields)

| Doc | Contenido |
|---|---|
| [A1 · Menú y navegación](A1-admin-menu-navegacion.md) | Menú nuevo izquierda/derecha, hamburguesa, retirada de Emblemas |
| [A2 · Catálogo y productos](A2-admin-catalogo-productos.md) | Agotados, Taza sin platillo, Mug con letra por variantes, etiqueta Novedad, piezas pendientes |
| [A3 · Datos para filtros](A3-admin-datos-filtros.md) | Color, forma, tipo de producto, Novedades / Fin de existencias |

## Solo theme (Liquid / CSS / JS)

| Doc | Contenido |
|---|---|
| [T1 · Home](T1-theme-home.md) | Titular Heritage y correcciones móviles de la portada |
| [T2 · Móvil en páginas existentes](T2-theme-movil-paginas.md) | Todas las colecciones, Nuestras mesas, Viste tu mesa, Artesanía |
| [T3 · PLP: filtros y panel lateral](T3-theme-plp-filtros.md) | Orden del lateral, “+ Filtros” como panel superpuesto |
| [T4 · Tarjetas de producto](T4-theme-tarjeta-producto.md) | Fondo blanco, estados/etiquetas, hover con segunda imagen |
| [T5 · PDP](T5-theme-pdp.md) | Dimensiones duplicadas, tipografía 14px, arreglos móviles |
| [T6 · Vajillas](T6-theme-vajillas.md) | Vista de piezas, “PIEZAS”, packs 56p/42p, enlaces del pack |
| [T7 · Cesta y búsqueda](T7-theme-cesta-busqueda.md) | Avisos de la cesta, pasarela, X unificada |

## Mixto (Admin + theme)

| Doc | Contenido |
|---|---|
| [M1 · Orden de resultados y relacionados](M1-mixto-resultados-relacionados.md) | Intercalado en PLP y lógica de sugeridos por tipo/colección |

## Fuera de este lote

- Extras pedidos por el cliente (mapamundi “Tu tienda más cercana”, blog de noticias,
  “Trabaja con nosotros” con `RRHH@lacartujadesevilla.com`): páginas nuevas, no entran aquí.
- Cuentas de usuario con favoritos, direcciones e historial: el cliente lo marcó **no urgente**.

## Dudas abiertas (bloquean ejecución)

1. **“Ambientes”** sustituye a “Nuestras mesas”: ¿solo rótulo, o también handle y URL?
   Si cambia la URL hace falta redirección.
2. **Emblemas**: ¿despublicar la colección o solo sacarla de menús y laterales?
   El cliente prefiere “esconder o deshabilitar”, falta concretar cuál.
3. **Heritage**: el menú dice “Heritage 1842” y el titular de home “…Pickman . 1841”.
   Confirmar el año correcto en cada sitio.

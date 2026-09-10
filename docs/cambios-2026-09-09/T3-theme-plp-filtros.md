# T3 · PLP: menú lateral y filtros — theme

Propietario: **repo (Codex)**, `sections/collection-grid.liquid` + facetas.
Los datos de cada filtro los prepara Admin (`A3`).

## Orden del menú lateral

Botón de novedades a la altura de las colecciones, y fin de existencias justo debajo:

```
Novedades
Fin de existencias
Aurora +
Ochavada +
Decoración +
Tipo de producto +
```

- **Tipo de producto** deja de ser faceta suelta: cuelga debajo de **Decoración**, con todos los
  productos y en **orden alfabético**.
- Como sección quedan **solo las colecciones**.
- **Fin de existencias** se destaca en otro color (igual que en el hamburguesa, `A1`).

## Filtros

- Añadir **colores**.
- **Forma**: añadir **Imperio / Viena** a Ochavada y Vega.
- Añadir **Novedades** (dentro de disponibilidad o como filtro propio).
- **Quitar** el filtro de **decorado**.

## Panel “+ Filtros”

Debajo del bloque anterior, un botón **“+ Filtros”**:

- Al pulsarlo, la caja de filtros se convierte en un **desplegable lateral por la izquierda** que
  **solapa** el menú ya existente.
- Contiene **solo los filtros adicionales**.
- **X arriba** para cerrar.
- **Abajo, dos botones**: *quitar todos los filtros* y *ver todos (nº de resultados)*.
- Estilo: simple y limpio, similar a la web que le gusta al cliente pero adaptado al nuestro, y
  **diferenciado** del lateral normal (propone fondo gris oscuro).

## Reordenar Decoración

Presentación más visual siguiendo la jerarquía Artístico / Baño / Gifts de `A1`.

## Limpieza

- Quitar los **textos pequeños debajo de las fotos horizontales** en las páginas de producto
  principales.

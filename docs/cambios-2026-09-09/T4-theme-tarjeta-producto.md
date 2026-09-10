# T4 · Tarjeta de producto — theme

Propietario: **repo (Codex)**. `snippets/*-card.liquid`, `blocks/product-card.liquid`.
Aplica a PLP, búsqueda, relacionados y home.

## Fondo

Los productos van en **PNG** y al cliente le gusta el **fondo blanco**, no gris.

## Estados y etiquetas

Referencia de diseño: https://cartuja.gropius.link/sistema-visual.html#states/9
(se puede adaptar el diseño si hace falta).

- **Novedades**: tira de color **azul**, para que se lea sobre el fondo blanco.
- **Fin de existencias**: estados de demanda tipo **últimas unidades / última unidad**.
- **Productos emblemáticos**: **Éxito en ventas / Muy solicitado**.
- La etiqueta “Novedad” solo debe salir en los 6 productos de `A2`.

## Hover con segunda imagen

Recuperar la funcionalidad: al hacer hover aparece la **segunda imagen** del producto, con
transición **fade in / fade out** fluida. Referencia que le gusta al cliente:
https://www.spode.co.uk/

Las segundas imágenes las irá subiendo el cliente (generadas con IA, ver `A2`); el theme debe
degradar bien cuando un producto todavía no tenga segunda imagen.

# A2 · Catálogo y productos — Admin

Propietario: **Admin (Claude)**. Cambios de producto, variantes y etiquetas.

## Disponibilidad

- Producto que aún no tenemos → la página debe poner **“Agotado”** hasta tenerlo.
- Antes de crear nada, revisar la web actual de La Cartuja por si el producto ya existe.

## Taza sin platillo

Eliminar el producto **“Taza sin platillo”**: no existe taza que no lleve platillo.
Toda taza va con platillo; el cliente enviará las fotos.

## Mug con letra

Los mugs de letras ocupan demasiados huecos de catálogo. Unificar en **un solo producto**:

- Título: **“Mug con letra”**.
- Imagen principal: generada con IA con todos los mugs juntos (la aporta el cliente).
- **Variantes por letra** (abecedario) en lugar de productos separados.
- Al seleccionar la letra debe mostrarse la foto de producto de esa letra, tipo
  AliExpress / Shein.

Requiere imagen por variante. La parte de selector/cambio de imagen la cubre el theme (`T5`).

## Etiqueta “Novedad”

Hay muchos artículos etiquetados como novedad que no lo son. **Quitar la etiqueta de todos** y
dejarla solo en:

- Áurea
- Vela Aromáticas
- Lapicero
- Caja con 6 posavasos
- Vaciabolsillo
- Abanico

Esa misma lista es la que cuelga del menú **Nuevo** (`A1`).

## Segunda imagen de producto (hover)

El cliente irá generando con IA una **segunda imagen** por producto para el hover del PLP.
Admin: subirla como segunda imagen del producto. El efecto lo hace el theme (`T4`).

## Piezas pendientes

Quedan bastantes piezas de decoración por incorporar, algunas ni siquiera están en la web
actual. El cliente las irá mandando.

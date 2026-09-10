# T5 · Página de producto (PDP) — theme

Propietario: **repo (Codex)**, `sections/product-detail.liquid` y relacionados.

## Escritorio

- **“Dimensiones” aparece dos veces**. Dejar la que **no** es desplegable para que se vea de
  primeras, pero su texto tiene que ser **negro**, no gris.
- Titular y descripción están en **12px** y se ven muy pequeños: **pasar a 14px**.
  Referencia de tamaños: http://spode.co.uk/ — pero sin que el texto sea tan grande que en
  pantallas pequeñas ocupe demasiado.

## Móvil

- Al cargar se ve como en la captura del cliente: debería verse la **foto completa**, quitando
  quizá el espacio de encima.
- El **botón de mensaje** debe ir **encima** del de “añadir a cesta” para que no se solapen.
- Al pulsar ese botón, abrirlo a **pantalla completa**: con el teclado desplegado apenas se ve
  la información ni lo que se escribe.
- Reducir el espacio entre la **imagen y el titular**.
- La sección **“No compras una pieza…”** deja un espacio blanco a su derecha: no ocupa el 100%
  del ancho.
- **“Completa tu mesa”** y **“Te puede interesar”**: pasar los productos a **scroll lateral**
  para que no ocupen tanto alto.
- Aplicar estos mismos cambios de diseño móvil a **vajillas, juegos, etc.** (ver `T6`).

## Mug con letra

El producto unificado de `A2` necesita en PDP el **selector de variante por letra** que cambia
la foto de producto a la de esa letra (patrón AliExpress / Shein).

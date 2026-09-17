#!/usr/bin/env python3
"""Lote 15 · Los nueve mugs nuevos de `~/Downloads/Mugs/` (2026-09-14).

Hoy en Shopify sólo hay «Mug 202 Rosa», «Mug Negro Vistas» y «Mug con letra». El
cliente manda foto (jpg con fondo + png recortado) de nueve decorados más. Se crean
en BORRADOR, tipo «Mug», con el título en la forma que ya usan las demás piezas para
que las colecciones automáticas por título (flor-de-lis-azul, ceilan, stewart…) los
recojan solos.

Precio: la tarifa 2026 sólo trae una línea de mug («Mug Alfabeto / 202 Rosa / vista
negro», 29,95 €) y los dos mugs existentes van a 29,95. Se aplica ese precio a todos;
CONFIRMAR con el cliente, sobre todo Georgica y Eden (decorados que no están en la
tarifa ni tienen colección).

Deshacer: borrar los nueve productos (van en el informe).

    python3 15_mugs.py            # ensayo
    python3 15_mugs.py --apply
"""

import argparse
import importlib
import os

from shopify_admin import Admin, add_common_args, banner

l13 = importlib.import_module("13_novedades_fotos")

CARPETA = os.path.expanduser("~/Downloads/Mugs")
PRECIO = "29.95"
DESC = "<p>Mug colección %s. Pieza fabricada a mano con loza fina en España.</p><p>Medidas: 12 x 8 x 8,4 cm.</p>"

# fichero (sin extensión) -> (handle, título, nombre del decorado para la descripción)
MUGS = {
    "mug-flor-lis-azul": ("mug-flor-lis-azul", "Mug Flor Lis Azul", "Flor de Lis Azul"),
    "mug-flor-lis-rosa": ("mug-flor-lis-rosa", "Mug Flor Lis Rosa", "Flor de Lis Rosa"),
    "mug-ceilan": ("mug-ceilan", "Mug Ceilan", "Ceilán"),
    "mug-bellavista": ("mug-bellavista", "Mug Bellavista", "Bellavista"),
    "mug-viejo-molino": ("mug-viejo-molino", "Mug Viejo Molino", "Viejo Molino"),
    "mug-negro-vistas-blue-aaron-stewart": ("mug-n-vistas-azul-a-stewart", "Mug N. Vistas Azul A. Stewart",
                                            "Negro Vistas Azul by Aaron Stewart"),
    "mug-negro-vistas-yellow-aaron-stewart": ("mug-n-vistas-amarillo-a-stewart", "Mug N. Vistas Amarillo A. Stewart",
                                              "Negro Vistas Amarillo by Aaron Stewart"),
    "mug-georgica": ("mug-georgica", "Mug Georgica", "Georgica"),
    "mug-eden": ("mug-eden", "Mug Eden", "Eden"),
}

Q = """
query ($q: String!) { products(first: 20, query: $q) { nodes { id handle status } } }
"""


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-15-mugs.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 15 · Mugs nuevos", admin)

    q = " OR ".join("handle:%s" % h for h, _, _ in MUGS.values())
    existe = {p["handle"]: p for p in admin.query(Q, {"q": q})["products"]["nodes"]}
    if existe:
        print("ya existen (se actualizan, ojo: productSet añade fotos): %s" % ", ".join(sorted(existe)))

    for fichero, (handle, titulo, decorado) in MUGS.items():
        fotos = [os.path.join(CARPETA, fichero + ext) for ext in (".jpg", ".png")]
        fotos = [f for f in fotos if os.path.exists(f)]
        # sin etiqueta `novedad`: completan catálogo, no van a la colección Novedades
        cfg = dict(titulo=titulo, tipo="Mug", fotos=fotos, precio=PRECIO, descripcion=DESC % decorado, tags=[])
        l13.sincronizar(admin, handle, cfg, existe.get(handle))

    admin.report(args.report)


if __name__ == "__main__":
    main()

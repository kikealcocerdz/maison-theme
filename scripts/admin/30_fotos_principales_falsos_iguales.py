#!/usr/bin/env python3
"""Lote 30 · Completa el lote 28 donde tomó una foto antigua por la de la carpeta.

El lote 28 reconoce «ya subida» por el nombre del fichero. Con las fotos de catálogo de
agosto (`Sopera_-_Negro_Vistas.png`, `taza-…-n-vistas-azul-a-stewart.jpg`…) el nombre
coincide pero la foto es otra (comprobado a ojo el 2026-09-23). Las subidas del cliente
por este mismo canal empezaron el 2026-09-10: si la primera foto es anterior, se sube la
de la carpeta y se pone primera. No borra nada.

Deshacer: `productDeleteMedia` de las creadas (informe).

    python3 30_fotos_principales_falsos_iguales.py            # ensayo
    python3 30_fotos_principales_falsos_iguales.py --apply
"""

import argparse
import importlib
import os

from shopify_admin import Admin, add_common_args, banner

L28 = importlib.import_module("28_fotos_principales")
subir = importlib.import_module("13_novedades_fotos").subir

DESDE = "2026-09-10"
Q_PRODUCTOS = """
query ($c: String) { products(first: 100, after: $c) {
  pageInfo { hasNextPage endCursor }
  nodes { id handle title media(first: 30) { nodes { id ... on MediaImage { createdAt image { url } } } } } } }
"""


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-30-fotos-falsos-iguales.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 30 · Foto de la carpeta donde la primera es de catálogo antiguo", admin)

    for h, (p, f) in sorted(L28.elegir(admin, Q_PRODUCTOS).items()):
        primera = (p["media"]["nodes"] or [{}])[0]
        if primera.get("createdAt", DESDE) >= DESDE:
            continue
        src = subir(admin, [f])[f] if admin.apply else "file://" + f
        body = admin.mutate("subir foto a «%s» (%s)" % (p["title"], os.path.basename(f)), L28.M_CREATE,
                            {"id": p["id"], "media": [{"originalSource": src, "alt": p["title"],
                                                       "mediaContentType": "IMAGE"}]}, "productCreateMedia")
        if body:
            admin.mutate("primera foto de «%s»" % p["title"], L28.M_REORDER,
                         {"id": p["id"], "moves": [{"id": body["media"][0]["id"], "newPosition": "0"}]},
                         "productReorderMedia")

    admin.report(args.report)


if __name__ == "__main__":
    main()

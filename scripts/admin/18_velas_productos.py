#!/usr/bin/env python3
"""Lote 18 · La vela aromática pasa de 1 producto con 4 aromas a 4 productos.

Título con el decorado al final, como el resto del catálogo, para que caigan solos
en su colección automática (202-rosa, ceilan, eden, negro-vistas). Fotos: las dos de
su subcarpeta y luego las dos generales (WhatsApp) de `Vela aromática/`. Tipo Vela,
etiqueta `novedad`, ACTIVOS y publicados (como estaba el original). Sin precio: la
tarifa no lo trae.

Después se borra `vela-aromatica` (copia entera en el informe) y hay que relanzar
`12_menus_modulo_cliente.py --apply`: el header enlazaba a esa ficha y ahora apunta a
Objetos decorativos filtrado por tipo Vela.

    python3 18_velas_productos.py            # ensayo
    python3 18_velas_productos.py --apply
"""

import argparse
import importlib
import os

from shopify_admin import Admin, add_common_args, banner

l13 = importlib.import_module("13_novedades_fotos")

CARPETA = os.path.join(l13.CARPETA, "Artístico/Vela aromática")
# subcarpeta -> (handle, título)
VELAS = {
    "202 rosa": ("vela-aromatica-202-rosa", "Vela aromática 202 Rosa"),
    "Ceilan": ("vela-aromatica-ceilan", "Vela aromática Ceilan"),
    "eden": ("vela-aromatica-eden", "Vela aromática Edén"),
    "Negro vistas": ("vela-aromatica-negro-vistas", "Vela aromática Negro Vistas"),
}
ORIGINAL = "vela-aromatica"

Q = """
query ($q: String!) { products(first: 20, query: $q) {
  nodes { id handle title status tags productType descriptionHtml
          media(first: 20) { nodes { alt ... on MediaImage { image { url } } } }
          variants(first: 10) { nodes { title price } } } } }
"""

M_DELETE = """
mutation ($input: ProductDeleteInput!) {
  productDelete(input: $input) { deletedProductId userErrors { field message } }
}
"""


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-18-velas.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 18 · vela aromática → 4 productos", admin)

    q = " OR ".join("handle:%s" % h for h in [ORIGINAL] + [h for h, _ in VELAS.values()])
    existe = {p["handle"]: p for p in admin.query(Q, {"q": q})["products"]["nodes"]}
    orig = existe.get(ORIGINAL)
    generales = l13.fotos(CARPETA)

    for sub, (handle, titulo) in VELAS.items():
        cfg = dict(titulo=titulo, tipo="Vela", fotos=l13.fotos(os.path.join(CARPETA, sub)) + generales,
                   estado="ACTIVE")
        l13.sincronizar(admin, handle, cfg, existe.get(handle))

    if orig:
        admin.planned.append(("copia de «Vela aromática» antes de borrarla", orig))
        admin.mutate("borrar «Vela aromática» (%s)" % orig["id"], M_DELETE, {"input": {"id": orig["id"]}}, "productDelete")

    admin.report(args.report)


if __name__ == "__main__":
    main()

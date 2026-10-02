#!/usr/bin/env python3
"""Lote 41 · Libro sin pestaña «Cuidados» (pedido del usuario, 2026-10-02).

La pestaña sale del metafield `custom.cuidados` y, si falta, de un texto fijo del theme
(«Aptas para lavavajillas…»), así que borrar el metafield no basta. Por eso:
  - asigna la plantilla `product.sin-cuidados` (= product.json sin el bloque Cuidados);
  - borra `custom.cuidados` del Libro («Apto para lavavajillas…», dato erróneo).

Sirve igual para otros productos que no son loza (camiseta, bolsa, velas…): basta con
asignarles la misma plantilla.

Deshacer: templateSuffix vacío y volver a escribir el metafield (valor en el informe).

    python3 41_libro_sin_cuidados.py           # ensayo
    python3 41_libro_sin_cuidados.py --apply   # aplica
"""

import argparse

from shopify_admin import Admin, add_common_args, banner

HANDLE = "libro"
SUFIJO = "sin-cuidados"

Q = """{ productByIdentifier(identifier: {handle: "%s"}) { id handle title templateSuffix
  cuidados: metafield(namespace: "custom", key: "cuidados") { type value } } }""" % HANDLE
M_PRODUCT = """
mutation ($p: ProductUpdateInput!) {
  productUpdate(product: $p) { product { handle templateSuffix } userErrors { field message } }
}
"""
M_DEL = """
mutation ($m: [MetafieldIdentifierInput!]!) {
  metafieldsDelete(metafields: $m) { deletedMetafields { key } userErrors { field message } }
}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-41-libro-sin-cuidados.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 41 · Libro sin pestaña Cuidados", admin)

    p = admin.query(Q)["productByIdentifier"]
    admin.done.append(("ANTES", p))
    print("%s · plantilla %r · cuidados %r" % (p["title"], p["templateSuffix"], p["cuidados"] and p["cuidados"]["value"]))

    if p["templateSuffix"] != SUFIJO:
        admin.mutate("plantilla %s" % SUFIJO, M_PRODUCT, {"p": {"id": p["id"], "templateSuffix": SUFIJO}}, "productUpdate")
    if p["cuidados"]:
        admin.mutate("borrar custom.cuidados", M_DEL,
                     {"m": [{"ownerId": p["id"], "namespace": "custom", "key": "cuidados"}]}, "metafieldsDelete")

    if admin.apply:
        admin.done.append(("DESPUÉS", admin.query(Q)["productByIdentifier"]))
    admin.report(args.report)


if __name__ == "__main__":
    main()

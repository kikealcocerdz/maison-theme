#!/usr/bin/env python3
"""Lote 22 · Colección `all` con orden manual.

`/collections/all` es la colección que Shopify genera sola cuando no existe una con
handle `all`: no aparece en el admin y no se puede ordenar. Medio menú apunta ahí
(`/collections/all?filter.p.product_type=…`), así que el cliente no controla el orden.

Al crear una colección con handle `all` Shopify la usa en esa misma URL. Se crea
automática (regla que cumple todo producto: título NO contiene «§§§») para que
no haya que mantener la lista a mano, y con `sortOrder: MANUAL`, que en las
automáticas Shopify sí permite (igual que ya hace «Novedades»). El orden inicial es
el que da Shopify; el cliente lo reordena en Admin → Colecciones → Todos los productos.

    python3 22_coleccion_all.py            # ensayo
    python3 22_coleccion_all.py --apply    # aplica
"""

import argparse

from shopify_admin import Admin, add_common_args, banner, publicar

Q_ALL = '{ collectionByHandle(handle: "all") { id title sortOrder productsCount { count } resourcePublicationsCount { count } } }'
M_CREATE = """
mutation ($input: CollectionInput!) {
  collectionCreate(input: $input) {
    collection { id handle title sortOrder productsCount { count } }
    userErrors { field message }
  }
}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-22-coleccion-all.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 22 · colección all (orden manual)", admin)

    existente = admin.query(Q_ALL)["collectionByHandle"]
    if existente:
        print("Ya existe: %s" % existente)
        gid = existente["id"]
    else:
        body = admin.mutate("crear colección all", M_CREATE, {"input": {
            "title": "Todos los productos",
            "handle": "all",
            "sortOrder": "MANUAL",
            "ruleSet": {"appliedDisjunctively": False, "rules": [
                {"column": "TITLE", "relation": "NOT_CONTAINS", "condition": "§§§"},
            ]},
        }}, "collectionCreate")
        gid = body["collection"]["id"] if body else "gid://shopify/Collection/ENSAYO"

    # Sin canal, Shopify sigue sirviendo en /collections/all la automática de siempre.
    if not existente or existente["resourcePublicationsCount"]["count"] == 0:
        publicar(admin, gid, "colección all")

    if admin.apply:
        print("\nDespués:", admin.query(Q_ALL)["collectionByHandle"])
    admin.report(args.report)


if __name__ == "__main__":
    main()

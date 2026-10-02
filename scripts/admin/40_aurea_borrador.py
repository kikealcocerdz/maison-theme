#!/usr/bin/env python3
"""Lote 40 · Pasa el producto «Áurea» a borrador (pedido del usuario, 2026-10-02).

Está activo a 0,00 € y sin control de stock: cualquiera podría comprarlo gratis. Va con el
lote 39 (colección `aurea` oculta). Se reactiva cuando tenga precio.

Deshacer: productUpdate con status ACTIVE (estado previo en el informe).

    python3 40_aurea_borrador.py           # ensayo
    python3 40_aurea_borrador.py --apply   # aplica
"""

import argparse

from shopify_admin import Admin, add_common_args, banner

Q = """{ products(first: 5, query: "title:Áurea") { nodes {
  id handle title status variants(first: 5) { nodes { sku price } } } } }"""
M = """
mutation ($p: ProductUpdateInput!) {
  productUpdate(product: $p) { product { handle status } userErrors { field message } }
}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-40-aurea-borrador.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 40 · producto Áurea a borrador", admin)

    antes = [p for p in admin.query(Q)["products"]["nodes"] if p["title"] == "Áurea"]
    admin.done.append(("ANTES", antes))
    for p in antes:
        print("%s · %s · precios %s" % (p["handle"], p["status"], [v["price"] for v in p["variants"]["nodes"]]))
        if p["status"] == "ACTIVE":
            admin.mutate("borrador %s" % p["handle"], M, {"p": {"id": p["id"], "status": "DRAFT"}}, "productUpdate")

    if admin.apply:
        admin.done.append(("DESPUÉS", [p for p in admin.query(Q)["products"]["nodes"] if p["title"] == "Áurea"]))
    admin.report(args.report)


if __name__ == "__main__":
    main()

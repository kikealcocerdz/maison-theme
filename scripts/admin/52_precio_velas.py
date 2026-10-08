#!/usr/bin/env python3
"""Lote 52 · Precio de las velas decoradas.

Correo de Mónica («RE: Últimas dudas de producto»): vela blanco 25,95 €, decorado 33,95 €.
Las 4 velas de la web son decoradas (202 Rosa, Ceilán, Edén, Negro Vistas) y estaban a 25,95 €.
Deshacer: el informe guarda los precios anteriores.

    python3 52_precio_velas.py           # ensayo
    python3 52_precio_velas.py --apply   # aplica
"""

import argparse

from shopify_admin import Admin, add_common_args, banner

PRECIO = "33.95"
HANDLES = ["vela-aromatica-202-rosa", "vela-aromatica-ceilan", "vela-aromatica-eden", "vela-aromatica-negro-vistas"]

Q = """query ($h: String!) { productByHandle(handle: $h) { id title variants(first: 5) { nodes { id price } } } }"""
M = """mutation ($p: ID!, $v: [ProductVariantsBulkInput!]!) { productVariantsBulkUpdate(productId: $p, variants: $v) {
  productVariants { id price } userErrors { field message } } }"""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-52-precio-velas.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 52 · Velas decoradas a %s €" % PRECIO, admin)
    for h in HANDLES:
        p = admin.query(Q, {"h": h})["productByHandle"]
        admin.done.append(("antes", p))
        print("%s: %s → %s" % (p["title"], [v["price"] for v in p["variants"]["nodes"]], PRECIO))
        admin.mutate(p["title"], M, {"p": p["id"], "v": [{"id": v["id"], "price": PRECIO} for v in p["variants"]["nodes"]]},
                     "productVariantsBulkUpdate")
    admin.report(args.report)


if __name__ == "__main__":
    main()

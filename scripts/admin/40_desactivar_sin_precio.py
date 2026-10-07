#!/usr/bin/env python3
"""Lote 40 · Pasa a borrador los productos activos sin precio o sin fotos (cliente 2026-10-01).

Excepciones: velas (se quedan por si llegan precios), `envoltorio-de-regalo` (complemento
de la cesta, no lleva foto) y `aurea` (Colección Áurea pendiente de decisión).
Deshacer: productUpdate status ACTIVE de los handles del informe.

    python3 40_desactivar_sin_precio.py            # ensayo
    python3 40_desactivar_sin_precio.py --apply
"""

import argparse

from shopify_admin import Admin, add_common_args, banner

EXCEPTO = {"envoltorio-de-regalo", "aurea"}
Q = '''query($c:String){ products(first:100, after:$c, query:"status:active"){ pageInfo{hasNextPage endCursor}
 nodes{ id handle title productType mediaCount{count} priceRangeV2{ maxVariantPrice{amount} } } } }'''
M = '''mutation($p: ProductUpdateInput!){ productUpdate(product:$p){ product{ handle status } userErrors{ field message } } }'''


def main():
    args = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-40-desactivar-sin-precio.json").parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 40 · Borrador: sin precio o sin fotos", admin)
    c = None
    while True:
        r = admin.query(Q, {"c": c})["products"]
        for p in r["nodes"]:
            falta = float(p["priceRangeV2"]["maxVariantPrice"]["amount"]) == 0 or p["mediaCount"]["count"] == 0
            if falta and p["productType"] != "Vela" and p["handle"] not in EXCEPTO:
                admin.mutate("borrador «%s»" % p["title"], M, {"p": {"id": p["id"], "status": "DRAFT"}}, "productUpdate")
        if not r["pageInfo"]["hasNextPage"]:
            break
        c = r["pageInfo"]["endCursor"]
    admin.report(args.report)


if __name__ == "__main__":
    main()

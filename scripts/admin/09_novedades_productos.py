#!/usr/bin/env python3
"""Lote 9 · Da de alta los seis productos nuevos del cliente como «novedad».

No existen ni en Shopify ni en lacartujadesevilla.com (comprobado el 2026-09-12), así
que se crean en BORRADOR: sin precio ni fotos no deben salir a la venta. Llevan la
etiqueta `novedad` (entran solos en «Novedades», colección automática) y un tipo de
producto que se añade a las reglas de «Decoración» para que también cuelguen de ahí.
Al activar cada uno (precio + foto) aparece en las dos colecciones.

Deshacer: borrar los productos desde el admin; las reglas extra de «Decoración» no
afectan a ningún otro producto.

    python3 09_novedades_productos.py            # ensayo
    python3 09_novedades_productos.py --apply
"""

import argparse

from shopify_admin import Admin, add_common_args, banner

VENDOR = "La Cartuja de Sevilla"
TAG = "novedad"
DECORACION = "decoracion"
# Foto provisional: un asset del tema (público en el CDN). Se sustituye por la real.
PLACEHOLDER = "https://la-cartuja-de-sevilla.myshopify.com/cdn/shop/t/7/assets/craft.webp?v=136599900388307154411788559705"

# (título, handle, tipo). Áurea no tiene tipo claro: va como «Decoración» hasta que
# el cliente diga qué es.
PRODUCTOS = [
    ("Áurea", "aurea", "Decoración"),
    ("Vela aromática", "vela-aromatica", "Vela"),
    ("Lapicero", "lapicero", "Lapicero"),
    ("Caja con 6 posavasos", "caja-6-posavasos", "Posavasos"),
    ("Vaciabolsillos", "vaciabolsillos", "Vaciabolsillo"),
    ("Abanico", "abanico", "Abanico"),
]

Q_ESTADO = """
query ($handles: String!, $col: String!) {
  products(first: 20, query: $handles) { nodes { id handle title status tags } }
  collectionByHandle(handle: $col) {
    id ruleSet { appliedDisjunctively rules { column relation condition } }
  }
}
"""

M_PRODUCT_CREATE = """
mutation ($product: ProductCreateInput!, $media: [CreateMediaInput!]) {
  productCreate(product: $product, media: $media) {
    product { id handle title status tags }
    userErrors { field message }
  }
}
"""

M_COLLECTION_UPDATE = """
mutation ($input: CollectionInput!) {
  collectionUpdate(input: $input) {
    collection { id handle ruleSet { rules { column relation condition } } }
    userErrors { field message }
  }
}
"""


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-09-novedades.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 9 · productos novedad", admin)

    handles = " OR ".join("handle:%s" % h for _, h, _ in PRODUCTOS)
    estado = admin.query(Q_ESTADO, {"handles": handles, "col": DECORACION})
    existentes = {p["handle"]: p for p in estado["products"]["nodes"]}
    col = estado["collectionByHandle"]
    if not col:
        raise SystemExit("no existe la colección `%s`" % DECORACION)

    # ---- 1 · productos ---------------------------------------------------
    for titulo, handle, tipo in PRODUCTOS:
        if handle in existentes:
            p = existentes[handle]
            print("\n· %s ya existe (%s, tags=%s) — no se toca" % (handle, p["status"], p["tags"]))
            continue
        admin.mutate("crear «%s» (borrador, tipo %s)" % (titulo, tipo), M_PRODUCT_CREATE, {
            "product": {
                "title": titulo,
                "handle": handle,
                "vendor": VENDOR,
                "productType": tipo,
                "status": "DRAFT",
                "tags": [TAG],
            },
            "media": [{"originalSource": PLACEHOLDER, "mediaContentType": "IMAGE",
                       "alt": "%s — imagen provisional" % titulo}],
        }, "productCreate")

    # ---- 2 · reglas de «Decoración» --------------------------------------
    reglas = [{"column": r["column"], "relation": r["relation"], "condition": r["condition"]}
              for r in col["ruleSet"]["rules"]]
    tipos_ya = {r["condition"] for r in reglas if r["column"] == "TYPE"}
    nuevas = [t for _, _, t in PRODUCTOS if t not in tipos_ya]
    nuevas = list(dict.fromkeys(nuevas))
    if nuevas:
        reglas += [{"column": "TYPE", "relation": "EQUALS", "condition": t} for t in nuevas]
        admin.mutate("«Decoración»: añadir tipos %s" % ", ".join(nuevas), M_COLLECTION_UPDATE, {
            "input": {"id": col["id"], "ruleSet": {
                "appliedDisjunctively": col["ruleSet"]["appliedDisjunctively"], "rules": reglas}},
        }, "collectionUpdate")
    else:
        print("\n· «Decoración» ya cubre todos los tipos — no se toca")

    admin.report(args.report)
    if admin.apply and not admin.failed:
        print("\nAhora: en el admin, poner precio + foto a cada producto y pasarlo a Activo.")


if __name__ == "__main__":
    main()

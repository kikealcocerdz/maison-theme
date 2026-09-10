#!/usr/bin/env python3
"""Lote 4 · «Mug con letra» en un solo producto con variantes (+ revisión de tazas).

Qué hace:
  1. Lee los 27 productos «Mug Letra X» que hay hoy (A–Z más la Ñ) con su precio,
     su SKU y su foto.
  2. Crea UN producto, `mug-con-letra`, en BORRADOR, con una opción «Letra» y una
     variante por cada uno: mismo precio, mismo SKU y la foto de esa letra como
     imagen de la variante. Así, al elegir la letra, la ficha ya enseña ese mug
     (el theme abre la galería por la foto de la variante).
  3. Con --archivar-originales, archiva los 27 productos sueltos.
  4. Lista las tazas sin platillo para que las revise el cliente. NO archiva
     ninguna: las que hay son «Taza Consomé» y «Taza Desayuno», y el propio menú
     nuevo las mantiene, así que el «Taza sin platillo» del brief tiene que
     señalarlo el cliente por handle:

       python3 04_mug_con_letra.py --apply --archivar-tazas handle-1,handle-2

Sale en borrador a propósito: el cliente quiere una foto generada con IA con todos
los mugs como imagen principal. Cuando la mande, se sube y se publica.

Ojo: archivar un producto deja su URL sin contenido. Las redirecciones necesitan el
permiso `write_url_redirects`, que hoy NO está concedido — hay que crearlas a mano
en Tienda online › Navegación › Redirecciones de URL.

    python3 04_mug_con_letra.py            # ensayo
    python3 04_mug_con_letra.py --apply    # aplica
"""

import argparse

from shopify_admin import Admin, add_common_args, banner

Q_MUGS = """
query {
  products(first: 60, query: "title:*Mug Letra*") {
    nodes {
      id handle title status
      media(first: 1) { nodes { ... on MediaImage { image { url } } } }
      variants(first: 1) { nodes { id price sku } }
    }
  }
}
"""

Q_EXISTE = """
query { productByIdentifier(identifier: {handle: "mug-con-letra"}) { id handle status } }
"""

Q_TAZAS = """
query { products(first: 100, query: "product_type:Taza") { nodes { id handle title } } }
"""

M_PRODUCT_SET = """
mutation ($input: ProductSetInput!) {
  productSet(synchronous: true, input: $input) {
    product { id handle status options { name optionValues { name } } variantsCount { count } }
    userErrors { field message }
  }
}
"""

M_ARCHIVE = """
mutation ($input: ProductInput!) {
  productUpdate(input: $input) {
    product { id handle status }
    userErrors { field message }
  }
}
"""


def letra_de(titulo):
    """«Mug Letra A» → «A». La Ñ viene con el SKU pegado en el handle, no en el título."""
    return titulo.rsplit(" ", 1)[-1].strip().upper()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archivar-originales", action="store_true",
                        help="archiva los «Mug Letra X» sueltos tras crear el unificado")
    parser.add_argument("--archivar-tazas", default="",
                        help="handles de tazas a archivar, separados por comas (vacío = ninguna)")
    add_common_args(parser, "informe-04-mug.json")
    args = parser.parse_args()

    admin = Admin(apply=args.apply)
    banner("Lote 4 · Mug con letra", admin)

    if admin.query(Q_EXISTE)["productByIdentifier"]:
        print("\n⚠ Ya existe /products/mug-con-letra. Bórralo o cámbiale el handle antes de seguir.")
        return

    mugs = admin.query(Q_MUGS)["products"]["nodes"]
    mugs.sort(key=lambda m: m["title"])
    print("\n%d mugs de letra encontrados" % len(mugs))

    valores, variantes, sin_foto = [], [], []
    for m in mugs:
        letra = letra_de(m["title"])
        var = (m["variants"]["nodes"] or [{}])[0]
        media = m["media"]["nodes"]
        url = media[0]["image"]["url"] if media and media[0].get("image") else None
        if not url:
            sin_foto.append(m["handle"])
        valores.append({"name": letra})
        v = {
            "optionValues": [{"optionName": "Letra", "name": letra}],
            "price": var.get("price"),
            "inventoryPolicy": "DENY",
        }
        if var.get("sku"):
            v["inventoryItem"] = {"sku": var["sku"], "tracked": True}
        if url:
            v["file"] = {"originalSource": url, "contentType": "IMAGE"}
        variantes.append(v)
        print("  · %-6s %-8s %s" % (letra, var.get("price", "?"), m["handle"]))

    if sin_foto:
        print("\n⚠ Sin foto (la variante quedará sin imagen): %s" % ", ".join(sin_foto))

    admin.mutate(
        "crear «Mug con letra» con %d variantes (borrador)" % len(variantes),
        M_PRODUCT_SET,
        {"input": {
            "title": "Mug con letra",
            "handle": "mug-con-letra",
            "productType": "Mug",
            "status": "DRAFT",
            "descriptionHtml": "<p>Elige tu inicial. Loza fina de La Cartuja de Sevilla.</p>",
            "productOptions": [{"name": "Letra", "values": valores}],
            "variants": variantes,
        }},
        "productSet",
    )

    if args.archivar_originales:
        for m in mugs:
            admin.mutate("archivar %s" % m["handle"], M_ARCHIVE,
                         {"input": {"id": m["id"], "status": "ARCHIVED"}}, "productUpdate")
    else:
        print("\n· Los 27 originales se quedan como están (usa --archivar-originales para archivarlos).")

    # ---- revisión de tazas ----------------------------------------------
    tazas = admin.query(Q_TAZAS)["products"]["nodes"]
    sin_platillo = [t for t in tazas if "platillo" not in t["title"].lower()]
    print("\n--- tazas cuyo título no dice «con platillo» (%d de %d) ---"
          % (len(sin_platillo), len(tazas)))
    for t in sin_platillo:
        print("  ·", t["handle"], "|", t["title"])
    print("  Son Consomé y Desayuno, y el menú nuevo las mantiene: no se archiva ninguna")
    print("  salvo que pases sus handles en --archivar-tazas.")

    objetivo = {h.strip() for h in args.archivar_tazas.split(",") if h.strip()}
    for t in tazas:
        if t["handle"] in objetivo:
            admin.mutate("archivar %s" % t["handle"], M_ARCHIVE,
                         {"input": {"id": t["id"], "status": "ARCHIVED"}}, "productUpdate")

    admin.report(args.report)


if __name__ == "__main__":
    main()

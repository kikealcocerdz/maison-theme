#!/usr/bin/env python3
"""Lote 1 · Colecciones «Novedades» y «Fin de existencias» + etiqueta de novedad.

Por qué: el theme ya enlaza /collections/novedades y /collections/fin-de-existencias
(lateral del listado y menú hamburguesa). Hoy esas dos colecciones NO existen, así que
esos enlaces dan 404.

Qué hace:
  1. Crea las dos colecciones como AUTOMÁTICAS por etiqueta (`novedad` y
     `fin-de-existencias`). Automáticas = el cliente sólo etiqueta el producto y entra
     solo; no hay lista que mantener.
  2. Etiqueta como `novedad` los seis productos que pidió el cliente.

Ojo (comprobado el 2026-09-10): el catálogo NO tiene ni una etiqueta, y ninguno de los
seis productos existe todavía con ese nombre. El paso 2 informará de los que no
encuentre y no inventará nada. Se puede volver a lanzar cuando estén dados de alta.

Deshacer: borrar las colecciones desde el admin, o quitar la etiqueta del producto.

    python3 01_novedades_fin_existencias.py            # ensayo
    python3 01_novedades_fin_existencias.py --apply    # aplica
"""

import argparse

from shopify_admin import Admin, add_common_args, banner

# Los seis del brief. Cada entrada: (etiqueta legible, término de búsqueda por título).
NOVEDADES = [
    ("Áurea", "Aurea"),
    ("Vela aromática", "Vela"),
    ("Lapicero", "Lapicero"),
    ("Caja con 6 posavasos", "Posavasos"),
    ("Vaciabolsillos", "Vaciabolsillo"),
    ("Abanico", "Abanico"),
]

COLECCIONES = [
    {
        "handle": "novedades",
        "title": "Novedades",
        "tag": "novedad",
        "descriptionHtml": "<p>Las últimas piezas incorporadas al catálogo.</p>",
    },
    {
        "handle": "fin-de-existencias",
        "title": "Fin de existencias",
        "tag": "fin-de-existencias",
        "descriptionHtml": "<p>Últimas unidades de decorados que se retiran.</p>",
    },
]

Q_COLLECTION = """
query ($handle: String!) {
  collectionByHandle(handle: $handle) { id handle title productsCount { count } }
}
"""

M_COLLECTION_CREATE = """
mutation ($input: CollectionInput!) {
  collectionCreate(input: $input) {
    collection { id handle title sortOrder }
    userErrors { field message }
  }
}
"""

Q_PRODUCT_SEARCH = """
query ($q: String!) {
  products(first: 20, query: $q) { nodes { id handle title tags productType } }
}
"""

M_TAGS_ADD = """
mutation ($id: ID!, $tags: [String!]!) {
  tagsAdd(id: $id, tags: $tags) {
    node { ... on Product { id handle tags } }
    userErrors { field message }
  }
}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_args(parser, "informe-01-novedades.json")
    args = parser.parse_args()

    admin = Admin(apply=args.apply)
    banner("Lote 1 · Novedades y Fin de existencias", admin)

    # ---- 1 · colecciones -------------------------------------------------
    for col in COLECCIONES:
        existing = admin.query(Q_COLLECTION, {"handle": col["handle"]})["collectionByHandle"]
        if existing:
            print("\n· %s ya existe (%s productos) — no se toca"
                  % (col["handle"], existing["productsCount"]["count"]))
            continue
        admin.mutate(
            "crear colección automática «%s» (etiqueta: %s)" % (col["title"], col["tag"]),
            M_COLLECTION_CREATE,
            {"input": {
                "title": col["title"],
                "handle": col["handle"],
                "descriptionHtml": col["descriptionHtml"],
                "sortOrder": "CREATED_DESC",
                "ruleSet": {
                    "appliedDisjunctively": False,
                    "rules": [{"column": "TAG", "relation": "EQUALS", "condition": col["tag"]}],
                },
            }},
            "collectionCreate",
        )

    # ---- 2 · etiqueta de novedad ----------------------------------------
    print("\n--- productos a etiquetar como `novedad` ---")
    no_encontrados = []
    for nombre, termino in NOVEDADES:
        found = admin.query(Q_PRODUCT_SEARCH, {"q": "title:*%s*" % termino})["products"]["nodes"]
        if not found:
            no_encontrados.append(nombre)
            print("\n· %s → sin resultados para «%s» (no existe todavía)" % (nombre, termino))
            continue
        if len(found) > 1:
            print("\n· %s → %d coincidencias; se etiquetan todas:" % (nombre, len(found)))
            for p in found:
                print("    - %s | %s" % (p["handle"], p["title"]))
        for p in found:
            if "novedad" in p["tags"]:
                print("  · %s ya lleva la etiqueta" % p["handle"])
                continue
            admin.mutate(
                "etiquetar %s como novedad" % p["handle"],
                M_TAGS_ADD,
                {"id": p["id"], "tags": ["novedad"]},
                "tagsAdd",
            )

    if no_encontrados:
        print("\n⚠ Sin dar de alta en el catálogo: %s" % ", ".join(no_encontrados))
        print("  Vuelve a lanzar este script cuando existan.")

    admin.report(args.report)


if __name__ == "__main__":
    main()

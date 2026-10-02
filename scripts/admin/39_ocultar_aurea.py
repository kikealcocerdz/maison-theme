#!/usr/bin/env python3
"""Lote 39 · Oculta temporalmente la colección Áurea (pedido del usuario, 2026-10-02).

- Despublica `aurea` de todos los canales donde está (Tienda online, Shop, Google & YouTube).
  La colección y su regla siguen existiendo: /collections/aurea pasa a dar 404.
- Quita «Colecciones › Contemporáneas › Áurea» de `main-menu`. El menú se reescribe a partir
  del menú publicado AHORA (no del árbol del lote 12), así que sólo cambia ese enlace.

NO toca el producto «Áurea» (sigue activo y a 0,00 €; ver checklist de lanzamiento).

Deshacer: `publishablePublish` de la colección con los canales del informe, y `menuUpdate`
con «main-menu ANTES» del informe (o volver a añadir el enlace a mano en el admin).

    python3 39_ocultar_aurea.py           # ensayo
    python3 39_ocultar_aurea.py --apply   # aplica
"""

import argparse

from shopify_admin import Admin, add_common_args, banner

HANDLE = "aurea"
MENU = "main-menu"

ITEM = "id title type resourceId url tags"
Q = """{
  collectionByHandle(handle: "%s") { id title
    resourcePublicationsV2(first: 20) { nodes { isPublished publication { id name } } } }
  menus(first: 20) { nodes { id handle title
    items { %s items { %s items { %s } } } } }
}""" % (HANDLE, ITEM, ITEM, ITEM)

M_UNPUBLISH = """
mutation ($id: ID!, $input: [PublicationInput!]!) {
  publishableUnpublish(id: $id, input: $input) {
    publishable { ... on Collection { handle } }
    userErrors { field message }
  }
}
"""
M_MENU = """
mutation ($id: ID!, $title: String!, $handle: String!, $items: [MenuItemUpdateInput!]!) {
  menuUpdate(id: $id, title: $title, handle: $handle, items: $items) {
    menu { handle items { title items { title items { title } } } }
    userErrors { field message }
  }
}
"""


def sin_aurea(items, quitados):
    """Copia del árbol de menú como MenuItemUpdateInput, sin los enlaces a /collections/aurea."""
    out = []
    for it in items:
        if (it.get("url") or "").rstrip("/").endswith("/collections/" + HANDLE):
            quitados.append(it["title"])
            continue
        nodo = {k: it[k] for k in ("id", "title", "type", "resourceId", "url", "tags") if it.get(k) is not None}
        if it.get("items"):
            nodo["items"] = sin_aurea(it["items"], quitados)
        out.append(nodo)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-39-ocultar-aurea.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 39 · ocultar colección Áurea", admin)

    antes = admin.query(Q)
    col = antes["collectionByHandle"]
    menu = next(m for m in antes["menus"]["nodes"] if m["handle"] == MENU)
    admin.done.append(("colección ANTES", col))
    admin.done.append(("main-menu ANTES", menu))

    canales = [n["publication"] for n in col["resourcePublicationsV2"]["nodes"] if n["isPublished"]]
    print("Publicada en:", ", ".join(c["name"] for c in canales) or "ningún canal")
    if canales:
        admin.mutate("despublicar colección %s" % HANDLE, M_UNPUBLISH,
                     {"id": col["id"], "input": [{"publicationId": c["id"]} for c in canales]},
                     "publishableUnpublish")

    quitados = []
    items = sin_aurea(menu["items"], quitados)
    print("Enlaces de menú que se quitan:", quitados or "ninguno")
    if quitados:
        admin.mutate("quitar Áurea de %s" % MENU, M_MENU,
                     {"id": menu["id"], "title": menu["title"], "handle": menu["handle"], "items": items},
                     "menuUpdate")

    if admin.apply:
        admin.done.append(("DESPUÉS", admin.query(Q)))
    admin.report(args.report)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Lote 7 · Quita «Tipo de producto» del menú `colecciones-sidebar`.

El sidebar de la página de colección ya pinta la faceta «Tipo de producto»
(completa y alfabética, la genera Shopify). El grupo del menú apuntaba a
colecciones por tipo, incompletas y sin orden; sobra. Sólo navegación: no toca
colecciones ni productos. El informe guarda el menú anterior para rehacerlo.

    python3 07_sidebar_sin_tipo.py            # ensayo
    python3 07_sidebar_sin_tipo.py --apply
"""

import argparse

from shopify_admin import Admin, add_common_args, banner

HANDLE = "colecciones-sidebar"
QUITAR = "tipo de producto"

ITEM = "id title type url resourceId tags"
Q_MENU = """
query { menus(first: 25) { nodes { id handle title
  items { %s items { %s items { %s } } } } } }
""" % (ITEM, ITEM, ITEM)

M_MENU_UPDATE = """
mutation ($id: ID!, $title: String!, $handle: String!, $items: [MenuItemUpdateInput!]!) {
  menuUpdate(id: $id, title: $title, handle: $handle, items: $items) {
    menu { id handle items { title url items { title url } } }
    userErrors { field message }
  }
}
"""


def limpiar(item):
    """Deja sólo los campos que acepta MenuItemUpdateInput."""
    out = {k: item[k] for k in ("id", "title", "type", "url", "resourceId", "tags") if item.get(k) is not None}
    if item.get("items"):
        out["items"] = [limpiar(i) for i in item["items"]]
    return out


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-07-sidebar.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 7 · sidebar sin «Tipo de producto»", admin)

    menus = {m["handle"]: m for m in admin.query(Q_MENU)["menus"]["nodes"]}
    menu = menus.get(HANDLE)
    if not menu:
        raise SystemExit("no existe el menú `%s`" % HANDLE)

    antes = [i["title"] for i in menu["items"]]
    items = [limpiar(i) for i in menu["items"] if i["title"].strip().lower() != QUITAR]
    print("\nantes :", " · ".join(antes))
    print("después:", " · ".join(i["title"] for i in items))
    if len(items) == len(antes):
        raise SystemExit("no había ningún «Tipo de producto» que quitar")

    admin.done.append(("%s ANTES" % HANDLE, menu))
    admin.mutate("reescribir `%s`" % HANDLE, M_MENU_UPDATE,
                 {"id": menu["id"], "title": menu["title"], "handle": HANDLE, "items": items},
                 "menuUpdate")
    admin.report(args.report)


if __name__ == "__main__":
    main()

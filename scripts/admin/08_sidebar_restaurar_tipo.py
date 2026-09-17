#!/usr/bin/env python3
"""Lote 8 · Devuelve «Tipo de producto» al menú `colecciones-sidebar` y renombra
«Gifts & Decor» → «Decoración».

Deshace el lote 7: el grupo tiene que seguir en el árbol, porque el tema
(`snippets/collection-nav`) lo pinta con la faceta de tipo de producto de Shopify
en vez de con sus hijos. Los hijos se restauran tal cual (fallback sin JS y para
poder rehacer el menú); el tema los ignora.

    python3 08_sidebar_restaurar_tipo.py            # ensayo
    python3 08_sidebar_restaurar_tipo.py --apply
"""

import argparse
import json

from shopify_admin import Admin, add_common_args, banner

HANDLE = "colecciones-sidebar"
ORIGEN = "informe-07-sidebar.json"

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


def limpiar(item, con_id=True):
    keys = ("title", "type", "url", "resourceId", "tags") + (("id",) if con_id else ())
    out = {k: item[k] for k in keys if item.get(k) is not None}
    if item.get("items"):
        out["items"] = [limpiar(i, con_id) for i in item["items"]]
    return out


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-08-sidebar.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 8 · restaurar «Tipo de producto» en el sidebar", admin)

    with open(ORIGEN) as fh:
        informe = json.load(fh)
    antes = next(p["resultado"] for p in informe["ejecutado"] if p["paso"].endswith("ANTES"))
    grupo = next(i for i in antes["items"] if i["title"].strip().lower() == "tipo de producto")

    menu = next(m for m in admin.query(Q_MENU)["menus"]["nodes"] if m["handle"] == HANDLE)
    items = [limpiar(i) for i in menu["items"]]
    # Los ids antiguos del grupo ya no existen: se recrea sin id (items nuevos).
    if not any(i["title"].strip().lower() == "tipo de producto" for i in items):
        items.append(limpiar(grupo, con_id=False))
    for i in items:
        if i["title"].strip().lower() == "gifts & decor":
            i["title"] = "Decoración"
    print("\ndespués:", " · ".join(i["title"] for i in items))

    admin.done.append(("%s ANTES" % HANDLE, menu))
    admin.mutate("reescribir `%s`" % HANDLE, M_MENU_UPDATE,
                 {"id": menu["id"], "title": menu["title"], "handle": HANDLE, "items": items},
                 "menuUpdate")
    admin.report(args.report)


if __name__ == "__main__":
    main()

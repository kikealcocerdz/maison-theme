#!/usr/bin/env python3
"""Lote 42 · Orden de «Tipo de producto» en `colecciones-sidebar`.

Desde 2026-10-02 el árbol de la barra lateral pinta los enlaces del menú (antes el tema
los sustituía por la faceta de tipo). Se ordenan por familia: mesa, servir, café/té,
juegos, decoración. Solo reordena; no añade ni quita enlaces.

    python3 42_sidebar_tipo_orden.py            # ensayo
    python3 42_sidebar_tipo_orden.py --apply
"""
import argparse

from shopify_admin import Admin, add_common_args, banner

ORDEN = ["Vajillas", "Platos", "Boles y cuencos", "Tazas", "Fuentes", "Bandejas", "Jarras y teteras",
         "Juegos de café", "Juegos de té", "Juegos de boles", "Mugs", "Objetos decorativos"]
Q = '''{ menus(first:20){ nodes{ id handle title items{ id title type url resourceId tags
  items{ id title type url resourceId tags items{ id title type url resourceId tags } } } } } }'''
M = '''mutation($id: ID!, $title: String!, $handle: String!, $items: [MenuItemUpdateInput!]!){
  menuUpdate(id:$id, title:$title, handle:$handle, items:$items){ menu{ handle } userErrors{ field message } } }'''


def limpio(it):
    n = {"id": it["id"], "title": it["title"], "type": it["type"], "tags": it["tags"],
         "items": [limpio(c) for c in it.get("items") or []]}
    if it.get("resourceId"):
        n["resourceId"] = it["resourceId"]
    else:
        n["url"] = it["url"]
    return n


def main():
    args = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-42-sidebar-tipo-orden.json").parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 42 · Orden de Tipo de producto en la barra lateral", admin)
    menu = next(m for m in admin.query(Q)["menus"]["nodes"] if m["handle"] == "colecciones-sidebar")
    admin.done.append(("ANTES", menu))
    items = [limpio(i) for i in menu["items"]]
    tipo = next(i for i in items if i["title"] == "Tipo de producto")
    assert sorted(c["title"] for c in tipo["items"]) == sorted(ORDEN), [c["title"] for c in tipo["items"]]
    tipo["items"].sort(key=lambda c: ORDEN.index(c["title"]))
    admin.mutate("reordenar Tipo de producto", M, {"id": menu["id"], "title": menu["title"],
                                                   "handle": menu["handle"], "items": items}, "menuUpdate")
    admin.report(args.report)


if __name__ == "__main__":
    main()

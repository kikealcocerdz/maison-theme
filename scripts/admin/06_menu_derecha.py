#!/usr/bin/env python3
"""Lote 6 · Crea (o reescribe) `menu-derecha`: Nuevo · Viste tu mesa · Ambientes · Legado.

Solo toca ese menú; `main-menu` no se mira siquiera. Después de aplicarlo hay que
elegirlo en Personalizar → Cabecera → «Menú de la derecha».

Los seis hijos de «Nuevo» (Áurea, Vela aromática, Lapicero, Caja 6 posavasos,
Vaciabolsillos, Abanico) no existen todavía como producto. Van igualmente, como
en el menú principal: si el producto existe, enlace directo; si no, una búsqueda
por su nombre, que devolverá la pieza en cuanto se dé de alta.

    python3 06_menu_derecha.py            # ensayo
    python3 06_menu_derecha.py --apply
"""

import argparse
import urllib.parse

from shopify_admin import Admin, add_common_args, banner

HANDLE = "menu-derecha"
TITULO = "Menú derecha"

# (rótulo, término de búsqueda). Si hay un producto cuyo título lo contiene, se
# enlaza directo; si no, la entrada apunta a /search con ese término.
HIJOS_NUEVO = [
    ("Áurea", "Aurea"),
    ("Vela aromática", "Vela aromatica"),
    ("Lapicero", "Lapicero"),
    ("Caja con 6 posavasos", "Posavasos"),
    ("Vaciabolsillo", "Vaciabolsillo"),
    ("Abanico", "Abanico"),
]

Q_DATOS = """
query {
  novedades: collectionByHandle(handle: "novedades") { id }
  pages(first: 50) { nodes { id handle } }
  products(first: 250, query: "tag:novedad OR title:*Aurea* OR title:*Vela* OR title:*Lapicero* OR title:*Posavasos* OR title:*Vaciabolsillo* OR title:*Abanico*") { nodes { id handle title } }
  menus(first: 25) { nodes { id handle title items { title type url items { title type url } } } }
}
"""

M_MENU_CREATE = """
mutation ($title: String!, $handle: String!, $items: [MenuItemCreateInput!]!) {
  menuCreate(title: $title, handle: $handle, items: $items) {
    menu { id handle items { title url items { title url } } }
    userErrors { field message }
  }
}
"""

M_MENU_UPDATE = """
mutation ($id: ID!, $title: String!, $handle: String!, $items: [MenuItemUpdateInput!]!) {
  menuUpdate(id: $id, title: $title, handle: $handle, items: $items) {
    menu { id handle items { title url items { title url } } }
    userErrors { field message }
  }
}
"""


def pagina(titulo, handle, pages, faltan):
    if handle not in pages:
        faltan.append((titulo, "página /%s" % handle))
        return None
    return {"title": titulo, "type": "PAGE", "resourceId": pages[handle]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_args(parser, "informe-06-menu-derecha.json")
    args = parser.parse_args()

    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 6 · menu-derecha", admin)

    datos = admin.query(Q_DATOS)
    pages = {n["handle"]: n["id"] for n in datos["pages"]["nodes"]}
    productos = {n["handle"]: n for n in datos["products"]["nodes"]}
    menus = {n["handle"]: n for n in datos["menus"]["nodes"]}
    faltan = []

    # ---- Nuevo ----------------------------------------------------------
    if datos["novedades"]:
        nuevo = {"title": "Nuevo", "type": "COLLECTION", "resourceId": datos["novedades"]["id"]}
    else:
        nuevo = {"title": "Nuevo", "type": "HTTP", "url": "/collections/novedades"}
        faltan.append(("Nuevo", "colección /novedades (lanza antes el lote 01)"))
    hijos = []
    for rotulo, termino in HIJOS_NUEVO:
        directo = [p for p in productos.values() if termino.lower() in p["title"].lower()]
        if directo:
            hijos.append({"title": rotulo, "type": "PRODUCT", "resourceId": directo[0]["id"]})
        else:
            url = "/search?q=%s&type=product" % urllib.parse.quote(termino)
            hijos.append({"title": rotulo, "type": "HTTP", "url": url})
            faltan.append(("Nuevo › " + rotulo, "sin producto aún → %s" % url))
    nuevo["items"] = hijos

    # ---- resto ----------------------------------------------------------
    items = [nuevo]
    for titulo, handle in (("Viste tu mesa", "viste-tu-mesa"), ("Ambientes", "nuestras-mesas")):
        it = pagina(titulo, handle, pages, faltan)
        if it:
            items.append(it)

    legado = pagina("Legado", "heritage-1841", pages, faltan)
    if legado:
        sub = []
        for titulo, handle in (("Heritage 1842", "heritage-1841"), ("Artesanía", "artesania"), ("Sellos", "identifica-tu-sello")):
            it = pagina(titulo, handle, pages, faltan)
            if it:
                sub.append(it)
        if sub:
            legado["items"] = sub
        items.append(legado)

    print("\n--- árbol ---")
    for it in items:
        print("  ·", it["title"])
        for sub in it.get("items", []):
            print("      ·", sub["title"])
    if faltan:
        print("\n--- sin destino (%d) ---" % len(faltan))
        for camino, motivo in faltan:
            print("  · %-22s %s" % (camino, motivo))

    if HANDLE in menus:
        admin.done.append(("menu-derecha ANTES", menus[HANDLE]))
        admin.mutate("reescribir `%s`" % HANDLE, M_MENU_UPDATE,
                     {"id": menus[HANDLE]["id"], "title": TITULO, "handle": HANDLE, "items": items},
                     "menuUpdate")
    else:
        admin.mutate("crear `%s`" % HANDLE, M_MENU_CREATE,
                     {"title": TITULO, "handle": HANDLE, "items": items},
                     "menuCreate")

    admin.report(args.report)
    if admin.apply and not admin.failed:
        print("\nAhora: Personalizar → Cabecera → «Menú de la derecha» → %s" % TITULO)


if __name__ == "__main__":
    main()

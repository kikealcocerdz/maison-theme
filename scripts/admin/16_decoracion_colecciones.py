#!/usr/bin/env python3
"""Lote 16 · Decoración con la misma estructura que el header (2026-09-14).

El header (lote 12) parte Decoración en cuatro columnas —Arte y colección · Objetos
decorativos · Baño · Gifts— pero no había colecciones detrás (enlaces a /search) y el
sidebar de las páginas de colección seguía con «Piezas decorativas · Mugs · Emblemas».

  1. Cuatro colecciones automáticas (reglas OR por tipo de producto, y por título para
     las bandejas Vistas / conmemorativa, que comparten tipo con las bandejas de pastas).
  2. La colección paraguas `decoracion` pasa a ser la unión de las cuatro (antes le
     faltaban los tipos nuevos: Tarro, Mancerina, Cepillero, Libro…).
  3. El grupo «Decoración» del menú `colecciones-sidebar` queda con esas cuatro entradas
     (fuera Mugs —está en Tipo de producto— y Emblemas —oculta—).

Después hay que relanzar `12_menus_modulo_cliente.py --apply` para que el header apunte
a las colecciones nuevas (ya editado allí).

Deshacer: borrar las cuatro colecciones (van en el informe), restaurar las reglas de
`decoracion` y el sidebar desde los «ANTES» del informe.

    python3 16_decoracion_colecciones.py            # ensayo
    python3 16_decoracion_colecciones.py --apply
"""

import argparse

from shopify_admin import Admin, add_common_args, banner

SIDEBAR = "colecciones-sidebar"


def tipo(*valores):
    return [{"column": "TYPE", "relation": "EQUALS", "condition": v} for v in valores]


def titulo(*valores):
    return [{"column": "TITLE", "relation": "CONTAINS", "condition": v} for v in valores]


# handle -> (título, reglas). Mismo reparto que el header.
GRUPOS = {
    "arte-y-coleccion": ("Arte y colección",
                         tipo("Palangana", "Jarro", "Cabeza", "Florero", "Tarro", "Mancerina", "Posavasos",
                              "Decoración", "Bombonera", "Champanera") + titulo("Juego Cartuja")),
    "objetos-decorativos": ("Objetos decorativos",
                            tipo("Vela", "Lapicero", "Vaciabolsillo") + titulo("Bandeja Vistas", "Bandeja conmemorativa")),
    "bano": ("Baño", tipo("Cepillero", "Jabonera", "Algodonera", "Conjunto de baño", "Palangana", "Jarro")),
    "gifts": ("Gifts", tipo("Libro", "Camiseta", "Bolsa")),
}

Q = """
query { collections(first: 250) { nodes { id handle title ruleSet { appliedDisjunctively rules { column relation condition } } } }
  menus(first: 25) { nodes { id handle title items { id title type url resourceId items { id title type url resourceId } } } } }
"""

M_CREATE = """
mutation ($input: CollectionInput!) {
  collectionCreate(input: $input) { collection { id handle title } userErrors { field message } }
}
"""

M_UPDATE = """
mutation ($input: CollectionInput!) {
  collectionUpdate(input: $input) { collection { id handle ruleSet { rules { column condition } } } userErrors { field message } }
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


def limpiar(item):
    out = {k: item[k] for k in ("id", "title", "type", "url", "resourceId") if item.get(k) is not None}
    if item.get("items"):
        out["items"] = [limpiar(i) for i in item["items"]]
    return out


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-16-decoracion-colecciones.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 16 · Decoración: colecciones + sidebar", admin)

    datos = admin.query(Q)
    cols = {c["handle"]: c for c in datos["collections"]["nodes"]}
    menu = next(m for m in datos["menus"]["nodes"] if m["handle"] == SIDEBAR)

    # 1. las cuatro colecciones
    ids = {}
    for handle, (nombre, reglas) in GRUPOS.items():
        if handle in cols:
            print("  · %s ya existe, se actualizan sus reglas" % handle)
            ids[handle] = cols[handle]["id"]
            admin.done.append(("%s ANTES" % handle, cols[handle]))
            admin.mutate("reglas de «%s»" % nombre, M_UPDATE, {"input": {
                "id": cols[handle]["id"], "ruleSet": {"appliedDisjunctively": True, "rules": reglas}}}, "collectionUpdate")
            continue
        res = admin.mutate("crear «%s» (%d reglas)" % (nombre, len(reglas)), M_CREATE, {"input": {
            "title": nombre, "handle": handle, "ruleSet": {"appliedDisjunctively": True, "rules": reglas}}}, "collectionCreate")
        if res:
            ids[handle] = res["collection"]["id"]

    # 2. paraguas = unión (sin duplicar)
    union, vistas = [], set()
    for _, reglas in GRUPOS.values():
        for r in reglas:
            k = (r["column"], r["condition"])
            if k not in vistas:
                vistas.add(k)
                union.append(r)
    deco = cols["decoracion"]
    admin.done.append(("decoracion ANTES", deco))
    admin.mutate("reglas de «Decoración» (%d)" % len(union), M_UPDATE, {"input": {
        "id": deco["id"], "ruleSet": {"appliedDisjunctively": True, "rules": union}}}, "collectionUpdate")

    # 3. sidebar
    items = [limpiar(i) for i in menu["items"]]
    grupo = next(i for i in items if i["title"].strip().lower() == "decoración")
    admin.done.append(("%s ANTES" % SIDEBAR, menu))
    grupo["items"] = []
    for handle, (nombre, _) in GRUPOS.items():
        if handle in ids:
            grupo["items"].append({"title": nombre, "type": "COLLECTION", "resourceId": ids[handle]})
        else:  # ensayo: la colección aún no existe
            grupo["items"].append({"title": nombre, "type": "HTTP", "url": "/collections/%s" % handle})
    print("\nsidebar › Decoración:", " · ".join(i["title"] for i in grupo["items"]))
    admin.mutate("reescribir `%s`" % SIDEBAR, M_MENU_UPDATE,
                 {"id": menu["id"], "title": menu["title"], "handle": SIDEBAR, "items": items}, "menuUpdate")

    admin.report(args.report)


if __name__ == "__main__":
    main()

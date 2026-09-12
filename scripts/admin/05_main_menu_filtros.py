#!/usr/bin/env python3
"""Lote 5 · Escribe `main-menu` con el árbol del brief, apuntando a filtros.

Esquema de destinos, por orden de preferencia:

  1. Colección que ya existe        →  /collections/<handle>          (decorados)
  2. Tipo de producto del catálogo  →  /collections/all?filter.p.product_type=<Tipo>
  3. Subfamilia que solo vive en el título (Plato Llano, Bol Grande, Taza Desayuno…)
                                    →  /search?q=<términos>&type=product
  4. Nada de lo anterior            →  la entrada NO se pinta y sale en el informe

No crea ni toca colecciones ni productos: solo navegación. `menuUpdate` sustituye el
menú entero, y el informe guarda el anterior completo para poder rehacerlo.

    python3 05_main_menu_filtros.py            # ensayo: imprime el árbol resuelto
    python3 05_main_menu_filtros.py --apply
"""

import argparse
import urllib.parse

from shopify_admin import Admin, add_common_args, banner

COL, TIPO, BUSQ = "col", "tipo", "busq"

# (rótulo, destino, hijos). Destino: (COL, handle) | (TIPO, "Tipo") | (BUSQ, "términos") | None
ARBOL = [
    ("Mesa", (TIPO, "Vajilla"), [
        ("Vajilla", (TIPO, "Vajilla"), []),
        ("Plato", (TIPO, "Plato"), [
            ("Bajo plato", (TIPO, "Bajoplato"), []),
            ("Plato llano", (BUSQ, "Plato Llano"), []),
            ("Plato hondo", (BUSQ, "Plato Hondo"), []),
            ("Plato postre", (BUSQ, "Plato Postre"), []),
            ("Plato pan", (BUSQ, "Plato Pan"), []),
            ("Platillo de consomé", (BUSQ, "Platillo Consome"), []),
        ]),
        ("Bol y Taza de consomé", (TIPO, "Bol"), [
            ("Bol grande", (BUSQ, "Bol Grande"), []),
            ("Bol pequeño", (BUSQ, "Bol Pequeño"), []),
            ("Bol mini", (BUSQ, "Bol Mini"), []),
            ("Taza de consomé", (BUSQ, "Taza Consome"), []),
            ("Taza de consomé con platillo", (BUSQ, "Taza Consome Con Platillo"), []),
        ]),
        ("Fuente y Ensaladera", (TIPO, "Fuente"), [
            ("Fuentes", (TIPO, "Fuente"), []),
            ("Ensaladeras", (TIPO, "Ensaladera"), []),
        ]),
        ("Sopera", (TIPO, "Sopera"), []),
        ("Salsera", (TIPO, "Salsera"), []),
        ("Cubitera", None, []),
    ]),

    ("Café & Té", (TIPO, "Taza"), [
        ("Juego de café", (BUSQ, "Juego Cafe"), []),
        ("Juego de té", (BUSQ, "Juego Te"), []),
        ("Mug", (TIPO, "Mug"), []),
        ("Taza de café con platillo", (BUSQ, "Taza Cafe Con Platillo"), []),
        ("Taza de té con platillo", (BUSQ, "Taza Te Con Platillo"), []),
        ("Taza de desayuno con platillo", (BUSQ, "Taza Desayuno Con Platillo"), []),
        ("Taza de desayuno", (BUSQ, "Taza Desayuno"), []),
        ("Azucarero", (TIPO, "Azucarero"), []),
        ("Bandeja de pastas", (BUSQ, "Bandeja Pastas"), []),
        ("Bombonera", (TIPO, "Bombonera"), []),
        ("Cafetera", (TIPO, "Cafetera"), []),
        ("Lechera", (TIPO, "Lechera"), []),
        ("Tetera", (TIPO, "Tetera"), []),
        ("Platos", (TIPO, "Platillo"), [
            ("Plato de pastas", (BUSQ, "Plato Pastas"), []),
            ("Platillo de desayuno", (BUSQ, "Platillo Desayuno"), []),
        ]),
    ]),

    ("Decoración", (COL, "decoracion"), [
        ("Artístico", (COL, "decoracion"), [
            ("Aguamanil", (TIPO, "Palangana"), []),
            ("Cabeza frenológica", (TIPO, "Cabeza"), []),
            ("Floreros – Tibores – Jarrones", (TIPO, "Florero"), []),
            ("Tarros de botica", None, []),
            ("Mancerina", None, []),
            ("Caja 6 posavasos", None, []),
            ("Hoja de parra", None, []),
            ("Vela aromática", None, []),
            ("Lapicero", None, []),
            ("Bandeja y vaciabolsillos", (TIPO, "Bandeja"), []),
            ("Bandeja Vistas", (BUSQ, "Bandeja Vistas"), []),
            ("Bandeja Conmemorativa", None, []),
            ("Vaciabolsillo", None, []),
        ]),
        ("Baño", None, [
            ("Conjunto de baño", None, []),
            ("Cepillero", None, []),
            ("Jabonera", None, []),
            ("Algodonera", None, []),
            # El aguamanil del brief se repite en Baño; ya está en Artístico y ese
            # grupo no tiene destino propio, así que duplicarlo no aporta.
        ]),
        ("Gifts", None, [
            ("Libro", None, []),
            ("Camiseta", None, []),
            ("Bolsa", None, []),
        ]),
    ]),

    ("Colecciones", (COL, None), [   # (COL, None) = /collections
        ("Clásicas", (COL, None), [
            ("202 Rosa", (COL, "202-rosa"), []),
            ("Negro Vistas", (COL, "negro-vistas"), []),
            ("Ceilán", (COL, "ceilan"), []),
            ("Flor de Lis Azul", (COL, "flor-de-lis-azul"), []),
            ("Flor de Lis Rosa", (COL, "flor-de-lis-rosa"), []),
            ("Viejo Molino", (COL, "viejo-molino"), []),
            ("Bellavista", (COL, "bellavista"), []),
            ("Aurora Blanco", (COL, "aurora-blanca"), []),
            ("Ochavado Blanco", (COL, "ochavada-blanca"), []),
        ]),
        ("Contemporáneas", (COL, None), [
            ("Áurea", (COL, "aurea"), []),
            ("Aaron Stewart", (COL, "vistas-stewart"), []),
            ("Oaxaca", (COL, "oaxaca"), []),
            ("Georgica", (COL, "georgica"), []),
            ("Edén", (COL, "eden"), []),
        ]),
        ("Fin de existencias", (COL, "fin-de-existencias"), [
            ("Escenas", (COL, "escenas"), []),
            ("Infanta Luisa", (COL, "infanta-luisa"), []),
            ("María Cristina", (COL, "maria-cristina"), []),
            ("Paraíso azul", (COL, "paraiso-azul"), []),
            ("Kensington", (COL, "kensington"), []),
            ("Azahar", (COL, "azahar"), []),
            ("Azahar New", (COL, "azahar-new"), []),
            ("Yedra", (COL, "yedra"), []),
            ("Basic Line Blue", (COL, "basic-line-blue"), []),
            ("Basic Line Red", (COL, "basic-line-red"), []),
            ("Laberinto", (COL, "laberinto"), []),
            ("Peces", (COL, "peces"), []),
        ]),
    ]),
]

Q_DATOS = """
query {
  collections(first: 250) { nodes { id handle } }
  productTypes(first: 250) { edges { node } }
  menus(first: 25) { nodes { id handle title items { title type url items { title type url items { title type url } } } } }
}
"""

M_MENU_UPDATE = """
mutation ($id: ID!, $title: String!, $handle: String!, $items: [MenuItemUpdateInput!]!) {
  menuUpdate(id: $id, title: $title, handle: $handle, items: $items) {
    menu { id handle items { title url items { title url items { title url } } } }
    userErrors { field message }
  }
}
"""


def resolver(destino, cols, tipos):
    """Devuelve (item_de_shopify, etiqueta_del_destino) o (None, motivo)."""
    if destino is None:
        return None, "sin destino"
    clase, valor = destino
    if clase == COL and valor is None:
        return {"type": "HTTP", "url": "/collections"}, "/collections"
    if clase == COL:
        if valor in cols:
            return {"type": "COLLECTION", "resourceId": cols[valor]}, "/collections/%s" % valor
        return None, "no existe la colección /%s" % valor
    if clase == TIPO:
        if valor not in tipos:
            return None, "no existe el tipo «%s»" % valor
        url = "/collections/all?filter.p.product_type=%s" % urllib.parse.quote(valor)
        return {"type": "HTTP", "url": url}, url
    if clase == BUSQ:
        url = "/search?q=%s&type=product" % urllib.parse.quote(valor)
        return {"type": "HTTP", "url": url}, url
    return None, "destino desconocido"


def construir(nodos, cols, tipos, fuera, ruta="", nivel=0, log=None):
    items = []
    for titulo, destino, hijos in nodos:
        camino = (ruta + " › " + titulo).strip(" ›")
        item, etiqueta = resolver(destino, cols, tipos)
        subitems = construir(hijos, cols, tipos, fuera, camino, nivel + 1, log) if hijos else []

        if item is None:
            if subitems:
                # Un agrupador sin destino propio (Baño, Gifts) no puede existir en
                # Shopify: sus hijos suben un nivel antes que perderlos.
                log.append("%s%s → agrupador sin destino, sus hijos suben un nivel" % ("  " * nivel, titulo))
                items.extend(subitems)
            else:
                fuera.append((camino, etiqueta))
            continue

        item["title"] = titulo
        if subitems:
            item["items"] = subitems
        items.append(item)
        log.append("%s%-34s %s" % ("  " * nivel, titulo, etiqueta))
    return items


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_args(parser, "informe-05-main-menu.json")
    args = parser.parse_args()

    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 5 · main-menu con filtros", admin)

    datos = admin.query(Q_DATOS)
    cols = {n["handle"]: n["id"] for n in datos["collections"]["nodes"]}
    tipos = {e["node"] for e in datos["productTypes"]["edges"]}
    menus = {n["handle"]: n for n in datos["menus"]["nodes"]}

    fuera, log = [], []
    items = construir(ARBOL, cols, tipos, fuera, log=log)

    print("\n--- árbol resuelto ---")
    for line in log:
        print("  " + line)

    if fuera:
        print("\n--- fuera del menú (%d), sin nada detrás ---" % len(fuera))
        for camino, motivo in fuera:
            print("  · %-44s %s" % (camino, motivo))

    if "main-menu" not in menus:
        print("\n✗ No hay `main-menu` en la tienda.")
        return

    admin.done.append(("main-menu ANTES", menus["main-menu"]))
    admin.mutate(
        "reescribir `main-menu` (%d entradas de primer nivel)" % len(items),
        M_MENU_UPDATE,
        {"id": menus["main-menu"]["id"], "title": "Main menu", "handle": "main-menu", "items": items},
        "menuUpdate",
    )
    admin.report(args.report)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Lote 3 · El menú nuevo del brief (izquierda y derecha del logo).

Qué hace:
  - Reescribe `main-menu` con el árbol de la izquierda: Mesa · Café & Té ·
    Decoración · Colecciones (con sus submenús).
  - Crea (o reescribe) `menu-derecha` con: Nuevo · Viste tu mesa · Ambientes ·
    Legado.

Cómo trata lo que falta: cada entrada apunta a una colección o a una página por
handle. Si el destino no existe, la entrada SE SALTA y aparece al final en la lista
«sin destino», que es la que hay que llevarle al cliente para que diga qué producto
va en cada una. El script no inventa colecciones (para eso está el lote 2).

Aviso: `menuUpdate` sustituye el menú entero. El informe guarda el menú anterior
completo, así que se puede reconstruir tal cual si hace falta.

Después de aplicarlo hay que apuntar el theme a estos menús (ajustes de las
secciones Header y Mega menu); mientras no se haga, el theme sigue con su árbol de
demostración.

    python3 03_menu_nuevo.py            # ensayo
    python3 03_menu_nuevo.py --apply    # aplica
"""

import argparse

from shopify_admin import Admin, add_common_args, banner

C, P, U = "collection", "page", "url"

# (título, destino, hijos). Destino: (C, handle) | (P, handle) | (U, ruta) | None
IZQUIERDA = [
    ("Mesa", (U, "/collections"), [
        ("Vajilla", (C, "vajillas-completas"), []),
        ("Plato", (C, "plato"), [
            ("Bajo plato", (C, "bajoplato"), []),
            ("Plato llano", (C, "plato-llano"), []),
            ("Plato hondo", (C, "plato-hondo"), []),
            ("Plato postre", (C, "plato-postre"), []),
            ("Plato pan", (C, "plato-pan"), []),
            ("Platillo de consomé", (C, "platillo-consome"), []),
        ]),
        ("Bol y Taza de consomé", (C, "bol"), [
            ("Bol grande", (C, "bol-grande"), []),
            ("Bol pequeño", (C, "bol-pequeno"), []),
            ("Bol mini", (C, "bol-mini"), []),
            ("Taza de consomé", (C, "taza-consome"), []),
            ("Taza de consomé con platillo", (C, "taza-consome-con-platillo"), []),
        ]),
        ("Fuente y Ensaladera", (C, "fuente"), [
            ("Fuentes", (C, "fuente"), []),
            ("Ensaladeras", (C, "ensaladera"), []),
        ]),
        ("Sopera", (C, "sopera"), []),
        ("Salsera", (C, "salsera"), []),
        ("Cubitera", (C, "cubitera"), []),
    ]),
    ("Café & Té", (U, "/collections"), [
        ("Juego de Café", (C, "juegos-cafe"), []),
        ("Juego de Té", (C, "juegos-te"), []),
        ("Mug", (C, "mugs"), []),
        ("Taza de café con platillo", (C, "taza-cafe-con-platillo"), []),
        ("Taza de té con platillo", (C, "taza-te-con-platillo"), []),
        ("Taza de desayuno con platillo", (C, "taza-desayuno-con-platillo"), []),
        ("Taza de desayuno", (C, "taza-desayuno"), []),
        ("Azucarero", (C, "azucarero"), []),
        ("Bandeja de pastas", (C, "bandeja-pastas"), []),
        ("Bombonera", (C, "bombonera"), []),
        ("Cafetera", (C, "cafetera"), []),
        ("Lechera", (C, "lechera"), []),
        ("Tetera", (C, "tetera"), []),
        ("Plato de pastas", (C, "plato-pastas"), []),
        ("Platillo de desayuno", (C, "platillo-desayuno"), []),
    ]),
    ("Decoración", (C, "decoracion"), [
        ("Artístico", (C, "decoracion-artistico"), [
            ("Aguamanil", (C, "palangana"), []),
            ("Cabeza frenológica", (C, "cabeza"), []),
            ("Floreros – Tibores – Jarrones", (C, "florero"), []),
            ("Tarros de botica", (C, "tarros-botica"), []),
            ("Mancerina", (C, "mancerina"), []),
            ("Caja 6 posavasos", (C, "posavasos"), []),
            ("Hoja de parra", (C, "hoja-de-parra"), []),
            ("Vela aromática", (C, "vela-aromatica"), []),
            ("Lapicero", (C, "lapicero"), []),
            ("Bandeja y vaciabolsillos", (C, "bandeja"), []),
            ("Bandeja Vistas", (C, "bandeja-vistas"), []),
            ("Bandeja Conmemorativa", (C, "bandeja-conmemorativa"), []),
            ("Vaciabolsillo", (C, "vaciabolsillo"), []),
        ]),
        ("Baño", (C, "bano"), [
            ("Conjunto de baño", (C, "conjunto-bano"), []),
            ("Cepillero", (C, "cepillero"), []),
            ("Jabonera", (C, "jabonera"), []),
            ("Algodonera", (C, "algodonera"), []),
            ("Aguamanil", (C, "palangana"), []),
        ]),
        ("Gifts", (C, "gifts"), [
            ("Libro", (C, "libro"), []),
            ("Camiseta", (C, "camiseta"), []),
            ("Bolsa", (C, "bolsa"), []),
        ]),
    ]),
    ("Colecciones", (U, "/collections"), [
        ("Clásicas", (U, "/collections"), [
            ("202 Rosa", (C, "202-rosa"), []),
            ("Negro Vistas", (C, "negro-vistas"), []),
            ("Ceilán", (C, "ceilan"), []),
            ("Flor de Lis Azul", (C, "flor-de-lis-azul"), []),
            ("Flor de Lis Rosa", (C, "flor-de-lis-rosa"), []),
            ("Viejo Molino", (C, "viejo-molino"), []),
            ("Bellavista", (C, "bellavista"), []),
            ("Aurora Blanco", (C, "aurora-blanca"), []),
            ("Ochavado Blanco", (C, "ochavada-blanca"), []),
        ]),
        ("Contemporáneas", (U, "/collections"), [
            ("Áurea", (C, "aurea"), []),
            ("Aaron Stewart", (C, "vistas-stewart"), []),
            ("Oaxaca", (C, "oaxaca"), []),
            ("Georgica", (C, "georgica"), []),
            ("Edén", (C, "eden"), []),
        ]),
        ("Fin de existencias", (C, "fin-de-existencias"), [
            ("Escenas", (C, "escenas"), []),
            ("Infanta Luisa", (C, "infanta-luisa"), []),
            ("María Cristina", (C, "maria-cristina"), []),
            ("Paraíso azul", (C, "paraiso-azul"), []),
            ("Kensington", (C, "kensington"), []),
            ("Azahar", (C, "azahar"), []),
            ("Azahar New", (C, "azahar-new"), []),
            ("Yedra", (C, "yedra"), []),
            ("Basic Line Blue", (C, "basic-line-blue"), []),
            ("Basic Line Red", (C, "basic-line-red"), []),
            ("Laberinto", (C, "laberinto"), []),
            ("Peces", (C, "peces"), []),
        ]),
    ]),
]

DERECHA = [
    ("Nuevo", (C, "novedades"), []),
    ("Viste tu mesa", (P, "viste-tu-mesa"), []),
    ("Ambientes", (P, "nuestras-mesas"), []),
    ("Legado", (P, "heritage-1841"), [
        ("Heritage 1842", (P, "heritage-1841"), []),
        ("Artesanía", (P, "artesania"), []),
        ("Sellos", (P, "identifica-tu-sello"), []),
    ]),
]

Q_MENUS = """
query { menus(first: 25) { nodes { id handle title items { title type url items { title type url items { title type url } } } } } }
"""

Q_RESOURCES = """
query {
  collections(first: 250) { nodes { id handle } }
  pages(first: 250) { nodes { id handle } }
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

M_MENU_CREATE = """
mutation ($title: String!, $handle: String!, $items: [MenuItemCreateInput!]!) {
  menuCreate(title: $title, handle: $handle, items: $items) {
    menu { id handle items { title url items { title url } } }
    userErrors { field message }
  }
}
"""


def build(nodes, cols, pages, faltan, ruta=""):
    """Convierte el árbol de arriba en items de Shopify, saltando lo que no existe."""
    out = []
    for title, target, children in nodes:
        camino = (ruta + " › " + title).strip(" ›")
        item = None
        if target is None:
            item = {"title": title, "type": "HTTP", "url": "#"}
        else:
            kind, ref = target
            if kind == U:
                item = {"title": title, "type": "HTTP", "url": ref}
            elif kind == C and ref in cols:
                item = {"title": title, "type": "COLLECTION", "resourceId": cols[ref]}
            elif kind == P and ref in pages:
                item = {"title": title, "type": "PAGE", "resourceId": pages[ref]}
            else:
                faltan.append((camino, "%s /%s" % ("colección" if kind == C else "página", ref)))

        hijos = build(children, cols, pages, faltan, camino) if children else []
        if item is None:
            # Sin destino propio pero con hijos válidos: se cuelgan del nivel de arriba
            # antes que perderlos.
            out.extend(hijos)
            continue
        if hijos:
            item["items"] = hijos
        out.append(item)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_args(parser, "informe-03-menu.json")
    args = parser.parse_args()

    admin = Admin(apply=args.apply)
    banner("Lote 3 · Menú nuevo", admin)

    recursos = admin.query(Q_RESOURCES)
    cols = {n["handle"]: n["id"] for n in recursos["collections"]["nodes"]}
    pages = {n["handle"]: n["id"] for n in recursos["pages"]["nodes"]}
    menus = {n["handle"]: n for n in admin.query(Q_MENUS)["menus"]["nodes"]}
    print("\n%d colecciones · %d páginas · menús: %s"
          % (len(cols), len(pages), ", ".join(sorted(menus))))

    faltan = []
    items_izq = build(IZQUIERDA, cols, pages, faltan)
    items_der = build(DERECHA, cols, pages, faltan)

    if "main-menu" in menus:
        print("\n--- menú actual `main-menu` (se guarda en el informe) ---")
        for it in menus["main-menu"]["items"]:
            print("  ·", it["title"], "→", it["url"])
        admin.done.append(("main-menu ANTES", menus["main-menu"]))
        admin.mutate("reescribir `main-menu` con el árbol de la izquierda",
                     M_MENU_UPDATE,
                     {"id": menus["main-menu"]["id"], "title": "Main menu",
                      "handle": "main-menu", "items": items_izq},
                     "menuUpdate")
    else:
        admin.mutate("crear `main-menu`", M_MENU_CREATE,
                     {"title": "Main menu", "handle": "main-menu", "items": items_izq},
                     "menuCreate")

    if "menu-derecha" in menus:
        admin.done.append(("menu-derecha ANTES", menus["menu-derecha"]))
        admin.mutate("reescribir `menu-derecha`", M_MENU_UPDATE,
                     {"id": menus["menu-derecha"]["id"], "title": "Menú derecha",
                      "handle": "menu-derecha", "items": items_der},
                     "menuUpdate")
    else:
        admin.mutate("crear `menu-derecha`", M_MENU_CREATE,
                     {"title": "Menú derecha", "handle": "menu-derecha", "items": items_der},
                     "menuCreate")

    if faltan:
        print("\n--- entradas SIN destino (%d): hacen falta esas colecciones ---" % len(faltan))
        for camino, destino in faltan:
            print("  · %-46s → %s" % (camino, destino))
        print("\n  El lote 2 crea las de tipo de producto; el resto necesita que el")
        print("  cliente diga qué productos van dentro (o una etiqueta por subfamilia).")

    admin.report(args.report)


if __name__ == "__main__":
    main()

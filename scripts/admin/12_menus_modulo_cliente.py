#!/usr/bin/env python3
"""Lote 12 · `main-menu` y `menu-derecha` con el árbol exacto del módulo de menú del cliente
(`la-cartuja-menu-final/menu.html`, 2026-09-14).

Cambia respecto al lote 5/6:
  - Mesa: los sueltos (Fuente y ensaladera, Sopera, Salsera, Cubitera) van bajo «Servir».
  - Café & Té: se agrupa en Tazas / Servicio / Platos; Juego de café y Juego de té
    quedan sueltos (el theme los pinta como tarjeta con foto).
  - Decoración: cuatro columnas, Arte y colección / Objetos decorativos / Baño / Gifts.
  - Colecciones: Nuevo y Fin de existencias sueltos (tarjetas); Fin de existencias pierde
    sus doce hijos —se llega a ellos desde su propia página—.
  - menu-derecha: Viste tu mesa · Ambientes · Legado. «Nuevo» sale de la barra (ya está
    en Colecciones).

Ninguna entrada se descarta: lo que no tiene colección ni tipo apunta a /search por su
nombre (así funciona en cuanto se dé de alta el producto), y una colección que aún no
existe apunta a /collections/<handle> por URL.

    python3 12_menus_modulo_cliente.py            # ensayo
    python3 12_menus_modulo_cliente.py --apply
"""

import argparse
import urllib.parse

from shopify_admin import Admin, add_common_args, banner

COL, TIPO, BUSQ, PAG, PROD, FILTRO = "col", "tipo", "busq", "pag", "prod", "filtro"

# (rótulo, destino, hijos). Destino: (COL, handle|None) | (TIPO, "Tipo") | (BUSQ, "términos") | (PAG, handle)
#   | (PROD, handle) -> ficha del producto | (FILTRO, (colección, Tipo, …)) -> colección filtrada por tipo
MAIN = [
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
        ("Bol y taza de consomé", (TIPO, "Bol"), [
            ("Bol grande", (BUSQ, "Bol Grande"), []),
            ("Bol pequeño", (BUSQ, "Bol Pequeño"), []),
            ("Bol mini", (BUSQ, "Bol Mini"), []),
            ("Taza de consomé", (BUSQ, "Taza Consome"), []),
            ("Taza de consomé con platillo", (BUSQ, "Taza Consome Con Platillo"), []),
        ]),
        ("Servir", (TIPO, "Fuente"), [
            ("Fuente y ensaladera", (TIPO, "Fuente"), []),
            ("Sopera", (TIPO, "Sopera"), []),
            ("Salsera", (TIPO, "Salsera"), []),
            ("Cubitera", (BUSQ, "Cubitera"), []),
        ]),
    ]),

    ("Café & Té", (TIPO, "Taza"), [
        ("Juego de Café", (BUSQ, "Juego Cafe"), []),
        ("Juego de Té", (BUSQ, "Juego Te"), []),
        ("Tazas", (TIPO, "Taza"), [
            ("Mug", (TIPO, "Mug"), []),
            ("Taza de café con platillo", (BUSQ, "Taza Cafe Con Platillo"), []),
            ("Taza de té con platillo", (BUSQ, "Taza Te Con Platillo"), []),
            ("Taza de desayuno con platillo", (BUSQ, "Taza Desayuno Con Platillo"), []),
            ("Taza de desayuno", (BUSQ, "Taza Desayuno"), []),
        ]),
        ("Servicio", (TIPO, "Cafetera"), [
            ("Azucarero", (TIPO, "Azucarero"), []),
            ("Bandeja de pastas", (BUSQ, "Bandeja Pastas"), []),
            ("Bombonera", (TIPO, "Bombonera"), []),
            ("Cafetera", (TIPO, "Cafetera"), []),
            ("Lechera", (TIPO, "Lechera"), []),
            ("Tetera", (TIPO, "Tetera"), []),
        ]),
        ("Platos", (TIPO, "Platillo"), [
            ("Plato de pastas", (BUSQ, "Plato Pastas"), []),
            ("Platillo de desayuno", (BUSQ, "Platillo Desayuno"), []),
        ]),
    ]),

    ("Decoración", (COL, "decoracion"), [
        ("Arte y colección", (COL, "arte-y-coleccion"), [
            ("Aguamanil", (FILTRO, ("arte-y-coleccion", "Palangana", "Jarro")), []),
            ("Cabeza frenológica", (PROD, "cabeza-frenologica"), []),
            ("Floreros · Tibores · Jarrones", (FILTRO, ("arte-y-coleccion", "Florero")), []),
            ("Tarros de botica", (PROD, "tarro-de-botica"), []),
            ("Mancerina", (PROD, "mancerina"), []),
            ("Caja 6 posavasos", (PROD, "caja-6-posavasos"), []),
            ("Hoja de parra", (PROD, "hoja-de-parra"), []),
        ]),
        ("Objetos decorativos", (COL, "objetos-decorativos"), [
            ("Vela aromática", (FILTRO, ("objetos-decorativos", "Vela")), []),
            ("Lapicero", (PROD, "lapicero"), []),
            ("Bandeja y vaciabolsillos", (COL, "objetos-decorativos"), []),
            ("Bandeja Vistas", (FILTRO, ("objetos-decorativos", "Bandeja")), []),
            ("Bandeja conmemorativa", (PROD, "bandeja-conmemorativa"), []),
            ("Vaciabolsillo", (PROD, "vaciabolsillos"), []),
        ]),
        ("Baño", (COL, "bano"), [
            ("Conjunto de baño", (PROD, "conjunto-de-bano"), []),
            ("Cepillero", (PROD, "cepillero"), []),
            ("Jabonera", (PROD, "jabonera"), []),
            ("Algodonera", (PROD, "algodonera"), []),
            ("Aguamanil", (FILTRO, ("bano", "Palangana", "Jarro")), []),
        ]),
        ("Gifts", (COL, "gifts"), [
            ("Libro", (PROD, "libro"), []),
            ("Camiseta", (PROD, "camiseta"), []),
            ("Bolsa", (PROD, "bolsa"), []),
        ]),
    ]),

    ("Colecciones", (COL, None), [
        ("Nuevo", (COL, "novedades"), []),
        ("Fin de existencias", (COL, "fin-de-existencias"), []),
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
    ]),
]

DERECHA = [
    ("Viste tu mesa", (PAG, "viste-tu-mesa"), []),
    ("Ambientes", (PAG, "nuestras-mesas"), []),
    ("Legado", (PAG, "heritage-1841"), [
        ("Heritage 1842", (PAG, "heritage-1841"), []),
        ("Artesanía", (PAG, "artesania"), []),
        ("Sellos", (PAG, "identifica-tu-sello"), []),
    ]),
]

Q_DATOS = """
query {
  collections(first: 250) { nodes { id handle } }
  productTypes(first: 250) { edges { node } }
  pages(first: 50) { nodes { id handle } }
  products(first: 250, query: "product_type:Cabeza OR product_type:Tarro OR product_type:Mancerina OR product_type:Posavasos OR product_type:Decoración OR product_type:Vela OR product_type:Lapicero OR product_type:Bandeja OR product_type:Vaciabolsillo OR product_type:Cepillero OR product_type:Jabonera OR product_type:Algodonera OR product_type:'Conjunto de baño' OR product_type:Libro OR product_type:Camiseta OR product_type:Bolsa") { nodes { id handle } }
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

M_MENU_CREATE = """
mutation ($title: String!, $handle: String!, $items: [MenuItemCreateInput!]!) {
  menuCreate(title: $title, handle: $handle, items: $items) {
    menu { id handle items { title url items { title url items { title url } } } }
    userErrors { field message }
  }
}
"""


ctx_prods = [{}]  # {handle: id} de los productos enlazados, se rellena en main()


def resolver(destino, cols, tipos, pages, avisos, camino):
    clase, valor = destino
    if clase == COL and valor is None:
        return {"type": "HTTP", "url": "/collections"}, "/collections"
    if clase == COL:
        if valor in cols:
            return {"type": "COLLECTION", "resourceId": cols[valor]}, "/collections/%s" % valor
        avisos.append("%s → la colección /%s no existe aún; va por URL" % (camino, valor))
        return {"type": "HTTP", "url": "/collections/%s" % valor}, "/collections/%s (no existe)" % valor
    if clase == TIPO:
        if valor not in tipos:
            avisos.append("%s → no existe el tipo «%s»; va a búsqueda" % (camino, valor))
            return resolver((BUSQ, valor), cols, tipos, pages, avisos, camino)
        url = "/collections/all?filter.p.product_type=%s" % urllib.parse.quote(valor)
        return {"type": "HTTP", "url": url}, url
    if clase == BUSQ:
        url = "/search?q=%s&type=product" % urllib.parse.quote(valor)
        return {"type": "HTTP", "url": url}, url
    if clase == PROD:
        prods = ctx_prods[0]
        if valor in prods:
            return {"type": "PRODUCT", "resourceId": prods[valor]}, "/products/%s" % valor
        avisos.append("%s → el producto /%s no existe aún; va a búsqueda" % (camino, valor))
        return resolver((BUSQ, valor.replace("-", " ")), cols, tipos, pages, avisos, camino)
    if clase == FILTRO:
        col, *tipos_f = valor
        url = "/collections/%s?%s" % (col, "&".join(
            "filter.p.product_type=%s" % urllib.parse.quote(t) for t in tipos_f))
        if col not in cols:
            avisos.append("%s → la colección /%s no existe aún (lote 16); va por URL" % (camino, col))
        return {"type": "HTTP", "url": url}, url
    if clase == PAG:
        if valor in pages:
            return {"type": "PAGE", "resourceId": pages[valor]}, "/pages/%s" % valor
        avisos.append("%s → la página /%s no existe aún; va por URL" % (camino, valor))
        return {"type": "HTTP", "url": "/pages/%s" % valor}, "/pages/%s (no existe)" % valor
    raise ValueError(destino)


def construir(nodos, ctx, ruta="", nivel=0):
    items = []
    for titulo, destino, hijos in nodos:
        camino = (ruta + " › " + titulo).strip(" ›")
        cols, tipos, pages, avisos, log = ctx
        item, etiqueta = resolver(destino, cols, tipos, pages, avisos, camino)
        item["title"] = titulo
        log.append("%s%-34s %s" % ("  " * nivel, titulo, etiqueta))
        if hijos:
            item["items"] = construir(hijos, ctx, camino, nivel + 1)
        items.append(item)
    return items


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_args(parser, "informe-12-menus-modulo-cliente.json")
    args = parser.parse_args()

    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 12 · menús con el árbol del módulo del cliente", admin)

    datos = admin.query(Q_DATOS)
    cols = {n["handle"]: n["id"] for n in datos["collections"]["nodes"]}
    tipos = {e["node"] for e in datos["productTypes"]["edges"]}
    pages = {n["handle"]: n["id"] for n in datos["pages"]["nodes"]}
    ctx_prods[0] = {n["handle"]: n["id"] for n in datos["products"]["nodes"]}
    menus = {n["handle"]: n for n in datos["menus"]["nodes"]}

    for handle, titulo, arbol in (("main-menu", "Main menu", MAIN), ("menu-derecha", "Menú derecha", DERECHA)):
        avisos, log = [], []
        items = construir(arbol, (cols, tipos, pages, avisos, log))
        print("\n--- %s ---" % handle)
        for line in log:
            print("  " + line)
        if avisos:
            print("\n--- avisos (%d) ---" % len(avisos))
            for a in avisos:
                print("  · " + a)

        if handle in menus:
            admin.done.append(("%s ANTES" % handle, menus[handle]))
            admin.mutate("reescribir `%s`" % handle, M_MENU_UPDATE,
                         {"id": menus[handle]["id"], "title": titulo, "handle": handle, "items": items},
                         "menuUpdate")
        else:
            admin.mutate("crear `%s`" % handle, M_MENU_CREATE,
                         {"title": titulo, "handle": handle, "items": items},
                         "menuCreate")

    admin.report(args.report)


if __name__ == "__main__":
    main()

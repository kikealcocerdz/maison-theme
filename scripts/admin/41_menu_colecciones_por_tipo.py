#!/usr/bin/env python3
"""Lote 41 · Menú superior: cada tipo de producto lleva a su propia colección.

Cliente 2026-10-01: unos enlaces iban al buscador (/search?q=Plato%20Llano → titular
«Buscar»), otros a /collections/all?filter.p.product_type=X (titular «Todos los
productos»). Como /collections/cafeteras-teteras, todos pasan a una colección
automática con su nombre de titular. Se reutilizan las colecciones por tipo que ya
había; las nuevas se crean y publican. «Bajo plato» pasa a «Bajoplato». «Lapicero»
sale del menú (producto en borrador, lote 40). «Cubitera» no existe como producto:
lleva a Champaneras.

    python3 41_menu_colecciones_por_tipo.py            # ensayo
    python3 41_menu_colecciones_por_tipo.py --apply
"""

import argparse

from shopify_admin import Admin, add_common_args, banner, publicar


def t(*tipos):
    return [("TYPE", "EQUALS", x) for x in tipos]


def ti(*textos):
    return [("TITLE", "CONTAINS", x) for x in textos]


NO_PLATILLO = [("TITLE", "NOT_CONTAINS", "Platillo")]

# handle: (título, disyuntiva, reglas)
NUEVAS = {
    "platos-llanos": ("Platos llanos", False, t("Plato") + ti("Plato Llano")),
    "platos-hondos": ("Platos hondos", False, t("Plato") + ti("Plato Hondo")),
    "platos-postre": ("Platos de postre", False, t("Plato") + ti("Postre")),
    "platos-pan": ("Platos de pan", False, t("Plato") + ti("Plato Pan")),
    "platos-pastas": ("Platos de pastas", False, t("Plato") + ti("Plato Pastas")),
    "platillos-consome": ("Platillos de consomé", False, t("Platillo") + ti("Consomé")),
    "platillos-desayuno": ("Platillos de desayuno", False, t("Platillo") + ti("Desayuno")),
    "boles-grandes": ("Boles grandes", False, t("Bol") + ti("Bol Grande")),
    "boles-pequenos": ("Boles pequeños", False, t("Bol") + ti("Bol Pequeño")),
    "boles-mini": ("Boles mini", False, t("Bol") + ti("Bol Mini")),
    "boles-tazas-consome": ("Boles y tazas de consomé", True, t("Bol") + ti("Taza Consomé")),
    "tazas-consome": ("Tazas de consomé", False, t("Taza") + ti("Taza Consomé") + NO_PLATILLO),
    "tazas-consome-platillo": ("Tazas de consomé con platillo", False, t("Taza") + ti("Taza Consomé Con Platillo")),
    "tazas-cafe-platillo": ("Tazas de café con platillo", False, t("Taza") + ti("Taza Café Con Platillo")),
    "tazas-te-platillo": ("Tazas de té con platillo", False, t("Taza") + ti("Taza Té Con Platillo")),
    "tazas-desayuno": ("Tazas de desayuno", False, t("Taza") + ti("Taza Desayuno") + NO_PLATILLO),
    "tazas-desayuno-platillo": ("Tazas de desayuno con platillo", False, t("Taza") + ti("Taza Desayuno Con Platillo")),
    "bandejas-pastas": ("Bandejas de pastas", False, t("Bandeja") + ti("Bandeja Pastas")),
    "fuentes-ensaladeras": ("Fuentes y ensaladeras", True, t("Fuente", "Ensaladera")),
    "servir": ("Servir", True, t("Fuente", "Ensaladera", "Sopera", "Salsera", "Champanera")),
    "cafe-te": ("Café & Té", True, ti("Juego Café", "Juego Té") + t("Taza", "Mug", "Cafetera", "Tetera", "Lechera",
                                                                      "Azucarero", "Bombonera", "Platillo") + ti("Bandeja Pastas", "Plato Pastas")),
    "servicio-cafe-te": ("Servicio de café y té", True, t("Azucarero", "Bombonera", "Cafetera", "Lechera", "Tetera") + ti("Bandeja Pastas")),
    "platos-cafe-te": ("Platos de café y té", True, t("Platillo") + ti("Plato Pastas")),
    "aguamaniles": ("Aguamaniles", True, t("Palangana", "Jarro")),
    "velas": ("Velas aromáticas", False, t("Vela")),
    "bandejas-vistas": ("Bandejas Vistas de Sevilla", False, ti("Bandeja Vistas")),
}
RETITULAR = {"bajoplato": "Bajoplato", "champanera": "Champaneras"}

# título del menú -> handle de destino
DESTINO = {
    "Mesa": "vajilla", "Vajilla": "vajilla", "Plato": "plato", "Bajo plato": "bajoplato",
    "Plato llano": "platos-llanos", "Plato hondo": "platos-hondos", "Plato postre": "platos-postre",
    "Plato pan": "platos-pan", "Platillo de consomé": "platillos-consome",
    "Bol y taza de consomé": "boles-tazas-consome", "Bol grande": "boles-grandes",
    "Bol pequeño": "boles-pequenos", "Bol mini": "boles-mini", "Taza de consomé": "tazas-consome",
    "Taza de consomé con platillo": "tazas-consome-platillo", "Servir": "servir",
    "Fuente y ensaladera": "fuentes-ensaladeras", "Sopera": "sopera", "Salsera": "salsera",
    "Cubitera": "champanera", "Café & Té": "cafe-te", "Juego de Café": "juegos-cafe",
    "Juego de Té": "juegos-te", "Tazas": "taza", "Mug": "mug",
    "Taza de café con platillo": "tazas-cafe-platillo", "Taza de té con platillo": "tazas-te-platillo",
    "Taza de desayuno con platillo": "tazas-desayuno-platillo", "Taza de desayuno": "tazas-desayuno",
    "Servicio": "servicio-cafe-te", "Azucarero": "azucarero", "Bandeja de pastas": "bandejas-pastas",
    "Bombonera": "bombonera", "Cafetera": "cafetera", "Lechera": "lechera", "Tetera": "tetera",
    "Platos": "platos-cafe-te", "Plato de pastas": "platos-pastas", "Platillo de desayuno": "platillos-desayuno",
    "Aguamanil": "aguamaniles", "Floreros · Tibores · Jarrones": "florero", "Vela aromática": "velas",
    "Bandeja Vistas": "bandejas-vistas",
}
RENOMBRAR = {"Bajo plato": "Bajoplato"}
QUITAR = {"Lapicero"}

Q_COLS = '''query($c:String){ collections(first:250, after:$c){ pageInfo{hasNextPage endCursor} nodes{ id handle title } } }'''
Q_MENU = '''{ menus(first:20){ nodes{ id handle title items{ id title type url resourceId tags
  items{ id title type url resourceId tags items{ id title type url resourceId tags } } } } } }'''
M_CREATE = '''mutation($input: CollectionInput!){ collectionCreate(input:$input){ collection{ id handle } userErrors{ field message } } }'''
M_UPDATE = '''mutation($input: CollectionInput!){ collectionUpdate(input:$input){ collection{ id handle title } userErrors{ field message } } }'''
M_MENU = '''mutation($id: ID!, $title: String!, $handle: String!, $items: [MenuItemUpdateInput!]!){
  menuUpdate(id:$id, title:$title, handle:$handle, items:$items){ menu{ handle } userErrors{ field message } } }'''


def main():
    args = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-41-menu-colecciones-tipo.json").parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 41 · Menú: colecciones por tipo", admin)

    cols, c = {}, None
    while True:
        r = admin.query(Q_COLS, {"c": c})["collections"]
        cols.update({n["handle"]: n for n in r["nodes"]})
        if not r["pageInfo"]["hasNextPage"]:
            break
        c = r["pageInfo"]["endCursor"]

    for h, (titulo, disy, reglas) in NUEVAS.items():
        if h in cols:
            print("  · %s ya existe" % h)
            continue
        body = admin.mutate("crear colección %s" % h, M_CREATE, {"input": {
            "title": titulo, "handle": h, "ruleSet": {"appliedDisjunctively": disy, "rules": [
                {"column": col, "relation": rel, "condition": cond} for col, rel, cond in reglas]}}}, "collectionCreate")
        if body:
            cols[h] = body["collection"]
            publicar(admin, body["collection"]["id"], h)
        else:
            cols[h] = {"id": "gid://shopify/Collection/ENSAYO-" + h, "handle": h}
    for h, titulo in RETITULAR.items():
        if cols[h]["title"] != titulo:
            admin.mutate("título %s → %s" % (h, titulo), M_UPDATE, {"input": {"id": cols[h]["id"], "title": titulo}}, "collectionUpdate")

    menu = next(m for m in admin.query(Q_MENU)["menus"]["nodes"] if m["handle"] == "main-menu")
    admin.done.append(("main-menu ANTES", menu))
    sin_destino = []

    def rehacer(items):
        out = []
        for it in items:
            if it["title"] in QUITAR:
                continue
            n = {"id": it["id"], "title": RENOMBRAR.get(it["title"], it["title"]), "type": it["type"], "tags": it["tags"],
                 "items": rehacer(it.get("items") or [])}
            url = it["url"] or ""
            if it["title"] in DESTINO:
                col = cols[DESTINO[it["title"]]]
                n["type"], n["resourceId"] = "COLLECTION", col["id"]
            elif "/search?" in url or "filter.p." in url:
                sin_destino.append(it["title"])
                n["url"] = url
            elif it.get("resourceId"):
                n["resourceId"] = it["resourceId"]
            else:
                n["url"] = url
            out.append(n)
        return out

    items = rehacer(menu["items"])
    if sin_destino:
        print("  ✗ sin destino: %s" % sin_destino)
    admin.mutate("reescribir main-menu", M_MENU, {"id": menu["id"], "title": menu["title"], "handle": menu["handle"],
                                                  "items": items}, "menuUpdate")
    admin.report(args.report)


if __name__ == "__main__":
    main()

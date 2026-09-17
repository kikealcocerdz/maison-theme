#!/usr/bin/env python3
"""Lote 21 · Rellenar `custom.pack` en las variantes de juego de café / té que no lo tienen.

Mismo síntoma que el lote 18 pero en los juegos: «Juego Cafe Flor Lis Azul · 15 P.»
no muestra las piezas del set. Recorre TODOS los productos de tipo Juego con
variantes 15 P. / 27 P. y rellena las que estén vacías (12 en el momento de escribirlo).

Composición, calcada de los juegos que sí la tienen:

  café 15 P.  azucarero 1 · cafetera 1 · lechera 1 · taza-cafe-con-platillo 6
  café 27 P.  idem con 12 tazas
  té   15 P.  azucarero 1 · lechera 1 · tetera 1 · taza-te-con-platillo 6
  té   27 P.  idem con 12 tazas

Handle de la pieza = `<pieza>-<sufijo>` (sufijo = handle del juego sin `juego-cafe-` /
`juego-te-`). Si no existe con ese handle se busca por título (hay handles con
erratas, p. ej. `taza-te-con-platilloochavado-blanco`). Metaobject `pieza_pack` con
handle `<pieza>-<sufijo>-<cantidad>`: se reutiliza si existe.

    python3 21_packs_juegos.py            # ensayo
    python3 21_packs_juegos.py --apply    # aplica
"""

import argparse
import json

from shopify_admin import Admin, add_common_args, banner

PACKS = {
    "cafe": {"15": [("azucarero", 1), ("cafetera", 1), ("lechera", 1), ("taza-cafe-con-platillo", 6)],
             "27": [("azucarero", 1), ("cafetera", 1), ("lechera", 1), ("taza-cafe-con-platillo", 12)]},
    "te":   {"15": [("azucarero", 1), ("lechera", 1), ("tetera", 1), ("taza-te-con-platillo", 6)],
             "27": [("azucarero", 1), ("lechera", 1), ("tetera", 1), ("taza-te-con-platillo", 12)]},
}

Q_JUEGOS = """
query { products(first: 100, query: "product_type:Juego") { nodes {
  handle title
  variants(first: 10) { nodes { id title pack: metafield(namespace: "custom", key: "pack") { value } } }
} } }
"""
Q_PRODUCTO = 'query ($h: String!) { productByIdentifier(identifier: {handle: $h}) { id } }'
Q_BUSCA = 'query ($q: String!) { products(first: 5, query: $q) { nodes { id handle title } } }'
Q_META = 'query ($h: String!) { metaobjectByHandle(handle: {type: "pieza_pack", handle: $h}) { id } }'

M_META_CREATE = """
mutation ($metaobject: MetaobjectCreateInput!) {
  metaobjectCreate(metaobject: $metaobject) {
    metaobject { id handle }
    userErrors { field message }
  }
}
"""
M_METAFIELDS_SET = """
mutation ($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) {
    metafields { key value }
    userErrors { field message }
  }
}
"""


def producto_gid(admin, pieza, sufijo, titulo_juego):
    """Producto de la pieza por handle; si no, por título («Taza Cafe Con Platillo <decorado>»)."""
    handle = "%s-%s" % (pieza, sufijo)
    found = admin.query(Q_PRODUCTO, {"h": handle})["productByIdentifier"]
    if found:
        return found["id"], handle
    decorado = titulo_juego.replace("Juego Cafe ", "").replace("Juego Te ", "")
    titulo = "%s %s" % (pieza.replace("-", " ").title(), decorado)
    hits = admin.query(Q_BUSCA, {"q": 'title:"%s"' % titulo})["products"]["nodes"]
    hits = [h for h in hits if h["title"].lower() == titulo.lower()]
    if hits:
        print("  ~ %s no existe; uso %s (%s)" % (handle, hits[0]["handle"], hits[0]["title"]))
        return hits[0]["id"], hits[0]["handle"]
    return None, handle


def pieza_gid(admin, handle, producto, cantidad):
    found = admin.query(Q_META, {"h": handle})["metaobjectByHandle"]
    if found:
        print("  = %s (existe)" % handle)
        return found["id"]
    body = admin.mutate("crear pieza %s" % handle, M_META_CREATE, {"metaobject": {
        "type": "pieza_pack",
        "handle": handle,
        "fields": [{"key": "producto", "value": producto}, {"key": "cantidad", "value": str(cantidad)}],
    }}, "metaobjectCreate")
    return body["metaobject"]["id"] if body else "gid://shopify/Metaobject/ENSAYO-" + handle


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-21-packs-juegos.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 21 · packs que faltan en juegos de café y té", admin)

    for juego in admin.query(Q_JUEGOS)["products"]["nodes"]:
        h = juego["handle"]
        if h.startswith("juego-cafe-"):
            tipo, sufijo = "cafe", h[len("juego-cafe-"):]
        elif h.startswith("juego-te-"):
            tipo, sufijo = "te", h[len("juego-te-"):]
        else:
            continue  # boles y otros juegos sin variantes de piezas
        for var in juego["variants"]["nodes"]:
            tamano = var["title"].split(" ")[0]
            if tamano not in PACKS[tipo] or var["pack"]:
                continue
            print("\n## %s · %s P." % (h, tamano))
            gids, faltan = [], []
            for pieza, cantidad in PACKS[tipo][tamano]:
                gid, handle_pieza = producto_gid(admin, pieza, sufijo, juego["title"])
                if not gid:
                    faltan.append(handle_pieza); continue
                gids.append(pieza_gid(admin, "%s-%s" % (handle_pieza, cantidad), gid, cantidad))
            if faltan:
                print("  ⚠ faltan productos %s; NO se escribe el pack (quedaría incompleto)" % ", ".join(faltan))
                admin.failed.append(("pack %s %s P." % (h, tamano), [{"message": "faltan " + ", ".join(faltan)}]))
                continue
            admin.mutate("custom.pack en %s %s P." % (h, tamano), M_METAFIELDS_SET, {"metafields": [{
                "ownerId": var["id"], "namespace": "custom", "key": "pack",
                "type": "list.metaobject_reference", "value": json.dumps(gids),
            }]}, "metafieldsSet")

    admin.report(args.report)


if __name__ == "__main__":
    main()

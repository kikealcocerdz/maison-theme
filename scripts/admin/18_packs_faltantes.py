#!/usr/bin/env python3
"""Lote 18 · Rellenar `custom.pack` en las variantes de vajilla que no lo tienen.

Síntoma: en la ficha de set, al pulsar «56 piezas» la rejilla «Tu pack contiene»
se queda vacía. El theme sólo pinta la lista si la variante tiene el metafield
`custom.pack` (lista de metaobjects `pieza_pack`: producto + cantidad). Cuatro
variantes se quedaron sin él en la carga inicial.

Composición, idéntica en todas las vajillas que sí lo tienen (42 = 9 piezas, 56 = 10):

  42 P.  fuente-med 1 · fuente-peq 1 · plato-hondo 12 · plato-llano 12 · plato-postre 12
         fuente-mini 1 · salsera 1 · sopera 1 · ensaladera 1
  56 P.  + fuente-gra 1, plato-llano 24, fuente-mini 2

Metaobject handle = `<pieza>-<sufijo>-<cantidad>`; si ya existe se reutiliza, si no
se crea. Al final `metafieldsSet` en la variante.

    python3 18_packs_faltantes.py            # ensayo
    python3 18_packs_faltantes.py --apply    # aplica
"""

import argparse

from shopify_admin import Admin, add_common_args, banner

PACKS = {
    "42": [("fuente-med", 1), ("fuente-peq", 1), ("plato-hondo", 12), ("plato-llano", 12),
           ("plato-postre", 12), ("fuente-mini", 1), ("salsera", 1), ("sopera", 1), ("ensaladera", 1)],
    "56": [("fuente-gra", 1), ("fuente-med", 1), ("fuente-peq", 1), ("plato-hondo", 12), ("plato-llano", 24),
           ("plato-postre", 12), ("fuente-mini", 2), ("salsera", 1), ("sopera", 1), ("ensaladera", 1)],
}

# (handle de la vajilla, sufijo de las piezas, tamaño)
FALTAN = [
    ("vajilla-flor-lis-azul", "flor-lis-azul", "56"),
    ("vajilla-n-vistas-azul-a-stewart", "n-vistas-azul-a-stewart", "42"),
    ("vajilla-n-vistas-amarillo-a-stewart", "n-vistas-amarillo-a-stewart", "56"),
    ("vajilla-negro-vistas", "negro-vistas", "42"),
]

Q_VARIANTES = """
query ($h: String!) {
  productByIdentifier(identifier: {handle: $h}) {
    variants(first: 10) { nodes { id title pack: metafield(namespace: "custom", key: "pack") { value } } }
  }
}
"""
Q_PRODUCTO = 'query ($h: String!) { productByIdentifier(identifier: {handle: $h}) { id } }'
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


def pieza_gid(admin, handle, producto_gid, cantidad):
    """Metaobject `pieza_pack` por handle; lo crea si falta. En ensayo devuelve un placeholder."""
    found = admin.query(Q_META, {"h": handle})["metaobjectByHandle"]
    if found:
        print("  = %s (existe)" % handle)
        return found["id"]
    body = admin.mutate("crear pieza %s" % handle, M_META_CREATE, {"metaobject": {
        "type": "pieza_pack",
        "handle": handle,
        "fields": [{"key": "producto", "value": producto_gid}, {"key": "cantidad", "value": str(cantidad)}],
    }}, "metaobjectCreate")
    return body["metaobject"]["id"] if body else "gid://shopify/Metaobject/ENSAYO-" + handle


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-18-packs-faltantes.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 18 · packs que faltan en vajillas", admin)

    for vajilla, sufijo, tamano in FALTAN:
        print("\n## %s · %s P." % (vajilla, tamano))
        variantes = admin.query(Q_VARIANTES, {"h": vajilla})["productByIdentifier"]["variants"]["nodes"]
        var = [v for v in variantes if v["title"].startswith(tamano)]
        if not var:
            print("  ⚠ no hay variante «%s P.»" % tamano); continue
        var = var[0]
        if var["pack"]:
            print("  = ya tiene pack, nada que hacer"); continue

        gids = []
        for pieza, cantidad in PACKS[tamano]:
            producto = admin.query(Q_PRODUCTO, {"h": "%s-%s" % (pieza, sufijo)})["productByIdentifier"]
            if not producto:
                print("  ⚠ falta el producto %s-%s; se omite esta pieza" % (pieza, sufijo)); continue
            gids.append(pieza_gid(admin, "%s-%s-%s" % (pieza, sufijo, cantidad), producto["id"], cantidad))

        admin.mutate("custom.pack en %s %s P." % (vajilla, tamano), M_METAFIELDS_SET, {"metafields": [{
            "ownerId": var["id"], "namespace": "custom", "key": "pack",
            "type": "list.metaobject_reference", "value": __import__("json").dumps(gids),
        }]}, "metafieldsSet")

    admin.report(args.report)


if __name__ == "__main__":
    main()

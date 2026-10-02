#!/usr/bin/env python3
"""Lote 43 · Ocho piezas «… Blanco» de forma 07 dentro de Aurora Blanca.

Fuente: correo del cliente 2026-10-02 (Bol pequeño, Bombonera, Bajoplato, Plato pan, Bol mini,
Taza desayuno, Champanera y Bol grande, todos «Blanco»). Solo salían en «Todos los productos»:
las colecciones Aurora Blanca y Aurora son automáticas por TÍTULO y estos se llaman «… Blanco».

Qué hace (sin tocar títulos ni handles):
  - etiqueta `aurora-blanca` en los 8 productos;
  - `custom.decorado = Aurora Blanca` (mismo código de decorado 0010 que sus hermanos; la
    forma NO se pone: son forma 07, no Aurora);
  - añade la regla «TAG = aurora-blanca» (OR) a las colecciones aurora-blanca y aurora.

Deshacer: quitar la etiqueta, borrar el metafield y quitar la regla (estado previo en el informe).

    python3 43_aurora_blanca_basicos.py           # ensayo
    python3 43_aurora_blanca_basicos.py --apply   # aplica
"""

import argparse

from shopify_admin import Admin, add_common_args, banner

HANDLES = ["bol-pequeno-blanco", "bombonera-blanco", "bajoplato-blanco", "plato-pan-blanco",
           "bol-mini-blanco", "taza-desayuno-blanco", "champanera-blanco", "bol-grande-blanco"]
TAG = "aurora-blanca"
DECORADO = "Aurora Blanca"
COLECCIONES = ["aurora-blanca", "aurora"]

Q_P = """{ productByIdentifier(identifier: {handle: "%s"}) { id handle title tags
  decorado: metafield(namespace: "custom", key: "decorado") { type value } } }"""
Q_C = """{ collectionByHandle(handle: "%s") { id handle title productsCount { count }
  ruleSet { appliedDisjunctively rules { column relation condition } } } }"""
M_TAGS = """
mutation ($id: ID!, $tags: [String!]!) {
  tagsAdd(id: $id, tags: $tags) { node { id } userErrors { field message } }
}
"""
M_MF = """
mutation ($m: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $m) { metafields { key } userErrors { field message } }
}
"""
M_COL = """
mutation ($c: CollectionInput!) {
  collectionUpdate(input: $c) { collection { handle } userErrors { field message } }
}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-43-aurora-blanca-basicos.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 43 · básicos blancos en Aurora Blanca", admin)

    tipo = "single_line_text_field"
    for h in HANDLES:
        p = admin.query(Q_P % h)["productByIdentifier"]
        admin.done.append(("ANTES", p))
        if TAG not in p["tags"]:
            admin.mutate("etiqueta %s → %s" % (TAG, h), M_TAGS, {"id": p["id"], "tags": [TAG]}, "tagsAdd")
        if not p["decorado"]:
            admin.mutate("decorado → %s" % h, M_MF, {"m": [{"ownerId": p["id"], "namespace": "custom",
                         "key": "decorado", "type": tipo, "value": DECORADO}]}, "metafieldsSet")

    for h in COLECCIONES:
        c = admin.query(Q_C % h)["collectionByHandle"]
        admin.done.append(("ANTES", c))
        reglas = c["ruleSet"]["rules"]
        if any(r["column"] == "TAG" and r["condition"] == TAG for r in reglas):
            continue
        assert c["ruleSet"]["appliedDisjunctively"], "%s no es OR: añadir una regla restringiría" % h
        nuevas = [{"column": r["column"], "relation": r["relation"], "condition": r["condition"]} for r in reglas]
        nuevas.append({"column": "TAG", "relation": "EQUALS", "condition": TAG})
        admin.mutate("regla TAG=%s en %s" % (TAG, h), M_COL,
                     {"c": {"id": c["id"], "ruleSet": {"appliedDisjunctively": True, "rules": nuevas}}}, "collectionUpdate")

    if admin.apply:
        for h in COLECCIONES:
            admin.done.append(("DESPUÉS", admin.query(Q_C % h)["collectionByHandle"]))
    admin.report(args.report)


if __name__ == "__main__":
    main()

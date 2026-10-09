#!/usr/bin/env python3
"""Lote 54 · Ochavada Blanca vacía tras renombrar «Ochavado Blanco» → «Ochavada Blanco».

El 2026-10-09 04:50 CEST se renombraron en el admin las 27 piezas «… Ochavado Blanco» a «… Ochavada Blanco».
Las colecciones automáticas filtran por título (CONTAINS «Ochavado» / «Ochavado Blanco») y se quedaron fuera.
Se AÑADE la variante «Ochavada…» a las reglas (OR); no se quita nada, valen los dos nombres.
Reglas anteriores (deshacer): ochavada = Ochavado | Negro Vistas | Stewart; ochavada-blanca = Ochavado Blanco | Ochavada Blanca.
Aplicado 2026-10-09: ochavada 112 → 139 productos, ochavada-blanca 1 → 28.

    python3 54_ochavada_reglas.py           # ensayo
    python3 54_ochavada_reglas.py --apply   # aplica
"""

import argparse

from shopify_admin import Admin, add_common_args, banner

NUEVAS = {"ochavada": "Ochavada", "ochavada-blanca": "Ochavada Blanco"}

Q = """query ($h: String!) { collectionByHandle(handle: $h) { id productsCount { count }
  ruleSet { appliedDisjunctively rules { column relation condition } } } }"""
M = """mutation ($input: CollectionInput!) { collectionUpdate(input: $input) {
  collection { handle ruleSet { rules { condition } } } userErrors { field message } } }"""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-54-ochavada-reglas.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 54 · Reglas Ochavada aceptan «Ochavada»", admin)
    for handle, cond in NUEVAS.items():
        c = admin.query(Q, {"h": handle})["collectionByHandle"]
        admin.done.append(("antes " + handle, c))
        rules = c["ruleSet"]["rules"]
        assert c["ruleSet"]["appliedDisjunctively"], "%s no es OR" % handle
        if any(r["condition"] == cond for r in rules):
            print("%s: ya tiene «%s»" % (handle, cond))
            continue
        print("%s (%d productos): + TITLE CONTAINS «%s»" % (handle, c["productsCount"]["count"], cond))
        admin.mutate(handle, M, {"input": {"id": c["id"], "ruleSet": {"appliedDisjunctively": True, "rules":
            rules + [{"column": "TITLE", "relation": "CONTAINS", "condition": cond}]}}}, "collectionUpdate")
    admin.report(args.report)


if __name__ == "__main__":
    main()

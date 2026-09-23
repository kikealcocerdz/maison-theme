#!/usr/bin/env python3
"""Lote 30 · colección «Cafeteras y teteras» (auditoría de enlaces 2026-09-23, §15 P0).

El megamenú (sections/header-group.json) enlaza /collections/cafeteras-teteras, que no
existía (404). Solo había `cafetera` (TYPE = Cafetera) y `tetera` (TYPE = Tetera): se
crea la unión como colección automática y se publica.
Deshacer: borrar la colección `cafeteras-teteras` en Admin.

    python3 30_coleccion_cafeteras_teteras.py           # ensayo
    python3 30_coleccion_cafeteras_teteras.py --apply   # aplica
"""
import argparse
from shopify_admin import Admin, add_common_args, banner, publicar

Q = '{ collectionByHandle(handle: "cafeteras-teteras") { id } }'
M = '''mutation ($input: CollectionInput!) { collectionCreate(input: $input) {
  collection { id handle } userErrors { field message } } }'''


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-30-coleccion-cafeteras-teteras.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 30 · colección Cafeteras y teteras", admin)

    if admin.query(Q)["collectionByHandle"]:
        print("  · cafeteras-teteras ya existe")
    else:
        r = admin.mutate("crear cafeteras-teteras", M, {"input": {
            "title": "Cafeteras y teteras", "handle": "cafeteras-teteras",
            "ruleSet": {"appliedDisjunctively": True, "rules": [
                {"column": "TYPE", "relation": "EQUALS", "condition": "Cafetera"},
                {"column": "TYPE", "relation": "EQUALS", "condition": "Tetera"}]}}}, "collectionCreate")
        if args.apply and r and r.get("collection"):
            publicar(admin, r["collection"]["id"], "cafeteras-teteras")
    admin.report(args.report)


if __name__ == "__main__":
    main()

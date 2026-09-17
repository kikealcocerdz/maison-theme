#!/usr/bin/env python3
"""Lote 17 · Las tres colecciones «Contemporáneas» que el header enlaza y no existían:
Áurea, Georgica y Edén (avisos del lote 12). Automáticas por título, como las demás
de decorado (`ceilan`, `bellavista`…). Hoy recogen: Áurea → el producto «Áurea»;
Georgica → «Mug Georgica»; Edén → «Mug Eden». Crecen solas al dar de alta piezas.

El menú ya apunta a /collections/<handle> por URL, así que no hay que relanzar el 12.

Deshacer: borrar las tres colecciones (ids en el informe).

    python3 17_colecciones_contemporaneas.py            # ensayo
    python3 17_colecciones_contemporaneas.py --apply
"""

import argparse

from shopify_admin import Admin, add_common_args, banner

# handle -> (título, palabras del título de producto que la disparan)
COLS = {
    "aurea": ("Áurea", ["Áurea", "Aurea"]),
    "georgica": ("Georgica", ["Georgica"]),
    "eden": ("Edén", ["Eden", "Edén"]),
}

Q = "query { collections(first: 250) { nodes { handle } } }"

M = """
mutation ($input: CollectionInput!) {
  collectionCreate(input: $input) { collection { id handle title } userErrors { field message } }
}
"""


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-17-colecciones-contemporaneas.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 17 · colecciones Áurea / Georgica / Edén", admin)

    existen = {c["handle"] for c in admin.query(Q)["collections"]["nodes"]}
    for handle, (titulo, palabras) in COLS.items():
        if handle in existen:
            print("  · %s ya existe" % handle)
            continue
        reglas = [{"column": "TITLE", "relation": "CONTAINS", "condition": p} for p in palabras]
        admin.mutate("crear «%s»" % titulo, M, {"input": {
            "title": titulo, "handle": handle,
            "ruleSet": {"appliedDisjunctively": True, "rules": reglas}}}, "collectionCreate")
    admin.report(args.report)


if __name__ == "__main__":
    main()

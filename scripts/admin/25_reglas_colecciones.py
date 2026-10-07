#!/usr/bin/env python3
"""Lote 25 · reglas de colección que no casan con los títulos reales.

Las colecciones por decorado filtran por «título contiene» con grafías que los
productos no llevan («Flor Lis Azul» → 2 productos cuando hay 35 con ese decorado,
«Ceilan» → 0, «Juego Cafe» → 0). Por eso «Descubre la colección» caía en
sets-regalo y «Te puede interesar» salía vacío. Se AÑADE la grafía real como
regla alternativa (OR), sin quitar la antigua: si mañana se corrigen títulos,
siguen entrando. No toca productos.

Deshacer: el informe guarda el ruleSet anterior entero de cada colección.

    python3 25_reglas_colecciones.py           # ensayo
    python3 25_reglas_colecciones.py --apply   # aplica
"""
import argparse
from shopify_admin import Admin, add_common_args, banner

# handle → grafías que faltan (columna TITLE, CONTAINS)
EXTRA = {
    "flor-de-lis-azul": ["Flor de Lis Azul"],
    "flor-de-lis-rosa": ["Flor de Lis Rosa"],
    "flor-lis": ["Flor de Lis"],
    "ceilan": ["Ceilán"],
    "juegos-cafe": ["Juego Café"],
    "juegos-te": ["Juego Té"],
    "ochavada-blanca": ["Ochavada Blanca"],
    "aurora": ["Flor de Lis", "Ceilán"],
}

Q = """
query ($handle: String!) {
  collectionByHandle(handle: $handle) {
    id handle title productsCount { count }
    ruleSet { appliedDisjunctively rules { column relation condition } }
  }
}
"""
M = """
mutation ($input: CollectionInput!) {
  collectionUpdate(input: $input) {
    collection { id handle productsCount { count } ruleSet { appliedDisjunctively rules { column relation condition } } }
    userErrors { field message }
  }
}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-25-reglas-colecciones.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 25 · reglas de colección con la grafía real", admin)

    for handle, extra in EXTRA.items():
        col = admin.query(Q, {"handle": handle})["collectionByHandle"]
        if not col or not col["ruleSet"]:
            print(f"  · {handle}: no existe o es manual, se salta")
            continue
        admin.done.append((f"{handle} ANTES", col))
        rules = [dict(r) for r in col["ruleSet"]["rules"]]
        have = {(r["column"], r["condition"]) for r in rules}
        new = [{"column": "TITLE", "relation": "CONTAINS", "condition": c} for c in extra if ("TITLE", c) not in have]
        if not new:
            print(f"  · {handle}: ya tiene las reglas")
            continue
        # Con más de una regla el conjunto tiene que ser OR (todas eran OR o de una sola regla).
        admin.mutate(
            f"{handle}: + {[r['condition'] for r in new]}", M,
            {"input": {"id": col["id"], "ruleSet": {"appliedDisjunctively": True, "rules": rules + new}}},
            "collectionUpdate",
        )
    if admin.apply:
        for handle in EXTRA:
            col = admin.query(Q, {"handle": handle})["collectionByHandle"]
            if col:
                print(f"  después {handle}: {col['productsCount']['count']} productos")
    admin.report(args.report)


if __name__ == "__main__":
    main()

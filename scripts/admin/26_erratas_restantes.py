#!/usr/bin/env python3
"""Lote 26 · erratas que quedaban del informe 2026-09-18.

Los 182 títulos del informe ya estaban corregidos en Admin el 2026-09-21 salvo
estos. Fuente: `Informe_checklist_erratas_web_La_Cartuja_2026-09-18.docx.md`.
  - 6 platos «Oaxaca … by Gastón y Daniela» → sin «Oaxaca» en el título (y la
    colección `oaxaca` gana la regla «Gastón y Daniela» para no vaciarse).
  - «Tetera Flor Lis de Rosa», «Mug  Flor de Lis Rosa» (×2, uno es el azul).
  - Colección `flor-lis`: título «Flor Lis» → «Flor de Lis».
  - Colección `bowls`: «Selección de bowls» → «Selección de boles».
  - Página heritage-1841: título «Heritage 1842» → «Heritage 1841» (SEO/pestaña).
Deshacer: el informe guarda título/descripción/ruleSet anteriores.

    python3 26_erratas_restantes.py           # ensayo
    python3 26_erratas_restantes.py --apply   # aplica
"""
import argparse
from shopify_admin import Admin, add_common_args, banner

TITULOS = {
    "plato-hondo-oaxaca-rosa-by-gaston-y-daniela-rosa": "Plato Hondo Rosa by Gastón y Daniela",
    "plato-llano-oaxaca-azul-by-gaston-y-daniela": "Plato Llano Azul by Gastón y Daniela",
    "plato-llano-oaxaca-amarillo-by-gaston-y-daniela": "Plato Llano Amarillo by Gastón y Daniela",
    "plato-postre-oaxaca-negro-by-gaston-y-daniela": "Plato Postre Negro by Gastón y Daniela",
    "plato-postre-oaxaca-verde-by-gaston-y-daniela": "Plato Postre Verde by Gastón y Daniela",
    "plato-postre-oaxaca-celeste-by-gaston-y-daniela": "Plato Postre Celeste by Gastón y Daniela",
    "tetera-flor-lis-rosa": "Tetera Flor de Lis Rosa",
    "mug-flor-lis-azul": "Mug Flor de Lis Azul",
    "mug-flor-lis-rosa": "Mug Flor de Lis Rosa",
}

Q_PROD = '{ productByHandle(handle: "%s") { id title } }'
M_PROD = 'mutation ($input: ProductInput!) { productUpdate(input: $input) { product { id title } userErrors { field message } } }'
Q_COL = '{ collectionByHandle(handle: "%s") { id title descriptionHtml ruleSet { appliedDisjunctively rules { column relation condition } } } }'
M_COL = 'mutation ($input: CollectionInput!) { collectionUpdate(input: $input) { collection { id title } userErrors { field message } } }'
Q_PAGE = '{ pages(first: 1, query: "handle:heritage-1841") { nodes { id title } } }'
M_PAGE = 'mutation ($id: ID!, $page: PageUpdateInput!) { pageUpdate(id: $id, page: $page) { page { id title } userErrors { field message } } }'


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-26-erratas-restantes.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 26 · erratas restantes", admin)

    # Antes de quitar «Oaxaca» de los títulos, la colección tiene que reconocerlos.
    ox = admin.query(Q_COL % "oaxaca")["collectionByHandle"]
    admin.done.append(("oaxaca ANTES", ox))
    rules = ox["ruleSet"]["rules"] + [{"column": "TITLE", "relation": "CONTAINS", "condition": "Gastón y Daniela"}]
    admin.mutate("oaxaca: + regla «Gastón y Daniela»", M_COL,
                 {"input": {"id": ox["id"], "ruleSet": {"appliedDisjunctively": True, "rules": rules}}}, "collectionUpdate")

    for handle, titulo in TITULOS.items():
        p = admin.query(Q_PROD % handle)["productByHandle"]
        if not p:
            print(f"  · {handle}: no existe"); continue
        if p["title"] == titulo:
            print(f"  · {handle}: ya correcto"); continue
        admin.done.append((f"{handle} ANTES", p))
        admin.mutate(f"{handle}: «{p['title']}» → «{titulo}»", M_PROD, {"input": {"id": p["id"], "title": titulo}}, "productUpdate")

    fl = admin.query(Q_COL % "flor-lis")["collectionByHandle"]
    admin.done.append(("flor-lis ANTES", fl))
    admin.mutate("flor-lis: título «Flor de Lis»", M_COL, {"input": {"id": fl["id"], "title": "Flor de Lis"}}, "collectionUpdate")

    bw = admin.query(Q_COL % "bowls")["collectionByHandle"]
    admin.done.append(("bowls ANTES", bw))
    admin.mutate("bowls: «bowls» → «boles» en la descripción", M_COL,
                 {"input": {"id": bw["id"], "descriptionHtml": bw["descriptionHtml"].replace("bowls", "boles")}}, "collectionUpdate")

    pg = admin.query(Q_PAGE)["pages"]["nodes"][0]
    admin.done.append(("heritage ANTES", pg))
    admin.mutate("heritage-1841: título «Heritage 1841»", M_PAGE, {"id": pg["id"], "page": {"title": "Heritage 1841"}}, "pageUpdate")
    admin.report(args.report)


if __name__ == "__main__":
    main()

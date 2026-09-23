#!/usr/bin/env python3
"""Lote 33 · erratas que quedaban tras el lote 26 (auditoría de Codex, 2026-09-23).

Fuente: `Informe_checklist_erratas_web_La_Cartuja_2026-09-18.docx.md`, líneas 202-204 y 279.
Deshacer: el informe guarda el título anterior.

    python3 33_erratas_codex.py           # ensayo
    python3 33_erratas_codex.py --apply   # aplica
"""
import argparse
from shopify_admin import Admin, add_common_args, banner

TITULOS = {
    "plato-postre-oaxaca-celeste-by-gaston-y-daniela": "Plato de Postre Celeste by Gastón y Daniela",
    "plato-postre-oaxaca-negro-by-gaston-y-daniela": "Plato de Postre Negro by Gastón y Daniela",
    "plato-postre-oaxaca-verde-by-gaston-y-daniela": "Plato de Postre Verde by Gastón y Daniela",
    "taza-te-con-platilloochavado-blanco": "Taza Té Con Platillo Ochavado Blanco",
}
Q = '{ productByHandle(handle: "%s") { id title } }'
M = 'mutation ($input: ProductInput!) { productUpdate(input: $input) { product { id title } userErrors { field message } } }'


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-33-erratas-codex.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 33 · erratas restantes (Codex)", admin)
    for handle, titulo in TITULOS.items():
        p = admin.query(Q % handle)["productByHandle"]
        if not p:
            print(f"  · {handle}: no existe"); continue
        if p["title"] == titulo:
            print(f"  · {handle}: ya correcto"); continue
        admin.done.append((f"{handle} ANTES", p))
        admin.mutate(f"{handle}: «{p['title']}» → «{titulo}»", M, {"input": {"id": p["id"], "title": titulo}}, "productUpdate")
    admin.report(args.report)


if __name__ == "__main__":
    main()

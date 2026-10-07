#!/usr/bin/env python3
"""Lote 37 · Página «Quiénes somos» (/pages/quienes-somos, plantilla page.quienes-somos).

Contenido de la entrega del cliente cartuja-quienes-somos v9 (2026-09-29), en sections/quienes-somos.liquid.
Enlazada desde la columna Editorial del megamenú y del footer.
Deshacer: borrar la página en Admin.

    python3 37_pagina_quienes_somos.py           # ensayo
    python3 37_pagina_quienes_somos.py --apply   # aplica
"""
import argparse
from shopify_admin import Admin, add_common_args, banner

HANDLE = "quienes-somos"
Q = '{ pages(first: 1, query: "handle:%s") { nodes { id handle title templateSuffix isPublished } } }' % HANDLE
M_CREATE = """
mutation ($page: PageCreateInput!) {
  pageCreate(page: $page) { page { id handle templateSuffix } userErrors { field message } }
}
"""
M_UPDATE = """
mutation ($id: ID!, $page: PageUpdateInput!) {
  pageUpdate(id: $id, page: $page) { page { id handle templateSuffix } userErrors { field message } }
}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-37-pagina-quienes-somos.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 37 · página Quiénes somos", admin)

    antes = admin.query(Q)["pages"]["nodes"]
    admin.done.append(("página ANTES", antes))
    if antes:
        admin.mutate("actualizar sufijo de la página", M_UPDATE,
                     {"id": antes[0]["id"], "page": {"templateSuffix": "quienes-somos", "isPublished": True}}, "pageUpdate")
    else:
        admin.mutate("crear página", M_CREATE, {"page": {
            "title": "Quiénes somos", "handle": HANDLE, "templateSuffix": "quienes-somos",
            "isPublished": True, "body": "",
        }}, "pageCreate")
    if admin.apply:
        print("Después:", admin.query(Q)["pages"]["nodes"])
    admin.report(args.report)


if __name__ == "__main__":
    main()

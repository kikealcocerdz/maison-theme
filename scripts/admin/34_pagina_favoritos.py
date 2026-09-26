#!/usr/bin/env python3
"""Lote 34 · Página «Tus favoritos» (/pages/favoritos, plantilla page.favoritos).

Muestra los favoritos guardados en el navegador (sections/favorites.liquid).
Deshacer: borrar la página en Admin.

    python3 34_pagina_favoritos.py           # ensayo
    python3 34_pagina_favoritos.py --apply   # aplica
"""
import argparse
from shopify_admin import Admin, add_common_args, banner

HANDLE = "favoritos"
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
    add_common_args(parser, "informe-34-pagina-favoritos.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 34 · página Tus favoritos", admin)

    antes = admin.query(Q)["pages"]["nodes"]
    admin.done.append(("página ANTES", antes))
    if antes:
        admin.mutate("actualizar sufijo de la página", M_UPDATE,
                     {"id": antes[0]["id"], "page": {"templateSuffix": "favoritos", "isPublished": True}}, "pageUpdate")
    else:
        admin.mutate("crear página", M_CREATE, {"page": {
            "title": "Tus favoritos", "handle": HANDLE, "templateSuffix": "favoritos",
            "isPublished": True, "body": "",
        }}, "pageCreate")
    if admin.apply:
        print("Después:", admin.query(Q)["pages"]["nodes"])
    admin.report(args.report)


if __name__ == "__main__":
    main()

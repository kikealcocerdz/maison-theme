#!/usr/bin/env python3
"""Lote 24 · página «Trabaja con nosotros» (plantilla page.trabaja).

Brief 2026-09-18 §13: página con envío de currículum a RRHH@lacartujadesevilla.com
y enlace en el pie (el enlace vive en sections/footer-group.json, en el theme).
El contenido lo pinta la plantilla; la página sólo aporta handle, título y sufijo.
Idempotente: si ya existe `trabaja-con-nosotros`, actualiza el sufijo y sale.
Deshacer: borrar la página en Tienda online › Páginas.

    python3 24_pagina_trabaja.py           # ensayo
    python3 24_pagina_trabaja.py --apply   # aplica
"""
import argparse
from shopify_admin import Admin, add_common_args, banner

HANDLE = "trabaja-con-nosotros"
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
    add_common_args(parser, "informe-24-pagina-trabaja.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 24 · página Trabaja con nosotros", admin)

    antes = admin.query(Q)["pages"]["nodes"]
    admin.done.append(("página ANTES", antes))
    if antes:
        admin.mutate("actualizar sufijo de la página", M_UPDATE,
                     {"id": antes[0]["id"], "page": {"templateSuffix": "trabaja", "isPublished": True}}, "pageUpdate")
    else:
        admin.mutate("crear página", M_CREATE, {"page": {
            "title": "Trabaja con nosotros", "handle": HANDLE, "templateSuffix": "trabaja",
            "isPublished": True, "body": "",
        }}, "pageCreate")
    if admin.apply:
        print("Después:", admin.query(Q)["pages"]["nodes"])
    admin.report(args.report)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Lote 11 · Pasa a ACTIVO y publica en Tienda online los productos de una etiqueta
(`novedad` por defecto; `--tag fin-de-existencias` para los 52 de la web antigua).

Sin esto no aparecen en «Novedades» ni en «Decoración» del storefront. Ojo: salen
con precio 0,00 € y foto provisional hasta que el cliente pase la ficha.

    python3 11_novedades_activar.py            # ensayo
    python3 11_novedades_activar.py --apply
    python3 11_novedades_activar.py --tag fin-de-existencias --apply
    python3 11_novedades_activar.py --handles tarro-de-botica mancerina --apply   # sólo esos
"""

import argparse

from shopify_admin import Admin, add_common_args, banner

Q = """
query ($q: String!) { products(first: 100, query: $q) { nodes { id handle title status resourcePublicationsCount { count } } }
  publications(first: 10) { nodes { id name } } }
"""

M = """
mutation ($input: ProductInput!) {
  productUpdate(input: $input) {
    product { id handle status }
    userErrors { field message }
  }
}
"""


M_PUBLISH = """
mutation ($id: ID!, $input: [PublicationInput!]!) {
  publishablePublish(id: $id, input: $input) {
    publishable { ... on Product { handle } }
    userErrors { field message }
  }
}
"""


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-11-novedades-activar.json")
    parser.add_argument("--tag", default="novedad")
    parser.add_argument("--handles", nargs="*", default=None,
                        help="sólo estos handles (por defecto, todos los de la etiqueta)")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 11 · activar y publicar tag:%s" % args.tag, admin)

    # con --handles se busca por handle (los mugs, p. ej., no llevan etiqueta)
    q = " OR ".join("handle:%s" % h for h in args.handles) if args.handles else "tag:%s" % args.tag
    datos = admin.query(Q, {"q": q})
    # Activo no basta: además hay que publicarlo en el canal Tienda online (y Shop).
    pubs = [{"publicationId": n["id"]} for n in datos["publications"]["nodes"]
            if n["name"] in ("Tienda online", "Online Store", "Shop")]
    for p in datos["products"]["nodes"]:
        if args.handles is not None and p["handle"] not in args.handles:
            continue
        if p["status"] != "ACTIVE":
            admin.mutate("activar «%s»" % p["title"], M,
                         {"input": {"id": p["id"], "status": "ACTIVE"}}, "productUpdate")
        if p["resourcePublicationsCount"]["count"] == 0:
            admin.mutate("publicar «%s» en Tienda online" % p["title"], M_PUBLISH,
                         {"id": p["id"], "input": pubs}, "publishablePublish")
    admin.report(args.report)


if __name__ == "__main__":
    main()

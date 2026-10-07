#!/usr/bin/env python3
"""Lote 39 · «Cuidados» por producto (metafield custom.cuidados) y texto del Libro.

El acordeón «Cuidados» de product.json lee `custom.cuidados` y, si está vacío, usa el
texto general de la plantilla. Cliente 2026-10-01: en el Libro, «Apto para lavavajillas».

    python3 39_cuidados_libro.py            # ensayo
    python3 39_cuidados_libro.py --apply
"""

import argparse

from shopify_admin import Admin, add_common_args, banner

TEXTO = "Apto para lavavajillas y para el uso diario."

M_DEF = """
mutation ($d: MetafieldDefinitionInput!) {
  metafieldDefinitionCreate(definition: $d) { createdDefinition { id } userErrors { field message code } }
}
"""
M_SET = """
mutation ($m: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $m) { metafields { id key value } userErrors { field message } }
}
"""


def main():
    args = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-39-cuidados-libro.json").parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 39 · Cuidados del Libro", admin)
    existe = admin.query('{ metafieldDefinitions(first:1, ownerType: PRODUCT, namespace:"custom", key:"cuidados") { nodes { id } } }')
    if not existe["metafieldDefinitions"]["nodes"]:
        admin.mutate("definición custom.cuidados", M_DEF, {"d": {
            "name": "Cuidados", "namespace": "custom", "key": "cuidados", "ownerType": "PRODUCT",
            "type": "multi_line_text_field",
            "description": "Texto del acordeón «Cuidados» de la ficha; vacío = texto general."}},
            "metafieldDefinitionCreate")
    libro = admin.query('{ productByHandle(handle:"libro") { id title } }')["productByHandle"]
    admin.mutate("cuidados de «%s»" % libro["title"], M_SET, {"m": [{
        "ownerId": libro["id"], "namespace": "custom", "key": "cuidados",
        "type": "multi_line_text_field", "value": TEXTO}]}, "metafieldsSet")
    admin.report(args.report)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Lote 14 · Ajustes tras el listado de «Decoración» del cliente (2026-09-14).

  1. «Vaciabolsillos» pasa a un solo producto con 5 diseños: Abanico Azul / Abanico
     Ocre / Abanico Rojo / Blanco / Fábrica Cartuja. Se le quitan las fotos actuales
     y se vuelve a sincronizar entero desde la carpeta (productSet no sustituye fotos).
  2. Se borra el producto «Abanico» (lote 09): era la misma serie.
  3. «Lapicero» recupera la etiqueta `novedad` (sin fotos aún: sigue con «Próximamente»).
  4. Se crean en borrador, con foto «Próximamente» y PVP de la tarifa 2026: Jabonera
     (29,95), Algodonera (68,95), Conjunto de baño (129,95). Y «Bandeja conmemorativa»
     sin precio (no está en la tarifa; en la web antigua sí existe).

Precio de los tres Abanico: 46,95 € = «vaciabolsillo decorado» de la tarifa. Es una
lectura nuestra (la serie Abanico no aparece con nombre); confirmar con el cliente.

Deshacer: «Abanico» se guarda entero en el informe; el resto son productos nuevos
(borrar) o una etiqueta (quitar).

    python3 14_decoracion_ajustes.py            # ensayo
    python3 14_decoracion_ajustes.py --apply
"""

import argparse
import importlib

from shopify_admin import Admin, add_common_args, banner

l13 = importlib.import_module("13_novedades_fotos")

# foto «Próximamente» que subió el cliente (la de Lapicero); Shopify la reimporta
PLACEHOLDER_URL = "https://cdn.shopify.com/s/files/1/1051/4641/7493/files/Cartuja_18_Composiciones_Proximamente_16.jpg"

VACIABOLSILLOS = dict(
    titulo="Vaciabolsillos", tipo="Vaciabolsillo", carpeta="Bandejas y vaciabolsillos",
    opcion="Diseño",
    variantes={
        "Novedad colección Abanico/Azul": "Abanico Azul",
        "Novedad colección Abanico/Ocre": "Abanico Ocre",
        "Novedad colección Abanico/Rojo": "Abanico Rojo",
        "Blanco": "Blanco",
        "Fabrica caruja": "Fábrica Cartuja",
    },
    precios={"Abanico Azul": "46.95", "Abanico Ocre": "46.95", "Abanico Rojo": "46.95",
             "Blanco": "37.95", "Fábrica Cartuja": "46.95"},
)

NUEVOS = {
    "jabonera": dict(titulo="Jabonera", tipo="Jabonera", precio="29.95", placeholder=PLACEHOLDER_URL),
    "algodonera": dict(titulo="Algodonera", tipo="Algodonera", precio="68.95", placeholder=PLACEHOLDER_URL),
    "conjunto-de-bano": dict(titulo="Conjunto de baño", tipo="Conjunto de baño", precio="129.95",
                             placeholder=PLACEHOLDER_URL),
    "bandeja-conmemorativa": dict(titulo="Bandeja conmemorativa", tipo="Bandeja", placeholder=PLACEHOLDER_URL),
}

Q = """
query ($q: String!) { products(first: 20, query: $q) {
  nodes { id handle title status tags productType
          media(first: 30) { nodes { id alt ... on MediaImage { image { url } } } }
          variants(first: 20) { nodes { title price } } } } }
"""

M_DELETE_PRODUCT = """
mutation ($input: ProductDeleteInput!) {
  productDelete(input: $input) { deletedProductId userErrors { field message } }
}
"""

M_TAGS_ADD = """
mutation ($id: ID!, $tags: [String!]!) {
  tagsAdd(id: $id, tags: $tags) { node { id } userErrors { field message } }
}
"""


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-14-decoracion-ajustes.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 14 · Ajustes de Decoración", admin)

    handles = ["vaciabolsillos", "abanico", "lapicero"] + list(NUEVOS)
    q = " OR ".join("handle:%s" % h for h in handles)
    existe = {p["handle"]: p for p in admin.query(Q, {"q": q})["products"]["nodes"]}
    print("existen: %s" % ", ".join(sorted(existe)))

    # 1. vaciabolsillos: fuera fotos, dentro todo de nuevo
    vb = existe["vaciabolsillos"]
    if vb["media"]["nodes"]:
        admin.mutate("quitar %d fotos de «Vaciabolsillos»" % len(vb["media"]["nodes"]), l13.M_DELETE_MEDIA,
                     {"id": vb["id"], "media": [m["id"] for m in vb["media"]["nodes"]]}, "productDeleteMedia")
    l13.sincronizar(admin, "vaciabolsillos", VACIABOLSILLOS, vb)

    # 2. abanico fuera (queda entero en el informe)
    ab = existe.get("abanico")
    if ab:
        admin.planned.append(("copia de «Abanico» antes de borrarlo", ab))
        admin.mutate("borrar «Abanico» (%s)" % ab["id"], M_DELETE_PRODUCT, {"input": {"id": ab["id"]}}, "productDelete")

    # 3. lapicero: etiqueta
    lp = existe.get("lapicero")
    if lp and l13.TAG not in lp["tags"]:
        admin.mutate("etiquetar «Lapicero» como novedad", M_TAGS_ADD, {"id": lp["id"], "tags": [l13.TAG]}, "tagsAdd")

    # 4. nuevos con placeholder
    for handle, cfg in NUEVOS.items():
        if handle in existe:
            print("  · %s ya existe, no se toca" % handle)
            continue
        l13.sincronizar(admin, handle, cfg, None)

    admin.report(args.report)


if __name__ == "__main__":
    main()

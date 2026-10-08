#!/usr/bin/env python3
"""Lote 51 · Ensaladera 202 Rosa mostraba la jabonera.

La foto «ensaladera» de fábrica (001_202_Rosa_ensaladera…) es la jabonera, y la sesión 202-rosa-068/069
está catalogada como «Juego de tocador (jabonera)» en fotos-producto-2/mapeo-fotos.csv. Las de la ensaladera
son la 032/033 (+034 detalle), el mismo cuenco gallonado del bodegón. Sube esas 3, quita las 3 de la jabonera
y deja: 032, bodegón, 033, 034. Deshacer: el informe guarda la media anterior.

    python3 51_ensaladera_202_rosa_fotos.py           # ensayo
    python3 51_ensaladera_202_rosa_fotos.py --apply   # aplica
"""

import argparse
import importlib.util
import os
import time

from shopify_admin import Admin, add_common_args, banner

_spec = importlib.util.spec_from_file_location("lote13", os.path.join(os.path.dirname(os.path.abspath(__file__)), "13_novedades_fotos.py"))
L13 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L13)

PRODUCTO = "gid://shopify/Product/11387597914453"
FOTOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../fotos-producto-2/optim/202-rosa")
NUEVAS = ["202-rosa-032.webp", "202-rosa-033.webp", "202-rosa-034.webp"]
JABONERA = ("001_202_Rosa_ensaladera_202_rosa", "202-rosa-068", "202-rosa-069")
ALT = "Ensaladera 202 Rosa"

Q = """query ($id: ID!) { product(id: $id) { title media(first: 30) { nodes { id alt status ... on MediaImage { image { url } } } } } }"""
M_CREATE = """mutation ($id: ID!, $media: [CreateMediaInput!]!) { productCreateMedia(productId: $id, media: $media) {
  media { id } mediaUserErrors { field message } } }"""
M_REORDER = """mutation ($id: ID!, $moves: [MoveInput!]!) { productReorderMedia(id: $id, moves: $moves) {
  job { id } mediaUserErrors { field message } } }"""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-51-ensaladera-202-rosa.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 51 · Ensaladera 202 Rosa: fotos de la ensaladera, fuera la jabonera", admin)

    antes = admin.query(Q, {"id": PRODUCTO})["product"]
    admin.done.append(("antes", antes))
    media = antes["media"]["nodes"]
    fuera = [m for m in media if any(j in (m.get("image") or {}).get("url", "") for j in JABONERA)]
    bodegon = [m for m in media if m not in fuera]
    assert len(fuera) == 3 and len(bodegon) == 1, "media inesperada: %s" % [m["image"]["url"] for m in media]
    print("quitar:", [m["image"]["url"].split("/")[-1].split("?")[0] for m in fuera])
    print("subir:", NUEVAS, "· queda:", bodegon[0]["image"]["url"].split("/")[-1].split("?")[0])
    if not args.apply:
        return admin.report(args.report)

    urls = L13.subir(admin, [os.path.join(FOTOS, f) for f in NUEVAS])
    nuevas = admin.mutate("crear 3 fotos", M_CREATE, {"id": PRODUCTO, "media": [
        {"originalSource": urls[os.path.join(FOTOS, f)], "alt": ALT, "mediaContentType": "IMAGE"} for f in NUEVAS]},
        "productCreateMedia")["media"]
    for _ in range(30):  # espera a que Shopify procese las imágenes antes de reordenar
        estado = {m["id"]: m["status"] for m in admin.query(Q, {"id": PRODUCTO})["product"]["media"]["nodes"]}
        if all(estado.get(n["id"]) == "READY" for n in nuevas):
            break
        time.sleep(2)
    admin.mutate("quitar jabonera", L13.M_DELETE_MEDIA, {"id": PRODUCTO, "media": [m["id"] for m in fuera]}, "productDeleteMedia")
    orden = [nuevas[0]["id"], bodegon[0]["id"], nuevas[1]["id"], nuevas[2]["id"]]
    admin.mutate("orden", M_REORDER, {"id": PRODUCTO, "moves": [{"id": i, "newPosition": str(n)} for n, i in enumerate(orden)]}, "productReorderMedia")
    admin.report(args.report)


if __name__ == "__main__":
    main()

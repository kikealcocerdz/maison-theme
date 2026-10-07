#!/usr/bin/env python3
"""Lote 38 · Segunda foto de producto (la del hover) desde «Segunda fotografia/».

Fuente: SwissTransfer del cliente 2026-10-01, copiada en `gropius/Segunda fotografia/`
(una carpeta por colección; se usan solo los `.webp` de `Web/`, 1440×1800; `4K/` no).
Fichero `<pieza>-<decorado>-02.webp` (2ª tanda, 2026-10-02: `-segunda.webp`) -> producto con las mismas palabras en el handle (cruce
del lote 28, sin el «02»).

Por producto: si la foto ya está en la posición 2, nada; si está en otra, se mueve a la 2;
si no está, se sube y se pone 2ª. La 1ª no se toca. NO borra ninguna foto.

    python3 38_segundas_fotos.py            # ensayo
    python3 38_segundas_fotos.py --apply
"""

import argparse
import importlib
import os
import re

from shopify_admin import Admin, add_common_args, banner

L28 = importlib.import_module("28_fotos_principales")
subir = importlib.import_module("13_novedades_fotos").subir

CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../Segunda fotografia")


def ficheros():
    for d, _, fs in os.walk(CARPETA):
        if "/Web" in d:
            yield from (os.path.join(d, f) for f in fs if f.endswith(("-02.webp", "-segunda.webp")))


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-38-segundas-fotos.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 38 · Segunda foto (hover)", admin)

    productos, c = [], None
    while True:
        r = admin.query(L28.Q_PRODUCTOS, {"c": c})["products"]
        productos += r["nodes"]
        if not r["pageInfo"]["hasNextPage"]:
            break
        c = r["pageInfo"]["endCursor"]
    por_palabras = {}
    for p in productos:
        por_palabras.setdefault(L28.palabras(p["handle"]), []).append(p)

    cuenta = {"ya segunda": 0, "mover": 0, "subir": 0, "sin producto": 0, "sin foto principal": 0}
    sin = []
    for f in sorted(ficheros()):
        hit = por_palabras.get(L28.palabras(re.sub(r"-(02|segunda)$", "", os.path.splitext(os.path.basename(f))[0])))
        if not hit or len(hit) > 1:
            cuenta["sin producto"] += 1
            sin.append(os.path.relpath(f, CARPETA))
            continue
        p = hit[0]
        media = p["media"]["nodes"]
        if not media:
            cuenta["sin foto principal"] += 1
            sin.append("SIN 1ª FOTO: " + p["handle"])
            continue
        clave = L28.plano(os.path.basename(f))
        urls = [L28.plano(((m.get("image") or {}).get("url") or "").split("?")[0].rsplit("/", 1)[-1]) for m in media]
        pos = next((i for i, u in enumerate(urls) if u.startswith(clave)), None)
        if pos == 1:
            cuenta["ya segunda"] += 1
            continue
        if pos is not None:
            cuenta["mover"] += 1
            mid = media[pos]["id"]
        else:
            cuenta["subir"] += 1
            src = subir(admin, [f])[f] if admin.apply else "file://" + f
            body = admin.mutate("subir 2ª foto a «%s»" % p["title"], L28.M_CREATE,
                                {"id": p["id"], "media": [{"originalSource": src, "alt": p["title"],
                                                           "mediaContentType": "IMAGE"}]}, "productCreateMedia")
            if not body:
                continue
            mid = body["media"][0]["id"]
        admin.mutate("segunda foto de «%s»" % p["title"], L28.M_REORDER,
                     {"id": p["id"], "moves": [{"id": mid, "newPosition": "1"}]}, "productReorderMedia")

    print("\nsin cruce: %s" % sin)
    print("\nResumen: %s" % cuenta)
    admin.report(args.report)


if __name__ == "__main__":
    main()

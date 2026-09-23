#!/usr/bin/env python3
"""Lote 28 · Foto principal de cada producto desde «PNG productos la cartuja/».

Fuente: carpeta del cliente `gropius/PNG productos la cartuja/` (2026-09-23), solo los
`.webp` de las carpetas `WebP/`, `WEBP_web/` y `otros producto webp/` (no `Originales/`,
no las `editorial-hover` que son para la 2ª foto).

Cruce fichero -> producto: mismas palabras en el nombre del fichero y en el handle
(sin prefijo numérico, sin «de/by/y/a», sin «1080-transparente»). Si dos ficheros caen
en el mismo producto gana el de `otros producto webp/` o `WEBP_web/` raíz (son las
correcciones; las tazas Flor de Lis Azul «con platillo» de las subcarpetas no traen
platillo), y si no el de la carpeta de colección antes que el de `Decoración/`.

Por producto: si la foto ya es la primera, nada; si ya está en otra posición, se sube a
la primera; si no está, se sube y se pone la primera. NO borra ninguna foto.

Deshacer: `productDeleteMedia` de los ids en `ejecutado` del informe (las creadas) o
reordenar a mano (las movidas).

    python3 28_fotos_principales.py            # ensayo
    python3 28_fotos_principales.py --apply
"""

import argparse
import importlib
import os
import re
import unicodedata

from shopify_admin import Admin, add_common_args, banner

subir = importlib.import_module("13_novedades_fotos").subir

CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../PNG productos la cartuja")
STOP = {"de", "by", "y", "a", "1080", "transparente"}

Q_PRODUCTOS = """
query ($c: String) { products(first: 100, after: $c) {
  pageInfo { hasNextPage endCursor }
  nodes { id handle title media(first: 30) { nodes { id ... on MediaImage { image { url } } } } } } }
"""
M_CREATE = """
mutation ($id: ID!, $media: [CreateMediaInput!]!) {
  productCreateMedia(productId: $id, media: $media) { media { id } userErrors { field message } }
}
"""
M_REORDER = """
mutation ($id: ID!, $moves: [MoveInput!]!) {
  productReorderMedia(id: $id, moves: $moves) { job { id } userErrors { field message } }
}
"""


def palabras(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"(\d+)cm", r"\1 cm", s).replace("aurrora", "aurora")
    return frozenset(t for t in re.split(r"[^a-z0-9]+", s) if t and t not in STOP)


def plano(s):
    """Nombre de fichero reducido a letras/números, para reconocerlo en la URL del CDN."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", os.path.splitext(s)[0])


def prioridad(path):
    if "otros producto webp" in path or os.path.basename(os.path.dirname(path)) == "WEBP_web":
        return 0
    return 2 if "/Decoración/" in path else 1


def ficheros():
    for d, _, fs in os.walk(CARPETA):
        if os.path.basename(d) in ("Originales", "png"):
            continue
        for f in fs:
            if f.endswith(".webp") and "editorial" not in f:
                yield os.path.join(d, f)


def elegir(admin, q=Q_PRODUCTOS):
    """{handle: (producto, fichero)} con todos los productos de la tienda."""
    productos, c = [], None
    while True:
        r = admin.query(q, {"c": c})["products"]
        productos += r["nodes"]
        if not r["pageInfo"]["hasNextPage"]:
            break
        c = r["pageInfo"]["endCursor"]
    por_palabras = {}
    for p in productos:
        por_palabras.setdefault(palabras(p["handle"]), []).append(p)

    elegido, sin_producto = {}, []
    for f in sorted(ficheros()):
        hit = por_palabras.get(palabras(re.sub(r"^\d+_", "", os.path.splitext(os.path.basename(f))[0])))
        if not hit or len(hit) > 1:
            sin_producto.append(os.path.relpath(f, CARPETA))
            continue
        h = hit[0]["handle"]
        if h not in elegido or prioridad(f) < prioridad(elegido[h][1]):
            elegido[h] = (hit[0], f)
    print("ficheros sin producto (se ignoran): %s" % sin_producto)
    return elegido


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-28-fotos-principales.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 28 · Foto principal desde «PNG productos la cartuja»", admin)

    elegido = elegir(admin)
    cuenta = {"ya primera": 0, "mover": 0, "subir": 0}
    for h, (p, f) in sorted(elegido.items()):
        media = p["media"]["nodes"]
        urls = [plano(((m.get("image") or {}).get("url") or "").split("?")[0].rsplit("/", 1)[-1]) for m in media]
        clave = plano(os.path.basename(f))
        pos = next((i for i, u in enumerate(urls) if u.startswith(clave)), None)
        if pos == 0:
            cuenta["ya primera"] += 1
            continue
        if pos is not None:
            cuenta["mover"] += 1
            mid = media[pos]["id"]
        else:
            cuenta["subir"] += 1
            src = subir(admin, [f])[f] if admin.apply else "file://" + f
            body = admin.mutate("subir foto a «%s» (%s)" % (p["title"], os.path.relpath(f, CARPETA)), M_CREATE,
                                {"id": p["id"], "media": [{"originalSource": src, "alt": p["title"],
                                                           "mediaContentType": "IMAGE"}]}, "productCreateMedia")
            if not admin.apply:
                continue
            if not body:
                continue
            mid = body["media"][0]["id"]
        admin.mutate("primera foto de «%s»" % p["title"], M_REORDER,
                     {"id": p["id"], "moves": [{"id": mid, "newPosition": "0"}]}, "productReorderMedia")

    print("\n%d productos con foto en la carpeta: %s" % (len(elegido), cuenta))
    admin.report(args.report)


if __name__ == "__main__":
    main()

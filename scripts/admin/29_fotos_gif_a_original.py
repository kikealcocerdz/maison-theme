#!/usr/bin/env python3
"""Lote 29 · Cambia las fotos del lote 28 que eran GIF/PSD disfrazados por el original.

En «PNG productos la cartuja/» 38 `.webp` de `WebP/` son GIF renombrados (256 colores,
transparencia de 1 bit) y `202 Rosa/Azucarero/202-rosa-azucarero.webp` es un PSD (Shopify
lo deja FAILED). Para cada uno: borra la foto que subió el lote 28 (la .gif o la FAILED,
reconocida por el nombre; las que ya tenía el producto no se tocan), sube el fichero de
`Originales/` con el mismo nombre (JPG/PNG real; el PSD sin original se convierte a PNG
con `sips`) y lo pone primero. `Azucarero-Ceilan.webp` no tiene original: se queda GIF.

Deshacer: `productDeleteMedia` de las creadas (informe); relanzar el lote 28 las vuelve a subir.

    python3 29_fotos_gif_a_original.py            # ensayo
    python3 29_fotos_gif_a_original.py --apply
"""

import argparse
import glob
import importlib
import os
import shutil
import subprocess
import tempfile

from shopify_admin import Admin, add_common_args, banner

L28 = importlib.import_module("28_fotos_principales")
subir = importlib.import_module("13_novedades_fotos").subir

Q_PRODUCTOS = """
query ($c: String) { products(first: 100, after: $c) {
  pageInfo { hasNextPage endCursor }
  nodes { id handle title media(first: 30) { nodes { id status ... on MediaImage { image { url } } } } } } }
"""
M_DELETE = """
mutation ($id: ID!, $media: [ID!]!) {
  productDeleteMedia(productId: $id, mediaIds: $media) { deletedMediaIds userErrors { field message } }
}
"""
FIRMAS = {b"\xff\xd8\xff": ".jpg", b"\x89PNG": ".png", b"RIFF": ".webp", b"GIF8": ".gif", b"8BPS": ".psd"}


def formato(path):
    with open(path, "rb") as fh:
        cabeza = fh.read(4)
    return next((ext for firma, ext in FIRMAS.items() if cabeza.startswith(firma)), None)


def original(path, tmp):
    """Fichero real (JPG/PNG) para subir en lugar de `path`, con la extensión que le toca."""
    stem = os.path.splitext(os.path.basename(path))[0]
    base = os.path.dirname(path)
    if os.path.basename(base) == "WebP":
        base = os.path.dirname(base)
    for cand in glob.glob(os.path.join(base, "Originales", stem + ".*")):
        if formato(cand) in (".jpg", ".png"):
            dst = os.path.join(tmp, stem + formato(cand))
            shutil.copy(cand, dst)
            return dst
    if formato(path) == ".psd":
        dst = os.path.join(tmp, stem + ".png")
        subprocess.run(["sips", "-s", "format", "png", path, "--out", dst], check=True, capture_output=True)
        return dst
    return None


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-29-fotos-gif-a-original.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 29 · Fotos GIF/PSD del lote 28 -> original", admin)
    tmp = tempfile.mkdtemp()

    for h, (p, f) in sorted(L28.elegir(admin, Q_PRODUCTOS).items()):
        if formato(f) == ".webp":
            continue
        nuevo = original(f, tmp)
        if not nuevo:
            print("\n! %s: %s sin original, se queda" % (h, os.path.basename(f)))
            continue
        clave = L28.plano(os.path.basename(f))
        viejas = [m["id"] for m in p["media"]["nodes"] if m["status"] == "FAILED" or (
            L28.plano(((m.get("image") or {}).get("url") or "").split("?")[0].rsplit("/", 1)[-1]).startswith(clave)
            and ".gif" in m["image"]["url"])]
        if viejas:
            admin.mutate("quitar foto GIF/FAILED de «%s»" % p["title"], M_DELETE,
                         {"id": p["id"], "media": viejas}, "productDeleteMedia")
        src = subir(admin, [nuevo])[nuevo] if admin.apply else "file://" + nuevo
        body = admin.mutate("subir original a «%s» (%s)" % (p["title"], os.path.basename(nuevo)), L28.M_CREATE,
                            {"id": p["id"], "media": [{"originalSource": src, "alt": p["title"],
                                                       "mediaContentType": "IMAGE"}]}, "productCreateMedia")
        if body:
            admin.mutate("primera foto de «%s»" % p["title"], L28.M_REORDER,
                         {"id": p["id"], "moves": [{"id": body["media"][0]["id"], "newPosition": "0"}]},
                         "productReorderMedia")

    admin.report(args.report)


if __name__ == "__main__":
    main()

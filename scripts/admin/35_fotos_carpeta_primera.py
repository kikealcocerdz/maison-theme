#!/usr/bin/env python3
"""Lote 35 · Foto de «PNG productos la cartuja/» como principal en TODOS los productos que la tienen.

Rehace 28 + 29 + 30 en una pasada, con la revisión visual del 2026-09-28 (página de
revisión: 125 «vale», 1 «no vale»). Sustituye al lote 31: las fotos que Adrián marcó mal
se han revisado una a una y solo `azucarero-202-rosa` sigue sin valer (se salta).

Por producto (cruce fichero -> producto del lote 28):
- fichero a subir = la .webp, o su original de `Originales/` si la .webp es GIF/PSD (lote 29);
- «ya subida» = una foto con el mismo nombre de fichero Y creada desde el 2026-09-10; las
  de antes con el mismo nombre son del catálogo de agosto y son otra foto (lote 30);
- ya primera -> nada; subida en otra posición -> se mueve a la primera; no subida -> se
  sube y se pone primera. NO borra ninguna foto.

Deshacer: `productDeleteMedia` de las creadas (informe) o reordenar las movidas.

    python3 35_fotos_carpeta_primera.py            # ensayo
    python3 35_fotos_carpeta_primera.py --apply
"""

import argparse
import importlib
import os
import tempfile

from shopify_admin import Admin, add_common_args, banner

L28 = importlib.import_module("28_fotos_principales")
L29 = importlib.import_module("29_fotos_gif_a_original")
subir = importlib.import_module("13_novedades_fotos").subir

NO_VALE = {"azucarero-202-rosa"}
DESDE = "2026-09-10"
Q_PRODUCTOS = """
query ($c: String) { products(first: 100, after: $c) {
  pageInfo { hasNextPage endCursor }
  nodes { id handle title media(first: 30) { nodes { id ... on MediaImage { createdAt image { url } } } } } } }
"""


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-35-fotos-carpeta-primera.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 35 · Foto de la carpeta como principal en todos", admin)
    tmp = tempfile.mkdtemp()

    cuenta = {"ya primera": 0, "mover": 0, "subir": 0, "no vale": 0, "sin original": 0}
    for h, (p, f) in sorted(L28.elegir(admin, Q_PRODUCTOS).items()):
        if h in NO_VALE:
            cuenta["no vale"] += 1
            continue
        real = f if L29.formato(f) == ".webp" else L29.original(f, tmp)
        if not real:  # ponytail: GIF sin original (Azucarero-Ceilan) se sube tal cual, como dejó el lote 29
            cuenta["sin original"] += 1
            real = f
        clave = L28.plano(os.path.basename(f))
        media = p["media"]["nodes"]
        pos = next((i for i, m in enumerate(media)
                    if (m.get("createdAt") or "") >= DESDE
                    and L28.plano(((m.get("image") or {}).get("url") or "").split("?")[0].rsplit("/", 1)[-1]).startswith(clave)),
                   None)
        if pos == 0:
            cuenta["ya primera"] += 1
            continue
        if pos is not None:
            cuenta["mover"] += 1
            mid = media[pos]["id"]
        else:
            cuenta["subir"] += 1
            src = subir(admin, [real])[real] if admin.apply else "file://" + real
            body = admin.mutate("subir foto a «%s» (%s)" % (p["title"], os.path.basename(real)), L28.M_CREATE,
                                {"id": p["id"], "media": [{"originalSource": src, "alt": p["title"],
                                                           "mediaContentType": "IMAGE"}]}, "productCreateMedia")
            if not body:
                continue
            mid = body["media"][0]["id"]
        admin.mutate("primera foto de «%s»" % p["title"], L28.M_REORDER,
                     {"id": p["id"], "moves": [{"id": mid, "newPosition": "0"}]}, "productReorderMedia")

    print("\nResumen: %s" % cuenta)
    admin.report(args.report)


if __name__ == "__main__":
    main()

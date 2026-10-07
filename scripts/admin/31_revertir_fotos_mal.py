#!/usr/bin/env python3
"""Lote 31 · Deshace las fotos principales de los lotes 28/29 que el diseñador marca mal.

Revisión de Adrián (2026-09-23): mal en general cafeteras, boles (todos los tamaños),
bandejas, tazas y azucareros; el Azucarero 202 Rosa trae una foto de Viejo Molino y el
bajoplato Flor de Lis Rosa también está mal. El resto, bien.

Para esos productos borra SOLO la foto que subieron los lotes 28/29 (ids en sus informes),
así vuelve a ser primera la que tenían antes. Las fotos antiguas no se tocan. Si el
producto se quedaría sin fotos, no se borra y se lista para revisarlo a mano.
Deshacer: volver a lanzar 28 y 29 (suben de nuevo los ficheros de la carpeta del cliente).

    python3 31_revertir_fotos_mal.py            # ensayo
    python3 31_revertir_fotos_mal.py --apply
"""
import argparse
import json
import re
import unicodedata

from shopify_admin import Admin, add_common_args, banner

PREFIJOS = ("cafetera", "bol ", "juego boles", "bandeja", "taza", "azucarero")
SUELTOS = ("bajoplato flor de lis rosa",)

Q = '{ products(first: 5, query: "title:\\"%s\\"") { nodes { id title media(first: 50) { nodes { id } } } } }'
M_DEL = '''mutation ($productId: ID!, $mediaIds: [ID!]!) { productDeleteMedia(productId: $productId, mediaIds: $mediaIds) {
  deletedMediaIds userErrors { field message } } }'''


def plano(t):
    return unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()


def nuevas():
    """título -> ids de las fotos que siguen vivas de los lotes 28/29."""
    subidas, borradas = {}, set()
    for f in ("informe-28-fotos-principales.json", "informe-29-fotos-gif-a-original.json"):
        for e in json.load(open(f))["ejecutado"]:
            m = re.match(r"subir (?:foto|original) a «(.*?)»", e["paso"])
            r = e.get("resultado") or {}
            if m:
                subidas.setdefault(m.group(1), []).extend(x["id"] for x in r.get("media") or [])
            borradas.update(r.get("deletedMediaIds") or [])
    return {t: [i for i in ids if i not in borradas] for t, ids in subidas.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-31-revertir-fotos-mal.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 31 · revertir fotos marcadas mal", admin)

    solo_nueva = []
    for titulo, ids in sorted(nuevas().items()):
        t = plano(titulo)
        if not ids or not (t.startswith(PREFIJOS) or t in SUELTOS):
            continue
        p = next((n for n in admin.query(Q % titulo.replace('"', ""))["products"]["nodes"] if n["title"] == titulo), None)
        if not p:
            print(f"  · {titulo}: no encontrado"); continue
        vivas = [m["id"] for m in p["media"]["nodes"]]
        quitar = [i for i in ids if i in vivas]
        if not quitar:
            continue
        if len(vivas) == len(quitar):
            solo_nueva.append(titulo); continue
        admin.mutate(f"quitar foto nueva de «{titulo}»", M_DEL, {"productId": p["id"], "mediaIds": quitar}, "productDeleteMedia")
    admin.done.append(("sin foto anterior (no se tocan)", solo_nueva))
    print(f"\nSin foto anterior, se dejan como están: {len(solo_nueva)}")
    for t in solo_nueva:
        print("  -", t)
    admin.report(args.report)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Lote 36 · Deshace el lote 35 si Adrián vuelve a rechazar esas fotos.

El lote 35 (2026-09-28) volvió a subir como principales las 104 fotos de la carpeta que
Adrián había marcado mal (lote 31), tras la revisión visual de ese día. Este lote borra
SOLO esas fotos (ids en `informe-35-fotos-carpeta-primera.json`), así cada producto vuelve
a la foto que tenía antes. Si el producto se quedaría sin fotos, no se toca y se lista.
Preparado por si acaso; no aplicado.

Deshacer: relanzar el lote 35 (vuelve a subirlas).

    python3 36_revertir_lote_35.py            # ensayo
    python3 36_revertir_lote_35.py --apply
"""
import argparse
import importlib
import json
import re

from shopify_admin import Admin, add_common_args, banner

L31 = importlib.import_module("31_revertir_fotos_mal")


def subidas():
    """título -> ids de las fotos que creó el lote 35."""
    out = {}
    for e in json.load(open("informe-35-fotos-carpeta-primera.json"))["ejecutado"]:
        m = re.match(r"subir foto a «(.*?)»", e["paso"])
        if m:
            out.setdefault(m.group(1), []).extend(x["id"] for x in (e.get("resultado") or {}).get("media") or [])
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-36-revertir-lote-35.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 36 · revertir lote 35", admin)

    solo_nueva = []
    for titulo, ids in sorted(subidas().items()):
        p = next((n for n in admin.query(L31.Q % titulo.replace('"', ""))["products"]["nodes"] if n["title"] == titulo), None)
        if not p:
            print(f"  · {titulo}: no encontrado"); continue
        vivas = [m["id"] for m in p["media"]["nodes"]]
        quitar = [i for i in ids if i in vivas]
        if not quitar:
            continue
        if len(vivas) == len(quitar):
            solo_nueva.append(titulo); continue
        admin.mutate(f"quitar foto del lote 35 de «{titulo}»", L31.M_DEL,
                     {"productId": p["id"], "mediaIds": quitar}, "productDeleteMedia")
    admin.done.append(("sin foto anterior (no se tocan)", solo_nueva))
    print(f"\nSin foto anterior, se dejan como están: {len(solo_nueva)}")
    for t in solo_nueva:
        print("  -", t)
    admin.report(args.report)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Lote 23 · mueve Aurora/Ochavado del grupo Clásicas a Blancas.

    python3 23_menu_colecciones_blancas.py          # ensayo
    python3 23_menu_colecciones_blancas.py --apply
"""

import argparse
import copy
import importlib.util
from pathlib import Path

from shopify_admin import Admin, add_common_args, banner


def cargar_base():
    path = Path(__file__).with_name("12_menus_modulo_cliente.py")
    spec = importlib.util.spec_from_file_location("menus_modulo_cliente", path)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def arbol_actualizado(base):
    arbol = copy.deepcopy(base.MAIN)
    colecciones = next(nodo for nodo in arbol if nodo[0] == "Colecciones")[2]
    clasicas = next(nodo for nodo in colecciones if nodo[0] == "Clásicas")[2]
    titulos_blancos = {"Aurora Blanco", "Ochavado Blanco"}
    blancos = [nodo for nodo in clasicas if nodo[0] in titulos_blancos]
    clasicas[:] = [nodo for nodo in clasicas if nodo[0] not in titulos_blancos]
    assert {nodo[0] for nodo in blancos} == titulos_blancos
    colecciones.append(("Blancas", (base.COL, None), blancos))
    return arbol


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_args(parser, "informe-23-menu-colecciones-blancas.json")
    args = parser.parse_args()
    base = cargar_base()
    admin = Admin(apply=args.apply)
    banner("Lote 23 · grupo Blancas en Colecciones", admin)

    datos = admin.query(base.Q_DATOS)
    menus = {n["handle"]: n for n in datos["menus"]["nodes"]}
    menu = menus["main-menu"]
    cols = {n["handle"]: n["id"] for n in datos["collections"]["nodes"]}
    tipos = {e["node"] for e in datos["productTypes"]["edges"]}
    pages = {n["handle"]: n["id"] for n in datos["pages"]["nodes"]}
    base.ctx_prods[0] = {n["handle"]: n["id"] for n in datos["products"]["nodes"]}
    avisos, log = [], []
    items = base.construir(arbol_actualizado(base), (cols, tipos, pages, avisos, log))

    admin.done.append(("main-menu ANTES", menu))
    admin.mutate(
        "reescribir `main-menu` con grupo Blancas",
        base.M_MENU_UPDATE,
        {"id": menu["id"], "title": menu["title"], "handle": menu["handle"], "items": items},
        "menuUpdate",
    )
    if admin.apply:
        despues = admin.query(base.Q_DATOS)
        admin.done.append((
            "main-menu DESPUÉS",
            next(n for n in despues["menus"]["nodes"] if n["handle"] == "main-menu"),
        ))
    admin.report(args.report)


if __name__ == "__main__":
    main()

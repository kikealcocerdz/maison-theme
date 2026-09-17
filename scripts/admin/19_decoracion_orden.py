#!/usr/bin/env python3
"""Lote 19 · Orden manual de la colección «Decoración» (ya estaba en MANUAL).

Las velas nuevas caían al final. Se reordena todo a mano, intercalando tipos y
colores para que no salgan cuatro palanganas seguidas: vela · tarro · mug · bandeja ·
florero · aguamanil · bombonera… Las fichas con foto «Próximamente» (lapicero,
jabonera, algodonera, conjunto de baño, bandeja conmemorativa) van al final de lo
visible; los 27 «Mug Letra» en borrador, los últimos (no se ven).

Lo que no esté en ORDEN se añade detrás en su orden actual. El orden anterior queda
en el informe.

    python3 19_decoracion_orden.py            # ensayo
    python3 19_decoracion_orden.py --apply
"""

import argparse

from shopify_admin import Admin, add_common_args, banner

HANDLE = "decoracion"

ORDEN = [
    "vela-aromatica-202-rosa", "tarro-de-botica", "mug-flor-lis-azul", "bandeja-vistas-sevilla-azul",
    "vela-aromatica-ceilan", "mancerina", "florero-alhambra-pequeno-azul", "mug-202-rosa",
    "vaciabolsillos", "cabeza-frenologica", "vela-aromatica-negro-vistas", "bombonera-202-rosa",
    "palangana-cartuja-azul", "mug-negro-vistas", "hoja-de-parra", "bandeja-vistas-plaza-espana-negra",
    "vela-aromatica-eden", "caja-6-posavasos", "jarro-cartuja-azul", "mug-ceilan",
    "champanera-202-rosa", "cepillero", "florero-alhambra-pequeno-rosa", "bandeja-vistas-maestranza-azul",
    "mug-bellavista", "bombonera-negro-vistas", "palangana-cartuja-rosa", "mug-con-letra",
    "bandeja-vistas-cibeles-azul", "champanera-blanco", "jarro-cartuja-rosa", "mug-viejo-molino",
    "florero-alhambra-pequeno-negro", "bandeja-vistas-sevilla-negro", "mug-flor-lis-rosa", "bombonera-blanco",
    "palangana-cartuja-negro", "mug-georgica", "bandeja-vistas-plaza-espana-azul", "champanera-negro-vistas",
    "jarro-cartuja-negro", "mug-eden", "florero-alhambra-pequeno-verde", "bandeja-vistas-cibeles-negro",
    "mug-n-vistas-azul-a-stewart", "palangana-cartuja-verde", "jarro-cartuja-verde", "mug-n-vistas-amarillo-a-stewart",
    "libro", "camiseta", "bolsa",
    # sin foto real todavía
    "lapicero", "jabonera", "algodonera", "conjunto-de-bano", "bandeja-conmemorativa",
]

Q = """
query ($h: String!) { collectionByHandle(handle: $h) {
  id sortOrder productsCount { count } products(first: 250) { nodes { id handle status } } } }
"""

M = """
mutation ($id: ID!, $moves: [MoveInput!]!) {
  collectionReorderProducts(id: $id, moves: $moves) { job { id } userErrors { field message } }
}
"""


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-19-decoracion-orden.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 19 · orden manual de Decoración", admin)

    col = admin.query(Q, {"h": HANDLE})["collectionByHandle"]
    actual = col["products"]["nodes"]
    por_handle = {p["handle"]: p for p in actual}
    print("sortOrder: %s · %d productos" % (col["sortOrder"], len(actual)))

    faltan = [h for h in ORDEN if h not in por_handle]
    if faltan:
        print("  ! no están en la colección (se ignoran): %s" % ", ".join(faltan))
    nuevo = [por_handle[h] for h in ORDEN if h in por_handle]
    resto = [p for p in actual if p["handle"] not in ORDEN]
    nuevo += resto
    print("  %d colocados a mano + %d detrás (%s…)" % (len(nuevo) - len(resto), len(resto),
                                                   ", ".join(p["handle"] for p in resto[:3])))
    for i, p in enumerate(nuevo[:12]):
        print("   %2d %s" % (i + 1, p["handle"]))

    admin.done.append(("%s ANTES" % HANDLE, [p["handle"] for p in actual]))
    moves = [{"id": p["id"], "newPosition": str(i)} for i, p in enumerate(nuevo)]
    admin.mutate("reordenar «Decoración» (%d)" % len(moves), M, {"id": col["id"], "moves": moves},
                 "collectionReorderProducts")
    admin.report(args.report)


if __name__ == "__main__":
    main()

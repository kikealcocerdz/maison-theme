#!/usr/bin/env python3
"""Lote 2 · Una colección automática por tipo de producto.

Por qué: el menú nuevo (Mesa, Café & Té) cuelga de subfamilias que hoy no tienen
colección, y la lógica de «te puede interesar» del theme busca la colección cuyo
handle coincide con el tipo del producto (`collections[product.type | handleize]`).
Sin ellas, ese bloque cae al respaldo.

Qué hace: por cada tipo de producto del catálogo crea una colección AUTOMÁTICA con
la regla `Tipo de producto = <tipo>`. El handle es el tipo en minúsculas y sin
acentos (azucarero, bol, bandeja…), que es justo lo que busca el theme.

Tipos vistos el 2026-09-10 (24): Azucarero, Bajoplato, Bandeja, Bol, Bombonera,
Cabeza, Cafetera, Champanera, Ensaladera, Florero, Fuente, Jarro, Juego, Lechera,
Mug, Palangana, Platillo, Plato, Salsera, Servicio, Sopera, Taza, Tetera, Vajilla.
El script vuelve a preguntarlos, así que no se queda viejo.

Duplicados: ya existen colecciones en plural hechas a mano (platos, tazas, bowls,
fuentes, bandejas, mugs, soperas, vajillas). Este script crea además la versión en
singular por tipo. Si prefieres no duplicar, pasa --saltar con esos tipos:

    python3 02_colecciones_por_tipo.py --saltar Plato,Taza,Bol,Fuente,Bandeja,Mug,Sopera,Vajilla

Deshacer: borrar las colecciones creadas (el informe lista sus handles).

    python3 02_colecciones_por_tipo.py            # ensayo
    python3 02_colecciones_por_tipo.py --apply    # aplica
"""

import argparse
import unicodedata

from shopify_admin import Admin, add_common_args, banner

# Título visible por tipo. Lo que no esté aquí usa el tipo tal cual.
TITULOS = {
    "Azucarero": "Azucareros",
    "Bajoplato": "Bajo plato",
    "Bandeja": "Bandejas",
    "Bol": "Boles",
    "Bombonera": "Bomboneras",
    "Cabeza": "Cabezas frenológicas",
    "Cafetera": "Cafeteras",
    "Champanera": "Champaneras",
    "Ensaladera": "Ensaladeras",
    "Florero": "Floreros, tibores y jarrones",
    "Fuente": "Fuentes",
    "Jarro": "Jarros",
    "Juego": "Juegos",
    "Lechera": "Lecheras",
    "Mug": "Mugs",
    "Palangana": "Aguamaniles",
    "Platillo": "Platillos",
    "Plato": "Platos",
    "Salsera": "Salseras",
    "Servicio": "Servicios",
    "Sopera": "Soperas",
    "Taza": "Tazas",
    "Tetera": "Teteras",
    "Vajilla": "Vajillas",
}

Q_TYPES = "query { productTypes(first: 250) { edges { node } } }"

Q_COLLECTIONS = """
query { collections(first: 250) { nodes { id handle title } } }
"""

M_COLLECTION_CREATE = """
mutation ($input: CollectionInput!) {
  collectionCreate(input: $input) {
    collection { id handle title }
    userErrors { field message }
  }
}
"""


def slug(text):
    """Mismo resultado que el filtro `handleize` de Liquid para estos nombres."""
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    out = "".join(c.lower() if c.isalnum() else "-" for c in norm)
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saltar", default="",
                        help="tipos a no crear, separados por comas (p. ej. Plato,Taza)")
    add_common_args(parser, "informe-02-colecciones-tipo.json")
    args = parser.parse_args()

    saltar = {s.strip().lower() for s in args.saltar.split(",") if s.strip()}

    admin = Admin(apply=args.apply)
    banner("Lote 2 · Colecciones automáticas por tipo de producto", admin)

    tipos = [e["node"] for e in admin.query(Q_TYPES)["productTypes"]["edges"]]
    existentes = {c["handle"]: c for c in admin.query(Q_COLLECTIONS)["collections"]["nodes"]}
    print("\n%d tipos en el catálogo · %d colecciones ya existentes" % (len(tipos), len(existentes)))

    for tipo in sorted(tipos):
        handle = slug(tipo)
        if tipo.lower() in saltar:
            print("\n· %s → saltado a petición" % tipo)
            continue
        if handle in existentes:
            print("\n· %s → ya existe /collections/%s" % (tipo, handle))
            continue
        plural = slug(TITULOS.get(tipo, tipo))
        aviso = ""
        if plural in existentes:
            aviso = "  (ojo: ya hay /collections/%s hecha a mano; esto añade la versión por tipo)" % plural
        print("\n· %s → crear /collections/%s%s" % (tipo, handle, aviso))
        admin.mutate(
            "crear colección «%s» (tipo = %s)" % (TITULOS.get(tipo, tipo), tipo),
            M_COLLECTION_CREATE,
            {"input": {
                "title": TITULOS.get(tipo, tipo),
                "handle": handle,
                "sortOrder": "BEST_SELLING",
                "ruleSet": {
                    "appliedDisjunctively": False,
                    "rules": [{"column": "TYPE", "relation": "EQUALS", "condition": tipo}],
                },
            }},
            "collectionCreate",
        )

    admin.report(args.report)


if __name__ == "__main__":
    main()

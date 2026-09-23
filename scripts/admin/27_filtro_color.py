#!/usr/bin/env python3
"""Lote 27 · filtro de color (plan 2026-09-18, §7 P0).

Crea la definición `custom.color` (texto, filtrable) y la rellena en cada producto:
  1. `custom.swatch` si lo tiene (hex → nombre),
  2. si no, el color del decorado (mirado sobre las fotos de producto),
  3. si no, un decorado o una palabra de color en el título.
Los que no casan con nada se quedan sin color y se listan en el informe.
Luego hay que activar «Color» en Search & Discovery → Filtros (solo UI).
Deshacer: borrar la definición con sus valores (metafieldDefinitionDelete, deleteAllAssociatedMetafields).

    python3 27_filtro_color.py           # ensayo
    python3 27_filtro_color.py --apply   # aplica
"""
import argparse
import re
from shopify_admin import Admin, add_common_args, banner

HEX = {"#2C4A7C": "Azul", "#C98A93": "Rosa", "#1F2124": "Negro", "#1A1A1A": "Negro",
       "#4A6B52": "Verde", "#D9B04A": "Amarillo"}
DECORADO = {
    "202 Rosa": "Rosa", "Flor de Lis Rosa": "Rosa", "Infanta Luisa": "Rosa",
    "Flor de Lis Azul": "Azul", "Ceilán": "Azul", "María Cristina": "Azul", "Paraíso Azul": "Azul",
    "Negro Vistas": "Negro", "Escenas": "Negro",
    "Aurora Blanca": "Blanco", "Ochavada Blanca": "Blanco",
    "Azahar": "Verde", "Azahar Nuevo": "Verde", "Yedra": "Verde",
    "Basic Line Red": "Rojo", "Kensington": "Rojo",
    "Viejo Molino": "Marrón", "Bellavista": "Multicolor",
}
# ponytail: primera palabra que aparezca; basta para los ~70 sin decorado ni swatch.
PALABRAS = [("azul", "Azul"), ("celeste", "Azul"), ("rosa", "Rosa"), ("negro", "Negro"),
            ("verde", "Verde"), ("amarillo", "Amarillo"), ("rojo", "Rojo"),
            ("blanc", "Blanco"), ("dorad", "Dorado"), ("oro", "Dorado")]

Q = '''{ products(first: 250%s) { pageInfo { hasNextPage endCursor } nodes { id handle title
  sw: metafield(namespace: "custom", key: "swatch") { value }
  dec: metafield(namespace: "custom", key: "decorado") { value }
  col: metafield(namespace: "custom", key: "color") { value } } } }'''
Q_DEF = '{ metafieldDefinitions(first: 1, ownerType: PRODUCT, namespace: "custom", key: "color") { nodes { id } } }'
M_DEF = '''mutation ($d: MetafieldDefinitionInput!) { metafieldDefinitionCreate(definition: $d) {
  createdDefinition { id } userErrors { field message } } }'''
M_SET = '''mutation ($m: [MetafieldsSetInput!]!) { metafieldsSet(metafields: $m) {
  metafields { id } userErrors { field message } } }'''


def color_de(p):
    sw = ((p["sw"] or {}).get("value") or "").upper()
    if sw in HEX:
        return HEX[sw]
    dec = (p["dec"] or {}).get("value")
    if dec in DECORADO:
        return DECORADO[dec]
    dec = next((d for d in DECORADO if d.lower() in p["title"].lower()), None)  # «Mug Ceilán»
    if dec:
        return DECORADO[dec]
    return next((c for w, c in PALABRAS if re.search(r"\b" + w, p["title"].lower())), None)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-27-filtro-color.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 27 · filtro de color", admin)

    if not admin.query(Q_DEF)["metafieldDefinitions"]["nodes"]:
        admin.mutate("definición custom.color", M_DEF, {"d": {
            "name": "Color", "namespace": "custom", "key": "color", "ownerType": "PRODUCT",
            "type": "single_line_text_field", "description": "Color principal (filtro de colecciones)",
            "access": {"storefront": "PUBLIC_READ"}}}, "metafieldDefinitionCreate")

    productos, after = [], None
    while True:
        r = admin.query(Q % (f', after: "{after}"' if after else ""))["products"]
        productos += r["nodes"]
        if not r["pageInfo"]["hasNextPage"]:
            break
        after = r["pageInfo"]["endCursor"]

    cambios, sin_color = [], []
    for p in productos:
        c = color_de(p)
        if not c:
            sin_color.append(p["title"])
        elif (p["col"] or {}).get("value") != c:
            cambios.append({"ownerId": p["id"], "namespace": "custom", "key": "color",
                            "type": "single_line_text_field", "value": c})
    admin.done.append(("sin color", sin_color))
    for i in range(0, len(cambios), 25):
        lote = cambios[i:i + 25]
        admin.mutate(f"color {i + 1}–{i + len(lote)} de {len(cambios)}", M_SET, {"m": lote}, "metafieldsSet")
    admin.report(args.report)


if __name__ == "__main__":
    main()

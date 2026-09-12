#!/usr/bin/env python3
"""Lote 10 · Da de alta los 52 productos de «Fin de existencias» de la web antigua.

Fuente: https://lacartujadesevilla.com/630-fin-de-existencias (52 artículos, leídos el
2026-09-12 y guardados en `datos-10-fin-existencias.json`: nombre, referencia, EAN,
precio rebajado / original, descripción y foto). Ninguno existe en Shopify (comprobado
por SKU y por título).

Cada producto se crea ACTIVO, con la misma pinta que el catálogo migrado:
  - título «Tipo Decorado» (Plato Llano Infanta Luisa), tipo = primera palabra,
  - precio rebajado + precio anterior tachado (compareAtPrice), SKU y EAN,
  - descripción de la web antigua limpia de estilos; si no tenía, la frase estándar,
  - metafields custom.decorado (+ custom.forma «Ochavada» en Yedra y Basic Line,
    que lo dicen sus descripciones; el resto se deja para el cliente) y
    custom.dimensiones cuando la descripción trae «Medidas:»,
  - la foto se importa desde la web antigua,
  - etiqueta `fin-de-existencias`: entra solo en la colección automática del lote 1.

Deshacer: borrar los productos (van en el informe) o quitarles la etiqueta.

    python3 10_fin_existencias_productos.py               # ensayo
    python3 10_fin_existencias_productos.py --apply --limit 1   # probar con uno
    python3 10_fin_existencias_productos.py --apply
"""

import argparse
import json
import os
import re
import unicodedata

from shopify_admin import Admin, add_common_args, banner

DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos-10-fin-existencias.json")
VENDOR = "La Cartuja de Sevilla"
TAG = "fin-de-existencias"
CATEGORIA = "gid://shopify/TaxonomyCategory/hg-11-10"  # Utensilios de mesa, como el resto

# Sufijo del título → valor del metafield (con acentos, como «Ceilán»). Orden importa:
# «Azahar Nuevo» antes que «Azahar».
DECORADOS = [
    ("Azahar Nuevo", "Azahar Nuevo"), ("Azahar", "Azahar"), ("Yedra", "Yedra"),
    ("Basic Line Red", "Basic Line Red"), ("Maria Cristina", "María Cristina"),
    ("Infanta Luisa", "Infanta Luisa"), ("Kensington", "Kensington"),
    ("Paraiso Azul", "Paraíso Azul"), ("Escenas", "Escenas"),
]
FORMAS = {"Yedra": "Ochavada", "Basic Line Red": "Ochavada"}

# Normalización de los nombres de la web antigua al estilo del catálogo migrado.
ARREGLOS = [
    (r"\s*colecci[oó]n\s+", " "), (r"\bde consom[eé]-desayuno\b", "consome/desayuno"),
    (r"\bbajo-plato\b", "bajoplato"), (r"\bplatilo\b", "platillo"),
    (r"\bazahar n\.", "azahar nuevo"), (r"\bconsom[eé]\b", "consome"),
    (r"\bcaf[eé]\b", "cafe"), (r"\bde\s+", ""),
]

Q_EXISTE = """
query ($q: String!) { products(first: 5, query: $q) { nodes { id handle title status } } }
"""

M_PRODUCT_SET = """
mutation ($input: ProductSetInput!) {
  productSet(input: $input, synchronous: true) {
    product {
      id handle title status
      variants(first: 1) { nodes { sku price compareAtPrice barcode } }
      media(first: 1) { nodes { ... on MediaImage { id status } } }
    }
    userErrors { field message code }
  }
}
"""


def sin_acentos(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def titulo(nombre):
    s = sin_acentos(nombre).lower()
    for pat, rep in ARREGLOS:
        s = re.sub(pat, rep, s)
    return " ".join("/".join(w.capitalize() for w in p.split("/")) for p in s.split())


def decorado(tit):
    for sufijo, valor in DECORADOS:
        if tit.endswith(" " + sufijo):
            return valor
    raise SystemExit("decorado desconocido en «%s»" % tit)


def limpiar_html(desc):
    """Quita estilos inline, spans, párrafos vacíos y el aviso de entrega de la web vieja."""
    s = re.sub(r"<(/?)span[^>]*>", "", desc)
    s = re.sub(r"<(\w+)[^>]*>", r"<\1>", s)
    parrafos = re.findall(r"<p>(.*?)</p>", s, re.S)
    parrafos = [p.strip() for p in parrafos if p.strip() and "Entrega disponible" not in p]
    return "".join("<p>%s</p>" % p for p in parrafos)


def producto(p):
    tit = titulo(p["name"])
    dec = decorado(tit)
    handle = re.sub(r"[^a-z0-9]+", "-", sin_acentos(tit).lower()).strip("-")
    desc = limpiar_html(p["desc"]) if p["desc"] else (
        "<p>%s colección %s. Pieza fabricada a mano con loza fina en España.</p>" % (tit, dec))
    metafields = [{"namespace": "custom", "key": "decorado", "type": "single_line_text_field", "value": dec}]
    if dec in FORMAS:
        metafields.append({"namespace": "custom", "key": "forma", "type": "single_line_text_field", "value": FORMAS[dec]})
    m = re.search(r"Medidas:\s*([^<]+?)\.?\s*</p>", desc)
    if m:
        metafields.append({"namespace": "custom", "key": "dimensiones", "type": "single_line_text_field", "value": m.group(1).replace("\xa0", " ").strip()})
    variante = {
        "optionValues": [{"optionName": "Title", "name": "Default Title"}],
        "price": "%.2f" % p["price"], "sku": p["ref"], "inventoryPolicy": "DENY",
        "inventoryItem": {"tracked": False},
    }
    if p["price_before"] and round(p["price_before"], 2) > p["price"]:
        variante["compareAtPrice"] = "%.2f" % p["price_before"]
    if p["ean"]:
        variante["barcode"] = p["ean"]
    return handle, {
        "title": tit, "handle": handle, "vendor": VENDOR, "productType": tit.split()[0],
        "status": "ACTIVE", "tags": [TAG], "descriptionHtml": desc, "category": CATEGORIA,
        "metafields": metafields,
        "productOptions": [{"name": "Title", "position": 1, "values": [{"name": "Default Title"}]}],
        "variants": [variante],
        "files": [{"originalSource": url, "alt": "%s — La Cartuja de Sevilla" % dec, "contentType": "IMAGE"}
                  for url in p["images"]],
    }


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-10-fin-existencias.json")
    parser.add_argument("--limit", type=int, default=0, help="sólo los N primeros (para probar)")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 10 · productos fin de existencias", admin)

    datos = json.load(open(DATOS))
    if args.limit:
        datos = datos[:args.limit]
    for p in datos:
        handle, inp = producto(p)
        hay = admin.query(Q_EXISTE, {"q": "handle:%s OR sku:%s" % (handle, p["ref"])})["products"]["nodes"]
        if hay:
            print("\n· %s ya existe (%s) — no se toca" % (handle, ", ".join(h["handle"] for h in hay)))
            continue
        admin.mutate("crear «%s» (%s, %s €)" % (inp["title"], p["ref"], inp["variants"][0]["price"]),
                     M_PRODUCT_SET, {"input": inp}, "productSet")

    admin.report(args.report)


if __name__ == "__main__":
    main()

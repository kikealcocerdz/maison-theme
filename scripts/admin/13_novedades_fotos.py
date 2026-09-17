#!/usr/bin/env python3
"""Lote 13 · Fotos y variantes de las novedades desde la carpeta del cliente.

Cruce hecho el 2026-09-14 de `~/Downloads/Novedades/` contra Shopify:
  - 6 productos ya existen (lote 09) pero alguien les quitó la etiqueta `novedad` y
    les puso una foto «Próximamente»; siguen sin variantes.
  - 7 productos de la carpeta no existen (hoja de parra, mancerina, tarros de botica,
    cepillero, bolsa, camiseta, libro).

Precios: PVP de `~/Downloads/Tarifa y PVP.pdf` (Tarifas 2026, página 4 «Decoración»)
cuando la pieza aparece con nombre claro. Áurea, vela aromática, abanico, bolsa,
camiseta y libro no están en la tarifa: se quedan a 0,00 € (no se inventa).

Un `productSet` por producto (crea o actualiza por handle): título, tipo, etiqueta
`novedad`, opción + variantes cuando la carpeta trae subcarpetas (aroma / color /
diseño), precio PVP, y todas las fotos subidas por `stagedUploadsCreate`. Los nuevos
van en BORRADOR; los seis existentes se quedan como están (activos).

Después, en los seis existentes, se retira la foto «Próximamente» (queda su URL en
el informe por si hay que volver a ponerla).

Deshacer: borrar los productos nuevos (van en el informe); en los existentes, borrar
las fotos subidas y volver a poner la «Próximamente».

    python3 13_novedades_fotos.py            # ensayo (no sube nada)
    python3 13_novedades_fotos.py --apply

APLICADO el 2026-09-14. No relanzar con --apply: `productSet` añade fotos, no las
sustituye, y se duplicarían. Los ajustes posteriores van en el lote 14.
"""

import argparse
import mimetypes
import os
import sys
import urllib.request
import uuid

from shopify_admin import Admin, AdminError, add_common_args, banner, publicar

CARPETA = os.path.expanduser("~/Downloads/Novedades")
VENDOR = "La Cartuja de Sevilla"
TAG = "novedad"
PLACEHOLDER = "Proximamente"  # fragmento del nombre de la foto provisional del cliente

# handle -> {titulo, tipo, carpeta, [opcion, variantes {subcarpeta: valor}],
#            [precio | precios {valor: PVP}], [tamanos {valor: PVP}] (2ª opción «Tamaño»)}
# ponytail: subcarpeta == variante; sin subcarpetas == producto simple.
PRODUCTOS = {
    "aurea": dict(titulo="Áurea", tipo="Decoración", carpeta="Aurea"),
    "vela-aromatica": dict(titulo="Vela aromática", tipo="Vela", carpeta="Artístico/Vela aromática",
                           opcion="Aroma", variantes={
                               "202 rosa": "202 Rosa", "Ceilan": "Ceilán", "eden": "Edén", "Negro vistas": "Negro Vistas"}),
    "caja-6-posavasos": dict(titulo="Caja con 6 posavasos", tipo="Posavasos", carpeta="Artístico/caja 6 posavasos",
                             precio="95.95"),
    # la foto suelta de «Bandejas y vaciabolsillos/» es la bandeja Abanico: va a `abanico`
    "vaciabolsillos": dict(titulo="Vaciabolsillos", tipo="Vaciabolsillo", carpeta="Bandejas y vaciabolsillos",
                           sin_raiz=True, opcion="Diseño",
                           variantes={"Blanco": "Blanco", "Fabrica caruja": "Fábrica Cartuja"},
                           precios={"Blanco": "37.95", "Fábrica Cartuja": "46.95"}),
    "abanico": dict(titulo="Abanico", tipo="Abanico", carpeta="Bandejas y vaciabolsillos/Novedad colección Abanico",
                    extra_raiz="Bandejas y vaciabolsillos", opcion="Color",
                    variantes={"Azul": "Azul", "Ocre": "Ocre", "Rojo": "Rojo"}),
    # nuevos
    "hoja-de-parra": dict(titulo="Hoja de parra", tipo="Decoración", carpeta="Artístico/Hoja de parra", precio="29.95"),
    "mancerina": dict(titulo="Mancerina", tipo="Mancerina", carpeta="Artístico/mancerina", precio="120.95"),
    "tarro-de-botica": dict(titulo="Tarro de botica", tipo="Tarro", carpeta="Artístico/Tarros de botica",
                            opcion="Color", variantes={
                                "Tarro de botica azul": "Azul", "Tarro de botica negro": "Negro",
                                "Tarro de botica rosa": "Rosa", "Tarro de botica verde": "Verde"},
                            tamanos={"Pequeño": "56.95", "Mediano": "72.95", "Grande": "96.95"}),
    "cepillero": dict(titulo="Cepillero", tipo="Cepillero", carpeta="Baño/Cepillero", precio="44.95"),
    "bolsa": dict(titulo="Bolsa", tipo="Bolsa", carpeta="Gifts/Bolsa"),
    "camiseta": dict(titulo="Camiseta", tipo="Camiseta", carpeta="Gifts/Camiseta"),
    "libro": dict(titulo="Libro", tipo="Libro", carpeta="Gifts/Libro"),
}
EXTS = (".png", ".jpg", ".jpeg", ".webp")

Q_ESTADO = """
query ($q: String!) { products(first: 20, query: $q) {
  nodes { id handle status media(first: 30) { nodes { id alt ... on MediaImage { image { url } } } } } } }
"""

M_STAGED = """
mutation ($input: [StagedUploadInput!]!) {
  stagedUploadsCreate(input: $input) {
    stagedTargets { url resourceUrl parameters { name value } }
    userErrors { field message }
  }
}
"""

M_PRODUCT_SET = """
mutation ($input: ProductSetInput!) {
  productSet(input: $input, synchronous: true) {
    product { id handle title status tags variants(first: 10) { nodes { title } } media(first: 30) { nodes { id alt } } }
    userErrors { field message }
  }
}
"""

M_DELETE_MEDIA = """
mutation ($id: ID!, $media: [ID!]!) {
  productDeleteMedia(productId: $id, mediaIds: $media) {
    deletedMediaIds
    userErrors { field message }
  }
}
"""


def fotos(carpeta):
    """Ficheros de imagen directamente en `carpeta` (sin bajar a subcarpetas), ordenados."""
    return sorted(
        os.path.join(carpeta, f) for f in os.listdir(carpeta)
        if f.lower().endswith(EXTS) and not f.startswith(".")
    )


def alt_de(path):
    return os.path.splitext(os.path.basename(path))[0].replace("_", " ")


def subir(admin, paths):
    """Sube ficheros locales al bucket temporal de Shopify. Devuelve {path: resourceUrl}."""
    if not paths:
        return {}
    inputs = [{
        "resource": "PRODUCT_IMAGE", "httpMethod": "POST",
        "filename": os.path.basename(p),
        "mimeType": mimetypes.guess_type(p)[0] or "image/jpeg",
    } for p in paths]
    body = admin._run(M_STAGED, {"input": inputs}, mutation=True)["stagedUploadsCreate"]
    if body["userErrors"]:
        raise AdminError("stagedUploadsCreate: %s" % body["userErrors"])
    out = {}
    for path, target in zip(paths, body["stagedTargets"]):
        _post_multipart(target, path)
        out[path] = target["resourceUrl"]
        print("  ↑ %s" % os.path.basename(path))
    return out


def _post_multipart(target, path):
    # multipart a mano: sin dependencias (stdlib no lo trae).
    boundary = uuid.uuid4().hex
    parts = []
    for p in target["parameters"]:
        parts.append(("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n"
                      % (boundary, p["name"], p["value"])).encode())
    with open(path, "rb") as fh:
        data = fh.read()
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    parts.append(("--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\n"
                  "Content-Type: %s\r\n\r\n" % (boundary, os.path.basename(path), mime)).encode())
    parts.append(data)
    parts.append(("\r\n--%s--\r\n" % boundary).encode())
    req = urllib.request.Request(
        target["url"], data=b"".join(parts), method="POST",
        headers={"Content-Type": "multipart/form-data; boundary=%s" % boundary},
    )
    with urllib.request.urlopen(req) as resp:
        if resp.status not in (200, 201, 204):
            raise AdminError("subida %s: HTTP %s" % (path, resp.status))


def sincronizar(admin, handle, cfg, existe):
    """Un productSet (crear o actualizar) a partir de la config y la carpeta de fotos."""
    titulo, tipo = cfg["titulo"], cfg["tipo"]
    opcion, variantes = cfg.get("opcion"), cfg.get("variantes", {})
    # fotos de producto (raíz) + de cada variante (subcarpeta); sin carpeta -> placeholder
    if cfg.get("fotos"):
        raiz, por_variante = list(cfg["fotos"]), {sub: [] for sub in variantes}
    elif cfg.get("carpeta"):
        carpeta = os.path.join(CARPETA, cfg["carpeta"])
        raiz = [] if cfg.get("sin_raiz") else fotos(carpeta)
        if cfg.get("extra_raiz"):
            raiz += fotos(os.path.join(CARPETA, cfg["extra_raiz"]))
        por_variante = {sub: fotos(os.path.join(carpeta, sub)) for sub in variantes}
    else:
        raiz, por_variante = [], {sub: [] for sub in variantes}
    todas = raiz + [p for ps in por_variante.values() for p in ps]
    faltan = [sub for sub, ps in por_variante.items() if not ps]
    if faltan:
        print("  ! %s: subcarpetas sin fotos: %s" % (handle, faltan))

    urls = subir(admin, todas) if admin.apply else {p: "file://" + p for p in todas}
    files = [{"originalSource": urls[p], "alt": alt_de(p), "contentType": "IMAGE"} for p in todas]
    if not files and cfg.get("placeholder"):
        files = [{"originalSource": cfg["placeholder"], "alt": "Próximamente", "contentType": "IMAGE"}]

    inp = {
        # productSet no hace upsert por handle: el existente necesita su id
        "id": existe["id"] if existe else None,
        "handle": handle, "title": titulo, "vendor": VENDOR, "productType": tipo,
        "tags": cfg.get("tags", [TAG]),
        "status": existe["status"] if existe else cfg.get("estado", "DRAFT"),
        "files": files,
    }
    if cfg.get("descripcion"):
        inp["descriptionHtml"] = cfg["descripcion"]
    if not existe:
        del inp["id"]
    tamanos = cfg.get("tamanos", {})
    if opcion:
        inp["productOptions"] = [{"name": opcion, "position": 1,
                                  "values": [{"name": v} for v in variantes.values()]}]
        if tamanos:
            inp["productOptions"].append({"name": "Tamaño", "position": 2,
                                          "values": [{"name": t} for t in tamanos]})
        inp["variants"] = []
        for sub, valor in variantes.items():
            for tam, precio_tam in (tamanos.items() or [(None, None)]):
                v = {"optionValues": [{"optionName": opcion, "name": valor}]}
                if tam:
                    v["optionValues"].append({"optionName": "Tamaño", "name": tam})
                precio = precio_tam or cfg.get("precios", {}).get(valor) or cfg.get("precio")
                if precio:
                    v["price"] = precio
                if por_variante[sub]:
                    p = por_variante[sub][0]
                    v["file"] = {"originalSource": urls[p], "alt": alt_de(p), "contentType": "IMAGE"}
                inp["variants"].append(v)
    else:
        inp["productOptions"] = [{"name": "Title", "position": 1, "values": [{"name": "Default Title"}]}]
        v = {"optionValues": [{"optionName": "Title", "name": "Default Title"}]}
        if cfg.get("precio"):
            v["price"] = cfg["precio"]
        inp["variants"] = [v]

    n_var = len(inp["variants"])
    con_precio = sum(1 for v in inp["variants"] if v.get("price"))
    accion = "actualizar" if existe else "crear"
    res = admin.mutate("%s «%s» (%d fotos, %d variantes, %d con precio)" % (
        accion, titulo, len(todas), n_var, con_precio),
        M_PRODUCT_SET, {"input": inp}, "productSet")
    if res and not existe:
        publicar(admin, res["product"]["id"], "«%s»" % titulo)
    return res


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__),
                             "informe-13-novedades-fotos.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 13 · Fotos y variantes de las novedades", admin)

    if not os.path.isdir(CARPETA):
        sys.exit("no existe %s" % CARPETA)

    q = " OR ".join("handle:%s" % h for h in PRODUCTOS)
    existentes = {p["handle"]: p for p in admin.query(Q_ESTADO, {"q": q})["products"]["nodes"]}
    print("existen ya: %s" % ", ".join(sorted(existentes)) or "ninguno")

    for handle, cfg in PRODUCTOS.items():
        sincronizar(admin, handle, cfg, existentes.get(handle))

    # quitar la «Próximamente» de los existentes, ya con fotos reales
    if admin.apply:
        estado = admin.query(Q_ESTADO, {"q": q})["products"]["nodes"]
        for p in estado:
            reales = [m for m in p["media"]["nodes"] if PLACEHOLDER not in ((m.get("image") or {}).get("url") or "")]
            prov = [m for m in p["media"]["nodes"] if m not in reales]
            if prov and reales:
                admin.mutate("quitar «Próximamente» de «%s» (%s)" % (
                    p["handle"], "; ".join(m["image"]["url"].split("?")[0] for m in prov)),
                    M_DELETE_MEDIA, {"id": p["id"], "media": [m["id"] for m in prov]}, "productDeleteMedia")

    admin.report(args.report)


if __name__ == "__main__":
    main()

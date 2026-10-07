#!/usr/bin/env python3
"""Lote 42 · Traducción de la tienda al inglés (locale `en`, ya publicado).

Fuente: todo lo traducible de Shopify (translatableResources) → traducir_en.traducir()
(glosario + reglas + traducciones/en.json). Registra con translationsRegister.

NO traduce: handles (URLs), nombres de decorado/forma (custom.decorado, custom.forma),
datos técnicos (cartuja.stock, códigos HS, nombres de fichero), plantillas de email y
albarán (ya vienen en inglés de Shopify) ni las cadenas del checkout/cuentas de Shopify
(`shopify.*`, `customer_accounts.*`: Shopify tiene las suyas). No pisa traducciones
existentes que no estén desactualizadas.

Deshacer: translationsRemove por recurso y clave (lista en el informe).

    python3 42_traducir_en.py --pendientes   # vuelca lo que falta en traducciones/pendientes-en.json
    python3 42_traducir_en.py                # ensayo
    python3 42_traducir_en.py --apply        # aplica
"""

import argparse
import collections
import json
import re
from pathlib import Path

from shopify_admin import Admin, add_common_args, banner
from traducir_en import traducir

LOCALE = "en"
TIPOS = [
    "PRODUCT", "PRODUCT_OPTION", "PRODUCT_OPTION_VALUE", "COLLECTION", "COLLECTION_IMAGE", "MEDIA_IMAGE",
    "PAGE", "BLOG", "LINK", "MENU", "FILTER", "DELIVERY_METHOD_DEFINITION", "SHOP_POLICY", "METAFIELD",
    "ONLINE_STORE_THEME", "ONLINE_STORE_THEME_JSON_TEMPLATE", "ONLINE_STORE_THEME_SECTION_GROUP",
    "ONLINE_STORE_THEME_LOCALE_CONTENT", "ONLINE_STORE_THEME_SETTINGS_CATEGORY",
]
METAFIELDS_SI = {"custom.color", "custom.dimensiones", "custom.chapter", "custom.editorial_text", "custom.servicio"}

Q = """query ($t: TranslatableResourceType!, $c: String) {
  translatableResources(first: 250, resourceType: $t, after: $c) {
    pageInfo { hasNextPage endCursor }
    nodes { resourceId
      translatableContent { key value digest type }
      translations(locale: "%s") { key value outdated } } } }""" % LOCALE
Q_MF = "query ($ids: [ID!]!) { nodes(ids: $ids) { ... on Metafield { id namespace key } } }"
M = """
mutation ($id: ID!, $t: [TranslationInput!]!) {
  translationsRegister(resourceId: $id, translations: $t) {
    translations { key }
    userErrors { field message }
  }
}
"""


def saltar(tipo, key, value, mf=None):
    v = str(value or "").strip()
    if not v or key == "handle":
        return True
    if tipo == "METAFIELD" and mf not in METAFIELDS_SI:
        return True
    if tipo.startswith("ONLINE_STORE_THEME") and (key.startswith(("shopify.", "customer_accounts."))
                                                   or re.search(r"\.(many|few|zero)$", key)):
        return True
    if re.fullmatch(r"[\w\-./:]+\.(webp|png|jpe?g|svg|gif|mp4)|https?://\S+|\{.*\}|[\d\s.,]+", v):
        return True
    if re.fullmatch(r"#[0-9a-fA-F]{3,8}|(tel|mailto|shopify|https?):\S+|custom\.\w+|\S+@\S+\.\w+|[a-z0-9_\-]+", v):
        return True                              # colores, enlaces, claves, emails, valores de selector («negro»)
    if all(re.fullmatch(r"[a-z0-9\-]+ \| \d+", l.strip()) for l in v.splitlines()):
        return True                              # listas «handle | cantidad»
    if re.fullmatch(r"/[\w\-/]*|[A-Z][a-z]+/[A-Z][a-z_]+", v):
        return True                              # rutas internas, zona horaria
    if not re.search(r"[A-Za-zÁÉÍÓÚáéíóúÑñ]", v):
        return True
    if tipo == "MEDIA_IMAGE" and (re.fullmatch(r"[\w\-()]+( \(\d+\))?", v) or v.startswith("WhatsApp Image")):
        return True                              # alt que es un nombre de fichero: img4, mug-eden, CartujadeSevilla-2 (2)
    return False


def leer(admin, tipo):
    out, c = [], None
    while True:
        d = admin.query(Q, {"t": tipo, "c": c})["translatableResources"]
        out += d["nodes"]
        if not d["pageInfo"]["hasNextPage"]:
            return out
        c = d["pageInfo"]["endCursor"]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-42-traducir-en.json")
    parser.add_argument("--pendientes", action="store_true")
    args = parser.parse_args()
    admin = Admin(apply=args.apply, strict=False)
    banner("Lote 42 · traducción al inglés", admin)

    pendientes = collections.defaultdict(dict)   # tipo → {texto: nº usos}
    plan = []                                    # (tipo, resourceId, [TranslationInput])
    for tipo in TIPOS:
        res = leer(admin, tipo)
        mf = {}
        if tipo == "METAFIELD":
            ids = [r["resourceId"] for r in res]
            for i in range(0, len(ids), 250):
                for n in admin.query(Q_MF, {"ids": ids[i:i + 250]})["nodes"]:
                    if n:
                        mf[n["id"]] = n["namespace"] + "." + n["key"]
        n_ok = n_falta = 0
        for r in res:
            hechas = {t["key"] for t in r["translations"] if not t["outdated"]}
            lote = []
            for c in r["translatableContent"]:
                if c["key"] in hechas or saltar(tipo, c["key"], c["value"], mf.get(r["resourceId"])):
                    continue
                en = traducir(c["value"])
                if en is None:
                    n_falta += 1
                    for f in (getattr(traducir, "faltan", None) or [c["value"]]):
                        pendientes[tipo][f] = pendientes[tipo].get(f, 0) + 1
                    traducir.faltan = []
                    continue
                if en.strip() == str(c["value"]).strip():
                    continue                     # igual en los dos idiomas (nombres propios)
                n_ok += 1
                lote.append({"locale": LOCALE, "key": c["key"], "value": en,
                             "translatableContentDigest": c["digest"]})
            if lote:
                plan.append((tipo, r["resourceId"], lote))
        print("%-38s recursos %4d · listas %5d · faltan %5d" % (tipo, len(res), n_ok, n_falta))

    total_faltan = sum(len(v) for v in pendientes.values())
    print("\nTextos únicos sin traducción: %d" % total_faltan)
    if args.pendientes:
        p = Path(__file__).with_name("traducciones") / "pendientes-en.json"
        p.write_text(json.dumps(pendientes, ensure_ascii=False, indent=1))
        print("Pendientes en %s" % p)
        return

    if not args.apply:
        print("Ensayo: se registrarían %d traducciones en %d recursos." % (sum(len(l) for _, _, l in plan), len(plan)))
        for tipo, rid, lote in plan[:5]:
            print("  %s %s" % (tipo, rid))
            for t in lote[:3]:
                print("     %s → %s" % (t["key"], t["value"][:100]))
    else:
        # 20 recursos por petición con alias (una llamada al CLI tarda ~3 s; 3.000 sueltas serían horas)
        trozos = [(rid, lote[j:j + 100]) for _, rid, lote in plan for j in range(0, len(lote), 100)]
        ok = mal = 0
        for i in range(0, len(trozos), 20):
            grupo = trozos[i:i + 20]
            cab = ", ".join("$id%d: ID!, $t%d: [TranslationInput!]!" % (n, n) for n in range(len(grupo)))
            cuerpo = " ".join("r%d: translationsRegister(resourceId: $id%d, translations: $t%d) "
                              "{ translations { key } userErrors { field message } }" % (n, n, n) for n in range(len(grupo)))
            variables = {}
            for n, (rid, lote) in enumerate(grupo):
                variables["id%d" % n], variables["t%d" % n] = rid, lote
            res = admin._run("mutation (%s) { %s }" % (cab, cuerpo), variables, mutation=True)
            for n, (rid, lote) in enumerate(grupo):
                body = res.get("r%d" % n) or {}
                if body.get("userErrors"):
                    mal += 1
                    admin.failed.append((rid, body["userErrors"]))
                else:
                    ok += len(lote)
            print("  %d/%d peticiones · %d traducciones · %d recursos con error" % (i // 20 + 1, (len(trozos) + 19) // 20, ok, mal))
        admin.done.append(("registradas", ok))
    admin.done.append(("pendientes", pendientes))
    admin.report(args.report)


if __name__ == "__main__":
    main()

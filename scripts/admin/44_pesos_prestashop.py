#!/usr/bin/env python3
"""Lote 44 · Peso de envío de cada variante, copiado de la tienda antigua (PrestaShop).

Fuente: fichas públicas de lacartujadesevilla.com (2026-10-06), `<meta property="product:weight:value">`
+ `"sku"` del JSON-LD = nuestra referencia de 9 caracteres. Las saca `pesos_prestashop_scrape.py`
a `pesos-prestashop.json` ({sku: {url, kg}}). Antes de este lote todas las variantes pesaban 0 kg,
así que DHL no podía tarificar ni etiquetar bien.

Qué NO hace: inventar pesos. SKU sin ficha o con peso 0 en PrestaShop → listado en el informe
(«sin_peso») para pedirlo al cliente. Variantes sin SKU no se tocan.
Deshacer: el informe guarda el peso anterior de cada variante (era 0).

    python3 44_pesos_prestashop.py           # ensayo
    python3 44_pesos_prestashop.py --apply   # aplica
"""

import argparse
import json
import os

from shopify_admin import Admin, add_common_args, banner

DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pesos-prestashop.json")

Q = """query ($a: String) { productVariants(first: 250, after: $a) {
  pageInfo { hasNextPage endCursor }
  nodes { id sku product { id handle status }
    inventoryItem { measurement { weight { value unit } } } } } }"""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-44-pesos-prestashop.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 44 · pesos de envío desde PrestaShop", admin)

    pesos = {k.lower(): v for k, v in json.load(open(DATOS)).items()}
    variantes, a = [], None
    while True:
        d = admin.query(Q, {"a": a})["productVariants"]
        variantes += d["nodes"]
        if not d["pageInfo"]["hasNextPage"]:
            break
        a = d["pageInfo"]["endCursor"]

    por_producto, antes, sin_peso = {}, [], []
    for v in variantes:
        sku = (v["sku"] or "").strip()
        if not sku:
            continue
        w = v["inventoryItem"]["measurement"]["weight"] or {}
        kg = (pesos.get(sku.lower()) or {}).get("kg")
        if not kg:
            sin_peso.append({"sku": sku, "handle": v["product"]["handle"], "status": v["product"]["status"]})
            continue
        if w.get("value") == kg and w.get("unit") == "KILOGRAMS":
            continue
        antes.append({"id": v["id"], "sku": sku, "antes": w, "kg": kg})
        por_producto.setdefault(v["product"]["id"], []).append(
            {"id": v["id"], "inventoryItem": {"measurement": {"weight": {"value": kg, "unit": "KILOGRAMS"}}}})

    print("Variantes: %d · a cambiar: %d en %d productos · sin peso: %d"
          % (len(variantes), len(antes), len(por_producto), len(sin_peso)))
    for x in antes[:10]:
        print("  %s → %s kg" % (x["sku"], x["kg"]))
    admin.done.append(("antes", antes))
    admin.done.append(("sin_peso", sin_peso))

    if admin.apply:
        # 25 productos por petición con alias (una llamada al CLI tarda ~3 s)
        grupos = list(por_producto.items())
        for i in range(0, len(grupos), 25):
            g = grupos[i:i + 25]
            cab = ", ".join("$p%d: ID!, $v%d: [ProductVariantsBulkInput!]!" % (n, n) for n in range(len(g)))
            cuerpo = " ".join("r%d: productVariantsBulkUpdate(productId: $p%d, variants: $v%d) "
                              "{ userErrors { field message } }" % (n, n, n) for n in range(len(g)))
            variables = {}
            for n, (pid, vs) in enumerate(g):
                variables["p%d" % n], variables["v%d" % n] = pid, vs
            res = admin._run("mutation (%s) { %s }" % (cab, cuerpo), variables, mutation=True)
            for n, (pid, _) in enumerate(g):
                errs = (res.get("r%d" % n) or {}).get("userErrors")
                if errs:
                    admin.failed.append((pid, errs))
            print("  %d/%d peticiones · %d productos con error" % (i // 25 + 1, (len(grupos) + 24) // 25, len(admin.failed)))
    admin.report(args.report)


if __name__ == "__main__":
    main()

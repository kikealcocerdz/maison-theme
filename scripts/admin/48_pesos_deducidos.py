#!/usr/bin/env python3
"""Lote 48 · Peso de las 15 variantes que el lote 44 dejó sin peso, deducido de piezas hermanas.

- Juegos de café (PS los tenía a 0 kg): suma de sus piezas según la metafield `custom.pack`
  (1 cafetera + 1 lechera + 1 azucarero + 6 tazas con platillo), con los pesos ya puestos en Shopify.
- Piezas sueltas sin ficha en PS (Escenas, Yedra): mediana del peso PS de la misma forma+pieza
  (SKU = forma 2 + decorado 3 + pieza 4) en otros decorados.
Pesos DEDUCIDOS, no del cliente: anotados en el informe para que lo confirmen.
Deshacer: poner peso 0 en los ids del informe.

    python3 48_pesos_deducidos.py           # ensayo
    python3 48_pesos_deducidos.py --apply   # aplica
"""
import argparse
import json
import os
import statistics

from shopify_admin import Admin, add_common_args, banner

PESOS_PS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pesos-prestashop.json")))

Q = """query ($a: String) { productVariants(first: 250, after: $a) {
  pageInfo { hasNextPage endCursor }
  nodes { id sku product { id handle } inventoryItem { measurement { weight { value } } }
    pack: metafield(namespace: "custom", key: "pack") { references(first: 20) { nodes { ... on Metaobject {
      fields { key value reference { ... on Product { handle } } } } } } } } } }"""
M = """
mutation ($p: ID!, $v: [ProductVariantsBulkInput!]!) {
  productVariantsBulkUpdate(productId: $p, variants: $v) { userErrors { field message } }
}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-48-pesos-deducidos.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 48 · pesos deducidos de piezas hermanas", admin)

    vs, a = [], None
    while True:
        d = admin.query(Q, {"a": a})["productVariants"]
        vs += d["nodes"]
        if not d["pageInfo"]["hasNextPage"]:
            break
        a = d["pageInfo"]["endCursor"]

    kg = lambda v: (v["inventoryItem"]["measurement"]["weight"] or {}).get("value") or 0
    por_handle = {v["product"]["handle"]: kg(v) for v in vs if kg(v)}  # productos de una variante
    plan = []
    for v in vs:
        sku = (v["sku"] or "").strip()
        if not sku or kg(v):
            continue
        if v["pack"]:
            partes = []
            for n in v["pack"]["references"]["nodes"]:
                f = {x["key"]: (x["reference"] or {}).get("handle") or x["value"] for x in n["fields"]}
                partes.append((f["producto"], int(f["cantidad"]), por_handle.get(f["producto"])))
            if any(p[2] is None for p in partes):
                print("  ✗ %s: pieza sin peso %s" % (sku, [p[0] for p in partes if p[2] is None]))
                continue
            peso, origen = round(sum(c * k for _, c, k in partes), 2), "suma pack: " + ", ".join("%s×%s" % (c, h) for h, c, _ in partes)
        else:
            hermanos = [x["kg"] for s, x in PESOS_PS.items()
                        if x.get("kg") and s[:2].lower() == sku[:2].lower() and s[5:] == sku[5:] and s.lower() != sku.lower()]
            if not hermanos:
                print("  ✗ %s: sin hermanos de forma %s pieza %s" % (sku, sku[:2], sku[5:]))
                continue
            peso, origen = statistics.median(hermanos), "mediana forma %s pieza %s (%d decorados: %s)" % (sku[:2], sku[5:], len(hermanos), sorted(set(hermanos)))
        plan.append({"id": v["id"], "producto": v["product"]["id"], "sku": sku, "handle": v["product"]["handle"], "kg": peso, "origen": origen})
        print("  %-10s %-38s %5.2f kg  ← %s" % (sku, v["product"]["handle"][:38], peso, origen[:90]))

    admin.done.append(("plan", plan))
    for x in plan:
        admin.mutate("peso %s" % x["sku"], M, {"p": x["producto"], "v": [
            {"id": x["id"], "inventoryItem": {"measurement": {"weight": {"value": x["kg"], "unit": "KILOGRAMS"}}}}]},
            "productVariantsBulkUpdate")
    admin.report(args.report)


if __name__ == "__main__":
    main()

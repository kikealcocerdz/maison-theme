#!/usr/bin/env python3
"""Lote 49 · Peso de las variantes ACTIVAS sin SKU (novedades y merchandising).

Fuente (2026-10-06):
  - «PS»: ficha pública de lacartujadesevilla.com buscada por nombre (mugs Edén/Georgica/Ceilán/
    Bellavista 0,4; vaciabolsillos 0,5; mancerina 150 aniversario 3,7; camiseta ancla 0,1; libro
    «Clásicos» 0,66).
  - «estimado»: sin ficha con peso; por analogía con piezas de loza parecidas (azucarero 0,4–0,5,
    bandeja de pastas 0,6, mug 0,4). El cliente debe confirmarlos (el informe los marca).
Los borradores (envoltorio, Áurea, lapicero, jabonera, algodonera, conjunto de baño, bandeja
conmemorativa) no se tocan. Deshacer: peso 0 en los ids del informe.

    python3 49_pesos_sin_sku.py           # ensayo
    python3 49_pesos_sin_sku.py --apply   # aplica
"""
import argparse

from shopify_admin import Admin, add_common_args, banner

# handle → (kg, origen); tarros por talla (opción 2 de la variante)
PESOS = {
    "mug-*": (0.4, "PS"),
    "vaciabolsillos": (0.5, "PS"),
    "mancerina": (3.7, "PS"),
    "camiseta": (0.1, "PS"),
    "libro": (0.66, "PS"),
    "bolsa": (0.2, "estimado: bolsa de tela"),
    "cepillero": (0.4, "estimado: como un mug"),
    "hoja-de-parra": (0.6, "estimado: como bandeja de pastas"),
    "caja-6-posavasos": (0.8, "estimado: 6 posavasos de loza + caja"),
    "vela-aromatica-*": (0.6, "estimado: portavela de loza con tapa + cera"),
}
TARRO = {"Pequeño": 0.5, "Mediano": 0.8, "Grande": 1.2}  # estimado: azucarero 0,4–0,5 → tallas mayores

Q = """query ($a: String) { productVariants(first: 250, after: $a) {
  pageInfo { hasNextPage endCursor }
  nodes { id sku selectedOptions { value } product { id handle status }
    inventoryItem { measurement { weight { value } } } } } }"""
M = """
mutation ($p: ID!, $v: [ProductVariantsBulkInput!]!) {
  productVariantsBulkUpdate(productId: $p, variants: $v) { userErrors { field message } }
}
"""


def peso(v):
    h = v["product"]["handle"]
    if h == "tarro-de-botica":
        talla = v["selectedOptions"][-1]["value"]
        return TARRO.get(talla), "estimado: tarro %s" % talla
    for k, (kg, origen) in PESOS.items():
        if h == k or (k.endswith("*") and h.startswith(k[:-1])):
            return kg, origen
    return None, None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-49-pesos-sin-sku.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 49 · pesos de variantes activas sin SKU", admin)

    vs, a = [], None
    while True:
        d = admin.query(Q, {"a": a})["productVariants"]
        vs += d["nodes"]
        if not d["pageInfo"]["hasNextPage"]:
            break
        a = d["pageInfo"]["endCursor"]

    por_producto, plan, sin = {}, [], []
    for v in vs:
        if v["sku"] or v["product"]["status"] != "ACTIVE" or (v["inventoryItem"]["measurement"]["weight"] or {}).get("value"):
            continue
        kg, origen = peso(v)
        if kg is None:
            sin.append(v["product"]["handle"])
            continue
        plan.append({"id": v["id"], "handle": v["product"]["handle"], "opciones": [o["value"] for o in v["selectedOptions"]], "kg": kg, "origen": origen})
        por_producto.setdefault(v["product"]["id"], []).append(
            {"id": v["id"], "inventoryItem": {"measurement": {"weight": {"value": kg, "unit": "KILOGRAMS"}}}})
    for x in plan:
        print("  %-30s %-22s %4.2f kg  %s" % (x["handle"], "/".join(x["opciones"])[:22], x["kg"], x["origen"]))
    print("Variantes: %d · productos: %d · sin regla: %s" % (len(plan), len(por_producto), sin))
    admin.done.append(("plan", plan))
    for pid, variantes in por_producto.items():
        admin.mutate("peso %s" % pid.split("/")[-1], M, {"p": pid, "v": variantes}, "productVariantsBulkUpdate")
    admin.report(args.report)


if __name__ == "__main__":
    main()

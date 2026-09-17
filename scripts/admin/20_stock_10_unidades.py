#!/usr/bin/env python3
"""Lote 20 · Suma 10 unidades a todas las variantes con seguimiento de stock, en su
ubicación, para que nada salga «Agotado».

Las variantes sin seguimiento (`tracked: false`) ya se venden siempre; se saltan.
Requiere scopes `read_locations`, `read_inventory`, `write_inventory`.

    python3 20_stock_10_unidades.py            # ensayo
    python3 20_stock_10_unidades.py --apply
    python3 20_stock_10_unidades.py --delta 25 --apply
"""

import argparse
import uuid

from shopify_admin import Admin, add_common_args, banner

Q_VARS = """
query ($cursor: String) {
  productVariants(first: 250, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes { id title product { title } inventoryQuantity
      inventoryItem { id tracked inventoryLevels(first: 1) { nodes { location { id name } quantities(names: ["available"]) { quantity } } } } }
  }
}
"""

M = """
mutation ($input: InventoryAdjustQuantitiesInput!, $key: String!) {
  inventoryAdjustQuantities(input: $input) @idempotent(key: $key) {
    inventoryAdjustmentGroup { changes { name delta quantityAfterChange } }
    userErrors { field message }
  }
}
"""


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__), "informe-20-stock.json")
    parser.add_argument("--delta", type=int, default=10)
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 20 · +%d unidades en todo el catálogo" % args.delta, admin)

    items, cursor = [], None
    while True:
        page = admin.query(Q_VARS, {"cursor": cursor})["productVariants"]
        for v in page["nodes"]:
            lv = v["inventoryItem"]["inventoryLevels"]["nodes"]
            if v["inventoryItem"]["tracked"] and lv:
                # cada artículo se ajusta en la ubicación donde está dado de alta (hay dos)
                v["loc"], v["qty"] = lv[0]["location"], lv[0]["quantities"][0]["quantity"]
                items.append(v)
                print("  %s · %s @ %s: %s → %s" % (v["product"]["title"], v["title"], v["loc"]["name"],
                                                  v["qty"], v["qty"] + args.delta))
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    print("variantes con seguimiento: %d" % len(items))

    # ponytail: 250 cambios por mutación (límite de la API)
    for i in range(0, len(items), 250):
        lote = items[i:i + 250]
        admin.mutate("+%d en %d variantes (lote %d)" % (args.delta, len(lote), i // 250 + 1), M, {"input": {
            "reason": "correction", "name": "available",
            "changes": [{"inventoryItemId": v["inventoryItem"]["id"], "locationId": v["loc"]["id"], "delta": args.delta,
                         "changeFromQuantity": v["qty"]}  # la API exige el stock previo
                        for v in lote],
        }, "key": "stock-20-%s-%d" % (uuid.uuid4(), i)}, "inventoryAdjustQuantities")
    admin.report(args.report)


if __name__ == "__main__":
    main()

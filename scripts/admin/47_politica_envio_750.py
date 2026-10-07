#!/usr/bin/env python3
"""Lote 47 · Política de envíos: «6,99 €» → «7,50 €» (Península, tarifa MRW del lote 45).

Solo sustituye esa cifra; el resto del texto intacto. Deshacer: el informe guarda el body anterior.

    python3 47_politica_envio_750.py           # ensayo
    python3 47_politica_envio_750.py --apply   # aplica
"""
import argparse

from shopify_admin import Admin, add_common_args, banner

Q = '{ shop { shopPolicies { type body } } }'
M = """
mutation ($p: ShopPolicyInput!) {
  shopPolicyUpdate(shopPolicy: $p) { shopPolicy { type } userErrors { field message } }
}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-47-politica-envio.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 47 · política de envíos 7,50 €", admin)
    body = next(p["body"] for p in admin.query(Q)["shop"]["shopPolicies"] if p["type"] == "SHIPPING_POLICY")
    admin.done.append(("antes", body))
    assert body.count("6,99 €") == 1, "esperaba una sola aparición de 6,99 €"
    admin.mutate("política envíos", M, {"p": {"type": "SHIPPING_POLICY", "body": body.replace("6,99 €", "7,50 €")}}, "shopPolicyUpdate")
    admin.report(args.report)


if __name__ == "__main__":
    main()

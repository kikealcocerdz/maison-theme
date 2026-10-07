#!/usr/bin/env python3
"""Lote 46 · Código arancelario 691200 + origen ES en las variantes de cerámica que no lo tenían.

Fuente: las 444 variantes que ya lo tenían usan 691200 / ES (vajilla de loza, fábrica de Salteras).
Necesario para envíos DHL fuera de la UE (aduanas). Solo tipos de cerámica (lista CERAMICA).
Qué NO hace: velas, bolsa, camiseta, libro, posavasos y «Decoración» → informe «sin_tocar» para
que el cliente confirme material/código. No pisa códigos existentes.
Deshacer: poner harmonizedSystemCode/countryCodeOfOrigin a null en los ids del informe.

    python3 46_aduanas_ceramica.py           # ensayo
    python3 46_aduanas_ceramica.py --apply   # aplica
"""

import argparse

from shopify_admin import Admin, add_common_args, banner

HS, ORIGEN = "691200", "ES"
CERAMICA = {"Mug", "Tarro", "Plato", "Cafetera", "Taza", "Lechera", "Fuente", "Salsera", "Vaciabolsillo",
            "Platillo", "Sopera", "Tetera", "Azucarero", "Ensaladera", "Bajoplato", "Bandeja", "Mancerina", "Cepillero"}

Q = """query ($a: String) { productVariants(first: 250, after: $a) {
  pageInfo { hasNextPage endCursor }
  nodes { sku product { title productType } inventoryItem { id harmonizedSystemCode countryCodeOfOrigin } } } }"""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-46-aduanas-ceramica.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 46 · HS 691200 / ES en cerámica sin código", admin)

    vs, a = [], None
    while True:
        d = admin.query(Q, {"a": a})["productVariants"]
        vs += d["nodes"]
        if not d["pageInfo"]["hasNextPage"]:
            break
        a = d["pageInfo"]["endCursor"]

    faltan = [v for v in vs if not v["inventoryItem"]["harmonizedSystemCode"]]
    poner = [v for v in faltan if v["product"]["productType"] in CERAMICA]
    sin_tocar = [{"sku": v["sku"], "titulo": v["product"]["title"], "tipo": v["product"]["productType"]}
                 for v in faltan if v not in poner]
    print("Sin código: %d · se ponen: %d · sin tocar: %d" % (len(faltan), len(poner), len(sin_tocar)))
    for x in sin_tocar:
        print("  sin tocar: %s (%s)" % (x["titulo"], x["tipo"]))
    admin.done.append(("ids", [v["inventoryItem"]["id"] for v in poner]))
    admin.done.append(("sin_tocar", sin_tocar))

    if admin.apply:
        for i in range(0, len(poner), 25):
            g = poner[i:i + 25]
            cab = ", ".join("$i%d: ID!" % n for n in range(len(g)))
            cuerpo = " ".join("r%d: inventoryItemUpdate(id: $i%d, input: {harmonizedSystemCode: \"%s\", countryCodeOfOrigin: %s}) "
                              "{ userErrors { field message } }" % (n, n, HS, ORIGEN) for n in range(len(g)))
            res = admin._run("mutation (%s) { %s }" % (cab, cuerpo), {"i%d" % n: v["inventoryItem"]["id"] for n, v in enumerate(g)}, mutation=True)
            for n, v in enumerate(g):
                errs = (res.get("r%d" % n) or {}).get("userErrors")
                if errs:
                    admin.failed.append((v["sku"], errs))
            print("  %d/%d · errores %d" % (i // 25 + 1, (len(poner) + 24) // 25, len(admin.failed)))
    admin.report(args.report)


if __name__ == "__main__":
    main()

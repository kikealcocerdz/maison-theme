#!/usr/bin/env python3
"""Lote 50 · Envío a Canarias, Ceuta y Melilla SIN IVA.

Correo Isabel 24/08: «La tarifa para Canarias, Ceuta y Melilla sería misma tarifa pero sin IVA».
El lote 45 les puso la tabla MRW ×1,21 como a Baleares (E2E 2026-10-08: 1 bol → 29,98 € en vez de 24,78 €).
Recalcula cada tramo de la zona con `mrw_islas` del lote 45 pero sin IVA y actualiza solo los precios
(mismos métodos y condiciones de peso). Deshacer: el informe guarda la zona anterior.

    python3 50_canarias_sin_iva.py           # ensayo
    python3 50_canarias_sin_iva.py --apply   # aplica
"""

import argparse
import importlib.util
import os

from shopify_admin import Admin, add_common_args, banner

_spec = importlib.util.spec_from_file_location("lote45", os.path.join(os.path.dirname(os.path.abspath(__file__)), "45_tarifas_envio_prestashop.py"))
L45 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L45)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-50-canarias-sin-iva.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 50 · Canarias, Ceuta y Melilla sin IVA", admin)

    antes = admin.query(L45.Q)
    zona = next(z for g in antes["deliveryProfile"]["profileLocationGroups"] for z in g["locationGroupZones"]["nodes"]
                if z["zone"]["id"] == L45.Z_CANARIAS)
    admin.done.append(("antes", zona))

    L45.IVA = 1.0  # ponytail: reutiliza la tabla del lote 45 tal cual, solo sin el ×1,21
    nuevos = {m["weightConditionsToCreate"][0]["criteria"]["value"]: m["rateDefinition"]["price"]["amount"]
              for m in L45.mrw_islas("Canarias, Ceuta y Melilla", 1.92)}

    cambios = []
    for m in zona["methodDefinitions"]["nodes"]:
        desde = next(float(c["conditionCriteria"]["value"]) for c in m["methodConditions"] if c["operator"] == "GREATER_THAN_OR_EQUAL_TO")
        nuevo = nuevos.get(int(desde) if desde == int(desde) else desde)
        assert nuevo is not None, "tramo sin equivalente: desde %s kg" % desde
        viejo = float(m["rateProvider"]["price"]["amount"])
        print("desde %5s kg: %7.2f € → %7.2f €" % (desde, viejo, nuevo))
        cambios.append({"id": m["id"], "rateDefinition": {"price": {"amount": nuevo, "currencyCode": "EUR"}}})
    assert len(cambios) == len(nuevos), "la zona tiene %d tramos y la tabla %d" % (len(cambios), len(nuevos))

    admin.mutate("Canarias: %d tramos sin IVA" % len(cambios), L45.M, {"id": L45.PERFIL, "p": {"locationGroupsToUpdate": [
        {"id": L45.GRUPO, "zonesToUpdate": [{"id": L45.Z_CANARIAS, "methodDefinitionsToUpdate": cambios}]}]}}, "deliveryProfileUpdate")
    admin.report(args.report)


if __name__ == "__main__":
    main()

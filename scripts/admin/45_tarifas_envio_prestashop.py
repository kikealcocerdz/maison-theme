#!/usr/bin/env python3
"""Lote 45 · Tarifas de envío por peso copiadas de PrestaShop (MRW nacional/Portugal, DHL internacional).

Fuente: admin PrestaShop leído 2026-10-06 → `tarifas-prestashop.json` (tablas de Clearis). Decisión del
usuario 2026-10-06: copiar exacto, IGNORAR «gastos de manipulación» 75 €, quitar BH/CN/KW/OM/QA/SG
(no activos en PrestaShop, sin zona DHL). Correo Isabel 29/09: nacional+Portugal = MRW, internacional = DHL.

Importes: MRW en PS van sin IVA con regla ES 21 % → aquí ×1,21 (la tienda incluye IVA en el envío).
Kg extra Baleares/Canarias (regla PS sin IVA): +1,53 / +1,92 € por kg sobre 10 kg; tramos de 2 kg hasta
50 y de 10 kg hasta 100, cobrados al límite superior del tramo. DHL tal cual (fuera de ES no lleva IVA PS).
DHL Worldwide >70 kg: sin tarifa (PS «desactivar transportista»). DHL UE y MRW >último tramo: el más alto.

Qué hace (perfil «Perfil general»):
  1. borra zonas «UE (Unión Europea)» e «Internacional» (+ sus métodos, incl. «DHL Commerce» inactivo)
     y los métodos «Estándar (provisional)» de Baleares y Canarias; Península «Estándar» 6,99 → 7,50
     (sigue «Envío gratuito» ≥150 €; «DHL Commerce» inactivo de Península no se toca);
  2. crea tramos MRW en Baleares y Canarias, zona Portugal y 8 zonas DHL.
Qué NO hace: Markets (Golfo y Asia sigue listando países sin envío), MRW sin integración de etiquetas.
Deshacer: el informe guarda el perfil entero anterior (zonas, países, métodos, condiciones).

    python3 45_tarifas_envio_prestashop.py           # ensayo
    python3 45_tarifas_envio_prestashop.py --apply   # aplica
"""

import argparse
import json
import os

from shopify_admin import Admin, add_common_args, banner

PERFIL = "gid://shopify/DeliveryProfile/142776664405"
GRUPO = "gid://shopify/DeliveryLocationGroup/144875028821"
Z_BALEARES = "gid://shopify/DeliveryZone/709304385877"
Z_CANARIAS = "gid://shopify/DeliveryZone/709304353109"
Z_BORRAR = ["gid://shopify/DeliveryZone/691715178837", "gid://shopify/DeliveryZone/691715146069"]
M_BORRAR = ["gid://shopify/DeliveryMethodDefinition/1416507097429", "gid://shopify/DeliveryMethodDefinition/1416507064661"]
M_PENINSULA = "gid://shopify/DeliveryMethodDefinition/1416506999125"
IVA = 1.21

T = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tarifas-prestashop.json")))
PAISES = T["paises_activos_por_zona"]

Q = """{ deliveryProfile(id: "%s") { profileLocationGroups { locationGroupZones(first: 30) { nodes {
  zone { id name countries { code { countryCode } provinces { code } } }
  methodDefinitions(first: 40) { nodes { id name active description
    rateProvider { __typename ... on DeliveryRateDefinition { price { amount } }
      ... on DeliveryParticipant { carrierService { id name } } }
    methodConditions { field operator conditionCriteria { __typename ... on Weight { value unit } ... on MoneyV2 { amount } } } } } } } } } }""" % PERFIL
M = """
mutation ($id: ID!, $p: DeliveryProfileInput!) {
  deliveryProfileUpdate(id: $id, profile: $p) { profile { id } userErrors { field message } }
}
"""


def metodo(nombre, precio, desde, hasta=None):
    conds = [{"criteria": {"value": desde, "unit": "KILOGRAMS"}, "operator": "GREATER_THAN_OR_EQUAL_TO"}]
    if hasta is not None:  # tramos [desde, hasta): el borde va al tramo siguiente
        conds.append({"criteria": {"value": round(hasta - 0.001, 3), "unit": "KILOGRAMS"}, "operator": "LESS_THAN_OR_EQUAL_TO"})
    return {"name": nombre, "active": True, "rateDefinition": {"price": {"amount": round(precio, 2), "currencyCode": "EUR"}},
            "weightConditionsToCreate": conds}


def tabla(nombre, rangos, precios, factor=1.0, abierto=True):
    """Un método por tramo; si `abierto`, el último sigue sin tope (= «coste más alto» de PS)."""
    out = []
    for i, ((a, b), p) in enumerate(zip(rangos, precios)):
        ultimo = i == len(rangos) - 1
        out.append(metodo(nombre, p * factor, a, None if (ultimo and abierto) else b))
    return out


def mrw_islas(fila, extra_kg):
    r = T["MRW"]["rangos_kg"]
    base = [p * IVA for p in T["MRW"][fila]]
    # tramos iguales seguidos de PS (0-1,1-2,2-3 al mismo precio) → uno solo
    tramos = []
    for (a, b), p in zip(r, base):
        if tramos and round(tramos[-1][2], 2) == round(p, 2):
            tramos[-1][1] = b
        else:
            tramos.append([a, b, p])
    out = [metodo("Estándar", p, a, b) for a, b, p in tramos]
    top = base[-1]
    cortes = list(range(10, 50, 2)) + list(range(50, 100, 10))
    for a in cortes:
        b = a + (2 if a < 50 else 10)
        out.append(metodo("Estándar", top + extra_kg * (b - 10), a, b))
    out.append(metodo("Estándar", top + extra_kg * 90, 100))
    return out


def zona(nombre, paises, metodos):
    return {"name": nombre, "countries": [{"code": c, "includeAllProvinces": True} for c in paises],
            "methodDefinitionsToCreate": metodos}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, "informe-45-tarifas-envio.json")
    args = parser.parse_args()
    admin = Admin(apply=args.apply)
    banner("Lote 45 · tarifas de envío PrestaShop → Shopify", admin)

    antes = admin.query(Q)
    admin.done.append(("antes", antes))

    paso1 = {"zonesToDelete": Z_BORRAR, "methodDefinitionsToDelete": M_BORRAR,
             "locationGroupsToUpdate": [{"id": GRUPO, "zonesToUpdate": [
                 {"id": Z_BALEARES, "methodDefinitionsToCreate": mrw_islas("Balears", 1.53)},
                 {"id": Z_CANARIAS, "methodDefinitionsToCreate": mrw_islas("Canarias, Ceuta y Melilla", 1.92)},
             ]}]}
    # Península: solo el precio del método existente (conserva su condición de importe < 150 €)
    pen = next(m for g in antes["deliveryProfile"]["profileLocationGroups"] for z in g["locationGroupZones"]["nodes"]
               for m in z["methodDefinitions"]["nodes"] if m["id"] == M_PENINSULA)
    paso1["locationGroupsToUpdate"][0]["zonesToUpdate"].append(
        {"id": "gid://shopify/DeliveryZone/691715113301", "methodDefinitionsToUpdate": [
            {"id": M_PENINSULA, "rateDefinition": {"price": {"amount": round(T["MRW"]["Peninsula"][0] * IVA, 2), "currencyCode": "EUR"}}}]})
    print("Península «%s» %s € → %.2f €" % (pen["name"], pen["rateProvider"]["price"]["amount"], T["MRW"]["Peninsula"][0] * IVA))

    ww, ue, mrw = T["DHL_EXPRESS_Worldwide"], T["DHL_Express_UE"], T["MRW"]
    nuevas = [
        zona("Portugal", PAISES["Portugal"], [metodo("Estándar", mrw["Portugal"][0] * IVA, 0, 5),
                                              metodo("Estándar", mrw["Portugal"][5] * IVA, 5)]),
        zona("UE · Francia e Italia", ["FR", "IT"], tabla("DHL Express", ue["rangos_kg"], ue["DHL EU Zona 2"])),
        zona("UE · Alemania y Benelux", PAISES["DHL EU Zona 3"], tabla("DHL Express", ue["rangos_kg"], ue["DHL EU Zona 3"])),
        zona("UE · Resto", PAISES["DHL EU Zona 4"], tabla("DHL Express", ue["rangos_kg"], ue["DHL EU Zona 4"])),
        zona("Reino Unido", ["GB"], tabla("DHL Express", ww["rangos_kg"], ww["DHL Zona 3"], abierto=False)),
        zona("Estados Unidos y Canadá", ["US", "CA"], tabla("DHL Express", ww["rangos_kg"], ww["DHL Zona 7"], abierto=False)),
        zona("Arabia Saudí y Emiratos", ["SA", "AE"], tabla("DHL Express", ww["rangos_kg"], ww["DHL Zona 8"], abierto=False)),
        zona("Chile", ["CL"], tabla("DHL Express", ww["rangos_kg"], ww["DHL Zona 9"], abierto=False)),
        zona("Australia", ["AU"], tabla("DHL Express", ww["rangos_kg"], ww["DHL Zona 10"], abierto=False)),
    ]
    paso2 = {"locationGroupsToUpdate": [{"id": GRUPO, "zonesToCreate": nuevas}]}

    for z in paso1["locationGroupsToUpdate"][0]["zonesToUpdate"][:2] + nuevas:
        ms = z["methodDefinitionsToCreate"]
        print("%-28s %2d tramos: %s" % (z.get("name") or z["id"][-12:], len(ms),
              " · ".join("%s+%s€" % (m["weightConditionsToCreate"][0]["criteria"]["value"], m["rateDefinition"]["price"]["amount"]) for m in ms[:6])))

    admin.mutate("paso 1 · borrar UE/Internacional + provisionales, tramos islas, Península 7,50", M, {"id": PERFIL, "p": paso1}, "deliveryProfileUpdate")
    admin.mutate("paso 2 · crear Portugal + 8 zonas DHL", M, {"id": PERFIL, "p": paso2}, "deliveryProfileUpdate")
    if admin.apply:
        admin.done.append(("después", admin.query(Q)))
    admin.report(args.report)


if __name__ == "__main__":
    main()

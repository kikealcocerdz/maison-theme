"""Traducción ES → EN de La Cartuja: glosario + reglas + memoria (traducciones/en.json).

`traducir(texto)` devuelve el inglés o None si no hay traducción. Orden:
  1. memoria exacta (traducciones/en.json: {"español": "inglés"}),
  2. reglas: título de producto (decorado + pieza), frase inicial de las fichas,
     medidas, opciones («15 P.»), tipos de producto,
  3. HTML: se traduce bloque a bloque (<p>, <li>, <h*>…) con 1 y 2; si falta un
     bloque, None (nunca se publica un texto a medio traducir).

Nombres de decorado y forma (Aurora, Bellavista, 202 Rosa, N. Vistas Azul A. Stewart…)
no se traducen: son nombres de colección. Orden inglés: «Ceilán Dinner Plate».
"""

import html
import json
import re
import unicodedata
from pathlib import Path

MEMORIA = Path(__file__).with_name("traducciones") / "en.json"

# pieza (como aparece en el título) → inglés. Se prueba de la más larga a la más corta.
PIEZAS = {
    "Azucarero": "Sugar Bowl",
    "Bol": "Bowl",
    "Juego Café 15 P.": "15-piece Coffee Set",
    "Juego Té 15 P.": "15-piece Tea Set",
    "Bajoplato": "Charger Plate",
    "Bandeja Pastas": "Pastry Tray",
    "Bol Grande": "Large Bowl",
    "Bol Mini": "Mini Bowl",
    "Bol Pequeño": "Small Bowl",
    "Bol Peq.": "Small Bowl",
    "Bombonera": "Bonbon Dish",
    "Cafetera": "Coffee Pot",
    "Champanera": "Champagne Bucket",
    "Ensaladera": "Salad Bowl",
    "Fuente Gra.": "Large Platter",
    "Fuente Med.": "Medium Platter",
    "Fuente Mini": "Mini Platter",
    "Fuente Peq.": "Small Platter",
    "Fuente Red.": "Round Platter",
    "Fuente Redonda": "Round Platter",
    "Juego Boles 6 P.": "Set of 6 Bowls",
    "Juego Boles Mini 6 P.": "Set of 6 Mini Bowls",
    "Juego Café": "Coffee Set",
    "Juego Té": "Tea Set",
    "Lechera": "Milk Jug",
    "Mug": "Mug",
    "Platillo Consomé": "Consommé Saucer",
    "Platillo Consomé/Desayuno": "Consommé/Breakfast Saucer",
    "Plato Hondo": "Soup Plate",
    "Plato Llano": "Dinner Plate",
    "Plato Llano 28 Cm.": "28 cm Dinner Plate",
    "Plato Llano 28Cm.": "28 cm Dinner Plate",
    "Plato Pan": "Bread Plate",
    "Plato Pastas": "Cake Plate",
    "Plato Postre": "Dessert Plate",
    "Salsera": "Gravy Boat",
    "Sopera": "Soup Tureen",
    "Taza Café Con Platillo": "Coffee Cup and Saucer",
    "Taza Consomé": "Consommé Cup",
    "Taza Consomé Con Platillo": "Consommé Cup and Saucer",
    "Taza Desayuno": "Breakfast Cup",
    "Taza Desayuno Con Platillo": "Breakfast Cup and Saucer",
    "Taza Té Con Platillo": "Teacup and Saucer",
    "Tetera": "Teapot",
    "Vajilla": "Dinner Service",
    "Vela aromática": "Scented Candle",
}
# lo que va detrás de la pieza y sí se traduce (el resto son nombres propios)
DECORADO_EN = {"Blanco": "White"}

# tipo de producto (filtros, product_type)
TIPOS = {
    "Azucarero": "Sugar Bowl", "Bajoplato": "Charger Plate", "Bandeja": "Tray", "Bol": "Bowl",
    "Bombonera": "Bonbon Dish", "Cabeza": "Head", "Cafetera": "Coffee Pot", "Champanera": "Champagne Bucket",
    "Ensaladera": "Salad Bowl", "Florero": "Vase", "Fuente": "Platter", "Jarro": "Jug", "Juego": "Set",
    "Lechera": "Milk Jug", "Mug": "Mug", "Palangana": "Basin", "Platillo": "Saucer", "Plato": "Plate",
    "Salsera": "Gravy Boat", "Sopera": "Soup Tureen", "Taza": "Cup", "Tetera": "Teapot",
    "Vajilla": "Dinner Service", "Servicio": "Service", "Áurea": "Áurea", "Lapicero": "Pen Holder",
    "Posavasos": "Coasters", "Vaciabolsillo": "Catchall Tray", "Tarro": "Jar", "Decoración": "Decoration",
    "Mancerina": "Mancerina", "Cepillero": "Toothbrush Holder", "Bolsa": "Bag", "Camiseta": "T-shirt",
    "Libro": "Book", "Jabonera": "Soap Dish", "Algodonera": "Cotton Jar", "Conjunto de baño": "Bathroom Set",
    "Vela": "Candle",
}

_memoria = None


def _norm(s):
    """NFC + espacios de no separación → espacio normal (para comparar con la memoria)."""
    return unicodedata.normalize("NFC", s).replace("\u00a0", " ").replace("\u202f", " ")


def memoria():
    global _memoria
    if _memoria is None:
        crudo = json.loads(MEMORIA.read_text()) if MEMORIA.exists() else {}
        _memoria = {_norm(k): v for k, v in crudo.items()}
    return _memoria


def _decimal(s):
    """22,5 → 22.5 (sólo comas entre dígitos)."""
    return re.sub(r"(\d),(\d)", r"\1.\2", s)


def titulo(t):
    t = t.strip()
    m = re.fullmatch(r"(Vajilla|Juego Café|Juego Té) (\d+) P\. (.+)", t)     # «Vajilla 56 P. 202 Rosa»
    if m:
        pieza = {"Vajilla": "Dinner Service", "Juego Café": "Coffee Set", "Juego Té": "Tea Set"}[m.group(1)]
        return "%s %s-piece %s" % (DECORADO_EN.get(m.group(3), m.group(3)), m.group(2), pieza)
    # sólo textos con forma de título: nada de frases («Azucarero colección X. Pieza fabricada…»)
    if len(t) > 70 or "." in t.replace("Gra.", "").replace("Med.", "").replace("Peq.", "").replace("Red.", "").replace("P.", "").replace("Cm.", "").replace("N. ", "").replace("A. ", "") \
            or re.search(r"\b(colecci[óo]n|fabricad[ao]|de color)\b", t, re.I):
        return None
    for pieza in sorted(PIEZAS, key=len, reverse=True):
        if t == pieza:
            return PIEZAS[pieza]
        if t.startswith(pieza + " "):
            resto = t[len(pieza) + 1:].strip()
            if pieza == "Mug" and re.fullmatch(r"[Ll]etra \w", resto):
                return "Letter Mug " + resto[-1]
            if resto[:1].islower():
                return None                                       # «Mug con letra · …» no es «pieza + decorado»
            resto = DECORADO_EN.get(resto, resto)
            return "%s %s" % (resto, PIEZAS[pieza])
    return None


R_INTRO = re.compile(r"^(?P<pieza>.+?) colecci[óo]n (?P<col>.+?)\. Fabricad[ao] a mano con loza fina en Espa[ñn]a\.?$")
# 2ª plantilla: «Plato hondo colección Aurora Blanca. Pieza fabricada a mano con loza fina en España.»
R_INTRO2 = re.compile(r"^(?P<pieza>.+?) (?:de la )?[Cc]olecci[óo]n (?P<col>.+?)\. Piezas? [Ff]abricadas? (?:a mano )?con loza fina en Espa[ñn]a\.?$")
# pieza tal como se escribe en la frase (en minúscula)
PIEZAS_FRASE = {
    "bajo-plato": "Charger plate", "bandeja de pastas": "Pastry tray", "bandeja pastas": "Pastry tray",
    "bol clásico grande": "Classic large bowl", "bol clásico pequeño": "Classic small bowl",
    "bol clásico mini": "Classic mini bowl", "cubitera": "Ice bucket",
    "fuente grande": "Large platter", "fuente mediana": "Medium platter", "fuente pequeña": "Small platter",
    "fuente pequeño": "Small platter", "fuente mini": "Mini platter", "fuente redonda": "Round platter",
    "plato de pan": "Bread plate", "platillo de pan": "Bread plate", "plato de pastas": "Cake plate",
    "plato de postre": "Dessert plate", "plato postre": "Dessert plate", "plato hondo": "Soup plate",
    "plato llano": "Dinner plate", "palto llano": "Dinner plate", "plato llano 28 cm": "28 cm dinner plate",
    "taza de consomé": "Consommé cup", "taza de desayuno": "Breakfast cup",
    "platillo consomé o desayuno": "Consommé/breakfast saucer",
    "platillo de consomé o desayuno": "Consommé/breakfast saucer",
    "plato llano de 28 cm": "28 cm dinner plate",
    "vajilla completa de 42 piezas": "Complete 42-piece dinner service",
}
ERRATAS = {"Belllavista": "Bellavista", "Yeloow": "Yellow", "by aaron": "by Aaron"}
DECORADOS = ["202 Rosa", "Aurora Blanca", "Azahar", "Azahar Nuevo", "Basic Line Red", "Bellavista", "Ceilán", "Escenas",
             "Flor de Lis Azul", "Flor de Lis Rosa", "Infanta Luisa", "Kensington", "María Cristina", "Negro Vistas",
             "Oaxaca", "Ochavada Blanca", "Paraíso Azul", "Viejo Molino", "Yedra"]


# textos alternativos de imagen escritos sin tildes / con guiones
NORMALIZA = [("Consome", "Consomé"), ("Cafe ", "Café "), (" Te ", " Té "), ("Ceilan", "Ceilán"),
             ("Flor De Lis", "Flor de Lis"), ("Flor Lis", "Flor de Lis"), ("Platilloochavado", "Platillo Ochavado"),
             ("A.Stewart", "A. Stewart"), ("N.Vistas", "N. Vistas"), ("Gra.N.", "Gra. N."), ("Vajilla-", "Vajilla ")]
SUFIJO = " — La Cartuja de Sevilla"


def regla(t):
    s = t.strip()
    if not s:
        return s
    if s.endswith(SUFIJO) and len(s) > len(SUFIJO):
        cabeza = s[:-len(SUFIJO)]
        en = regla(cabeza)
        return (en or cabeza.replace("-", " ")) + SUFIJO
    norm = s
    for mal, bien in NORMALIZA:
        norm = norm.replace(mal, bien)
    if norm != s:
        return regla(norm) or titulo(norm)
    if s in TIPOS:
        return TIPOS[s]
    m = re.fullmatch(r"(\d+) [Pp]\.", s)                      # opción «15 P.»
    if m:
        return "%s pcs" % m.group(1)
    m = re.fullmatch(r"[Mm]edidas?:?\s*(.+)", s)              # «Medidas: 16,5 x 11,5 x 12 cm.», «Medidas:16,5 cm diámetro.»
    if m and re.fullmatch(r"[\d\s.,x;:cmlL]*(diámetro|alto|di[áa]metro|[\d\s.,x;cmlL])*", m.group(1)):
        v = _decimal(m.group(1)).replace("diámetro", "diameter").replace("alto", "high").replace(";", ",")
        return "Dimensions: " + re.sub(r"\s+", " ", re.sub(r"x(\d)", r"x \1", v)).strip()
    if re.fullmatch(r"[\d.,]+( x [\d.,]+)*\s*cm\.?", s):      # metafield dimensiones
        return _decimal(s)
    m = R_INTRO2.match(s)
    if m and re.search(r"\b(de color|diseñad[oa])\b", m.group("col")):
        m = None                                                  # frase especial: va a la memoria
    if m:
        col = m.group("col")
        for mal, bien in ERRATAS.items():
            col = col.replace(mal, bien)
        letra = re.fullmatch(r"Alfabeto Letra (\w)", col)
        if letra and m.group("pieza") == "Mug":
            return "Alphabet mug, letter %s. Handmade in fine earthenware in Spain." % letra.group(1)
        pz = m.group("pieza")
        sin = lambda x: unicodedata.normalize("NFD", x).encode("ascii", "ignore").decode().lower()
        if sin(pz).endswith(" " + sin(col)):                      # «Cafetera Escenas colección Escenas»
            pz = pz[:-len(col) - 1]
        else:                                                     # «Fuente Gra. Maria Cristina colección …»
            for d in sorted(DECORADOS, key=len, reverse=True):
                if sin(pz).endswith(" " + sin(d)):
                    pz = pz[:-len(d) - 1]
                    break
        en_pz = PIEZAS_FRASE.get(pz.lower()) or next((v for k, v in PIEZAS.items() if k.lower() == pz.lower()), None)
        if en_pz:
            return "%s from the %s collection. Handmade in fine earthenware in Spain." % (en_pz[0] + en_pz[1:].lower(), col)
    m = R_INTRO.match(s)                                       # frase inicial de las fichas
    if m and re.fullmatch(r"Alfabeto Letra (\w)", m.group("col")):
        return "Alphabet mug, letter %s. Handmade in fine earthenware in Spain." % m.group("col")[-1]
    if m:
        pieza = titulo(m.group("pieza")) or PIEZAS.get(m.group("pieza"))
        if pieza:
            return "%s from the %s collection. Handmade in fine earthenware in Spain." % (pieza[0] + pieza[1:].lower(), m.group("col"))
    return titulo(s)


def _traducible(t):
    """Trozo con palabras que traducir (no URL, email, teléfono, número ni espacio)."""
    t = html.unescape(t).strip()
    if not t or not re.search(r"[A-Za-zÁÉÍÓÚáéíóúÑñ]{2}", t):
        return False
    return not re.fullmatch(r"(https?://|www\.)\S+|\S+@\S+|[\w.\-]+\.(com|es|net)\S*", t)


BLOQUE = re.compile(r"(<(p|li|h[1-6]|td|th|span|strong|em|a|figcaption|blockquote)\b[^>]*>)(.*?)(</\2>)", re.S)


def traducir(texto):
    if texto is None:
        return None
    s = _norm(str(texto))
    mem = memoria()
    if s in mem:
        return mem[s]
    if s.strip() in mem:
        return mem[s.strip()]
    if "<" not in s:
        return regla(html.unescape(s))
    # HTML: traducir el texto de cada bloque hoja; si alguno falta → None
    faltan = []

    def sub(m):
        inner = m.group(3)
        if re.search(r"<(p|li|h[1-6]|div|ul|ol|table)\b", inner):   # no es hoja: bajar
            return m.group(1) + BLOQUE.sub(sub, inner) + m.group(4)
        plano = html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()
        if not plano or not _traducible(plano):
            return m.group(0)
        en = mem.get(_norm(inner.strip())) or mem.get(plano)
        if en is None and not re.search(r"<[^>]+>", inner):
            en = regla(plano)
        if en is None and not re.search(r"<[^>]+>", inner):
            faltan.append(plano)
            return m.group(0)
        if en is None:
            # formato interno (<br>, <a>, <strong>…): se traduce cada trozo de texto entre etiquetas
            partes = re.split(r"(<[^>]+>)", inner)
            for i, parte in enumerate(partes):
                if parte.startswith("<") or not _traducible(parte):
                    continue
                t = html.unescape(parte).strip()
                en_p = mem.get(t) or regla(t)
                if en_p is None:
                    faltan.append(t)
                    return m.group(0)
                partes[i] = parte.replace(parte.strip(), en_p)
            return m.group(1) + "".join(partes) + m.group(4)
        return m.group(1) + en + m.group(4)

    out = BLOQUE.sub(sub, s)
    traducir.faltan = faltan
    return None if faltan else out


traducir.faltan = []

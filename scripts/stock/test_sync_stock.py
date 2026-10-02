"""python3 test_sync_stock.py — recetas y casos, sin red."""
import sync_stock as s

refs = {r: {} for r in ("010150101", "010150102", "010150461", "010150360", "010150330",
                         "070150191", "070150431", "010150340")}
conj = {"0100": [("0101", "", 1), ("0102", "", 1)],          # azucarero = cuerpo + tapa
        "0460": [("0360", "", 1), ("0461", "", 1)],          # taza café con platillo
        "0052": [("0191", "", 6)],                           # juego boles = 6 × bol pequeño
        "0430": [("0340", "", 1), ("0431", "07", 1)],        # taza desayuno: siempre forma 07
        "0021": [("0460", "", 6), ("0100", "", 1)],          # conjunto de conjuntos
        "0450": [("0350", "", 1), ("0451", "", 1)]}

assert s.recipe("010150330", refs, conj) == {"010150330": 1}                        # simple
assert s.recipe(" 010150330 ".lower(), refs, conj) == {"010150330": 1}              # espacios / mayúsculas
assert s.recipe("010150100", refs, conj) == {"010150101": 1, "010150102": 1}        # cuerpo + tapa
assert s.recipe("010150460", refs, conj) == {"010150461": 1, "010150360": 1}        # taza + platillo
assert s.recipe("070150052", refs, conj) == {"070150191": 6}                        # 6 × bol
assert s.recipe("010150430", refs, conj) == {"010150340": 1, "070150431": 1}        # forma fija 07
assert s.recipe("010150021", refs, conj) == {"010150461": 6, "010150360": 6, "010150101": 1, "010150102": 1}
assert s.recipe("010150450", refs, conj) is None                                    # faltan piezas
assert s.recipe("010150999", refs, conj) is None                                    # pieza desconocida
assert s.recipe("", refs, conj) is None

avail = {"a": 5, "b": 1, "c": 0}
biz = {"a": 10, "b": 0, "c": None}
# (caso, stock, bizcocho, inventario, política, fabricable)
assert s.disponibilidad({"a": 1}, avail, biz) == (1, 5, 10, 15, "CONTINUE", True)
assert s.disponibilidad({"a": 1, "b": 1}, avail, biz) == (1, 1, 0, 1, "CONTINUE", True)   # manda el más escaso
assert s.disponibilidad({"a": 6}, avail, biz) == (2, 0, 2, 2, "CONTINUE", True)           # pack de 6: 2 con bizcocho
assert s.disponibilidad({"b": 2}, avail, biz) == (3, 0, 0, 0, "CONTINUE", True)           # fase 3: bajo pedido sin tope
assert s.disponibilidad({"c": 1}, avail, biz) == (4, 0, 0, 0, "DENY", False)              # sin línea de bizcocho
assert s.disponibilidad({"a": 1, "c": 1}, avail, biz) == (4, 0, 0, 0, "DENY", False)      # una pieza no fabricable
s.TOPE_CASO3 = 20
assert s.disponibilidad({"b": 2}, avail, biz) == (3, 0, 0, 20, "DENY", True)              # con tope: hasta 20
assert s.disponibilidad({"c": 1}, avail, biz) == (4, 0, 0, 0, "DENY", False)
print("ok")

"""python3 traducciones/merge.py < lote.json — añade {es: en} a traducciones/en.json."""
import json, sys
from pathlib import Path
p = Path(__file__).with_name("en.json")
mem = json.loads(p.read_text())
nuevo = json.load(sys.stdin)
mem.update(nuevo)
p.write_text(json.dumps(mem, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
print("+%d → %d entradas" % (len(nuevo), len(mem)))

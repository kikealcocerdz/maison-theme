"""Integra la entrega «cartuja-quienes-somos» del cliente en el theme: prefijo qs- y estilos bajo .qs.

    python3 scripts/build_quienes_somos.py <carpeta cartuja-quienes-somos> .

Regenera sections/quienes-somos.liquid, templates/page.quienes-somos.json,
assets/quienes-somos.{css,js} y assets/qs-*.webp. No editar esos ficheros a mano.
"""
import re, shutil, pathlib, sys
SRC = pathlib.Path(sys.argv[1]); THEME = pathlib.Path(sys.argv[2])
def webp_size(p):
    """Ancho y alto de una WebP (VP8/VP8L/VP8X) sin dependencias."""
    b = p.read_bytes()[:40]; kind = b[12:16]
    if kind == b"VP8X": return 1 + int.from_bytes(b[24:27], "little"), 1 + int.from_bytes(b[27:30], "little")
    if kind == b"VP8L":
        v = int.from_bytes(b[21:25], "little"); return (v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1
    return int.from_bytes(b[26:28], "little") & 0x3FFF, int.from_bytes(b[28:30], "little") & 0x3FFF
CSS_ORDER = ["base", "styles", "editorial", "content-v6", "hover-v7", "final-v8", "readability-v9"]

def blocks(css):
    """Parte CSS minificado en (prelude, body) de primer nivel."""
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0: break
        depth, k = 1, j + 1
        while depth:
            depth += {"{": 1, "}": -1}.get(css[k], 0); k += 1
        out.append((css[i:j].strip(), css[j + 1:k - 1])); i = k
    return out

def scope_sel(sel):
    sel = sel.strip()
    if sel in (":root", "html", "body"): return ".qs"
    sel = re.sub(r"^(html|body)\b", ".qs", sel)
    if re.match(r"\.qs(?![\w-])", sel): return sel
    if sel.startswith(".motion-ready"): return ".qs" + sel
    return ".qs " + sel

def scope(css):
    out = []
    for pre, body in blocks(css):
        if pre.startswith("@font-face"): continue            # el theme ya carga EB Garamond y Montserrat
        if pre.startswith("@keyframes"): out.append(f"{pre}{{{body}}}")
        elif pre.startswith("@"): out.append(f"{pre}{{{scope(body)}}}")
        else: out.append(",".join(scope_sel(s) for s in pre.split(",")) + "{" + body + "}")
    return "".join(out)

css = "".join((SRC / f"{n}.css").read_text() for n in CSS_ORDER)
css = re.sub(r"/\*.*?\*/", "", css, flags=re.S).replace(".reveal", ".qs-reveal")
css = re.sub(r"url\(['\"]?assets/([^'\")]+)['\"]?\)", r"url(qs-\1)", css)   # mismas carpeta assets/ en Shopify
(THEME / "assets/quienes-somos.css").write_text("/* Quiénes somos (entrega v9) encapsulada bajo .qs. Generado: no editar a mano. */\n" + scope(css) + "\n")

imgs = sorted(p.name for p in (SRC / "assets").glob("*.webp") if p.name != "logo-oficial.webp")
for name in imgs: shutil.copy(SRC / "assets" / name, THEME / "assets" / f"qs-{name}")

js = (SRC / "script.js").read_text()
js = js.replace("assets/${src}.webp", "${base}qs-${src}.webp").replace("`assets/archivo-${d.id}.webp`", "`${base}qs-archivo-${d.id}.webp`") \
       .replace("`assets/${details[detailIndex].image}.webp`", "`${base}qs-${details[detailIndex].image}.webp`") \
       .replace("document.body.classList.add('motion-ready')", "root.classList.add('motion-ready')").replace("'.reveal'", "'.qs-reveal'")
js = js.replace("(()=>{'use strict';", "(()=>{'use strict';const root=document.querySelector('.qs');if(!root)return;const base=root.dataset.assets;", 1)
assert "assets/" not in js.replace("dataset.assets", ""), "quedan rutas assets/ en el JS"
(THEME / "assets/quienes-somos.js").write_text(js)

html = (SRC / "index.html").read_text()
main = re.search(r'<main id="contenido">(.*)</main>', html, re.S).group(1)
dialog = re.search(r"(<dialog.*?</dialog>)", html, re.S).group(1)
body = main + dialog
body = body.replace('class="reveal"', 'class="qs-reveal"')
body = re.sub(r'class="([^"]*)\breveal\b([^"]*)"', r'class="\1qs-reveal\2"', body)
body = body.replace("https://la-cartuja-de-sevilla.myshopify.com/collections/all", "{{ routes.all_products_collection_url }}")
body = body.replace('src="assets/logo-oficial.webp"', "src=\"{{ 'logo-navy.png' | asset_url }}\"")
def dims(tag):
    if " width=" in tag: return tag
    m = re.search(r'src="assets/([^"]+)"', tag)
    if not m: return tag
    w, h = webp_size(SRC / "assets" / m.group(1))
    return tag.replace("<img ", f'<img width="{w}" height="{h}" ', 1)
body = re.sub(r"<img [^>]*>", lambda m: dims(m.group(0)), body)
body = re.sub(r'src="assets/([^"]+)"', lambda m: "src=\"{{ 'qs-" + m.group(1) + "' | asset_url }}\"", body)
body = body.replace('<section class="hero">', '<section class="hero" data-header-variant="light">')
assert 'assets/' not in body
# Flechas como SVG fino: los caracteres ←/→/↗ salían como emoji en iPhone (cliente 2026-10-05).
_svg = lambda d: f'<svg class="qs-arrow" viewBox="0 0 24 24" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="1.25" vector-effect="non-scaling-stroke" aria-hidden="true"><path vector-effect="non-scaling-stroke" d="{d}"/></svg>'
body = body.replace('>←<', '>' + _svg("M20 12H4M10 6l-6 6 6 6") + '<').replace('>→<', '>' + _svg("M4 12h16M14 6l6 6-6 6") + '<').replace('↗', _svg("M7 17 17 7M9 7h8v8"))
section = """{%- comment -%}
  Quiénes somos: entrega cerrada del cliente (cartuja-quienes-somos v9, 2026-09-29),
  integrada tal cual. Estilos en assets/quienes-somos.css (todo bajo .qs) y lógica en
  assets/quienes-somos.js; imágenes con prefijo qs-. Cabecera y pie son los del theme.
  ponytail: textos fijos en el HTML como vienen en la entrega; pasar a ajustes si el
  cliente quiere editarlos desde el editor.
{%- endcomment -%}
{{ 'quienes-somos.css' | asset_url | stylesheet_tag }}
<div class="qs" data-assets="{{ 'qs-portada.webp' | asset_url | split: 'qs-portada.webp' | first }}">
""" + body + """
</div>
<script src="{{ 'quienes-somos.js' | asset_url }}" defer></script>

{% stylesheet %}
/* 2026-10-05 · cliente: ←, → y ↗ eran caracteres de texto (en iPhone ↗ sale como emoji).
   Ahora son SVG de trazo fino; miden 1em, así que heredan el font-size que ya tenían. */
.qs .qs-arrow { display: inline-block; vertical-align: middle; }
/* El hero arranca bajo la cabecera fija del theme (la entrega traía la suya). */
.qs .hero-copy { padding-top: calc(var(--header-h) + 56px); }
/* 2026-10-05 · cliente: en móvil Propósito / Misión / Visión dejaba un hueco blanco enorme.
   La entrega fija min-height (hasta 600px en .story-copy) para que no salte al cambiar de
   pestaña; aquí manda el texto. #piezas sube la especificidad sobre quienes-somos.css. */
@media (max-width: 1000px) {
  .qs #piezas .story-copy, .qs #piezas .story-copy h3, .qs #piezas .story-copy > p { min-height: 0; }
  .qs #piezas .story-copy > p { margin-bottom: 22px; }
  .qs #piezas .story-photo { aspect-ratio: 4 / 3; }
}
{% endstylesheet %}

{% schema %}
{ "name": "Quiénes somos", "tag": "section", "class": "section-quienes-somos"}
{% endschema %}
"""
(THEME / "sections/quienes-somos.liquid").write_text(section)
(THEME / "templates/page.quienes-somos.json").write_text('{\n  "sections": {\n    "main": { "type": "quienes-somos", "settings": {} }\n  },\n  "order": ["main"]\n}\n')
print("imágenes:", len(imgs), "| css:", (THEME / "assets/quienes-somos.css").stat().st_size, "B")

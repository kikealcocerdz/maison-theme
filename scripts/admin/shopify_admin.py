"""Envoltorio mínimo sobre `shopify store execute` (CLI Connector).

Sin dependencias: subprocess + json. La autenticación es la que ya tiene guardada
el CLI (`store auth`), así que no hay tokens en el repo ni en el entorno.

Todos los scripts de esta carpeta:
  - por defecto NO tocan nada: imprimen la mutación y sus variables (ensayo).
  - con `--apply` ejecutan de verdad, una mutación cada vez, y muestran
    `userErrors` y el estado posterior.

Uso desde un script:

    from shopify_admin import Admin
    admin = Admin(apply=args.apply)
    data = admin.query(QUERY, {"handle": "novedades"})
    admin.mutate("crear colección novedades", MUTATION, variables, "collectionCreate")
"""

import json
import os
import subprocess
import sys
import tempfile

STORE = os.environ.get("CARTUJA_STORE", "la-cartuja-de-sevilla.myshopify.com")
CLI = ["npx", "-y", "@shopify/cli@4.7.1"]


class AdminError(RuntimeError):
    pass


class Admin:
    def __init__(self, apply=False, store=STORE, strict=True):
        self.apply = apply
        self.store = store
        self.strict = strict  # con False, un userErrors se anota y el script sigue
        self.done = []      # (etiqueta, payload) de lo ejecutado
        self.planned = []   # (etiqueta, variables) de lo que se ejecutaría
        self.failed = []    # (etiqueta, userErrors)

    # ---- transporte ------------------------------------------------------
    def _run(self, query, variables=None, mutation=False):
        cmd = CLI + [
            "store", "execute",
            "--store", self.store,
            "--query", query,
            "--json",
        ]
        if variables is not None:
            cmd += ["--variables", json.dumps(variables)]
        if mutation:
            cmd += ["--allow-mutations"]

        with tempfile.NamedTemporaryFile("r+", suffix=".json", delete=False) as fh:
            out_path = fh.name
        cmd += ["--output-file", out_path]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
            try:
                with open(out_path) as fh:
                    raw = fh.read()
            except OSError:
                raw = ""
        finally:
            try:
                os.unlink(out_path)
            except OSError:
                pass

        if not raw.strip():
            raise AdminError(
                "sin respuesta del CLI (código %s)\n%s\n%s"
                % (proc.returncode, proc.stdout[-1500:], proc.stderr[-1500:])
            )
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise AdminError("respuesta no es JSON: %s\n%s" % (exc, raw[:1500]))

        if isinstance(payload, dict) and payload.get("errors"):
            raise AdminError(json.dumps(payload["errors"], indent=2, ensure_ascii=False))
        return payload

    # ---- lectura ---------------------------------------------------------
    def query(self, query, variables=None):
        """Consulta de sólo lectura. Se ejecuta siempre, también en ensayo."""
        return self._run(query, variables, mutation=False)

    # ---- escritura -------------------------------------------------------
    def mutate(self, label, query, variables, root_field):
        """Ejecuta una mutación (o la imprime, si estamos en ensayo).

        `root_field` es el campo de la respuesta donde vienen los `userErrors`
        (p. ej. "collectionCreate"). Devuelve None en ensayo.
        """
        if not self.apply:
            self.planned.append((label, variables))
            print("\n· [ENSAYO] %s" % label)
            print(_indent(query.strip()))
            print("  variables:")
            print(_indent(json.dumps(variables, indent=2, ensure_ascii=False), 4))
            return None

        print("\n· %s" % label)
        payload = self._run(query, variables, mutation=True)
        body = (payload or {}).get(root_field) or {}
        errors = body.get("userErrors") or []
        if errors:
            print("  ✗ userErrors:")
            print(_indent(json.dumps(errors, indent=2, ensure_ascii=False), 4))
            self.failed.append((label, errors))
            if self.strict:
                raise AdminError("%s devolvió userErrors" % label)
            return None
        print("  ✓ " + json.dumps(_summary(body), ensure_ascii=False)[:400])
        self.done.append((label, body))
        return body

    # ---- informe ---------------------------------------------------------
    def report(self, path):
        data = {
            "modo": "aplicado" if self.apply else "ensayo",
            "tienda": self.store,
            "ejecutado": [{"paso": l, "resultado": b} for l, b in self.done],
            "planificado": [{"paso": l, "variables": v} for l, v in self.planned],
            "fallido": [{"paso": l, "userErrors": e} for l, e in self.failed],
        }
        with open(path, "w") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        print("\nInforme en %s" % path)


def _indent(text, spaces=2):
    pad = " " * spaces
    return "\n".join(pad + line for line in text.splitlines())


def _summary(body):
    out = {}
    for key, value in body.items():
        if key == "userErrors":
            continue
        if isinstance(value, dict):
            out[key] = {k: v for k, v in value.items() if k in ("id", "handle", "title", "status")} or value
        else:
            out[key] = value
    return out


def add_common_args(parser, default_report):
    parser.add_argument("--apply", action="store_true",
                        help="ejecuta de verdad; sin este flag sólo se imprime el plan")
    parser.add_argument("--report", default=default_report,
                        help="ruta del informe JSON (por defecto %s)" % default_report)
    return parser


def banner(title, admin):
    modo = "APLICAR (escribe en la tienda)" if admin.apply else "ENSAYO (no escribe nada)"
    print("=" * 72)
    print(title)
    print("tienda: %s | modo: %s" % (admin.store, modo))
    print("=" * 72)

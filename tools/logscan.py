"""Resume un console.log de Arma Reforger (servidor, juego o Workbench) en pocas lineas.

Uso:
  python tools/logscan.py RUTA/console.log [--ok "[TEST] OK"] [--fail "FALLO"] [--grep REGEX] [--max 20]

Muestra: errores de compilacion, excepciones de la maquina virtual (con motivo y pila), errores de script
de TU codigo, recuento de OK/FALLO del autotest, y problemas tipicos (puerto ocupado, recursos sin registrar).
Codigo de salida: 0 si no hay errores de compilacion, excepciones ni fallos; 1 si los hay.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit

# lineas de error que salen siempre con mods conocidos y no son tuyas (anade las tuyas con --ignore)
NOISE = [
	"Wrong GUID/name for resource",
	"is trying to set friendly factions",
	"needs a entity catalog manager",
	"Resource leaks",
	"robotomono_msdf",
	"Unknown class 'SCR_WidgetExportRuleRoot'",
]

KNOWN = [
	("Unable to start replication", "El puerto (2001) esta ocupado: hay otro servidor o cliente de prueba abierto. Ciérralo y repite."),
	("invalid prefab resource GUID", "Prefab sin registrar: abre el proyecto en Workbench (tools/register.py) para que entre en resourceDatabase.rdb."),
	("metafile without corresponding resource", "Hay un .meta sin su archivo (o al reves)."),
	("resource not registered", "Recurso sin registrar: ejecuta tools/register.py."),
	("No navmesh file specified", "El SCR_AIWorld del mundo no tiene navmesh: la IA no se movera (\"Failed move\")."),
	("Failed move", "La IA no encuentra camino: waypoint fuera de la navmesh (usa GetReachablePoint) o mundo sin navmesh."),
	("dependency", "Problema de dependencias del addon.gproj (¿esta la carpeta del mod en -addonsDir?)."),
]


def scan(text, ok_mark, fail_mark, extra_grep=None, max_items=20, ignore=()):
	lines = text.splitlines()
	res = {"compile": [], "vm": [], "script_err": [], "ok": 0, "fail": [], "known": {}, "grep": []}
	noise = NOISE + list(ignore)
	i = 0
	while i < len(lines):
		l = lines[i]
		if "Can't compile" in l or ("SCRIPT" in l and "(E): @\"" in l):
			res["compile"].append(l.strip())
		elif "Virtual Machine Exception" in l:
			block = [l.strip()]
			j = i + 1
			while j < len(lines) and j < i + 16 and lines[j].strip() and "(E)" not in lines[j][:40]:
				block.append(lines[j].strip())
				j += 1
			res["vm"].append("\n    ".join(block))
			i = j
			continue
		elif "SCRIPT" in l and "(E)" in l and not any(n in l for n in noise):
			res["script_err"].append(l.strip())
		if ok_mark and ok_mark in l:
			res["ok"] += 1
		if fail_mark and fail_mark in l:
			res["fail"].append(l.strip())
		for k, msg in KNOWN:
			if k in l:
				res["known"].setdefault(msg, 0)
				res["known"][msg] += 1
		if extra_grep and re.search(extra_grep, l):
			res["grep"].append(l.strip())
		i += 1
	return res


def report(res, max_items=20):
	out = []
	def section(title, items):
		if not items:
			return
		uniq = list(dict.fromkeys(items))
		out.append(f"## {title} ({len(items)})")
		for x in uniq[:max_items]:
			out.append("  " + x[:400])
		if len(uniq) > max_items:
			out.append(f"  ... y {len(uniq) - max_items} mas")
	section("ERRORES DE COMPILACION", res["compile"])
	section("EXCEPCIONES (Virtual Machine Exception)", res["vm"])
	section("FALLOS DEL AUTOTEST", res["fail"])
	section("Errores de script (filtrado el ruido conocido)", res["script_err"])
	section("Coincidencias de --grep", res["grep"])
	if res["known"]:
		out.append("## Pistas")
		for msg, n in res["known"].items():
			out.append(f"  [{n}x] {msg}")
	out.append(f"## Resumen: OK={res['ok']} FALLO={len(res['fail'])} compilacion={len(res['compile'])} excepciones={len(res['vm'])}")
	return "\n".join(out)


def has_problems(res):
	return bool(res["compile"] or res["vm"] or res["fail"])


def main():
	ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	ap.add_argument("log")
	ap.add_argument("--ok", default="[TEST] OK")
	ap.add_argument("--fail", default="FALLO")
	ap.add_argument("--grep")
	ap.add_argument("--ignore", action="append", default=[])
	ap.add_argument("--max", type=int, default=20)
	a = ap.parse_args()
	res = scan(kit.read_text(a.log), a.ok, a.fail, a.grep, a.max, a.ignore)
	print(report(res, a.max))
	sys.exit(1 if has_problems(res) else 0)


if __name__ == "__main__":
	main()

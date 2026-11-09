"""Busca recursos ({GUID}ruta) del juego, de los mods descargados y de tus proyectos. Nunca inventes un GUID:
copialo de aqui.

Uso:
  python tools/find.py --build                 (una vez, o tras instalar mods: crea out/index/resources.txt)
  python tools/find.py G36 .et                 (todas las palabras deben aparecer; .et filtra por extension)
  python tools/find.py Character FFAA Rifleman --max 30
  python tools/find.py --source FFAA-Core loadout     (solo lo que venga de una carpeta de mod concreta)

El indice sale de:
  - proyectos de Workbench: los .meta (GUID exacto de cada archivo);
  - .pak y resourceDatabase.rdb del juego y de los mods: todas las referencias "{GUID}ruta" que contienen.
    (Un recurso que nada referencia puede no salir; en ese caso busca su ruta con tools/pakgrep.py.)
"""
import argparse
import mmap
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit

EXT = r"(?:et|ent|conf|layout|imageset|edds|emat|xob|nmn|acp|st|bt|ct|ai|ptc|anm|agr|asi|sig|styles|fnt|c|gproj)"
REF = re.compile(rb"\{([0-9A-F]{16})\}([A-Za-z0-9_][A-Za-z0-9_ /\.\-\(\)]{2,180}?\." + EXT.encode() + rb")(?![A-Za-z0-9])")
META = re.compile(r'Name "\{([0-9A-F]{16})\}([^"]+)"')


def index_path():
	return os.path.join(kit.ensure_out("index"), "resources.txt")


def scan_bin(path, source, found):
	try:
		with open(path, "rb") as f:
			size = os.fstat(f.fileno()).st_size
			if size == 0:
				return
			mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
			for m in REF.finditer(mm):
				key = (m.group(1).decode(), m.group(2).decode("latin-1"))
				found.setdefault(key, source)
			mm.close()
	except (OSError, ValueError) as e:
		print("  no se pudo leer", path, e)


def build(cfg):
	found = {}
	t0 = time.time()
	# proyectos de Workbench (exacto, desde .meta)
	wb = cfg["workbench_addons"]
	for proj in sorted(os.listdir(wb)):
		pdir = os.path.join(wb, proj)
		if not os.path.isfile(os.path.join(pdir, "addon.gproj")):
			continue
		for dp, dn, fn in os.walk(pdir):
			dn[:] = [d for d in dn if d not in (".git", "tools", "__pycache__")]
			for f in fn:
				if f.endswith(".meta"):
					m = META.search(kit.read_text(os.path.join(dp, f)))
					if m:
						found[(m.group(1), m.group(2))] = "proyecto:" + proj
	print(f"proyectos: {len(found)} recursos")
	# mods descargados y juego base (.pak y .rdb)
	roots = [("juego", cfg["game_addons"]), ("mod", cfg["downloaded_addons"])]
	for kind, root in roots:
		if not os.path.isdir(root):
			continue
		for d in sorted(os.listdir(root)):
			full = os.path.join(root, d)
			if not os.path.isdir(full):
				continue
			files = [os.path.join(dp, f) for dp, dn, fn in os.walk(full) for f in fn if f.endswith((".pak", ".rdb"))]
			n0 = len(found)
			for p in files:
				scan_bin(p, f"{kind}:{d}", found)
			print(f"{kind}:{d}: +{len(found) - n0}")
	with open(index_path(), "w", encoding="utf-8") as f:
		for (g, path), src in sorted(found.items(), key=lambda x: x[0][1].lower()):
			f.write(f"{{{g}}}{path}\t{src}\n")
	print(f"indice: {index_path()} ({len(found)} recursos, {int(time.time() - t0)} s)")


def search(words, ext=None, source=None, limit=50):
	p = index_path()
	if not os.path.exists(p):
		kit.die("no hay indice: ejecuta python tools/find.py --build")
	words = [w.lower() for w in words]
	n = 0
	with open(p, encoding="utf-8") as f:
		for line in f:
			low = line.lower()
			ref, src = line.rstrip("\n").split("\t")
			if ext and not ref.lower().endswith(ext.lower()):
				continue
			if source and source.lower() not in src.lower():
				continue
			if all(w in low for w in words):
				print(f"{ref}    [{src}]")
				n += 1
				if n >= limit:
					print(f"... (hay mas; afina la busqueda o usa --max)")
					break
	if n == 0:
		print("sin resultados")


def main():
	ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	ap.add_argument("words", nargs="*")
	ap.add_argument("--build", action="store_true")
	ap.add_argument("--source")
	ap.add_argument("--max", type=int, default=50)
	a = ap.parse_args()
	cfg = kit.load_config()
	if a.build:
		build(cfg)
		return
	exts = [w for w in a.words if w.startswith(".")]
	words = [w for w in a.words if not w.startswith(".")]
	search(words, exts[0] if exts else None, a.source, a.max)


if __name__ == "__main__":
	main()

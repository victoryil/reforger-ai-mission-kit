"""Busca texto dentro de los .pak del juego o de un mod y muestra el contexto. Sirve para ver como esta hecho un
prefab, un layout o una config del juego (propiedades exactas, GUIDs de componentes, sintaxis).

Uso:
  python tools/pakgrep.py "SizeLayoutWidgetClass" [--n 3] [--before 200] [--after 1500]
  python tools/pakgrep.py "Workbench_01.et" --mods            (busca tambien en los mods descargados)
  python tools/pakgrep.py "ImageSetTextureClass" --only data007.pak

Ojo: muchos archivos dentro de los .pak van comprimidos y no se encuentran asi; los pequenos y muchos
prefabs/layouts/configs si van en texto plano. Si no sale, prueba otra palabra del mismo archivo.
"""
import argparse
import glob
import mmap
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit


def paks(cfg, mods, only):
	out = sorted(glob.glob(os.path.join(cfg["game_addons"], "data", "*.pak")))
	if mods:
		out += sorted(glob.glob(os.path.join(cfg["downloaded_addons"], "*", "*.pak")))
	if only:
		out = [p for p in out if only.lower() in p.lower()]
	return out


def main():
	sys.stdout.reconfigure(encoding="utf-8")
	ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	ap.add_argument("text")
	ap.add_argument("--n", type=int, default=3)
	ap.add_argument("--before", type=int, default=200)
	ap.add_argument("--after", type=int, default=1500)
	ap.add_argument("--mods", action="store_true")
	ap.add_argument("--only")
	a = ap.parse_args()
	cfg = kit.load_config()
	pat = a.text.encode("utf-8")
	shown = 0
	for p in paks(cfg, a.mods, a.only):
		with open(p, "rb") as f:
			mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
			i = mm.find(pat)
			while i >= 0 and shown < a.n:
				chunk = mm[max(0, i - a.before): i + a.after]
				text = chunk.decode("utf-8", "replace")
				# recorta la basura binaria de los bordes
				text = "".join(c if ((c.isprintable() and c != "�") or c in "\n\t") else "" for c in text).strip()
				print(f"===== {os.path.basename(os.path.dirname(p))}/{os.path.basename(p)} @ {i}")
				print(text)
				shown += 1
				i = mm.find(pat, i + 1)
			mm.close()
		if shown >= a.n:
			break
	if shown == 0:
		print("sin resultados (puede estar comprimido)")


if __name__ == "__main__":
	main()

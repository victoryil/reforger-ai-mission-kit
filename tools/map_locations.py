"""Saca los sitios con nombre del mapa de tu mision (ciudades, pueblos, aldeas, bases, puertos, aeropuertos) con
coordenadas a ras de suelo, para elegir donde poner objetivos, el punto de aparicion o los enemigos.

Uso:
  python tools/map_locations.py              -> out/map_<proyecto>.tsv  (tipo, nombre, x y z)
  python tools/map_locations.py --grep Morton

Arranca el servidor de pruebas con -<dumpmap_param> (el proyecto creado con new_project.py lo trae:
<PREFIJO>DumpMap) y lee las lineas [MAP] del log. Una vez generado, basta con leer el .tsv.
Las coordenadas son "x y z" en metros: x este-oeste, y altura, z norte-sur (como "coords" en los .layer).
"""
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit


def main():
	ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	ap.add_argument("--grep")
	ap.add_argument("--refresh", action="store_true", help="vuelve a arrancar el servidor aunque ya exista el .tsv")
	a = ap.parse_args()
	cfg = kit.load_config()
	out = os.path.join(kit.ensure_out(), f"map_{cfg['project']}.tsv")
	if a.refresh or not os.path.exists(out):
		param = cfg.get("dumpmap_param")
		if not param:
			kit.die('falta "dumpmap_param" en kit.config.json (p. ej. "OADumpMap")')
		here = os.path.dirname(os.path.abspath(__file__))
		subprocess.run([sys.executable, os.path.join(here, "server_test.py"), "--no-selftest", "--secs", "150",
			"--until", "[MAP] FIN", f"--param=-{param}"])
		log = os.path.join(kit.OUT, "logs", "server_last.log")
		rows = []
		for l in kit.read_text(log).splitlines():
			if "[MAP]\t" in l:
				parts = l.split("[MAP]\t", 1)[1].split("\t")
				if len(parts) >= 3:
					rows.append("\t".join(parts[:3]))
		if not rows:
			kit.die("no salio ninguna linea [MAP] (¿el mundo tiene SCR_MapEntity? mira out/logs/server_last.log)")
		with open(out, "w", encoding="utf-8") as f:
			f.write("tipo\tnombre\tx y z\n" + "\n".join(rows) + "\n")
		print(f"{len(rows)} sitios -> {out}")
	for l in kit.read_text(out).splitlines():
		if not a.grep or a.grep.lower() in l.lower():
			print(l)


if __name__ == "__main__":
	main()

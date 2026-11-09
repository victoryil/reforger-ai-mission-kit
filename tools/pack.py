"""Empaqueta uno o varios proyectos con la linea de comandos de Workbench (como hace "Publish", sin subir nada).

Uso:
  python tools/pack.py [PROYECTO ...]        (por defecto, el "project" de kit.config.json)

Deja cada mod en out/packed/<PROYECTO>/ (addon.gproj, data.pak, resourceDatabase.rdb). Empaqueta primero las
dependencias propias (por ejemplo, un kit de interfaz) y luego la mision. Lo usan server_test.py --packed y
client_test.py, que cargan desde out/packed.
"""
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit


def pack(cfg, name):
	proj = kit.project_dir(cfg, name)
	name = os.path.basename(proj.rstrip("/\\"))
	tmp = os.path.join(kit.ensure_out(), "packing_" + name)
	dst = os.path.join(kit.ensure_out("packed"), name)
	shutil.rmtree(tmp, ignore_errors=True)
	log = os.path.join(kit.ensure_out("logs"), f"pack_{name}.log")
	cmd = [cfg["workbench_exe"], "-wbModule=ResourceManager", "-gproj", os.path.join(proj, "addon.gproj").replace("\\", "/"),
		"-addonsDir", kit.addons_dirs(cfg, for_game=True), "-packAddon", "-packAddonDir", tmp.replace("\\", "/")]
	with open(log, "w") as f:
		subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
	if not os.path.isdir(tmp) or not os.listdir(tmp):
		print(f"FALLO al empaquetar {name}: mira {log}")
		return False
	shutil.rmtree(dst, ignore_errors=True)
	shutil.move(tmp, dst)
	print(f"empaquetado {name}: {', '.join(sorted(os.listdir(dst)))}")
	return True


def main():
	cfg = kit.load_config()
	names = sys.argv[1:] or [cfg["project"]]
	ok = all([pack(cfg, n) for n in names])
	sys.exit(0 if ok else 1)


if __name__ == "__main__":
	main()

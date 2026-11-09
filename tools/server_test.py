"""Arranca un servidor dedicado de PRUEBAS con tu mision, espera y resume el log.

Uso:
  python tools/server_test.py [--project NOMBRE] [--secs 300] [--until "FIN autotest"] [--packed]
                              [--no-selftest] [--keep-save] [--param -otroParam] [--grep REGEX]

- Sin --packed: carga el proyecto SIN empaquetar (-gproj) y el mundo de kit.config.json ("world"). Es lo mas
  rapido para comprobar que compila y para el autotest de servidor.
- Con --packed: carga lo empaquetado por tools/pack.py (out/packed) con "-addons GUID -server ESCENARIO",
  igual que un servidor real. Necesario para probar la cabecera de mision (un proyecto sin empaquetar no la carga).
- Activa el autotest con -<selftest_param> (kit.config.json) salvo --no-selftest.
- Borra antes las partidas guardadas de la carpeta de pruebas ("save_files_to_clear") salvo --keep-save:
  cada prueba empieza limpia (si no, el autotest carga lo que dejo la anterior).
- Termina al ver --until en el log o al pasar --secs. Cierra SOLO el proceso que ha abierto.
- Deja el log en out/logs/server_last.log y lo resume con logscan. Codigo de salida 1 si hay errores.
"""
import argparse
import os
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit
import logscan

MARKER = "rkit_server_test"


def main():
	ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	ap.add_argument("--project")
	ap.add_argument("--secs", type=int, default=300)
	ap.add_argument("--until", help="texto del log que indica que ya ha terminado (p. ej. 'FIN del autotest')")
	ap.add_argument("--packed", action="store_true")
	ap.add_argument("--no-selftest", action="store_true")
	ap.add_argument("--keep-save", action="store_true")
	ap.add_argument("--param", action="append", default=[], help="parametro extra para el servidor (repetible)")
	ap.add_argument("--grep")
	ap.add_argument("--ok", default="[TEST] OK")
	ap.add_argument("--fail", default="FALLO")
	a = ap.parse_args()
	cfg = kit.load_config()

	if kit.find_processes("rkit_"):
		print("Hay otra prueba del kit en marcha; espero a que termine...")
		kit.wait_free("rkit_", 900)
	if kit.port_busy(cfg.get("server_port", 2001)):
		print(f"AVISO: el puerto {cfg.get('server_port', 2001)} esta ocupado (¿otro servidor o el juego?). La prueba fallara con 'Unable to start replication'.")

	profile = os.path.join(cfg["work_dir"], MARKER).replace("\\", "/")
	os.makedirs(profile, exist_ok=True)
	shutil.rmtree(os.path.join(profile, "logs"), ignore_errors=True)
	if not a.keep_save:
		for rel in cfg.get("save_files_to_clear", []):
			p = os.path.join(profile, rel)
			if os.path.exists(p):
				os.remove(p)
				print("borrada partida de pruebas", rel)

	cmd = [cfg["server_exe"]]
	if a.packed:
		packed = os.path.join(kit.OUT, "packed").replace("\\", "/")
		cmd += ["-addonsDir", kit.addons_dirs(cfg, extra=packed, include_workbench=False),
			"-addons", cfg["project_guid"], "-server", cfg["scenario"]]
	else:
		proj = kit.project_dir(cfg, a.project)
		cmd += ["-gproj", os.path.join(proj, "addon.gproj").replace("\\", "/"), "-addonsDir", kit.addons_dirs(cfg), "-server", cfg["world"]]
	cmd += ["-profile", profile, "-maxFPS", "30", "-noSound", "-logLevel", "normal"]
	if not a.no_selftest and cfg.get("selftest_param"):
		cmd.append("-" + cfg["selftest_param"])
	cmd += a.param
	print("arrancando:", " ".join(f'"{c}"' if " " in c else c for c in cmd))
	p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	t0 = time.time()
	log = None
	while time.time() - t0 < a.secs:
		time.sleep(3)
		if p.poll() is not None:
			print("el servidor se ha cerrado solo (mira el log)")
			break
		d = kit.newest_dir(os.path.join(profile, "logs"))
		if d:
			log = os.path.join(d, "console.log")
			if a.until and os.path.exists(log) and a.until in kit.read_text(log):
				print("visto:", a.until)
				time.sleep(2)
				break
	if p.poll() is None:
		kit.powershell(f"Stop-Process -Id {p.pid} -Force")
	d = kit.newest_dir(os.path.join(profile, "logs"))
	if not d:
		kit.die("no hay log del servidor")
	dst = os.path.join(kit.ensure_out("logs"), "server_last.log")
	shutil.copyfile(os.path.join(d, "console.log"), dst)
	print(f"log: {dst}  ({int(time.time() - t0)} s)")
	res = logscan.scan(kit.read_text(dst), a.ok, a.fail, a.grep)
	print(logscan.report(res))
	sys.exit(1 if logscan.has_problems(res) else 0)


if __name__ == "__main__":
	main()

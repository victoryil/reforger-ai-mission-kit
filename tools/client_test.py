"""Prueba con el JUEGO real: aloja tu escenario empaquetado, despliega solo, ejecuta tu autotest de cliente
y saca capturas cuando tu script lo pide. Abre una ventana visible (pide permiso al usuario la primera vez).

Uso:
  python tools/client_test.py [--secs 300] [--shots CAPTURA_HUD,CAPTURA_MAPA] [--until "FIN autotest de cliente"]
                              [--faction FFAA] [--param -otro] [--no-clienttest]

Pasos previos: python tools/pack.py (con todas tus dependencias propias) -> deja el mod en out/packed.

- Carga out/packed + mods descargados con "-addons GUID -server ESCENARIO" (kit.config.json).
- --faction (o "client_faction") despliega directo en esa faccion con -tdmf/-tdml, sin menus.
- Activa tu autotest de cliente con -<clienttest_param>.
- Cada marca de --shots que aparezca en el log se captura a out/shots/<MARCA>.png (ventana del juego).
- Termina con --until o --secs; cierra SOLO su proceso. Log en out/logs/client_last.log + resumen.

En tu script: Print("[MI][CLIENT] CAPTURA_HUD") cuando la pantalla este lista para la foto.
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
import screenshot

MARKER = "rkit_client_test"


def main():
	ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	ap.add_argument("--secs", type=int, default=300)
	ap.add_argument("--shots", default="", help="marcas del log separadas por comas")
	ap.add_argument("--until")
	ap.add_argument("--faction")
	ap.add_argument("--param", action="append", default=[])
	ap.add_argument("--no-clienttest", action="store_true")
	ap.add_argument("--ok", default="OK:")
	ap.add_argument("--fail", default="FALLO")
	a = ap.parse_args()
	cfg = kit.load_config()

	if kit.find_processes("rkit_"):
		print("Hay otra prueba del kit en marcha; espero a que termine...")
		kit.wait_free("rkit_", 900)
	profile = os.path.join(cfg["work_dir"], MARKER).replace("\\", "/")
	os.makedirs(profile, exist_ok=True)
	shutil.rmtree(os.path.join(profile, "logs"), ignore_errors=True)
	for rel in cfg.get("save_files_to_clear", []):
		p = os.path.join(profile, rel)
		if os.path.exists(p):
			os.remove(p)

	packed = os.path.join(kit.OUT, "packed").replace("\\", "/")
	if not os.path.isdir(packed):
		kit.die("no hay nada en out/packed: ejecuta antes python tools/pack.py")
	cmd = [cfg["game_exe"], "-addonsDir", kit.addons_dirs(cfg, extra=packed, for_game=True, include_workbench=False),
		"-addons", cfg["project_guid"], "-server", cfg["scenario"], "-window", "-profile", profile]
	faction = a.faction or cfg.get("client_faction")
	if faction:
		cmd += ["-tdmf", faction, "-tdml", "0"]
	if not a.no_clienttest and cfg.get("clienttest_param"):
		cmd.append("-" + cfg["clienttest_param"])
	cmd += a.param
	print("arrancando el juego:", " ".join(f'"{c}"' if " " in c else c for c in cmd))
	p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	shots = [s.strip() for s in a.shots.split(",") if s.strip()]
	taken = set()
	shot_dir = kit.ensure_out("shots")
	t0 = time.time()
	while time.time() - t0 < a.secs:
		time.sleep(1)
		if p.poll() is not None:
			print("el juego se ha cerrado")
			break
		d = kit.newest_dir(os.path.join(profile, "logs"))
		if not d:
			continue
		text = kit.read_text(os.path.join(d, "console.log")) if os.path.exists(os.path.join(d, "console.log")) else ""
		for s in shots:
			if s not in taken and s in text:
				time.sleep(1.2)
				screenshot.capture(os.path.join(shot_dir, s + ".png"))
				taken.add(s)
		if "Virtual Machine Exception" in text and "vm_shot" not in taken:
			# el juego muestra un cartel de error: se captura para verlo
			screenshot.capture(os.path.join(shot_dir, "ERROR_VM.png"))
			taken.add("vm_shot")
		if a.until and a.until in text:
			time.sleep(2)
			break
	if p.poll() is None:
		kit.powershell(f"Stop-Process -Id {p.pid} -Force")
	d = kit.newest_dir(os.path.join(profile, "logs"))
	if not d:
		kit.die("no hay log del juego")
	dst = os.path.join(kit.ensure_out("logs"), "client_last.log")
	shutil.copyfile(os.path.join(d, "console.log"), dst)
	missing = [s for s in shots if s not in taken]
	print(f"log: {dst}  ({int(time.time() - t0)} s)  capturas: {sorted(taken - {'vm_shot'})}" + (f"  SIN CAPTURAR: {missing}" if missing else ""))
	res = logscan.scan(kit.read_text(dst), a.ok, a.fail)
	print(logscan.report(res))
	sys.exit(1 if logscan.has_problems(res) or missing else 0)


if __name__ == "__main__":
	main()

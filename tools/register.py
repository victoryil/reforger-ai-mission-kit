"""Registra los recursos nuevos de un proyecto (resourceDatabase.rdb) abriendo una instancia PROPIA de Workbench.

Cuando creas prefabs, configs, layouts o texturas como texto, el motor no los conoce hasta que Workbench
los registra. Sin registrar: "invalid prefab resource GUID", no se replican, el inventario no funciona.

Uso:
  python tools/register.py [--project NOMBRE] [--timeout 180]

Abre Workbench con el proyecto, espera a que reescriba resourceDatabase.rdb y cierra SOLO la instancia que ha
abierto (por su PID). Nunca toca un Workbench que ya tuvieras abierto. Al final resume los avisos del log.
"""
import argparse
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit
import logscan


def main():
	ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	ap.add_argument("--project")
	ap.add_argument("--timeout", type=int, default=180)
	a = ap.parse_args()
	cfg = kit.load_config()
	proj = kit.project_dir(cfg, a.project)
	rdb = os.path.join(proj, "resourceDatabase.rdb")
	before = os.path.getmtime(rdb) if os.path.exists(rdb) else 0
	cmd = [cfg["workbench_exe"], "-gproj", os.path.join(proj, "addon.gproj").replace("\\", "/"),
		"-addonsDir", kit.addons_dirs(cfg, for_game=True)]
	print("abriendo Workbench propio para", proj)
	p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	t0 = time.time()
	changed = False
	while time.time() - t0 < a.timeout:
		time.sleep(2)
		if os.path.exists(rdb) and os.path.getmtime(rdb) != before:
			changed = True
			time.sleep(6)
			break
		if p.poll() is not None:
			break
	if p.poll() is None:
		kit.powershell(f"Stop-Process -Id {p.pid} -Force")
	print("resourceDatabase.rdb", "actualizado" if changed else "SIN CAMBIOS (¿no habia nada nuevo, o Workbench tardo demasiado?)")
	logdir = kit.newest_dir(cfg.get("workbench_logs", ""))
	if logdir and os.path.getmtime(logdir) >= t0 - 5:
		log = os.path.join(logdir, "console.log")
		text = kit.read_text(log)
		name = os.path.basename(proj)
		lines = [l for l in text.splitlines() if ("(E)" in l or "(W)" in l) and "$profile:" not in l
			and (name in l or "Can't compile" in l or "metafile" in l)]
		for l in lines[:30]:
			print("  " + l.strip()[:300])
		res = logscan.scan(text, "", "")
		if res["compile"]:
			print(logscan.report(res))
	sys.exit(0 if changed else 2)


if __name__ == "__main__":
	main()

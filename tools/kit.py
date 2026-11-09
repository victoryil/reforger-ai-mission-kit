"""Utilidades comunes del kit: configuracion, procesos, logs.

Toda herramienta lee `kit.config.json` (en la raiz del repo, o la ruta de la variable RKIT_CONFIG).
Copia `kit.config.example.json` a `kit.config.json` y ajusta las rutas de tu PC.
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")


def die(msg, code=1):
	print("ERROR: " + msg, file=sys.stderr)
	sys.exit(code)


def load_config():
	path = os.environ.get("RKIT_CONFIG") or os.path.join(ROOT, "kit.config.json")
	if not os.path.exists(path):
		die(f"no existe {path}. Copia kit.config.example.json a kit.config.json y pon tus rutas (ver docs/02-entorno.md).")
	with open(path, encoding="utf-8") as f:
		cfg = json.load(f)
	cfg["_path"] = path
	return cfg


def project_dir(cfg, name=None):
	"""Carpeta del proyecto: nombre dentro de workbench_addons, ruta absoluta o el de la config."""
	name = name or cfg.get("project")
	if not name:
		die("indica el proyecto (--project NOMBRE) o pon \"project\" en kit.config.json")
	if os.path.isabs(name) and os.path.isdir(name):
		return name
	p = os.path.join(cfg["workbench_addons"], name)
	if not os.path.isdir(p):
		die(f"no existe el proyecto {p}")
	return p


def addons_dirs(cfg, extra=None, for_game=False, include_workbench=True):
	"""Lista para -addonsDir: addons del juego/servidor, mods descargados, proyectos de Workbench y extra.
	include_workbench=False para probar lo empaquetado sin que se cuelen los proyectos sin empaquetar."""
	base = cfg["game_addons"] if for_game else cfg["server_addons"]
	dirs = [base, cfg["downloaded_addons"]]
	if include_workbench:
		dirs.append(cfg["workbench_addons"])
	dirs += cfg.get("extra_addons_dirs", [])
	if extra:
		dirs.append(extra)
	return ",".join(d.replace("\\", "/") for d in dirs if d)


def ensure_out(*parts):
	p = os.path.join(OUT, *parts)
	os.makedirs(p, exist_ok=True)
	return p


# ---------------------------------------------------------------- procesos (solo los nuestros)

def powershell(cmd, timeout=60):
	r = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", cmd], capture_output=True, text=True, timeout=timeout)
	return r.stdout.strip()


def find_processes(marker, name_like="ArmaReforger%"):
	"""PIDs cuyo nombre empieza por ArmaReforger y cuya linea de comandos contiene `marker`."""
	out = powershell(
		"Get-CimInstance Win32_Process -Filter \"Name like '" + name_like + "'\" | "
		"Where-Object { $_.CommandLine -like '*" + marker.replace("'", "''") + "*' } | ForEach-Object { $_.ProcessId }")
	return [int(x) for x in out.split() if x.strip().isdigit()]


def kill_marked(marker):
	"""Cierra SOLO procesos de Arma cuya linea de comandos contiene `marker` (nunca por nombre de ejecutable)."""
	pids = find_processes(marker)
	for pid in pids:
		powershell(f"Stop-Process -Id {pid} -Force")
	return pids


def wait_free(marker, timeout=600):
	"""Espera a que no quede ningun proceso con `marker` (p. ej. un cliente de prueba anterior)."""
	end = time.time() + timeout
	while time.time() < end:
		if not find_processes(marker):
			return True
		time.sleep(3)
	return False


def port_busy(port):
	out = subprocess.run(["netstat", "-ano", "-p", "UDP"], capture_output=True, text=True).stdout
	return any(f":{port} " in l for l in out.splitlines())


def newest_dir(path):
	if not os.path.isdir(path):
		return None
	dirs = [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
	return max(dirs, key=os.path.getmtime) if dirs else None


def read_text(path):
	with open(path, encoding="utf-8", errors="replace") as f:
		return f.read()

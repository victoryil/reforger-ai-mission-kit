"""Comprueba que el entorno esta listo: rutas de kit.config.json, Python y Pillow, git, Steam, puerto libre,
indices generados y el proyecto. Ejecutalo lo primero en un PC nuevo y cuando algo falle sin motivo claro.

Uso:
  python tools/doctor.py
"""
import importlib.util
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit

OK, BAD, WARN = "[OK]  ", "[FALTA]", "[AVISO]"


def line(state, text):
	print(f"{state} {text}")
	return state != BAD


def main():
	good = True
	good &= line(OK if sys.version_info >= (3, 9) else BAD, f"Python {sys.version.split()[0]} (hace falta 3.9 o superior)")
	good &= line(OK if importlib.util.find_spec("PIL") else BAD, "Pillow (capturas e imagenes): pip install pillow")
	line(OK if shutil.which("git") else WARN, "git (para commits pequenos y poder volver atras)")
	cfg = kit.load_config()
	line(OK, f"config: {cfg['_path']}")
	for key in ["workbench_exe", "server_exe", "game_exe", "game_addons", "server_addons", "downloaded_addons", "workbench_addons", "api_docs"]:
		v = cfg.get(key, "")
		good &= line(OK if v and os.path.exists(v) else BAD, f"{key}: {v}")
	wd = cfg.get("work_dir", "")
	line(OK if wd else BAD, f"work_dir (perfiles y partidas de prueba): {wd}")
	proj = os.path.join(cfg["workbench_addons"], cfg.get("project", ""))
	if cfg.get("project") and os.path.isfile(os.path.join(proj, "addon.gproj")):
		line(OK, f"proyecto: {proj}")
		line(OK if os.path.exists(os.path.join(proj, "resourceDatabase.rdb")) else WARN, "resourceDatabase.rdb (si falta: python tools/register.py)")
	else:
		line(WARN, f"proyecto '{cfg.get('project')}' no existe todavia (crea uno con tools/new_project.py)")
	steam = kit.powershell("(Get-Process steam -ErrorAction SilentlyContinue | Select-Object -First 1).Id")
	line(OK if steam else WARN, "Steam abierto (el juego y Workbench lo necesitan para arrancar)")
	busy = kit.port_busy(cfg.get("server_port", 2001))
	line(WARN if busy else OK, f"puerto {cfg.get('server_port', 2001)} " + ("OCUPADO: hay un servidor o juego abierto; las pruebas fallaran" if busy else "libre"))
	line(OK if os.path.exists(os.path.join(kit.OUT, "index", "resources.txt")) else WARN, "indice de recursos (python tools/find.py --build)")
	line(OK if os.path.exists(os.path.join(kit.ROOT, "reference", "generated", "INDEX.tsv")) else WARN, "referencia de la API (python tools/api.py --build)")
	print("\nTodo listo." if good else "\nArregla lo marcado como [FALTA] en kit.config.json (ver docs/02-entorno.md).")
	sys.exit(0 if good else 1)


if __name__ == "__main__":
	main()

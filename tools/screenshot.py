"""Captura la ventana del juego (o de Workbench) a PNG. Solo Windows. Necesita Pillow (pip install pillow).

Uso:
  python tools/screenshot.py SALIDA.png [--title "Arma Reforger"] [--marker TEXTO --log RUTA_LOG --timeout 300]

- Sin --marker: captura ya.
- Con --marker: espera a que el texto aparezca en el log y entonces captura (asi tu script de prueba en el juego
  hace Print("CAPTURA_TIENDA") cuando la pantalla esta lista, y la captura sale en el momento justo).

Para ver la captura, una IA puede abrir el PNG (Claude: Read del archivo; Codex: adjuntar o describir).
"""
import argparse
import ctypes
import ctypes.wintypes as wt
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit

user32 = ctypes.windll.user32
try:
	ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
	user32.SetProcessDPIAware()


def find_window(title_prefix):
	found = []

	@ctypes.WINFUNCTYPE(ctypes.c_bool, wt.HWND, wt.LPARAM)
	def cb(hwnd, _):
		if not user32.IsWindowVisible(hwnd):
			return True
		n = user32.GetWindowTextLengthW(hwnd)
		if n:
			buf = ctypes.create_unicode_buffer(n + 1)
			user32.GetWindowTextW(hwnd, buf, n + 1)
			if buf.value.startswith(title_prefix):
				found.append(hwnd)
		return True

	user32.EnumWindows(cb, 0)
	return found[0] if found else None


def capture(out, title="Arma Reforger"):
	from PIL import ImageGrab
	hwnd = find_window(title)
	if not hwnd:
		print(f"no hay ninguna ventana que empiece por '{title}'")
		return False
	user32.ShowWindow(hwnd, 9)
	user32.SetForegroundWindow(hwnd)
	time.sleep(0.4)
	r = wt.RECT()
	user32.GetWindowRect(hwnd, ctypes.byref(r))
	img = ImageGrab.grab(bbox=(r.left, r.top, r.right, r.bottom), all_screens=True)
	os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
	img.save(out)
	print(f"captura {out} ({img.size[0]}x{img.size[1]})")
	return True


def wait_marker(log_or_dir, marker, timeout):
	"""Espera a que `marker` salga en el log (si es carpeta de logs, usa la sesion mas reciente)."""
	end = time.time() + timeout
	while time.time() < end:
		path = log_or_dir
		if os.path.isdir(path):
			d = kit.newest_dir(path)
			path = os.path.join(d, "console.log") if d else ""
		if path and os.path.exists(path) and marker in kit.read_text(path):
			return True
		time.sleep(0.5)
	return False


def main():
	ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	ap.add_argument("out")
	ap.add_argument("--title", default="Arma Reforger")
	ap.add_argument("--marker")
	ap.add_argument("--log", help="console.log o carpeta logs del perfil")
	ap.add_argument("--timeout", type=int, default=300)
	ap.add_argument("--delay", type=float, default=1.0, help="segundos tras ver la marca (animaciones)")
	a = ap.parse_args()
	if a.marker:
		if not a.log or not wait_marker(a.log, a.marker, a.timeout):
			kit.die(f"no aparecio '{a.marker}' en el log")
		time.sleep(a.delay)
	sys.exit(0 if capture(a.out, a.title) else 1)


if __name__ == "__main__":
	main()

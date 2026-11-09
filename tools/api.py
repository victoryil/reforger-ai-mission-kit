"""Referencia COMPACTA de la API de scripts de Arma Reforger, generada en tu PC desde la documentacion oficial
que trae Arma Reforger Tools (Workbench/docs). Sale siempre de TU version del juego y gasta muchos menos
tokens que leer la documentacion HTML.

Uso:
  python tools/api.py --build                       (una vez por version: crea reference/generated/, ~1-3 min)
  python tools/api.py class SCR_PlayerController    (la clase: base, cadena de herencia y metodos publicos)
  python tools/api.py class LayoutSlot --all        (incluye protegidos y atributos)
  python tools/api.py method SetPadding             (en que clases existe un metodo y su firma)
  python tools/api.py search inventory storage      (clases cuyo nombre o descripcion contienen las palabras)
  python tools/api.py children ScriptComponent      (clases que heredan de una)

Lo generado NO se sube a git (es documentacion de Bohemia Interactive): cada uno lo genera con su Workbench.
"""
import argparse
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit

GEN = os.path.join(kit.ROOT, "reference", "generated")
SUBDIRS = ["ArmaReforgerScriptAPIPublic", "EnfusionScriptAPI"]

TAG = re.compile(r"<[^>]+>")
ROW = re.compile(r'<tr id="row_([0-9_]+)"[^>]*>.*?<a class="el" href="([^"]+)"[^>]*>([^<]+)</a>.*?<td class="desc">(.*?)</td>', re.S)
SECTION = re.compile(r'<h2 [^>]*class="groupheader"[^>]*>(.*?)</h2>', re.S)
MEMITEM = re.compile(r'<tr class="memitem:[^"]*"[^>]*>\s*<td class="memItemLeft"[^>]*>(.*?)</td>\s*<td class="memItemRight"[^>]*>(.*?)</td>\s*</tr>(?:\s*<tr class="memdesc:[^"]*"[^>]*>\s*<td class="mdescLeft">.*?</td>\s*<td class="mdescRight">(.*?)</td>)?', re.S)


def clean(s):
	s = html.unescape(TAG.sub("", s)).replace("\xa0", " ")
	return re.sub(r"\s+", " ", s).strip()


def parse_hierarchy(path, parents, briefs, files):
	text = kit.read_text(path)
	byrow = {}
	for m in ROW.finditer(text):
		row, href, name, desc = m.group(1), m.group(2), clean(m.group(3)), clean(m.group(4))
		byrow[row] = name
		files.setdefault(name, href)
		if desc:
			briefs.setdefault(name, desc)
		parent_row = "_".join(row.strip("_").split("_")[:-1])
		if parent_row:
			parents.setdefault(name, byrow.get(parent_row + "_"))


def parse_class(path):
	text = kit.read_text(path)
	sections = []
	pos = [(m.start(), clean(m.group(1))) for m in SECTION.finditer(text)]
	for i, (start, title) in enumerate(pos):
		if "Documentation" in title:
			break
		end = pos[i + 1][0] if i + 1 < len(pos) else len(text)
		chunk = text[start:end]
		items = []
		for m in MEMITEM.finditer(chunk):
			if "inherit" in chunk[max(0, m.start() - 120):m.start()]:
				continue
			left, right, desc = clean(m.group(1)), clean(m.group(2)), clean(m.group(3) or "")
			sig = (left + " " + right).strip()
			items.append((sig, desc))
		if items:
			sections.append((title, items))
	return sections


def build(cfg):
	parents, briefs, files = {}, {}, {}
	roots = []
	for sub in SUBDIRS:
		h = os.path.join(cfg["api_docs"], sub, "html")
		if os.path.exists(os.path.join(h, "hierarchy.html")):
			roots.append(h)
			parse_hierarchy(os.path.join(h, "hierarchy.html"), parents, briefs, files)
	if not roots:
		kit.die(f"no encuentro la documentacion en {cfg['api_docs']} (Workbench/docs de Arma Reforger Tools)")
	# clases que solo estan en el listado de clases (sin jerarquia)
	for h in roots:
		for f in os.listdir(h):
			if f.startswith("interface") and f.endswith(".html") and "-members" not in f:
				name = f[len("interface"):-5].replace("__", "\x00").replace("_1_1", "::").replace("_", "").replace("\x00", "_")
				files.setdefault(name, f)
	os.makedirs(os.path.join(GEN, "classes"), exist_ok=True)
	idx, meth = [], []
	n = 0
	for name in sorted(files):
		href = files[name]
		path = next((os.path.join(h, href) for h in roots if os.path.exists(os.path.join(h, href))), None)
		if not path:
			continue
		secs = parse_class(path)
		base = parents.get(name) or ""
		chain = []
		b = base
		while b and len(chain) < 12:
			chain.append(b)
			b = parents.get(b)
		lines = [f"class {name}" + (f" : {base}" for _ in [0]).__next__() if base else f"class {name}"]
		if chain[1:]:
			lines.append("  herencia: " + " > ".join(chain))
		if briefs.get(name):
			lines.append("  // " + briefs[name])
		for title, items in secs:
			lines.append(f"  [{title}]")
			for sig, desc in items:
				lines.append("    " + sig + (f"   // {desc}" if desc else ""))
				if "Public" in title and "Attributes" not in title:
					mname = re.search(r"(\w+)\s*\(", sig)
					if mname:
						meth.append(f"{mname.group(1)}\t{name}\t{sig}")
		safe = re.sub(r"[^A-Za-z0-9_]", "_", name)
		with open(os.path.join(GEN, "classes", safe + ".txt"), "w", encoding="utf-8") as f:
			f.write("\n".join(lines) + "\n")
		idx.append(f"{name}\t{base}\t{briefs.get(name, '')}")
		n += 1
	with open(os.path.join(GEN, "INDEX.tsv"), "w", encoding="utf-8") as f:
		f.write("clase\tbase\tdescripcion\n" + "\n".join(idx) + "\n")
	with open(os.path.join(GEN, "METHODS.tsv"), "w", encoding="utf-8") as f:
		f.write("metodo\tclase\tfirma\n" + "\n".join(sorted(meth)) + "\n")
	print(f"API: {n} clases, {len(meth)} metodos publicos -> {GEN}")


def load_index():
	p = os.path.join(GEN, "INDEX.tsv")
	if not os.path.exists(p):
		kit.die("no hay referencia generada: python tools/api.py --build")
	rows = {}
	with open(p, encoding="utf-8") as f:
		next(f)
		for l in f:
			c, b, d = (l.rstrip("\n").split("\t") + ["", ""])[:3]
			rows[c] = (b, d)
	return rows


def show_class(name, all_members):
	safe = re.sub(r"[^A-Za-z0-9_]", "_", name)
	p = os.path.join(GEN, "classes", safe + ".txt")
	if not os.path.exists(p):
		rows = load_index()
		near = [c for c in rows if name.lower() in c.lower()][:15]
		kit.die("no existe esa clase. Parecidas: " + ", ".join(near))
	out, skip = [], False
	for l in kit.read_text(p).splitlines():
		if l.startswith("  ["):
			skip = not all_members and ("Protected" in l or "Private" in l or "Attributes" in l)
		if not skip:
			out.append(l)
	print("\n".join(out))


def main():
	sys.stdout.reconfigure(encoding="utf-8")
	ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	ap.add_argument("cmd", nargs="?", choices=["class", "method", "search", "children"])
	ap.add_argument("args", nargs="*")
	ap.add_argument("--build", action="store_true")
	ap.add_argument("--all", action="store_true")
	ap.add_argument("--max", type=int, default=40)
	a = ap.parse_args()
	cfg = kit.load_config()
	if a.build:
		build(cfg)
		return
	if not a.cmd or not a.args:
		ap.print_help()
		return
	if a.cmd == "class":
		show_class(a.args[0], a.all)
	elif a.cmd == "method":
		p = os.path.join(GEN, "METHODS.tsv")
		n = 0
		with open(p, encoding="utf-8") as f:
			for l in f:
				m, c, s = (l.rstrip("\n").split("\t") + ["", ""])[:3]
				if m.lower() == a.args[0].lower() or (a.args[0].lower() in m.lower() and len(a.args) > 1 and a.args[1] == "~"):
					print(f"{c}: {s}")
					n += 1
					if n >= a.max:
						break
		if not n:
			print("sin resultados (prueba: api.py method NOMBRE ~  para buscar por parte del nombre)")
	elif a.cmd == "search":
		words = [w.lower() for w in a.args]
		n = 0
		for c, (b, d) in load_index().items():
			if all(w in (c + " " + d).lower() for w in words):
				print(f"{c}" + (f" : {b}" if b else "") + (f"  // {d}" if d else ""))
				n += 1
				if n >= a.max:
					break
	elif a.cmd == "children":
		for c, (b, d) in load_index().items():
			if b == a.args[0]:
				print(c)


if __name__ == "__main__":
	main()

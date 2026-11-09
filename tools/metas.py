"""Crea el .meta (con un GUID nuevo) de cada recurso de un proyecto que no lo tenga: prefabs (.et), mundos (.ent),
configs (.conf), layouts (.layout), imagesets y texturas (.edds). Sin .meta, Workbench asigna GUID por su
cuenta y tus referencias "{GUID}ruta" escritas a mano no coincidirian.

Uso:
  python tools/metas.py [--project NOMBRE]     -> imprime "{GUID}ruta" de cada recurso (nuevos marcados)

Despues: python tools/register.py para que Workbench los registre.
"""
import argparse
import io
import os
import re
import secrets
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit

KINDS = {".et": "EntityTemplateResourceClass", ".ent": "ENTResourceClass", ".conf": "CONFResourceClass",
	".layout": "LayoutResourceClass", ".imageset": "ImageSetResourceClass", ".styles": "StylesResourceClass"}
PLATFORMS = ["XBOX_ONE", "XBOX_SERIES", "PS4", "PS5", "HEADLESS"]
TEXTURE_META = """MetaFileClass {{
 Name "{{{guid}}}{rel}"
 Configurations {{
  PNGResourceClass PC : "{{DC555BD399D92412}}Configs/System/ResourceTypes/PC/TextureUnspecified.conf" {{
  }}
  PNGResourceClass XBOX_ONE : "{{8F13AE697AE60784}}Configs/System/ResourceTypes/XBOX_ONE/TextureUnspecified.conf" {{
  }}
  PNGResourceClass XBOX_SERIES : "{{D28E01700D90F52C}}Configs/System/ResourceTypes/XBOX_SERIES/TextureUnspecified.conf" {{
  }}
  PNGResourceClass PS4 : "{{C6CD3D8752652D2A}}Configs/System/ResourceTypes/PS4/TextureUnspecified.conf" {{
  }}
  PNGResourceClass PS5 : "{{6248F71B9D7C1E93}}Configs/System/ResourceTypes/PS5/TextureUnspecified.conf" {{
  }}
  PNGResourceClass HEADLESS : "{{699C82A6807668A7}}Configs/System/ResourceTypes/HEADLESS/TextureUnspecified.conf" {{
  }}
 }}
}}
"""


def new_guid():
	return secrets.token_hex(8).upper()


def meta_text(rel, guid):
	ext = os.path.splitext(rel)[1]
	if ext == ".edds":
		return TEXTURE_META.format(guid=guid, rel=rel)
	k = KINDS[ext]
	lines = ["MetaFileClass {", f' Name "{{{guid}}}{rel}"', " Configurations {", f"  {k} PC {{", "  }"]
	for pl in PLATFORMS:
		lines += [f"  {k} {pl} : PC {{", "  }"]
	lines += [" }", "}"]
	return "\n".join(lines) + "\n"


def ensure_metas(proj):
	"""Devuelve {ruta_relativa: guid} de todos los recursos, creando los .meta que falten."""
	out = {}
	for dp, dn, fn in os.walk(proj):
		dn[:] = [d for d in dn if d not in (".git", "tools", "__pycache__", "docs")]
		for f in fn:
			ext = os.path.splitext(f)[1]
			if ext not in KINDS and ext != ".edds":
				continue
			p = os.path.join(dp, f)
			rel = os.path.relpath(p, proj).replace("\\", "/")
			meta = p + ".meta"
			if os.path.exists(meta):
				m = re.search(r'Name "\{([0-9A-F]{16})\}', kit.read_text(meta))
				if m:
					out[rel] = (m.group(1), False)
					continue
			g = new_guid()
			io.open(meta, "w", encoding="utf-8", newline="\n").write(meta_text(rel, g))
			out[rel] = (g, True)
	return out


def main():
	ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	ap.add_argument("--project")
	a = ap.parse_args()
	cfg = kit.load_config()
	proj = kit.project_dir(cfg, a.project)
	for rel, (g, new) in sorted(ensure_metas(proj).items()):
		print(f"{{{g}}}{rel}" + ("   (nuevo)" if new else ""))


if __name__ == "__main__":
	main()

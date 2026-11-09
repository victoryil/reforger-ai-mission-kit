"""Crea un proyecto de mision nuevo y COMPILABLE desde templates/project, con todo conectado:
addon.gproj, mundo (sub-escena del mapa con su AIWorld y navmesh), escenario (.conf), GameMode, facciones,
equipo, punto de aparicion, gestor de mision por fases, autotests de servidor y cliente, guardado y docs.

Uso (minimo):
  python tools/new_project.py --name OpAzor --prefix OA --title "Operacion Azor" --map Eden

Opciones utiles (si no las das, se usan las del juego base: US contra USSR):
  --map Eden|Arland|Cain|<{GUID}ruta/al/mundo.ent>
  --player-faction US  --player-faction-conf "{GUID}Configs/Factions/US.conf"
  --enemy-faction-conf "{GUID}Configs/Factions/USSR.conf"
  --loadout "{GUID}Configs/Loadouts/US/Regular/Loadout_US_Rifleman.conf"
  --enemy-group "{GUID}Prefabs/Groups/OPFOR/....et"   --player-character "{GUID}Prefabs/Characters/....et"
  --spawn "x y z"  --phase1 "x y z"  --phase2 "x y z"   (luego afinalas con tools/map_locations.py)
  --deps GUID1,GUID2 (mods de los que depende: FFAA, RHS, MCUIK...)   --players 4   --author "Yo"
  --update-config   (pone este proyecto como "project" en kit.config.json)

Los GUIDs de facciones, equipos y grupos salen de: python tools/find.py <palabras> .conf/.et
"""
import argparse
import io
import json
import os
import re
import secrets
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit
import metas

TEMPLATE = os.path.join(kit.ROOT, "templates", "project")
MAPS = {
	"eden": ("{853E92315D1D9EFE}worlds/Eden/Eden.ent", "{70CCCF16487C927F}Prefabs/AI/SCR_AIWorld_Eden.et",
		"{AD5F99CD7C59D5E0}worlds/GameMaster/Navmeshes/GM_Eden.nmn", "{C35ECF3276824654}worlds/GameMaster/Navmeshes/GM_Eden_vehicles.nmn", "5000 0 5000"),
	"arland": ("{A9806AF617972E97}worlds/Arland/Arland.ent", "{01DC74137CFDDB6A}Prefabs/AI/SCR_AIWorld_Arland.et",
		"{D8EF7131FB31AF97}worlds/GameMaster/Navmeshes/GM_Arland.nmn", "{A0AEEB1E7EF474FA}worlds/GameMaster/Navmeshes/GM_Arland_vehicles.nmn", "2000 0 2000"),
	"cain": ("{1EA95DAE3230BEB0}worlds/Cain/Cain.ent", "{672531FAC0834C06}Prefabs/AI/SCR_AIWorld_Cain.et",
		"{ACBE49C3E71A9E65}worlds/GameMaster/Navmeshes/GM_Cain.nmn", "{27D8B11BF4E78009}worlds/GameMaster/Navmeshes/GM_Cain_vehicles.nmn", "6000 0 6000"),
}
DEFAULTS = {
	"player_faction": "US",
	"player_faction_conf": "{5EB46557DF2AA24F}Configs/Factions/US.conf",
	"enemy_faction_conf": "{09727032415AC39B}Configs/Factions/USSR.conf",
	"loadout": "{7C7C65FD583E6612}Configs/Loadouts/US/Regular/Loadout_US_Rifleman.conf",
	"enemy_group": "{E552DABF3636C2AD}Prefabs/Groups/OPFOR/Group_USSR_RifleSquad.et",
	"player_character": "{26A9756790131354}Prefabs/Characters/Factions/BLUFOR/US_Army/Character_US_Rifleman.et",
}


def main():
	ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	ap.add_argument("--name", required=True, help="nombre interno sin espacios (carpeta y ID)")
	ap.add_argument("--prefix", required=True, help="prefijo de clases, 2-4 letras (p. ej. OA)")
	ap.add_argument("--title", required=True)
	ap.add_argument("--map", default="Eden")
	ap.add_argument("--author", default="")
	ap.add_argument("--description", default="")
	ap.add_argument("--players", type=int, default=4)
	ap.add_argument("--player-faction", default=DEFAULTS["player_faction"])
	ap.add_argument("--player-faction-conf", default=DEFAULTS["player_faction_conf"])
	ap.add_argument("--enemy-faction-conf", default=DEFAULTS["enemy_faction_conf"])
	ap.add_argument("--loadout", default=DEFAULTS["loadout"])
	ap.add_argument("--enemy-group", default=DEFAULTS["enemy_group"])
	ap.add_argument("--player-character", default=DEFAULTS["player_character"])
	ap.add_argument("--spawn")
	ap.add_argument("--phase1")
	ap.add_argument("--phase2")
	ap.add_argument("--deps", default="")
	ap.add_argument("--update-config", action="store_true")
	a = ap.parse_args()
	cfg = kit.load_config()

	if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", a.name):
		kit.die("--name: solo letras, numeros y _ (sin espacios)")
	if not re.fullmatch(r"[A-Z][A-Z0-9]{1,3}", a.prefix):
		kit.die("--prefix: 2-4 mayusculas/numeros, empezando por letra")
	dst = os.path.join(cfg["workbench_addons"], a.name)
	if os.path.exists(dst):
		kit.die(f"ya existe {dst}")

	m = MAPS.get(a.map.lower())
	if m:
		map_ent, aiworld, nav_s, nav_v, center = m
	else:
		map_ent, aiworld, nav_s, nav_v, center = a.map, "{E0A05C76552E7F58}Prefabs/AI/SCR_AIWorld.et", "", "", "5000 0 5000"
		print("AVISO: mapa propio: pon a mano el AIWorld y la navmesh en Worlds/<name>/<name>_Layers/default.layer")
	spawn = a.spawn or center
	guid = secrets.token_hex(8).upper()
	deps = "\n".join(f'  "{d.strip()}"' for d in a.deps.split(",") if d.strip())
	values = {
		"NAME": a.name, "P": a.prefix, "TITLE": a.title, "AUTHOR": a.author, "DESCRIPTION": a.description or a.title,
		"GUID": guid, "DEPENDENCIES": deps, "PLAYERS": str(a.players),
		"MAP_ENT": map_ent, "AIWORLD": aiworld, "NAV_SOLDIERS": nav_s, "NAV_VEHICLES": nav_v,
		"SPAWN_POS": spawn, "PHASE1_POS": a.phase1 or spawn, "PHASE2_POS": a.phase2 or spawn,
		"PLAYER_FACTION_KEY": a.player_faction, "PLAYER_FACTION_CONF": a.player_faction_conf,
		"ENEMY_FACTION_CONF": a.enemy_faction_conf, "PLAYER_LOADOUT": a.loadout,
		"ENEMY_GROUP": a.enemy_group, "PLAYER_CHARACTER": a.player_character,
		"SELFTEST_PARAM": a.prefix.lower() + "SelfTest", "CLIENTTEST_PARAM": a.prefix.lower() + "ClientTest",
	}

	# 1) copiar renombrando PFX -> prefijo y NAME -> nombre
	for dp, dn, fn in os.walk(TEMPLATE):
		rel_dir = os.path.relpath(dp, TEMPLATE)
		out_dir = os.path.join(dst, rel_dir.replace("PFX", a.prefix).replace("NAME", a.name)) if rel_dir != "." else dst
		os.makedirs(out_dir, exist_ok=True)
		for f in fn:
			shutil.copyfile(os.path.join(dp, f), os.path.join(out_dir, f.replace("PFX", a.prefix).replace("NAME", a.name)))

	# 2) valores simples e IDs nuevos
	ids = {}
	def fill(text):
		text = re.sub(r"\{\{ID:(\w+)\}\}", lambda mm: "{" + ids.setdefault(mm.group(1), secrets.token_hex(8).upper()) + "}", text)
		for k, v in values.items():
			text = text.replace("{{" + k + "}}", v)
		return text
	files = [os.path.join(dp, f) for dp, dn, fn in os.walk(dst) for f in fn]
	for p in files:
		s = io.open(p, encoding="utf-8").read()
		io.open(p, "w", encoding="utf-8", newline="\n").write(fill(s))

	# 3) .meta con GUID para cada recurso, y referencias {{REF:ruta}} -> {GUID}ruta
	guids = metas.ensure_metas(dst)
	def ref(mm):
		rel = mm.group(1).replace("PFX", a.prefix).replace("NAME", a.name)
		if rel not in guids:
			kit.die(f"referencia a un recurso que no existe en la plantilla: {rel}")
		return "{" + guids[rel][0] + "}" + rel
	for p in files:
		s = io.open(p, encoding="utf-8").read()
		n = re.sub(r"\{\{REF:([^}]+)\}\}", ref, s)
		if n != s:
			io.open(p, "w", encoding="utf-8", newline="\n").write(n)
	left = [p for p in files if "{{" in io.open(p, encoding="utf-8").read()]
	if left:
		print("AVISO: quedan marcadores sin rellenar en:", left)

	# repositorio git propio del proyecto con un primer commit (para poder volver atras)
	if shutil.which("git"):
		import subprocess
		subprocess.run(["git", "init", "-q"], cwd=dst)
		subprocess.run(["git", "add", "-A"], cwd=dst)
		subprocess.run(["git", "commit", "-q", "-m", "Proyecto inicial (reforger-ai-mission-kit)"], cwd=dst)

	world = "{" + guids[f"Worlds/{a.name}/{a.name}.ent"][0] + f"}}Worlds/{a.name}/{a.name}.ent"
	scenario = "{" + guids[f"Missions/{a.name}.conf"][0] + f"}}Missions/{a.name}.conf"
	print(f"\nproyecto creado: {dst}")
	print(f"  GUID del mod:  {guid}")
	print(f"  mundo:         {world}")
	print(f"  escenario:     {scenario}")
	print(f"  autotests:     -{values['SELFTEST_PARAM']}  /  -{values['CLIENTTEST_PARAM']}")
	if a.update_config:
		path = cfg["_path"]
		data = json.load(open(path, encoding="utf-8"))
		data.update({"project": a.name, "project_guid": guid, "world": world, "scenario": scenario,
			"selftest_param": values["SELFTEST_PARAM"], "clienttest_param": values["CLIENTTEST_PARAM"],
			"client_faction": a.player_faction, "save_files_to_clear": [f"profile/{a.name}/partida.json"],
			"dumpmap_param": a.prefix + "DumpMap"})
		json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
		print(f"  kit.config.json actualizado (project = {a.name})")
	print("\nSiguiente: python tools/register.py   y   python tools/server_test.py --until \"FIN del autotest\"")


if __name__ == "__main__":
	main()

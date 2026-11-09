# 02 · Entorno

## Qué hace falta (Windows)

| Programa | Dónde | Para qué |
|---|---|---|
| Arma Reforger | Steam | el cliente de prueba (`ArmaReforgerSteamDiag.exe`) |
| Arma Reforger Tools | Steam → Biblioteca → Herramientas | Workbench: registrar, empaquetar y publicar; trae la documentación de la API |
| Arma Reforger Server | Steam → Herramientas (Arma Reforger Server) | servidor dedicado para las pruebas |
| Python 3.9 o superior | python.org o Microsoft Store | las herramientas |
| Pillow | `pip install pillow` | capturas e imágenes |
| git | git-scm.com | commits pequeños y poder volver atrás |
| Codex o Claude Code | — | el asistente |

Steam tiene que estar **abierto** para que arranquen el juego y Workbench.

## Configuración: `kit.config.json`

Copia `kit.config.example.json` a `kit.config.json` (no se sube a git) y ajusta las rutas:

| Clave | Qué es |
|---|---|
| `workbench_exe`, `server_exe`, `game_exe` | ejecutables (en Steam: clic derecho → Administrar → Ver archivos locales) |
| `game_addons`, `server_addons` | carpeta `addons` del juego y del servidor |
| `downloaded_addons` | mods del Workshop: `Documents/My Games/ArmaReforger/addons` (puede estar en OneDrive) |
| `workbench_addons` | tus proyectos: `Documents/My Games/ArmaReforgerWorkbench/addons` |
| `workbench_logs` | `Documents/My Games/ArmaReforgerWorkbench/logs` |
| `api_docs` | `…/Arma Reforger Tools/Workbench/docs` |
| `work_dir` | carpeta para perfiles y partidas de prueba (p. ej. `C:/ArmaReforgerTest`) |
| `project`, `project_guid`, `world`, `scenario` | tu misión (los rellena `new_project.py --update-config`) |
| `selftest_param`, `clienttest_param`, `dumpmap_param` | parámetros que activan los autotests y el volcado del mapa |
| `client_faction` | facción en la que despliega el cliente de prueba (`-tdmf`) |
| `save_files_to_clear` | partidas guardadas de la carpeta de pruebas que se borran antes de cada prueba |

Para tener varias configuraciones (una por misión), usa la variable de entorno `RKIT_CONFIG=ruta/al/config.json`.

## Primera vez

```
python tools/doctor.py
python tools/find.py --build        (1-2 min; repetir al instalar mods)
python tools/api.py --build         (2-4 min; repetir al actualizar el juego)
```

## Mods que se usarán

- Suscríbete en el Workshop desde el juego y ábrelo una vez para que se descarguen en `downloaded_addons`.
- Sus GUID se ponen en `Dependencies` del `addon.gproj` (`--deps` en `new_project.py`). El GUID es la parte final del nombre de la carpeta del mod: `FFAA-Core-DevBranch_6872C9965058DE7A` → `6872C9965058DE7A`.
- Para ver qué prefabs trae un mod: `python tools/find.py --source NombreCarpeta palabra`.

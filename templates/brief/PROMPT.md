# Mensaje para pegar en tu IA (Codex o Claude Code)

Abre el asistente **dentro de la carpeta de este repositorio** (`reforger-ai-mission-kit`), adjunta o pega tu `MISION.md` relleno, y pega esto:

---

Vas a crear una misión completa de Arma Reforger con las herramientas de este repositorio.

1. Lee `AGENTS.md` entero y después `docs/03-lecciones-enfusion.md`. Son las reglas de trabajo y los errores que ya se conocen.
2. Ejecuta `python tools/doctor.py`. Si falta algo, dime exactamente qué tengo que instalar o qué ruta poner en `kit.config.json`.
3. Si no existen todavía, genera los índices: `python tools/find.py --build` y `python tools/api.py --build`.
4. Lee mi encargo (`MISION.md`, adjunto abajo) y escríbeme un **plan por fases pequeñas**. Para cada fase indica qué harás, cómo lo probarás y qué tendré que mirar yo. Si falta algo imprescindible, pregúntamelo todo junto en ese mismo mensaje.
5. Cuando te dé el visto bueno (o si en el encargo pone que no hace falta), empieza:
   1. `tools/new_project.py` con mi mapa y mis facciones (busca los GUID con `tools/find.py`).
   2. `tools/register.py`.
   3. `tools/server_test.py --until "FIN del autotest"`, que debe pasar antes de tocar nada.
   4. Sitios: `tools/map_locations.py`.
   5. Ve fase a fase siguiendo el flujo de `AGENTS.md`: programar, compilar, autotest, cliente con capturas cuando haya algo visible, commit y DEVLOG.
6. Al acabar cada fase, dime qué está probado en servidor, qué has visto en el cliente (con la captura) y qué tengo que probar yo jugando.

No inventes GUIDs, coordenadas ni funciones: usa `find.py`, `map_locations.py` y `api.py`. No publiques nada ni cierres mis programas.

Mi encargo:

(pega aquí tu MISION.md)

---

## Consejos

- **Primera sesión:** que haga el esqueleto y la primera fase, y pruébalo tú en el juego antes de seguir. Así ves pronto si algo del encargo se ha entendido mal.
- **Si la conversación se hace larga:** en una sesión nueva, pídele que lea `AGENTS.md` y el `docs/DEVLOG.md` del proyecto y siga desde ahí.
- **Si algo falla jugando:** pégale el error tal cual sale (o el `console.log` de `Documents/My Games/ArmaReforger/logs`). Que lo reproduzca en `server_test.py` o `client_test.py` antes de darlo por arreglado.

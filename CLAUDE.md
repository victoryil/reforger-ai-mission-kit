# CLAUDE.md

Las instrucciones de este repositorio son las de @AGENTS.md (las mismas para Claude y para Codex). Léelas enteras.

Notas propias de Claude Code:
- Las pruebas largas (`server_test.py`, `client_test.py`, `api.py --build`, `find.py --build`) tardan minutos. Lánzalas en segundo plano y sigue con otra cosa; no hagas `sleep` en primer plano.
- Para **ver** una captura de `out/shots/*.png`, ábrela con la herramienta Read: ves la imagen.
- Usa Grep/Glob sobre `reference/generated/` y `out/index/resources.txt` en vez de leerlos enteros (son grandes).
- Si el usuario tiene memoria persistente, guarda lo no obvio (rutas de su PC, preferencias), no lo que ya está en el repo.

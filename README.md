# reforger-ai-mission-kit

**Kit para crear misiones de Arma Reforger con un asistente de IA** (Codex, Claude Code u otro), con el método, las herramientas y la plantilla con los que se hicieron una campaña entera ([Reconquista Canaria](https://github.com/victoryil)) y los mods [MCUIK](https://victoryil.github.io/MCUIK/) y [MCES](https://victoryil.github.io/MCES/).

La idea es que la IA:
- no programe a ciegas, sino que **compruebe cada paso en el motor real**: compila, autotest en un servidor dedicado y capturas del juego;
- no gaste tokens buscando a mano: **índices de recursos y de la API** que se consultan en un segundo;
- no repita errores conocidos: **lecciones** documentadas y una **plantilla de misión que ya compila y pasa su autotest**.

## Qué trae

| Carpeta | Contenido |
|---|---|
| `AGENTS.md` / `CLAUDE.md` | instrucciones para la IA (Codex lee `AGENTS.md`; Claude Code, `CLAUDE.md`, que lo incluye) |
| `docs/` | el método de trabajo, el entorno, las lecciones de Enfusion, las pruebas, recursos y mundo, publicar, interfaz y la API |
| `tools/` | herramientas en Python: proyecto nuevo, buscar recursos y API, registrar, empaquetar, servidor y cliente de prueba, capturas, logs, sitios del mapa |
| `templates/project/` | misión mínima completa: mundo, modo de juego, facciones, aparición, fases, red, guardado y autotests |
| `templates/brief/` | ficha de encargo (`MISION.md`) y el mensaje para pegar a la IA (`PROMPT.md`) |
| `reference/` | chuleta de la API y recetas de código probadas (red, IA, mapa, acciones, componentes colocables) |

## Empezar (persona)

1. Instala Arma Reforger, **Arma Reforger Tools** y **Arma Reforger Server** desde Steam; Python 3.9+ y `pip install pillow`; y git.
2. Clona este repositorio. Copia `kit.config.example.json` a `kit.config.json` y pon tus rutas ([docs/02-entorno.md](docs/02-entorno.md)).
3. `python tools/doctor.py` (todo en [OK]).
4. Rellena [`templates/brief/MISION.md`](templates/brief/MISION.md).
5. Abre Codex o Claude Code **en esta carpeta** y pega el mensaje de [`templates/brief/PROMPT.md`](templates/brief/PROMPT.md) con tu ficha.

La IA hará el resto: proyecto, fases, pruebas y capturas. Te irá diciendo qué está probado y qué tienes que mirar tú jugando.

## Lo que hacen las herramientas

```text
python tools/new_project.py --name OpAzor --prefix OA --title "Operación Azor" --map Eden --update-config
python tools/register.py                         # registra recursos con un Workbench propio (no toca el tuyo)
python tools/server_test.py --until "FIN del autotest"
python tools/map_locations.py --grep pueblo      # sitios del mapa con coordenadas
python tools/find.py Group USSR .et              # {GUID}ruta de prefabs del juego y de tus mods
python tools/api.py class SCR_AIGroup            # API compacta (generada de tu Workbench)
python tools/pack.py
python tools/client_test.py --shots CAPTURA_JUEGO,CAPTURA_MAPA --until "FIN autotest de cliente"
```

Lo que hace `new_project.py` y comprueban las pruebas de la plantilla:
- **Servidor:** el proyecto compila y su autotest recorre la misión hasta la victoria.
- **Cliente:** en el juego real aparece en el sitio elegido, ve el objetivo y el mapa se centra en él. Las capturas quedan en `out/shots/`.

## Requisitos y límites

- **Solo Windows** (las herramientas usan rutas y procesos de Windows).
- **La primera publicación en el Workshop** la haces tú desde Workbench.
- **Colocar decorado a ojo** es mejor hacerlo en el editor de Workbench. La IA puede poner entidades por coordenadas, pero no ve el resultado salvo con capturas.
- **Referencia de la API:** se genera en tu PC desde la documentación que trae Arma Reforger Tools. No se incluye aquí porque es de Bohemia Interactive y cambia con cada versión.

## Créditos

Hecho por victoryil y Claude (Anthropic) durante el desarrollo de Reconquista Canaria. Arma Reforger y Enfusion son de Bohemia Interactive; este kit no está afiliado a Bohemia Interactive.

## Licencia

[MIT](LICENSE): puedes usarlo, modificarlo y redistribuirlo (también en tus mods) manteniendo el aviso de copyright.

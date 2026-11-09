# AGENTS.md — instrucciones para el asistente de IA (Codex, Claude Code u otro)

Vas a crear o modificar una **misión de Arma Reforger** (motor Enfusion, lenguaje Enforce Script) en el PC del usuario, con herramientas de este repositorio. Este archivo es tu contrato de trabajo. Léelo entero antes de empezar y vuelve a él si dudas.

Documentación ampliada en `docs/`:
- [01 Cómo trabajar](docs/01-como-trabajo.md)
- [02 Entorno](docs/02-entorno.md)
- [03 Lecciones de Enfusion](docs/03-lecciones-enfusion.md) (**obligatoria**)
- [04 Pruebas](docs/04-pruebas.md)
- [05 Recursos, prefabs y mundo](docs/05-recursos-y-mundo.md)
- [06 Empaquetar y publicar](docs/06-empaquetar-y-publicar.md)
- [07 Interfaz](docs/07-interfaz.md)
- [08 API](docs/08-api.md)

Recetas de código probadas: `reference/patterns/`. Chuleta de la API: `reference/cheatsheet.md`.

## 0. Antes de nada

1. `python tools/doctor.py`. Si algo sale [FALTA], arréglalo en `kit.config.json` (copia de `kit.config.example.json`) o pídeselo al usuario.
2. Si no existen todavía, genera los índices. Tardan unos minutos, pero ahorran muchísimos tokens después:
   - `python tools/find.py --build`
   - `python tools/api.py --build`
3. Lee el encargo del usuario (`templates/brief/MISION.md` relleno, o lo que te haya pasado). Si falta algo **imprescindible**, pregunta una vez y en bloque. Si no, decide algo razonable y apúntalo en el DEVLOG.

## 1. Flujo obligatorio (por fases pequeñas)

```
plan por fases → (fase) programar → compilar → autotest servidor → [cliente + capturas si hay interfaz o red] → commit → siguiente
```

- **Proyecto nuevo:**
  1. `python tools/new_project.py --name X --prefix XX --title "..." --map Eden|Arland|Cain [facciones/equipos] --update-config`
  2. `python tools/register.py`
  3. `python tools/server_test.py --until "FIN del autotest"`

  Debe salir `OK=n FALLO=0`. Así compruebas que la base funciona antes de tocar nada.
- **Sitios del mapa:** `python tools/map_locations.py` da ciudades, pueblos, bases… con coordenadas `x y z`. Elige posiciones de ahí; nunca te inventes coordenadas.
- **Recursos:** `python tools/find.py palabras .et` da `{GUID}ruta`. **Nunca inventes un GUID.** Copia exactamente lo que salga.
- **API:**
  - `python tools/api.py class Clase`
  - `python tools/api.py method Metodo`
  - `python tools/api.py search palabras`

  Consúltala antes de usar una función que no hayas visto en este repo.
- **Después de crear o renombrar prefabs, configs, layouts o texturas:**
  1. `python tools/metas.py`
  2. `python tools/register.py`
- **Cada cambio de código:**
  1. `python tools/server_test.py --until "FIN del autotest"`.
  2. Lee el resumen. Si hay errores de compilación o `Virtual Machine Exception`, arréglalos antes de seguir.
- **Interfaz, red o algo que se vea:**
  1. `python tools/pack.py` (y las dependencias propias).
  2. `python tools/client_test.py --shots CAPTURA_X,... --until "FIN autotest de cliente"`.
  3. **Mira las capturas** en `out/shots/` y corrige lo que se vea mal.
  4. La primera vez, pide permiso al usuario: abre una ventana del juego.
- **Commit pequeño** por cada paso que funcione (`git` dentro de la carpeta del proyecto), con mensaje claro.
- **Documentación del proyecto:** apunta en `docs/DEVLOG.md` qué has hecho, qué has probado y qué queda.

## 2. Reglas que NO se rompen

- **Procesos:**
  - Nunca cierres procesos por nombre de ejecutable (`taskkill /IM ArmaReforgerServer.exe`): el usuario puede tener un servidor de verdad. Las herramientas cierran solo lo que abren.
  - Nunca cierres el Workbench ni el juego del usuario.
- **Pruebas:** no lances dos pruebas a la vez, ni con un servidor del usuario encendido. Todos usan el puerto UDP 2001 (ver doc 04).
- **GUIDs:** no inventes GUIDs, rutas de prefabs, nombres de clases ni firmas. Comprueba con `find.py` / `api.py`.
- **Código ajeno:** no copies código de otros mods (muchos tienen licencia No-Derivatives). Puedes depender de ellos y usar sus prefabs.
- **Publicar:** no publiques en el Workshop ni subas nada a internet sin que el usuario lo pida. La primera publicación la hace el usuario desde Workbench.
- **Secretos:** no guardes contraseñas ni claves en archivos del proyecto.
- **Archivos del usuario:** no sobrescribas archivos que el usuario edite a mano en Workbench (capas `.layer` que haya tocado) sin preguntar; mira `git status` antes.
- **Resultados:** sé honesto con los resultados. Si una prueba falla o no has podido verlo en el juego, dilo.

## 3. Enforce Script: errores que ya han pasado (resumen; detalle en docs/03)

| Error | Causa | Solución |
|---|---|---|
| `NULL pointer to instance. Variable 'c'` | un objeto nuevo guardado solo en un **parámetro** se libera al momento | variable local: `Color c = color; if (!c) c = ...;` |
| `Expected name, not a keyword` | nombres reservados: `out`, `debug`, `auto`, `ref`, `class`, `null`… | otro nombre |
| `Failed move` (IA quieta) | waypoint fuera de la navmesh, o el mundo sin navmesh | `Util.OnNavmesh(pos)`; AIWorld con su `.nmn` (lo pone la plantilla) |
| `invalid prefab resource GUID` / inventario no funciona | prefab sin registrar | `tools/metas.py` + `tools/register.py` |
| `Unable to start replication` | puerto 2001 ocupado | cierra la otra prueba o el servidor |
| algo replicado no llega al cliente | falta `Replication.BumpMe()` tras cambiar un `[RplProp()]` | llámalo en el servidor |
| datos «de la partida anterior» tras «Reload Game» | los `static` sobreviven | `Reset()` de tus estáticos al iniciar el GameMode |
| `%%` sale tal cual | `string.Format` no escapa `%` | escribe `%` |
| tildes que no pasan a mayúscula | `ToUpper()` no toca tildes y modifica en sitio | función propia |
| no compila `bool * float` | no hay conversión implícita | usa un `if` |

## 4. Definición de «hecho» para cada fase

- Compila sin errores y el autotest de servidor pasa (`FALLO=0`).
- Si toca la interfaz o la red: el cliente de prueba pasa y has **mirado** las capturas.
- Hay commit y una línea en el DEVLOG.
- Al usuario le dices qué está probado en servidor, qué se ha visto en el cliente y qué falta probar jugando.

## 5. Herramientas (todas: `python tools/<x>.py --help`)

| Herramienta | Para qué |
|---|---|
| `doctor.py` | comprobar el entorno |
| `new_project.py` | proyecto nuevo completo y compilable desde la plantilla |
| `find.py` | buscar `{GUID}ruta` de prefabs, configs, mundos, navmesh… |
| `api.py` | API compacta: clase, método, búsqueda, hijas |
| `pakgrep.py` | ver el texto de prefabs, layouts y configs del juego (sintaxis exacta) |
| `map_locations.py` | sitios con nombre del mapa y coordenadas |
| `metas.py` | crear los `.meta` (GUID) que falten |
| `register.py` | registrar recursos con una instancia propia de Workbench |
| `server_test.py` | servidor de pruebas + autotest + resumen del log |
| `pack.py` | empaquetar proyectos (como publicar, pero en local) |
| `client_test.py` | juego real con tu escenario + autotest de cliente + capturas |
| `screenshot.py` | capturar la ventana del juego (ya o al ver una marca en el log) |
| `logscan.py` | resumir cualquier `console.log` |
| `png2edds.py` | PNG → textura `.edds` sin Workbench |

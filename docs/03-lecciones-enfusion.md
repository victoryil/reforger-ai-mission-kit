# 03 · Lecciones de Enfusion (léelas antes de programar)

Todo lo de aquí ha pasado de verdad haciendo misiones con IA. Cada punto dice el síntoma, la causa y qué hacer.

## Enforce Script (el lenguaje)

- **Objetos guardados solo en un parámetro se liberan.**
  - Síntoma: `NULL pointer to instance. Variable 'c'`.
  - Causa: `void F(Color c = null) { if (!c) c = Color.FromRGBA(...); w.SetColor(c); }`. El objeto nuevo asignado al parámetro no tiene a nadie que lo retenga.
  - Solución: `Color col = c; if (!col) col = ...;` (variable local) o un miembro `ref`.
- **Palabras reservadas como nombre:** `out`, `debug`, `auto`, `ref`, `class`, `null`, `this`, `super`, `owned`, `notnull`, `private`, `protected`, `static`, `const`… El error es `Expected name, not a keyword`.
- **`string.Format`** usa `%1`…`%9`. El porcentaje se escribe `%` tal cual; `%%` saldría doble.
- **`ToUpper()` / `ToLower()` / `Replace()`** modifican la cadena en sitio. `ToUpper()` no convierte tildes ni eñes: haz una función propia que reemplace `á→Á`, etc.
- **Sin conversiones implícitas raras:** `bool * float` no compila. Usa un `if`.
- **Los `static` sobreviven a «Reload Game»** de Workbench y a volver a entrar en partida. Pon un `Reset()` que limpie tus estáticos y llámalo en el `OnPostInit` del componente del modo de juego. Si no, el servidor «cree» que ya ha enviado cosas, quedan widgets huérfanos…
- **Enums de la API:** muchos no salen en la documentación oficial. Si no estás seguro de un valor, compila: el compilador te lo dice. Ejemplos comprobados: `EGameOverTypes.FACTION_VICTORY_SCORE` y `EMapDescriptorType.MDT_NAME_CITY`.
- **`CallLater`:** `GetGame().GetCallqueue().CallLater(Metodo, ms, repetir, args...)`. Para pararlo, `Remove(Metodo)`. Un `CallLater` repetido a 0 ms es un bucle por fotograma.
- **Tiempo de juego:** `GetGame().GetWorld().GetWorldTime() / 1000.0` (segundos).

## Recursos, GUIDs y registro

- **Todo recurso nuevo (prefab, config, layout, imageset, textura, mundo) necesita su `.meta` con GUID** y que Workbench lo registre en `resourceDatabase.rdb`.
  - Sin registrar, el servidor lo crea pero **no se replica** a los clientes («invalid prefab resource GUID»), y los contenedores **no admiten inventario**.
  - Solución: `tools/metas.py` + `tools/register.py`.
- **Workbench no convierte un PNG en textura por sí solo**, y Enfusion no carga PNG directamente. Usa `tools/png2edds.py` (lados múltiplos de 4) y crea el `.meta` con `metas.py`.
- **Nunca inventes GUIDs ni rutas.** Búscalos con `tools/find.py`. Los IDs internos de componentes y entidades en tus propios archivos sí puedes generarlos al azar (16 hexadecimales), mientras sean únicos en el archivo.

## Prefabs

- **Herencia:** `MiCosa : "{GUID}Prefabs/.../Padre.et" { ... }`.
  - Para **cambiar un componente que ya tiene el padre**, escríbelo con **el mismo GUID de componente que el padre**. Mira el padre con `pakgrep.py`.
  - Si pones un GUID nuevo, duplicas el componente.
  - Ejemplo: los props destructibles heredan `DestructibleMultiPhase_Props_Base.et`, que trae `RplComponent "{5624A88DC2D9928D}"` desactivado. Para que tu prop se replique, pon `RplComponent "{5624A88DC2D9928D}" { Enabled 1 }`.
- **Contenedores con inventario** (armarios, cajas):
  - `SCR_UniversalInventoryStorageComponent` + el **`InventoryStorageManagerComponent` básico**. El `SCR_` da NULL en `OnItemAdded` en entidades estáticas.
  - Para llenarlos por script, usa el `SCR_InventoryStorageManagerComponent` **de un personaje** (`TrySpawnPrefabToStorage`).
- **Acciones de usuario** (lo que sale al mirar algo y pulsar F):
  - Van en `ActionsManagerComponent` → `additionalActions`, con una clase tuya que herede de `ScriptedUserAction`.
  - Si la acción solo abre interfaz en el cliente: `HasLocalEffectOnlyScript() { return true; }` y `CanBroadcastScript() { return false; }`. Ver `reference/patterns/acciones-de-usuario.md`.

## Mundo, IA y navmesh

- **Sin navmesh, la IA no se mueve** («Failed move», «No navmesh file specified»).
  - El `SCR_AIWorld` del mundo necesita sus `.nmn`: soldados y vehículos.
  - La plantilla trae los de Eden, Arland y Cain. Para otros mapas, búscalos con `find.py nmn <mapa>`.
- **Waypoints y grupos siempre sobre la navmesh**, a ras de suelo:
  - `GetReachablePoint` + descartar puntos más de 1,5 m por encima del terreno (tejados y pisos altos). Lo hace `Util.OnNavmesh(pos)`.
  - Si no, el grupo se queda atascado.
- **Grupos atascados:** si un grupo con ruta no se mueve en ~2 min, dale una ruta nueva alrededor de donde esté.
- **Personaje dentro de un vehículo:** el vehículo es `character.GetRootParent()`. `CompartmentAccessComponent` no tiene `GetVehicle()`.
- **Coordenadas:** `x y z` = este, altura, norte, en metros. En las capas (`.layer`) la altura `y` es absoluta. Saca los sitios con `map_locations.py`, que ya da `y` a ras de suelo.
- **Nombres de sitios del mapa:** vienen como clave de traducción (`#AR-MapLocation_Morton`). Se traducen con `WidgetManager.Translate(clave)`.

## Red y replicación

- **La lógica de la misión, solo en el servidor:** `if (!Replication.IsServer()) return;`.
- **Estado compartido:**
  - Usa `[RplProp()]` en un componente con `RplComponent` (el GameMode lo tiene). Tras cambiarlo en el servidor, llama a `Replication.BumpMe()`.
  - Para reaccionar en el cliente: `[RplProp(onRplName: "OnCambio")]`.
- **Avisos a todos:**
  - `[RplRpc(RplChannel.Reliable, RplRcver.Broadcast)]` en el componente del GameMode, y `Rpc(Metodo, args)` desde el servidor.
  - En una partida alojada el servidor también es jugador: llama además al método directamente si `!System.IsConsoleApp()`.
- **Mensajes a un jugador o peticiones de un jugador al servidor:**
  - Van por un componente de su `PlayerController`. El más cómodo es `modded class SCR_PlayerControllerGroupComponent`, que todos tienen.
  - `[RplRpc(..., RplRcver.Server)]` sirve para pedir; `RplRcver.Owner` para responder a ese jugador.
  - Ver `reference/patterns/red.md`.
- **Entidades por red:** se pasan como `RplId` (`RplComponent.Id()`) y se recuperan con `Replication.FindItem(id)`.

## Interfaz

- **Solo en clientes:** en el servidor dedicado `System.IsConsoleApp()` es `true` y no hay `Workspace`.
- **Layouts como texto:**
  - Los GUID de widgets y slots van **entre comillas**: `ImageWidgetClass "{…}" {`.
  - Imagen de un imageset: `Texture "{GUID}….imageset"` + `Image "nombre"`.
  - Ancho y alto fijos: `SizeLayoutWidget` con `AllowWidthOverride 1` / `WidthOverride N`.
  - Mira layouts del juego con `pakgrep.py "SizeLayoutWidgetClass"`.
- **Un texto largo dentro de una fila horizontal no hace salto de línea** salvo que su slot esté en modo `Fill`: `LayoutSlot.SetSizeMode(w, LayoutSizeMode.Fill)`.
- **La vista 3D de objetos (`ItemPreviewWidget`) ignora la opacidad.** Para marcar algo como «bloqueado», usa texto gris o un candado.
- **Ventanas con ratón:** `SCR_ConfigurableDialogUi.CreateFromPreset(presets.conf, "tag", miDialogo)`.
  - El botón principal cierra la ventana salvo que sobrescribas `OnConfirm()`.
  - Antes de abrir una ventana de aviso, comprueba `GetGame().GetMenuManager().IsAnyDialogOpen()`.
- **Mapa:** suscríbete a `SCR_MapEntity.GetOnMapOpenComplete()` / `GetOnMapClose()` para dibujar encima. Ábrelo por código con `MenuManager.OpenMenu(ChimeraMenuPreset.MapMenu)`; céntralo con `ZoomPanSmooth`.
- **Kit de interfaz listo:** [MCUIK](https://victoryil.github.io/MCUIK/) (paneles, avisos animados, iconos) y [MCES](https://victoryil.github.io/MCES/) (tienda). Ver doc 07.

## Partidas guardadas

- **Formato:** JSON con `JsonSaveContext` / `JsonLoadContext` en `$profile:TuMision/partida.json`.
  - Guarda una copia antes de sobrescribir.
  - Versiona el formato (`"version"`).
  - Lee con `ReadValue`, que devuelve `false` si falta la clave: así cargas partidas antiguas.
- **Guarda lo que «ya ha pasado».** Al cargar una partida, la historia volvía a lanzar la conversación del paso en curso. Hay que guardar, por ejemplo, que ese paso ya se anunció.
- **Partidas de prueba:** `server_test.py` borra antes de cada prueba los guardados del perfil de pruebas (`save_files_to_clear`). Si no, el autotest carga lo que dejó la prueba anterior (por ejemplo, la historia ya terminada) y falla sin motivo aparente.

## Pruebas y servidor

- **Puerto:** el servidor dedicado y el juego escuchan en **UDP 2001 aunque se les pase `-bindPort`**. Dos pruebas a la vez, o una prueba con tu servidor de juego encendido, dan «Unable to start replication». Una prueba cada vez.
- **Escenario:** un proyecto **sin empaquetar** carga el mundo en el servidor (`-server {GUID}Worlds/….ent`), pero **no la cabecera de misión**. Para probar el escenario de verdad, `pack.py` + `server_test.py --packed` o `client_test.py`.
- **Desplegar en el cliente sin menús:** `-tdmf <Facción> -tdml 0`. `-autodeployLoadout` tiene un fallo del juego base.
- **Parámetros propios:** `System.IsCLIParam("miParametro")` lee `-miParametro`. Con las herramientas del kit, pásalos así: `--param=-miParametro` (con `=`).
- **Cerrar procesos:** solo los que has abierto tú, por PID o por una marca en su línea de comandos. Nunca por nombre de ejecutable.

## Workbench y Workshop

- **Primera publicación:** se hace desde la ventana de Workbench (Publish Project). La línea de órdenes (`-publishAddon`) solo actualiza mods ya publicados.
- **Al publicar un mod** que depende de otro proyecto tuyo, Workbench ofrece publicar los dos. Marca solo el que quieres.
- **Lanzar el juego desde Workbench** solo resuelve las dependencias listadas en `profile/.projectList_*.conf`.
- **Categoría del Workshop:** para mods de sistemas o librerías es «System».
- **Licencia de otros mods:** muchos (por ejemplo, Freedom Fighters) son *No-Derivatives*. Puedes depender de ellos y usar sus prefabs, pero no copiar su código ni sus configs.

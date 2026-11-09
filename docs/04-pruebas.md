# 04 · Pruebas

Hay tres niveles. Úsalos siempre en este orden.

| Nivel | Herramienta | Tarda | Comprueba |
|---|---|---|---|
| 1. Compilar + autotest de servidor | `server_test.py` | 1-5 min | que compila, que no hay excepciones y que la lógica de la misión avanza |
| 2. Empaquetado | `pack.py` + `server_test.py --packed` | 2-4 min | que el mod y el escenario cargan como en un servidor real |
| 3. Cliente real con capturas | `pack.py` + `client_test.py` | 2-5 min | red real, despliegue del jugador, interfaz (lo ves en las capturas) |

## 1. Autotest de servidor

```
python tools/server_test.py --until "FIN del autotest"
```

- Arranca un servidor dedicado sin ventana con tu proyecto sin empaquetar y el parámetro `-<selftest_param>`.
- Termina al ver la marca o al agotar `--secs`.
- Copia el log a `out/logs/server_last.log` y lo resume:

```
## FALLOS DEL AUTOTEST (1)
  ... [OA][TEST] FALLO: aparecen los grupos enemigos (0)
## Resumen: OK=14 FALLO=1 compilacion=0 excepciones=0
```

Si hay errores de compilación, el resumen da archivo y línea (`@"Scripts/Game/OA/OA_Mission.c,120"`). Si hay excepciones, da el motivo y la pila.

### Cómo escribir el autotest (`XX_SelfTest.c`)

- **Una comprobación** es `Check(condición, "qué se comprueba")`, que escribe `[XX][TEST] OK: …` o `FALLO: …`.
- **Simula al jugador:**
  - Crea un soldado con `Util.Spawn(prefabDePersonaje, pos)` y muévelo con `SetOrigin`.
  - Llama a la lógica del servidor directamente: la misma función que llamaría el RPC del menú. Así pruebas compras, construcciones o reclutamientos sin red.
- **Cumple las fases a la fuerza:**
  - Mata o borra los enemigos con `SCR_EntityHelper.DeleteEntityAndChildren`.
  - Destruye el objetivo, o llama a `CompletePhase()`.
  - Comprueba que pasa a la siguiente fase.
- **Pasos con tiempo:** con `CallLater` (aparecer, esperar a que la IA se coloque, comprobar).
- **Termina siempre con `FIN del autotest: N comprobaciones, M fallos`.** Es la marca que espera `--until`.
- **Desactiva el guardado** durante el autotest (o usa un archivo aparte), para no pisar partidas reales.

## 2. Empaquetado

```
python tools/pack.py [MisDependencias] MiMision
python tools/server_test.py --packed --until "FIN del autotest"
```

Carga desde `out/packed` con `-addons GUID -server {GUID}Missions/….conf`, igual que un servidor de verdad. Sirve para ver que el escenario (`SCR_MissionHeader`) y todas las dependencias cargan.

## 3. Cliente real y capturas

```
python tools/pack.py
python tools/client_test.py --shots CAPTURA_JUEGO,CAPTURA_MAPA --until "FIN autotest de cliente"
```

- **Qué hace:**
  - Abre el juego en ventana (`-window`), alojando tu escenario.
  - Despliega directamente en `client_faction` (`-tdmf … -tdml 0`).
  - Activa `-<clienttest_param>`.
- **Capturas:** en tu `XX_ClientTest.c`, cuando la pantalla esté lista, haz `Print("[XX][CLIENT] CAPTURA_TIENDA")`. La herramienta ve la marca en el log y guarda `out/shots/CAPTURA_TIENDA.png`.
- **Errores:** si sale un cartel de «Virtual Machine Exception», también lo captura (`ERROR_VM.png`). Mira el log para el detalle.
- **Mira las capturas.**
  - Claude: Read del PNG.
  - Codex: ábrela o adjúntala.

  Comprueba que no se pisen textos, que se lea todo y que los colores y tamaños estén bien. Corrige y repite.
- **Escaparate:** para que la captura enseñe algo, el autotest de cliente puede provocarlo antes de la marca: un aviso, abrir una ventana, centrar el mapa (`ZoomPanSmooth`).

**Pide permiso al usuario la primera vez**: se abre una ventana del juego en su escritorio.

## Leer cualquier log

```
python tools/logscan.py "C:/…/console.log" [--grep "MiTexto"] [--ok "[XX][TEST] OK"] [--fail FALLO]
```

| Log | Dónde está |
|---|---|
| Servidor de pruebas | `out/logs/server_last.log` |
| Cliente de pruebas | `out/logs/client_last.log` |
| Workbench | `workbench_logs/<fecha>/console.log` |
| Juego del usuario | `Documents/My Games/ArmaReforger/logs/<fecha>/console.log` |

## Problemas típicos

| Síntoma | Causa |
|---|---|
| `Unable to start replication` | puerto 2001 ocupado: otra prueba, el juego o tu servidor abiertos |
| el autotest «empieza a medias» | cargó una partida guardada: revisa `save_files_to_clear` |
| `FALLO` en grupos de IA (0 soldados) | prefab de grupo mal (compruébalo con `find.py`) o posición fuera de la navmesh |
| el cliente no despliega | facción mal en `client_faction` o sin equipo en el LoadoutManager |
| no salen las capturas | la marca no se escribe (¿el autotest de cliente arrancó? busca `INICIO autotest de cliente`) |

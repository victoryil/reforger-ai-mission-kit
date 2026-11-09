# {{TITLE}} · Diseño

## Qué es
{{DESCRIPTION}}

## Sistemas
| Sistema | Archivo | Qué hace |
|---|---|---|
| Gestor de misión | `Scripts/Game/{{P}}/{{P}}_MissionComponent.c` | fases en orden, objetivo y marca replicados, avisos, guardado, victoria |
| Aparición | `{{P}}_SpawnLogic.c` | despliegue directo en la facción `{{PLAYER_FACTION_KEY}}` en `{{P}}_PlayerSpawn` |
| Utilidades | `{{P}}_Util.c` | crear entidades, suelo, navmesh, grupos, volcado del mapa |
| Autotest servidor | `{{P}}_SelfTest.c` (`-{{SELFTEST_PARAM}}`) | recorre la misión entera |
| Autotest cliente | `{{P}}_ClientTest.c` (`-{{CLIENTTEST_PARAM}}`) | red real y capturas |

## Fases
(mantener al día con BuildPhases())
1. ...

## Qué colocar a mano en el editor (si algo)
- ...

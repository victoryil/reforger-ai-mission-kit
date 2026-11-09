# 05 · Recursos, prefabs y mundo (todo como texto)

## Estructura de un proyecto (la que crea `new_project.py`)

```
MiMision/
  addon.gproj                      ID, GUID, título, dependencias
  Worlds/MiMision/MiMision.ent     sub-escena del mapa (SubScene { Parent "{GUID}worlds/Eden/Eden.ent" })
  Worlds/MiMision/MiMision_Layers/default.layer   entidades del mundo (AIWorld, GameMode, aparición…)
  Missions/MiMision.conf           escenario (SCR_MissionHeader): nombre, descripción, jugadores
  Prefabs/XX/XX_GameMode.et        modo de juego + XX_MissionComponent + XX_SpawnLogic
  Prefabs/XX/XX_FactionManager.et  facciones (configs del juego o de mods)
  Prefabs/XX/XX_LoadoutManager.et  equipo del jugador
  Prefabs/XX/XX_SpawnPoint.et      punto de aparición
  Scripts/Game/XX/*.c              tu código
  docs/                            DISENO.md, DEVLOG.md
```

## Capas del mundo (`.layer`)

Cada entidad es un bloque con su clase, un nombre opcional, su prefab y su posición:

```
SCR_SpawnPoint XX_PlayerSpawn : "{GUID}Prefabs/XX/XX_SpawnPoint.et" {
 coords 5135 14.1 4012
 angles 0 90 0
}
GenericEntity : "{GUID}Prefabs/Props/.../Mesa.et" {
 coords 5140 14.2 4015
}
```

- **Posición:** `coords x y z` en metros, con `y` absoluta. Sácala de `map_locations.py`, que ya trae `y` a ras de suelo, o pon `y` del terreno.
- **Nombre:** el que va tras la clase (`XX_PlayerSpawn`) se busca por script con `GetGame().GetWorld().FindEntityByName("XX_PlayerSpawn")`.
- **Capas del usuario:** si las edita en Workbench, no las sobrescribas. Añade una capa tuya (`MiCapa.layer`) en la misma carpeta.

## Prefabs

Un prefab propio hereda de otro y cambia lo que haga falta:

```
SCR_ChimeraCharacter : "{GUID}Prefabs/Characters/.../Character_CIV_X.et" {
 ID "6A0C0F000D000001"
 components {
  ActionsManagerComponent "{520EA1D2F659CE02}" {      <- MISMO GUID que en el padre
   additionalActions {
    XX_TalkAction "{6A0C0F000D000011}" {
     ParentContextList {
      "default"
     }
     UIInfo UIInfo "{6A0C0F000D000012}" {
      Name "Hablar"
     }
     VisibilityRange 3
    }
   }
  }
 }
}
```

- `ID` es un hexadecimal de 16 cifras, único.
- Para modificar un componente que ya tiene el padre, usa su mismo GUID de componente. Míralo en el padre con `pakgrep.py "Character_CIV_X.et"` o abriendo el prefab del mod.
- Componentes nuevos, con GUID nuevo.
- Después: `metas.py` + `register.py`.

## Buscar lo que necesitas

```
python tools/find.py Group USSR .et              grupos de IA
python tools/find.py Character FFAA Rifleman .et soldados de un mod
python tools/find.py Configs/Factions .conf      facciones
python tools/find.py Loadout .conf US            equipos
python tools/find.py Waypoint .et                waypoints de IA
python tools/find.py Vehicles UAZ .et            vehículos
python tools/find.py --source RHS-StatusQuo M4   solo de un mod
python tools/pakgrep.py "AIWaypoint_Defend.et"   ver el texto de un prefab o config
```

## Facciones y equipo

- **Facciones:** `XX_FactionManager.et` hereda `FactionManager_Base.et` y lista `SCR_Faction "{id}" : "{GUID}Configs/Factions/X.conf"`.
  - `m_bIsPlayable 1` solo en la del jugador.
  - La clave de la facción (`US`, `USSR`, `FFAA`…) es la que usa el código (`GetFactionByKey`).
- **Equipo:** `XX_LoadoutManager.et` → `SCR_FactionPlayerLoadout "{id}" : "{GUID}Configs/Loadouts/…conf"`.
- **Con mods** (RHS, FFAA…): pon sus GUID en `Dependencies` y usa sus configs y prefabs.

## Mapas de la plantilla

| `--map` | Mundo | AIWorld + navmesh |
|---|---|---|
| Eden (Everon) | `{853E92315D1D9EFE}worlds/Eden/Eden.ent` | `SCR_AIWorld_Eden`, `GM_Eden(.nmn/_vehicles.nmn)` |
| Arland | `{A9806AF617972E97}worlds/Arland/Arland.ent` | `SCR_AIWorld_Arland`, `GM_Arland…` |
| Cain (Kolguyev) | `{1EA95DAE3230BEB0}worlds/Cain/Cain.ent` | `SCR_AIWorld_Cain`, `GM_Cain…` |

Otros mapas (de mods): `find.py <mapa> .ent` y `find.py nmn <mapa>`. Pon el AIWorld y la navmesh a mano en `default.layer`.

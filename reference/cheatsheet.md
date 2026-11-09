# Chuleta de la API (lo que más se usa al hacer misiones)

Todas las firmas están comprobadas con `tools/api.py` y usadas en misiones que funcionan. Para cualquier otra cosa: `python tools/api.py method X` / `class Y`.

## Juego, mundo y tiempo

| Para | Código |
|---|---|
| mundo | `GetGame().GetWorld()` → `BaseWorld` |
| altura del suelo | `world.GetSurfaceY(x, z)` |
| entidad por nombre (de la capa) | `world.FindEntityByName("Nombre")` |
| segundos de juego | `world.GetWorldTime() / 1000.0` |
| modo de juego | `SCR_BaseGameMode.Cast(GetGame().GetGameMode())` |
| ¿servidor? / ¿dedicado sin pantalla? | `Replication.IsServer()` / `System.IsConsoleApp()` |
| parámetro `-miParam` | `System.IsCLIParam("miParam")` |
| llamar más tarde / repetir / parar | `GetGame().GetCallqueue().CallLater(Metodo, ms, repetir, args…)` / `.Remove(Metodo)` |
| log | `Print("texto", LogLevel.NORMAL)` (también `WARNING`, `ERROR`) |

## Crear y borrar entidades

```c
Resource res = Resource.Load(prefab);                 // ResourceName "{GUID}Prefabs/....et"
EntitySpawnParams p = new EntitySpawnParams();
p.TransformMode = ETransformMode.WORLD;
Math3D.AnglesToMatrix(Vector(yawGrados, 0, 0), p.Transform);
p.Transform[3] = pos;
IEntity e = GetGame().SpawnEntityPrefab(res, GetGame().GetWorld(), p);
SCR_EntityHelper.DeleteEntityAndChildren(e);          // borrar (con hijos)
e.GetOrigin();  e.SetOrigin(pos);  e.GetRootParent();  e.FindComponent(TipoDeComponente)
```

## Jugadores

| Para | Código |
|---|---|
| ids de jugadores | `GetGame().GetPlayerManager().GetPlayers(array<int> ids)` |
| su personaje | `GetGame().GetPlayerManager().GetPlayerControlledEntity(id)` |
| id desde el personaje | `GetGame().GetPlayerManager().GetPlayerIdFromControlledEntity(ent)` |
| jugador local (cliente) | `GetGame().GetPlayerController()` → `.GetControlledEntity()`, `.GetPlayerId()` |
| ¿muerto? | `ChimeraCharacter.Cast(e).GetCharacterController().IsDead()` |
| ¿destruido? (objetos/vehículos) | `DamageManagerComponent.Cast(e.FindComponent(DamageManagerComponent)).IsDestroyed()` |
| facción | `GetGame().GetFactionManager().GetFactionByKey("US")` |
| admin | `GetGame().GetPlayerManager().HasPlayerRole(id, EPlayerRole.ADMINISTRATOR)` |

## IA

```c
SCR_AIGroup g = SCR_AIGroup.Cast(Spawn(grupoPrefab, OnNavmesh(pos)));
AIWaypoint wp = AIWaypoint.Cast(Spawn("{93291E72AC23930F}Prefabs/AI/Waypoints/AIWaypoint_Defend.et", OnNavmesh(pos)));
g.AddWaypoint(wp);
g.GetAgentsCount();                       // vivos
array<AIAgent> a = {}; g.GetAgents(a);    // a[i].GetControlledEntity()
NavmeshWorldComponent nav = GetGame().GetAIWorld().GetNavmeshWorldComponent("Soldiers");
vector outPos; nav.GetReachablePoint(pos, 40, outPos);
```

| Waypoints del juego base | GUID |
|---|---|
| Move | `{750A8D1695BD6998}Prefabs/AI/Waypoints/AIWaypoint_Move.et` |
| Defend | `{93291E72AC23930F}Prefabs/AI/Waypoints/AIWaypoint_Defend.et` |
| Patrol | `{22A875E30470BD4F}Prefabs/AI/Waypoints/AIWaypoint_Patrol.et` |
| SearchAndDestroy | `{B3E7B8DC2BAB8ACC}Prefabs/AI/Waypoints/AIWaypoint_SearchAndDestroy.et` |
| Follow | `{A0509D3C4DD4475E}Prefabs/AI/Waypoints/AIWaypoint_Follow.et` |
| GetInNearest | `{B049D4C74FBC0C4D}Prefabs/AI/Waypoints/AIWaypoint_GetInNearest.et` |
| Cycle (repetir lista) | `{35BD6541CBB8AC08}Prefabs/AI/Waypoints/AIWaypoint_Cycle.et` → `AIWaypointCycle.SetWaypoints(array)` |

## Red

```c
[RplProp()] protected int m_iFase;                          // en un componente del GameMode
[RplProp(onRplName: "OnFaseCambiada")] protected string m_s; // y en el cliente llama a OnFaseCambiada
Replication.BumpMe();                                       // servidor, tras cambiar RplProp

[RplRpc(RplChannel.Reliable, RplRcver.Broadcast)] protected void RpcDo_X(string a) { ... }   // a todos
[RplRpc(RplChannel.Reliable, RplRcver.Server)]    protected void RpcAsk_X(int a) { ... }     // cliente -> servidor
[RplRpc(RplChannel.Reliable, RplRcver.Owner)]     protected void RpcDo_Y(string a) { ... }   // servidor -> ese jugador
Rpc(RpcDo_X, "hola");

RplComponent rpl = RplComponent.Cast(e.FindComponent(RplComponent)); RplId id = rpl.Id();
RplComponent r2 = RplComponent.Cast(Replication.FindItem(id)); IEntity e2 = r2.GetEntity();
```

## Inventario

```c
SCR_InventoryStorageManagerComponent inv = SCR_InventoryStorageManagerComponent.Cast(personaje.FindComponent(SCR_InventoryStorageManagerComponent));
inv.TrySpawnPrefabToStorage(prefabObjeto);    // false si no cabe
```

## Mapa y avisos

```c
SCR_HintManagerComponent.ShowCustomHint(texto, titulo, segundos);    // aviso sencillo (cliente)
SCR_MapMarkerBase m = new SCR_MapMarkerBase();
m.SetType(SCR_EMapMarkerType.PLACED_CUSTOM); m.SetWorldPos(x, z); m.SetCustomText("Objetivo");
m.SetIconEntry(1); m.SetColorEntry(1);
SCR_MapMarkerManagerComponent.GetInstance().InsertStaticMarker(m, false, true);   // servidor: lo ven todos
SCR_MapEntity map = SCR_MapEntity.GetMapInstance(); map.ZoomPanSmooth(map.GetMinZoom() * 6, x, z, 0.1);
GetGame().GetMenuManager().OpenMenu(ChimeraMenuPreset.MapMenu);
GetGame().GetMenuManager().IsAnyDialogOpen();
```

## Fin de partida

```c
gm.EndGameMode(SCR_GameModeEndData.CreateSimple(EGameOverTypes.FACTION_VICTORY_SCORE, -1, factionManager.GetFactionIndex(faccion)));
```

## Guardar y cargar (JSON)

```c
FileIO.MakeDirectory("$profile:MiMision");
JsonSaveContext s = new JsonSaveContext(); s.WriteValue("fase", 3); s.SaveToFile("$profile:MiMision/partida.json");
JsonLoadContext l = new JsonLoadContext(); if (l.LoadFromFile(ruta)) { int f; l.ReadValue("fase", f); }
FileIO.FileExists(ruta); FileIO.CopyFile(a, b);
```

## Interfaz (cliente)

```c
WorkspaceWidget ws = GetGame().GetWorkspace();
Widget w = ws.CreateWidgets(layoutResourceName, padre);
w.FindAnyWidget("Nombre"); TextWidget.Cast(x).SetText("…"); RichTextWidget (admite <b>, <color rgba="r,g,b,a">)
FrameSlot.SetAnchorMin(w, 1, 0); FrameSlot.SetAnchorMax(w, 1, 0); FrameSlot.SetAlignment(w, 1, 0); FrameSlot.SetPos(w, -18, 18);
LayoutSlot.SetPadding(w, l, t, r, b); LayoutSlot.SetSizeMode(w, LayoutSizeMode.Fill);
ImageWidget.Cast(x).LoadImageFromSet(0, imagesetResourceName, "icono");
SCR_ConfigurableDialogUi.CreateFromPreset(presetsConf, "tag", miDialogo);
WidgetManager.Translate("#clave")   // traducir claves de texto
```

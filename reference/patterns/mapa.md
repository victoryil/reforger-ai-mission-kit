# Mapa: marcas, dibujar encima y sitios con nombre

## Marca para todos (desde el servidor)

```c
SCR_MapMarkerBase m = new SCR_MapMarkerBase();
m.SetType(SCR_EMapMarkerType.PLACED_CUSTOM);
m.SetWorldPos(pos[0], pos[2]);
m.SetCustomText("Objetivo");
m.SetIconEntry(1);      // indice en la lista de iconos del juego
m.SetColorEntry(1);     // indice de color
SCR_MapMarkerManagerComponent mm = SCR_MapMarkerManagerComponent.GetInstance();
mm.InsertStaticMarker(m, false, true);
int id = m.GetMarkerID();
// quitarla
SCR_MapMarkerBase old = mm.GetStaticMarkerByID(id);
if (old)
	mm.RemoveStaticMarker(old);
```

## Dibujar tu propia capa sobre el mapa (cliente)

```c
SCR_MapEntity.GetOnMapOpenComplete().Insert(OnMapOpen);   // y GetOnMapClose()

void OnMapOpen(MapConfiguration config)
{
	if (config && config.MapEntityMode != EMapEntityMode.FULLSCREEN)
		return;                                              // solo el mapa de la tecla M
	SCR_MapEntity mapEnt = SCR_MapEntity.GetMapInstance();
	Widget parent = mapEnt.GetMapMenuRoot();                 // cuelga aqui tus widgets
	// de mundo a pantalla: mapEnt.WorldToScreen(x, z, outSx, outSy, true)
}
```

- **Áreas de color:** usa un `CanvasWidget` con `SetDrawCommands` (polígonos).
- **Iconos:** `ImageWidget` colocados con `FrameSlot.SetPos` en cada fotograma mientras el mapa está abierto.

## Sitios con nombre

`python tools/map_locations.py` (la plantilla trae `XX_Util.DumpMap()`). Por script: `mapEnt.GetByType(items, EMapDescriptorType.MDT_NAME_TOWN)` → `item.Entity().GetOrigin()`, `WidgetManager.Translate(item.GetDisplayName())`.

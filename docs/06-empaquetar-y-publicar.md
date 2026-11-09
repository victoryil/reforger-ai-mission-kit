# 06 · Empaquetar, servidor dedicado y publicar

## Empaquetar (local)

```
python tools/pack.py MiKitPropio MiMision
```

Usa la línea de órdenes de Workbench (`-wbModule=ResourceManager -packAddon -packAddonDir`). Deja cada mod en `out/packed/<Proyecto>/`, con `addon.gproj`, `data.pak` y `resourceDatabase.rdb`. Es exactamente lo que se sube al publicar. Empaqueta primero tus dependencias propias.

## Probar como servidor real

```
python tools/server_test.py --packed --no-selftest --secs 120
```

Para un servidor dedicado de verdad, con su `config.json`:

```json
{
  "bindPort": 2001,
  "game": {
    "name": "Mi mision",
    "scenarioId": "{GUID}Missions/MiMision.conf",
    "mods": [ { "modId": "GUID_DE_TU_MOD", "name": "MiMision", "version": "1.0.0" } ]
  }
}
```

`ArmaReforgerServer.exe -config ruta/config.json -profile ruta/perfil`.

- Con `"version"` fijada, el servidor descarga esa versión exacta. Para coger siempre la última, quítala.
- Justo después de publicar, el CDN del Workshop puede dar error 502 unos minutos. Reintenta.
- Haz copia de las partidas (`perfil/...`) antes de actualizar el mod en un servidor con gente.

## Publicar en el Workshop (lo hace el usuario)

1. Abre el proyecto en Workbench y espera a que termine de cargar.
2. Menú **Workbench → Publish Project**. Si el proyecto depende de otro tuyo, Workbench ofrece publicar los dos: **marca solo el que quieres**.
3. Rellena la ventana:
   - **Nombre y versión:** `1.0.0` la primera vez. Después, `1.0.1` para arreglos, `1.1.0` para añadidos y `2.0.0` si rompes algo para otros mods.
   - **Resumen** (una línea) y **descripción**.
   - **Imagen:** `thumbnail.png` de 1280×720 en la raíz del proyecto.
   - **Categoría:**
     - «System» para librerías y sistemas.
     - El tipo de escenario para una misión.
   - **Licencia:** por ejemplo, MIT o APL-SA si quieres que otros reutilicen. Con APL-ND nadie podrá modificarlo.
   - **Dependencias:** salen del `addon.gproj`.
4. Publica. El enlace queda en `https://reforger.armaplatform.com/workshop/<GUID>`.

La **primera** publicación solo se puede hacer desde la ventana. Las actualizaciones también se pueden hacer por línea de órdenes (`-publishAddon`), pero es más seguro desde la ventana.

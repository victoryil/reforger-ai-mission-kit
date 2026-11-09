# 07 · Interfaz

## Opción recomendada: usar los kits ya hechos

| Mod | Qué da | Docs |
|---|---|---|
| **MCUIK** – Modern Common UI Kit (`B8DFCB8639E9DA37`) | 60 iconos, tema de colores, paneles, chips, filas, barras, avisos animados, diálogos con voz, ventanas de lista y de evento | https://victoryil.github.io/MCUIK/ |
| **MCES** – Modern Common Economy & Shop (`AE9A7FAB88A56E07`) | tienda con pestañas, tarjetas 3D y compra validada en servidor; tu misión pone el dinero | https://victoryil.github.io/MCES/ |

1. Añade sus GUID a `Dependencies` (`--deps B8DFCB8639E9DA37,AE9A7FAB88A56E07` en `new_project.py`).
2. Sigue su «Guía para IA».
3. Prueba con `client_test.py` y mira las capturas.

Ejemplo mínimo, en un componente que corre en clientes:

```c
if (!System.IsConsoleApp())
{
    MCUIK_Notify.Reset();
    Widget panel = MCUIK.Panel(MCUIK.CreateLayer(), "objective", "OBJETIVO", 320);
    MCUIK.Place(panel, 1, 0, 1, 0, -18, 18);
    MCUIK.Text(MCUIK.Content(panel), "Llegad a Morton", 16);
}
MCUIK_Notify.Toast("zone", "Zona asegurada", "Morton está despejado.", MCUIK_Theme.Success());
```

## Sin kits: lo mínimo del juego base

- **Avisos sencillos:** `SCR_HintManagerComponent.ShowCustomHint(texto, titulo, segundos)` (lo usa la plantilla).
- **Marcas en el mapa:** ver `reference/patterns/mapa.md`.
- **Ventanas:** `SCR_ConfigurableDialogUi` con un `.conf` de presets y tu layout de contenido. Ver doc 03, apartado Interfaz.

## Hacer tu propia interfaz bien

1. **Layouts generados por script**, no a mano. El generador de MCUIK (`MCUIK/tools/gen_layouts.py`) escribe `.layout` desde una descripción en Python y se puede importar desde tus herramientas.
2. **Iconos:**
   - Dibújalos en SVG.
   - Pásalos a PNG (Python: `resvg-py` + `Pillow`).
   - Pásalos a `.edds` con `tools/png2edds.py`.
   - Haz un `.imageset` (atlas) y créale el `.meta` con `tools/metas.py`.
3. **Registra** con `tools/register.py`.
4. **Ajusta en rondas:** `client_test.py --shots …`, mira, corrige y repite. Comprueba que no se pisen textos, que el contraste sea suficiente, que nada tape el centro de la pantalla y que se ajuste a 1080p.
5. **Diseño que funciona en Reforger:**
   - Paneles oscuros semitransparentes con una franja de color.
   - Números grandes con icono, y barras en vez de frases.
   - Avisos a un lado y diálogos abajo.
   - Nada de texto largo en el HUD.

# 08 · Referencia de la API (barata en tokens)

Arma Reforger Tools trae la referencia oficial de scripts en HTML (Doxygen), en `…/Workbench/docs`: unas 30.000 páginas. Leerla así gasta muchísimo. `tools/api.py` la convierte, **en tu PC**, en archivos de texto compactos.

## Generar (una vez por versión del juego)

```
python tools/api.py --build
```

Crea `reference/generated/`, que no se sube a git porque es documentación de Bohemia:

| Archivo | Contenido |
|---|---|
| `INDEX.tsv` | `clase  base  descripción` (unas 9.000 clases) |
| `METHODS.tsv` | `método  clase  firma` (unos 100.000 métodos públicos) |
| `classes/<Clase>.txt` | la clase: base, cadena de herencia y métodos por sección, con su descripción |

## Consultar

```
python tools/api.py class SCR_AIGroup                 la clase (métodos públicos)
python tools/api.py class LayoutSlot --all            también protegidos y atributos
python tools/api.py method GetReachablePoint          en qué clases está y su firma
python tools/api.py method Waypoint ~                 métodos cuyo nombre contiene "Waypoint"
python tools/api.py search inventory storage manager  clases por nombre o descripción
python tools/api.py children SCR_BaseGameModeComponent   clases que heredan de una
```

Para una IA, lo más barato es hacer grep sobre `reference/generated/METHODS.tsv` o `INDEX.tsv`, y leer solo el `.txt` de la clase que necesite.

## Límites

- **Enums:** los valores no vienen. Pruébalos compilando, o busca ejemplos en `reference/patterns`.
- **Métodos heredados:** no se repiten en cada clase. Mira la cadena `herencia:` y consulta la base.
- **Documentación oficial:** solo cubre lo público. Lo que hacen las clases por dentro no está (los scripts del juego van comprimidos en los .pak). Para ver **cómo** usa el juego algo, busca prefabs y configs con `pakgrep.py`, o mira las recetas probadas en `reference/patterns/`.

Chuleta con lo más usado: [`reference/cheatsheet.md`](../reference/cheatsheet.md).

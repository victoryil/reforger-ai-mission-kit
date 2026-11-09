# 01 · Cómo trabajar (el método que funciona)

Este es el método con el que se ha hecho una campaña completa (Reconquista Canaria) y dos mods de sistemas (MCUIK y MCES) con un asistente de IA. Lo importante no es escribir mucho código de golpe, sino **comprobar cada paso en el motor real**.

## 1. Entender y planificar

1. **Lee el encargo** del usuario (`templates/brief/MISION.md`).
2. **Haz un plan por fases pequeñas.** Cada fase debe poder probarse sola. Por ejemplo:
   1. Esqueleto: proyecto, mundo y modo de juego, y el jugador aparece.
   2. Fase 1 de la misión.
   3. Enemigos.
   4. Fases siguientes.
   5. Fin de partida.
   6. Interfaz.
   7. Pulido.
3. **Escribe el plan** en `docs/DISENO.md` del proyecto: qué hace cada sistema y cómo se coloca cada cosa.
4. **Pregunta solo lo imprescindible**, todo junto y una vez. Si es una decisión de diseño menor, elige algo razonable, sigue y apúntalo en el DEVLOG.

## 2. Bucle de cada fase

```
programar → metas/registrar (si hay recursos nuevos) → server_test → (pack + client_test + mirar capturas) → commit → DEVLOG
```

- **Arranca de algo que funciona.** `new_project.py` deja una misión mínima que compila y cuyo autotest pasa. Pruébala antes de cambiar nada: si falla luego, sabrás que ha sido tu cambio.
- **Cambios pequeños.** Si algo falla después de cambiar cinco cosas, no sabrás cuál ha sido.
- **El autotest de servidor crece contigo.** Cada sistema nuevo tiene su paso en `XX_SelfTest.c`, con `Check(condición, "qué se comprueba")`. Al final hay decenas de comprobaciones que se ejecutan en un minuto cada vez.
- **Lo visual se mira.** Una interfaz no está bien hasta que la has visto en una captura del juego. Se ajusta en rondas: captura, corregir, captura.
- **Lee el log, no lo adivines.** `logscan.py` te da errores de compilación con archivo y línea, excepciones con su pila y fallos del autotest.

## 3. Ahorrar tokens (y errores)

| En vez de… | Haz |
|---|---|
| explorar carpetas de mods buscando un prefab | `python tools/find.py palabras .et` |
| leer la documentación HTML de la API | `python tools/api.py class X` / `method Y` |
| adivinar la sintaxis de un `.layout` o un prefab | `python tools/pakgrep.py "TextoQueAparezca"` y mira uno del juego |
| leer logs de miles de líneas | `python tools/logscan.py log` (o el resumen que ya dan las pruebas) |
| inventar coordenadas | `python tools/map_locations.py --grep pueblo` |
| reescribir utilidades | `reference/patterns/` y `XX_Util.c` de la plantilla |

## 4. Qué se puede hacer sin el editor visual (casi todo)

Los archivos de Enfusion son **texto**, y la IA puede escribirlos directamente:
- prefabs (`.et`);
- mundos y capas (`.ent`, `.layer`);
- configs (`.conf`);
- layouts de interfaz (`.layout`);
- imagesets.

Lo único que necesita Workbench es **registrar** los archivos nuevos, y eso lo hace `register.py` con su propia instancia.

Lo que sí conviene que haga una persona en el editor visual:
- **Colocar a ojo** edificios, decorado y detalles de un pueblo. La IA puede poner entidades en una capa por coordenadas, pero no ve el resultado salvo con capturas.
- **La primera publicación** en el Workshop: necesita la ventana de Workbench y la cuenta del usuario.

## 5. Comunicación con el usuario

- Al acabar cada fase di qué está **probado en servidor**, qué se ha **visto en el cliente** y qué falta **probar jugando**.
- Si una prueba falla, dilo y cuenta qué vas a hacer.
- Si algo no se puede (por ejemplo, el editor visual), sáltalo, apúntalo y sigue con lo siguiente.

## 6. Documentación del proyecto

- `docs/DISENO.md`: cómo funciona cada sistema y cómo colocar cosas a mano.
- `docs/DEVLOG.md`: entradas fechadas con lo hecho, lo probado y lo pendiente. Cuando una IA nueva retome el proyecto, empezará leyendo esto.

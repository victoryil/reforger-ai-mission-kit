# Encargo de misión (rellena lo que esté entre {{ }} y borra lo que no aplique)

> Rellena esta ficha y pásasela a tu IA junto con `templates/brief/PROMPT.md`. Cuanto más concreto, mejor sale. Lo que dejes vacío lo decidirá la IA, y lo apuntará en el DEVLOG para que lo revises.

## 1. Identidad

- **Título:** {{TÍTULO}}
- **Subtítulo o lema:** {{SUBTÍTULO}}
- **Nombre interno** (sin espacios, para carpetas): {{NOMBRE_PROYECTO}}
- **Prefijo de clases** (2-4 mayúsculas): {{PREFIJO, p. ej. OA}}
- **Autor:** {{AUTOR}}
- **Descripción** (sale en la pantalla de selección de escenario): {{DESCRIPCIÓN, 2-3 frases}}

## 2. Planteamiento

- **Tipo:** {{misión con principio y final / campaña persistente / defensa por oleadas / ...}}
- **Sinopsis:** {{qué pasa, dónde, quién eres, qué hay que conseguir}}
- **Tono:** {{serio y realista / con humor / ...}}
- **Duración objetivo:** {{MINUTOS}}
- **Jugadores:** {{N}}, cooperativo. ¿IA aliada en los huecos? {{sí/no}}

## 3. Mundo

- **Mapa:** {{Eden (Everon) / Arland / Cain (Kolguyev) / mapa de un mod: nombre y GUID}}
- **Zona de juego:** {{pueblos o zona: p. ej. "alrededor de Morton y Saint-Pierre"}}. La IA sacará coordenadas con `map_locations.py`.
- **Hora y tiempo:** {{amanecer, mediodía, noche…; despejado, lluvia, niebla}}

## 4. Bandos

- **Jugadores:** {{facción: US / USSR / FIA / de un mod (FFAA, RHS…)}}. Unidad: {{p. ej. infantería ligera, fuerzas especiales}}
- **Enemigo:** {{facción}}, {{cómo de numeroso y equipado}}
- **Civiles:** {{sí/no; comportamiento}}
- **Mods de los que depende** (nombre y GUID del Workshop): {{p. ej. RHS Status Quo 595F2BF2F44836FB; FFAA Core 6872C9965058DE7A}}

## 5. Fases (en orden)

Para cada una: qué hay que hacer, dónde y cuándo se da por cumplida.

1. {{p. ej. Llegar al punto de reunión al norte de Morton}}
2. {{p. ej. Asaltar el puesto de mando enemigo (dos grupos defendiendo) y destruir la radio}}
3. {{p. ej. Rescatar al rehén de la casa grande y llevarlo a la extracción}}
4. {{p. ej. Aguantar 5 minutos en la extracción hasta que llegue el helicóptero}}

- **Condiciones de derrota:** {{mueren todos / muere el rehén / se acaba el tiempo / ...}}
- **Final:** {{qué pasa al ganar: mensaje, pantalla de victoria}}

## 6. Equipo, vehículos y apoyos

- **Equipo inicial:** {{armas, munición, médico, radios…}}
- **Vehículos disponibles:** {{…}}
- **Apoyos:** {{morteros, refuerzos, evacuación médica… o ninguno}}

## 7. Interfaz y extras

- **Interfaz:** {{básica del juego / moderna con MCUIK (avisos, paneles, diálogos)}}
- **¿Tienda o economía?** {{no / sí con MCES: qué se compra y con qué}}
- **Textos:** idioma {{español}}. ¿Voces? {{no / sí}}
- **Persistencia** (guardar al cerrar el servidor): {{sí/no}}

## 8. Rutas de tu PC

Van en `kit.config.json`; si ya lo has rellenado, déjalo vacío.

- **Proyectos de Workbench:** {{RUTA}}
- **Mods descargados:** {{RUTA}}

## 9. Reglas

- Pregúntame solo lo imprescindible; si no, decide y apúntalo.
- {{¿Puede abrir el juego en ventana para hacer capturas sin preguntar? sí/no}}
- {{Otras: no tocar mis capas del editor, no publicar nada, etc.}}

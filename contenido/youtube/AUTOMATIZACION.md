# Automatización semanal de Shorts

Cada **jueves por la mañana** (hora de España), una tarea programada de Claude Code abre una sesión
nueva en este repositorio y sigue este procedimiento. Al terminar abre un PR, lo fusiona y avisa con
un resumen.

**Lo que hace:** escribir los Shorts y el plan de la próxima semana sin plan, con las fuentes
buscadas en internet.

**Lo que no hace:** grabar, montar ni publicar en YouTube. Eso sigue siendo trabajo de una persona.

## Procedimiento

### 1. Leer el contexto

1. `.claude/youtube/voice.md`: la voz de Dani y las reglas del canal.
2. `contenido/youtube/README.md`.
3. Todas las tandas de `contenido/youtube/shorts/`, para no repetir ningún tema ya escrito
   (programado o de reserva).
4. Todos los planes de `contenido/youtube/planes/`, para saber cuál es la **última semana
   planificada**.

### 2. Decidir qué semana se planifica

La semana siguiente a la última planificada (de lunes a domingo). Si esa semana ya empezó o empieza
en menos de 7 días, avisar en el resumen de que el canal va justo de margen.

Cada semana lleva **cuatro Shorts**: lunes, miércoles, viernes y domingo.

### 3. Elegir los cuatro Shorts

1. **Primero, las reservas** de tandas anteriores cuya fuente se pueda confirmar, empezando por las
   de nota más alta. Una reserva cuyo dato no se confirma se queda donde está, con una nota.
2. **Después, temas nuevos** de curiosidades de tecnología (móviles, internet, ordenadores, inventos
   tecnológicos) que no estén en ninguna tanda.
3. Escribir al menos **seis candidatos** para quedarse con los cuatro mejores. Los que sobren y
   tengan fuente confirmada pasan a reserva.

### 4. Comprobar cada dato (obligatorio)

Para cada Short, **antes de escribir el guion**:

1. Buscar el dato en internet con `WebSearch`.
2. Confirmarlo en **al menos dos fuentes fiables**: organismos oficiales, la propia empresa,
   enciclopedias, museos o medios de referencia. Un blog o un agregador no cuentan como fuente
   fiable.
3. Si las fuentes no coinciden en un detalle (una fecha, una cifra, quién lo hizo), el guion no lo
   afirma o lo dice con su matiz, y se anota en «Ojo».
4. Si el dato no se confirma, **se descarta**. Nunca se escribe un dato sin fuente ni se inventa una
   cifra, una fecha o un nombre.
5. Las leyendas urbanas que se repiten pero no están demostradas no se cuentan como hechos.

### 5. Escribir cada Short

Mismo formato que [`shorts/tanda-02.md`](shorts/tanda-02.md):

- **Título** (con «¿Sabías que…?»), **texto en pantalla** (0–2 s, distinto del arranque hablado) y
  **fuentes** con sus enlaces.
- **Lo que dicen** las fuentes, en una o dos frases, y **Ojo** si hay matices.
- **Guion** de 30–45 segundos (75–110 palabras) con `[EN PANTALLA: ...]` en cada bloque: arranque
  con «¿Sabías que…?», giro, explicación y cierre que vuelve al principio.
- **Bucle**: qué frase final enlaza con el principio.
- **Antes de grabar**, si algo depende del rodaje (una prueba, unos derechos de imagen, el texto
  exacto de un menú).

### 6. Puntuar los arranques

Pasar la traducción literal al inglés de cada arranque por `.claude/skills/yt-script/hookscore.py`.
Si alguno sale WEAK, reescribirlo una vez añadiendo qué gana o pierde quien mira, o un nombre o una
fecha que estén en las fuentes. Programar los cuatro de nota más alta; el orden de publicación va de
mayor a menor nota.

### 7. Guardar

1. Crear una rama desde `main`: `shorts/semana-AAAA-MM-DD` (el lunes de la semana planificada).
2. Escribir `contenido/youtube/shorts/tanda-NN.md` (siguiente número libre), numerando los Shorts
   a continuación del último que exista.
3. Si se usa una reserva de una tanda anterior, en esa tanda cambiar su fila de «Reserva» a la fecha
   de publicación, y añadir su Short a la tabla de la tanda nueva con una referencia.
4. Escribir `contenido/youtube/planes/semana-AAAA-MM-DD.md` con el mismo formato que
   [`planes/semana-2026-11-02.md`](planes/semana-2026-11-02.md).
5. Actualizar las tablas de `contenido/youtube/README.md`.
6. Commit, push de la rama, PR contra `main` y **fusionarlo** (merge commit). El dueño del canal ha
   pedido que la automatización fusione sus propios PR sin esperar revisión.

### 8. Avisar

El resumen final de la sesión dice:

- qué semana se ha planificado y los cuatro Shorts con su nota;
- qué reservas se han usado o se han dejado, y por qué;
- cualquier dato descartado o con matiz;
- qué hay que grabar, y lo que esté marcado como «Antes de grabar»;
- el enlace al PR.

## Si algo falla

- **No se confirman cuatro datos:** programar los que se confirmen, dejar el resto del plan como
  «hueco» y decirlo en el resumen. Nunca rellenar con un dato sin fuente.
- **El push, el PR o la fusión fallan:** no reintentar a la fuerza. Dejar el trabajo en la rama y
  explicar en el resumen qué falló.

# Automatización de Shorts

Todo el canal funciona sin intervención, en dos piezas:

1. **Escribir (Claude Code, cada jueves a las 8:48, hora de España).** Una tarea programada abre una
   sesión nueva en este repositorio, sigue el procedimiento de abajo, abre un PR y lo fusiona.
2. **Montar (GitHub Actions, `.github/workflows/montar-shorts.yml`).** En cuanto entra en `main` un
   archivo nuevo en `contenido/youtube/shorts/datos/`, o cada jueves a las 10:30 UTC como red de
   seguridad, monta cada Short pendiente con `herramientas/shorts/montar.py` y lo publica como
   **release `short-NN`** con el MP4 y la descripción lista para pegar en YouTube.

**Lo que queda fuera:** subir el MP4 a YouTube. Ver «Subir a YouTube» al final.

## Cómo se monta un Short

`montar.py` lee `datos/NN.json` y, para cada bloque:

- busca una imagen con licencia libre (dominio público, CC0, CC BY o CC BY-SA; nunca NC ni ND) en
  Wikimedia Commons y, si no hay, en Openverse; si no encuentra ninguna, usa una tarjeta con el texto
  del gancho;
- genera la voz con edge-tts (voz `es-ES-AlvaroNeural`);
- compone la imagen sobre su propio fondo desenfocado, con un zoom lento.

Después une los bloques y añade el gancho en amarillo, los subtítulos y la marca. La descripción
incluye las fuentes del dato y la **atribución de cada imagen**, que es obligatoria para CC BY y
CC BY-SA: hay que pegarla entera en YouTube.

Para probar sin internet: `python3 herramientas/shorts/montar.py datos/11.json --sin-red`.

Para volver a montar un Short (por ejemplo, si una imagen no encaja): en GitHub, Actions > Montar
Shorts > Run workflow, con su número en «rehacer». También se puede cambiar la búsqueda de imagen de
ese bloque en su JSON: al fusionarlo no se rehace solo, hay que usar «rehacer».

## Procedimiento de escritura (para la tarea del jueves)

### 1. Leer el contexto

1. `.claude/youtube/voice.md`: la voz de Dani, las reglas del canal y cómo escribir para el montaje
   automático.
2. `contenido/youtube/README.md`.
3. Todas las tandas de `contenido/youtube/shorts/`, para no repetir ningún tema ya escrito
   (programado, de reserva o descartado).
4. Todos los planes de `contenido/youtube/planes/`, para saber cuál es la **última semana
   planificada**.

### 2. Decidir qué semana se planifica

La semana siguiente a la última planificada (de lunes a domingo). Si esa semana empieza en menos de
7 días, avisar en el resumen de que el canal va justo de margen.

Cada semana lleva **cuatro Shorts**: lunes, miércoles, viernes y domingo.

### 3. Elegir los cuatro Shorts

1. **Primero, las reservas** de tandas anteriores, empezando por las de nota más alta.
2. **Después, temas nuevos** de curiosidades de tecnología (móviles, internet, ordenadores, inventos
   tecnológicos) que no estén en ninguna tanda.
3. Escribir al menos **seis candidatos** para quedarse con los cuatro mejores. Los que sobren y
   tengan fuente confirmada pasan a reserva, con su archivo de datos.

### 4. Comprobar cada dato (obligatorio)

Para cada Short nuevo, **antes de escribir el guion**:

1. Buscar el dato en internet con `WebSearch`.
2. Confirmarlo en **al menos dos fuentes fiables**: organismos oficiales, la propia empresa,
   enciclopedias, museos o medios de referencia. Un blog o un agregador no cuentan como fuente
   fiable.
3. Si las fuentes no coinciden en un detalle (una fecha, una cifra, quién lo hizo), el guion no lo
   afirma o lo dice con su matiz, y se anota en «Ojo».
4. Si el dato no se confirma, **se descarta**. Nunca se escribe un dato sin fuente ni se inventa una
   cifra, una fecha o un nombre.
5. Las leyendas urbanas que se repiten pero no están demostradas no se cuentan como hechos.

Las reservas ya tienen fuentes comprobadas; basta con revisar que los enlaces siguen siendo válidos.

### 5. Escribir cada Short

Dos cosas por cada Short:

**a) La ficha en la tanda**, con el mismo formato que [`shorts/tanda-02.md`](shorts/tanda-02.md):
título (con «¿Sabías que…?»), texto en pantalla (distinto del arranque hablado), fuentes con enlace,
lo que dicen, «Ojo» si hay matices, el guion y el bucle.

**b) El archivo de datos `contenido/youtube/shorts/datos/NN.json`**, que es lo que se monta:

```json
{
  "id": "21",
  "titulo": "¿Sabías que …?",
  "texto_pantalla": "TRES PALABRAS",
  "publicacion": "2026-11-16",
  "bloques": [
    {"texto": "¿Sabías que …? (arranque, lo que dice la voz)", "imagen": "english search query"},
    {"texto": "giro", "imagen": "…"},
    {"texto": "explicación", "imagen": "…"},
    {"texto": "cierre que vuelve al principio", "imagen": "…"}
  ],
  "fuentes": ["https://…", "https://…"],
  "hashtags": ["#SabíasQue", "#Tecnología", "#Shorts"]
}
```

- **Cuatro bloques**, 75–110 palabras en total (30–45 segundos de voz).
- **`texto`** es exactamente lo que se locuta: sin acotaciones ni `[EN PANTALLA]`.
- **`imagen`** es una búsqueda **en inglés**, de 1 a 4 palabras, de algo concreto que exista en
  Wikimedia Commons: un objeto, un lugar, una persona conocida, un logo. Evitar conceptos abstractos.
- **`publicacion`** es la fecha prevista; `null` en las reservas.
- **Una reserva que se programa** ya tiene su JSON: solo hay que cambiar su `publicacion`.
- Validar que el JSON se lee bien (`python3 -c "import json,sys; json.load(open(sys.argv[1]))" archivo`).

### 6. Puntuar los arranques

Pasar la traducción literal al inglés de cada arranque por `.claude/skills/yt-script/hookscore.py`.
Si alguno sale WEAK, reescribirlo una vez añadiendo qué gana o pierde quien mira, o un nombre o una
fecha que estén en las fuentes. Programar los cuatro de nota más alta, de mayor a menor nota.

### 7. Probar el montaje

`python3 herramientas/shorts/montar.py contenido/youtube/shorts/datos/NN.json --salida /tmp/prueba --sin-red`
para cada Short nuevo. Si falla, corregir el JSON antes de seguir.

### 8. Guardar

1. Crear una rama desde `main`: `shorts/semana-AAAA-MM-DD` (el lunes de la semana planificada).
2. Escribir `contenido/youtube/shorts/tanda-NN.md` (siguiente número libre), numerando los Shorts a
   continuación del último que exista, y sus `datos/NN.json`.
3. Si se usa una reserva de una tanda anterior, en esa tanda cambiar su fila de «Reserva» a la fecha
   de publicación, y en su JSON poner la fecha en `publicacion`.
4. Escribir `contenido/youtube/planes/semana-AAAA-MM-DD.md` con el mismo formato que
   [`planes/semana-2026-11-02.md`](planes/semana-2026-11-02.md).
5. Actualizar las tablas de `contenido/youtube/README.md`.
6. Commit, push de la rama, PR contra `main` y **fusionarlo** (merge commit). El dueño del canal ha
   pedido que la automatización fusione sus propios PR sin esperar revisión. Al fusionarlo, GitHub
   Actions monta los vídeos.

### 9. Avisar

El resumen final de la sesión dice:

- qué semana se ha planificado y los cuatro Shorts con su nota y su fecha;
- qué reservas se han usado o se han dejado, y por qué;
- cualquier dato descartado o con matiz;
- el enlace al PR, y que los vídeos aparecerán en
  https://github.com/primewievoficial-bot/Iprofix15-/releases en unos minutos.

## Si algo falla

- **No se confirman cuatro datos:** programar los que se confirmen, dejar el resto del plan como
  «hueco» y decirlo en el resumen. Nunca rellenar con un dato sin fuente.
- **El push, el PR o la fusión fallan:** no reintentar a la fuerza. Dejar el trabajo en la rama y
  explicar en el resumen qué falló.
- **Un montaje falla en GitHub Actions** (sin voz, sin red): el flujo termina en rojo y lo reintenta
  el siguiente jueves, o a mano con «Run workflow».

## Subir a YouTube

Los vídeos quedan en las releases de GitHub, cada uno con su descripción. Para que también se suban
solos haría falta:

1. un proyecto de Google Cloud con la YouTube Data API activada y credenciales OAuth del canal;
2. guardar esas credenciales como secretos del repositorio;
3. y, para que salgan **públicos**, pasar la auditoría de Google para apps de la API: sin ella, los
   vídeos subidos por la API quedan en privado.

Mientras tanto, subir cada Short es abrir su release, descargar el MP4 y pegar la descripción.

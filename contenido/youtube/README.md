# Contenido de YouTube · iProfix15

El canal es **solo de Shorts** con el formato **«¿Sabías que…?»**: una curiosidad de tecnología por
vídeo, con la voz de **Dani**, el presentador ficticio del canal (ver `.claude/youtube/voice.md`).

## Cómo funciona, sin intervención

1. **Cada jueves por la mañana**, una tarea programada de Claude Code escribe los cuatro Shorts de la
   próxima semana sin plan, con las fuentes buscadas en internet, y lo fusiona en `main`.
2. **GitHub Actions monta los vídeos** en cuanto entran en `main`: imágenes con licencia libre, voz
   sintética y subtítulos. Cada Short queda como descarga en
   [Releases](https://github.com/primewievoficial-bot/Iprofix15-/releases) (`short-NN`), con su
   descripción, fuentes y atribuciones listas para pegar.
3. **Lo único manual:** subir el MP4 a YouTube el día que toca.

Detalles en [`AUTOMATIZACION.md`](AUTOMATIZACION.md). Código del montaje en `herramientas/shorts/`.

## Shorts

| Tanda | Shorts | Fuentes |
|---|---|---|
| [Tanda 1](shorts/tanda-01.md) | 01–10 (7 programados, 2 de reserva, 09 descartado) | Comprobadas, con enlaces |
| [Tanda 2](shorts/tanda-02.md) | 11–20 (8 programados, 2 de reserva) | Comprobadas, con enlaces |

Datos para el montaje: [`shorts/datos/`](shorts/datos/).

## Planes semanales

- [Semana del 19 al 25 de octubre](planes/semana-2026-10-19.md): Shorts 01–03
- [Semana del 26 de octubre al 1 de noviembre](planes/semana-2026-10-26.md): Shorts 04–07
- [Semana del 2 al 8 de noviembre](planes/semana-2026-11-02.md): Shorts 11–14
- [Semana del 9 al 15 de noviembre](planes/semana-2026-11-09.md): Shorts 15–18

## Auditorías

- [19 de octubre: previa al lanzamiento](auditorias/2026-10-19-previa-lanzamiento.md). Hecha cuando
  el canal iba a ser de tutoriales largos. Su arreglo principal sigue valiendo: comprobar los datos
  antes de publicar.

## La regla del canal

**Ningún dato sin fuente comprobada.** Cada Short lleva enlazadas sus fuentes, y la descripción de
YouTube las incluye. Un canal de curiosidades vive de que lo que cuenta sea verdad.

## Sobre las puntuaciones

`hookscore.py` solo entiende inglés, así que se puntuó la traducción literal de cada arranque. Las
curiosidades puras puntúan bajo en «STAKES», porque no cuestan nada al espectador. Es una
orientación, no una predicción.

## Historial

El canal empezó planificado como tutoriales largos de reparación (cambio de batería y de pantalla del
iPhone 13). Esos guiones se convirtieron en Shorts de la tanda 1, y los originales están en el
historial de Git.

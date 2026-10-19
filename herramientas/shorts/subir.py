#!/usr/bin/env python3
"""subir.py - sube un Short montado a YouTube con la YouTube Data API v3.

    python3 subir.py datos/11.json salida/11.mp4 salida/11-descripcion.txt

Necesita tres variables de entorno (secretos del repositorio en GitHub):
YT_CLIENT_ID, YT_CLIENT_SECRET y YT_REFRESH_TOKEN. Ver contenido/youtube/SUBIR_A_YOUTUBE.md.

El vídeo se sube como privado y programado para publicarse el día de «publicacion» del JSON a la
hora SHORTS_HORA (por defecto 18:00, hora de España). Si esa fecha ya pasó, se publica al momento.
Un Short sin fecha (reserva) no se sube.

Ojo: mientras el proyecto de Google Cloud no pase la auditoría de la API de YouTube, YouTube deja
los vídeos subidos por la API bloqueados en privado, aunque estén programados.

Escribe el identificador del vídeo en la salida estándar. Sale con código 3 si se agotó la cuota
diaria de la API, para que el flujo pare y lo reintente al día siguiente.
"""
import datetime, json, os, sys, urllib.error, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

HORA = os.environ.get("SHORTS_HORA", "18:00")
ZONA = ZoneInfo("Europe/Madrid")


def token():
    datos = urllib.parse.urlencode({
        "client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"}).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", datos, timeout=30) as r:
        return json.load(r)["access_token"]

def estado(publicacion):
    st = {"selfDeclaredMadeForKids": False, "embeddable": True, "license": "youtube"}
    if os.environ.get("SHORTS_SOLO_PRIVADO"):  # subida de prueba
        st["privacyStatus"] = "private"
        return st
    h, m = map(int, HORA.split(":"))
    fecha = datetime.date.fromisoformat(publicacion)
    cuando = datetime.datetime(fecha.year, fecha.month, fecha.day, h, m, tzinfo=ZONA)
    if cuando > datetime.datetime.now(ZONA) + datetime.timedelta(minutes=30):
        st["privacyStatus"] = "private"
        st["publishAt"] = cuando.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        st["privacyStatus"] = "public"
    return st

def subir(ruta_json, mp4, ruta_desc):
    with open(ruta_json, encoding="utf-8") as f:
        s = json.load(f)
    if not s.get("publicacion"):
        print(f"Short {s['id']}: sin fecha de publicación (reserva), no se sube", file=sys.stderr)
        return None
    with open(ruta_desc, encoding="utf-8") as f:
        descripcion = f.read()
    meta = {
        "snippet": {
            "title": s["titulo"][:100],
            "description": descripcion[:4900],
            "tags": [h.lstrip("#") for h in s.get("hashtags", [])],
            "categoryId": "28",  # Ciencia y tecnología
            "defaultLanguage": "es", "defaultAudioLanguage": "es-ES"},
        "status": estado(s["publicacion"])}
    tam = os.path.getsize(mp4)
    cab = {"Authorization": f"Bearer {token()}", "Content-Type": "application/json; charset=UTF-8",
           "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(tam)}
    url = ("https://www.googleapis.com/upload/youtube/v3/videos"
           "?uploadType=resumable&part=snippet,status")
    req = urllib.request.Request(url, json.dumps(meta).encode(), cab, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            destino = r.headers["Location"]
        with open(mp4, "rb") as f:
            put = urllib.request.Request(destino, f.read(), {"Content-Type": "video/mp4"}, method="PUT")
        with urllib.request.urlopen(put, timeout=600) as r:
            video = json.load(r)
    except urllib.error.HTTPError as e:
        cuerpo = e.read().decode(errors="replace")
        if "quotaExceeded" in cuerpo or "uploadLimitExceeded" in cuerpo:
            print(f"Cuota de YouTube agotada: {cuerpo[:300]}", file=sys.stderr)
            sys.exit(3)
        raise RuntimeError(f"YouTube respondió {e.code}: {cuerpo[:800]}")
    st = meta["status"]
    cuando = st.get("publishAt", "al momento")
    print(f"Short {s['id']} subido: https://youtu.be/{video['id']} ({st['privacyStatus']}, "
          f"publicación {cuando})", file=sys.stderr)
    return video["id"]

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    vid = subir(*sys.argv[1:])
    if vid:
        print(vid)

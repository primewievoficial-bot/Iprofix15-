#!/usr/bin/env python3
"""montar.py - monta un Short vertical a partir de su archivo de datos.

    python3 montar.py contenido/youtube/shorts/datos/11.json --salida salida/
    python3 montar.py contenido/youtube/shorts/datos/*.json --salida salida/
    python3 montar.py datos/11.json --salida salida/ --sin-red    # prueba sin internet

Para cada bloque del guion busca una imagen con licencia libre (Wikimedia Commons y, si no hay,
Openverse), genera la voz con edge-tts y compone un vídeo 1080x1920 con ffmpeg: imagen centrada
sobre su propio fondo desenfocado, un zoom lento, el texto del gancho los primeros segundos y
subtítulos. Escribe además NN-descripcion.txt con el título, las fuentes del dato y la atribución
de cada imagen, que es obligatoria para las licencias CC BY y CC BY-SA.

Solo se aceptan imágenes de dominio público, CC0, CC BY o CC BY-SA. Nunca NC (no comercial) ni ND
(sin obras derivadas), y nunca imágenes sin licencia clara.

Con --sin-red no se conecta a nada: usa tarjetas de texto en lugar de imágenes y silencio en lugar
de voz, con la duración que tendría la voz. Sirve para probar el montaje.
"""
import argparse, asyncio, json, os, re, shutil, subprocess, sys, tempfile, textwrap
import urllib.parse, urllib.request

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
VOZ = os.environ.get("SHORTS_VOZ", "es-ES-AlvaroNeural")
UA = "iProfix15-shorts/1.0 (https://github.com/primewievoficial-bot/Iprofix15-)"
FUENTE = next((f for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                           "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")
               if os.path.exists(f)), None)
PAUSA = 0.25          # silencio entre bloques, en segundos
PALABRAS_POR_SEG = 2.6  # solo para --sin-red

LICENCIA_OK = re.compile(r"^(public domain|pd|cc0|cc[- ]by(-sa)?([- ]\d(\.\d)?)?)", re.I)
LICENCIA_NO = re.compile(r"\b(nc|nd|fair use|non-?free|all rights)\b", re.I)


# --- imágenes ----------------------------------------------------------------------------------

def http_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def descargar(url, ruta):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r, open(ruta, "wb") as f:
        shutil.copyfileobj(r, f)

def limpiar_html(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", t or "")).strip()

def licencia_valida(nombre):
    return bool(nombre) and LICENCIA_OK.match(nombre.strip()) and not LICENCIA_NO.search(nombre)

def buscar_commons(consulta, usadas):
    q = urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
        "gsrsearch": f"{consulta} filetype:bitmap", "gsrlimit": 15, "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 1280})
    datos = http_json(f"https://commons.wikimedia.org/w/api.php?{q}")
    paginas = sorted(datos.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    for p in paginas:
        info = (p.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata", {})
        lic = meta.get("LicenseShortName", {}).get("value", "")
        if info.get("mime") not in ("image/jpeg", "image/png") or info.get("width", 0) < 640:
            continue
        if not licencia_valida(lic) or info.get("descriptionurl") in usadas:
            continue
        return {"url": info.get("thumburl") or info["url"], "pagina": info["descriptionurl"],
                "autor": limpiar_html(meta.get("Artist", {}).get("value", "")) or "Desconocido",
                "licencia": lic, "origen": "Wikimedia Commons",
                "titulo": p["title"].removeprefix("File:")}
    return None

def buscar_openverse(consulta, usadas):
    q = urllib.parse.urlencode({"q": consulta, "license": "by,by-sa,cc0,pdm", "page_size": 15,
                                "mature": "false"})
    for r in http_json(f"https://api.openverse.org/v1/images/?{q}").get("results", []):
        if (r.get("width") or 0) < 640 or r.get("foreign_landing_url") in usadas:
            continue
        lic = f"CC {r['license'].upper()} {r.get('license_version') or ''}".strip()
        if r["license"] in ("cc0", "pdm"):
            lic = "CC0" if r["license"] == "cc0" else "Public domain"
        return {"url": r["url"], "pagina": r.get("foreign_landing_url") or r["url"],
                "autor": r.get("creator") or "Desconocido", "licencia": lic,
                "origen": f"Openverse ({r.get('source', '')})", "titulo": r.get("title") or ""}
    return None

def buscar_imagen(consulta, usadas):
    for buscador in (buscar_commons, buscar_openverse):
        try:
            img = buscador(consulta, usadas)
        except Exception as e:  # una caída de un buscador no debe parar el Short
            print(f"    aviso: {buscador.__name__} falló para «{consulta}»: {e}", file=sys.stderr)
            continue
        if img:
            return img
    return None


# --- voz -----------------------------------------------------------------------------------------

async def _tts(texto, ruta):
    import edge_tts
    await edge_tts.Communicate(texto, VOZ, rate="+8%").save(ruta)

def generar_voz(texto, ruta, sin_red):
    if sin_red:
        dur = max(1.5, len(texto.split()) / PALABRAS_POR_SEG)
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", f"{dur:.2f}",
             "-c:a", "libmp3lame", "-q:a", "4", ruta])
    else:
        for intento in range(3):
            try:
                asyncio.run(_tts(texto, ruta))
                break
            except Exception as e:
                if intento == 2:
                    raise RuntimeError(f"no se pudo generar la voz: {e}")
    return duracion(ruta)


# --- composición ---------------------------------------------------------------------------------

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"falló: {' '.join(cmd[:4])}…\n{r.stderr[-1500:]}")
    return r.stdout

def duracion(ruta):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "default=nw=1:nk=1", ruta]).strip())

def fuente(tam):
    return ImageFont.truetype(FUENTE, tam) if FUENTE else ImageFont.load_default()

def lienzo_desde_imagen(ruta_img, ruta_png):
    """Imagen centrada sobre su propia versión ampliada, desenfocada y oscurecida."""
    img = Image.open(ruta_img).convert("RGB")
    fondo = img.copy()
    esc = max(W / fondo.width, H / fondo.height)
    fondo = fondo.resize((int(fondo.width * esc) + 1, int(fondo.height * esc) + 1))
    x, y = (fondo.width - W) // 2, (fondo.height - H) // 2
    fondo = fondo.crop((x, y, x + W, y + H)).filter(ImageFilter.GaussianBlur(40))
    fondo = Image.eval(fondo, lambda v: int(v * 0.45))
    ancho = W - 80
    alto = int(img.height * ancho / img.width)
    if alto > 1150:
        alto = 1150
        ancho = int(img.width * alto / img.height)
    img = img.resize((ancho, alto))
    fondo.paste(img, ((W - ancho) // 2, 300 + (1150 - alto) // 2))
    fondo.save(ruta_png)

def lienzo_tarjeta(texto, ruta_png):
    """Plan B sin imagen: tarjeta con el texto del bloque, con los colores del canal."""
    img = Image.new("RGB", (W, H), (18, 24, 38))
    d = ImageDraw.Draw(img)
    lineas = textwrap.wrap(texto, 22)[:7]
    f = fuente(70)
    alto = len(lineas) * 90
    for i, l in enumerate(lineas):
        ancho = d.textlength(l, font=f)
        d.text(((W - ancho) / 2, (H - alto) / 2 + i * 90), l, font=f, fill=(240, 240, 240))
    img.save(ruta_png)

def ass_tiempo(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"

def ass_texto(t):
    return t.replace("\\", "").replace("{", "(").replace("}", ")")

def escribir_ass(ruta, gancho, bloques_tiempos):
    """Subtítulos en trozos de pocas palabras, repartidos según su longitud dentro de cada bloque."""
    cab = textwrap.dedent(f"""\
        [Script Info]
        ScriptType: v4.00+
        PlayResX: {W}
        PlayResY: {H}

        [V4+ Styles]
        Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
        Style: Sub,DejaVu Sans,76,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,6,2,2,70,70,330,1
        Style: Gancho,DejaVu Sans,104,&H0000E5FF,&H0000E5FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,8,3,8,60,60,170,1
        Style: Marca,DejaVu Sans,40,&H99FFFFFF,&H99FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,9,40,50,60,1

        [Events]
        Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
        """)
    eventos = []
    total = bloques_tiempos[-1][2] if bloques_tiempos else 0
    eventos.append(f"Dialogue: 1,{ass_tiempo(0)},{ass_tiempo(min(2.8, total))},Gancho,,0,0,0,,"
                   f"{{\\fad(150,250)}}{ass_texto(gancho)}")
    eventos.append(f"Dialogue: 0,{ass_tiempo(0)},{ass_tiempo(total)},Marca,,0,0,0,,iProfix15")
    for texto, ini, fin in bloques_tiempos:
        palabras = texto.split()
        trozos, actual = [], []
        for p in palabras:
            actual.append(p)
            if len(actual) >= 4 or re.search(r"[.,;:?!»]$", p):
                trozos.append(" ".join(actual))
                actual = []
        if actual:
            trozos.append(" ".join(actual))
        peso = sum(len(t) for t in trozos) or 1
        t = ini
        for tr in trozos:
            d = (fin - ini) * len(tr) / peso
            eventos.append(f"Dialogue: 0,{ass_tiempo(t)},{ass_tiempo(t + d)},Sub,,0,0,0,,{ass_texto(tr)}")
            t += d
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(cab + "\n".join(eventos) + "\n")

def clip_bloque(png, dur, ruta):
    frames = max(1, int(round(dur * FPS)))
    filtro = (f"scale={W * 2}:{H * 2},zoompan=z='min(zoom+0.0006,1.10)':d={frames}"
              f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},format=yuv420p")
    run(["ffmpeg", "-y", "-loop", "1", "-i", png, "-vf", filtro, "-frames:v", str(frames),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", ruta])


# --- Short completo ------------------------------------------------------------------------------

def montar(ruta_json, salida, sin_red):
    with open(ruta_json, encoding="utf-8") as f:
        s = json.load(f)
    sid = s["id"]
    print(f"Short {sid}: {s['titulo']}")
    tmp = tempfile.mkdtemp(prefix=f"short{sid}-")
    usadas, atribuciones, clips, audios, tiempos = set(), [], [], [], []
    t = 0.0
    silencio = os.path.join(tmp, "pausa.mp3")
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(PAUSA),
         "-c:a", "libmp3lame", "-q:a", "4", silencio])
    for i, b in enumerate(s["bloques"]):
        voz = os.path.join(tmp, f"voz{i}.mp3")
        dur = generar_voz(b["texto"], voz, sin_red) + PAUSA
        png = os.path.join(tmp, f"lienzo{i}.png")
        img = None if sin_red else buscar_imagen(b["imagen"], usadas)
        if img:
            bruta = os.path.join(tmp, f"img{i}")
            descargar(img["url"], bruta)
            lienzo_desde_imagen(bruta, png)
            usadas.add(img["pagina"])
            atribuciones.append(img)
            print(f"  bloque {i + 1}: {img['titulo']} ({img['licencia']})")
        else:
            lienzo_tarjeta(b.get("tarjeta") or s["texto_pantalla"], png)
            print(f"  bloque {i + 1}: sin imagen para «{b['imagen']}», tarjeta de texto")
        clip = os.path.join(tmp, f"clip{i}.mp4")
        clip_bloque(png, dur, clip)
        clips.append(clip)
        audios += [voz, silencio]
        tiempos.append((b["texto"], t, t + dur - PAUSA))
        t += dur

    lista_v = os.path.join(tmp, "v.txt")
    lista_a = os.path.join(tmp, "a.txt")
    with open(lista_v, "w") as f:
        f.writelines(f"file '{c}'\n" for c in clips)
    with open(lista_a, "w") as f:
        f.writelines(f"file '{a}'\n" for a in audios)
    ass = os.path.join(tmp, "subs.ass")
    escribir_ass(ass, s["texto_pantalla"], tiempos)

    os.makedirs(salida, exist_ok=True)
    mp4 = os.path.join(salida, f"{sid}.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lista_v,
         "-f", "concat", "-safe", "0", "-i", lista_a,
         "-vf", f"ass={ass}", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
         "-shortest", "-movflags", "+faststart", mp4])

    with open(os.path.join(salida, f"{sid}-descripcion.txt"), "w", encoding="utf-8") as f:
        f.write(descripcion(s, atribuciones))
    print(f"  -> {mp4} ({duracion(mp4):.1f} s, {len(atribuciones)} imágenes con licencia)")
    shutil.rmtree(tmp, ignore_errors=True)
    return mp4

def descripcion(s, atribuciones):
    lineas = [s["titulo"], "", s["bloques"][0]["texto"], ""]
    if s.get("fuentes"):
        lineas.append("Fuentes:")
        lineas += [f"- {u}" for u in s["fuentes"]]
        lineas.append("")
    if atribuciones:
        lineas.append("Imágenes:")
        for a in atribuciones:
            lineas.append(f"- «{a['titulo']}», {a['autor']}, {a['licencia']}, vía {a['origen']}: {a['pagina']}")
        lineas.append("")
    lineas.append("Voz generada por síntesis de voz. Dani es la voz ficticia del canal.")
    lineas.append("")
    lineas.append(" ".join(s.get("hashtags", ["#SabíasQue", "#Tecnología", "#Shorts"])))
    return "\n".join(lineas) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("datos", nargs="+", help="archivos NN.json de contenido/youtube/shorts/datos/")
    ap.add_argument("--salida", default="salida")
    ap.add_argument("--sin-red", action="store_true", help="probar sin imágenes ni voz reales")
    a = ap.parse_args()
    fallos = []
    for d in a.datos:
        try:
            montar(d, a.salida, a.sin_red)
        except Exception as e:
            print(f"ERROR en {d}: {e}", file=sys.stderr)
            fallos.append(d)
    if fallos:
        print(f"{len(fallos)} Short(s) sin montar: {', '.join(fallos)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

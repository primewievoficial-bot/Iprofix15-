# Subir los Shorts a YouTube automáticamente

El flujo de GitHub Actions ya sabe subir cada Short a YouTube, programado para publicarse su día a las
18:00 (hora de España). Le faltan las credenciales de tu canal, que solo puedes crear tú.

Son tres fases:

1. **Credenciales** (unos 20 minutos, una sola vez).
2. **Prueba:** subir un Short en privado para comprobar que funciona.
3. **Auditoría de Google y activación.** Sin auditoría, YouTube deja **bloqueados en privado** todos
   los vídeos subidos por la API y no se pueden publicar. Por eso la subida real no se activa hasta
   que Google apruebe el proyecto.

---

## Fase 1 · Credenciales

Hazlo con la **cuenta de Google dueña del canal**.

### 1. Crear el proyecto

1. Entra en https://console.cloud.google.com.
2. Arriba, en el selector de proyectos: **Nuevo proyecto**. Nombre: `iprofix15-shorts`. Crear.
3. Comprueba que el proyecto nuevo está seleccionado arriba.

### 2. Activar la API de YouTube

1. Menú > **APIs y servicios** > **Biblioteca**.
2. Busca **YouTube Data API v3** > **Habilitar**.

### 3. Pantalla de consentimiento

1. Menú > **APIs y servicios** > **Pantalla de consentimiento de OAuth** (puede llamarse **Google
   Auth Platform**). Pulsa **Comenzar** si te lo pide.
2. Nombre de la aplicación: `iProfix15 Shorts`. Correo de asistencia: el tuyo.
3. Público: **Externo**. Datos de contacto: tu correo. Acepta y crea.
4. En **Público**, añade tu correo como **usuario de prueba**.
5. Muy importante: en **Público**, pulsa **Publicar aplicación** para pasarla a **En producción**. Si
   se queda en «Prueba», Google invalida el permiso cada 7 días y la subida deja de funcionar.

### 4. Crear el cliente OAuth

1. **Clientes** (o **Credenciales** > **Crear credenciales** > **ID de cliente de OAuth**).
2. Tipo de aplicación: **Aplicación web**. Nombre: `iprofix15-github`.
3. En **URI de redirección autorizados**, añade exactamente:
   `https://developers.google.com/oauthplayground`
4. Crear. Copia el **ID de cliente** y el **Secreto del cliente** y guárdalos.

### 5. Conseguir el token de actualización

1. Abre https://developers.google.com/oauthplayground.
2. Arriba a la derecha, el engranaje ⚙️: marca **Use your own OAuth credentials** y pega el ID de
   cliente y el secreto.
3. A la izquierda, en la caja de abajo («Input your own scopes»), escribe:
   `https://www.googleapis.com/auth/youtube.upload`
   y pulsa **Authorize APIs**.
4. Entra con la cuenta del canal. Si tienes varios canales, elige el del canal de iProfix15.
5. Saldrá «Google no ha verificado esta aplicación»: es tu propia aplicación. Pulsa
   **Configuración avanzada** > **Ir a iProfix15 Shorts** > **Continuar**.
6. De vuelta en el Playground: **Exchange authorization code for tokens**.
7. Copia el **Refresh token** (empieza por `1//`).

### 6. Guardar las credenciales en GitHub

1. Abre https://github.com/primewievoficial-bot/Iprofix15-/settings/secrets/actions.
2. **New repository secret**, tres veces:

| Nombre | Valor |
|---|---|
| `YT_CLIENT_ID` | el ID de cliente |
| `YT_CLIENT_SECRET` | el secreto del cliente |
| `YT_REFRESH_TOKEN` | el refresh token |

No pegues estas credenciales en ningún otro sitio: ni en el chat, ni en un archivo del repositorio.

---

## Fase 2 · Prueba

1. Abre https://github.com/primewievoficial-bot/Iprofix15-/actions/workflows/montar-shorts.yml.
2. **Run workflow**. En «probar_subida» escribe `1` y pulsa **Run workflow**.
3. Cuando termine (unos minutos), en **YouTube Studio** > **Contenido** debería aparecer el Short 01
   en **privado**. Probablemente con el aviso de bloqueo de la API: es lo esperado.

Esa subida de prueba no cuenta: el Short 01 sigue pendiente de su subida real.

Si falla, abre la ejecución y mira el paso «Probar la subida a YouTube». Los errores habituales:

- `invalid_grant`: el refresh token caducó o la app estaba en «Prueba». Repite el paso 5 con la app
  en producción.
- `insufficientPermissions` o `youtubeSignupRequired`: la cuenta del paso 5 no es la del canal.

---

## Fase 3 · Auditoría y activación

### Pedir la auditoría

1. Formulario oficial: **YouTube API Services – Audit and Quota Extension Form**
   (https://support.google.com/youtube/contact/yt_api_form).
2. Indica que es una herramienta interna que sube vídeos **solo a tu propio canal**, con el número
   del proyecto `iprofix15-shorts`.
3. Google puede pedir capturas del uso, una política de privacidad y detalles del proyecto. Suele
   tardar semanas.

### Activar la subida real

Cuando Google apruebe el proyecto:

1. Abre https://github.com/primewievoficial-bot/Iprofix15-/settings/variables/actions.
2. **New repository variable**: nombre `YT_SUBIR`, valor `si`.

Desde ese momento, cada día a las 10:30 UTC el flujo sube los Shorts con fecha que aún no estén en
YouTube, programados para su día a las 18:00, y apunta el enlace en su release.

### Cosas a saber

- **Cuota:** la API permite unas 6 subidas al día. Si hay más pendientes, el resto se sube al día
  siguiente.
- **Si una fecha ya pasó**, el Short se publica en el momento de subirlo.
- **Las reservas** (sin fecha) no se suben.
- **Cambiar la hora:** variable de entorno `SHORTS_HORA` en el flujo (por defecto `18:00`).
- **Parar la subida:** borra la variable `YT_SUBIR` o cámbiala a otro valor.

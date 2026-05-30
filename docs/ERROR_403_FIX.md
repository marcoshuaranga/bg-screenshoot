# 🔴 Error: 403 access_denied - SOLUCIÓN RÁPIDA

## El Problema
```
Error 403: access_denied
The app is currently being tested, and can only be accessed by developer-approved testers.
```

## La Causa
❌ **No te agregaste como usuario de prueba** en la pantalla de consentimiento OAuth.

---

## ✅ SOLUCIÓN (5 minutos)

### Paso 1: Ir a la pantalla de consentimiento OAuth
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Selecciona tu proyecto
3. Ve a **"APIs & Services"** > **"OAuth consent screen"** (menú izquierdo)

### Paso 2: Agregar usuarios de prueba
1. Baja hasta la sección **"Test users"**
2. Haz clic en **"+ ADD USERS"**
3. **Escribe tu correo de Gmail** (el que usarás para autenticarte)
   ```
   tu-correo@gmail.com
   ```
4. Haz clic en **"Add"**
5. Haz clic en **"SAVE"** abajo

### Paso 3: Verificar configuración

Asegúrate de que:
- ✅ Tu correo aparece en la lista de "Test users"
- ✅ El estado muestra "Testing"
- ✅ El scope `drive.file` está agregado (en la sección "Scopes")

### Paso 4: Reintentar autenticación

1. **Elimina el token anterior** (si existe):
   ```bash
   del token.pickle
   ```

2. **Vuelve a ejecutar:**
   ```bash
   .\.venv\Scripts\python screenshot_capture.py -s -g
   ```

3. Se abrirá el navegador nuevamente
4. Selecciona tu cuenta de Gmail
5. **Ahora debería funcionar** ✅

---

## Verificación Visual

Cuando funcione correctamente, verás:

```
🔐 Authenticating with Google Drive...
✅ Connected to Google Drive
📁 Using Google Drive folder: Screenshots
💾 Local folder: C:\Users\TuNombre\Screenshots
📸 Screenshot saved and uploaded to Google Drive: screenshot_20260527_123456.png
```

---

## Si el error persiste

### Opción A: Verificar que usaste el correo correcto
- El correo en "Test users" debe ser EXACTAMENTE el mismo que usas al autenticarte
- Distingue entre correos personales y de trabajo

### Opción B: Revisar scopes
1. En "OAuth consent screen" > **"EDIT APP"**
2. Ve a la sección **"Scopes"**
3. Asegúrate de tener: `.../auth/drive.file`
4. Si no está, agrégalo:
   - Click **"ADD OR REMOVE SCOPES"**
   - Busca "drive.file"
   - Selecciona: `https://www.googleapis.com/auth/drive.file`
   - **SAVE AND CONTINUE**

### Opción C: Esperar 5 minutos
- A veces Google tarda unos minutos en propagar los cambios
- Espera 5 minutos y vuelve a intentar

---

## ⚠️ MUY IMPORTANTE

**NO** intentes "Publicar" la app para solucionar esto.

La app en modo **"Testing"** funciona perfectamente para uso personal, solo necesitas agregarte como usuario de prueba.

---

## Resumen del error

| Error | Causa | Solución |
|-------|-------|----------|
| 403: access_denied | No estás en la lista de Test Users | Agrégarte en OAuth consent screen > Test users |

¿Sigue sin funcionar después de seguir estos pasos?

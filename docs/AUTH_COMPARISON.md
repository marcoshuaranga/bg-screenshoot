# Comparación de métodos de autenticación de Google Drive

## 1. API Keys (Claves de API)
❌ **NO funciona para este caso**

**Qué son:**
- Identificadores simples para tu proyecto
- Solo autenticación, no autorización

**Limitaciones:**
- ❌ Solo para datos públicos (lectura)
- ❌ NO puede acceder a Drive privado
- ❌ NO puede crear/subir archivos
- ❌ Solo para APIs que no requieren datos de usuario

**Ejemplo de uso:** YouTube API (videos públicos), Maps API, etc.

---

## 2. Service Accounts (Cuentas de servicio)
⚠️ **Posible pero NO recomendado para este caso**

**Qué son:**
- Cuentas "robot" con su propio Google Drive
- Para aplicaciones servidor-a-servidor
- No requieren intervención del usuario

**Ventajas:**
- ✅ No requiere autenticación del usuario cada vez
- ✅ Bueno para automatización backend
- ✅ Ideal para empresas/servidores

**Desventajas para uso personal:**
- ❌ Los archivos se suben al Drive de la cuenta de servicio, NO al tuyo
- ❌ No ves los archivos en tu Drive personal
- ❌ Necesitas compartir manualmente desde la cuenta de servicio a tu cuenta
- ❌ Más complejo de configurar para uso personal

**Cuándo usar:**
- Aplicaciones backend/servidor
- Bots automatizados
- Aplicaciones empresariales que gestionan su propio almacenamiento

---

## 3. OAuth 2.0 (Elegido) ✅
✅ **MEJOR OPCIÓN para este caso**

**Qué es:**
- Autorización que actúa en nombre del usuario
- El usuario da permiso explícito a la aplicación

**Ventajas:**
- ✅ Los archivos aparecen en TU Drive personal
- ✅ Tú controlas los permisos
- ✅ Ves y gestionas los archivos directamente en tu Drive
- ✅ Estándar para aplicaciones de escritorio
- ✅ Autenticación una sola vez (token guardado)
- ✅ Puedes revocar acceso cuando quieras

**Desventajas:**
- ⚠️ Requiere configuración inicial (una vez)
- ⚠️ Muestra advertencia "app no verificada" (normal para apps personales)

**Cuándo usar:**
- ✅ Aplicaciones de escritorio
- ✅ Aplicaciones personales
- ✅ Cuando quieres acceso a tu propio Drive
- ✅ Cuando quieres ver archivos en tu cuenta

---

## Resumen para este proyecto

| Método | ¿Funciona? | ¿Archivos en mi Drive? | Complejidad |
|--------|------------|------------------------|-------------|
| API Keys | ❌ No | - | Muy Simple |
| Service Account | ⚠️ Sí | ❌ No (Drive separado) | Compleja |
| OAuth 2.0 | ✅ Sí | ✅ Sí | Media |

**Elegí OAuth 2.0 porque:**
1. Los screenshots aparecen directamente en tu Google Drive personal
2. Puedes verlos, organizarlos y compartirlos fácilmente
3. Es el método estándar para aplicaciones que actúan "en tu nombre"
4. Una vez configurado, funciona automáticamente

---

## ¿Prefieres usar Service Account?

Si prefieres usar Service Account (aunque los archivos no aparecerán en tu Drive personal), puedo modificar el código. Sería útil si:
- Quieres un Drive completamente separado para screenshots
- No te importa no ver los archivos en tu Drive personal
- Prefieres una configuración más simple (sin OAuth browser flow)

**¿Quieres que cambie a Service Account?**

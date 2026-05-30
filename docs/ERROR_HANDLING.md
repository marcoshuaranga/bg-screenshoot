# Sistema de Manejo de Errores - Google Drive

## Patrones de Diseño Implementados

### 1. **Circuit Breaker Pattern** (Modo Offline Automático)

Protege contra fallos repetidos en Google Drive desactivando temporalmente las subidas.

**Estados:**
- 🟢 **CLOSED** (Normal): Todo funciona correctamente
- 🔴 **OPEN** (Offline): Demasiados fallos, subidas desactivadas temporalmente
- 🟡 **HALF-OPEN** (Prueba): Probando si el servicio se recuperó

**Funcionamiento:**
```
1. Subida falla → contador aumenta
2. Después de 5 fallos → Circuit OPEN (offline por 5 minutos)
3. Después de 5 minutos → Circuit HALF-OPEN (prueba conexión)
4. Si 2 subidas exitosas → Circuit CLOSED (vuelve a normal)
```

**Ventajas:**
- ✅ No desperdicia recursos intentando subir repetidamente
- ✅ Protege contra problemas de red temporales
- ✅ Recuperación automática
- ✅ Los screenshots se siguen guardando localmente

---

### 2. **Retry Pattern** (Reintentos Inteligentes)

Reintenta subidas fallidas con retardo exponencial.

**Configuración:**
- **Intentos máximos:** 3
- **Retardo base:** 2 segundos
- **Estrategia:** Exponential backoff (2s, 4s, 8s)

**Funcionamiento:**
```
Intento 1: Falla → Espera 2s
Intento 2: Falla → Espera 4s
Intento 3: Falla → Registra error y abre circuit
```

**Errores que NO se reintentan:**
- ❌ **Autenticación** (401/403): Token inválido
- ❌ **Cuota excedida**: Drive lleno
- ❌ **Permisos**: Sin acceso a la carpeta

**Errores que SÍ se reintentan:**
- ✅ **Red**: Timeout, conexión perdida
- ✅ **Servidor**: Error 500, 503 (servidor ocupado)
- ✅ **Desconocidos**: Otros errores temporales

---

### 3. **Error Classification** (Clasificación de Errores)

Identifica el tipo de error para tomar decisiones inteligentes.

**Tipos de error:**

| Tipo | Descripción | ¿Reintenta? | Ejemplo |
|------|-------------|-------------|---------|
| 🌐 **NETWORK** | Problemas de conexión | ✅ Sí | Timeout, sin internet |
| 🔐 **AUTH** | Autenticación fallida | ❌ No | Token expirado |
| 💾 **QUOTA** | Cuota excedida | ❌ No | Drive lleno |
| 🚫 **PERMISSION** | Sin permisos | ❌ No | Carpeta eliminada |
| ❓ **UNKNOWN** | Error desconocido | ✅ Sí | Otros |

---

## Ejemplos de Escenarios

### Escenario 1: Sin Internet Temporal
```
[1] 📸 screenshot.png
⚠️  Upload failed (attempt 1/3): network
🔄 Retrying in 2s...
⚠️  Upload failed (attempt 2/3): network
🔄 Retrying in 4s...
[Internet vuelve]
✅ [1] 📸 screenshot.png ☁️
```

### Escenario 2: Sin Internet Prolongado
```
[1] 📸 screenshot.png
❌ All 3 attempts failed: network
[2] 📸 screenshot.png
❌ All 3 attempts failed: network
[3-5] ... fallos continuos ...
🔴 Circuit breaker OPEN - Too many failures. Retry in 300s
[6-20] 📸 screenshots (guardados solo local, sin intentar subir)
⚠️  Circuit breaker OPEN - Skipping upload (retry in 120s)
...
[Después de 5 minutos]
🔄 Circuit breaker: Testing if service recovered...
✅ Circuit breaker: Service recovered - CLOSED
```

### Escenario 3: Token Expirado
```
[1] 📸 screenshot.png
❌ Non-retryable error (authentication): Invalid credentials
[2-∞] 📸 screenshots (guardados solo local)
⚠️  Circuit breaker OPEN
```
**Solución:** Elimina `token.pickle` y reautentica

### Escenario 4: Drive Lleno
```
[1] 📸 screenshot.png
❌ Non-retryable error (quota_exceeded): Storage quota exceeded
🔴 Circuit breaker OPEN - Too many failures
[2-∞] 📸 screenshots (guardados solo local)
```
**Solución:** Libera espacio en Google Drive

---

## Control Manual

### Desde System Tray

**Ver estado:**
- Menú → Muestra "Drive: ✅ Online" o "Drive: ⚠️ Offline"

**Resetear conexión:**
- Si Circuit está OPEN → Aparece opción "🔄 Reset Drive Connection"
- Click para forzar reintento inmediato

---

## Logs de Ejemplo

```log
2026-05-27 17:00:00 - INFO - [1] 📸 screenshot_20260527_170000.png ☁️
2026-05-27 17:01:00 - WARNING - ⚠️  Upload failed (attempt 1/3): network
2026-05-27 17:01:02 - INFO - 🔄 Retrying in 2s...
2026-05-27 17:01:04 - INFO - [2] 📸 screenshot_20260527_170100.png ☁️
2026-05-27 17:02:00 - ERROR - ❌ All 3 attempts failed: Connection timeout
2026-05-27 17:03:00 - WARNING - 🔴 Circuit breaker OPEN - Too many failures. Retry in 300s
2026-05-27 17:08:00 - INFO - 🔄 Circuit breaker: Testing if service recovered...
2026-05-27 17:08:05 - INFO - ✅ Circuit breaker: Service recovered - CLOSED
```

---

## Configuración

Puedes ajustar los parámetros en `screenshot_tray.py`:

```python
self.circuit_breaker = CircuitBreaker(
    failure_threshold=5,      # Fallos antes de abrir circuit
    timeout_duration=300,     # Segundos en modo offline (5 min)
    success_threshold=2       # Éxitos para cerrar circuit
)

retry_with_backoff(
    _upload,
    max_retries=3,           # Intentos por subida
    base_delay=2             # Segundos base (2, 4, 8...)
)
```

---

## Ventajas del Sistema

✅ **Robusto**: Maneja fallos sin detener el programa
✅ **Inteligente**: Diferencia errores temporales de permanentes
✅ **Eficiente**: No desperdicia recursos en fallos repetidos
✅ **Recuperación automática**: Vuelve a intentar cuando el servicio se recupera
✅ **Transparente**: Logs detallados de cada error
✅ **Local siempre funciona**: Screenshots nunca se pierden

---

## Garantías

- 🔒 **Los screenshots SIEMPRE se guardan localmente** (independiente de Drive)
- 🔄 **El programa NUNCA se detiene** por errores de Drive
- 📝 **Todos los errores se registran** en el log
- ⚡ **Recuperación automática** cuando el servicio vuelve

# Ejecutar en Background (sin mantener terminal abierta)

## El Problema
❌ Si cierras la terminal, el programa se detiene.

## Soluciones para Windows

### ✅ Opción 1: pythonw.exe (Más Simple)

**pythonw.exe** ejecuta Python sin mostrar ventana de consola.

**Crear archivo .bat:**

Crea un archivo `start_screenshots.bat`:

```batch
@echo off
cd /d "E:\Users\maracudev\DevDrive\hobby\background-screenshot"
start "" ".venv\Scripts\pythonw.exe" screenshot_capture.py -i 60 -g
```

**Uso:**
1. Doble clic en `start_screenshots.bat`
2. El programa corre en background sin ventana
3. **Para detener:** Usa el Administrador de Tareas (Task Manager)
   - Busca "pythonw.exe"
   - Terminar proceso

**Ventajas:**
- ✅ Simple, un solo clic
- ✅ No hay ventana visible
- ✅ Puedes cerrar todo

**Desventajas:**
- ⚠️ No ves el output/errores
- ⚠️ Debes terminar manualmente desde Task Manager

---

### ✅ Opción 2: Windows Task Scheduler (Recomendado)

Ejecuta automáticamente al iniciar Windows o en horarios específicos.

**Configuración:**

1. Abre **Task Scheduler** (Programador de tareas)
   - Presiona `Win + R`
   - Escribe: `taskschd.msc`

2. **Create Basic Task** (Crear tarea básica)
   - Name: `Screenshot Capture`
   - Description: `Take screenshots every minute`

3. **Trigger** (Desencadenador):
   - Opciones:
     - **"When I log on"** - Al iniciar sesión
     - **"Daily"** - Diariamente a una hora
     - **"At startup"** - Al iniciar Windows

4. **Action** (Acción):
   - **Start a program**
   - Program: `E:\Users\maracudev\DevDrive\hobby\background-screenshot\.venv\Scripts\python.exe`
   - Arguments: `screenshot_capture.py -i 60 -g`
   - Start in: `E:\Users\maracudev\DevDrive\hobby\background-screenshot`

5. **Settings** (Configuración adicional):
   - ✅ Allow task to be run on demand
   - ✅ Run task as soon as possible after scheduled start is missed
   - ✅ If running task does not end when scheduled, do not start new instance

**Ventajas:**
- ✅ Inicia automáticamente
- ✅ Se puede configurar horarios
- ✅ Fácil de activar/desactivar
- ✅ Windows lo gestiona

**Detener:**
- Task Scheduler > Encuentra la tarea > Right-click > **End** o **Disable**

---

### ✅ Opción 3: Minimizar a System Tray (Avanzado)

Crear una versión GUI que se ejecute en la bandeja del sistema.

**Requiere modificar el código** para agregar una interfaz de bandeja.

Bibliotecas necesarias:
- `pystray` - Icon en system tray
- `PIL` - Para el icono

¿Te interesa esta opción? Puedo implementarla.

---

## Comparación Rápida

| Método | Dificultad | Auto-inicio | Fácil de detener | Visible |
|--------|-----------|-------------|------------------|---------|
| pythonw.exe + .bat | ⭐ Fácil | ❌ No | ⚠️ Task Manager | ❌ No |
| Task Scheduler | ⭐⭐ Media | ✅ Sí | ✅ Sí | ❌ No |
| System Tray | ⭐⭐⭐ Avanzado | ✅ Sí | ✅ Sí | ✅ Icono |

---

## Recomendación

Para uso diario: **Task Scheduler**
- Inicia automáticamente
- Fácil de controlar
- No requiere modificar código

Para pruebas rápidas: **pythonw.exe + .bat**
- Simple y rápido
- No es persistente

Para la mejor experiencia: **System Tray app**
- Requiere más trabajo inicial
- Experiencia profesional

---

## ¿Qué opción prefieres?

1. Te creo el archivo `.bat` para pythonw.exe
2. Te doy instrucciones detalladas para Task Scheduler
3. Modifico el código para agregar System Tray

# Python Project Guidelines

Este documento establece las reglas y mejores prácticas para el desarrollo de este proyecto Python.

## 📋 Tabla de Contenidos

1. [Estilo de Código](#estilo-de-código)
2. [Type Hints](#type-hints)
3. [Documentación](#documentación)
4. [Testing](#testing)
5. [Gestión de Dependencias](#gestión-de-dependencias)
6. [Git Workflow](#git-workflow)
7. [Estructura de Proyecto](#estructura-de-proyecto)
8. [Pre-commit Hooks](#pre-commit-hooks)

---

## 🎨 Estilo de Código

### PEP 8 + Ruff

Seguimos [PEP 8](https://peps.python.org/pep-0008/) con configuración de Ruff.

#### Line Length

```python
# ✅ Bien - máximo 120 caracteres
result = some_function(param1, param2, param3)

# ❌ Evitar - líneas muy largas
result = some_very_long_function_name_that_takes_many_parameters(param1, param2, param3, param4, param5, param6, param7, param8)
```

#### Imports

```python
# ✅ Bien - ordenados con isort (automático con Ruff)
import os
import sys
from pathlib import Path

import pytest
from google.auth import credentials

from config_manager import Config
from screenshot_tray import ScreenshotCapture

# ❌ Evitar - desordenados
from screenshot_tray import ScreenshotCapture
import sys
from config_manager import Config
import os
```

#### Naming Conventions

```python
# ✅ Bien
class ScreenshotCapture:  # PascalCase para clases
    def take_screenshot(self):  # snake_case para funciones
        max_retries = 3  # snake_case para variables
        TIMEOUT = 300  # UPPER_CASE para constantes

# ❌ Evitar
class screenshot_capture:  # No usar snake_case en clases
    def TakeScreenshot(self):  # No usar PascalCase en funciones
        MaxRetries = 3  # No usar PascalCase en variables
```

#### Comparaciones

```python
# ✅ Bien - comparaciones pythonic
if value:  # En lugar de == True
if not value:  # En lugar de == False
if value is None:  # Para None

# ❌ Evitar
if value == True:
if value == False:
if value == None:
```

#### String Formatting

```python
# ✅ Bien - f-strings (Python 3.6+)
message = f"Screenshot {count} saved to {path}"

# ✅ También aceptable
message = "Screenshot {} saved to {}".format(count, path)

# ❌ Evitar - % formatting (antiguo)
message = "Screenshot %s saved to %s" % (count, path)
```

### Verificar estilo

```bash
# Verificar issues
uv run ruff check .

# Auto-corregir
uv run ruff check . --fix

# Formatear código
uv run ruff format .
```

---

## 🏷️ Type Hints

Usamos type hints para mejorar la legibilidad y detectar errores.

### Funciones

```python
# ✅ Bien - con type hints
def take_screenshot(region: tuple[int, int, int, int] | None = None) -> bool:
    """Take a screenshot of the screen"""
    return True

# ❌ Evitar - sin type hints
def take_screenshot(region=None):
    return True
```

### Variables (Python 3.6+)

```python
# ✅ Bien - type hints en variables complejas
screenshots: list[Path] = []
config: dict[str, Any] = {}

# Aceptable - tipos simples sin hints
count = 0
name = "screenshot"
```

### Optional y Union

```python
from typing import Optional

# ✅ Bien - Python 3.10+ (preferido)
def process(value: str | None) -> int | None:
    pass

# ✅ También válido - Python 3.5+
def process(value: Optional[str]) -> Optional[int]:
    pass
```

### Type Checking

```bash
# Opcional: usar mypy para verificar tipos
pip install mypy
mypy *.py
```

---

## 📚 Documentación

### Docstrings

Seguimos el estilo **Google** para docstrings.

#### Funciones

```python
def upload_to_drive(filepath: Path, folder_id: str) -> bool:
    """Upload a file to Google Drive.

    Args:
        filepath: Path to the file to upload
        folder_id: Google Drive folder ID

    Returns:
        True if upload successful, False otherwise

    Raises:
        HttpError: If Google Drive API returns an error

    Example:
        >>> upload_to_drive(Path("screenshot.png"), "abc123")
        True
    """
    pass
```

#### Clases

```python
class CircuitBreaker:
    """Circuit Breaker Pattern implementation for API calls.

    The circuit breaker prevents repeated calls to a failing service.
    It has three states: CLOSED (normal), OPEN (failing), and HALF_OPEN (testing).

    Attributes:
        state: Current state of the circuit breaker
        failure_count: Number of consecutive failures
        failure_threshold: Failures before opening circuit

    Example:
        >>> breaker = CircuitBreaker(failure_threshold=5)
        >>> breaker.call(upload_function)
    """
    pass
```

#### Módulos

```python
"""Screenshot capture with Google Drive integration.

This module provides functionality to automatically capture screenshots
and upload them to Google Drive with circuit breaker pattern for reliability.
"""
```

### Comentarios

```python
# ✅ Bien - comentarios que explican POR QUÉ
# Use exponential backoff to avoid overwhelming the API
delay = base_delay * (2 ** attempt)

# ❌ Evitar - comentarios que explican QUÉ (obvio del código)
# Increment counter by 1
counter += 1
```

---

## 🧪 Testing

### Estructura de Tests

```python
class TestScreenshotCapture:
    """Test ScreenshotCapture class"""

    def test_take_screenshot_success(self, mock_pyautogui):
        """Test successful screenshot capture"""
        # Arrange
        capturer = ScreenshotCapture()

        # Act
        result = capturer.take_screenshot()

        # Assert
        assert result is True
        assert capturer.screenshot_count == 1
```

### Naming

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`
- Fixtures: descriptive names sin `test_` prefix

### Coverage Goal

- Mínimo: **70%** coverage
- Objetivo: **80%+** coverage
- Core business logic: **90%+**

### Comandos

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=. --cov-report=html

# Run specific test
uv run pytest tests/test_config_manager.py::TestConfig::test_save_config -v

# Run in watch mode (con pytest-watch)
uv pip install pytest-watch
ptw
```

### Mocking

```python
# ✅ Bien - mock external dependencies
def test_upload_to_drive(mock_drive_service):
    with patch('screenshot_tray.MediaFileUpload'):
        result = upload_to_drive("test.png")
    assert result is True

# ❌ Evitar - no mockear lógica interna
def test_calculate_total():
    with patch('my_module.add'):  # No mockear tu propia lógica
        result = calculate_total(1, 2)
```

---

## 📦 Gestión de Dependencias

### uv - Package Manager

Usamos [uv](https://github.com/astral-sh/uv) como gestor de paquetes (más rápido que pip).

#### Instalar dependencias

```bash
# Crear virtual environment
uv venv

# Instalar desde requirements.txt
uv pip install -r requirements.txt

# Instalar paquete específico
uv pip install requests

# Instalar dev dependencies
uv pip install pytest pytest-cov ruff
```

#### Actualizar requirements.txt

```bash
# Exportar dependencias exactas
uv pip freeze > requirements.txt

# O mejor: mantener requirements.txt manualmente con versiones mínimas
# pyautogui>=0.9.54
# PyYAML>=6.0.1
```

### Versiones

```txt
# ✅ Bien - versiones específicas para prod
pyautogui==0.9.54
PyYAML==6.0.1

# ✅ También válido - versiones mínimas flexibles
pyautogui>=0.9.54,<1.0.0
PyYAML>=6.0.1

# ❌ Evitar - sin versiones (puede romper en futuro)
pyautogui
PyYAML
```

### Separar dependencias

```txt
# requirements.txt - producción
pyautogui==0.9.54
PyYAML==6.0.1

# requirements-dev.txt - desarrollo
-r requirements.txt
pytest==8.1.1
pytest-cov==5.0.0
ruff==0.4.4
```

---

## 🔄 Git Workflow

### Commit Messages

Seguimos [Conventional Commits](https://www.conventionalcommits.org/).

```bash
# ✅ Bien
git commit -m "feat: add circuit breaker pattern for Drive uploads"
git commit -m "fix: handle corrupted YAML config files"
git commit -m "docs: update README with testing section"
git commit -m "test: add tests for config manager"
git commit -m "refactor: simplify error classification logic"

# ❌ Evitar
git commit -m "update"
git commit -m "fix bug"
git commit -m "changes"
```

### Tipos de commits

- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `test`: Agregar o modificar tests
- `refactor`: Refactorización sin cambiar funcionalidad
- `style`: Cambios de formato (whitespace, formatting)
- `chore`: Tareas de mantenimiento (deps, build)
- `perf`: Mejoras de performance

### Branches

```bash
# ✅ Bien - descriptivo
feature/google-drive-integration
fix/circuit-breaker-timeout
docs/update-readme

# ❌ Evitar - genérico
dev
test
fix
```

### .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/

# Testing
.pytest_cache/
htmlcov/
.coverage

# IDE
.vscode/
.idea/
*.swp

# Project specific
credentials.json
token.pickle
logs/
*.log
```

---

## 📂 Estructura de Proyecto

```
background-screenshot/
├── README.md                    # Documentación principal
├── requirements.txt             # Dependencias
├── pyproject.toml              # Configuración (Ruff, etc)
├── pytest.ini                  # Configuración de pytest
├── config.yaml                 # Configuración de usuario
│
├── *.py                        # Módulos principales
│   ├── screenshot_capture.py
│   ├── screenshot_tray.py
│   ├── config_manager.py
│   ├── config_dialog.py
│   └── region_selector.py
│
├── tests/                      # Tests
│   ├── __init__.py
│   ├── conftest.py            # Fixtures compartidos
│   ├── test_*.py              # Test files
│   └── README.md              # Docs de testing
│
├── docs/                       # Documentación adicional
│   ├── GDRIVE_SETUP.md
│   ├── ERROR_HANDLING.md
│   └── ...
│
├── logs/                       # Logs (git ignored)
└── .venv/                      # Virtual env (git ignored)
```

### Módulos

- Un archivo = una responsabilidad principal
- Máximo ~500 líneas por archivo
- Si crece mucho, dividir en módulos

---

## 🎣 Pre-commit Hooks

### Instalación

```bash
uv pip install pre-commit
```

### Configuración (.pre-commit-config.yaml)

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: uv run pytest tests/ -v
        language: system
        pass_filenames: false
        always_run: true
```

### Uso

```bash
# Instalar hooks
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files

# Auto-ejecuta en cada commit
git commit -m "feat: add new feature"
```

---

## 📝 Checklist para Pull Requests

Antes de hacer merge:

- [ ] Tests pasan (`pytest`)
- [ ] Coverage >= 70% (`pytest --cov`)
- [ ] Linter pasa (`ruff check .`)
- [ ] Código formateado (`ruff format .`)
- [ ] Docstrings actualizados
- [ ] README actualizado (si aplica)
- [ ] Commit messages siguen convención

---

## 🚀 CI/CD (Futuro)

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.12"

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv pip install -r requirements.txt

      - name: Run Ruff
        run: uv run ruff check .

      - name: Run tests
        run: uv run pytest tests/ --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 🔧 Herramientas Recomendadas

### Esenciales (ya tienes)

- ✅ **uv** - Package manager
- ✅ **pytest** - Testing framework
- ✅ **pytest-cov** - Coverage
- ✅ **Ruff** - Linter + Formatter

### Opcional pero útiles

- **mypy** - Type checking
- **pre-commit** - Git hooks
- **pytest-watch** - Auto-run tests
- **ipython** - Better REPL
- **black** - Code formatter (alternativa a Ruff format)

### VS Code Extensions

- Python
- Pylance
- Ruff
- Git Graph
- Error Lens

---

## 📖 Referencias

- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pytest Documentation](https://docs.pytest.org/)
- [uv Documentation](https://github.com/astral-sh/uv)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## 🎯 Resumen: Quick Start

```bash
# Setup
uv venv
uv pip install -r requirements.txt

# Antes de commit
uv run ruff check . --fix     # Lint & fix
uv run ruff format .          # Format
uv run pytest tests/ -v       # Test

# Durante desarrollo
uv run pytest tests/ --cov    # Test con coverage
uv run ruff check .           # Solo verificar
```

---

**Última actualización:** 2026-05-27

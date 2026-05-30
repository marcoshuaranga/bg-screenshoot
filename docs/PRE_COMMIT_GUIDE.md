# Pre-commit Hooks - Guía de Uso

## ✅ Instalación Completada

Los pre-commit hooks ya están configurados y activos en este repositorio.

## 🔄 ¿Qué hace automáticamente?

Cada vez que haces `git commit`, automáticamente ejecuta:

1. **Ruff Linter** - Verifica y corrige problemas de código
2. **Ruff Format** - Formatea el código automáticamente
3. **Trailing Whitespace** - Elimina espacios al final de líneas
4. **End of File Fixer** - Asegura que archivos terminen con newline
5. **Check YAML** - Valida sintaxis de config.yaml
6. **Check Large Files** - Previene commits de archivos >1MB
7. **Check Merge Conflicts** - Detecta marcadores de conflicto
8. **Mixed Line Ending** - Normaliza line endings (LF)
9. **Pytest** - Ejecuta los tests

## 🚀 Uso Normal

### Hacer commit (con hooks)

```bash
# Los hooks se ejecutan AUTOMÁTICAMENTE
git add .
git commit -m "feat: add new feature"

# Si algún hook falla o modifica archivos:
# 1. Los archivos modificados NO se commitean
# 2. Debes revisar los cambios
# 3. Agregar de nuevo y re-intentar
git add .
git commit -m "feat: add new feature"
```

### Ejemplo de flujo

```bash
$ git add .
$ git commit -m "feat: add screenshot feature"

# Output:
ruff.....................................Failed
- hook id: ruff
- exit code: 1
Found 3 errors.

ruff-format..............................Passed
trim trailing whitespace.................Passed
pytest-check.............................Passed

# Archivos fueron modificados, agregar de nuevo
$ git add .
$ git commit -m "feat: add screenshot feature"

# Output:
ruff.....................................Passed
ruff-format..............................Passed
trim trailing whitespace.................Passed
pytest-check.............................Passed
[main abc1234] feat: add screenshot feature
```

## 🔧 Comandos Útiles

### Ejecutar hooks manualmente (en todos los archivos)

```bash
uv run pre-commit run --all-files
```

### Ejecutar hook específico

```bash
# Solo Ruff
uv run pre-commit run ruff --all-files

# Solo tests
uv run pre-commit run pytest-check --all-files

# Solo formato
uv run pre-commit run ruff-format --all-files
```

### Saltar hooks (NO RECOMENDADO)

```bash
# En caso de emergencia, puedes saltar los hooks
git commit -m "fix: urgent fix" --no-verify

# ⚠️ Usar solo en casos excepcionales
```

### Actualizar versiones de hooks

```bash
uv run pre-commit autoupdate
```

### Desinstalar hooks

```bash
uv run pre-commit uninstall
```

### Re-instalar hooks

```bash
uv run pre-commit install
```

## 📋 Hooks Configurados

| Hook                        | Descripción                  | Auto-fix |
| --------------------------- | ---------------------------- | -------- |
| **ruff**                    | Linter (PEP 8, imports, etc) | ✅ Sí    |
| **ruff-format**             | Formateador de código        | ✅ Sí    |
| **trailing-whitespace**     | Elimina espacios finales     | ✅ Sí    |
| **end-of-file-fixer**       | Agrega newline final         | ✅ Sí    |
| **check-yaml**              | Valida YAML                  | ❌ No    |
| **check-added-large-files** | Previene archivos grandes    | ❌ No    |
| **check-merge-conflict**    | Detecta conflictos           | ❌ No    |
| **mixed-line-ending**       | Normaliza line endings       | ✅ Sí    |
| **pytest-check**            | Ejecuta tests                | ❌ No    |

## ⚙️ Configuración

La configuración está en `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      # ... otros hooks

  - repo: local
    hooks:
      - id: pytest-check
        entry: uv run pytest tests/ -v --tb=short -x
        # ...
```

## 🎯 Modificar Comportamiento

### Desactivar hook de tests (si es muy lento)

Edita `.pre-commit-config.yaml` y comenta:

```yaml
# - repo: local
#   hooks:
#     - id: pytest-check
#       # ...
```

### Cambiar argumentos de Ruff

```yaml
- id: ruff
  args: [--fix, --exit-non-zero-on-fix, --ignore=E501]
```

### Ejecutar hooks solo en ciertos archivos

```yaml
- id: ruff
  files: ^(screenshot_.*\.py|config_.*\.py)$
```

## 🐛 Troubleshooting

### "Hook failed" pero código parece correcto

```bash
# Ver detalles del error
uv run pre-commit run --all-files --verbose

# Limpiar cache
uv run pre-commit clean
uv run pre-commit install
```

### Tests fallan en pre-commit pero pasan manualmente

```bash
# Verificar que el entorno sea el mismo
uv run pytest tests/ -v

# Si el problema persiste, desactiva pytest hook temporalmente
```

### Hooks muy lentos

```bash
# Opción 1: Desactivar pytest en pre-commit
# Editar .pre-commit-config.yaml y comentar pytest-check

# Opción 2: Ejecutar solo en archivos modificados
# (ya configurado por defecto)
```

## 📚 Workflow Recomendado

### Durante Desarrollo

```bash
# Trabaja normalmente
# Edita archivos...

# Antes de commit, verifica manualmente (opcional)
uv run ruff check . --fix
uv run pytest tests/ -v

# Commit - hooks se ejecutan automáticamente
git add .
git commit -m "feat: new feature"
```

### Si hooks modifican archivos

```bash
# 1. Hooks ejecutan y modifican archivos
git commit -m "feat: new feature"
# > ruff-format.....Failed (files modified)

# 2. Revisar cambios (opcional)
git diff

# 3. Agregar cambios y re-intentar
git add .
git commit -m "feat: new feature"
# > All hooks passed! ✅
```

## 🎓 Tips

1. **Commits pequeños**: Hooks son más rápidos con menos archivos
2. **Fix antes de commit**: Ejecuta `ruff check . --fix` antes de commitear
3. **Tests primero**: Asegúrate que los tests pasen antes de commit
4. **Review cambios**: Revisa lo que los hooks modificaron
5. **No saltar hooks**: `--no-verify` solo en emergencias

## 🔗 Referencias

- [Pre-commit Documentation](https://pre-commit.com/)
- [Ruff Pre-commit](https://github.com/astral-sh/ruff-pre-commit)
- [Pre-commit Hooks Repo](https://github.com/pre-commit/pre-commit-hooks)

---

**Última actualización:** 2026-05-27

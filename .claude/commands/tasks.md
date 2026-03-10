---
description: "PASO 4 — Descompone el plan en tareas y crea los issues en GitHub. Ejecutar cuando el equipo haya aprobado el plan."
---

## Ejecución

### 1. Verificar rama y PR

```bash
git branch --show-current
gh pr view --json number,state,url,body
```

- Si la rama es `main` o `master`: ERROR "No estás en una rama de feature. Ejecuta /status."
- Si no hay PR: ERROR "No hay PR abierto. ¿Ejecutaste /start?"

### 2. Gate: plan aprobado

Verificar en el body del PR:
- `- [x] Spec creado` ✓
- `- [x] Spec aprobado por el equipo de desarrollo` ✓
- `- [x] Plan generado` ✓
- `- [x] Plan aprobado por el equipo de desarrollo` ✓

Si la aprobación del plan no está marcada:

```
🚫 BLOQUEADO

El plan no ha sido aprobado todavía.

El equipo de desarrollo debe aprobar el plan
en el PR antes de generar las tareas.
```

**PARAR.**

### 3. Delegar en speckit.tasks

Invocar `/speckit.tasks`.

`speckit.tasks` se encarga de:
- Leer `spec.md`, `plan.md`, `data-model.md`, `contracts/`
- Generar `tasks.md` con tareas ordenadas por dependencias
- Organizar por fases y user stories
- Marcar paralelizables con `[P]`

**Esperar a que `speckit.tasks` termine completamente antes de continuar.**
Si produce ERROR: propagar y parar.

### 4. Delegar en speckit.taskstoissues

Invocar `/speckit.taskstoissues`.

`speckit.taskstoissues` se encarga de:
- Leer `tasks.md`
- Crear un issue en GitHub por cada tarea
- Enlazar los issues al PR

**Esperar a que `speckit.taskstoissues` termine completamente antes de continuar.**
Si produce ERROR: propagar y parar.

### 5. Commit de las tareas

```bash
git add specs/
git commit -m "docs: añadir tasks.md"
git push origin HEAD
```

### 6. Actualizar estado del PR

Marcar: `- [x] Tareas generadas`

Añadir fila:
```
| Tareas generadas | YYYY-MM-DD | tasks.md + issues creados |
```

```bash
gh pr edit --body "<body-actualizado>"
```

### 7. Informe final

```
✅ Tareas generadas

📋 tasks.md creado
🎫 Issues creados en GitHub

─────────────────────────────────────────
➡️  SIGUIENTE PASO
─────────────────────────────────────────
OPCIONAL: Si quieres validar la calidad
de los requirements antes de implementar:
  /checklist

Cuando estés listo para implementar:
  /implement
─────────────────────────────────────────
```

### Cierre de sesión

Leer el contexto actual de la sesión (igual que `/context`).

- **🟢 / 🟡**: No mostrar nada.
- **🟠**: Mostrar al final del informe:
  ```
  🟠 El contexto está alto. Abre una sesión nueva antes del siguiente comando.
  ```
- **🔴**: Mostrar antes del informe final e interrumpir si el usuario intenta continuar:
  ```
  🔴 Contexto crítico. Abre una sesión nueva AHORA antes de continuar.
  ```

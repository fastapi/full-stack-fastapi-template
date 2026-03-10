---
description: "PASO 3 — Genera el plan técnico. Ejecutar cuando el equipo haya aprobado el spec."
---

## Ejecución

### 1. Verificar rama y PR

```bash
git branch --show-current
gh pr view --json number,state,url,body
```

- Si la rama es `main` o `master`: ERROR "No estás en una rama de feature. Ejecuta /status."
- Si no hay PR: ERROR "No hay PR abierto. ¿Ejecutaste /start?"

### 2. Gate: spec aprobado

Verificar en el body del PR:
- `- [x] Spec creado` ✓
- `- [x] Spec aprobado por el equipo de desarrollo` ✓

Si la aprobación no está marcada:

```
🚫 BLOQUEADO

El spec no ha sido aprobado todavía.

El equipo de desarrollo debe aprobar el spec
en el PR antes de generar el plan.

Si ya comentaron pero no aprobaron:
  Ejecuta /consolidate-spec primero.
```

**PARAR.**

### 3. Delegar en speckit.plan

Invocar `/speckit.plan`.

`speckit.plan` se encarga de:
- Ejecutar los scripts de setup del plan
- Generar `research.md` resolviendo incógnitas técnicas
- Generar `data-model.md` con entidades y relaciones
- Generar `contracts/` con los contratos de interfaz
- Actualizar el contexto del agente

**Esperar a que `speckit.plan` termine completamente antes de continuar.**
Si produce ERROR: propagar y parar.

### 4. Verificar artefactos generados

```bash
ls specs/<directorio-rama>/
```

Confirmar que existen: `research.md`, `data-model.md`.
Si faltan: ERROR "speckit.plan no generó todos los artefactos. Revisa los errores anteriores."

### 5. Commit del plan

```bash
git add specs/
git commit -m "docs: añadir plan técnico"
git push origin HEAD
```

### 6. Actualizar estado del PR

Marcar: `- [x] Plan generado`

Añadir fila:
```
| Plan generado | YYYY-MM-DD | research.md + data-model.md |
```

```bash
gh pr edit --body "<body-actualizado>"
```

### 7. Informe final

```
✅ Plan técnico generado

📁 Artefactos:
   specs/<directorio>/research.md
   specs/<directorio>/data-model.md
   specs/<directorio>/contracts/  (si aplica)

─────────────────────────────────────────
➡️  SIGUIENTE PASO
─────────────────────────────────────────
Comparte el PR con el equipo para que
revisen el plan técnico.

Cuando el equipo apruebe el plan, ejecuta:
/tasks
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

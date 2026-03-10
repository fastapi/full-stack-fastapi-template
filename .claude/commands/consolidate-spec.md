---
description: "PASO 2 — Integra el feedback del equipo en el spec. Ejecutar después de que hayan comentado en el PR. Repetible."
---

## Ejecución

### 1. Verificar rama y PR

```bash
git branch --show-current
gh pr view --json number,state,url,body
```

- Si la rama es `main` o `master`: ERROR "No estás en una rama de feature. Ejecuta /status."
- Si no hay PR: ERROR "No hay PR abierto. ¿Ejecutaste /start?"

### 2. Gate: spec creado

Verificar en el body del PR: `- [x] Spec creado`

Si no está marcado: ERROR "El spec no existe todavía. Ejecuta /start primero."

### 3. Verificar que hay comentarios

```bash
gh pr view --json comments -q '.comments[].body'
```

Si no hay comentarios: ERROR "No hay comentarios en el PR todavía. Comparte el PR con el equipo y espera su feedback."

### 4. Delegar en speckit.clarify

Invocar `/speckit.clarify` con el contexto de los comentarios del PR.

`speckit.clarify` se encarga de:
- Leer el spec actual
- Procesar las clarificaciones necesarias
- Actualizar `spec.md` con las decisiones tomadas

**Esperar a que `speckit.clarify` termine completamente antes de continuar.**
Si produce ERROR: propagar y parar.

### 5. Commit del spec actualizado

```bash
git add specs/
git commit -m "docs: actualizar spec con feedback del equipo"
git push origin HEAD
```

### 6. Actualizar historial del PR

Añadir fila a la tabla:
```
| Spec revisado | YYYY-MM-DD | Feedback integrado vía speckit.clarify |
```

```bash
gh pr edit --body "<body-actualizado>"
```

### 7. Informe final

```
✅ Spec actualizado

─────────────────────────────────────────
➡️  SIGUIENTE PASO
─────────────────────────────────────────
Si hay más rondas de feedback:
  Vuelve a ejecutar /consolidate-spec

Si el spec está listo para aprobación:
  Pide al equipo que apruebe el spec en el PR.
  Cuando lo hagan, ejecuta: /plan
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

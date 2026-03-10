---
description: "PASO 6 — Guarda el código y lo deja para revisión del equipo. Repetible para iterar."
---

## Ejecución

### 1. Verificar rama y PR

```bash
git branch --show-current
gh pr view --json number,state,url,body,isDraft
```

- Si la rama es `main` o `master`: ERROR "No estás en una rama de feature. Ejecuta /status."
- Si no hay PR: ERROR "No hay PR abierto. ¿Ejecutaste /start?"

### 2. Gate: código generado

Verificar en el body del PR: `- [x] Código generado`

Si no está marcado: ERROR "El código no ha sido generado todavía. Ejecuta /implement primero."

### 3. Verificar que hay cambios para guardar

```bash
git status --porcelain
```

Si no hay cambios: ERROR "No hay cambios nuevos para guardar."

### 4. Mostrar resumen de cambios

```bash
git diff --stat HEAD
```

Mostrar al usuario qué ficheros se van a guardar.

### 5. Commit y push

```bash
git add -A
git commit -m "feat(<branch-name>): <resumen-breve-de-los-cambios>"
git push origin HEAD
```

### 6. Sacar el PR de draft (solo la primera vez)

Si el PR está en draft (`isDraft: true`):
```bash
gh pr ready
```

Si ya está en review: no hacer nada, el push es suficiente.

### 7. Actualizar estado del PR (solo la primera vez)

Si el PR estaba en draft, marcar: `- [x] En revisión de código`

Añadir fila:
```
| En revisión de código | YYYY-MM-DD | PR listo para revisión |
```

```bash
gh pr edit --body "<body-actualizado>"
```

### 8. Informe final

```
✅ Código guardado

🔗 PR: <PR_URL>

─────────────────────────────────────────
➡️  SIGUIENTE PASO
─────────────────────────────────────────
El equipo de desarrollo revisará el código.

Si necesitas hacer más cambios:
  Vuelve a ejecutar /submit

Cuando el dev apruebe el PR, ejecuta:
  /deploy-to-stage
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

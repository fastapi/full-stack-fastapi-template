---
description: "UTILIDAD — Muestra en qué punto del flujo estás ahora mismo."
---

## Ejecución

### 1. Recopilar estado

```bash
git branch --show-current
git status --porcelain
gh pr view --json number,title,state,isDraft,url,body,reviewDecision 2>/dev/null || echo "NO_PR"
```

### 2. Interpretar y mostrar

**Caso: en main sin feature activa**
```
📍 Estás en la rama principal, sin ninguna feature activa.

Para iniciar una feature:
  /start <descripción>
```

**Caso: en rama de feature con PR**

Leer checkboxes del PR y determinar el último paso completado.
Para cada paso, determinar su estado según esta lógica:
- ✅ si el checkbox está marcado
- ▶️  si es el siguiente ejecutable ahora mismo (pasos anteriores completos)
- ⏳ si está pendiente de una acción externa (aprobación del equipo)
- 🔒 si está bloqueado porque pasos anteriores no están completos

```
📍 Feature activa: <BRANCH_NAME>
🔗 PR: <PR_URL>

PROGRESO:
  ✅ Spec creado
  ✅ Spec aprobado
  ✅ Plan generado
  ⏳ Plan aprobado por el equipo      ← el equipo debe aprobar en GitHub
  🔒 Tareas generadas
  🔒 Código generado
  🔒 En revisión de código
  🔒 Publicado

➡️  SIGUIENTE
    Cuando el equipo apruebe el plan en GitHub, ejecuta:
    /tasks
```

### 3. Cambios sin guardar

Si `git status --porcelain` devuelve cambios:
```
⚠️  Hay cambios sin guardar en tu rama.
    Se guardarán en el próximo /submit.
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

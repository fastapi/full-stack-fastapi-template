# Guía técnica del kit de desarrollo

Documentación para el equipo de desarrollo sobre cómo está construido el kit, cómo instalarlo y cómo mantenerlo.

---

## Índice

1. [Arquitectura del kit](#1-arquitectura-del-kit)
2. [Instalación y configuración](#2-instalación-y-configuración)
3. [Qué hace cada comando por dentro](#3-qué-hace-cada-comando-por-dentro)
4. [Tu rol en el flujo: aprobar el spec, el plan y el código](#4-tu-rol-en-el-flujo-aprobar-el-spec-el-plan-y-el-código)
5. [Cómo añadir o modificar comandos](#5-cómo-añadir-o-modificar-comandos)

---

## 1. Arquitectura del kit

El kit está dividido en dos capas que conviven en `.claude/commands/`:

```
.claude/commands/
├── speckit.*          ← upstream (no tocar)
│   ├── speckit.specify.md
│   ├── speckit.plan.md
│   ├── speckit.tasks.md
│   ├── speckit.taskstoissues.md
│   ├── speckit.implement.md
│   ├── speckit.clarify.md
│   ├── speckit.checklist.md
│   ├── speckit.analyze.md
│   ├── speckit.retro.md
│   └── speckit.constitution.md
│
└── project commands   ← nuestro kit (orquestadores)
    ├── start.md
    ├── consolidate-spec.md
    ├── plan.md
    ├── tasks.md
    ├── checklist.md
    ├── implement.md
    ├── submit.md
    ├── deploy-to-stage.md
    ├── status.md
    └── context.md
```

**Principio de diseño:** los comandos del kit no tienen lógica propia sobre specs, planes o código. Delegan completamente en los `speckit.*` correspondientes. Su responsabilidad exclusiva es:

- Gestionar el PR (abrir, actualizar estado, historial)
- Verificar gates antes de ejecutar cada paso
- Proporcionar instrucciones claras sobre el siguiente paso

### Relación entre comandos

| Nuestro comando | Delega en | Responsabilidad propia |
|---|---|---|
| `/start` | `speckit.specify` | Abrir PR draft, push inicial |
| `/consolidate-spec` | `speckit.clarify` | Verificar gate, commit, actualizar PR |
| `/plan` | `speckit.plan` | Verificar gate, commit, actualizar PR |
| `/tasks` | `speckit.tasks` + `speckit.taskstoissues` | Verificar gate, commit, actualizar PR |
| `/checklist` | `speckit.checklist` | Commit (sin gate) |
| `/implement` | `speckit.implement` | Verificar gate, sync con main |
| `/submit` | — | Git add/commit/push, PR ready |
| `/deploy-to-stage` | — | Verificar aprobación, squash merge |
| `/status` | — | Leer estado del PR y orientar |
| `/context` | — | Mostrar uso de contexto de sesión |

### Estado del PR como fuente de verdad

El estado del flujo vive en el body del PR, no en ficheros locales. Los checkboxes son el mecanismo de gate:

```markdown
## Estado
- [x] Spec creado
- [x] Spec aprobado por el equipo de desarrollo
- [x] Plan generado
- [ ] Plan aprobado por el equipo de desarrollo   ← bloquea /tasks
- [ ] Tareas generadas                             ← bloquea /implement
- [ ] Código generado                              ← bloquea /submit
- [ ] En revisión de código                        ← bloquea /deploy-to-stage
- [ ] Publicado
```

Los comandos leen este body con `gh pr view --json body` para determinar si pueden ejecutarse.

### Permisos en settings.json

El `.claude/settings.json` del repo controla qué comandos bash puede ejecutar Claude. Los comandos del kit necesitan:

```json
{
  "permissions": {
    "allow": [
      "Bash(git push *)",
      "Bash(git push origin HEAD)",
      "Bash(git rebase *)",
      "Bash(git merge *)",
      "Bash(gh pr *)",
      "Bash(gh run *)",
      "Bash(jq *)",
      "Bash(mkdir *)",
      "Bash(cp *)",
      "Bash(chmod *)"
    ]
  }
}
```

Fusionar con los permisos existentes — no reemplazar.

---

## 2. Instalación y configuración

### Prerequisitos

- Claude Code Desktop instalado
- `gh` CLI autenticado (`gh auth login`)
- `jq` instalado (`brew install jq` en Mac)
- Acceso al repo con permisos de push

### Pasos de instalación

**1. Copiar los comandos del kit al repo:**

```bash
cp path/to/kit/commands/*.md .claude/commands/
```

**2. Actualizar `.claude/settings.json`** fusionando los permisos del kit con los existentes (ver sección anterior).

**3. Verificar que speckit está instalado:**

```bash
ls .claude/commands/speckit.*.md
```

Si no están, seguir las instrucciones de instalación de [full-stack-agentic](https://github.com/alexfdz/full-stack-agentic).

**4. Verificar `gh` CLI:**

```bash
gh auth status
gh pr list  # debe funcionar sin errores
```

**5. Comprobar que la rama `main` existe y tiene acceso:**

```bash
git fetch origin main
```

### Verificación post-instalación

Ejecutar en Claude Code:

```
/status
```

Debe responder con algo como:
```
📍 Estás en la rama principal, sin ninguna feature activa.
Para iniciar una feature: /start <descripción>
```

---

## 3. Qué hace cada comando por dentro

### `/start <descripción>`

1. Verifica que estás en `main` y no hay cambios sin commitear
2. Invoca `speckit.specify` con la descripción — este crea la rama `NNN-short-name`, escribe `specs/NNN-short-name/spec.md` y el checklist de calidad
3. Hace push de la nueva rama a origin
4. Abre un PR draft con el template de estados y la tabla de historial
5. Informa al usuario del PR URL y del siguiente paso

**Qué puede fallar:** si `speckit.specify` falla (descripción vacía, error de scripts bash), el error se propaga y no se abre PR. La rama puede quedar creada localmente — el usuario debe hacer `git checkout main && git branch -d NNN-short-name` manualmente.

---

### `/consolidate-spec`

1. Verifica que hay PR abierto y que el checkbox `Spec creado` está marcado
2. Verifica que hay comentarios en el PR
3. Invoca `speckit.clarify` con el contexto de los comentarios
4. Hace commit y push de `spec.md` actualizado
5. Añade fila al historial del PR

**Repetible:** puede ejecutarse tantas veces como haya rondas de feedback.

---

### `/plan`

1. Verifica gate: `Spec aprobado` marcado en el PR
2. Invoca `speckit.plan` — genera `research.md`, `data-model.md`, `contracts/`
3. Verifica que los artefactos existen
4. Commit y push
5. Marca `Plan generado` en el PR

**Gate duro:** si el spec no está aprobado, para completamente con mensaje explicativo.

---

### `/tasks`

1. Verifica gate: `Plan aprobado` marcado en el PR
2. Invoca `speckit.tasks` — genera `tasks.md` con fases y dependencias
3. Invoca `speckit.taskstoissues` — crea Issues en GitHub por tarea
4. Commit y push
5. Marca `Tareas generadas` en el PR

---

### `/checklist` (opcional)

1. Verifica que hay un spec en la rama actual (sin gate de aprobaciones)
2. Invoca `speckit.checklist` — hace preguntas sobre el enfoque, genera `checklists/<dominio>.md`
3. Commit y push

No bloquea ningún paso siguiente. El usuario puede ejecutarlo en cualquier momento.

---

### `/implement`

1. Verifica gate: `Tareas generadas` marcado en el PR
2. Verifica que no hay cambios sin commitear
3. Hace `git fetch origin && git rebase origin/main` antes de implementar
4. Invoca `speckit.implement` — lee spec, plan, data-model, contracts y tasks para generar el código
5. Marca `Código generado` en el PR

**Importante:** el rebase previo es crítico para evitar conflictos. Si hay conflictos de rebase, para con error explícito — el dev debe resolverlos.

---

### `/submit`

1. Verifica gate: `Código generado` marcado en el PR
2. Verifica que hay cambios sin commitear
3. Muestra `git diff --stat HEAD`
4. Hace `git add -A && git commit && git push`
5. Si el PR está en draft: `gh pr ready`
6. Actualiza estado del PR a `En revisión de código` (solo la primera vez)

**Repetible:** si el equipo pide cambios y el agente los hace, `/submit` vuelve a hacer push sin cambiar el estado del PR (ya no está en draft).

---

### `/deploy-to-stage`

1. Verifica gate: `En revisión de código` marcado en el PR
2. Verifica `reviewDecision == APPROVED` vía `gh pr view --json reviewDecision`
3. Ejecuta `gh pr merge --squash --delete-branch`
4. Lista `gh run list --limit 3` para confirmar que GitHub Actions arrancó

Cualquier miembro del equipo puede ejecutarlo. El gate es la aprobación del PR — sin ella el comando se bloquea.

---

### `/status`

Lee `git branch --show-current`, `git status --porcelain` y `gh pr view --json body,reviewDecision` para construir un informe legible del progreso. No ejecuta ninguna acción.

---

### `/context`

Lee el fichero de sesión activa de Claude Code para obtener `remaining_percentage`. Muestra una barra visual con semáforo de colores y el siguiente paso pendiente. No ejecuta ninguna acción.

---

## 4. Tu rol en el flujo: aprobar el spec, el plan y el código

Como dev, tu responsabilidad en el flujo es revisar y aprobar en GitHub los tres puntos de decisión técnica:

### Aprobar el spec

Cuando la PM ejecuta `/start`, el PR draft se abre con `spec.md`. Tú debes:

1. Abrir el PR en GitHub
2. Ir a la pestaña **Files changed**
3. Revisar `spec.md` — requisitos, casos de uso, criterios de aceptación
4. Dejar comentarios inline si hay algo que cambiar (la PM ejecutará `/consolidate-spec` para integrarlos)
5. Cuando esté bien: **Review changes → Approve**

Tras tu aprobación, la PM puede ejecutar `/plan`.

### Aprobar el plan

Cuando la PM ejecuta `/plan`, el PR se actualiza con `research.md`, `data-model.md` y `contracts/`. Tú debes:

1. Revisar los artefactos técnicos en **Files changed**
2. Dejar comentarios si hay decisiones técnicas que cambiar
3. Cuando esté bien: **Review changes → Approve**

Tras tu aprobación, la PM puede ejecutar `/tasks`.

### Revisar el código y aprobarlo

Cuando la PM ejecuta `/submit`, el PR sale de draft. Tú debes:

1. Revisar el código en **Files changed**
2. Pedir cambios si los hay — la PM o el agente los harán y volverán a ejecutar `/submit`
3. Cuando el código esté listo: **Review changes → Approve**

Tras tu aprobación, cualquiera puede ejecutar `/deploy-to-stage` para publicar a main.

> **Nota sobre los checkboxes:** los gates del flujo dependen de los checkboxes en el body del PR. Cuando apruebas el PR con "Approve", los comandos lo detectan automáticamente vía `reviewDecision`. Para los checkboxes de spec y plan aprobados, edita el body del PR manualmente cambiando `- [ ]` por `- [x]` en la línea correspondiente.

---

## 5. Cómo añadir o modificar comandos

### Estructura de un comando

Cada fichero `.md` en `.claude/commands/` sigue este patrón:

```markdown
---
description: "Descripción breve que Claude Code muestra en el autocompletado"
---

## Propósito
Qué hace el comando y para qué sirve.

## Ejecución

### 1. Verificaciones previas
...

### 2. Gate (si aplica)
Condición que debe cumplirse. Si no se cumple: ERROR o bloqueo con mensaje.

### 3. Lógica principal
Invocación a speckit o comandos bash.

### 4. Actualizar estado del PR
Marcar checkboxes, añadir fila al historial.

### 5. Informe final
Qué mostrar al usuario y cuál es el siguiente paso.

### Cierre de sesión
Bloque estándar de semáforo de contexto.
```

### Añadir un nuevo comando

1. Crear `.claude/commands/mi-comando.md` siguiendo la estructura anterior
2. Si el comando necesita permisos bash nuevos, añadirlos a `.claude/settings.json`
3. Si el comando forma parte del flujo lineal, actualizar el `## Estado` del template del PR en `start.md` para añadir el nuevo checkbox
4. Actualizar `status.md` para que el nuevo paso aparezca en el informe de progreso

### Modificar un comando existente

- Los comandos de speckit (`speckit.*`) **no se modifican** — son upstream
- Los comandos del kit se pueden editar libremente
- Si cambias los gates de un comando, asegúrate de que `status.md` refleja el nuevo estado
- Si cambias el template del PR en `start.md`, los PRs existentes no se actualizan automáticamente

### Convenciones

- Los mensajes de error empiezan con `🚫 BLOQUEADO` o `ERROR:`
- Los informes finales empiezan con `✅`
- El siguiente paso siempre se muestra en un bloque delimitado con `─────`
- Los comandos bash críticos (merge, push) se validan antes de ejecutar
- Los gates leen el body del PR con `gh pr view --json body` — no usan ficheros locales como fuente de verdad

---

*Para dudas sobre speckit (specify, plan, tasks, implement, etc.) consulta la documentación upstream en `.specify/` y los propios ficheros de comando en `.claude/commands/speckit.*.md`.*

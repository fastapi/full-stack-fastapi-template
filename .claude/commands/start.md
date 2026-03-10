---
description: "PASO 1 — Inicia una nueva feature. Crea el PR draft y arranca el proceso de especificación."
---

## User Input

```text
$ARGUMENTS
```

Descripción de la feature en lenguaje natural. **Obligatoria.**
Si está vacía: ERROR "Describe la feature. Ejemplo: /start quiero que los usuarios puedan restablecer su contraseña"

---

## Ejecución

### 1. Verificar punto de partida limpio

```bash
git status --porcelain
git branch --show-current
```

- Si hay cambios sin commitear: ERROR "Hay cambios sin guardar. Guárdalos o descártalos antes de iniciar una feature nueva."
- Si la rama actual no es `main` o `master`: ERROR "Debes estar en la rama principal. Ejecuta /status para ver dónde estás."

### 2. Delegar en speckit.specify

Invocar `/speckit.specify` pasando `$ARGUMENTS` como descripción de la feature.

`speckit.specify` se encarga de:
- Generar el nombre corto y número de rama (`NNN-short-name`)
- Crear y hacer checkout de la rama
- Escribir `specs/NNN-short-name/spec.md`
- Generar el checklist de calidad
- Hacer preguntas de clarificación si las hay

**Esperar a que `speckit.specify` termine completamente antes de continuar.**
Si produce ERROR: propagar y parar.

### 3. Leer rama y spec creados

```bash
git branch --show-current
```

```bash
ls specs/ | sort | tail -1
```

`BRANCH_NAME` = rama activa
`SPEC_PATH` = `specs/<último-directorio>/spec.md`

### 4. Push de la rama

```bash
git push -u origin HEAD
```

### 5. Abrir PR draft

```bash
gh pr create \
  --title "$BRANCH_NAME" \
  --draft \
  --base main \
  --body "$(cat <<EOF
## Feature
Spec: $SPEC_PATH

## Estado
- [x] Spec creado
- [ ] Spec aprobado por el equipo de desarrollo
- [ ] Plan generado
- [ ] Plan aprobado por el equipo de desarrollo
- [ ] Tareas generadas
- [ ] Código generado
- [ ] En revisión de código
- [ ] Publicado

## Historial

| Estado | Fecha | Nota |
|--------|-------|------|
| Spec creado | $(date +%Y-%m-%d) | Feature iniciada |

## Notas
EOF
)"
```

### 6. Informe final

```
✅ Feature iniciada

📋 Spec:  <SPEC_PATH>
🌿 Rama:  <BRANCH_NAME>
🔗 PR:    <PR_URL>

─────────────────────────────────────────
➡️  SIGUIENTE PASO
─────────────────────────────────────────
Comparte el PR con el equipo de desarrollo
para que revisen el spec.

Cuando hayan comentado, ejecuta:
/consolidate-spec
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

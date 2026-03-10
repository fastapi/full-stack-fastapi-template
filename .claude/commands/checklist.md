---
description: "OPCIONAL — Valida la calidad de los requirements antes de implementar. Puede ejecutarse en cualquier momento."
---

## Propósito

Genera un checklist que valida que el spec, el plan y las tareas están bien escritos, son completos y no tienen ambigüedades. No bloquea el flujo — es una herramienta de calidad opcional.

Recuerda: el checklist valida los **requirements**, no el código. Es un "test unitario del spec escrito en inglés".

---

## Ejecución

### 1. Verificar rama y PR

```bash
git branch --show-current
gh pr view --json number,state,url,body
```

- Si la rama es `main` o `master`: ERROR "No estás en una rama de feature. Ejecuta /status."
- Si no hay PR: ERROR "No hay PR abierto. ¿Ejecutaste /start?"

### 2. Verificar que hay algo que revisar

Confirmar que existe al menos `spec.md` en el directorio de la feature.

```bash
ls specs/<directorio-rama>/
```

Si no hay spec: ERROR "No hay spec para revisar. Ejecuta /start primero."

### 3. Delegar en speckit.checklist

Invocar `/speckit.checklist` con el contexto de la fase actual.

`speckit.checklist` se encarga de:
- Detectar qué artefactos están disponibles (spec, plan, tasks)
- Hacer preguntas de clarificación sobre el enfoque del checklist
- Generar el fichero en `specs/<directorio>/checklists/<dominio>.md`
- Validar completeness, clarity, consistency, measurability, coverage

**Esperar a que `speckit.checklist` termine completamente antes de continuar.**

### 4. Commit del checklist

```bash
git add specs/
git commit -m "docs: añadir checklist de requirements"
git push origin HEAD
```

### 5. Informe final

```
✅ Checklist generado

📋 <ruta-al-checklist>

Revisa los items marcados como [Gap], [Ambiguity]
o [Conflict] antes de continuar con /implement.

─────────────────────────────────────────
➡️  SIGUIENTE PASO
─────────────────────────────────────────
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

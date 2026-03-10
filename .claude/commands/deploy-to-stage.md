---
description: "PASO 7 — Publica a main con squash merge. Requiere que el PR esté aprobado."
---

## Propósito

Fusiona la feature a `main` con squash merge — todos los commits de iteración se aplanan en uno solo. GitHub Actions despliega automáticamente al detectar el merge.

---

## Ejecución

### 1. Verificar rama y PR

```bash
git branch --show-current
gh pr view --json number,state,url,body,reviewDecision
```

- Si la rama es `main`: ERROR "Ya estás en main."
- Si no hay PR: ERROR "No hay PR abierto para esta rama."

### 2. Gate: código entregado

Verificar en el body del PR: `- [x] En revisión de código`

Si no está marcado: ERROR "El código no ha sido entregado. Ejecuta /submit primero."

### 3. Gate: PR aprobado

Comprobar `reviewDecision`.

Si NO es `APPROVED`:

```
🚫 BLOQUEADO

El PR no tiene aprobación todavía.

El equipo debe revisar y aprobar el PR en GitHub
antes de poder publicar a main.

🔗 PR: <PR_URL>
```

**PARAR.**

### 4. Squash merge a main

```bash
gh pr merge --squash --delete-branch
```

Si falla por conflictos:

```
🚫 ERROR: Hay conflictos al fusionar con main.

No se ha realizado ningún cambio.
Resuelve los conflictos manualmente antes de continuar.
```

**PARAR.**

### 5. Verificar que GitHub Actions se ha disparado

```bash
gh run list --limit 3
```

Mostrar los workflows activos para confirmar que el deploy arrancó.

### 6. Informe final

```
✅ Publicado en main

🌿 Fusionado: <BRANCH> → main (squash)
🗑️  Rama eliminada
🚀 Deploy en curso — GitHub Actions desplegando

─────────────────────────────────────────
Esta feature está completa.
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

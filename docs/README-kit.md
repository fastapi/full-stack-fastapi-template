# Spec-Driven Kit — Estructura del repositorio

Este kit está diseñado para que PMs y diseñadoras puedan contribuir código con Claude Code sin necesitar conocimientos de git.

## Ficheros de este kit

```
.specify/
├── memory/
│   └── constitution.md          ← Principios del proyecto (ya generado)
├── commands/
│   ├── new-feature.md         ← /project.new-feature
│   ├── deliver.md              ← /project.deliver
│   ├── status.md                ← /project.status
│   ├── sync.md           ← /project.sync
│   ├── deploy-to-stage.md      ← /deploy-to-stage
│   ├── explore.md              ← /project.explore
│   ├── discard.md             ← /project.discard
│   └── consolidate-spec.md       ← /project.consolidate-spec
├── scripts/
│   └── pr-template.md           ← Template de PR
└── specs/                       ← Se crea automáticamente con /project.new-feature

docs/
└── onboarding.md                ← Guía para PMs y diseñadoras
```

## Setup inicial (solo el equipo de desarrollo)

1. Inicializa spec-kit:
   ```
   specify init . --ai claude
   ```

2. Copia los ficheros de commands a `.specify/commands/`

3. Copia `constitution.md` a `.specify/memory/constitution.md`

4. Copia `onboarding.md` a `docs/onboarding.md`

5. Crea las ramas base:
   ```
   git checkout -b staging && git push origin staging
   git checkout main
   ```

6. Rellena la sección 10 del `constitution.md` con las decisiones técnicas del proyecto.

### Instalar la barra de estado (una vez por máquina, cada persona del equipo)

Requiere `jq` instalado (`brew install jq` en macOS).

```bash
# Copiar el script
mkdir -p ~/.claude
cp statusline.sh ~/.claude/statusline.sh
chmod +x ~/.claude/statusline.sh

# Activar en Claude Code
cp settings.json ~/.claude/settings.json
```

Si ya tienes un `~/.claude/settings.json`, añade solo la entrada `statusLine` manualmente:
```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh"
  }
}
```

Reinicia Claude Code. Verás la barra en la parte inferior del terminal:
```
 [Claude Sonnet 4.6]  📁 mi-proyecto  🌿 feat/001-login
 ████████░░░░░░░░░░░░ 38% │ $0.12 │ ⏱ 8m 22s
```

**Colores del contexto:**
- Verde `< 50%` → puedes continuar
- Amarillo `50–79%` → termina el paso y abre sesión nueva
- Naranja `80–89%` → abre sesión nueva al terminar lo que estás haciendo
- Rojo `≥ 90%` → abre sesión nueva ahora

## Onboarding de PMs y diseñadoras

Comparte `docs/onboarding.md` con ellas y haz una sesión de 30 minutos donde ejecuten `/project.new-feature` juntas por primera vez.

Los únicos comandos que necesitan recordar son:
- `/project.new-feature` — empezar algo nuevo
- `/project.deliver` — compartir su trabajo
- `/project.status` — saber dónde están
- `/project.sync` — ponerse al día

El resto aparece de forma natural en el flujo.

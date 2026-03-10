---
description: "UTILIDAD — Muestra cuánta memoria le queda a Claude en esta sesión."
---

## Ejecución

### 1. Leer contexto real de la sesión

```bash
ls -t ~/.claude/sessions/ 2>/dev/null | head -1
```

Leer `remaining_percentage` o calcular desde `used_tokens` / `total_tokens`.
Si no se puede leer: usar estimación conservadora basada en la longitud de la conversación.

### 2. Determinar nivel

| % usado | Nivel | Emoji |
|---------|-------|-------|
| < 50%   | Puedes continuar | 🟢 |
| 50–79%  | Termina el paso actual | 🟡 |
| 80–89%  | Abre sesión nueva pronto | 🟠 |
| ≥ 90%   | Abre sesión nueva YA | 🔴 |

### 3. Mostrar informe

Mostrar SOLO el nivel actual, la barra y la recomendación correspondiente. Ejemplo para 🟠:

```
[████████████████░░░░]  83% usado

🟠  Abre sesión nueva pronto
```

La recomendación es obligatoria y se muestra siempre debajo de la barra.

### 4. Mostrar siguiente paso

Mostrar el siguiente paso pendiente del flujo (igual que `/status`) para que al abrir sesión nueva el usuario sepa qué ejecutar.

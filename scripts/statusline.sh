#!/usr/bin/env bash
# statusline.sh — Barra de estado para Claude Code
# Muestra el modelo, carpeta, rama git, uso del contexto, coste y tiempo de sesión
# Requiere: jq
#
# Instalación:
#   cp statusline.sh ~/.claude/statusline.sh
#   chmod +x ~/.claude/statusline.sh
# Luego activa en ~/.claude/settings.json (ver settings.json del kit)

# ── Colores ANSI ────────────────────────────────────────────────
RESET="\033[0m"
BOLD="\033[1m"

BG_DARK="\033[48;5;235m"
BG_GREEN="\033[48;5;22m"
BG_YELLOW="\033[48;5;130m"
BG_ORANGE="\033[48;5;166m"
BG_RED="\033[48;5;88m"

FG_WHITE="\033[97m"
FG_GRAY="\033[38;5;245m"
FG_GREEN="\033[38;5;82m"
FG_YELLOW="\033[38;5;220m"
FG_ORANGE="\033[38;5;208m"
FG_RED="\033[38;5;196m"

# ── Leer JSON de stdin ──────────────────────────────────────────
stdin_data=$(cat)

# ── Extraer valores con jq ──────────────────────────────────────
IFS=$'\t' read -r current_dir model_name cost duration_ms ctx_used git_branch < <(
  echo "$stdin_data" | jq -r '[
    .workspace.current_dir // "unknown",
    .model.display_name // "Claude",
    (try (.cost.total_cost_usd // 0 | . * 100 | floor / 100) catch 0),
    (.cost.total_duration_ms // 0),
    (try (
      if .context_window.remaining_percentage != null then
        (100 - .context_window.remaining_percentage | floor)
      else
        ((.context_window.used_tokens // 0) /
         ((.context_window.total_tokens // 200000) | if . == 0 then 200000 else . end) * 100 | floor)
      end
    ) catch 0),
    .workspace.git_branch // ""
  ] | @tsv'
)

# ── Carpeta actual (solo el nombre, no la ruta completa) ────────
folder=$(basename "$current_dir")

# ── Duración en formato legible ─────────────────────────────────
duration_s=$(( ${duration_ms%.*} / 1000 ))
if [ "$duration_s" -ge 3600 ]; then
  duration_fmt=$(printf "%dh %02dm" $((duration_s/3600)) $(( (duration_s%3600)/60 )))
elif [ "$duration_s" -ge 60 ]; then
  duration_fmt=$(printf "%dm %02ds" $((duration_s/60)) $((duration_s%60)))
else
  duration_fmt="${duration_s}s"
fi

# ── Coste formateado ────────────────────────────────────────────
if [ -z "$cost" ] || [ "$cost" = "0" ] || [ "$cost" = "null" ]; then
  cost_fmt="$0.00"
else
  cost_fmt=$(printf '$%.2f' "$cost")
fi

# ── Barra de progreso del contexto ─────────────────────────────
ctx_used=${ctx_used:-0}
bar_total=20
bar_filled=$(( ctx_used * bar_total / 100 ))
[ "$bar_filled" -gt "$bar_total" ] && bar_filled=$bar_total
bar_empty=$(( bar_total - bar_filled ))

bar_str=""
for ((i=0; i<bar_filled; i++)); do bar_str+="█"; done
for ((i=0; i<bar_empty; i++)); do bar_str+="░"; done

# ── Color del contexto según umbral ────────────────────────────
# Verde  < 50%  → sesión fresca
# Amarillo 50-79% → contexto moderado, avisa al terminar el paso
# Naranja 80-89% → contexto alto, avisa antes de continuar
# Rojo   >= 90% → contexto crítico, pide sesión nueva ahora
if [ "$ctx_used" -lt 50 ]; then
  ctx_color="$FG_GREEN"
  ctx_bg="$BG_GREEN"
  ctx_label="🟢"
  ctx_msg=""
elif [ "$ctx_used" -lt 80 ]; then
  ctx_color="$FG_YELLOW"
  ctx_bg="$BG_YELLOW"
  ctx_label="🟡"
  ctx_msg=""
elif [ "$ctx_used" -lt 90 ]; then
  ctx_color="$FG_ORANGE"
  ctx_bg="$BG_ORANGE"
  ctx_label="🟠"
  ctx_msg=" ← abre sesión nueva al terminar este paso"
else
  ctx_color="$FG_RED"
  ctx_bg="$BG_RED"
  ctx_label="🔴"
  ctx_msg=" ← ABRE SESIÓN NUEVA AHORA"
fi

# ── Rama git ────────────────────────────────────────────────────
if [ -n "$git_branch" ] && [ "$git_branch" != "null" ]; then
  branch_str=" 🌿 ${git_branch}"
else
  # Intentar leer la rama directamente si jq no la devolvió
  if command -v git &>/dev/null; then
    git_branch=$(git -C "$current_dir" rev-parse --abbrev-ref HEAD 2>/dev/null)
    [ -n "$git_branch" ] && branch_str=" 🌿 ${git_branch}" || branch_str=""
  else
    branch_str=""
  fi
fi

# ── Línea 1: modelo, carpeta, rama ─────────────────────────────
line1="${BG_DARK}${FG_WHITE}${BOLD} ${model_name} ${RESET}"
line1+="${BG_DARK}${FG_GRAY} 📁 ${folder}${branch_str} ${RESET}"

# ── Línea 2: barra de contexto, coste, tiempo ──────────────────
line2="${BG_DARK}${ctx_color}${BOLD} ${bar_str} ${ctx_used}%${RESET}"
line2+="${BG_DARK}${FG_GRAY} │ ${cost_fmt} │ ⏱ ${duration_fmt}${RESET}"
if [ -n "$ctx_msg" ]; then
  line2+="${ctx_color}${BOLD}${ctx_msg}${RESET}"
fi

# ── Output ──────────────────────────────────────────────────────
printf "%b\n%b\n" "$line1" "$line2"

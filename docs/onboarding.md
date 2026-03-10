# Guía de trabajo — Cómo funciona todo esto

Bienvenida al equipo. Esta guía explica cómo trabajamos, dónde vive el trabajo que creas, y cómo colaboramos sin pisarnos.

No necesitas saber nada de programación ni de git para seguir esta guía.

---

## Las cuatro cajas

Todo el trabajo existe en uno de estos cuatro sitios. En cualquier momento puedes saber exactamente dónde está lo que estás haciendo.

```
🖥️  TU ORDENADOR        🔄  SALA DE REVISIÓN       🧪  PRUEBAS INTERNAS      🌍  EL MUNDO REAL
    (local)                  (GitHub PR)                 (staging)                 (producción)

  Tu trabajo             Lo que has                 Lo que probáis            Lo que usan
  en progreso            compartido para            juntas antes              los usuarios
                         que el equipo revise       de publicar

  Solo tú lo ves         El equipo y tú lo veis     Todo el equipo lo ve      Todo el mundo lo ve
```

### ¿Dónde está mi trabajo ahora mismo?

- Acabas de empezar algo → **Tu ordenador**
- Has ejecutado `/submit` → **Sala de revisión**
- El equipo ha aprobado y has ejecutado `/deploy-to-stage` → **Pruebas internas**
- El equipo ha publicado → **El mundo real**

---

## Los comandos

Estos son los únicos comandos que necesitas. Escríbelos en Claude Code exactamente como aparecen aquí.

### `/start`
**Cuándo usarlo:** Cuando quieres empezar a trabajar en algo nuevo.

Escribe `/start` seguido de una descripción de lo que quieres construir. Claude se encarga de todo lo demás: crea tu espacio de trabajo, abre la sala de revisión y prepara el spec.

---

### `/consolidate-spec`
**Cuándo usarlo:** Cuando el equipo ha dejado comentarios en la sala de revisión y quieres integrarlos en el spec.

Claude lee todos los comentarios y los incorpora al spec. Puedes ejecutarlo tantas veces como haya rondas de feedback.

---

### `/plan`
**Cuándo usarlo:** Cuando el equipo ha aprobado el spec.

Claude genera el plan técnico. Requiere que el spec esté aprobado — si no lo está, te avisará.

---

### `/tasks`
**Cuándo usarlo:** Cuando el equipo ha aprobado el plan técnico.

Claude descompone el plan en tareas concretas y las convierte en issues en GitHub.

---

### `/checklist`
**Cuándo usarlo:** (Opcional) Cuando quieres validar que el spec está bien escrito antes de implementar.

---

### `/implement`
**Cuándo usarlo:** Cuando las tareas están generadas y quieres que Claude escriba el código.

---

### `/submit`
**Cuándo usarlo:** Cuando quieres que el equipo vea el código que Claude ha generado.

Manda todo a la sala de revisión y avisa al equipo. Puedes ejecutarlo tantas veces como quieras — cada vez, el equipo ve los cambios más recientes.

---

### `/deploy-to-stage`
**Cuándo usarlo:** Cuando el equipo ha aprobado el código y quieres mandarlo a pruebas internas.

El equipo podrá ver y probar tu feature en el entorno de pruebas antes de publicarla para los usuarios reales. Requiere que el PR esté aprobado — si no lo está, te avisará.

---

### `/status`
**Cuándo usarlo:** Cuando no sabes muy bien dónde estás o qué tienes pendiente.

Te dice, en lenguaje normal, en qué punto del flujo estás y cuál es el siguiente paso.

---

### `/context`
**Cuándo usarlo:** Cuando quieres saber cuánta memoria le queda a Claude en esta sesión.

---

## Cómo colaboramos varias personas en el mismo spec

### El modelo de rondas

El spec no se escribe entre todas a la vez. Avanza en rondas:

```
Ronda 1 ── Quien abre la feature escribe el draft inicial del spec con /start
               ↓
Ronda 2 ── Las demás leen y dejan comentarios en la sala de revisión
           (nunca editáis el fichero directamente)
               ↓
Ronda 3 ── /consolidate-spec fusiona todos los comentarios
               ↓
Ronda 4 ── Revisión final antes de pasar al plan técnico
```

### En la práctica

- **Escribes el spec** → ejecutas `/submit` → avisas al equipo por Slack
- **Recibes el aviso** → vas a la sala de revisión en GitHub → dejas tus comentarios
- **Cuando todas han comentado** → quien abrió la feature ejecuta `/consolidate-spec`
- **Revisión final** → el equipo aprueba en GitHub antes de continuar

---

## El ciclo de vida completo de una feature

```
/start "descripción"
        ↓
   Rondas de spec (comentarios + /consolidate-spec)
        ↓
   El equipo aprueba el spec  ← checkpoint obligatorio
        ↓
/plan → plan técnico generado
        ↓
   El equipo aprueba el plan  ← checkpoint obligatorio
        ↓
/tasks → tareas e issues generados
        ↓
/implement → código generado
        ↓
/submit → sala de revisión sale de DRAFT
        ↓
   El equipo hace code review y aprueba  ← checkpoint obligatorio
        ↓
/deploy-to-stage → feature en pruebas internas → 🌍 publicado
```

---

## Estado de la sala de revisión

Cada sala de revisión tiene un checklist que indica en qué fase está:

```
- [x] Spec creado
- [x] Spec aprobado por el equipo de desarrollo
- [x] Plan generado
- [ ] Plan aprobado por el equipo de desarrollo     ← esperando aquí
- [ ] Tareas generadas
- [ ] Código generado
- [ ] En revisión de código
- [ ] Publicado
```

Si no sabes en qué punto estás, mira el checklist de tu sala de revisión o ejecuta `/status`.

---

## Preguntas frecuentes

**¿Puedo perder trabajo?**
No. Todo lo que entregas queda guardado para siempre con fecha y hora. Incluso si algo sale mal, se puede recuperar.

**¿Qué hago si Claude me dice que hay un "conflicto"?**
Contacta al equipo de desarrollo. Es la única situación donde necesitas su ayuda técnica directa.

**¿Puedo trabajar en dos features a la vez?**
Sí, pero es mejor terminar una antes de empezar otra. Si necesitas hacerlo, avisa al equipo de desarrollo primero.

**¿Cómo sé si el equipo ha revisado lo que entregué?**
`/status` te lo dirá. También puedes mirar tu sala de revisión en GitHub — los comentarios del equipo aparecen ahí.

**¿Qué es GitHub?**
Es el sitio donde vive la sala de revisión. No necesitas entrar ahí directamente — Claude lo gestiona por ti — pero si quieres ver el estado de tu feature, puedes buscarlo en github.com/[nombre-del-proyecto].

---

*¿Algo no está claro? Pregunta al equipo de desarrollo antes de seguir. Es mejor preguntar que suponer.*

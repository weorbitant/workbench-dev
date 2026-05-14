# KS: ops-suite

## Estructura (60 min)

| Bloque | Contenido | Tiempo |
|--------|-----------|--------|
| 1 | El problema | 5 min |
| 2 | El plugin — qué es, configuración, dos tipos de skill | 15 min |
| 3 | Demo: estado del sistema | 18 min |
| 4 | Demo: mensajes | 12 min |
| 5 | Cierre + Q&A | 10 min |

---

## Slide: El problema

**Título:** Antes de ops-suite

**Contenido:**

Cuando algo fallaba en producción o quería tener el cuadro completo del sistema, el proceso era siempre el mismo:

1. Port-forward manual a la base de datos
2. Ir pod a pod revisando logs
3. Abrir el dashboard de RabbitMQ por separado
4. Comparar mentalmente qué había en dev vs prod
5. Buscar qué migraciones estaban aplicadas

**Resultado:** 4-5 herramientas, varios terminales, 20-30 min de trabajo manual antes de empezar a resolver nada.

**Lo que quería:** una sola conversación que me diera el cuadro completo.

---

## Slide: Dos tipos de skill — la decisión de diseño clave

**Título:** Cómo funcionan las skills por dentro

**El descubrimiento:** no todas las skills se ejecutan igual.

| | Read-only | Destructiva |
|--|-----------|-------------|
| Ejemplos | service-logs, deploy-status, queue-status | db-migrate, queue-reprocess, deploy |
| Cómo corre | Subagente nuevo — contexto limpio | Conversación actual — tiene el historial |
| Auto-invocable | Sí, Claude las lanza solo cuando tiene sentido | No, requiere `/ops-suite:xxx` explícito |
| `disable-model-invocation` | ausente | `true` |
| Confirmación | No necesaria | Siempre pide confirmación |

**El punto no obvio:**

Cuando una skill read-only se invoca, abre en un **contexto nuevo**. No sabe nada de lo que se ha dicho antes en la conversación. Si le dices "estamos en dev", la siguiente skill no lo recuerda.

Por eso existe `/tmp/ops-suite-session/`: es el mecanismo para pasar estado entre skills aisladas. La skill que resuelve el entorno lo escribe ahí; las que vienen después lo leen sin volver a preguntar.

```
Conversación principal
  │
  ├── "¿hay errores en dev?"
  │     └── service-logs (subagente nuevo)
  │           Lee /tmp/ops-suite-session/config.json  ← estado compartido
  │           Escribe env seleccionado
  │
  ├── (service-logs auto-encadena)
  │     └── service-status (otro subagente nuevo)
  │           Lee /tmp/ops-suite-session/  ← no vuelve a preguntar
  │
  └── "→ Run /ops-suite:db-migrate dev"  ← tú decides, corre en contexto actual
```

**Por qué importa al diseñar una skill:**
- Si necesitas que dos skills compartan información → escríbela en session state
- Si necesitas el historial de conversación → usa `disable-model-invocation: true` (y acepta que es destructiva-first)
- `workflow-deploy` es el caso especial: es destructiva pero sin `disable-model-invocation`, porque cada paso tiene su propio `AskUserQuestion` — la seguridad viene de los checkpoints, no del flag

---

## Slide: Qué es ops-suite

**Título:** ops-suite

**Subtítulo:** Un plugin de Claude Code para operar tu infraestructura sin salir del terminal

**Bullets:**
- Instala nuevas skills en Claude Code: kubectl, migraciones, colas, deploys
- Una conversación en lenguaje natural en lugar de múltiples herramientas
- Skills read-only se auto-invocan. Skills destructivas requieren comando explícito + confirmación

**Skills disponibles:**

| Skill | Qué hace | Tipo |
|-------|----------|------|
| deploy-status | Qué hay desplegado en cada env, drift entre envs | read-only |
| service-status | Estado de pods: réplicas, CPU, memoria, reinicios | read-only |
| service-logs | Logs + clasificación de errores + siguiente paso sugerido | read-only |
| db-query | Consulta en lenguaje natural → SQL con confirmación previa | read-only |
| db-migrate | Lista migraciones pendientes → aplica con confirmación | destructiva |
| queue-status | Estado de todas las colas y DLQs | read-only |
| queue-triage | Inspecciona mensajes fallidos, clasifica el error | read-only |
| queue-reprocess | Reencola o purga mensajes | destructiva |
| deploy | Despliega un PR, verifica salud, revisa logs | destructiva |
| workflow-deploy | Deploy guiado con intake form y checkpoints | destructiva |

---

## Slide: Configuración

**Título:** Configuración — tres líneas

**Muestra el fichero:** `~/.config/ops-suite/config.yaml`

```yaml
# Qué tecnologías usas (determina qué adapters se cargan)
orchestrator: kubernetes          # kubernetes | docker-compose | ecs
message_broker: rabbitmq          # rabbitmq | sqs | kafka | azure-service-bus
database: postgresql              # postgresql | mysql | mongodb

# Tus entornos
environments:
  dev:
    context: "dev-cluster"
    namespaces:
      apps: "my-apps"
      infra: "shared-infra"
    services:
      broker:
        name: "rabbitmq"
        management_port: 15672
        vhost: "my_vhost"
      database:
        name: "pgbouncer"
        port: 6432
        default_db: "myapp_dev"
  prod:
    # misma estructura, distintos valores

# Deploy
deploy:
  ci_provider: github-actions
  migration_tool: mikro-orm
  migration_command: "npm run migrations:up"
```

**Punto clave:**
> El plugin no está acoplado a Kubernetes ni a RabbitMQ. Cada skill carga un **adapter** según lo que configures. Si cambias a ECS o a SQS, cambias una línea.

**Cómo instalarlo:**
```
# 1. Añadir en .claude/settings.json
{ "plugins": ["/path/to/ops-suite"] }

# 2. Generar config con el wizard
/ops-suite:configure

# 3. Reiniciar Claude Code
```

---

## Demo 1: Estado del sistema

### Qué tocar

**Paso 1 — Qué hay desplegado**

Escribe en Claude Code:
```
¿qué hay desplegado en [tu-servicio]?
```

Claude ejecuta `deploy-status`. Output esperado:
- Tabla: env / commit / PR / autor / timestamp / réplicas
- Sección de drift: si dev y prod están en sync o cuántos commits de diferencia

**Qué mostrar:**
- La tabla con la información completa sin haber escrito un kubectl
- El drift entre envs con la lista de commits que hay de diferencia
- Que resuelve image tag → commit → PR → autor cruzando con GitHub Actions

---

**Paso 2 — Qué migraciones hay**

Escribe:
```
¿qué migraciones hay pendientes en dev?
```

Claude ejecuta `db-migrate` en modo listado (sin aplicar). Output esperado:
- Lista de migraciones aplicadas
- Lista de migraciones pendientes (si las hay)

**Qué mostrar:**
- Sin port-forward manual, sin conectarse a la DB a mano
- Si hay pendientes, el output sugiere ejecutar `/ops-suite:db-migrate dev`

---

**Paso 3 — Qué está fallando**

Escribe:
```
¿hay errores en los logs de [tu-servicio] en dev?
```

Claude ejecuta `service-logs`. Output esperado:
- Total de errores y tipos únicos
- Desglose por tipo: error, cuántas veces, muestra del mensaje
- Recommended next steps: qué comando ejecutar según el tipo de error

**Qué mostrar:**
- Todos los pods a la vez, no uno a uno
- La clasificación automática de errores
- Que ya te dice qué hacer a continuación (si hay errores de DB → sugiere db-migrate)

---

### Slide de cierre demo 1

**Título:** De 20 minutos a una conversación

**Antes:**
- Port-forward manual
- Pod a pod en kubectl logs
- Buscar en GitHub Actions qué se desplegó
- Comparar migraciones a mano

**Ahora:**
- `¿qué hay desplegado?` → tabla completa con drift
- `¿migraciones pendientes?` → estado sin conectarse
- `¿hay errores?` → clasificado + siguiente paso

---

## Demo 2: Mensajes

### Qué tocar

**Paso 1 — Estado de las colas**

Escribe:
```
¿cómo están las colas en dev?
```

Claude ejecuta `queue-status`. Output esperado:
- Lista de todas las colas con consumers y mensajes
- DLQs con el número de mensajes acumulados

**Qué mostrar:**
- Sin abrir el dashboard de RabbitMQ
- Si hay DLQs con mensajes, Claude ya sugiere el siguiente paso

---

**Paso 2 — Triaje**

Escribe:
```
triaje la DLQ de [tu-queue] en dev
```

Claude ejecuta `queue-triage`. Output esperado:
- Muestra de mensajes fallidos (los primeros N)
- Clasificación del error: tipo, stack trace, patrón
- Causa raíz identificada

**Qué mostrar:**
- No hace falta saber leer el mensaje en crudo
- Te dice por qué están fallando, no solo que están fallando

---

**Paso 3 — Reprocess**

Escribe:
```
/ops-suite:queue-reprocess [queue-name] dev
```

Claude ejecuta `queue-reprocess`. Output esperado:
- Muestra los mensajes que va a mover
- Pide confirmación antes de actuar
- Reencola y confirma 0 mensajes en la DLQ

**Qué mostrar:**
- Requiere comando explícito (no se auto-invoca)
- Confirmación antes de tocar nada
- Verifica el resultado automáticamente

---

### Slide de cierre demo 2

**Título:** Triaje de DLQs sin abrir el dashboard

**Antes:**
- Abrir RabbitMQ Management UI
- Peek mensajes uno a uno
- Leer el JSON a mano para entender el error
- Shovel manualmente o vía script

**Ahora:**
- `¿cómo están las colas?` → conteo de DLQs
- `triaje la DLQ de X` → causa raíz identificada
- `/ops-suite:queue-reprocess` → reencola con confirmación

---

## Slide: Cierre

**Título:** ops-suite en resumen

**Bullets:**
- Un plugin, una conversación, el cuadro completo
- No reemplaza saber de infraestructura — elimina el trabajo repetitivo de conseguir la información
- Technology-agnostic: kubernetes/ecs, rabbitmq/sqs, postgres/mysql — cambias el config
- Read-only es automático. Destructivo es siempre explícito y con confirmación

**Instalación:**
```
{ "plugins": ["/path/to/ops-suite"] }   # settings.json
/ops-suite:configure                     # wizard
# reiniciar Claude Code
```

---

## Checklist de verificación antes de la KS

Antes de presentar, prueba estos comandos contra tu entorno dev:

- [ ] `¿qué hay desplegado en [servicio]?` → tabla con drift visible
- [ ] `¿qué migraciones hay pendientes en dev?` → lista sin error
- [ ] `¿hay errores en los logs de [servicio] en dev?` → output clasificado
- [ ] `¿cómo están las colas en dev?` → lista con DLQs si las hay
- [ ] `triaje la DLQ de [queue] en dev` → causa raíz identificada
- [ ] `/ops-suite:queue-reprocess [queue] dev` → pide confirmación (no ejecutar en producción)

**Setup previo a la presentación:**
- Terminal con Claude Code abierto
- ops-suite apuntando a dev
- Tener algún servicio con al menos algún error en logs (o DLQ con mensajes) para que la demo sea real
- No usar prod en pantalla

# Línea del Tiempo — Sistema IoT de Seguridad para Cocinas Industriales
## Proyecto de Grado · UIS · Cesar Daniel Ávila Barbosa (2224642)

---

## CÓMO LEER ESTE DOCUMENTO

Este archivo es un documento de trabajo vivo. Cada sección tiene espacio
para que añadas notas, fechas exactas, nombres de personas, decisiones
que tomaste y por qué. Lo que está escrito en [CORCHETES] es un espacio
para que tú completes con información que yo no tengo.

Categorías usadas:
  [INVESTIGACIÓN]  Revisión de literatura, datos, normas
  [DECISIÓN]       Cambio de rumbo, elección técnica o de alcance
  [DESARROLLO]     Código, hardware, implementación
  [PROBLEMA]       Obstáculo encontrado y cómo se resolvió
  [HITO]           Entrega, presentación, demo

---
---

# PARTE 1 — EL ORIGEN
# Materia de Microcontroladores · [SEMESTRE — completa aquí]
# Aproximadamente: Mar–Abr 2026

---

## [HITO] Idea original: sistema de llamada automática a bomberos
Fecha: [completa aquí — ¿cuándo fue la primera clase o la primera idea?]
Contexto: Materia de Microcontroladores, UIS.

La idea inicial era construir un sistema que detectara una emergencia en
una cocina y llamara automáticamente a los bomberos sin intervención humana.
El enfoque era completamente de automatización de respuesta, no de monitoreo.

Notas adicionales que quieras agregar:
[...]

---

## [DESARROLLO] Primera maqueta: ESP32 + página web básica
Fecha: [completa aquí]

El primer prototipo físico consistía en:
- ESP32 como microcontrolador principal
- Página web para visualizar datos de sensores en tiempo real
- [¿Qué sensores tenía esta primera versión? ¿Temperatura sola? ¿Gas también?]
- [¿La página web era local o ya tenía servidor?]

En esta etapa no había backend separado — la página web era
[completa: ¿era servida desde el ESP32 mismo, era un archivo local, otra cosa?]

Notas adicionales:
[...]

---

## [DECISIÓN] Se descarta la llamada automática a bomberos
Fecha: [completa aquí]
Razón principal: Implicaciones legales — llamar a servicios de emergencia
de forma automatizada sin confirmación humana genera responsabilidades
legales que el proyecto no podía asumir.

Decisión tomada: en lugar de llamar directamente, el sistema enviaría
una alerta al celular del responsable y le daría la opción de llamar él mismo.

Impacto en el alcance:
- El sistema pasa de "automatizar la respuesta" a "monitorear y alertar"
- El usuario retiene el control de la decisión final
- Se reduce el riesgo legal del proyecto

Notas adicionales:
[...]

---

## [DECISIÓN] Idea de Smart Campus entra al proyecto
Fecha: Vacaciones [completa: ¿vacaciones de mitad de año? ¿entre semestres?]

La integración con Smart Campus UIS fue una idea paralela que existía
desde antes de que el proyecto tomara su forma actual. [Completa: ¿de
dónde salió esta idea? ¿fue sugerida por un profesor, salió de la materia,
fue iniciativa propia?]

Esta decisión amplió el alcance del proyecto de un dispositivo aislado
a un nodo dentro de una plataforma de monitoreo universitaria distribuida.

División de trabajo establecida en este período:
- Carlos (Cayalam): investigación, estado del arte, documentación académica
- Cesar: implementación práctica, código, hardware

Notas adicionales:
[...]

---
---

# PARTE 2 — PRIMERA EVOLUCIÓN
# Del prototipo simple al sistema con servidor
# Aproximadamente: Abr–May 2026

---

## [DECISIÓN] Se incorpora un servidor externo (Django)
Fecha: [completa aquí]
Razón: Era necesario tener persistencia de datos, historial de lecturas
y una API que múltiples clientes pudieran consultar. El ESP32 solo no
podía manejar esa carga ni almacenar el histórico.

El sistema pasa de:
  ESP32 → página web directa
a:
  ESP32 → Django REST API → base de datos → frontend React

Tecnologías elegidas:
- Backend: Django + Django REST Framework
- Base de datos: SQLite (desarrollo) → [¿PostgreSQL en producción?]
- Frontend: React + Vite

Razón de estas elecciones sobre alternativas:
[¿Por qué Django y no Flask, FastAPI u otro? ¿Por qué React y no Vue?]
[...]

---

## [DESARROLLO] Backend Django — primeras versiones
Fecha: Mayo 2026 (según historial de commits: 11 de mayo de 2026)

Endpoints implementados:
- GET  /api/lecturas/           → todas las lecturas paginadas (100/página)
- GET  /api/lecturas/ultima/    → última lectura en tiempo real
- GET  /api/lecturas/alertas/   → solo lecturas con alerta activa
- GET  /api/lecturas/resumen/   → resumen del estado del sistema
- POST /api/lecturas/           → recibir nueva lectura desde ESP32

Modelo de datos inicial: temperatura + gas
Segunda migración (0002): se añadió presión como variable adicional

El ESP32 envía datos cada 5 segundos vía HTTP POST.

Notas adicionales:
[...]

---

## [DESARROLLO] Frontend React — Dashboard
Fecha: Mayo 2026

Componentes desarrollados:
- Dashboard con lectura actual de sensores
- Gráficas de temperatura y gas con Recharts
- Historial de lecturas con paginación
- Página de alertas activas
- Actualización automática cada 5 segundos

Contribución de Carlos (commits b20cd8b, 034e603, 1a05a5d, 503f953):
- Integración completa Backend-Frontend
- Multi-page routing con React Router
- Gráficas con Recharts
- Dashboard con tabla de historial

Contribución de Cesar (commits d54f8da, ef56361, c34f236, y siguientes):
- Multi-page routing y API integration con datos reales
- Fix: mostrar errores cuando backend no está disponible
- Diseño profesional con CSS por componente
- Sensor de presión integrado al sistema

Notas adicionales:
[...]

---

## [PROBLEMA] Conflicto de pines en Arduino Uno con Wokwi
Fecha: [completa aquí]

Los pines PWM usados para los ventiladores (9, 10) entraban en conflicto
con los drivers A4988 de los steppers del diagrama original.

Solución: reasignación de pines
- Vent1: pin 9 → pin 3 (PWM libre)
- Vent2: pin 10 → pin 5 (PWM libre)
- Vent3: pin 6 (sin cambio)
- LED aspersor: pin 5 → pin 2
- PIR: pin 3 → pin A3

También se corrigió la conversión de temperatura: el sensor NTC de Wokwi
no usa la fórmula Steinhart-Hart real sino un mapeo lineal
(0 raw = -55°C, 1023 raw = 155°C).

Notas adicionales:
[...]

---
---

# PARTE 3 — SEGUNDA EVOLUCIÓN
# Del monitoreo básico al sistema inteligente con lógica de prioridades
# Aproximadamente: May–Jul 2026

---

## [DECISIÓN] Se define la lógica de prioridades de seguridad
Fecha: [completa aquí]

El sistema necesitaba manejar situaciones donde varios sensores disparaban
al mismo tiempo. Se definió un sistema de decisión en cascada donde cada
prioridad superior bloquea las inferiores:

P1 — Gas ≥ 73%: EMERGENCIA TOTAL
  → Todos los ventiladores al 100%
  → Válvula cerrada
  → Buzzer rápido (150ms)
  → Razón: explosión de gas es el riesgo más inmediato e irreversible

P2 — Temperatura ≥ 70°C: INCENDIO
  (subdividido posteriormente en dos fases, ver más abajo)
  → Aspersores ON
  → Válvula cerrada
  → Razón: incendio activo requiere cortar combustible

P3 — Presión ≥ 68%: PRESIÓN ALTA
  → Refuerzo de Vent2 (extracción)
  → Razón: presión alta es peligrosa para llamas de fogones y fugas

P4 — Temp 20–60°C: OPERACIÓN NORMAL
  → Control PWM proporcional en Vent1 y Vent2

Justificación del orden de prioridades:
[¿Tuviste que argumentar esto ante alguien? ¿Hay alguna norma técnica que lo respalde?]
[...]

---

## [DECISIÓN] Lógica de incendio revisada — dos fases
Fecha: Jun–Jul 2026
Razón del cambio: Se identificó que encender todos los ventiladores
durante un incendio es contraproducente porque alimenta las llamas
con oxígeno adicional.

Fase P2a — Incendio moderado (70–90°C):
  → Vent1 (inyección) APAGADO — no alimentar las llamas
  → Vent2 (extracción) al 100% — evacuar el humo
  → Aspersores ON

Fase P2b — Incendio severo (>90°C):
  → TODOS los ventiladores APAGADOS
  → Razón: a esa temperatura el flujo de aire propaga las llamas lateralmente
  → Aspersores ON, buzzer rápido igual que emergencia de gas

Esta decisión refleja el principio real de los sistemas contra incendios:
primero cortar la ventilación, luego suprimir con aspersores.

Fuente técnica de referencia para esta decisión:
[¿Hay algún paper o norma que respalda esto? Vale la pena buscarlo para el libro]
[...]

---

## [DECISIÓN] Se abandona Twilio/WhatsApp, se opta por app móvil propia
Fecha: [completa aquí]

Secuencia de decisiones:
1. Primera idea: llamar a bomberos automáticamente → descartado (legal)
2. Segunda idea: WhatsApp automático con pywhatkit → descartado
   Razón: pywhatkit viola TOS de WhatsApp y es bloqueado por Meta
3. Tercera idea: Twilio para SMS/llamada → descartado
   Razón: costo y accesibilidad para usuarios finales
4. Decisión final: app Android propia con alarma de audio personalizada
   Razón: más accesible, sin dependencia de terceros, control total del UX

La app envía notificación local + alarma de audio diferenciada según
el tipo de emergencia (gas vs incendio). El usuario decide si llama.

Notas adicionales sobre esta decisión:
[...]

---

## [DECISIÓN] Foco cambia: de automatización a envío masivo de datos
Fecha: [completa aquí]

Insight clave: en una cocina industrial real las variables cambian muy
rápido y de forma compleja. El valor real del sistema no está en
automatizar la respuesta sino en capturar, transmitir y analizar
el mayor volumen posible de datos para que el responsable humano
pueda tomar decisiones informadas.

Esto conecta directamente con Smart Campus: el sistema deja de ser
un dispositivo aislado y se convierte en un nodo de una red de monitoreo.

Implicación técnica: se diseña el simulador de cocinas virtuales que
genera datos JSON sintéticos para validar la plataforma sin necesidad
de tener múltiples maquetas físicas.

[¿Cuántas cocinas virtuales está contemplado simular?]
[¿Qué protocolo usa la integración con Smart Campus — MQTT, HTTP, otro?]
[...]

---
---

# PARTE 4 — ESTADO ACTUAL
# Sep 2026

---

## [HITO] Propuesta de proyecto de grado formalizada
Fecha: 2026 [completa el mes exacto]

Título oficial:
"Diseño de un prototipo de Plataforma IoT para el monitoreo de condiciones
de riesgo para cocinas industriales con integración al Smart Campus UIS"

Subtítulo:
"Nodo físico y simulación de múltiples cocinas mediante datos JSON"

Pregunta de investigación:
¿De qué manera una plataforma IoT puede ayudar con el monitoreo y
detección de alarmas en los sistemas de cocinas industriales y así
minimizar el tiempo de respuesta ante algún incidente?

Objetivo general:
Desarrollar un prototipo IoT sobre la plataforma Smart Campus UIS para
el monitoreo de variables de riesgo (temperatura, concentración de GLP
y presencia de llama) con el fin de identificar posibles riesgos en
cocinas industriales ubicadas en entornos cerrados.

Objetivos específicos:
1. Analizar referentes tecnológicos, técnicos y requerimientos para
   detección de gas, temperatura y llama en cocinas industriales.
2. Definir escenarios de operación, niveles de riesgo, modelo de datos
   y respuestas esperadas del sistema.
3. Diseñar la arquitectura de software e infraestructura que integre
   nodo físico, backend, app móvil y generador de cocinas virtuales.
4. Implementar el prototipo físico con sensores de GLP, temperatura y
   llama, alarmas locales y módulo de ventilación de prueba.
5. Validar mediante pruebas controladas el funcionamiento de hardware,
   software y Smart Campus UIS.

Director de proyecto: [completa aquí]
Modalidad: Práctica / Proyecto Aplicado
Código del estudiante: 2224642

---

## [DESARROLLO] Repositorio organizado en GitHub Organization
Fecha: Sep 2026
Organización: github.com/cocinas-industriales-uis

Repositorios:
- esp32          → Firmware Arduino/ESP32 (sceht.ino + wokwi_diagram.json)
- servidor       → Backend Django REST API
- pagina-web     → Frontend React + Recharts
- investigacion  → Análisis estadístico, notebooks, informes, referencias
- mqtt           → Broker MQTT (pendiente de implementar)
- app-movil      → App Android (pendiente de implementar)

Hitos de limpieza del historial:
- Eliminados archivos pesados del historial: frontend.zip (30MB) y
  cocinas_industriales_IoT.zip (65MB × 3 copias)
- Unificadas ramas main y master
- Autoría de commits verificada: 4 commits de Carlos (Cayalam) a su nombre,
  resto a nombre de Cesar

---

## [DESARROLLO] Prototipo de simulador interactivo HTML
Fecha: Jun–Sep 2026

Archivos generados (en docs/diagramas/):
- simulador_cocina.html      → simulador completo con sliders
- diagrama_prioridades.html  → diagrama de lógica de prioridades
- logica_prioridades_cocina.html → versión alternativa del diagrama

El simulador replica la lógica completa del firmware en el navegador:
- Sliders de temperatura, gas y presión
- Ventiladores animados con velocidad proporcional
- LCD virtual con los mismos mensajes que el hardware real
- LEDs de válvula, aspersor y buzzer con estados animados
- Badge de prioridad activa

---
---

# PARTE 5 — LO QUE FALTA
# Oct 2026 → Feb 2027

---

## [DESARROLLO PENDIENTE] Integración MQTT
Fecha planificada: Oct 2026

Estado actual: el ESP32 envía datos vía HTTP POST al servidor Django.
MQTT permitirá comunicación en tiempo real bidireccional y menor latencia.

Tareas:
- [ ] Configurar broker Mosquitto en servidor
- [ ] Modificar firmware ESP32 para publicar en topics MQTT
- [ ] Suscriptor Django que consume mensajes y persiste en BD
- [ ] Validar latencia vs HTTP actual
- [ ] Integrar con protocolo de Smart Campus UIS

Preguntas abiertas:
[¿Smart Campus ya usa MQTT o tiene su propio protocolo?]
[¿Quién autoriza las pruebas de carga en la infraestructura institucional?]
[...]

---

## [DESARROLLO PENDIENTE] App móvil Android
Fecha planificada: Oct–Nov 2026
Rama: feat/app-emergencia (pendiente de migrar a organización)

Funcionalidades planificadas:
- Pantalla principal: estado de sensores en tiempo real
- Sistema de alarma de audio diferenciada por tipo de emergencia
  (sonido distinto para gas vs incendio vs presión)
- Notificaciones push cuando se supera umbral crítico
- Historial de alertas con timestamp
- Botón de llamada (el usuario decide si llama, no el sistema)

Tecnología: [¿Android nativo, Flutter, React Native?]
[...]

---

## [DESARROLLO PENDIENTE] Simulador de cocinas virtuales (datos JSON)
Fecha planificada: [completa aquí]

El informe menciona que se generarán cocinas virtuales con datos
sintéticos para validar la plataforma sin maquetas físicas múltiples.

Tareas:
- [ ] Definir el formato JSON de cada "cocina virtual"
- [ ] Generador de datos sintéticos con variación realista de variables
- [ ] Pruebas de carga: incrementar gradualmente número de cocinas
- [ ] Medir latencia, pérdida de mensajes y recuperación ante fallo
- [ ] Documentar resultados para el capítulo de validación del libro

[¿Cuántas cocinas virtuales se planea simular simultáneamente?]
[...]

---

## [VALIDACIÓN PENDIENTE] Pruebas de integración
Fecha planificada: Nov 2026

Escenarios a probar:
1. Operación normal (todos los sensores en rangos seguros)
2. Alerta de gas no crítica (P3 activo, ventiladores acelerados)
3. Emergencia de gas (P1, todos al máximo, válvula cerrada)
4. Incendio moderado (P2a, solo extracción, aspersores)
5. Incendio severo (P2b, todo apagado, aspersores)
6. Fallo del servidor (¿qué hace el ESP32 si no hay respuesta?)
7. Prueba de carga: N cocinas virtuales simultáneas

Métricas a medir:
- Latencia: desde que el sensor detecta hasta que llega la alerta al celular
- Tasa de falsos positivos con los umbrales actuales
- Tiempo de recuperación tras fallo de comunicación

---

## [HITO PENDIENTE] Entrega del libro de tesis
Fecha planificada: Ene 2027

Estructura del libro (pendiente de confirmar con director):
Cap 1: Introducción, planteamiento del problema, objetivos
Cap 2: Marco teórico y estado del arte
Cap 3: Metodología y diseño del sistema
Cap 4: Implementación (firmware, backend, frontend, app)
Cap 5: Validación y resultados
Cap 6: Conclusiones y trabajo futuro
Anexos: código fuente, tablas de pruebas, manual de instalación

[¿Tienes ya la plantilla de la UIS para el documento final?]
[¿Quién es el director? ¿Ya tiene asignado co-director?]

---

## [HITO PENDIENTE] Sustentación ante jurado
Fecha planificada: Feb 2027

Elementos de la presentación:
- Demo en vivo del simulador HTML (sin necesidad de hardware)
- Demo del prototipo físico [¿estará listo para la sustentación?]
- Presentación de resultados de pruebas de integración
- Defensa del análisis estadístico (Mann-Kendall, binomial negativa)
- Argumentación de las decisiones de diseño (especialmente la lógica P1-P4)

---
---

# RESUMEN DE LA EVOLUCIÓN DE LA IDEA CENTRAL

Versión 1 (Mar 2026 — inicio en Microcontroladores):
  "Sistema que detecta emergencia y llama a los bomberos automáticamente"
  Foco: automatización de la respuesta de emergencia
  Hardware: ESP32 + sensores básicos + página web directa

Versión 2 (Abr–May 2026 — decisión legal y técnica):
  "Sistema que detecta, alerta al responsable y le da la opción de llamar"
  Foco: notificación humana con decisión humana (sin compromiso legal)
  Hardware: ESP32 + Django backend + React frontend + Twilio/WhatsApp

Versión 3 (May–Jun 2026 — decisión de accesibilidad):
  "Sistema de monitoreo con alerta en app propia + historial de datos"
  Foco: accesibilidad y control del canal de notificación
  Hardware: ESP32 + Django + React + app Android propia

Versión 4 (Jul–Sep 2026 — ampliación de alcance):
  "Plataforma IoT de monitoreo distribuido integrada a Smart Campus UIS"
  Foco: envío masivo de datos, múltiples cocinas virtuales, escalabilidad
  Hardware: ESP32 (nodo físico) + cocinas virtuales JSON + Smart Campus UIS
  Título final: "Diseño de un prototipo de Plataforma IoT para el monitoreo
  de condiciones de riesgo para cocinas industriales con integración al
  Smart Campus UIS"

La evolución refleja un desplazamiento desde la automatización de la
respuesta hacia la instrumentación, el monitoreo continuo y la integración
en una plataforma institucional más grande.

---

# PERSONAS Y ROLES

Cesar Daniel Ávila Barbosa (2224642)
  Rol: implementación práctica, firmware, backend, frontend, infraestructura
  GitHub: cesardanielavilabarbosa-blip

Carlos (Cayalam)
  Rol: investigación, estado del arte, documentación académica
  GitHub: Cayalam
  Commits propios: b20cd8b, 034e603, 1a05a5d, 503f953 (11 mayo 2026)

Director de proyecto: [completa aquí]
[¿Hay co-director o asesor externo?]

---

# TECNOLOGÍAS USADAS POR COMPONENTE

Firmware (repo: esp32)
  Plataforma:     Arduino Uno / ESP32
  Lenguaje:       C++ (Arduino)
  Sensores:       NTC temperatura (A0), MQ-6 gas GLP (A1), presión (A2)
  Actuadores:     3 motores DC via L293D, LED válvula, LED aspersor, buzzer
  Display:        LCD 16×2 I2C
  Simulación:     Wokwi (wokwi_diagram.json)

Backend (repo: servidor)
  Framework:      Django + Django REST Framework
  Base de datos:  SQLite (dev)
  Endpoints:      /api/lecturas/ con 5 rutas
  Comunicación:   HTTP POST desde ESP32 cada 5 segundos
  Pendiente:      migración a MQTT

Frontend (repo: pagina-web)
  Framework:      React + Vite
  Gráficas:       Recharts
  Routing:        React Router
  Actualización:  polling cada 5 segundos
  Páginas:        Dashboard, Historial, Alertas

App móvil (repo: app-movil)
  Tecnología:     [pendiente de definir]
  Estado:         en desarrollo
  Rama origen:    feat/app-emergencia

Comunicación IoT (repo: mqtt)
  Protocolo:      MQTT (pendiente)
  Estado:         planificado

Análisis estadístico (repo: investigacion)
  Herramienta:    Python + Jupyter Notebooks
  Métodos:        Regresión binomial negativa, Mann-Kendall
  Datos:          Positiva 2026, OSB salud mental, Bomberos Bucaramanga,
                  Bomberos Bogotá, NFPA, BLS SOII, CPSC NEISS

---

Última actualización: Sep 2026

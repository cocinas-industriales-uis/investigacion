# SEGUIMIENTO DE AUDITORÍA — Sistema IoT Cocinas Industriales UIS

> Archivo vivo. Se actualiza al cierre de cada fase. Para retomar: leer la sección 12 y el estado de las fases (sección 3).
> Convención: **[V]** verificado por lectura estática del código · **[S]** sospecha sin verificar · **[E]** verificado ejecutando.
> Última actualización: 2026-10-12 · Fase 0 cerrada · Fase 1 (firmware) **validada parcialmente** (solo en PC con stubs).

## 1. Objetivo y alcance
Auditar y corregir por componentes el prototipo (firmware, MQTT, backend, web, app móvil), validar cada cambio y, al final, actualizar la investigación para que describa el sistema realmente construido. La investigación académica NO se modifica hasta la fase final.

## 2. Inventario de componentes (confirmado en disco)
Cada carpeta es un repositorio git independiente (6 repos; no hay repo raíz).

| Componente | Tecnología confirmada | Último commit | Pruebas existentes |
|---|---|---|---|
| `esp32/` | Arduino C++ para ESP32 DevKit (`cocina_esp32_1_.ino`, 553 líneas): WiFi, PubSubClient, ArduinoJson, LiquidCrystal_I2C. `wokwi_diagram.json` (Arduino Uno) | 2026-10-02 | Ninguna |
| `mqtt/` | Python, paho-mqtt 1.6.1; `mqtt_client.py` (suscriptor→Django ORM), `mqtt_simulator.py`, `mqtt_test.py`, `mosquitto.conf` | 2026-10-07 | `mqtt_test.py` (necesita broker) |
| `servidor/` | Django 5.2.7 + DRF 3.15.2, SQLite por defecto / PostgreSQL, app `cocina` (modelo `Lectura`); app `sensores` vacía y no instalada | 2026-09-24 | `sensores/tests.py` vacío; ninguna real |
| `pagina-web/` | React 19 + Vite 8 + Recharts + axios + react-router; 3 páginas | 2026-09-24 | Ninguna (solo eslint) |
| `app-movil/` | Kotlin + Compose + Retrofit/OkHttp-SSE; modo mock (debug) y remoto (esqueleto) | 2026-10-09 | 3 archivos de pruebas unitarias (no ejecutadas; el README dice que nunca se compiló) |
| `investigacion/` | Docs, 3 HTML de diagramas/simulador, informes .docx/.pdf, notebooks | 2026-10-02 | — |

## 3. Estado de las fases
| # | Fase | Estado |
|---|---|---|
| 0 | Inventario y mapa de dependencias | **Cerrada** (este documento) |
| 1 | Firmware, hardware y adquisición de datos (`esp32/`) | **Validada parcialmente** (ver sección 13) |
| 2 | Contrato MQTT + suscriptor + simulador (`mqtt/`) | Pendiente — **siguiente** |
| 3 | Backend Django (modelo, API, auth, alarmas, stream) | Pendiente |
| 4 | Web (`pagina-web/`) | Pendiente |
| 5 | App móvil (`app-movil/`) | Pendiente |
| 6 | Integración extremo a extremo y trazabilidad | Pendiente |
| 7 | Actualización de la investigación | Pendiente |

## 4. Archivos revisados / modificados
- Revisados (lectura): todos los fuentes de `esp32/`, `mqtt/` (cliente completo; simulador y test solo cabecera), `servidor/` (backend, cocina, requirements, .env.example), `pagina-web/` (api.js, páginas principales, componentes de lectura/ventiladores), `app-movil/` (README, build, manifest, AppContainer, capa remota), READMEs de todos los repos, PROTOTIPO.docx, listado_materiales.docx, textos de los 3 HTML, línea de tiempo (tramo final), troubleshooting_backend.md.
- No leídos aún (pendiente en su fase): resto de `mqtt_simulator.py`/`mqtt_test.py`, `Graficas.jsx`/`HistorialLecturas.jsx`/`HistorialPage.jsx`, UI y servicio Android, tests Android, Informe_Plataforma_Web (.docx), presentación PDF, notebooks.
- Modificados (Fase 1, repo `esp32`): `cocina_esp32_1_.ino`, `README.md` (reescrito: estaba obsoleto), nuevo `test_host/`. Repo `investigacion`: solo este archivo.

## 5. Hallazgos detectados (todos [V] por lectura estática salvo indicación; aún sin ejecutar)

### Críticos
- **C1. Ruptura de la ruta de datos MQTT→BD.** `mqtt/mqtt_client.py` hace `Lectura.objects.create(...)` con campos que el modelo no tiene (`delta_t, prioridad, ventilador_inyeccion, ventilador_emergencia, valvula_cerrada, aspersor_activo, cocina_id, ts_esp32`) y el modelo tiene `ventilador_inyeccion_1/_2` booleanos. Resultado esperado: `TypeError` capturado y registrado; no se guarda nada. Además las migraciones (0001, 0002) no contienen esos campos. *(Evidencia: models.py vs mqtt_client.py:139-155.)*
- **C2. Sin autenticación en la API.** `DEFAULT_PERMISSION_CLASSES = AllowAny`: cualquiera puede leer, crear, modificar y borrar lecturas (ModelViewSet completo). Sistema de seguridad física cuya telemetría es falsificable.
- **C3. El reconocimiento de alarma y el login que exige la app no existen.** La app espera `auth/login/`, `alarmas/`, `alarmas/{id}/reconocer/` y `stream/` (SSE); el backend solo tiene `lecturas/`. (Ya reconocido en el README de la app.)

### Altos
- **A1. Validadores del backend incompatibles con el firmware.** Serializer: temperatura −10..100, `nivel_gas` 0..1023, `presion` 900..1100 hPa. Firmware ESP32: ADC 0..4095, presión como porcentaje/raw de potenciómetro, temperatura −55..155. `estado_sistema` max_length=20 y choices de 5 valores; el cliente MQTT genera hasta `VERIFICANDO_INCENDIO_MODERADO` (29 car.) y 10 estados distintos.
- **A2. Contrato no unificado entre componentes:** web usa `nivel_gas`, `ventilador_*` booleanos, `presion` en hPa; app usa `gas_raw/gas_pct`, `v1_pct…`, `prioridad`, `cocina_id`; MQTT usa el segundo. La web no mostrará ventiladores/prioridad/cocina.
- **A3. `AlertasPage.jsx` usa `alerta.tipo` y `alerta.mensaje`**, campos que `AlertaSerializer` no entrega → lista de alertas con celdas vacías.
- **A4. `mqtt_client.py` vive en `mqtt/` pero hace `django.setup()` con `backend.settings`** y su README manda ejecutarlo como `python cocina/mqtt_client.py` desde otro directorio (`Backend_cocina/`) que no existe en la estructura actual. Con la estructura de repos separados no arranca sin ajustar `PYTHONPATH`. Además no está integrado como proceso del servidor.
- **A5. [CORREGIDO Fase 1: pin 23] Conflicto de pines en firmware:** `BUZZER_PIN 21` coincide con SDA del I2C por defecto del ESP32 (el propio código lo comenta como "OJO"). El LCD y el buzzer se interferirían.
- **A6. Autenticación/transporte MQTT:** broker con `allow_anonymous true`, sin TLS; credenciales WiFi/IP en claro en el .ino (placeholders). Aceptable en desarrollo, no para validar seguridad.

### Medios
- M1. `lcd.clear()` cada 50 ms en el loop → parpadeo. **[E] 200 clears/10 s; CORREGIDO en Fase 1 (falta verlo en hardware).**
- M2. `analogWrite()` en ESP32 requiere core Arduino-ESP32 3.x; no documentado la versión requerida [S].
- M3. Firmware: tras `sensorError` publicaba 0 °C como dato válido y además contaminaba ΔT (pico espurio al recuperar: 9 vueltas con P3/P2 en la prueba). **[E] CORREGIDO en Fase 1** (`sensor_ok`, ΔT protegido).
- M4. **[No reproducido en simulación con σ=10 cuentas]** Firmware: `calcularDeltaT` usa ventana `HIST_N * dt` sobre 10 muestras de 50 ms (~0,5 s) → ΔT/s ruidoso con ADC cuantizado; umbral 2 °C/s puede disparar P3 por ruido [S: validar con datos].
- M5. Firmware: P5 (presión+gas) se evalúa antes que P4 correctamente, pero P6/P7 usan `presAlta && !gasAlerta`; revisar casos de borde en fase 1 (tabla de verdad).
- M6. `ALLOWED_HOSTS` documentado como `*` en troubleshooting; CORS fijo en código (ignora `.env`); `CORS_ALLOWED_ORIGINS` no incluye la app/IP del ESP.
- M7. `settings.py` declara "Django 6.0.5" en cabecera mientras requirements fija 5.2.7; `rest_framework_simplejwt` y `drf-yasg` instalados/pedidos pero sin endpoints de token ni documentación.
- M8. `paho-mqtt==1.6.1` fijado, API `mqtt.Client(client_id=…)` sin `CallbackAPIVersion` (válido solo en 1.x). `requirements.txt` de mqtt pide `django>=4.2` mientras el backend usa 5.2.7.
- M9. Web: URL base `http://localhost:8000/api` hardcodeada pese a existir `VITE_API_URL` en `.env.example`; `Dashboard.jsx` y `DashboardPage.jsx` duplicados (el primero sin uso en rutas); botón "Emergencia" sin acción; texto "Sistema Normal" y "Todos los parámetros… dentro de rangos" estáticos (no dependen del estado real) → **información de seguridad engañosa**. Umbrales de `AlertasPage` (35 °C, 450 ppm) distintos a los del firmware y el gas se rotula "ppm" sobre un valor raw.
- M10. Web: `obtenerLecturas(limit)` envía `limit`, que DRF PageNumberPagination ignora (devuelve 100 por página).
- M11. La app nunca se compiló según su README; el modo remoto no se ha probado.

- F1-1 (nuevo, Fase 1, Alto). Red bloqueante en firmware: `conectarWiFi()` hasta 15 s en `setup()` y `reconectarMQTT()` con 3 intentos + `delay(500)` en cada vuelta → con broker caído el control local quedaba sin atender hasta ~10 s por vuelta. **[E] CORREGIDO parcialmente** (sin delays, 1 intento/10 s); persiste ~3 s por intento por el timeout TCP de `connect()` (ABIERTO, requiere hardware/FreeRTOS).
- F1-2 (Medio) **[RESUELTO por decisión del usuario 2026-10-12: cerrar válvula y sonar ya; [E] T11]**. Con llama + T ≥ 60 °C + gas ≥ 10 % LEL, P3 espera 10 s: válvula abierta y buzzer mudo durante la confirmación (los ventiladores suben por temperatura). **[E]** No se modificó la lógica de seguridad.
- F1-3 (Medio) **[RESUELTO por decisión del usuario 2026-10-12: llama + NTC averiado = P3 inmediato; [E] T19/T20]**. Con falla del NTC y llama, `temperatura=0` solo permite P8 (sin aspersor ni válvula). Definir respuesta conservadora.

### Bajos
- B1. Typo `obtenerAlertusPorTipo` en api.js; README de web menciona "datos de prueba automáticos" que no existen.
- B2. (README esp32 ya corregido en Fase 1; el archivo sigue sin carpeta homónima) Nombre de archivo `cocina_esp32_1_.ino` vs. documentación que habla de `sceht.ino`; el `.ino` no está en carpeta homónima (Arduino IDE exige carpeta con el mismo nombre).
- B3. App `sensores/` de Django vacía y no instalada.
- B4. Sin `.gitignore` verificado para `db.sqlite3`/`.env` en todos los repos (revisar en fase 3).

## 6. Correcciones realizadas
**Fase 1 (esp32/cocina_esp32_1_.ino):**
- A5 → `BUZZER_PIN` 21→23 (el 21 es SDA del LCD). **Requiere recablear el buzzer** si ya está montado en 21.
- M1 → LCD: `lcdLinea()` reescribe solo si cambia el texto; ya no hay `lcd.clear()` cada 50 ms.
- M3 → falla de NTC: no alimenta el historial de ΔT (antes un −999 provocaba pico de ΔT y P3/P2 espurio al recuperarse); el payload añade `sensor_ok` (campo aditivo, compatible); la LCD muestra `ERR`.
- F1-1 → WiFi y MQTT ya no bloquean. Antes `setup()` tardaba hasta 17 s sin WiFi y el loop hasta ~10 s por vuelta con el broker caído (actuadores sin atender). Ahora `setup()` ~0,5 s, reintentos cada 10 s.
- Documentación: README del firmware reescrito con placa, pines, lógica, payload y pendientes.

## 7. Pruebas ejecutadas
**Fase 1 — [E] en PC** (`esp32/test_host/run.sh`: compila el `.ino` real con stubs de la API Arduino y ejecuta 18 escenarios):
- Línea base (firmware original): 18 escenarios, **5 con fallo** (pin buzzer/SDA, ΔT tras falla de sensor + `sensor_ok`, reintentos MQTT en ráfaga, `setup()` 17 s sin WiFi, 200 `lcd.clear()`/10 s).
- Tras las correcciones: **0 fallos**, 1 caso `ABIERTO` (F1-1 residual). Tras las decisiones F1-2/F1-3: 20 escenarios, 0 fallos. Lógica P0–P8, confirmación 10 s, cadencia 0,5/1/5 s y claves del payload: OK.
- Limitaciones: stubs sin ADC/PWM reales ni tiempos de red reales; el toolchain ESP32/arduino-cli **no está disponible** en este entorno (sin acceso de red) → **compilación real pendiente**. Ruido de ΔT: con σ=10 cuentas (supuesto) no hubo falsos P3 → M4 **no reproducido**.
Previstas en otras fases: compilación del firmware (arduino-cli, si es viable en el entorno), `manage.py check/makemigrations --check/test`, `mqtt_test.py` con mosquitto, `npm run lint && npm run build`, `./gradlew testDebugUnitTest` (probablemente no ejecutable aquí: requiere Android SDK; se registrará como limitación).

## 8. Decisiones técnicas
- D0. Las carpetas son repos independientes: los cambios se harán por repo y se documentarán aquí; no se crea repo raíz.
- D1 (propuesta, pendiente de ratificar en fase 3). Tomar el **payload MQTT del firmware actual** como contrato canónico de lectura (es el que ya usan MQTT, simulador, app y tests) y adaptar modelo/serializers/web a él, conservando compatibilidad con los campos antiguos solo si es barato.

## 9. Discrepancias código ↔ informes ↔ diagramas
| Tema | Código actual | Documentos | Prioridad documental |
|---|---|---|---|
| Transporte ESP32→servidor | MQTT únicamente | Línea de tiempo y README esp32: HTTP POST cada 5 s; MQTT "pendiente" | Código es más reciente |
| Placa | ESP32 DevKit (ADC 12 bits) | README esp32 (**ya reescrito**); `wokwi_diagram.json` sigue siendo Arduino Uno y no corresponde al firmware; PROTOTIPO: "ESP32 Vedikit v4" | Código/PROTOTIPO |
| Sensores | NTC (A0), MQ-2, potenciómetro de presión, KY-026 | Materiales: DS18B20, MQ-6, KY-026, OLED; diagramas v2: BMP280 y MQ-2; PROTOTIPO: relé y válvula solenoide | **Contradicción real: definir BOM definitivo (decisión humana)** |
| Display | LCD 16×2 I2C | Materiales: OLED 0.96" | Decisión humana |
| Prioridades | P0–P8 + Normal=9, umbrales LEL 10/20 %, confirmación 10 s | README esp32 (viejo): 4 prioridades por % de gas; `simulador_cocina.docx`: 73 %/70–90 °C | Código y `Simulador_IoT_Cocinas_v3.html` coinciden; el resto está obsoleto |
| P7 | Temp > 20 °C | Diagrama v2: 30–60 °C; MQTT README: 20–60 °C | Alinear tras validar en fase 1 |
| P0 | Todo OFF (gas+llama), válvula cerrada | Consistente con diagramas v2/v3 | — |
| Backend | `lecturas/` booleanos | troubleshooting_backend.md cita `/api/ingesta/` y `/api/dispositivos/` que no existen en `servidor/`; dice que el backend "no está en el repo" (ya está) | Código |
| Alcance de la investigación | — | Objetivo: Smart Campus UIS, "múltiples cocinas virtuales"; no hay integración Smart Campus en código | Registrar como pendiente de trazabilidad |
| Nombre oficial del trabajo | — | Propuesta ≠ PROTOTIPO.docx (ventilación) | Aclarar con el estudiante |

## 10. Pruebas físicas / integraciones pendientes
- Calibración MQ-2 (raw↔%LEL) con gas real y NTC con termistor real (el código usa Steinhart-Hart, el README dice mapeo lineal Wokwi).
- Comportamiento de LCD+buzzer con el conflicto de pin 21.
- Latencia ESP32→broker→BD→web/app con medición real.
- Prueba de pérdida de WiFi/broker (el firmware sigue actuando localmente; verificar).
- Alarma sonora/pantalla completa en teléfono real, push FCM.
- Seguridad física: la válvula/aspersor son LEDs en el prototipo; no se valida control real de gas.

## 11. Dependencias entre tareas
`esp32 (payload) → mqtt (validación/simulador) → servidor (modelo, API, alarmas) → pagina-web / app-movil → investigación`.
- No corregir web ni app antes de fijar el contrato en fase 3.
- La decisión del BOM (sección 9) condiciona el README de firmware y la memoria final, no el código de fases 2–5.

## 12. Próximo paso exacto
**Fase 2 — MQTT:** (1) añadir `sensor_ok` al contrato y validar el payload real del firmware (16 claves) en `mqtt_client.py`/simulador/tests; (2) resolver A4 (ubicación/ejecución de `mqtt_client.py`, rutas del README) y M8 (paho 1.6.1 vs 2.x); (3) probar con Mosquitto si es instalable aquí, o con un broker en proceso; (4) NO tocar el modelo Django hasta la Fase 3 (C1 depende de ello).

## 8b. Decisiones del usuario
- 2026-10-12 · F1-2: con llama + gas ≥ 10 % LEL durante la confirmación de P3 → válvula cerrada y buzzer inmediatos (aspersor/corte de inyección esperan).
- 2026-10-12 · F1-3: llama + NTC averiado → P3 sin espera.

## 13. Fase 1 — cierre
Estado: **Validada parcialmente.** Cambios en `esp32` en commit local (push pendiente de autorización de GitHub).
| Pendiente | Tipo | Dónde |
|---|---|---|
| Compilar con arduino-cli/core ESP32 3.x | verificación (sin red en este entorno) | usuario o fase 6 |
| Recablear buzzer a GPIO23 | hardware | usuario |
| Timeout TCP de MQTT / tarea FreeRTOS | hardware | fase 6 |
| Calibrar NTC, MQ-2, ruido ΔT | pruebas físicas | fase 6 |
| Contrato: nuevo campo `sensor_ok` | integración | fase 2 y 3 |
| `wokwi_diagram.json` obsoleto (Uno) | documentación | fase 7 |

# SEGUIMIENTO DE AUDITORÍA — Sistema IoT Cocinas Industriales UIS

> Archivo vivo. Se actualiza al cierre de cada fase. Para retomar: leer la sección 12 y el estado de las fases (sección 3).
> Convención: **[V]** verificado por lectura estática del código · **[S]** sospecha sin verificar · **[E]** verificado ejecutando.
> Última actualización: 2026-10-15 · Fase 0 cerrada · Fases 1 y 2 **validadas parcialmente** · Fase 3A (backend) **validada dentro del alcance comprobado** (18 pruebas OK en el entorno del usuario).

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
| 2 | Contrato MQTT + suscriptor + simulador (`mqtt/`) | **Validada parcialmente** (ver sección 14) |
| 3A | Backend: modelo, migración, API de lectura, autenticación | **Validada dentro del alcance comprobado** (ver sección 15) |
| 3B | Backend: alarmas con reconocimiento + `stream/` SSE | Pendiente — **siguiente** |
| 4 | Web (`pagina-web/`) | Pendiente |
| 5 | App móvil (`app-movil/`) | Pendiente |
| 6 | Integración extremo a extremo y trazabilidad | Pendiente |
| 7 | Actualización de la investigación | Pendiente |

## 4. Archivos revisados / modificados
- Fase 2 (repo `mqtt`): modificados `mqtt_client.py` (refactor), `mqtt_simulator.py`, `README.md`, `requirements.txt`; nuevos `payload.py`, `test_offline.py`, `test_data/firmware_payloads.jsonl`, `.gitignore`. Repo `esp32`: `test_host/test.cpp` (escenario `DUMP`).
- Revisados (lectura): todos los fuentes de `esp32/`, `mqtt/` (cliente completo; simulador y test solo cabecera), `servidor/` (backend, cocina, requirements, .env.example), `pagina-web/` (api.js, páginas principales, componentes de lectura/ventiladores), `app-movil/` (README, build, manifest, AppContainer, capa remota), READMEs de todos los repos, PROTOTIPO.docx, listado_materiales.docx, textos de los 3 HTML, línea de tiempo (tramo final), troubleshooting_backend.md.
- No leídos aún (pendiente en su fase): resto de `mqtt_simulator.py`/`mqtt_test.py`, `Graficas.jsx`/`HistorialLecturas.jsx`/`HistorialPage.jsx`, UI y servicio Android, tests Android, Informe_Plataforma_Web (.docx), presentación PDF, notebooks.
- Modificados (Fase 1, repo `esp32`): `cocina_esp32_1_.ino`, `README.md` (reescrito: estaba obsoleto), nuevo `test_host/`. Repo `investigacion`: solo este archivo.

## 5. Hallazgos detectados (todos [V] por lectura estática salvo indicación; aún sin ejecutar)

### Críticos
- **C1. [Lado MQTT resuelto en Fase 2; falta el modelo → Fase 3]** **Ruptura de la ruta de datos MQTT→BD.** `mqtt/mqtt_client.py` hace `Lectura.objects.create(...)` con campos que el modelo no tiene (`delta_t, prioridad, ventilador_inyeccion, ventilador_emergencia, valvula_cerrada, aspersor_activo, cocina_id, ts_esp32`) y el modelo tiene `ventilador_inyeccion_1/_2` booleanos. Resultado esperado: `TypeError` capturado y registrado; no se guarda nada. Además las migraciones (0001, 0002) no contienen esos campos. *(Evidencia: models.py vs mqtt_client.py:139-155.)*
- **C2. [CORREGIDO Fase 3A, sin ejecutar]** **Sin autenticación en la API.** `DEFAULT_PERMISSION_CLASSES = AllowAny`: cualquiera puede leer, crear, modificar y borrar lecturas (ModelViewSet completo). Sistema de seguridad física cuya telemetría es falsificable.
- **C3. [PARCIAL: `auth/login/` hecho en 3A; faltan alarmas, reconocimiento y `stream/` → 3B]** **El reconocimiento de alarma y el login que exige la app no existen.** La app espera `auth/login/`, `alarmas/`, `alarmas/{id}/reconocer/` y `stream/` (SSE); el backend solo tiene `lecturas/`. (Ya reconocido en el README de la app.)

### Altos
- **A1. [CORREGIDO Fase 3A, sin ejecutar: el backend ya no valida la entrada HTTP (se eliminó; valida `mqtt/payload.py`); estado ≤ 20 caracteres]** **Validadores del backend incompatibles con el firmware.** Serializer: temperatura −10..100, `nivel_gas` 0..1023, `presion` 900..1100 hPa. Firmware ESP32: ADC 0..4095, presión como porcentaje/raw de potenciómetro, temperatura −55..155. `estado_sistema` max_length=20 y choices de 5 valores; el cliente MQTT genera hasta `VERIFICANDO_INCENDIO_MODERADO` (29 car.) y 10 estados distintos.
- **A2. Contrato no unificado entre componentes:** web usa `nivel_gas`, `ventilador_*` booleanos, `presion` en hPa; app usa `gas_raw/gas_pct`, `v1_pct…`, `prioridad`, `cocina_id`; MQTT usa el segundo. La web no mostrará ventiladores/prioridad/cocina.
- **A3. [Backend corregido en 3A: `AlertaSerializer` entrega `tipo` y `mensaje`; falta verificar en la web]** **`AlertasPage.jsx` usa `alerta.tipo` y `alerta.mensaje`**, campos que `AlertaSerializer` no entrega → lista de alertas con celdas vacías.
- **A4. [RESUELTO Fase 2: `SERVIDOR_DIR`, Django cargado en forma diferida, README corregido]** **`mqtt_client.py` vive en `mqtt/` pero hace `django.setup()` con `backend.settings`** y su README manda ejecutarlo como `python cocina/mqtt_client.py` desde otro directorio (`Backend_cocina/`) que no existe en la estructura actual. Con la estructura de repos separados no arranca sin ajustar `PYTHONPATH`. Además no está integrado como proceso del servidor.
- **A5. [CORREGIDO Fase 1: pin 23] Conflicto de pines en firmware:** `BUZZER_PIN 21` coincide con SDA del I2C por defecto del ESP32 (el propio código lo comenta como "OJO"). El LCD y el buzzer se interferirían.
- **A6. Autenticación/transporte MQTT:** broker con `allow_anonymous true`, sin TLS; credenciales WiFi/IP en claro en el .ino (placeholders). Aceptable en desarrollo, no para validar seguridad.

### Medios
- M1. `lcd.clear()` cada 50 ms en el loop → parpadeo. **[E] 200 clears/10 s; CORREGIDO en Fase 1 (falta verlo en hardware).**
- M2. `analogWrite()` en ESP32 requiere core Arduino-ESP32 3.x; no documentado la versión requerida [S].
- M3. Firmware: tras `sensorError` publicaba 0 °C como dato válido y además contaminaba ΔT (pico espurio al recuperar: 9 vueltas con P3/P2 en la prueba). **[E] CORREGIDO en Fase 1** (`sensor_ok`, ΔT protegido).
- M4. **[No reproducido en simulación con σ=10 cuentas]** Firmware: `calcularDeltaT` usa ventana `HIST_N * dt` sobre 10 muestras de 50 ms (~0,5 s) → ΔT/s ruidoso con ADC cuantizado; umbral 2 °C/s puede disparar P3 por ruido [S: validar con datos].
- M5. Firmware: P5 (presión+gas) se evalúa antes que P4 correctamente, pero P6/P7 usan `presAlta && !gasAlerta`; revisar casos de borde en fase 1 (tabla de verdad).
- M6. **[CORREGIDO 3A: CORS y ALLOWED_HOSTS salen de `.env`]** `ALLOWED_HOSTS` documentado como `*` en troubleshooting; CORS fijo en código (ignora `.env`); `CORS_ALLOWED_ORIGINS` no incluye la app/IP del ESP.
- M7. **[Parcial 3A: simplejwt ya se usa; `drf-yasg` sigue sin usarse]** `settings.py` declara "Django 6.0.5" en cabecera mientras requirements fija 5.2.7; `rest_framework_simplejwt` y `drf-yasg` instalados/pedidos pero sin endpoints de token ni documentación.
- M8. **[RESUELTO Fase 2: se quitó `django` de requirements de mqtt; se documenta que el código usa paho 1.x]** `paho-mqtt==1.6.1` fijado, API `mqtt.Client(client_id=…)` sin `CallbackAPIVersion` (válido solo en 1.x). `requirements.txt` de mqtt pide `django>=4.2` mientras el backend usa 5.2.7.
- M9. Web: URL base `http://localhost:8000/api` hardcodeada pese a existir `VITE_API_URL` en `.env.example`; `Dashboard.jsx` y `DashboardPage.jsx` duplicados (el primero sin uso en rutas); botón "Emergencia" sin acción; texto "Sistema Normal" y "Todos los parámetros… dentro de rangos" estáticos (no dependen del estado real) → **información de seguridad engañosa**. Umbrales de `AlertasPage` (35 °C, 450 ppm) distintos a los del firmware y el gas se rotula "ppm" sobre un valor raw.
- M10. **[Backend corregido 3A: `?limit=` funciona (LimitOffset, máx. 1000)]** Web: `obtenerLecturas(limit)` envía `limit`, que DRF PageNumberPagination ignora (devuelve 100 por página).
- M11. La app nunca se compiló según su README; el modo remoto no se ha probado.

- F1-1 (nuevo, Fase 1, Alto). Red bloqueante en firmware: `conectarWiFi()` hasta 15 s en `setup()` y `reconectarMQTT()` con 3 intentos + `delay(500)` en cada vuelta → con broker caído el control local quedaba sin atender hasta ~10 s por vuelta. **[E] CORREGIDO parcialmente** (sin delays, 1 intento/10 s); persiste ~3 s por intento por el timeout TCP de `connect()` (ABIERTO, requiere hardware/FreeRTOS).
- F1-2 (Medio) **[RESUELTO por decisión del usuario 2026-10-12: cerrar válvula y sonar ya; [E] T11]**. Con llama + T ≥ 60 °C + gas ≥ 10 % LEL, P3 espera 10 s: válvula abierta y buzzer mudo durante la confirmación (los ventiladores suben por temperatura). **[E]** No se modificó la lógica de seguridad.
- F1-3 (Medio) **[RESUELTO por decisión del usuario 2026-10-12: llama + NTC averiado = P3 inmediato; [E] T19/T20]**. Con falla del NTC y llama, `temperatura=0` solo permite P8 (sin aspersor ni válvula). Definir respuesta conservadora.

- F2-1 (nuevo, Alto, **[E] corregido**). El validador rechazaba temperaturas > 155 °C: justo las de un incendio severo (el firmware considera válido el NTC hasta 300 °C) se descartaban antes de guardarse. Rango ahora −55..300.
- F2-2 (nuevo, Alto, **[E] corregido**). Mensajes malformados (temperatura como texto, JSON que no es objeto, prioridad nula) lanzaban excepciones fuera de `try` en `on_message` y detendrían el suscriptor (paho 1.x relanza las excepciones del callback) → un solo mensaje basura tumbaba toda la ingesta. Ahora nunca propaga.
- F2-3 (nuevo, Medio, corregido). Sin validación de rangos/tipos en `gas_raw`, `presion_raw`, `v*_pct`, bool, topic ni tamaño (se aceptaba gas_raw=99999); `cocinas/#` aceptaba topics arbitrarios como `cocinas/a/b`.
- F2-4 (nuevo, Medio, **abierto**). El simulador no reproduce el firmware: intervalo fijo (el firmware usa 0,5/1/5 s según prioridad), `delta_t` constante por escenario, `confirmando` siempre falso y sin confirmación de 10 s, P8 sin escenario, P4 con 70 % fijo. Sirve para carga/UI, no para validar tiempos ni la lógica del firmware.
- F2-5 (nuevo, Medio, **abierto → Fase 3/6**). `ts` del ESP32 es `millis()` desde el arranque, no hora real; la hora de la lectura es la de recepción (`auto_now_add`). Si el ESP32 se desconecta y reenvía, o hay latencia, la referencia temporal es la de llegada. Criterio de aceptación "referencias temporales" pendiente.
- F2-6 (nuevo, Medio, **abierto, decisión humana**). Broker anónimo y sin TLS; el firmware no soporta usuario/contraseña. El cliente y el simulador ya aceptan `MQTT_USER/MQTT_PASSWORD`, pero cerrar el broker exige cambiar firmware (`connect(id,user,pass)`) y `mosquitto.conf` a la vez.

- F3-1 (nuevo, Medio, **corregido sin ejecutar**). `ModelViewSet` permitía borrar y modificar lecturas, y `POST /lecturas/` aceptaba datos falsos: pasó a solo lectura; la ingesta es únicamente por MQTT.
- F3-2 (nuevo, Medio, **corregido sin ejecutar**). Los datos históricos quedaban incompatibles con el contrato: la migración 0003 los conserva (`cocina_id="legado"`) y elimina `presion` (hPa, sin sentido para el potenciómetro).
- F3-3 (nuevo, Medio, **abierto → 3B**). SSE bajo WSGI síncrono ocupa un worker por cliente: se resolverá en 3B con sondeo acotado y documentando el límite (el prototipo no necesita ASGI).

- F3-4 (nuevo, Medio, **[E] corregido**). `servidor/cocina/` no tenía `__init__.py` (ya faltaba en el repo original): Django lo tolera, pero `manage.py test cocina` importaba `tests.py` como módulo suelto y fallaba con `ImportError: attempted relative import`. Detectado al ejecutar las pruebas en el entorno del usuario; añadido el archivo.
- F3-5 (nuevo, Bajo, **[E] corregido**). `?desde=` con fecha imposible (mes 13) lanzaba `ValueError` → 500 para un usuario autenticado; ahora responde 400 (cubierto por `test_filtro_desde`). Hallado por revisión de código.
- F3-6 (nuevo, Bajo, **abierto**). `psycopg2-binary`, `pillow`, `drf-yasg`, `gunicorn` y `whitenoise` están en `requirements.txt` sin uso comprobado; el usuario ejecuta Python 3.14, versión que Django 5.2.7 no declara como soportada oficialmente (funcionó en las pruebas). Revisar en Fase 6 al fijar el entorno reproducible.

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

**Fase 2 (repo mqtt):**
- `payload.py` (nuevo): validación estricta de tipos/rangos del contrato y conversión a campos de lectura; no lanza excepciones; estado = prioridad (≤ 17 caracteres); `confirmando` y `sensor_ok` son campos aparte (antes el prefijo `VERIFICANDO_` generaba estados de 29 caracteres).
- `mqtt_client.py`: `on_message` robusto, `guardar_lectura` con `close_old_connections()` (sobrevive a reinicios de la BD), Django diferido y `SERVIDOR_DIR` (A4), `OSError` genérico al conectar, `MQTT_USER/PASSWORD` opcional.
- `mqtt_simulator.py`: `sensor_ok`, import tardío de paho, auth opcional.
- Contrato en BD: campos canónicos del payload (`gas_raw, gas_pct, presion_raw, presion_pct, llama, v1_pct, v2_pct, v3_pct, valvula, aspersor, confirmando, sensor_ok, ts_esp32, cocina_id, estado_sistema…`). **El modelo Django aún no los tiene (Fase 3).**
- README de mqtt: instrucciones de ejecución, contrato, pruebas.

## 7. Pruebas ejecutadas
**Fase 1 — [E] en PC** (`esp32/test_host/run.sh`: compila el `.ino` real con stubs de la API Arduino y ejecuta 18 escenarios):
- Línea base (firmware original): 18 escenarios, **5 con fallo** (pin buzzer/SDA, ΔT tras falla de sensor + `sensor_ok`, reintentos MQTT en ráfaga, `setup()` 17 s sin WiFi, 200 `lcd.clear()`/10 s).
- Tras las correcciones: **0 fallos**, 1 caso `ABIERTO` (F1-1 residual). Tras las decisiones F1-2/F1-3: 20 escenarios, 0 fallos. Lógica P0–P8, confirmación 10 s, cadencia 0,5/1/5 s y claves del payload: OK.
- Limitaciones: stubs sin ADC/PWM reales ni tiempos de red reales; el toolchain ESP32/arduino-cli **no está disponible** en este entorno (sin acceso de red) → **compilación real pendiente**. Ruido de ΔT: con σ=10 cuentas (supuesto) no hubo falsos P3 → M4 **no reproducido**.
**Fase 2 — [E] en PC, sin broker/paho/Django reales** (no instalables aquí):
- Línea base (código original, con paho/Django/modelo simulados; los campos del modelo se leen de `models.py`): un payload válido del firmware **no se guardaba** (`TypeError`: 8 campos inexistentes); 3 mensajes malformados lanzaban excepción; 200 °C rechazado; `gas_raw=99999` aceptado; estado de 29 caracteres.
- Después: `python -m unittest test_offline -v` → **15 pruebas OK** (7 payloads reales generados por el firmware, malformados, topics, tamaño, simulador vs. tabla del README, `on_message` con BD que falla). Comprobación por mutación: con el rango antiguo (155 °C) y con el prefijo `VERIFICANDO_` las pruebas fallan, es decir, detectan esas regresiones.
- No ejecutado: `mqtt_test.py` (requiere Mosquitto), integración real con paho, escritura real en la BD.
Previstas en otras fases: compilación del firmware (arduino-cli, si es viable en el entorno), `manage.py check/makemigrations --check/test`, `mqtt_test.py` con mosquitto, `npm run lint && npm run build`, `./gradlew testDebugUnitTest` (probablemente no ejecutable aquí: requiere Android SDK; se registrará como limitación).

## 8. Decisiones técnicas
- D0. Las carpetas son repos independientes: los cambios se harán por repo y se documentarán aquí; no se crea repo raíz.
- D1 (propuesta, pendiente de ratificar en fase 3). Tomar el **payload MQTT del firmware actual** como contrato canónico de lectura (es el que ya usan MQTT, simulador, app y tests) y adaptar modelo/serializers/web a él, conservando compatibilidad con los campos antiguos solo si es barato.

- D1 (aplicada en `mqtt/payload.py`, **pendiente de ratificar en Fase 3**): la BD usará los nombres del payload (`gas_raw`, `llama`, `v1_pct`…). La web usa nombres antiguos (`nivel_gas`, `llama_detectada`, `ventilador_*`): el serializer de Fase 3 expondrá ambos o se actualizará la web. El cambio es local a `procesar_mensaje()` si se decide otra cosa.
- D2. Estado del sistema = prioridad; `confirmando` y `sensor_ok` separados (evita estados de 29 caracteres y facilita filtrar alertas).

- D8 (Fase 3A, confirmada al ejecutar las pruebas). El modelo `Lectura` usa los nombres del payload MQTT; la web los usará en la Fase 4 y los alias legados se eliminarán después.

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
| README mqtt vs firmware | El firmware NO envía `cocina_id`; se deduce del topic | README mqtt decía que `cocina_id` iba en el payload (**corregido en Fase 2**) | Código |
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
**Usuario:** (1) responder cómo se define el código de reconocimiento de alarmas (decisión de seguridad, bloquea 3B); (2) hacer commit y push de `servidor` con `cocina/__init__.py`, `views.py`, `tests.py` y `settings.py` (DEFAULT_AUTO_FIELD).
**Fase 3B:** modelo `Alarma` (una activa por cocina; creada por P0–P5; escalada si empeora; persiste hasta ser reconocida; código hasheado, límite de intentos, usuario y hora), `GET alarmas/`, `POST alarmas/{id}/reconocer/`, `GET stream/` (SSE con eventos `reading` y `alarm`) e integración con el suscriptor MQTT (crear/escalar alarmas al guardar cada lectura). Después Fase 4 (login en la web).

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

## 14. Fase 2 — cierre
Estado: **Validada parcialmente** (lógica probada con módulos simulados; falta broker, paho y BD reales).
| Pendiente | Tipo | Dónde |
|---|---|---|
| Ejecutar `mqtt_test.py` con Mosquitto y `mqtt_client.py` con paho 1.6.1 + Django | verificación (no instalable aquí) | usuario |
| Modelo con los campos del contrato (C1) | integración | Fase 3 |
| F2-4 simulador fiel al firmware | mejora | Fase 6 (si se necesita para pruebas de carga/latencia) |
| F2-5 referencia temporal | diseño | Fase 3/6 |
| F2-6 autenticación/TLS del broker + firmware | decisión humana | usuario |

## 15. Fase 3A — cierre
Estado: **Validada dentro del alcance comprobado.**
Evidencia (salida pegada por el usuario, 2026-10-15; Python 3.14, Django 5.2.7, SQLite): `makemigrations --check --dry-run` → sin cambios; `migrate` aplicó `0003_contrato_firmware` sin error; `manage.py test cocina -v 2` → **18 pruebas OK** (autenticación y límite de intentos de login, solo lectura, paginación y filtros, `ultimas`, alertas con `tipo/mensaje`, resumen, contrato con el payload del suscriptor MQTT, severidad igual a la app, filtro `desde`). La salida mostró además que una primera ejecución falló por F3-4 y se corrigió.
Cambios en `servidor/`: `cocina/models.py`, `migrations/0003_contrato_firmware.py`, `serializers.py`, `views.py`, `urls.py`, `pagination.py`, `admin.py`, `__init__.py` (nuevo), `backend/settings.py` (autenticación obligatoria, CORS/hosts por `.env`, throttling, `DEFAULT_AUTO_FIELD`), `.env.example`, `README.md`, `cocina/tests.py`.
**No comprobado (limitaciones):** migración 0003 con filas reales antiguas (solo se aplicó sobre BD vacía/de prueba; la conversión de estados y ventiladores no se ha visto con datos); PostgreSQL; servidor en ejecución atendiendo peticiones reales (las pruebas usan el cliente de DRF); CORS desde la web; rendimiento con muchas lecturas (índices añadidos pero sin medir).
| Pendiente | Tipo | Dónde |
|---|---|---|
| Probar migración 0003 con datos antiguos (copia de BD real o filas de ejemplo) | verificación | usuario / Fase 6 |
| Alarmas, reconocimiento y `stream/` (C3) | desarrollo | 3B |
| Login en la web (la API exige token) | integración | Fase 4 |
| Commit y push de `servidor` con los archivos nuevos | operación | usuario |
| Confirmar D3 (sin ingesta HTTP de lecturas) y D4 (todo endpoint autenticado) | decisión | usuario |
| F2-6: autenticación/TLS del broker MQTT (requiere cambiar firmware y `mosquitto.conf`) | decisión | usuario |

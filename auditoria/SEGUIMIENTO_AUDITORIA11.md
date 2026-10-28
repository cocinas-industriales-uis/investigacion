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
| 3B | Backend: alarmas con reconocimiento + `stream/` SSE | **Validada dentro del alcance comprobado** (ver sección 16) |
| 4 | Web (`pagina-web/`) | **Corregido, pendiente de validación** por el usuario (ver sección 18) |
| 5 | App móvil (`app-movil/`) | **Corregido, pendiente de validación** en Android (ver sección 19) |
| 6 | Integración extremo a extremo y trazabilidad | **En curso** (6.1 hecha; ver sección 20) |
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
**(Actualizado 2026-10-28)** Fase 6.1 hecha (sección 20). Siguiente: 6.2 entorno reproducible (Mosquitto + Django + simulador), 6.3 lista de pruebas físicas con criterios de aceptación, 6.4 quitar alias legados del backend (requiere confirmación del usuario). Usuario: seguir validando Fases 4 y 5 en su equipo y borrar `pagina-web/src/components/Dashboard.jsx` y `Alertas.jsx`.
**(Actualizado 2026-10-26)** Fase 5 entregada. Usuario: aplicar el zip, ejecutar `python manage.py test cocina` (esperado 57 OK), abrir `app-movil/` en Android Studio, compilar y probar en emulador/teléfono (sección 19). Siguiente: Fase 6 (integración extremo a extremo).
**(Actualizado 2026-10-22)** Fase 4 entregada: el usuario debe ejecutar en su equipo `npm install`, `npm run lint`, `npm test`, `npm run build` y probar `npm run dev` con el backend (ver sección 18). Siguiente: Fase 5 (app móvil).
**(Actualizado 2026-10-21)** 3B validada. Siguiente: Fase 4 (web). Usuario: fijar su código con un usuario existente (`createsuperuser` si no tiene), ratificar D9–D11 y subir los cambios.
**Usuario (3B):** copiar los archivos de `fase3b_alarmas.zip`, ejecutar `python manage.py migrate` y `python manage.py test cocina -v 2` (esperado: 50 pruebas OK), fijar un código (`fijar_codigo_reconocimiento <usuario>`), commit/push (submódulos primero, luego el repo externo) y ratificar D9–D11. **Siguiente fase: 4 (web).**
(Texto anterior, ya cumplido en 3B:)
**Usuario:** (1) responder cómo se define el código de reconocimiento de alarmas (decisión de seguridad, bloquea 3B); (2) hacer commit y push de `servidor` con `cocina/__init__.py`, `views.py`, `tests.py` y `settings.py` (DEFAULT_AUTO_FIELD).
**Fase 3B:** modelo `Alarma` (una activa por cocina; creada por P0–P5; escalada si empeora; persiste hasta ser reconocida; código hasheado, límite de intentos, usuario y hora), `GET alarmas/`, `POST alarmas/{id}/reconocer/`, `GET stream/` (SSE con eventos `reading` y `alarm`) e integración con el suscriptor MQTT (crear/escalar alarmas al guardar cada lectura). Después Fase 4 (login en la web).

## 8c. Decisiones provisionales de 3B (pendientes de ratificar por el usuario)
- D9. Código de reconocimiento: **personal por usuario**, solo hash, bloqueo tras 5 fallos (300 s), fijado con `manage.py fijar_codigo_reconocimiento`. El usuario no eligió entre las 3 opciones; se tomó la recomendada. Cambiarla afecta solo `cocina/alarmas.py` y el comando.
- D10. Una alarma se crea con la lectura **confirmada** (`confirmando=false`). Consecuencia: una P3 por temperatura aparece ~10 s después (lo que tarda el firmware en confirmar), aunque haya gas (esa parte ya actúa en el firmware por F1-2). Opción `ALARMA_CON_CONFIRMANDO=True` para alarmar de inmediato.
- D11. Una alarma reconocida no se reabre por la misma condición durante el episodio (60 s sin lecturas P0–P5 lo termina); una prioridad más grave abre otra.

## 8b. Decisiones del usuario
- 2026-10-28 · D10 ratificada (opción A): la alarma se crea cuando el firmware confirma la emergencia (`confirmando=false`); `ALARMA_CON_CONFIRMANDO` se queda en `False`. Sin cambios de código.
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

## 16. Fase 3B — cierre
Estado: **Validada dentro del alcance comprobado.**
Evidencia del usuario (2026-10-21, equipo propio, Arch Linux, venv): `makemigrations --check --dry-run` → «No changes detected»; `migrate` aplicó `cocina.0004_alarmas_y_codigos` sin error; `manage.py test cocina -v 2` → **«Ran 50 tests in 15.950s — OK»** (la salida completa se conserva para el anexo de pruebas de la investigación, sección final). `fijar_codigo_reconocimiento` con un usuario inexistente respondió el error esperado («No existe el usuario»); **no se ha comprobado aún con un usuario real** ni `test_integracion` en su equipo.
Evidencia en el entorno de auditoría (anterior):
Cambios: `servidor/cocina/{models.py (Alarma, CodigoReconocimiento), migrations/0004_alarmas_y_codigos.py, alarmas.py, stream.py, serializers.py, views.py, urls.py, admin.py, management/commands/fijar_codigo_reconocimiento.py, test_alarmas.py}`, `backend/settings.py` (RECON_*, ALARMA_*, STREAM_*, throttle `reconocer`), `mqtt/mqtt_client.py` (procesar_alarma tras guardar), `mqtt/test_offline.py` (+2), `mqtt/test_integracion.py` (nuevo), READMEs.
Evidencia (entorno de auditoría, Python 3.13, Django 5.2.7): `manage.py check` y `makemigrations --check` sin cambios; `test cocina` → **50 OK** (18 de 3A + 32 nuevas: umbrales P0–P5, P3 en confirmación, una activa por cocina incluso a nivel de BD, escalada, persistencia, episodios, contrato AlarmDto, reconocimiento, idempotencia, bloqueo y expiración, código ajeno, SSE); `test_offline` 17 OK; `test_integracion` 3 OK (payloads reales del firmware → `on_message` real → BD → alarma → API). Prueba en vivo con `runserver`: un cliente SSE con token recibió `reading` y `alarm` mientras el handler MQTT procesaba un payload de fuga de gas; `GET alarmas/` devolvió la alarma con el contrato de la app.
**No comprobado:** ejecución en la máquina del usuario; broker Mosquitto real y paho; PostgreSQL; concurrencia real (la unicidad se probó por restricción de BD, no con escrituras simultáneas); SSE con varios clientes o bajo gunicorn; la app contra este backend (Fase 5: la app trata 400/403 como código inválido pero **429 es nuevo** para ella).
| Hallazgo | Sev. | Estado |
|---|---|---|
| F3-3 SSE por sondeo = un hilo/worker por cliente (WSGI) | Medio | Documentado; válido para pocos clientes |
| F3-7 La app debe manejar 429 (bloqueo) y 403 «sin código asignado» | Medio | Fase 5 |
| F3-8 Alarma de P3 por temperatura llega ~10 s tarde (D10) | Bajo | Decisión del usuario |
| F3-9 `reconocida_por` guarda nombre en texto (auditoría simple) | Bajo | Aceptado |
| Pendientes previos: probar migración 0003 con datos antiguos; D3/D4; F2-6 (broker sin auth/TLS); F2-5 hora de referencia | — | Sin cambio |

## 17. Anexo para la investigación (registrar al final, Fase 7)
Pruebas con evidencia propia del usuario que deben incorporarse a la memoria/investigación: Fase 3A (18 pruebas OK, 2026-10-15) y Fase 3B (50 pruebas OK, 2026-10-21, `Ran 50 tests in 15.950s`). Fase 4: pendiente de que el usuario pegue la salida de `npm install/lint/test/build`. Fase 5: pendiente la salida de `python manage.py test cocina` (57) y de la compilación/pruebas en Android Studio. Cada fase siguiente añadirá su salida aquí.

## 18. Fase 4 — Web (`pagina-web/`)
Estado: **Corregido, pendiente de validación** (probado en el entorno de auditoría con sustitutos; falta `npm install/build/lint` reales en el equipo del usuario).
### Hallazgos (todos [V] por lectura del código)
| Id | Sev. | Hallazgo | Estado |
|---|---|---|---|
| F4-1 | Crítico | La web no tenía login; con la API autenticada (3A) todas las llamadas devolvían 401 | Corregido |
| F4-2 | Crítico | Estados antiguos (`GAS_DETECTADO`…) con `|| estadoInfo.NORMAL` por defecto: un estado desconocido (p. ej. `EMERGENCIA_GAS`) se mostraba como «Sistema Normal» | Corregido (severidad de la API; lo desconocido = «Sin datos») |
| F4-3 | Alto | Texto fijo «Sistema Normal» y «Todos los parámetros… dentro de los rangos» siempre visibles | Corregido (derivado de la lectura) |
| F4-4 | Alto | Gráficas tomaban `slice(-20)` de una lista ordenada de más nueva a más vieja: mostraban las lecturas MÁS ANTIGUAS | Corregido y probado |
| F4-5 | Alto | Sin cocina seleccionada: «última lectura» de cualquier cocina; gráficas mezclaban cocinas | Corregido (selector, `lecturas/ultimas/`, filtro `cocina_id`) |
| F4-6 | Alto | Sin indicación de datos obsoletos: si el ESP32 deja de reportar, la web seguía mostrando el último estado | Corregido (aviso a los 30 s: constante `STALE_S`) |
| F4-7 | Medio | Unidades incorrectas: gas en «ppm» (era `gas_raw`), presión en «hPa» (es % de escala), límites 35 °C / 450 ppm inventados | Corregido (% de escala ADC + raw y umbrales del firmware) |
| F4-8 | Medio | Alertas = lecturas (`lecturas/alertas/`), sin alarmas ni reconocimiento | Corregido (`alarmas/`, `reconocer`, evento `alarm`) |
| F4-9 | Medio | Botón «Emergencia» sin acción, «Configuraciones» y «Salida» falsos | Eliminados / «Cerrar sesión» real. **No se inventó una acción de emergencia** |
| F4-10 | Medio | `API_BASE_URL` fija (`localhost:8000`); `VITE_API_URL` documentada pero no usada | Corregido (`src/config.js`, proxy de Vite) |
| F4-11 | Medio | Sondeo cada 5 s en 3 páginas, sin stream | Corregido (stream SSE + respaldo por sondeo) |
| F4-12 | Bajo | `components/Dashboard.jsx` duplicado y sin uso; `crearLectura` (POST inexistente); `obtenerAlertusPorTipo`; «Industruales» | Eliminados/corregidos |
| F4-13 | Bajo | Historial: «Total» = tamaño de la muestra (100) y paginación en el cliente | Corregido (`count` y `limit/offset` del servidor) |
Descartado tras verificar: la cabecera `Cache-Control` de la web **no** rompía CORS (el backend la permite); se retiró igualmente por innecesaria.
### Pruebas ejecutadas (entorno de auditoría)
- `node --test src/test/*.test.js`: **11 pruebas OK** (severidad, obsolescencia, alarmas, orden de gráficas, analizador SSE, reconexión y 401 del stream).
- Todos los `.js/.jsx` compilan con esbuild; reglas básicas de eslint (`no-undef`, `no-unused-vars`…) sin errores.
- **Prueba en navegador (Chromium/Playwright) contra Django real** con lecturas inyectadas por el `on_message` real del suscriptor: **25/25 pasos OK** — redirección al login, error de credenciales, login/usuario/rol, sin datos ≠ normal, lectura en vivo por stream, alarma P1 en vivo, cabecera «Emergencia», contador e insignia, código malo/bueno, alarma reconocida con nombre, gráfica cronológica, historial con total del servidor, selector de 2 cocinas, caída y recuperación del servidor (Reconectando → En vivo), aviso de dato obsoleto a los 33 s, token adulterado → login, usuario sin código, cerrar sesión, sin errores de JavaScript.
### No comprobado (limitaciones)
- `npm install`, `npm run build`, `npm run lint` con las versiones reales (sin acceso a npm aquí): el navegador probó un empaquetado con esbuild en el que **`react-router-dom` y `recharts` fueron sustituidos por versiones mínimas** (axios y React sí eran los reales). Las gráficas reales de Recharts y el enrutador real no se han visto funcionar; la regla `react-hooks` del lint del proyecto no se pudo ejecutar.
- Navegadores distintos de Chromium, pantallas pequeñas, accesibilidad, CORS entre orígenes distintos (se usó proxy mismo origen), `localStorage` bloqueado.
- Muchas cocinas o lecturas (el stream consume un hilo del servidor por pestaña abierta: F3-3).
### Pendientes que dejó la Fase 4
| Pendiente | Tipo | Dónde |
|---|---|---|
| Ejecutar `npm install && npm run lint && npm test && npm run build` y `npm run dev` con el backend | validación | usuario |
| Quitar del backend los alias legados (`nivel_gas`, `llama_detectada`, `presion`, `ventilador_*`) ahora que la web no los usa — confirmar antes que la app móvil tampoco | limpieza | Fase 5 / backend |
| ¿La web debe tener algún control de emergencia? (el botón no hacía nada y se eliminó; cualquier acción hacia el hardware es decisión del usuario) | decisión | usuario |
| Gestión de usuarios y códigos solo por línea de comandos / admin de Django (sin pantalla en la web) | alcance | usuario |
| Despliegue de la web (HTTPS, `VITE_API_URL`, CORS_ALLOWED_ORIGINS) | operación | Fase 6 |

## 19. Fase 5 — App móvil (`app-movil/`)
Estado: **Corregido, pendiente de validación.** La app **no se ha compilado como app Android ni probado en dispositivo**.
### Hallazgos
| Id | Sev. | Hallazgo | Estado |
|---|---|---|---|
| F5-1 | Alto | Las lecturas del snapshot REST se marcaban como recibidas «ahora»: un dato de hace horas (ESP32 apagado) se veía como actual durante 15 s tras cada (re)conexión | Corregido (`timestamp` del servidor; sin hora válida = desactualizado) |
| F5-2 | Alto | 401 (el token dura 12 h, sin refresco) no se trataba: la app reintentaba para siempre mostrando «Reconectando» | Corregido (cierra la sesión; vuelve al login) |
| F5-3 | Alto | `sensor_ok` ignorado: con el sensor de temperatura averiado se mostraba una temperatura falsa (0.0 °C) | Corregido (`sensor_ok` en el DTO; «SENSOR AVERIADO») |
| F5-4 | Medio | 429 (bloqueo del servidor) y 403 «sin código asignado» se mostraban como «no se pudo contactar» / «código incorrecto» | Corregido (excepciones y mensajes propios; el backend añade `motivo` al 403) |
| F5-5 | Medio | Login con 429 mostraba «No se pudo iniciar sesión» | Corregido |
| F5-6 | Medio | Pasar a «servidor real» exigía editar `build.gradle.kts` | Corregido (`-PUSE_MOCK=false -PAPI_BASE_URL=...`) |
| F5-7 | Medio | Alarma de P3 por temperatura tarda ~10 s (el backend crea la alarma al confirmar, D10); sonido/pantalla completa dependen de la alarma | **Abierto — decisión del usuario (D10)** |
| F5-8 | Bajo | Cierre normal del stream (a los 30 min) cuenta como fallo y muestra «Reconectando» ~1 s | Aceptado |
| F5-9 | Bajo | Al cerrar sesión por 401 no se informa «sesión expirada» | Abierto (menor) |
| F5-10 | — | Release: `minify` sin comprobar reglas de ProGuard para Retrofit/serialization; sin FCM; sin pruebas instrumentadas | Abierto (ya documentado) |
Descartado tras verificar: los campos del contrato que usa la app (`cocina_id`, `gas_raw`…, `id` como texto, `inicio` con `Z`) coinciden con el backend; la app **no usa** los alias legados (`nivel_gas`…), igual que la web.
### Pruebas ejecutadas (entorno de auditoría)
- Compilador Kotlin 2.0.21 (el embebido en Gradle) sobre `domain/`, `util/`, `ViewModels` (sin la fábrica), `Dtos`, `ApiService` y `RemoteMonitoringRepository`, con sustitutos mínimos de Android/OkHttp/Retrofit: **compila sin errores**.
- JUnit 4.13.2: **15 pruebas OK** (5 de dominio existentes, 5 nuevas de frescura de datos, 5 de reconocimiento incluyendo bloqueo del servidor y usuario sin código).
- `servidor`: **57 pruebas OK** (50 previas + 7 de `test_contrato_app.py`, que validan contra respuestas reales de Django los esquemas de `ReadingDto`, `AlarmDto`, `UserDto`/login, los códigos 400/401/403/429, y los eventos del stream); `makemigrations --check` sin cambios.
### No comprobado
Compilación con Gradle/Android (Compose, `AppContainer`, servicios, actividades, Keystore), decodificación real con kotlinx.serialization (plugin no disponible aquí; el contrato se comprobó con esquemas que replican los DTO), OkHttp-SSE contra el servidor, ejecución en emulador/teléfono, sonido, vibración, notificaciones, pantalla de bloqueo, marcador, comportamiento con ahorro de batería. El `AppContainer` modificado y los cambios de `DashboardScreen` solo se revisaron a mano.
### Pendientes
| Pendiente | Tipo | Dónde |
|---|---|---|
| Compilar en Android Studio, ejecutar `./gradlew testDebugUnitTest` y probar en emulador contra el backend real (login, alarma, sonido, reconocer, 401 con token vencido) | validación | usuario |
| Ratificar D10 (alarma tras confirmar o inmediata: `ALARMA_CON_CONFIRMANDO`) | decisión | usuario |
| Quitar del backend los alias legados (`nivel_gas`, `llama_detectada`, `presion`, `ventilador_*`): ni la web ni la app los usan | limpieza | Fase 6 (con confirmación) |
| Push FCM, íconos, ProGuard, certificate pinning | alcance | usuario |

## 20. Fase 6 — Integración extremo a extremo
Estado: **En curso.** 6.1 hecha; 6.2–6.4 pendientes.
### 6.1 Tramo MQTT → BD → alarma → stream (entorno de auditoría, sin broker ni paho)
- Archivo modificado: `mqtt/test_integracion.py` (prueba nueva `test_stream_entrega_lectura_y_alarma_y_mide_latencia`).
- Verifica con payloads reales del firmware y el `on_message` real que un mensaje P1 produce, en el primer sondeo del stream, un evento `reading` y un evento `alarm` (estado ACTIVA).
- Medido [E]: procesar el mensaje (BD + alarma) ≈ 7 ms; hasta el evento SSE ≈ 9 ms. Peor caso adicional por sondeo del servidor: `STREAM_POLL_S` = 1 s. Latencia del servidor por tanto ≲ 1,01 s, sin contar WiFi/broker/red del cliente.
- Contexto del firmware: al escalar a P0–P3 se publica de inmediato; el intervalo normal es 5 s, 1 s en P4–P5 y 0,5 s en P0–P3 (`getIntervalo`).
- Pruebas: `mqtt/test_integracion.py` + `test_offline.py` = 21 OK; `servidor` 57 OK (re-ejecutadas hoy).
### No comprobado
Broker Mosquitto real, paho-mqtt, ESP32, latencia de red/WiFi, navegador y app contra el tramo completo, carga con varios clientes SSE.
### Pendiente
| Pendiente | Tipo |
|---|---|
| 6.2 Entorno reproducible (Mosquitto + Django + suscriptor + simulador) | Fase 6 |
| 6.3 Lista de pruebas físicas con criterios de aceptación | Fase 6 |
| 6.4 Quitar alias legados del backend (`nivel_gas`, `llama_detectada`, `presion`, `ventilador_*`) | Fase 6, con confirmación del usuario |
| Borrar `components/Dashboard.jsx` y `components/Alertas.jsx` (huérfanos) | usuario |
| Hardware definitivo (NTC/MQ-2/LCD vs DS18B20/MQ-6/OLED/relé) | decisión del usuario |

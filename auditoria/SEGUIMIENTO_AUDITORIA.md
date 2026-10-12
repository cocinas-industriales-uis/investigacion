# SEGUIMIENTO DE AUDITORÍA — Sistema IoT Cocinas Industriales UIS

> Archivo vivo. Se actualiza al cierre de cada fase. Para retomar: leer la sección 12 y el estado de las fases (sección 3).
> Convención: **[V]** verificado por lectura estática del código · **[S]** sospecha sin verificar · **[E]** verificado ejecutando.
> Última actualización: 2026-10-11 · Fase 0 (inventario) cerrada · Ninguna prueba ejecutada todavía.

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
| 1 | Firmware, hardware y adquisición de datos (`esp32/`) | Pendiente de revisión — **siguiente** |
| 2 | Contrato MQTT + suscriptor + simulador (`mqtt/`) | Pendiente |
| 3 | Backend Django (modelo, API, auth, alarmas, stream) | Pendiente |
| 4 | Web (`pagina-web/`) | Pendiente |
| 5 | App móvil (`app-movil/`) | Pendiente |
| 6 | Integración extremo a extremo y trazabilidad | Pendiente |
| 7 | Actualización de la investigación | Pendiente |

## 4. Archivos revisados / modificados
- Revisados (lectura): todos los fuentes de `esp32/`, `mqtt/` (cliente completo; simulador y test solo cabecera), `servidor/` (backend, cocina, requirements, .env.example), `pagina-web/` (api.js, páginas principales, componentes de lectura/ventiladores), `app-movil/` (README, build, manifest, AppContainer, capa remota), READMEs de todos los repos, PROTOTIPO.docx, listado_materiales.docx, textos de los 3 HTML, línea de tiempo (tramo final), troubleshooting_backend.md.
- No leídos aún (pendiente en su fase): resto de `mqtt_simulator.py`/`mqtt_test.py`, `Graficas.jsx`/`HistorialLecturas.jsx`/`HistorialPage.jsx`, UI y servicio Android, tests Android, Informe_Plataforma_Web (.docx), presentación PDF, notebooks.
- Modificados: **ninguno** (solo se creó este archivo).

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
- **A5. Conflicto de pines en firmware:** `BUZZER_PIN 21` coincide con SDA del I2C por defecto del ESP32 (el propio código lo comenta como "OJO"). El LCD y el buzzer se interferirían.
- **A6. Autenticación/transporte MQTT:** broker con `allow_anonymous true`, sin TLS; credenciales WiFi/IP en claro en el .ino (placeholders). Aceptable en desarrollo, no para validar seguridad.

### Medios
- M1. `lcd.clear()` cada 50 ms en el loop → parpadeo [S: confirmar en hardware].
- M2. `analogWrite()` en ESP32 requiere core Arduino-ESP32 3.x; no documentado la versión requerida [S].
- M3. Firmware: tras `sensorError` fuerza `temperatura = 0` y se publica 0 °C como dato válido (indistinguible de lectura real).
- M4. Firmware: `calcularDeltaT` usa ventana `HIST_N * dt` sobre 10 muestras de 50 ms (~0,5 s) → ΔT/s ruidoso con ADC cuantizado; umbral 2 °C/s puede disparar P3 por ruido [S: validar con datos].
- M5. Firmware: P5 (presión+gas) se evalúa antes que P4 correctamente, pero P6/P7 usan `presAlta && !gasAlerta`; revisar casos de borde en fase 1 (tabla de verdad).
- M6. `ALLOWED_HOSTS` documentado como `*` en troubleshooting; CORS fijo en código (ignora `.env`); `CORS_ALLOWED_ORIGINS` no incluye la app/IP del ESP.
- M7. `settings.py` declara "Django 6.0.5" en cabecera mientras requirements fija 5.2.7; `rest_framework_simplejwt` y `drf-yasg` instalados/pedidos pero sin endpoints de token ni documentación.
- M8. `paho-mqtt==1.6.1` fijado, API `mqtt.Client(client_id=…)` sin `CallbackAPIVersion` (válido solo en 1.x). `requirements.txt` de mqtt pide `django>=4.2` mientras el backend usa 5.2.7.
- M9. Web: URL base `http://localhost:8000/api` hardcodeada pese a existir `VITE_API_URL` en `.env.example`; `Dashboard.jsx` y `DashboardPage.jsx` duplicados (el primero sin uso en rutas); botón "Emergencia" sin acción; texto "Sistema Normal" y "Todos los parámetros… dentro de rangos" estáticos (no dependen del estado real) → **información de seguridad engañosa**. Umbrales de `AlertasPage` (35 °C, 450 ppm) distintos a los del firmware y el gas se rotula "ppm" sobre un valor raw.
- M10. Web: `obtenerLecturas(limit)` envía `limit`, que DRF PageNumberPagination ignora (devuelve 100 por página).
- M11. La app nunca se compiló según su README; el modo remoto no se ha probado.

### Bajos
- B1. Typo `obtenerAlertusPorTipo` en api.js; README de web menciona "datos de prueba automáticos" que no existen.
- B2. Nombre de archivo `cocina_esp32_1_.ino` vs. documentación que habla de `sceht.ino`; el `.ino` no está en carpeta homónima (Arduino IDE exige carpeta con el mismo nombre).
- B3. App `sensores/` de Django vacía y no instalada.
- B4. Sin `.gitignore` verificado para `db.sqlite3`/`.env` en todos los repos (revisar en fase 3).

## 6. Correcciones realizadas
Ninguna (fase de inventario).

## 7. Pruebas ejecutadas
Ninguna. Previstas por fase: compilación del firmware (arduino-cli, si es viable en el entorno), `manage.py check/makemigrations --check/test`, `mqtt_test.py` con mosquitto, `npm run lint && npm run build`, `./gradlew testDebugUnitTest` (probablemente no ejecutable aquí: requiere Android SDK; se registrará como limitación).

## 8. Decisiones técnicas
- D0. Las carpetas son repos independientes: los cambios se harán por repo y se documentarán aquí; no se crea repo raíz.
- D1 (propuesta, pendiente de ratificar en fase 3). Tomar el **payload MQTT del firmware actual** como contrato canónico de lectura (es el que ya usan MQTT, simulador, app y tests) y adaptar modelo/serializers/web a él, conservando compatibilidad con los campos antiguos solo si es barato.

## 9. Discrepancias código ↔ informes ↔ diagramas
| Tema | Código actual | Documentos | Prioridad documental |
|---|---|---|---|
| Transporte ESP32→servidor | MQTT únicamente | Línea de tiempo y README esp32: HTTP POST cada 5 s; MQTT "pendiente" | Código es más reciente |
| Placa | ESP32 DevKit (ADC 12 bits) | README esp32 y `wokwi_diagram.json`: Arduino Uno; PROTOTIPO: "ESP32 Vedikit v4" | Código/PROTOTIPO |
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
**Fase 1 — firmware:** (1) intentar compilar `cocina_esp32_1_.ino` con arduino-cli (core esp32 3.x + librerías) para obtener una línea base; (2) extraer la lógica de prioridades a una tabla de verdad y contrastarla con `Simulador_IoT_Cocinas_v3.html`; (3) resolver A5 (pin buzzer/SDA), M1 y M3 con cambios localizados; (4) actualizar README del firmware (placa, pines, payload, dependencias); (5) emitir informe A–G de la fase.

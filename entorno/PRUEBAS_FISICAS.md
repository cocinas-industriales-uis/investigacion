# Pruebas físicas con el ESP32 (Fase 6.3)

Las ejecutas tú: dependen del hardware. Marca cada una como **OK / FALLA / NO PROBADA** y anota la fecha y la observación.
**Seguridad:** usa fuentes de baja energía (encendedor a distancia, gas de encendedor sin llama para el MQ-2), en un lugar ventilado, con otra persona presente y un extintor a mano. Nunca pruebes con la instalación de gas real.

**Preparación:** firmware actual cargado; buzzer en **GPIO 23** (antes en 21, que es SDA del LCD); broker + servidor + suscriptor corriendo; web y app conectadas (`ALARMA_CON_CONFIRMANDO=False`, D10-A); usuario con código de reconocimiento. Los umbrales salen de `cocina_esp32_1_.ino` (ADC 12 bits, 0–4095).

| ID | Acción | Esperado en el ESP32 | Esperado en servidor / web / app | Criterio de aceptación |
|---|---|---|---|---|
| PF-01 | Arrancar con WiFi y broker disponibles | LCD muestra estado; conecta a WiFi y MQTT | Llega una lectura en ≤ 10 s; estado Normal/P9 | Aparece la lectura en web y app |
| PF-02 | Arrancar **sin WiFi** | `setup()` no queda bloqueado; reintenta cada 10 s | — | El LCD y los sensores funcionan sin red |
| PF-03 | Cortar y devolver el broker (30 s) | Reconecta (reintento 10 s) sin reiniciar | Web/app: aviso de dato obsoleto tras > 30 s sin lecturas y recuperación al volver | Sin reinicios; el aviso aparece y desaparece |
| PF-04 | Calentar el NTC (secador/agua tibia) de 20 a 60 °C | Ventilación proporcional; P7 | Lectura P7, severidad NORMAL; temperatura creciente coherente con un termómetro (±2 °C) | Error de temperatura ≤ 2 °C |
| PF-05 | Gas de encendedor (sin llama) hasta ADC ≥ 800 | P4 prealerta; publica cada 1 s | Severidad RIESGO; alarma si es P0–P5 confirmada | Cambio a P4 en ≤ 2 s |
| PF-06 | Gas hasta ADC ≥ 1640 | P1; **válvula cerrada** (LED rojo), ventilador de emergencia | Alarma "Fuga de gas crítica" ACTIVA en web y app | Válvula cierra al instante; alarma en ≤ 2 s; suena en la app |
| PF-07 | Presión (potenciómetro) a ADC ≥ 2786 | P6 | Severidad ADVERTENCIA; `presion_pct` ≈ 68 % o más | Coincide con la perilla (±5 %) |
| PF-08 | Llama (KY-026) sin gas, T < 60 °C | P8 | ADVERTENCIA, sin alarma | No abre alarma |
| PF-09 | Llama + T ≥ 60 °C sin gas | P3 con confirmación de 10 s (`confirmando=true`) | Tarjeta roja de inmediato; **alarma ≈ 10 s después** (D10-A) | Sin alarma antes de confirmar; alarma tras confirmar |
| PF-10 | Llama + T ≥ 60 °C + gas ≥ 10 % LEL | P3: válvula cerrada y buzzer ya (F1-2) | Alarma tras la confirmación | Válvula/buzzer en < 1 s |
| PF-11 | Llama + gas ≥ 1640 | P0; evacuar | Alarma P0 "Gas y llama simultáneos" | Alarma en ≤ 2 s |
| PF-12 | Desconectar el NTC | Publica `sensor_ok=false`; sin falsos P3 por ΔT al reconectar | Web/app: "SENSOR AVERIADO", no 0,0 °C | Ningún disparo falso al desconectar/reconectar |
| PF-13 | Buzzer + LCD a la vez | Buzzer suena sin corromper el LCD (I2C) | — | LCD legible mientras suena |
| PF-14 | Reconocer una alarma en web y en app | **No** cambia nada en el ESP32 | Alarma pasa a RECONOCIDA con el usuario; código malo → 403; 5 fallos → bloqueo 429 | El hardware no recibe órdenes |
| PF-15 | Token vencido / cerrar sesión en la app | — | La app vuelve al login | Sin "Reconectando" infinito |
| PF-16 | Mantener 2 clientes (web + app) 30 min | — | Reconexión automática del stream a los 30 min | Sin pérdida de alarmas |
| PF-17 | Medir latencia: de llama/gas al sonido en la app | — | Objetivo: ≤ 3 s en P0/P1 (≈ 0,5 s publicar + ≤ 1 s sondeo + red) | Anota el valor medido |
| PF-18 | Ruido del ΔT: calentar rápido el NTC con llama activa | Observar P3 por ΔT ≥ 2 °C/s | **Pendiente de verificar** si el cálculo sobre ~0,5 s da falsos disparos (M-ΔT del seguimiento) | Documenta cuántos disparos falsos hay en 10 min |

**Pendiente de decisión (no bloquea estas pruebas):** hardware definitivo. Las pruebas usan lo que corre el firmware (NTC, MQ-2, LCD 16×2, potenciómetro). Si el prototipo final usa DS18B20/MQ-6/OLED/relé/solenoide, hay que repetir PF-04 a PF-13.

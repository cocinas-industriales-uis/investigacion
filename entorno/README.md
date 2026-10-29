# Entorno reproducible (Fase 6.2)

Levanta Mosquitto, el servidor Django, el suscriptor MQTT, la web y, opcionalmente, el simulador. **No sustituye las pruebas con el ESP32 real** (`PRUEBAS_FISICAS.md`).

> Estado de validación: los archivos de esta carpeta **no se han ejecutado con Docker** (no había Docker en el entorno de auditoría). Lo que sí se ejecutó: el YAML se parsea y `prueba_humo.py` pasó contra un servidor Django real con lecturas inyectadas por el `on_message` real. Si algo falla al construir, es información útil: avísame con el mensaje.

## Opción A — Docker
```bash
cd investigacion/entorno
cp .env.example .env                      # SECRET_KEY y ALARMA_CON_CONFIRMANDO (False = decisión D10-A)
docker compose up -d --build              # mosquitto, servidor, suscriptor, web
docker compose exec servidor python manage.py createsuperuser
docker compose exec servidor python manage.py fijar_codigo_reconocimiento <usuario>   # código para reconocer alarmas
docker compose --profile sim up simulador # cocinas virtuales (otra terminal)
```
Web: http://localhost:5173 · API: http://localhost:8000/api/ · broker: `localhost:1883`.
La BD vive en el volumen `datos` (no toca tu `db.sqlite3`). Para parar: `docker compose down` (añade `-v` para borrar la BD).

## Opción B — sin Docker (Arch)
```bash
sudo pacman -S mosquitto && mosquitto -c investigacion/entorno/mosquitto.conf   # terminal 1
cd servidor && source venv/bin/activate && python manage.py migrate && python manage.py runserver   # terminal 2
cd mqtt && pip install -r requirements.txt && SERVIDOR_DIR=../servidor python mqtt_client.py        # terminal 3
cd mqtt && python mqtt_simulator.py --escenario gas_critico --cocina cocina_01 --intervalo 2        # terminal 4
cd pagina-web && npm install && npm run dev                                                          # terminal 5
```
(Si tu `mosquitto.conf` por defecto no deja conexiones anónimas, usa el de esta carpeta.)

## Prueba de humo (cliente → servidor)
Con tráfico en marcha (simulador o ESP32):
```bash
python investigacion/entorno/prueba_humo.py --usuario <usuario> --clave '<clave>' --segundos 60 --exigir-alarma
```
Comprueba login, stream SSE, llegada de lecturas y alarmas, y muestra el retardo servidor→cliente. Sale con 0 si todo bien.
Con el escenario `gas_critico` o `incendio_moderado` debe llegar al menos una alarma.

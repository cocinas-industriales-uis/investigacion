# Notas de depuración — backend Django

> El código del backend (`Backend_cocina/`) todavía no se ha agregado a este
> repositorio. Estas notas vienen de una sesión de depuración previa y quedan
> aquí para no perderlas; cuando se agregue el backend, esto se puede mover a
> su README o a un CONTRIBUTING.md.

## Problema 1 — ESP32 no podía conectarse (`ALLOWED_HOSTS`)

El backend rechazaba las peticiones del ESP32 porque su IP de hotspot no
estaba en `ALLOWED_HOSTS`.

En `Backend_cocina/.env`:

```
# Antes
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Después (desarrollo con hotspot, IP cambia)
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,*
```

Reiniciar con:

```bash
python manage.py runserver 0.0.0.0:8000
```

> `*` es válido para desarrollo local. Antes de exponer el backend en
> producción hay que reemplazarlo por la IP o el dominio real — dejarlo así
> públicamente acepta peticiones de cualquier origen.

## Problema 2 — `/api/dispositivos/1/ultima/` devolvía 404

Faltaba el `queryset` en el ViewSet. En `Backend_cocina/backend/settings.py`
(o el archivo de views correspondiente):

```python
class DispositivoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DispositivoResumenSerializer
    queryset = Dispositivo.objects.none()  # ← faltaba esta línea
```

## Problema 3 — `POST /api/ingesta/` devolvía 400

El ESP32 sí llegaba a conectar, pero el backend rechazaba el JSON por datos
fuera de rango o campos faltantes. Pendiente de resolver: revisar en el
Serial Monitor del Arduino IDE la respuesta completa del backend
(`Respuesta backend: ...`) para identificar qué campo específico falla.

## Pendiente — ruta "Historial" en el frontend

Quedó sin resolver: acceso a la ruta de historial fallaba. Falta precisar si
era pantalla en blanco, error del navegador, "API Desconectada", o redirección
al login, y revisar la consola del navegador (F12) para el error exacto.

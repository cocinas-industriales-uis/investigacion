#!/usr/bin/env python3
"""Prueba de humo del tramo servidor → cliente (solo biblioteca estándar).

Entra con usuario y contraseña, abre el stream SSE y espera lecturas y alarmas. Para cada evento muestra el
retardo entre la hora de recepción en el servidor (`timestamp`) y el momento en que llega a este cliente.
Genera tráfico en otra terminal: `docker compose --profile sim up simulador` o el ESP32.

    python prueba_humo.py --usuario admin --clave '...' [--api http://localhost:8000/api] [--segundos 60]
        [--exigir-alarma]    # falla si no llega ninguna alarma
Salida 0 = OK, 1 = falló alguna comprobación.
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime


def _json(req, timeout=10):
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default="http://localhost:8000/api")
    ap.add_argument("--usuario", required=True)
    ap.add_argument("--clave", required=True)
    ap.add_argument("--segundos", type=int, default=60)
    ap.add_argument("--exigir-alarma", action="store_true")
    a = ap.parse_args()
    api = a.api.rstrip("/")

    try:
        body = json.dumps({"username": a.usuario, "password": a.clave}).encode()
        tok = _json(urllib.request.Request(api + "/auth/login/", body, {"Content-Type": "application/json"}))["access"]
    except (urllib.error.URLError, KeyError) as e:
        print(f"FALLO login: {e}")
        return 1
    print("OK login")

    req = urllib.request.Request(api + "/stream/", headers={"Authorization": "Bearer " + tok, "Accept": "text/event-stream"})
    lecturas, alarmas, retardos = 0, 0, []
    fin = time.time() + a.segundos
    try:
        with urllib.request.urlopen(req, timeout=a.segundos + 5) as r:
            evento = None
            while time.time() < fin:
                linea = r.readline().decode("utf-8").rstrip("\n")
                if linea.startswith("event:"):
                    evento = linea[6:].strip()
                elif linea.startswith("data:") and evento in ("reading", "alarm"):
                    datos = json.loads(linea[5:].strip())
                    if evento == "reading":
                        lecturas += 1
                        t = datetime.fromisoformat(datos["timestamp"].replace("Z", "+00:00"))
                        retardos.append(time.time() - t.timestamp())
                        if datos.get("prioridad", 9) <= 5:
                            print(f"  lectura {datos['cocina_id']} P{datos['prioridad']} {datos['severidad']}")
                    else:
                        alarmas += 1
                        print(f"  alarma #{datos['id']} {datos['cocina_id']} {datos['tipo']} {datos['estado']}")
    except (OSError, urllib.error.URLError) as e:
        if lecturas == 0:
            print(f"FALLO stream: {e}")
            return 1
    ok = lecturas > 0 and (alarmas > 0 or not a.exigir_alarma)
    print(f"\nlecturas: {lecturas}  alarmas: {alarmas}")
    if retardos:
        retardos.sort()
        print(f"retardo servidor→cliente: mediana {retardos[len(retardos)//2]*1000:.0f} ms, máx {retardos[-1]*1000:.0f} ms "
              "(incluye hasta 1 s de sondeo; supone relojes sincronizados)")
    print("RESULTADO:", "OK" if ok else "FALLÓ (no llegaron lecturas" + (" / alarmas)" if a.exigir_alarma else ")"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

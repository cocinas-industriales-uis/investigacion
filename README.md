# 📊 Investigación — Sistema IoT de Seguridad para Cocinas Industriales

<div align="center">

![Estado](https://img.shields.io/badge/estado-en%20progreso-yellow?style=flat-square)
![UIS](https://img.shields.io/badge/UIS-Proyecto%20de%20Grado-67B93E?style=flat-square)
![Python](https://img.shields.io/badge/análisis-Python%20%2B%20Jupyter-3776AB?style=flat-square)

Repositorio de investigación, análisis estadístico, documentación técnica
y planeación del proyecto de grado.<br>
Universidad Industrial de Santander (UIS) · 2025–2026

[Organización](https://github.com/cocinas-industriales-uis) ·
[Firmware](https://github.com/cocinas-industriales-uis/esp32) ·
[Servidor](https://github.com/cocinas-industriales-uis/servidor) ·
[Página web](https://github.com/cocinas-industriales-uis/pagina-web)

</div>

---

## Contenido del repositorio

```
investigacion/
│
├── analisis/
│   ├── datos/
│   │   ├── estadisticas_riesgos_laborales_positiva_2026.csv
│   │   └── osb_saludmental-tipodeaccidente.csv
│   └── notebooks/
│       ├── Justificacion_Estadistica_Cocinas_IoT.ipynb   ← notebook principal
│       ├── HTMLS.ipynb
│       └── historial/
│           ├── v1.ipynb
│           ├── v2.ipynb
│           └── exploracion_untitled2.ipynb
│
├── docs/
│   ├── diagramas/
│   │   ├── diagrama_prioridades.html     ← lógica de prioridades interactiva
│   │   ├── logica_prioridades_cocina.html
│   │   └── simulador_cocina.html         ← simulador del sistema sin hardware
│   ├── informes/
│   │   ├── Informe_Plataforma_Web_Seguridad_Cocinas_IoT.docx
│   │   ├── PROTOTIPO.docx / .pdf
│   │   └── listado_materiales.docx
│   ├── presentacion/
│   │   └── presentacion_sustentacion.pdf
│   └── justificacion_estadistica_incendios.md
│
├── referencias/
│   └── estado_del_arte.md
│
└── planeacion/
    ├── Proyecto-Cocinas.docx               ← propuesta formal del proyecto
    ├── guia_planeacion_trabajo_de_grado.docx
    └── linea_del_tiempo_proyecto.md        ← evolución del proyecto
```

---

## Análisis estadístico

El análisis estadístico justifica la necesidad del sistema a partir de
datos reales de accidentalidad en Colombia y casos documentados en prensa.

### Métodos utilizados

**Regresión binomial negativa**
Aplicada para modelar la frecuencia de accidentes laborales cuando la
varianza supera a la media (sobredispersión), lo cual es común en datos
de incidentalidad. Permite estimar la tasa esperada de eventos según
las variables del entorno.

**Prueba de tendencia Mann-Kendall**
Prueba no paramétrica aplicada sobre series temporales de accidentalidad
para detectar tendencias crecientes o decrecientes estadísticamente
significativas, independiente de la distribución de los datos.

### Datasets utilizados

| Dataset | Fuente | Contenido |
|---|---|---|
| `estadisticas_riesgos_laborales_positiva_2026.csv` | Positiva ARL | Estadísticas de accidentalidad laboral Colombia 2026 |
| `osb_saludmental-tipodeaccidente.csv` | OSB | Accidentes por tipo en entornos laborales |

### Notebook principal

`Justificacion_Estadistica_Cocinas_IoT.ipynb` contiene el análisis
completo listo para reproducir. Para ejecutarlo:

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install jupyter pandas numpy scipy matplotlib seaborn pymannkendall statsmodels

# Abrir el notebook
jupyter notebook analisis/notebooks/Justificacion_Estadistica_Cocinas_IoT.ipynb
```

---

## Justificación estadística — datos clave

### Datos verificados Colombia

| Fuente | Dato | Relevancia |
|---|---|---|
| Bomberos Bucaramanga 2024 | 1.653 emergencias — 179 incendios estructurales (10,83%) | Evidencia magnitud local |
| Bomberos Bogotá, Puente Aranda 2014–2021 | 303 incendios estructurales; calor y llama: 16–29% de causas | Causas en cocinas industriales y comerciales |

### Casos documentados en prensa

- **Bucaramanga, mayo 2019** — Incendio por recalentamiento de extractor
  en restaurante. 11 unidades bomberiles, 1 lesionado, ~$100M en pérdidas.
  *(Vanguardia)*
- **Envigado, octubre 2025** — Incendio originado en cocina; posible fuga
  en pipeta de gas y acumulación. 1 lesionado. *(El Colombiano)*
- **Bogotá, febrero 2026** — Incendio en ductos de extracción de
  restaurante; requirió ventilación mecánica. *(Infobae / Bomberos Bogotá)*

Los tres casos comparten la misma causa raíz: falla en el monitoreo
de temperatura, gas y ventilación en cocinas industriales.

---

## Estado del arte — papers base

> Los PDFs no se incluyen en el repositorio por derechos de autor.
> Las referencias completas y enlaces de acceso están en
> `referencias/estado_del_arte.md`.

| Autor(es) | Año | Aporte al proyecto |
|---|---|---|
| Hsu, Jhuang, Huang, Liang & Shiau | 2019 | Arquitectura base: sensor + microcontrolador + alarma en cocina |
| Kweon, Park, Park, Yoo & Ha | 2022 | Sistema inalámbrico con sensor electroquímico CO₂ |
| Kodali et al. | 2018 | Sensores MQ-6/MQ-4/MQ-135 con ESP32 — antecedente directo del hardware |
| Yépez & Ko | 2020 | Registro verificable de eventos de riesgo vía blockchain |
| Mensch et al. | 2021 | 16 sensores, 60 experimentos en cocina simulada (NIST) |
| Maltezos et al. | 2022 | Temperatura + humo + llama + gas con ESP32; 32 ms de latencia |
| Jena et al. | 2023 | Detección IoT de fugas de GLP con alarma y ventilación automática |
| Chrysafiadi & Tsichrintzi | 2025 | Arquitectura con lógica difusa para clasificación de riesgo |

---

## Simuladores y diagramas interactivos

En `docs/diagramas/` hay tres archivos HTML que se pueden abrir
directamente en el navegador sin instalar nada:

| Archivo | Descripción |
|---|---|
| `simulador_cocina.html` | Simulador completo con sliders de sensores, ventiladores animados y LCD virtual |
| `diagrama_prioridades.html` | Diagrama interactivo de la lógica de prioridades P1–P4 |
| `logica_prioridades_cocina.html` | Versión alternativa del diagrama con tooltips |

```bash
# Abrir en el navegador desde terminal
xdg-open docs/diagramas/simulador_cocina.html
```

---

## Documentación del sistema

| Documento | Ubicación | Contenido |
|---|---|---|
| Propuesta formal | `planeacion/Proyecto-Cocinas.docx` | Objetivos, alcance, arquitectura del sistema completo |
| Informe plataforma web | `docs/informes/Informe_Plataforma_Web_Seguridad_Cocinas_IoT.docx` | Documentación del backend y frontend |
| Prototipo | `docs/informes/PROTOTIPO.docx` / `.pdf` | Documentación del prototipo físico |
| Listado de materiales | `docs/informes/listado_materiales.docx` | BOM del hardware |
| Presentación sustentación | `docs/presentacion/presentacion_sustentacion.pdf` | Slides de presentación |
| Justificación estadística | `docs/justificacion_estadistica_incendios.md` | Datos y casos documentados |
| Línea del tiempo | `planeacion/linea_del_tiempo_proyecto.md` | Evolución del proyecto desde su origen |
| Guía de planeación | `planeacion/guia_planeacion_trabajo_de_grado.docx` | Estructura del libro y checklist de avance |

---

## Evolución del proyecto

El proyecto ha pasado por cuatro versiones desde su origen en la materia
de Microcontroladores (2026):

| Versión | Idea central | Cambio que la motivó |
|---|---|---|
| v1 | Llamar a bomberos automáticamente | Idea original en Microcontroladores |
| v2 | Alertar al responsable vía Twilio/WhatsApp | Implicaciones legales de llamar directamente |
| v3 | App Android propia con alarma de audio | Accesibilidad y control del canal de notificación |
| v4 | Plataforma IoT integrada a Smart Campus UIS | Ampliar el alcance a monitoreo distribuido y envío masivo de datos |

Detalle completo en `planeacion/linea_del_tiempo_proyecto.md`.

---

## División de trabajo

| Integrante | Rol |
|---|---|
| **Cesar Daniel Ávila Barbosa** (2224642) | Implementación práctica: firmware, backend, frontend, infraestructura |
| **Carlos (Cayalam)** | Investigación: estado del arte, análisis estadístico, documentación académica |

---

## Checklist de investigación

- [x] Identificación del problema y casos reales documentados
- [x] Revisión de 8 papers del área (2018–2025)
- [x] Datasets de accidentalidad recopilados (Positiva, OSB)
- [x] Datos de Bomberos Bucaramanga y Bogotá verificados
- [x] Análisis estadístico (regresión binomial negativa + Mann-Kendall)
- [x] Propuesta formal redactada con objetivos y arquitectura
- [ ] Búsqueda de papers adicionales en IEEE Xplore y Scopus
- [ ] Verificación de cada referencia con DOI antes de citar en el libro
- [ ] Protocolo de pruebas del sistema definido
- [ ] Resultados de pruebas documentados
- [ ] Borrador del libro revisado por el director

---

<div align="center">
  <sub>Proyecto de grado · UIS · 2025–2026 · Cesar Daniel Ávila Barbosa</sub>
</div>

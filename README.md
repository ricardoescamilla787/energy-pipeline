# Pipeline de Nuclear Outages

Pipeline de datos que extrae información de Nuclear Outages de EE.UU. desde la API abierta de EIA, la almacena en archivos Parquet, la expone mediante una API REST y la presenta en un dashboard web interactivo.

---

## Descripción general

Este proyecto implementa un pipeline completo de datos en 4 partes:

- **Part 1 — Conector de datos**: extrae el dataset de U.S. Nuclear Outages desde la API de EIA con paginación automática, validación y extracción incremental
- **Part 2 — Modelo de datos**: estructura los datos en 2 tablas (`outages` y `outage_stats`) guardadas en archivos Parquet
- **Part 3 — API REST**: expone los datos mediante 3 endpoints construidos con Flask
- **Part 4 — Dashboard web**: interfaz que consume la API y presenta los datos con filtros, ordenamiento y paginación

El sistema funciona en dos modos — **local** sin configuración extra, y **nube** usando Railway + Supabase.

---

## Demo en producción

API desplegada en Railway:

```
GET  https://web-production-43799.up.railway.app/data
GET  https://web-production-43799.up.railway.app/stats
POST https://web-production-43799.up.railway.app/refresh
```

---

## Requisitos previos

- Python 3.11 o superior
- pip
- Git
- Clave de API de EIA
- Cuenta en Supabase (solo para despliegue en la nube)
- Cuenta en Railway (solo para despliegue en la nube)

---

## Tecnologías utilizadas

- **Python** — lenguaje principal
- **pandas** — manipulación y transformación de datos
- **Parquet** — almacenamiento eficiente de datos
- **Flask** — servidor de la API REST
- **Gunicorn** — servidor WSGI para producción
- **pytest** — tests automatizados
- **HTML / CSS / JavaScript** — dashboard web
- **Supabase Storage** — almacenamiento persistente de Parquets en la nube
- **Railway** — despliegue del API en la nube

---

## Estructura del proyecto

```
challenge_energy/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py           # claves, rutas y constantes
│   │   ├── model.py            # construcción de tablas del modelo de datos
│   │   │
│   │   ├── services/
│   │   │   ├── extractor.py    # extracción paginada desde la API de EIA
│   │   │   ├── validator.py    # validación de campos requeridos
│   │   │   ├── transformer.py  # limpieza y agregación de datos
│   │   │   ├── storage.py      # lectura y escritura local y en Supabase
│   │   │   └── pipeline.py     # orquestador del pipeline completo
│   │   │
│   │   └── utils/
│   │       ├── http_client.py  # peticiones HTTP con reintentos
│   │       └── logger.py       # configuración del logger
│   │
│   ├── tests/
│   │   ├── test_connector.py   # tests del pipeline y extractor
│   │   ├── test_parquet.py     # tests del modelo de datos
│   │   └── test_api.py         # tests de los endpoints del API
│   │
│   ├── data/                   # archivos Parquet locales 
│   │
│   ├── api.py                  # API REST con Flask
│   ├── run.py                  # punto de entrada del pipeline
│   ├── schema.sql              # esquema de referencia para MySQL
│   └── pipeline.log            # log de ejecuciones 
│
├── frontend/
│   ├── templates/
│   │   └── index.html          # dashboard web
│   └── static/
│       ├── css/styles.css
│       └── js/app.js
│
├── er_diagram.svg              # diagrama entidad-relación
├── Procfile                    # configuración de arranque para Railway
├── .env                        # variables de entorno
├── .env.example                # plantilla del archivo .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Configuración de variables de entorno

Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

Abre `.env` y configura los valores:

```
# Clave de la API de EIA — obligatoria siempre
# Obtén una gratis en: https://www.eia.gov/opendata/
EIA_API_KEY=tu_clave_de_eia

# Credenciales de Supabase — solo necesarias para modo nube
# Obtén estos valores en: Supabase → Settings → API Keys
SUPABASE_URL=https://pfawamnrwofutlrrnjff.supabase.co el sistema corre en modo local guardando los Parquets en `backend/data/`.

---

## Inicio rápido — modo local

### 1. Clonar el repositorio

```bash
git clone https://github.com/ricardoescamilla787/energy-pipeline.git
cd challenge_energy
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar el pipeline

```bash
cd backend
python run.py
```

Descarga los datos históricos desde la API de EIA (2007–hoy) y genera los archivos Parquet en `backend/data/`.

### 4. Iniciar el API

Abre una nueva terminal:

```bash
cd backend
python api.py
```

El API queda disponible en `http://localhost:5000`.

### 5. Abrir el dashboard

Abre `frontend/templates/index.html` en tu navegador. En Windows:

```bash
start frontend/templates/index.html
```

### 6. Ejecutar los tests

```bash
cd backend
pytest tests/ -v
```

---

## Despliegue en la nube

El sistema usa **Railway** para el API y **Supabase** para el almacenamiento de los Parquets.

### Requisitos previos

- Cuenta en [Railway](https://railway.app) conectada a GitHub
- Proyecto en [Supabase](https://supabase.com) con un bucket llamado `parquet-data`

### 1. Configurar Supabase

1. Crea un proyecto en Supabase
2. Ve a **Storage** y crea un bucket llamado `parquet-data`
3. Ve a **Settings → API Keys → Legacy anon, service_role API keys**
4. Copia la `service_role` key y la `Project URL`

### 2. Desplegar en Railway

1. Ve a [railway.app](https://railway.app) y crea un nuevo proyecto
2. Selecciona **Deploy from GitHub repo**
3. Selecciona el repositorio `energy-pipeline` (nombre en GitHub)
4. En **Variables** agrega:

```
EIA_API_KEY=tu_clave_de_eia
SUPABASE_URL=https://pfawamnrwofutlrrnjff.supabase.co
SUPABASE_KEY=tu_service_role_key
```

5. Railway detecta el `Procfile` y despliega automáticamente
6. URL pública del proyecto: `https://web-production-43799.up.railway.app`

### 3. Cargar los datos iniciales

Una vez desplegado llama al endpoint `/refresh` para cargar los datos:

```bash
curl -X POST https://web-production-43799.up.railway.app/refresh
```

### 4. Actualizar el frontend para producción

En `frontend/static/js/app.js` cambia la URL del API:

```javascript
// Local
const API_BASE = "http://localhost:5000"

// Nube
const API_BASE = "https://web-production-43799.up.railway.app"
```

---

## Endpoints del API

### GET /data

Devuelve los registros de interrupciones paginados y filtrados.

| Parámetro  | Tipo   | Default | Descripción                       |
|------------|--------|---------|-----------------------------------|
| date_from  | string | —       | Filtrar desde fecha (YYYY-MM-DD)  |
| date_to    | string | —       | Filtrar hasta fecha (YYYY-MM-DD)  |
| min_outage | float  | —       | Mínimo de MW fuera de servicio    |
| page       | int    | 1       | Número de página                  |
| limit      | int    | 50      | Registros por página (máximo 500) |

**Ejemplo de petición:**
```
GET https://web-production-43799.up.railway.app/data?date_from=2024-01-01&date_to=2024-12-31&limit=25&page=1
```

**Ejemplo de respuesta:**
```json
{
  "status": "ok",
  "total": 366,
  "page": 1,
  "pages": 15,
  "limit": 25,
  "data": [
    {
      "period": "2024-12-31",
      "capacity": 100013.0,
      "outage": 7430.0,
      "percent_outage": 7.43
    }
  ]
}
```

---

### POST /refresh

Dispara el pipeline de extracción incremental desde la API de EIA.

**Ejemplo de respuesta exitosa:**
```json
{
  "status": "ok",
  "pipeline": {
    "status": "success",
    "records": 1,
    "period_from": "2026-03-21",
    "period_to": "2026-03-21"
  }
}
```

**Ejemplo de respuesta cuando ya está actualizado:**
```json
{
  "status": "ok",
  "pipeline": {
    "status": "up_to_date",
    "records": 0
  }
}
```

---

### GET /stats

Devuelve las estadísticas anuales precalculadas.

**Ejemplo de respuesta:**
```json
{
  "status": "ok",
  "data": [
    {
      "year": 2024,
      "avg_outage_mw": 8234.5,
      "avg_percent_outage": 8.23,
      "max_outage_mw": 18450.0,
      "min_outage_mw": 1200.0,
      "total_records": 366
    }
  ]
}
```

---

## Modelo de datos

El modelo tiene 2 tablas guardadas como archivos Parquet. Ver `schema.sql` y `er_diagram.svg` para el esquema completo y las relaciones.

**`outages`** — un registro por día

| Columna        | Tipo    | Descripción                         |
|----------------|---------|-------------------------------------|
| period         | date    | Fecha del registro (clave primaria) |
| capacity       | decimal | Capacidad total instalada (MW)      |
| outage         | decimal | Capacidad fuera de servicio (MW)    |
| percent_outage | decimal | Porcentaje fuera de servicio        |
| ingested_at    | datetime| Fecha y hora de ingesta             |

**`outage_stats`** — un registro por año (agregados precalculados)

| Columna            | Tipo    | Descripción                      |
|--------------------|---------|----------------------------------|
| year               | int     | Año (clave primaria)             |
| avg_outage_mw      | decimal | Promedio diario de MW            |
| avg_percent_outage | decimal | Promedio de % fuera de servicio  |
| max_outage_mw      | decimal | Máximo diario del año (MW)       |
| min_outage_mw      | decimal | Mínimo diario del año (MW)       |
| total_records      | int     | Número de registros del año      |

---

## Supuestos asumidos

- La API de EIA publica un registro diario por el total de la flota nuclear de EE.UU.
- El campo `period` se usa como clave primaria natural — la API garantiza un registro único por día.
- La extracción incremental se basa en el último `period` guardado — en ejecuciones posteriores solo se descargan registros más recientes que el último guardado.
- Los datos históricos disponibles en la API comienzan desde 2007, no desde 2003 como indica el selector del dashboard de EIA.
- Se eligió el dataset de U.S. Nuclear Outages por ser el agregado nacional — responde directamente la pregunta del negocio sin la complejidad de los niveles facility o generator.
- El frontend se conecta a `http://localhost:5000` por defecto en modo local. En producción hay que actualizar `API_BASE` en `app.js`.
- En modo local los Parquets se guardan en `backend/data/`. En modo nube se guardan en Supabase Storage.

---

## Ejemplos de resultados

**Primera ejecución — descarga completa:**
```
2026-03-20 10:30:01 - INFO - Iniciando pipeline
2026-03-20 10:30:01 - INFO - Descargando registros desde offset=0
2026-03-20 10:30:03 - INFO - Descargando registros desde offset=5000
2026-03-20 10:30:04 - INFO - Paginación completa — 7019 registros extraídos
2026-03-20 10:30:04 - INFO - Validación OK — 7019 registros
2026-03-20 10:30:04 - INFO - Datos crudos guardados: 7019 registros
2026-03-20 10:30:04 - INFO - Estadísticas guardadas: 20 registros
2026-03-20 10:30:04 - INFO - Pipeline completado — 7019 registros nuevos procesados
```

**Segunda ejecución — extracción incremental:**
```
2026-03-21 08:00:00 - INFO - Iniciando pipeline
2026-03-21 08:00:02 - INFO - Paginación completa — 7020 registros extraídos
2026-03-21 08:00:02 - INFO - Registros nuevos después de 2026-03-20: 1
2026-03-21 08:00:02 - INFO - Pipeline completado — 1 registros nuevos procesados
```

**Tests:**
```
collected 20 items

tests/test_api.py::test_data_empty_when_no_parquet PASSED
tests/test_api.py::test_data_returns_records PASSED
tests/test_api.py::test_data_filter_by_date PASSED
tests/test_api.py::test_data_filter_by_min_outage PASSED
tests/test_api.py::test_data_pagination PASSED
tests/test_api.py::test_refresh_success PASSED
tests/test_api.py::test_refresh_returns_error_on_failure PASSED
tests/test_connector.py::test_fetch_raises_without_api_key PASSED
tests/test_connector.py::test_fetch_returns_records PASSED
tests/test_connector.py::test_fetch_paginates PASSED
tests/test_connector.py::test_raises_on_401 PASSED
tests/test_connector.py::test_retries_on_network_error PASSED
tests/test_connector.py::test_pipeline_success PASSED
tests/test_connector.py::test_pipeline_up_to_date PASSED
tests/test_parquet.py::test_outages_columns PASSED
tests/test_parquet.py::test_outages_no_duplicates PASSED
tests/test_parquet.py::test_outages_row_count PASSED
tests/test_parquet.py::test_stats_columns PASSED
tests/test_parquet.py::test_stats_years PASSED
tests/test_parquet.py::test_stats_total_records PASSED

20 passed in 3.26s
```

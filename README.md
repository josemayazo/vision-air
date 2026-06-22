# 📊 Dusty Monitor - API REST para Monitoreo Ambiental Escolar

API REST construida con **FastAPI** y **PostgreSQL** para un sistema IoT de monitoreo de calidad del aire en instituciones educativas.

## 📋 Características

✅ **Gestión de Dispositivos IoT** - Registro y control de sensores ESP32  
✅ **Almacenamiento de Lecturas** - Datos de sensores ambientales en tiempo real  
✅ **Alertas Automáticas** - Generación de alertas por contaminación  
✅ **Estadísticas** - Gráficos y análisis de calidad del aire  
✅ **Gamificación** - Sistema de misiones educativas  
✅ **Documentación Interactiva** - Swagger UI integrada  
✅ **Código Limpio** - Estructura modular y bien documentada  

---

## 🗂️ Estructura del Proyecto

```
vision_air_api/
├── app/
│   ├── __init__.py              # Inicialización de la app
│   ├── main.py                  # Configuración y setup de FastAPI
│   ├── config.py                # Configuración y variables de entorno
│   ├── database.py              # Conexión a PostgreSQL
│   ├── models.py                # Modelos SQLAlchemy (ORM)
│   ├── schemas.py               # Esquemas Pydantic (validación)
│   ├── crud.py                  # Operaciones CRUD reutilizables
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── dispositivos.py      # Endpoints: /api/v1/dispositivos
│   │   ├── lecturas.py          # Endpoints: /api/v1/lecturas
│   │   ├── alertas.py           # Endpoints: /api/v1/alertas
│   │   └── misiones.py          # Endpoints: /api/v1/misiones
│   └── utils/
│       ├── __init__.py
│       └── alerts.py            # Funciones de validación y alertas
├── migrations/
│   └── 001_initial_schema.sql   # Script SQL de base de datos
├── .env.example                 # Variables de entorno (plantilla)
├── .gitignore                   # Archivos a ignorar en Git
├── requirements.txt             # Dependencias Python
├── main.py                      # Punto de entrada
└── README.md                    # Este archivo
```

---

## 🚀 Instalación Rápida

### Requisitos Previos
- Python 3.10+
- PostgreSQL 12+
- pip o conda

### Paso 1: Clonar y Entrar al Directorio

```bash
cd c:\Users\jose_\Documents\projects\vision_air\vision_air_api
```

### Paso 2: Crear Entorno Virtual

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar Base de Datos

**Opción A: Con archivo .env**

```bash
# Crear archivo .env (copiar de .env.example)
cp .env.example .env

# Editar .env con tus credenciales de PostgreSQL
# DB_HOST=localhost
# DB_PORT=5432
# DB_USER=postgres
# DB_PASSWORD=tu_contraseña_aqui
# DB_NAME=dusty_monitor
```

**Opción B: Variables de Entorno del Sistema**

```bash
set DB_HOST=localhost
set DB_PORT=5432
set DB_USER=postgres
set DB_PASSWORD=tu_contraseña
set DB_NAME=dusty_monitor
```

### Paso 5: Crear Base de Datos

```sql
-- Conectarse a PostgreSQL como superusuario
psql -U postgres

-- Crear la base de datos
CREATE DATABASE dusty_monitor;

-- Salir
\q
```

### Paso 6: Ejecutar Migraciones SQL

```bash
# Conectarse a la BD y ejecutar el script
psql -U postgres -d dusty_monitor -f migrations\001_initial_schema.sql
```

### Paso 7: Ejecutar la API

```bash
# Con el script main.py
python main.py

# O con uvicorn directamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: **http://localhost:8000**

---

## 📚 Documentación Interactiva

Una vez que la API esté corriendo, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## 🔌 Endpoints Disponibles

### 🔧 Dispositivos
```
POST   /api/v1/dispositivos              - Crear dispositivo
GET    /api/v1/dispositivos              - Listar todos
GET    /api/v1/dispositivos/{id}         - Obtener dispositivo específico
```

### 📡 Lecturas
```
POST   /api/v1/lecturas                  - Registrar nueva lectura (desde ESP32)
GET    /api/v1/lecturas/actual           - Última lectura de un dispositivo
GET    /api/v1/lecturas/estadisticas     - Datos agrupados para gráficos
```

### ⚠️ Alertas
```
GET    /api/v1/alertas/recientes         - Alertas recientes no resueltas
GET    /api/v1/alertas/dispositivo/{id}  - Alertas de un dispositivo específico
PATCH  /api/v1/alertas/{id}/resolver     - Marcar alerta como resuelta
```

### 🎮 Misiones
```
GET    /api/v1/misiones                  - Listar misiones activas
GET    /api/v1/misiones/{id}             - Obtener misión específica
POST   /api/v1/misiones                  - Crear nueva misión
PATCH  /api/v1/misiones/{id}/progreso    - Actualizar progreso
```

---

## 📝 Ejemplos de Uso

### 1️⃣ Registrar un Dispositivo

```bash
curl -X POST "http://localhost:8000/api/v1/dispositivos" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "ESP32_AULA_1",
    "nombre": "Sensor Aula de Ciencias",
    "ubicacion": "Laboratorio de Biología",
    "limite_co2": 900,
    "limite_pm25": 25
  }'
```

### 2️⃣ Enviar Lectura desde ESP32

```bash
curl -X POST "http://localhost:8000/api/v1/lecturas" \
  -H "Content-Type: application/json" \
  -d '{
    "dispositivo_id": "ESP32_AULA_1",
    "temperatura": 22.5,
    "humedad": 55.3,
    "pm1_0": 5.2,
    "pm2_5": 12.4,
    "pm4_0": 18.7,
    "pm10": 24.3,
    "voc": 150,
    "co2": 850
  }'
```

### 3️⃣ Obtener Última Lectura

```bash
curl -X GET "http://localhost:8000/api/v1/lecturas/actual?dispositivo_id=ESP32_AULA_1"
```

### 4️⃣ Obtener Estadísticas

```bash
curl -X GET "http://localhost:8000/api/v1/lecturas/estadisticas?dispositivo_id=ESP32_AULA_1&filtro=hoy"
```

---

## 🔒 Seguridad en Producción

Cuando despliegues en producción:

1. **Cambiar credenciales** en `.env`
2. **Usar HTTPS** en lugar de HTTP
3. **Implementar autenticación** (JWT, OAuth2)
4. **Configurar CORS** adecuadamente
5. **Usar Gunicorn** en lugar de uvicorn en desarrollo
6. **Implementar rate limiting**
7. **Validar todas las entradas**

---

## 🐳 Deploy con Docker (Opcional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t dusty-monitor-api .
docker run -p 8000:8000 --env-file .env dusty-monitor-api
```

---

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app
```

---

## 📊 Modelo de Datos

### Tabla: dispositivos
```sql
id (PK)               VARCHAR(50)
nombre               VARCHAR(255)
ubicacion            VARCHAR(255)
limite_co2           INT (default: 900)
limite_pm25          INT (default: 25)
ultimo_contacto      TIMESTAMP WITH TIME ZONE
```

### Tabla: lecturas
```sql
id (PK, autoincremental)  BIGINT
dispositivo_id (FK)       VARCHAR(50)
fecha_hora                TIMESTAMP WITH TIME ZONE
temperatura               NUMERIC(4,2)
humedad                   NUMERIC(5,2)
pm1_0, pm2_5, pm4_0, pm10 NUMERIC(5,2)
voc                       INT
co2                       INT
```

### Tabla: historial_alertas
```sql
id (PK, autoincremental)  INT
dispositivo_id (FK)       VARCHAR(50)
fecha_hora                TIMESTAMP WITH TIME ZONE
variable_afectada         VARCHAR(50)
valor_detectado           NUMERIC(5,2)
nivel_critico             VARCHAR(10) [ALTA|MEDIA]
resuelto                  BOOLEAN (default: false)
```

### Tabla: misiones_usuario
```sql
id (PK, autoincremental)  INT
titulo                    VARCHAR(255)
categoria                 VARCHAR(100)
descripcion               TEXT
progreso                  INT (0-100)
activa                    BOOLEAN (default: true)
```

---

## 🛠️ Troubleshooting

### Error: "Could not connect to database"
- Verificar que PostgreSQL está corriendo
- Revisar credenciales en `.env`
- Confirmar que la BD existe: `psql -U postgres -l`

### Error: "ModuleNotFoundError"
- Activar el entorno virtual
- Reinstalar dependencias: `pip install -r requirements.txt`

### Error: "Port 8000 already in use"
- Cambiar puerto: `uvicorn app.main:app --port 8001`
- O matar el proceso: `lsof -i :8000` y `kill -9 <PID>`

---

## 📞 Contacto & Soporte

Para reportar problemas o sugerencias, contactar al equipo de desarrollo.

---

## 📄 Licencia

Este proyecto está bajo licencia MIT.

---

**Hecho con ❤️ para monitoreo ambiental escolar**

# 📐 Arquitectura de la API - Dusty Monitor

## 🏗️ Descripción General

Esta es una **API REST** de **nivel empresarial** construida con **FastAPI** que implementa un sistema IoT para monitoreo ambiental escolar.

### Stack Tecnológico

```
┌─────────────────────────────────────────────────────┐
│                    CLIENTE (Frontend/ESP32)         │
└──────────────────┬──────────────────────────────────┘
                   │
                   │ HTTP/REST
                   │ JSON
                   ▼
┌─────────────────────────────────────────────────────┐
│               FASTAPI (main.py)                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  Routers & Endpoints (/routers/)             │  │
│  │  ├─ dispositivos.py                          │  │
│  │  ├─ lecturas.py                              │  │
│  │  ├─ alertas.py                               │  │
│  │  └─ misiones.py                              │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │  CRUD Layer (crud.py)                        │  │
│  │  ├─ crear_dispositivo()                      │  │
│  │  ├─ obtener_ultima_lectura()                 │  │
│  │  ├─ crear_alerta()                           │  │
│  │  └─ actualizar_progreso_mision()             │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │  Validación (schemas.py)                     │  │
│  │  Pydantic Models para entrada/salida         │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │  Utilidades (utils/alerts.py)                │  │
│  │  ├─ validar_y_generar_alertas()              │  │
│  │  ├─ calcular_calidad_aire()                  │  │
│  │  └─ es_dispositivo_conectado()               │  │
│  └──────────────────────────────────────────────┘  │
└──────────────────┬──────────────────────────────────┘
                   │
                   │ SQLAlchemy ORM
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│         PostgreSQL Database (models.py)             │
│  ┌───────────────┐  ┌──────────────┐               │
│  │ dispositivos  │  │  lecturas    │               │
│  ├───────────────┤  ├──────────────┤               │
│  │ id (PK)       │  │ id (PK)      │               │
│  │ nombre        │  │ dispositivo_id(FK)           │
│  │ ubicacion     │  │ fecha_hora   │               │
│  │ limite_co2    │  │ temperatura  │               │
│  │ limite_pm25   │  │ humedad      │               │
│  │ ultimo_contacto│ │ pm2_5        │               │
│  │               │  │ co2          │               │
│  └───────────────┘  └──────────────┘               │
│  ┌─────────────────────────┐                       │
│  │  historial_alertas      │                       │
│  ├─────────────────────────┤                       │
│  │ id (PK)                 │                       │
│  │ dispositivo_id (FK)     │                       │
│  │ fecha_hora              │                       │
│  │ variable_afectada       │                       │
│  │ valor_detectado         │                       │
│  │ nivel_critico           │                       │
│  │ resuelto                │                       │
│  └─────────────────────────┘                       │
│  ┌──────────────────────────┐                      │
│  │  misiones_usuario        │                      │
│  ├──────────────────────────┤                      │
│  │ id (PK)                  │                      │
│  │ titulo                   │                      │
│  │ categoria                │                      │
│  │ progreso (0-100)         │                      │
│  │ activa                   │                      │
│  └──────────────────────────┘                      │
└─────────────────────────────────────────────────────┘
```

---

## 📦 Componentes Principales

### 1. **main.py** - Punto de Entrada
- Inicializa la aplicación FastAPI
- Configura middleware (CORS)
- Registra todos los routers
- Maneja eventos de startup/shutdown
- Define rutas de salud

### 2. **config.py** - Configuración
- Carga variables de entorno desde `.env`
- Construye URL de conexión a BD
- Gestiona configuraciones por ambiente
- Centraliza valores constantes

### 3. **database.py** - Conexión a BD
- Configura SQLAlchemy engine
- Define sesiones
- Proporciona función `get_db()` como dependencia FastAPI
- Inicializa tablas en startup

### 4. **models.py** - Modelos ORM
- Define 4 tablas principales:
  - `Dispositivo` - Sensores IoT
  - `Lectura` - Datos de sensores
  - `HistorialAlerta` - Alertas generadas
  - `MisionUsuario` - Gamificación
- Incluye índices para optimizar queries
- Relaciones entre tablas

### 5. **schemas.py** - Validación Pydantic
- Esquemas para cada recurso (Base, Create, Response)
- Validación automática de tipos
- Documentación OpenAPI integrada
- Schemas reutilizables (ej: EstadoDispositivo)

### 6. **crud.py** - Operaciones de Base de Datos
- Funciones reutilizables de CRUD
- Separación de lógica BD del router
- Handles para errores y logging
- 20+ funciones de operaciones comunes

### 7. **routers/** - Endpoints REST
```
├── dispositivos.py   → POST /dispositivos, GET /dispositivos, GET /dispositivos/{id}
├── lecturas.py       → POST /lecturas, GET /lecturas/actual, GET /lecturas/estadisticas
├── alertas.py        → GET /alertas/recientes, PATCH /alertas/{id}/resolver
└── misiones.py       → GET /misiones, POST /misiones, PATCH /misiones/{id}/progreso
```

### 8. **utils/alerts.py** - Lógica de Negocio
- Generación automática de alertas
- Cálculo de calidad del aire
- Verificación de estado de conexión
- Utilidades de validación

---

## 🔄 Flujos de Datos

### Flujo 1: Registrar Lectura (ESP32 → API → BD)

```
1. ESP32 envía POST /api/v1/lecturas
   {
     "dispositivo_id": "ESP32_AULA_1",
     "temperatura": 22.5,
     "co2": 950,
     "pm2_5": 28.3,
     ...
   }

2. Router (lecturas.py) recibe solicitud
   ↓ Validación Pydantic (schemas.py)

3. Router llama CRUD (crud.py)
   - crud.crear_lectura()
   - crud.actualizar_ultimo_contacto()

4. CRUD accede a BD (database.py)
   - INSERT lecturas
   - UPDATE dispositivos

5. Generar Alertas (utils/alerts.py)
   - Si CO2 > limite_co2 → INSERT historial_alertas
   - Si PM2.5 > limite_pm25 → INSERT historial_alertas

6. Respuesta JSON al ESP32
   {
     "id": 12345,
     "dispositivo_id": "ESP32_AULA_1",
     "fecha_hora": "2024-06-21T15:30:45.123456+00:00",
     "temperatura": 22.5,
     ...
   }
```

### Flujo 2: Obtener Última Lectura (Frontend)

```
1. Frontend envía GET /api/v1/lecturas/actual?dispositivo_id=ESP32_AULA_1

2. Router (lecturas.py) procesa:
   - obtener_dispositivo()
   - obtener_ultima_lectura()

3. Utilidades (alerts.py):
   - es_dispositivo_conectado() → boolean
   - calcular_minutos_sin_contacto() → int

4. Respuesta con lectura + estado:
   {
     "lectura": {...},
     "estado_dispositivo": {
       "dispositivo_id": "ESP32_AULA_1",
       "conectado": true,
       "minutos_sin_contacto": 2
     }
   }
```

### Flujo 3: Generar Estadísticas (Gráficos)

```
1. Frontend: GET /api/v1/lecturas/estadisticas?dispositivo_id=ESP32_AULA_1&filtro=hoy

2. Router obtiene lecturas del período especificado

3. CRUD agrupa datos:
   - Si filtro="hoy" → agrupar por hora
   - Si filtro="semana" → agrupar por día
   - Si filtro="mes" → agrupar por día

4. Calcula promedios:
   - temperatura_promedio
   - humedad_promedio
   - pm25_promedio
   - co2_promedio

5. Respuesta JSON para gráficos:
   {
     "filtro": "hoy",
     "periodo": "Últimas 24 horas",
     "datos": [
       {
         "timestamp": "10:00",
         "temperatura_promedio": 22.5,
         "pm25_promedio": 15.3,
         "co2_promedio": 850,
         ...
       },
       ...
     ],
     "total_lecturas": 1440
   }
```

---

## 🔐 Seguridad & Buenas Prácticas

### Implementadas:
✅ Validación de entrada con Pydantic  
✅ Manejo de excepciones global  
✅ CORS configurado  
✅ Logging centralizado  
✅ Índices de BD para performance  
✅ Código documentado (docstrings)  
✅ Separación de capas (router → CRUD → BD)  
✅ Credenciales en variables de entorno  

### Por Implementar (Producción):
⚠️ Autenticación (JWT)  
⚠️ Autorización (roles/permisos)  
⚠️ Rate limiting  
⚠️ HTTPS/TLS  
⚠️ API key validation  
⚠️ Backup automático BD  
⚠️ Monitoreo y alertas  

---

## 📊 Performance

### Índices de Base de Datos:
- `idx_lecturas_dispositivo_fecha` - Optimiza búsqueda de lecturas por dispositivo y tiempo
- `idx_lecturas_fecha` - Optimiza búsqueda por rango de fechas
- `idx_alertas_dispositivo_resuelto` - Optimiza búsqueda de alertas activas
- `idx_alertas_fecha_resuelto` - Optimiza búsqueda de alertas recientes
- `idx_misiones_activas` - Optimiza búsqueda de misiones activas

### Optimizaciones:
- Pool de conexiones a BD
- Reciclaje de conexiones cada hora
- Validación de conexión antes de usar
- Paginación implícita en estadísticas

---

## 🚀 Escalabilidad

```
Arquitectura actual (Single Server):
Client(s) → FastAPI → PostgreSQL

Arquitectura futura (Load Balanced):
Clients → Load Balancer → FastAPI instances (N) → PostgreSQL Cluster
         → Redis (Cache)
         → Message Queue (Kafka/RabbitMQ)
```

---

## 📈 Monitoreo & Logs

- Logs en consola con timestamp y nivel
- Niveles: DEBUG, INFO, WARNING, ERROR
- Integración con herramientas: DataDog, New Relic, etc.
- Métricas: requests/segundo, latencia, errores

---

## 🔧 Dependencias Principales

| Librería | Versión | Propósito |
|----------|---------|----------|
| FastAPI | 0.104.1 | Framework web |
| Uvicorn | 0.24.0 | Servidor ASGI |
| SQLAlchemy | 2.0.23 | ORM para BD |
| Psycopg2 | 2.9.9 | Driver PostgreSQL |
| Pydantic | 2.5.0 | Validación datos |
| Alembic | 1.12.1 | Migraciones BD |

---

**Última actualización**: Junio 2024  
**Mantenedor**: Equipo de Desarrollo  
**Ambiente**: Production-Ready

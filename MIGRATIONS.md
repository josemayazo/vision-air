# Migraciones de Base de Datos

## Estado Actual

Se identificó un problema crítico: el campo `valor_detectado` en la tabla `historial_alertas` está limitado a `NUMERIC(5, 2)` (máximo 999.99), pero necesita permitir valores como CO2 = 1200 ppm.

## Solución

Se han actualizado:

1. **Model (app/models.py)**: 
   - `HistorialAlerta.valor_detectado` ahora es `Numeric(10, 2)`
   - Permite valores hasta 99999.99

2. **Migration SQL (migrations/002_fix_valor_detectado_precision.sql)**:
   - Script para aplicar el cambio en BD existente

## Cómo Aplicar la Migración

### Opción 1: Si tienes BD vacía (recomendado)
```bash
# Simplemente elimina todos los datos/tabla y recrea:
cd vision_air_api
python -c "
from app.database import Base, engine
Base.metadata.drop_all(bind=engine)  # ⚠️ Elimina TODOS los datos
Base.metadata.create_all(bind=engine)  # Crea tablas con esquema correcto
print('BD recreada con esquema correcto')
"
```

### Opción 2: Si tienes BD con datos importantes
```bash
# Ejecuta la migración SQL manualmente en tu BD:
psql -U elayazo -h localhost -d vision-air-db -f migrations/002_fix_valor_detectado_precision.sql

# O si usas pgAdmin:
# 1. Abre pgAdmin
# 2. Ve a: Tools → Query Tool
# 3. Copia el contenido de 002_fix_valor_detectado_precision.sql
# 4. Ejecuta
```

### Opción 3: Con Docker (si usas PostgreSQL en contenedor)
```bash
docker exec -i postgres_container_name psql -U elayazo -d vision-air-db < migrations/002_fix_valor_detectado_precision.sql
```

## Verificación

Después de aplicar la migración, verifica:

```bash
# En psql:
\d historial_alertas;

# Deberías ver:
# valor_detectado | numeric(10,2) | not null |
```

## Archivos Cambiados

- ✅ `app/models.py` - Modelo actualizado (Numeric(10, 2))
- ✅ `migrations/001_initial_schema.sql` - Schema inicial corregido
- ✅ `migrations/002_fix_valor_detectado_precision.sql` - Migración para BD existente

## Siguiente Paso

Después de aplicar la migración, prueba nuevamente con Postman:

```bash
# 1. Crear dispositivo
POST http://localhost:8000/api/v1/dispositivos/
{
  "id": "ESP32_AULA_1",
  "nombre": "Sensor de Aula 1",
  "ubicacion": "Aula de Clase",
  "limite_co2": 900,
  "limite_pm25": 25
}

# 2. Registrar lectura con CO2 alto (1200 ppm)
POST http://localhost:8000/api/v1/lecturas/
{
  "dispositivo_id": "ESP32_AULA_1",
  "temperatura": 23.2,
  "humedad": 48.5,
  "pm1_0": 12.3,
  "pm2_5": 18.9,
  "pm4_0": 22.1,
  "pm10": 28.5,
  "voc": 200,
  "co2": 1200
}

# Debería crear una alerta sin error ✅
```

## Referencia SQL

El comando aplicado:

```sql
ALTER TABLE historial_alertas 
ALTER COLUMN valor_detectado TYPE NUMERIC(10, 2);
```

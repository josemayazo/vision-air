-- ============================================================
-- Script de Migración SQL para Dusty Monitor
-- Base de Datos: PostgreSQL
-- ============================================================

-- ============================================================
-- TABLA: dispositivos
-- Descripción: Registro de dispositivos IoT (sensores ESP32)
-- ============================================================
CREATE TABLE IF NOT EXISTS dispositivos (
    id VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    ubicacion VARCHAR(255) NOT NULL,
    limite_co2 INTEGER NOT NULL DEFAULT 900,
    limite_pm25 INTEGER NOT NULL DEFAULT 25,
    ultimo_contacto TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE dispositivos IS 'Almacena los dispositivos IoT conectados al sistema';
COMMENT ON COLUMN dispositivos.id IS 'Identificador único del dispositivo (ej: ESP32_AULA_1)';
COMMENT ON COLUMN dispositivos.nombre IS 'Nombre descriptivo del sensor';
COMMENT ON COLUMN dispositivos.ubicacion IS 'Ubicación física del dispositivo';
COMMENT ON COLUMN dispositivos.limite_co2 IS 'Límite máximo de CO2 en ppm';
COMMENT ON COLUMN dispositivos.limite_pm25 IS 'Límite máximo de PM2.5 en µg/m³';
COMMENT ON COLUMN dispositivos.ultimo_contacto IS 'Último timestamp de comunicación con el dispositivo';


-- ============================================================
-- TABLA: lecturas
-- Descripción: Lecturas de sensores (registradas cada minuto)
-- ============================================================
CREATE TABLE IF NOT EXISTS lecturas (
    id BIGSERIAL PRIMARY KEY,
    dispositivo_id VARCHAR(50) NOT NULL REFERENCES dispositivos(id) ON DELETE CASCADE,
    fecha_hora TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    temperatura NUMERIC(4, 2),
    humedad NUMERIC(5, 2),
    pm1_0 NUMERIC(5, 2),
    pm2_5 NUMERIC(5, 2),
    pm4_0 NUMERIC(5, 2),
    pm10 NUMERIC(5, 2),
    voc INTEGER,
    co2 INTEGER
);

COMMENT ON TABLE lecturas IS 'Datos de sensores enviados por los dispositivos IoT';
COMMENT ON COLUMN lecturas.dispositivo_id IS 'Referencia al dispositivo que registró la lectura';
COMMENT ON COLUMN lecturas.temperatura IS 'Temperatura en grados Celsius';
COMMENT ON COLUMN lecturas.humedad IS 'Humedad relativa en porcentaje';
COMMENT ON COLUMN lecturas.pm1_0 IS 'Partículas PM1.0 en µg/m³';
COMMENT ON COLUMN lecturas.pm2_5 IS 'Partículas PM2.5 en µg/m³';
COMMENT ON COLUMN lecturas.pm4_0 IS 'Partículas PM4.0 en µg/m³';
COMMENT ON COLUMN lecturas.pm10 IS 'Partículas PM10 en µg/m³';
COMMENT ON COLUMN lecturas.voc IS 'Compuestos Orgánicos Volátiles en ppb';
COMMENT ON COLUMN lecturas.co2 IS 'Dióxido de Carbono en ppm';

-- Índice compuesto para optimizar consultas temporales
CREATE INDEX IF NOT EXISTS idx_lecturas_dispositivo_fecha 
ON lecturas (dispositivo_id, fecha_hora DESC);

-- Índice adicional para búsquedas por rango de fechas
CREATE INDEX IF NOT EXISTS idx_lecturas_fecha 
ON lecturas (fecha_hora DESC);


-- ============================================================
-- TABLA: historial_alertas
-- Descripción: Registro de alertas por exceso de contaminación
-- ============================================================
CREATE TABLE IF NOT EXISTS historial_alertas (
    id SERIAL PRIMARY KEY,
    dispositivo_id VARCHAR(50) NOT NULL REFERENCES dispositivos(id) ON DELETE CASCADE,
    fecha_hora TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    variable_afectada VARCHAR(50) NOT NULL,
    valor_detectado NUMERIC(10, 2) NOT NULL,
    nivel_critico VARCHAR(10) NOT NULL CHECK (nivel_critico IN ('ALTA', 'MEDIA')),
    resuelto BOOLEAN NOT NULL DEFAULT FALSE
);

COMMENT ON TABLE historial_alertas IS 'Historial de alertas generadas cuando se superan los límites configurados';
COMMENT ON COLUMN historial_alertas.dispositivo_id IS 'Referencia al dispositivo que generó la alerta';
COMMENT ON COLUMN historial_alertas.variable_afectada IS 'Variable que superó el límite (PM2.5, CO2, PM10, VOC)';
COMMENT ON COLUMN historial_alertas.valor_detectado IS 'Valor medido que superó el límite';
COMMENT ON COLUMN historial_alertas.nivel_critico IS 'Nivel de severidad: ALTA (>1.5x límite) o MEDIA (1-1.5x límite)';
COMMENT ON COLUMN historial_alertas.resuelto IS 'Indica si la alerta ha sido resuelta';

-- Índices para consultas frecuentes de alertas
CREATE INDEX IF NOT EXISTS idx_alertas_dispositivo_resuelto 
ON historial_alertas (dispositivo_id, resuelto);

CREATE INDEX IF NOT EXISTS idx_alertas_fecha_resuelto 
ON historial_alertas (fecha_hora DESC, resuelto);


-- ============================================================
-- TABLA: misiones_usuario
-- Descripción: Misiones de gamificación para motivar a estudiantes
-- ============================================================
CREATE TABLE IF NOT EXISTS misiones_usuario (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    descripcion TEXT,
    progreso INTEGER NOT NULL DEFAULT 0 CHECK (progreso >= 0 AND progreso <= 100),
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE misiones_usuario IS 'Misiones educativas para gamificación del sistema';
COMMENT ON COLUMN misiones_usuario.titulo IS 'Título de la misión (ej: Cuidar el aire del aula)';
COMMENT ON COLUMN misiones_usuario.categoria IS 'Categoría educativa (ej: STEM Ciencias)';
COMMENT ON COLUMN misiones_usuario.progreso IS 'Porcentaje de progreso (0-100)';
COMMENT ON COLUMN misiones_usuario.activa IS 'Indica si la misión está activa';

-- Índice para consultas de misiones activas
CREATE INDEX IF NOT EXISTS idx_misiones_activas 
ON misiones_usuario (activa);


-- ============================================================
-- DATOS INICIALES (Opcional)
-- ============================================================

-- Insertar algunos dispositivos de ejemplo
INSERT INTO dispositivos (id, nombre, ubicacion, limite_co2, limite_pm25)
VALUES 
    ('ESP32_AULA_1', 'Sensor Aula de Ciencias', 'Laboratorio de Biología', 900, 25),
    ('ESP32_AULA_2', 'Sensor Aula Principal', 'Sala de Clase Primaria', 900, 25),
    ('ESP32_BIBLIOTECA', 'Sensor Biblioteca', 'Zona de Lectura', 700, 20)
ON CONFLICT DO NOTHING;

-- Insertar algunas misiones de ejemplo
INSERT INTO misiones_usuario (titulo, categoria, descripcion, progreso, activa)
VALUES
    ('Cuidar el aire del aula', 'STEM Ciencias', 'Mantén el CO2 bajo en el aula durante una semana', 0, TRUE),
    ('Experto en PM2.5', 'STEM Ciencias', 'Aprende cómo las partículas PM2.5 afectan la salud', 45, TRUE),
    ('Ingeniero STEM', 'STEM Tecnología', 'Participa en la instalación y calibración de sensores', 75, TRUE)
ON CONFLICT DO NOTHING;


-- ============================================================
-- VISTAS ÚTILES (Opcional)
-- ============================================================

-- Vista: Última lectura de cada dispositivo
CREATE OR REPLACE VIEW v_ultimas_lecturas AS
SELECT DISTINCT ON (d.id)
    d.id,
    d.nombre,
    d.ubicacion,
    l.fecha_hora,
    l.temperatura,
    l.humedad,
    l.pm2_5,
    l.co2,
    CASE 
        WHEN (CURRENT_TIMESTAMP AT TIME ZONE 'UTC' - d.ultimo_contacto) < INTERVAL '3 minutes'
        THEN 'Conectado'
        ELSE 'Desconectado'
    END as estado
FROM dispositivos d
LEFT JOIN lecturas l ON d.id = l.dispositivo_id
ORDER BY d.id, l.fecha_hora DESC;


-- ============================================================
-- FIN DEL SCRIPT DE MIGRACIÓN
-- ============================================================

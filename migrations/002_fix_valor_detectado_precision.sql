-- ============================================================
-- Script de Migración #2 para Dusty Monitor
-- Cambiar precisión del campo valor_detectado en historial_alertas
-- ============================================================
-- 
-- RAZÓN: El campo valor_detectado está limitado a NUMERIC(5, 2)
-- lo que permite máximo 999.99, pero CO2 puede ser 1200+ ppm
-- SOLUCIÓN: Cambiar a NUMERIC(10, 2) para permitir hasta 99999.99
--
-- ============================================================

-- Cambiar el tipo de datos del campo valor_detectado
ALTER TABLE historial_alertas 
ALTER COLUMN valor_detectado TYPE NUMERIC(10, 2);

-- Comentario actualizado
COMMENT ON COLUMN historial_alertas.valor_detectado IS 'Valor medido que superó el límite (ahora permite hasta 99999.99 - CO2, PM2.5, etc)';

-- ============================================================
-- Verificación
-- ============================================================
-- Para verificar el cambio:
-- \d historial_alertas;
-- SELECT column_name, data_type FROM information_schema.columns 
-- WHERE table_name = 'historial_alertas' AND column_name = 'valor_detectado';

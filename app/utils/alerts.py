"""
Utilidades para validaciones y procesamiento de alertas.

Este módulo contiene funciones auxiliares para validar datos y generar alertas
automáticamente basadas en los límites configurados en los dispositivos.
"""

from sqlalchemy.orm import Session
from app.models import Dispositivo, Lectura, HistorialAlerta
from app.schemas import AlertaBase
from app import crud
import logging

logger = logging.getLogger(__name__)


def validar_y_generar_alertas(
    db: Session,
    lectura: Lectura,
    dispositivo: Dispositivo
) -> list[HistorialAlerta]:
    """
    Valida si una lectura supera los límites y genera alertas automáticamente.
    
    Args:
        db: Sesión de SQLAlchemy
        lectura: Lectura a validar
        dispositivo: Dispositivo que tomó la lectura
        
    Returns:
        list: Lista de alertas generadas (puede estar vacía)
    """
    alertas_generadas = []
    
    try:
        # Verificar CO2
        if lectura.co2 and lectura.co2 > dispositivo.limite_co2:
            nivel = "ALTA" if lectura.co2 > dispositivo.limite_co2 * 1.5 else "MEDIA"
            
            alerta_data = AlertaBase(
                dispositivo_id=dispositivo.id,
                variable_afectada="CO2",
                valor_detectado=lectura.co2,
                nivel_critico=nivel
            )
            alerta = crud.crear_alerta(db, alerta_data)
            alertas_generadas.append(alerta)
            logger.info(f"Alerta CO2 ({nivel}): {lectura.co2} ppm en {dispositivo.id}")
        
        # Verificar PM2.5
        if lectura.pm2_5 and float(lectura.pm2_5) > dispositivo.limite_pm25:
            nivel = "ALTA" if float(lectura.pm2_5) > dispositivo.limite_pm25 * 1.5 else "MEDIA"
            
            alerta_data = AlertaBase(
                dispositivo_id=dispositivo.id,
                variable_afectada="PM2.5",
                valor_detectado=lectura.pm2_5,
                nivel_critico=nivel
            )
            alerta = crud.crear_alerta(db, alerta_data)
            alertas_generadas.append(alerta)
            logger.info(f"Alerta PM2.5 ({nivel}): {lectura.pm2_5} µg/m³ en {dispositivo.id}")
        
        # Verificar PM10
        if lectura.pm10:
            limite_pm10 = 50  # Límite por defecto para PM10
            if float(lectura.pm10) > limite_pm10:
                nivel = "ALTA" if float(lectura.pm10) > limite_pm10 * 1.5 else "MEDIA"
                
                alerta_data = AlertaBase(
                    dispositivo_id=dispositivo.id,
                    variable_afectada="PM10",
                    valor_detectado=lectura.pm10,
                    nivel_critico=nivel
                )
                alerta = crud.crear_alerta(db, alerta_data)
                alertas_generadas.append(alerta)
                logger.info(f"Alerta PM10 ({nivel}): {lectura.pm10} µg/m³ en {dispositivo.id}")
        
        # Verificar VOC (Compuestos Orgánicos Volátiles)
        if lectura.voc:
            limite_voc = 250  # Límite por defecto para VOC
            if lectura.voc > limite_voc:
                nivel = "ALTA" if lectura.voc > limite_voc * 1.5 else "MEDIA"
                
                alerta_data = AlertaBase(
                    dispositivo_id=dispositivo.id,
                    variable_afectada="VOC",
                    valor_detectado=lectura.voc,
                    nivel_critico=nivel
                )
                alerta = crud.crear_alerta(db, alerta_data)
                alertas_generadas.append(alerta)
                logger.info(f"Alerta VOC ({nivel}): {lectura.voc} ppb en {dispositivo.id}")
    
    except Exception as e:
        logger.error(f"Error al generar alertas: {str(e)}")
    
    return alertas_generadas


def calcular_calidad_aire(temperatura: float, humedad: float, pm25: float, co2: int) -> str:
    """
    Calcula el índice de calidad del aire basado en los parámetros principales.
    
    Args:
        temperatura: Temperatura en °C
        humedad: Humedad relativa en %
        pm25: PM2.5 en µg/m³
        co2: CO2 en ppm
        
    Returns:
        str: Categoría de calidad ("EXCELENTE", "BUENA", "ACEPTABLE", "MALA", "MUY MALA")
    """
    # Puntuación basada en PM2.5 (principal indicador)
    if pm25 <= 12:
        pm25_score = 1
    elif pm25 <= 35.4:
        pm25_score = 2
    elif pm25 <= 55.4:
        pm25_score = 3
    elif pm25 <= 150.4:
        pm25_score = 4
    else:
        pm25_score = 5
    
    # Puntuación basada en CO2
    if co2 <= 400:
        co2_score = 1
    elif co2 <= 600:
        co2_score = 2
    elif co2 <= 900:
        co2_score = 3
    elif co2 <= 1200:
        co2_score = 4
    else:
        co2_score = 5
    
    # Promedio de scores
    avg_score = (pm25_score + co2_score) / 2
    
    if avg_score <= 1.5:
        return "EXCELENTE"
    elif avg_score <= 2.5:
        return "BUENA"
    elif avg_score <= 3.5:
        return "ACEPTABLE"
    elif avg_score <= 4.5:
        return "MALA"
    else:
        return "MUY MALA"


def es_dispositivo_conectado(ultimo_contacto, timeout_minutos: int = 3) -> bool:
    """
    Determina si un dispositivo está conectado basándose en el último contacto.
    
    Args:
        ultimo_contacto: Timestamp del último contacto
        timeout_minutos: Minutos para considerar dispositivo desconectado
        
    Returns:
        bool: True si el dispositivo está conectado, False si no
    """
    from datetime import datetime, timedelta, timezone
    
    if not ultimo_contacto:
        return False
    
    ahora = datetime.now(timezone.utc)
    # Normalizar: si ultimo_contacto es naive, asumir UTC
    if ultimo_contacto.tzinfo is None:
        ultimo_contacto = ultimo_contacto.replace(tzinfo=timezone.utc)
    
    tiempo_transcurrido = ahora - ultimo_contacto
    return tiempo_transcurrido <= timedelta(minutes=timeout_minutos)


def calcular_minutos_sin_contacto(ultimo_contacto) -> int:
    """
    Calcula los minutos que han pasado desde el último contacto con el dispositivo.
    
    Args:
        ultimo_contacto: Timestamp del último contacto
        
    Returns:
        int: Número de minutos transcurridos
    """
    from datetime import datetime, timezone
    
    if not ultimo_contacto:
        return -1
    
    ahora = datetime.now(timezone.utc)
    # Normalizar: si ultimo_contacto es naive, asumir UTC
    if ultimo_contacto.tzinfo is None:
        ultimo_contacto = ultimo_contacto.replace(tzinfo=timezone.utc)
    
    tiempo_transcurrido = ahora - ultimo_contacto
    return int(tiempo_transcurrido.total_seconds() / 60)

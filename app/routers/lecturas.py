"""
Router para endpoints de lecturas de sensores.

Maneja el registro de nuevas lecturas (desde ESP32) y la consulta de datos históricos.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import LecturaCreate, LecturaResponse, LecturaActualResponse, EstadoDispositivo, EstadisticasResponse
from app import crud
from app.utils.alerts import validar_y_generar_alertas, es_dispositivo_conectado, calcular_minutos_sin_contacto
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/lecturas",
    tags=["Lecturas"],
    responses={
        400: {"description": "Datos inválidos"},
        404: {"description": "Dispositivo no encontrado"}
    }
)


@router.post(
    "/",
    response_model=LecturaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nueva lectura",
    description="Recibe datos de sensores desde el ESP32 y los almacena en la BD"
)
def registrar_lectura(
    lectura: LecturaCreate,
    db: Session = Depends(get_db)
):
    """
    Registra una nueva lectura de sensores (típicamente enviada por ESP32 cada minuto).
    
    Automáticamente:
    - Actualiza el timestamp de último contacto del dispositivo
    - Genera alertas si los valores superan los límites configurados
    
    Args:
        lectura: Datos de la lectura con todas las métricas ambientales
        
    Returns:
        LecturaResponse: La lectura registrada con ID y timestamp
        
    Raises:
        HTTPException 400: Si los datos están incompletos o son inválidos
        HTTPException 404: Si el dispositivo no existe
    """
    try:
        logger.debug(f"[LECTURA] Recibiendo lectura: dispositivo={lectura.dispositivo_id}")
        logger.debug(f"   temp={lectura.temperatura}C, humidity={lectura.humedad}%, voc={lectura.voc}")
        logger.debug(f"   pm25={lectura.pm2_5}, co2={lectura.co2}ppm")
        
        # Crear la lectura
        db_lectura = crud.crear_lectura(db, lectura)
        logger.info(f"[SUCCESS] Lectura registrada: id={db_lectura.id}, dispositivo={lectura.dispositivo_id}")
        
        # Obtener el dispositivo para validar alertas
        dispositivo = crud.obtener_dispositivo(db, lectura.dispositivo_id)
        
        # Validar y generar alertas automáticamente
        if dispositivo:
            logger.debug(f"[VALIDAR] Umbrales del dispositivo {lectura.dispositivo_id}")
            logger.debug(f"   CO2_limit={dispositivo.limite_co2}ppm, PM25_limit={dispositivo.limite_pm25}")
            validar_y_generar_alertas(db, db_lectura, dispositivo)
            logger.debug(f"[VALIDAR] Completado")
        else:
            logger.warning(f"[WARNING] Dispositivo no encontrado para validación: {lectura.dispositivo_id}")
        
        return db_lectura
    
    except ValueError as e:
        logger.warning(f"[VALIDATION_ERROR] Lectura del dispositivo {lectura.dispositivo_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"[ERROR] Registrar lectura del dispositivo {lectura.dispositivo_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al registrar lectura"
        )


@router.get(
    "/actual",
    response_model=LecturaActualResponse,
    summary="Obtener última lectura",
    description="Devuelve la última lectura registrada y el estado de conexión del dispositivo"
)
def obtener_lectura_actual(
    dispositivo_id: str = Query(..., description="ID del dispositivo"),
    db: Session = Depends(get_db)
):
    """
    Obtiene la última lectura registrada de un dispositivo junto con su estado de conexión.
    
    El dispositivo se considera "Conectado" si su último contacto fue hace menos de 3 minutos.
    
    Args:
        dispositivo_id: ID del dispositivo
        
    Returns:
        LecturaActualResponse: Última lectura y estado del dispositivo
        
    Raises:
        HTTPException 404: Si el dispositivo no existe
    """
    dispositivo = crud.obtener_dispositivo(db, dispositivo_id)
    if not dispositivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispositivo {dispositivo_id} no encontrado"
        )
    
    # Obtener última lectura
    lectura = crud.obtener_ultima_lectura(db, dispositivo_id)
    
    # Determinar estado de conexión
    conectado = es_dispositivo_conectado(dispositivo.ultimo_contacto)
    minutos_sin_contacto = calcular_minutos_sin_contacto(dispositivo.ultimo_contacto)
    
    estado = EstadoDispositivo(
        dispositivo_id=dispositivo_id,
        conectado=conectado,
        minutos_sin_contacto=minutos_sin_contacto if minutos_sin_contacto >= 0 else 0
    )
    
    return LecturaActualResponse(
        lectura=lectura,
        estado_dispositivo=estado
    )


@router.get(
    "/estadisticas",
    response_model=EstadisticasResponse,
    summary="Obtener estadísticas de lecturas",
    description="Devuelve datos agrupados para gráficos de progreso"
)
def obtener_estadisticas(
    dispositivo_id: str = Query(..., description="ID del dispositivo"),
    filtro: str = Query("hoy", regex="^(hoy|semana|mes)$", description="Período: hoy, semana o mes"),
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas de lecturas agrupadas por tiempo para visualización en gráficos.
    
    Args:
        dispositivo_id: ID del dispositivo
        filtro: Período de tiempo ("hoy", "semana", "mes")
        
    Returns:
        EstadisticasResponse: Datos agrupados con promedios
        
    Raises:
        HTTPException 404: Si el dispositivo no existe
    """
    dispositivo = crud.obtener_dispositivo(db, dispositivo_id)
    if not dispositivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispositivo {dispositivo_id} no encontrado"
        )
    
    try:
        stats = crud.obtener_estadisticas_lecturas(db, dispositivo_id, filtro)
        
        # Mapear al formato de respuesta
        periodo_nombres = {
            "hoy": "Últimas 24 horas",
            "semana": "Última semana",
            "mes": "Último mes"
        }
        
        return EstadisticasResponse(
            filtro=filtro,
            periodo=periodo_nombres.get(filtro, "Período desconocido"),
            datos=stats["datos"],
            total_lecturas=stats["total_lecturas"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener estadísticas"
        )

"""
Router para endpoints de dispositivos IoT.

Maneja las operaciones CRUD para registrar y consultar dispositivos.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import DispositivoCreate, DispositivoResponse
from app import crud

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/dispositivos",
    tags=["Dispositivos"],
    responses={404: {"description": "Dispositivo no encontrado"}}
)


@router.post(
    "/",
    response_model=DispositivoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo dispositivo",
    description="Registra un nuevo dispositivo IoT en el sistema"
)
def crear_dispositivo(
    dispositivo: DispositivoCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo dispositivo IoT.
    
    - **id**: Identificador único (ej: ESP32_AULA_1)
    - **nombre**: Nombre descriptivo del sensor
    - **ubicacion**: Ubicación física del dispositivo
    - **limite_co2**: Límite máximo de CO2 (default: 900 ppm)
    - **limite_pm25**: Límite máximo de PM2.5 (default: 25 µg/m³)
    """
    try:
        logger.debug(f"[CREATE] Intentando crear dispositivo: {dispositivo.id}")
        logger.debug(f"   nombre={dispositivo.nombre}, ubicacion={dispositivo.ubicacion}")
        logger.debug(f"   CO2_limit={dispositivo.limite_co2}ppm, PM25_limit={dispositivo.limite_pm25}")
        
        db_dispositivo = crud.crear_dispositivo(db, dispositivo)
        
        logger.info(f"[SUCCESS] Dispositivo creado: {dispositivo.id}")
        return db_dispositivo
    except ValueError as e:
        logger.warning(f"[VALIDATION_ERROR] Dispositivo {dispositivo.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"[ERROR] Crear dispositivo {dispositivo.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear dispositivo"
        )


@router.get(
    "/",
    response_model=list[DispositivoResponse],
    summary="Listar todos los dispositivos",
    description="Obtiene la lista de todos los dispositivos registrados"
)
def listar_dispositivos(db: Session = Depends(get_db)):
    """
    Obtiene todos los dispositivos registrados en el sistema.
    
    Returns:
        Lista de dispositivos con su información
    """
    try:
        logger.debug("[LIST] Obteniendo todos los dispositivos...")
        dispositivos = crud.obtener_todos_dispositivos(db)
        logger.info(f"[SUCCESS] {len(dispositivos)} dispositivos obtenidos")
        for d in dispositivos:
            logger.debug(f"   {d.id}: {d.nombre} (ultimo_contacto={d.ultimo_contacto})")
        return dispositivos
    except Exception as e:
        logger.error(f"[ERROR] Listar dispositivos: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener dispositivos"
        )


@router.get(
    "/{dispositivo_id}",
    response_model=DispositivoResponse,
    summary="Obtener dispositivo específico",
    description="Obtiene los detalles de un dispositivo por su ID"
)
def obtener_dispositivo(
    dispositivo_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene la información detallada de un dispositivo específico.
    
    Args:
        dispositivo_id: ID del dispositivo (ej: ESP32_AULA_1)
        
    Returns:
        DispositivoResponse: Datos del dispositivo
        
    Raises:
        HTTPException 404: Si el dispositivo no existe
    """
    try:
        logger.debug(f"[GET] Buscando dispositivo: {dispositivo_id}")
        dispositivo = crud.obtener_dispositivo(db, dispositivo_id)
        
        if not dispositivo:
            logger.warning(f"[NOT_FOUND] Dispositivo: {dispositivo_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dispositivo {dispositivo_id} no encontrado"
            )
        
        logger.info(f"[SUCCESS] Dispositivo encontrado: {dispositivo_id}")
        logger.debug(f"   nombre={dispositivo.nombre}, ubicacion={dispositivo.ubicacion}")
        logger.debug(f"   ultimo_contacto={dispositivo.ultimo_contacto}")
        return dispositivo
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Obtener dispositivo {dispositivo_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener dispositivo"
        )

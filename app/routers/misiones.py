"""
Router para endpoints de misiones de gamificación.

Maneja consultas y actualizaciones de las misiones educativas del sistema.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import MisionCreate, MisionResponse
from app import crud
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/misiones",
    tags=["Misiones"],
    responses={404: {"description": "Misión no encontrada"}}
)


class ActualizarProgresoRequest(BaseModel):
    """Esquema para actualizar el progreso de una misión."""
    progreso: int = Field(..., ge=0, le=100, description="Nuevo porcentaje de progreso (0-100)")


@router.get(
    "/",
    response_model=list[MisionResponse],
    summary="Obtener misiones activas",
    description="Devuelve las misiones activas y su porcentaje de progreso"
)
def obtener_misiones(
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las misiones activas para el sistema de gamificación.
    
    Las misiones se utilizan para motivar a los estudiantes a monitorear
    y mejorar la calidad del aire en sus espacios.
    
    Returns:
        list[MisionResponse]: Lista de misiones activas con su progreso
    """
    misiones = crud.obtener_misiones_activas(db)
    return misiones


@router.get(
    "/{mision_id}",
    response_model=MisionResponse,
    summary="Obtener misión específica",
    description="Obtiene los detalles de una misión por su ID"
)
def obtener_mision(
    mision_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene la información detallada de una misión específica.
    
    Args:
        mision_id: ID de la misión
        
    Returns:
        MisionResponse: Datos de la misión
        
    Raises:
        HTTPException 404: Si la misión no existe
    """
    mision = crud.obtener_mision(db, mision_id)
    
    if not mision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Misión {mision_id} no encontrada"
        )
    
    return mision


@router.post(
    "/",
    response_model=MisionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva misión",
    description="Registra una nueva misión de gamificación"
)
def crear_mision(
    mision: MisionCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva misión para el sistema de gamificación.
    
    Args:
        mision: Datos de la misión a crear
        
    Returns:
        MisionResponse: La misión creada con su ID
    """
    try:
        db_mision = crud.crear_mision(db, mision)
        return db_mision
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear misión"
        )


@router.patch(
    "/{mision_id}/progreso",
    response_model=MisionResponse,
    summary="Actualizar progreso de misión",
    description="Actualiza el porcentaje de progreso de una misión"
)
def actualizar_progreso(
    mision_id: int,
    datos: ActualizarProgresoRequest,
    db: Session = Depends(get_db)
):
    """
    Actualiza el progreso de una misión.
    
    Cuando el progreso alcanza el 100%, la misión se marca automáticamente como inactiva.
    
    Args:
        mision_id: ID de la misión
        datos: Nuevo porcentaje de progreso (0-100)
        
    Returns:
        MisionResponse: Misión actualizada
        
    Raises:
        HTTPException 400: Si el progreso está fuera del rango 0-100
        HTTPException 404: Si la misión no existe
    """
    mision = crud.obtener_mision(db, mision_id)
    
    if not mision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Misión {mision_id} no encontrada"
        )
    
    try:
        mision_actualizada = crud.actualizar_progreso_mision(db, mision_id, datos.progreso)
        return mision_actualizada
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

"""
Router para endpoints de alertas de calidad del aire.

Maneja la consulta y gestión del historial de alertas.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import AlertaResponse
from app import crud

router = APIRouter(
    prefix="/alertas",
    tags=["Alertas"],
    responses={404: {"description": "Recurso no encontrado"}}
)


@router.get(
    "/recientes",
    response_model=list[AlertaResponse],
    summary="Obtener alertas recientes",
    description="Devuelve alertas no resueltas o del día actual"
)
def obtener_alertas_recientes(
    db: Session = Depends(get_db)
):
    """
    Obtiene el listado de alertas recientes que no han sido resueltas.
    
    Incluye:
    - Todas las alertas no resueltas de las últimas 24 horas
    - Alertas generadas hoy aún si fueron hace más de 24 horas
    
    Returns:
        list[AlertaResponse]: Lista de alertas recientes ordenadas por fecha (más recientes primero)
    """
    alertas = crud.obtener_alertas_recientes(db, horas=24)
    return alertas


@router.get(
    "/dispositivo/{dispositivo_id}",
    response_model=list[AlertaResponse],
    summary="Obtener alertas de un dispositivo",
    description="Devuelve todas las alertas no resueltas de un dispositivo específico"
)
def obtener_alertas_dispositivo(
    dispositivo_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las alertas no resueltas de un dispositivo específico.
    
    Args:
        dispositivo_id: ID del dispositivo
        
    Returns:
        list[AlertaResponse]: Lista de alertas del dispositivo
        
    Raises:
        HTTPException 404: Si el dispositivo no existe
    """
    # Verificar que el dispositivo existe
    dispositivo = crud.obtener_dispositivo(db, dispositivo_id)
    if not dispositivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispositivo {dispositivo_id} no encontrado"
        )
    
    alertas = crud.obtener_alertas_por_dispositivo(db, dispositivo_id)
    return alertas


@router.patch(
    "/{alerta_id}/resolver",
    response_model=AlertaResponse,
    summary="Marcar alerta como resuelta",
    description="Actualiza el estado de una alerta para marcarla como resuelta"
)
def resolver_alerta(
    alerta_id: int,
    db: Session = Depends(get_db)
):
    """
    Marca una alerta como resuelta (resuelto = true).
    
    Se utiliza cuando se han tomado acciones para mejorar la calidad del aire
    y la alerta ya no requiere atención inmediata.
    
    Args:
        alerta_id: ID de la alerta a resolver
        
    Returns:
        AlertaResponse: Alerta actualizada
        
    Raises:
        HTTPException 404: Si la alerta no existe
    """
    alerta = crud.marcar_alerta_como_resuelta(db, alerta_id)
    
    if not alerta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alerta {alerta_id} no encontrada"
        )
    
    return alerta

"""
Operaciones CRUD (Create, Read, Update, Delete) para la base de datos.

Este módulo contiene funciones reutilizables para operaciones de BD,
manteniendo la lógica separada de los routers.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, timedelta
from app.models import Dispositivo, Lectura, HistorialAlerta, MisionUsuario
from app.schemas import (
    DispositivoCreate, LecturaCreate, AlertaBase, MisionCreate
)
import logging

logger = logging.getLogger(__name__)


# ==================== DISPOSITIVOS ====================

def crear_dispositivo(db: Session, dispositivo: DispositivoCreate) -> Dispositivo:
    """
    Crea un nuevo dispositivo en la base de datos.
    
    Args:
        db: Sesión de SQLAlchemy
        dispositivo: Datos del dispositivo a crear
        
    Returns:
        Dispositivo: El dispositivo creado
        
    Raises:
        Exception: Si el dispositivo ya existe
    """
    # Verificar si ya existe
    dispositivo_existente = db.query(Dispositivo).filter(Dispositivo.id == dispositivo.id).first()
    if dispositivo_existente:
        raise ValueError(f"Dispositivo con ID {dispositivo.id} ya existe")
    
    db_dispositivo = Dispositivo(**dispositivo.model_dump())
    db.add(db_dispositivo)
    db.commit()
    db.refresh(db_dispositivo)
    
    logger.info(f"Dispositivo creado: {dispositivo.id}")
    return db_dispositivo


def obtener_dispositivo(db: Session, dispositivo_id: str) -> Dispositivo:
    """
    Obtiene un dispositivo por su ID.
    
    Args:
        db: Sesión de SQLAlchemy
        dispositivo_id: ID del dispositivo
        
    Returns:
        Dispositivo: El dispositivo encontrado o None
    """
    return db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()


def obtener_todos_dispositivos(db: Session) -> list[Dispositivo]:
    """
    Obtiene todos los dispositivos registrados.
    
    Args:
        db: Sesión de SQLAlchemy
        
    Returns:
        list: Lista de dispositivos
    """
    return db.query(Dispositivo).all()


def actualizar_ultimo_contacto(db: Session, dispositivo_id: str) -> Dispositivo:
    """
    Actualiza el timestamp del último contacto del dispositivo.
    
    Args:
        db: Sesión de SQLAlchemy
        dispositivo_id: ID del dispositivo
        
    Returns:
        Dispositivo: El dispositivo actualizado
    """
    dispositivo = obtener_dispositivo(db, dispositivo_id)
    if dispositivo:
        dispositivo.ultimo_contacto = datetime.utcnow()
        db.commit()
        db.refresh(dispositivo)
    return dispositivo


# ==================== LECTURAS ====================

def crear_lectura(db: Session, lectura: LecturaCreate) -> Lectura:
    """
    Crea una nueva lectura de sensor en la base de datos.
    
    También actualiza el último contacto del dispositivo.
    
    Args:
        db: Sesión de SQLAlchemy
        lectura: Datos de la lectura
        
    Returns:
        Lectura: La lectura creada
        
    Raises:
        ValueError: Si el dispositivo no existe
    """
    # Verificar que el dispositivo existe
    dispositivo = obtener_dispositivo(db, lectura.dispositivo_id)
    if not dispositivo:
        raise ValueError(f"Dispositivo {lectura.dispositivo_id} no existe")
    
    # Crear la lectura
    db_lectura = Lectura(**lectura.model_dump())
    db.add(db_lectura)
    
    # Actualizar último contacto del dispositivo
    actualizar_ultimo_contacto(db, lectura.dispositivo_id)
    
    db.commit()
    db.refresh(db_lectura)
    
    logger.info(f"Lectura registrada: Dispositivo {lectura.dispositivo_id}")
    return db_lectura


def obtener_ultima_lectura(db: Session, dispositivo_id: str) -> Lectura:
    """
    Obtiene la última lectura registrada de un dispositivo.
    
    Args:
        db: Sesión de SQLAlchemy
        dispositivo_id: ID del dispositivo
        
    Returns:
        Lectura: La última lectura registrada o None
    """
    return db.query(Lectura).filter(
        Lectura.dispositivo_id == dispositivo_id
    ).order_by(desc(Lectura.fecha_hora)).first()


def obtener_lecturas_por_periodo(
    db: Session,
    dispositivo_id: str,
    filtro: str = "hoy"
) -> list[Lectura]:
    """
    Obtiene lecturas agrupadas por un período específico.
    
    Args:
        db: Sesión de SQLAlchemy
        dispositivo_id: ID del dispositivo
        filtro: "hoy", "semana" o "mes"
        
    Returns:
        list: Lista de lecturas del período especificado
    """
    ahora = datetime.utcnow()
    
    # Definir el rango de fechas según el filtro
    if filtro == "hoy":
        fecha_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    elif filtro == "semana":
        fecha_inicio = ahora - timedelta(days=ahora.weekday())
    elif filtro == "mes":
        fecha_inicio = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        fecha_inicio = ahora - timedelta(days=30)
    
    query = db.query(Lectura).filter(
        and_(
            Lectura.dispositivo_id == dispositivo_id,
            Lectura.fecha_hora >= fecha_inicio
        )
    ).order_by(desc(Lectura.fecha_hora))
    
    return query.all()


def obtener_estadisticas_lecturas(
    db: Session,
    dispositivo_id: str,
    filtro: str = "hoy"
) -> dict:
    """
    Genera estadísticas de lecturas para gráficos.
    
    Args:
        db: Sesión de SQLAlchemy
        dispositivo_id: ID del dispositivo
        filtro: "hoy", "semana" o "mes"
        
    Returns:
        dict: Datos estadísticos agrupados
    """
    lecturas = obtener_lecturas_por_periodo(db, dispositivo_id, filtro)
    
    if not lecturas:
        return {
            "filtro": filtro,
            "datos": [],
            "total_lecturas": 0
        }
    
    # Agrupar por hora (si es hoy) o día (si es semana/mes)
    datos_agrupados = {}
    
    for lectura in lecturas:
        if filtro == "hoy":
            clave = lectura.fecha_hora.strftime("%H:00")  # Agrupar por hora
        else:
            clave = lectura.fecha_hora.strftime("%Y-%m-%d")  # Agrupar por día
        
        if clave not in datos_agrupados:
            datos_agrupados[clave] = {
                "timestamp": clave,
                "temperatura_promedio": [],
                "humedad_promedio": [],
                "pm25_promedio": [],
                "co2_promedio": [],
                "lecturas_count": 0
            }
        
        if lectura.temperatura:
            datos_agrupados[clave]["temperatura_promedio"].append(float(lectura.temperatura))
        if lectura.humedad:
            datos_agrupados[clave]["humedad_promedio"].append(float(lectura.humedad))
        if lectura.pm2_5:
            datos_agrupados[clave]["pm25_promedio"].append(float(lectura.pm2_5))
        if lectura.co2:
            datos_agrupados[clave]["co2_promedio"].append(lectura.co2)
        
        datos_agrupados[clave]["lecturas_count"] += 1
    
    # Calcular promedios
    datos_finales = []
    for clave, datos in sorted(datos_agrupados.items()):
        datos_finales.append({
            "timestamp": clave,
            "temperatura_promedio": sum(datos["temperatura_promedio"]) / len(datos["temperatura_promedio"]) if datos["temperatura_promedio"] else None,
            "humedad_promedio": sum(datos["humedad_promedio"]) / len(datos["humedad_promedio"]) if datos["humedad_promedio"] else None,
            "pm25_promedio": sum(datos["pm25_promedio"]) / len(datos["pm25_promedio"]) if datos["pm25_promedio"] else None,
            "co2_promedio": sum(datos["co2_promedio"]) / len(datos["co2_promedio"]) if datos["co2_promedio"] else None,
            "lecturas_count": datos["lecturas_count"]
        })
    
    return {
        "filtro": filtro,
        "datos": datos_finales,
        "total_lecturas": len(lecturas)
    }


# ==================== ALERTAS ====================

def crear_alerta(db: Session, alerta: AlertaBase) -> HistorialAlerta:
    """
    Crea un nuevo registro de alerta en el historial.
    
    Args:
        db: Sesión de SQLAlchemy
        alerta: Datos de la alerta
        
    Returns:
        HistorialAlerta: La alerta creada
        
    Raises:
        ValueError: Si el dispositivo no existe
    """
    dispositivo = obtener_dispositivo(db, alerta.dispositivo_id)
    if not dispositivo:
        raise ValueError(f"Dispositivo {alerta.dispositivo_id} no existe")
    
    db_alerta = HistorialAlerta(**alerta.model_dump())
    db.add(db_alerta)
    db.commit()
    db.refresh(db_alerta)
    
    logger.warning(f"Alerta creada: {alerta.variable_afectada} en {alerta.dispositivo_id}")
    return db_alerta


def obtener_alertas_recientes(db: Session, horas: int = 24) -> list[HistorialAlerta]:
    """
    Obtiene alertas recientes no resueltas o del día actual.
    
    Args:
        db: Sesión de SQLAlchemy
        horas: Número de horas hacia atrás para buscar
        
    Returns:
        list: Lista de alertas recientes
    """
    fecha_limite = datetime.utcnow() - timedelta(hours=horas)
    
    alertas = db.query(HistorialAlerta).filter(
        and_(
            HistorialAlerta.fecha_hora >= fecha_limite,
            HistorialAlerta.resuelto == False
        )
    ).order_by(desc(HistorialAlerta.fecha_hora)).all()
    
    return alertas


def obtener_alertas_por_dispositivo(db: Session, dispositivo_id: str) -> list[HistorialAlerta]:
    """
    Obtiene todas las alertas no resueltas de un dispositivo específico.
    
    Args:
        db: Sesión de SQLAlchemy
        dispositivo_id: ID del dispositivo
        
    Returns:
        list: Lista de alertas del dispositivo
    """
    return db.query(HistorialAlerta).filter(
        and_(
            HistorialAlerta.dispositivo_id == dispositivo_id,
            HistorialAlerta.resuelto == False
        )
    ).order_by(desc(HistorialAlerta.fecha_hora)).all()


def marcar_alerta_como_resuelta(db: Session, alerta_id: int) -> HistorialAlerta:
    """
    Marca una alerta como resuelta.
    
    Args:
        db: Sesión de SQLAlchemy
        alerta_id: ID de la alerta
        
    Returns:
        HistorialAlerta: La alerta actualizada
    """
    alerta = db.query(HistorialAlerta).filter(HistorialAlerta.id == alerta_id).first()
    if alerta:
        alerta.resuelto = True
        db.commit()
        db.refresh(alerta)
        logger.info(f"Alerta {alerta_id} marcada como resuelta")
    return alerta


# ==================== MISIONES ====================

def crear_mision(db: Session, mision: MisionCreate) -> MisionUsuario:
    """
    Crea una nueva misión de gamificación.
    
    Args:
        db: Sesión de SQLAlchemy
        mision: Datos de la misión
        
    Returns:
        MisionUsuario: La misión creada
    """
    db_mision = MisionUsuario(**mision.model_dump())
    db.add(db_mision)
    db.commit()
    db.refresh(db_mision)
    
    logger.info(f"Misión creada: {mision.titulo}")
    return db_mision


def obtener_misiones_activas(db: Session) -> list[MisionUsuario]:
    """
    Obtiene todas las misiones activas.
    
    Args:
        db: Sesión de SQLAlchemy
        
    Returns:
        list: Lista de misiones activas
    """
    return db.query(MisionUsuario).filter(MisionUsuario.activa == True).all()


def obtener_mision(db: Session, mision_id: int) -> MisionUsuario:
    """
    Obtiene una misión específica por su ID.
    
    Args:
        db: Sesión de SQLAlchemy
        mision_id: ID de la misión
        
    Returns:
        MisionUsuario: La misión encontrada o None
    """
    return db.query(MisionUsuario).filter(MisionUsuario.id == mision_id).first()


def actualizar_progreso_mision(
    db: Session,
    mision_id: int,
    nuevo_progreso: int
) -> MisionUsuario:
    """
    Actualiza el progreso de una misión.
    
    Args:
        db: Sesión de SQLAlchemy
        mision_id: ID de la misión
        nuevo_progreso: Nuevo porcentaje de progreso (0-100)
        
    Returns:
        MisionUsuario: La misión actualizada
        
    Raises:
        ValueError: Si el progreso está fuera del rango 0-100
    """
    if not 0 <= nuevo_progreso <= 100:
        raise ValueError("El progreso debe estar entre 0 y 100")
    
    mision = obtener_mision(db, mision_id)
    if mision:
        mision.progreso = nuevo_progreso
        if nuevo_progreso == 100:
            mision.activa = False
        db.commit()
        db.refresh(mision)
        logger.info(f"Misión {mision_id} progreso actualizado a {nuevo_progreso}%")
    
    return mision

"""
Configuración de la conexión a la base de datos PostgreSQL usando SQLAlchemy.

Este módulo establece la conexión con PostgreSQL y proporciona una sesión
para las operaciones de base de datos.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from app.config import settings
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Crear el motor de la base de datos
# echo=True muestra los queries SQL en logs (desactivar en producción)
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,  # Verifica conexión antes de usarla
    pool_recycle=3600,   # Recicla conexiones cada hora
)

# Crear la sesión
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para los modelos ORM
Base = declarative_base()


def get_db() -> Session:
    """
    Dependencia para obtener una sesión de base de datos en FastAPI.
    
    Yields:
        Session: Sesión de SQLAlchemy para operaciones de BD
        
    Example:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            # usar db para consultas
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Error en sesión de base de datos: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Inicializa la base de datos creando todas las tablas definidas en los modelos.
    
    Se debe ejecutar una sola vez al iniciar la aplicación si no existen las tablas.
    Maneja errores gracefully en caso de que la BD no esté disponible.
    """
    try:
        logger.info("[INIT] Inicializando base de datos...")
        Base.metadata.create_all(bind=engine)
        logger.info("[SUCCESS] Base de datos inicializada correctamente")
        return True
    except Exception as e:
        logger.error(f"[ERROR] No se pudo conectar a la BD: {str(e)}", exc_info=True)
        logger.warning("[WARNING] Continuando sin BD. La API funcionará en modo limitado.")
        return False

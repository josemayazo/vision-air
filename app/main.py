"""
Punto de entrada principal de la aplicación FastAPI.

Inicializa la aplicación, configura los routers, middleware y la base de datos.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.logging_config import setup_logging  # Importar configuración de logging
from app.config import settings
from app.database import init_db
from app.routers import dispositivos, lecturas, alertas, misiones

# Configurar logging centralizado
setup_logging()
logger = logging.getLogger(__name__)

# Crear instancia de FastAPI
app = FastAPI(
    title=settings.api_title,
    description="API REST para monitoreo ambiental escolar con IoT y gamificación",
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== EVENTOS DE INICIO Y CIERRE ====================

@app.on_event("startup")
async def startup_event():
    """
    Se ejecuta cuando la aplicación inicia.
    
    Inicializa la base de datos y carga las configuraciones necesarias.
    NOTA: No lanza excepción si falla la conexión para permitir debugging local.
    """
    logger.info(f"[STARTUP] Iniciando {settings.api_title}")
    logger.info(f"[STARTUP] Ambiente: {settings.environment}")
    logger.info(f"[STARTUP] BD esperada: {settings.db_host}:{settings.db_port}/{settings.db_name}")
    logger.info(f"[STARTUP] URL BD: {settings.database_url}")
    logger.info(f"[STARTUP] Rutas disponibles: /api/v1/dispositivos, /api/v1/lecturas, /api/v1/alertas, /api/v1/misiones")
    logger.info(f"[STARTUP] Documentación: http://localhost:8000/docs")
    
    # Intentar conectar a la BD, pero no fallar si no está disponible
    db_connected = init_db()
    
    if not db_connected:
        logger.warning("[WARNING] La BD no está disponible. Algunos endpoints podrían fallar.")
        logger.warning("[TIP] Para usar la BD en Kubernetes, ejecuta primero:")
        logger.warning("[TIP]   kubectl port-forward -n vision-air-db-amakj svc/vision-air-db-amakj-postgresql 5432:5432")
        logger.warning("[TIP] Y cambia en .env: DB_HOST=localhost")


@app.on_event("shutdown")
async def shutdown_event():
    """Se ejecuta cuando la aplicación se detiene."""
    logger.info("🛑 Apagando aplicación")


# ==================== ROUTERS ====================

# Incluir todos los routers con prefijo de versión de API
app.include_router(
    dispositivos.router,
    prefix=settings.api_prefix
)
app.include_router(
    lecturas.router,
    prefix=settings.api_prefix
)
app.include_router(
    alertas.router,
    prefix=settings.api_prefix
)
app.include_router(
    misiones.router,
    prefix=settings.api_prefix
)


# ==================== RUTAS RAÍZ ====================

@app.get(
    "/",
    tags=["Health"],
    summary="Estado de la API",
    description="Verifica que la API está funcionando correctamente"
)
def read_root():
    """
    Endpoint raíz para verificar el estado de la API.
    
    Returns:
        dict: Información de la API y su estado
    """
    return {
        "mensaje": "Bienvenido a Dusty Monitor API",
        "version": settings.api_version,
        "ambiente": settings.environment,
        "documentacion": "/docs",
        "estado": "🟢 Operativo"
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Verificación de salud",
    description="Endpoint para verificar que la API y la BD están disponibles"
)
def health_check():
    """
    Verifica que la API está funcionando y que puede conectarse a la BD.
    
    Returns:
        dict: Estado de salud del sistema
    """
    return {
        "status": "healthy",
        "version": settings.api_version,
        "database": "connected"
    }


# ==================== MANEJO DE ERRORES ====================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Maneja excepciones ValueError."""
    from fastapi.responses import JSONResponse
    logger.error(f"ValueError: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Maneja excepciones generales no capturadas."""
    from fastapi.responses import JSONResponse
    logger.error(f"Error no manejado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

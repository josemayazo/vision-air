"""
Configuración centralizada de logging para la aplicación.

IMPORTANTE: setup_logging() debe llamarse una SOLA VEZ desde main.py
para evitar handlers duplicados y problemas de rendimiento.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Crear directorio de logs si no existe
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configuración de niveles
LOG_LEVEL = logging.DEBUG  # Cambiar a INFO en producción
FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Control para evitar handlers duplicados
_logging_configured = False

def setup_logging():
    """
    Configura el logging para toda la aplicación.
    
    IMPORTANTE: Se llama UNA SOLA VEZ desde main.py.
    Si se llama múltiples veces, ignora configuraciones posteriores.
    
    Crea:
    - Archivo de logs con rotación cada 10 MB
    - Salida a consola (sin colores ni emojis para evitar problemas en Windows)
    """
    global _logging_configured
    
    # Evitar duplicar handlers si ya está configurado
    if _logging_configured:
        return logging.getLogger()
    
    root_logger = logging.getLogger()
    
    # Limpiar handlers previos si existen
    root_logger.handlers.clear()
    root_logger.setLevel(LOG_LEVEL)
    
    # Formato detallado (sin emojis para evitar problemas de encoding)
    formatter = logging.Formatter(FORMAT, datefmt=DATE_FORMAT)
    
    # ===== HANDLER: Archivo =====
    log_file = LOG_DIR / "vision_air_api.log"
    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10_000_000,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        print(f"[INIT] Logs guardados en: {log_file}")
    except Exception as e:
        print(f"[ERROR] No se pudo configurar file handler: {e}")
    
    # ===== HANDLER: Consola (simple, sin colores) =====
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # ===== Loggers específicos por módulo =====
    # Reduce verbosidad de librerías externas
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Logs detallados para nuestros módulos
    logging.getLogger("app").setLevel(logging.DEBUG)
    logging.getLogger("app.crud").setLevel(logging.DEBUG)
    logging.getLogger("app.routers").setLevel(logging.DEBUG)
    logging.getLogger("app.utils").setLevel(logging.DEBUG)
    
    _logging_configured = True
    
    return root_logger

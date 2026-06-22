"""
Configuración centralizada de la aplicación FastAPI.

Este módulo gestiona todas las variables de configuración y de entorno,
manteniendo separadas las configuraciones por ambiente (desarrollo, producción).
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Clase de configuración que carga variables de entorno.
    
    Attributes:
        db_host: Dirección del servidor PostgreSQL
        db_port: Puerto del servidor PostgreSQL
        db_user: Usuario de la base de datos
        db_password: Contraseña de la base de datos
        db_name: Nombre de la base de datos
        api_title: Título de la API
        api_version: Versión de la API
        debug: Modo debug
        environment: Ambiente de ejecución (development, production)
    """
    
    # Base de Datos
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_name: str = os.getenv("DB_NAME", "dusty_monitor")
    
    # API
    api_title: str = os.getenv("API_TITLE", "Dusty Monitor - Air Quality IoT API")
    api_version: str = os.getenv("API_VERSION", "v1.0.0")
    api_prefix: str = "/api/v1"
    
    # Ambiente
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Configuraciones de negocio
    device_connection_timeout_minutes: int = 3  # Minutos para considerar un dispositivo desconectado
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def database_url(self) -> str:
        """
        Construye la URL de conexión a PostgreSQL.
        
        Returns:
            str: URL de conexión en formato postgresql://user:password@host:port/dbname
        """
        return (
            f"postgresql://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )


# Instancia global de configuración
settings = Settings()

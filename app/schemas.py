"""
Esquemas Pydantic para validación de datos de entrada y salida.

Define la estructura de los payloads de la API REST.
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class DispositivoBase(BaseModel):
    """Esquema base para dispositivos (campos comunes)."""
    id: str = Field(..., min_length=1, max_length=50, description="ID único del dispositivo")
    nombre: str = Field(..., min_length=1, max_length=255, description="Nombre del dispositivo")
    ubicacion: str = Field(..., min_length=1, max_length=255, description="Ubicación física")
    limite_co2: int = Field(default=900, gt=0, description="Límite CO2 en ppm")
    limite_pm25: int = Field(default=25, gt=0, description="Límite PM2.5 en µg/m³")


class DispositivoCreate(DispositivoBase):
    """Esquema para crear un dispositivo."""
    pass


class DispositivoResponse(DispositivoBase):
    """Esquema de respuesta para dispositivos."""
    ultimo_contacto: Optional[datetime] = Field(None, description="Último contacto con el dispositivo")
    
    class Config:
        from_attributes = True


class LecturaBase(BaseModel):
    """Esquema base para lecturas de sensores."""
    dispositivo_id: str = Field(..., description="ID del dispositivo")
    temperatura: Optional[Decimal] = Field(None, ge=-40, le=60, description="Temperatura en °C")
    humedad: Optional[Decimal] = Field(None, ge=0, le=100, description="Humedad relativa %")
    pm1_0: Optional[Decimal] = Field(None, ge=0, description="PM1.0 µg/m³")
    pm2_5: Optional[Decimal] = Field(None, ge=0, description="PM2.5 µg/m³")
    pm4_0: Optional[Decimal] = Field(None, ge=0, description="PM4.0 µg/m³")
    pm10: Optional[Decimal] = Field(None, ge=0, description="PM10 µg/m³")
    voc: Optional[int] = Field(None, ge=0, description="VOCs en ppb")
    co2: Optional[int] = Field(None, ge=0, description="CO2 en ppm")


class LecturaCreate(LecturaBase):
    """Esquema para registrar una nueva lectura (desde ESP32)."""
    pass


class LecturaResponse(LecturaBase):
    """Esquema de respuesta para lecturas."""
    id: int = Field(..., description="ID único de la lectura")
    fecha_hora: datetime = Field(..., description="Timestamp de la lectura")
    
    class Config:
        from_attributes = True


class EstadoDispositivo(BaseModel):
    """Esquema para estado actual del dispositivo."""
    dispositivo_id: str
    conectado: bool = Field(..., description="True si el dispositivo está conectado")
    minutos_sin_contacto: int = Field(..., description="Minutos desde último contacto")


class LecturaActualResponse(BaseModel):
    """Esquema para respuesta de última lectura actual."""
    lectura: Optional[LecturaResponse] = None
    estado_dispositivo: EstadoDispositivo


class AlertaBase(BaseModel):
    """Esquema base para alertas."""
    dispositivo_id: str
    variable_afectada: str = Field(..., description="Variable que disparó alerta (PM2.5, CO2)")
    valor_detectado: Decimal
    nivel_critico: str = Field(..., pattern="^(ALTA|MEDIA)$", description="ALTA o MEDIA")


class AlertaResponse(AlertaBase):
    """Esquema de respuesta para alertas."""
    id: int
    fecha_hora: datetime
    resuelto: bool
    
    class Config:
        from_attributes = True


class MisionBase(BaseModel):
    """Esquema base para misiones."""
    titulo: str = Field(..., min_length=1, max_length=255)
    categoria: str = Field(..., min_length=1, max_length=100)
    progreso: int = Field(default=0, ge=0, le=100)
    descripcion: Optional[str] = None


class MisionCreate(MisionBase):
    """Esquema para crear una misión."""
    pass


class MisionResponse(MisionBase):
    """Esquema de respuesta para misiones."""
    id: int
    activa: bool
    
    class Config:
        from_attributes = True


class EstadisticasResponse(BaseModel):
    """Esquema de respuesta para estadísticas."""
    filtro: str
    periodo: str
    datos: List[dict] = Field(..., description="Datos agrupados por tiempo")
    total_lecturas: int


class ErrorResponse(BaseModel):
    """Esquema estándar para respuestas de error."""
    detail: str = Field(..., description="Descripción del error")
    status_code: int = Field(..., description="Código HTTP de error")

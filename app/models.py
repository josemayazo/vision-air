"""
Modelos ORM de SQLAlchemy para la base de datos PostgreSQL.

Define las tablas y sus relaciones según el modelo de datos especificado.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text, Index, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base


class Dispositivo(Base):
    """
    Modelo para dispositivos IoT (sensores ESP32).
    
    Attributes:
        id: Identificador único del dispositivo (ej: ESP32_AULA_1)
        nombre: Nombre descriptivo del sensor
        ubicacion: Ubicación física del dispositivo
        limite_co2: Límite de CO2 en ppm (default: 900)
        limite_pm25: Límite de PM2.5 en µg/m³ (default: 25)
        ultimo_contacto: Último timestamp de comunicación con el dispositivo
        lecturas: Relación con las lecturas registradas
        alertas: Relación con el historial de alertas
    """
    __tablename__ = "dispositivos"
    
    id = Column(String(50), primary_key=True, unique=True, nullable=False)
    nombre = Column(String(255), nullable=False)
    ubicacion = Column(String(255), nullable=False)
    limite_co2 = Column(Integer, default=900, nullable=False)
    limite_pm25 = Column(Integer, default=25, nullable=False)
    ultimo_contacto = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    lecturas = relationship("Lectura", back_populates="dispositivo", cascade="all, delete-orphan")
    alertas = relationship("HistorialAlerta", back_populates="dispositivo", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Dispositivo(id={self.id}, nombre={self.nombre})>"


class Lectura(Base):
    """
    Modelo para las lecturas de sensores (registradas cada minuto).
    
    Attributes:
        id: Identificador único autoincremental
        dispositivo_id: FK a la tabla dispositivos
        fecha_hora: Timestamp de la lectura
        temperatura: Temperatura en °C
        humedad: Humedad relativa en %
        pm1_0: Partículas PM1.0 en µg/m³
        pm2_5: Partículas PM2.5 en µg/m³
        pm4_0: Partículas PM4.0 en µg/m³
        pm10: Partículas PM10 en µg/m³
        voc: Compuestos Orgánicos Volátiles (ppb)
        co2: Dióxido de Carbono (ppm)
        dispositivo: Relación con el dispositivo
    """
    __tablename__ = "lecturas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dispositivo_id = Column(String(50), ForeignKey("dispositivos.id"), nullable=False)
    fecha_hora = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    temperatura = Column(Numeric(4, 2), nullable=True)
    humedad = Column(Numeric(5, 2), nullable=True)
    pm1_0 = Column(Numeric(5, 2), nullable=True)
    pm2_5 = Column(Numeric(5, 2), nullable=True)
    pm4_0 = Column(Numeric(5, 2), nullable=True)
    pm10 = Column(Numeric(5, 2), nullable=True)
    voc = Column(Integer, nullable=True)
    co2 = Column(Integer, nullable=True)
    
    # Relaciones
    dispositivo = relationship("Dispositivo", back_populates="lecturas")
    
    # Índice compuesto para optimizar consultas temporales
    __table_args__ = (
        Index('idx_lecturas_dispositivo_fecha', 'dispositivo_id', 'fecha_hora'),
    )
    
    def __repr__(self):
        return f"<Lectura(id={self.id}, dispositivo_id={self.dispositivo_id}, fecha_hora={self.fecha_hora})>"


class HistorialAlerta(Base):
    """
    Modelo para el historial de alertas generadas por exceso de contaminación.
    
    Attributes:
        id: Identificador único autoincremental
        dispositivo_id: FK a la tabla dispositivos
        fecha_hora: Timestamp de la alerta
        variable_afectada: Variable que disparó la alerta (ej: "PM2.5", "CO2")
        valor_detectado: Valor medido que superó el límite
        nivel_critico: Nivel de severidad ("ALTA", "MEDIA")
        resuelto: Indica si la alerta ha sido resuelta
        dispositivo: Relación con el dispositivo
    """
    __tablename__ = "historial_alertas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dispositivo_id = Column(String(50), ForeignKey("dispositivos.id"), nullable=False)
    fecha_hora = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    variable_afectada = Column(String(50), nullable=False)  # PM2.5, CO2, etc
    valor_detectado = Column(Numeric(10, 2), nullable=False)  # Permite hasta 99999.99 (CO2 1200, PM25 45.8, etc)
    nivel_critico = Column(String(10), nullable=False)  # ALTA, MEDIA
    resuelto = Column(Boolean, default=False, nullable=False)
    
    # Relaciones
    dispositivo = relationship("Dispositivo", back_populates="alertas")
    
    def __repr__(self):
        return f"<HistorialAlerta(id={self.id}, dispositivo_id={self.dispositivo_id}, variable={self.variable_afectada})>"


class MisionUsuario(Base):
    """
    Modelo para las misiones de gamificación en la UI.
    
    Attributes:
        id: Identificador único autoincremental
        titulo: Título de la misión
        categoria: Categoría educativa (ej: "STEM Ciencias")
        progreso: Porcentaje de progreso (0-100)
        activa: Indica si la misión está activa
        descripcion: Descripción detallada de la misión
    """
    __tablename__ = "misiones_usuario"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(255), nullable=False)
    categoria = Column(String(100), nullable=False)
    progreso = Column(Integer, default=0, nullable=False)  # 0-100
    activa = Column(Boolean, default=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<MisionUsuario(id={self.id}, titulo={self.titulo}, progreso={self.progreso}%)>"

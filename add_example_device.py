"""
Script para agregar un dispositivo de ejemplo a la base de datos.
Ejecutar: python add_example_device.py
"""

from datetime import datetime
from sqlalchemy.orm import sessionmaker
from app.database import engine, Base
from app.models import Dispositivo

# Crear las tablas si no existen
Base.metadata.create_all(bind=engine)

# Crear sesión
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Verificar si el dispositivo ya existe
    dispositivo_existente = session.query(Dispositivo).filter_by(id="ESP32_AULA_1").first()
    
    if dispositivo_existente:
        print("❌ El dispositivo ESP32_AULA_1 ya existe")
        session.close()
        exit()
    
    # Crear dispositivo de ejemplo
    dispositivo = Dispositivo(
        id="ESP32_AULA_1",
        nombre="Sensor de Aula 1",
        ubicacion="Aula de Clase - Piso 2",
        limite_co2=900,
        limite_pm25=25,
        ultimo_contacto=datetime.now()
    )
    
    # Agregar a la sesión y guardar
    session.add(dispositivo)
    session.commit()
    
    print("✅ Dispositivo agregado exitosamente:")
    print(f"   ID: {dispositivo.id}")
    print(f"   Nombre: {dispositivo.nombre}")
    print(f"   Ubicación: {dispositivo.ubicacion}")
    print(f"   Límite CO2: {dispositivo.limite_co2} ppm")
    print(f"   Límite PM2.5: {dispositivo.limite_pm25} µg/m³")
    
except Exception as e:
    session.rollback()
    print(f"❌ Error al agregar dispositivo: {e}")
    
finally:
    session.close()

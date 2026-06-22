"""
Script para inicializar y probar la API localmente.

Ejecutar: python setup_dev.py
"""

import os
import sys
import subprocess
from pathlib import Path

def crear_archivo_env():
    """Crea archivo .env si no existe."""
    env_path = Path(".env")
    if not env_path.exists():
        print("📝 Creando archivo .env...")
        env_content = """# ============================================================
# Configuración de Base de Datos
# ============================================================
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=tu_contraseña_segura_aqui
DB_NAME=dusty_monitor

# ============================================================
# Configuración de API
# ============================================================
API_TITLE=Dusty Monitor - Air Quality IoT API
API_VERSION=v1.0.0
DEBUG=True
LOG_LEVEL=INFO
ENVIRONMENT=development

# ============================================================
# Notas:
# - DEBUG=True solo para desarrollo
# - Cambiar DB_PASSWORD a algo seguro
# - En producción: DEBUG=False, ENVIRONMENT=production
# ============================================================
"""
        with open(env_path, "w") as f:
            f.write(env_content)
        print("✅ Archivo .env creado. Actualiza las credenciales de BD.")
    else:
        print("✅ Archivo .env ya existe")

def instalar_dependencias():
    """Instala las dependencias del proyecto."""
    print("\n📦 Instalando dependencias...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencias instaladas")
    except subprocess.CalledProcessError:
        print("❌ Error al instalar dependencias")
        sys.exit(1)

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║      🌍 Dusty Monitor - API Setup Script 🌍             ║
    ║              Air Quality IoT Monitoring                  ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Crear .env
    crear_archivo_env()
    
    # Instalar dependencias
    instalar_dependencias()
    
    print("""
    ✨ ¡Setup completado! Próximos pasos:
    
    1. Edita el archivo .env con tus credenciales de PostgreSQL
    2. Crea la base de datos:
       createdb dusty_monitor
    3. Ejecuta las migraciones:
       psql -U postgres -d dusty_monitor -f migrations/001_initial_schema.sql
    4. Inicia la API:
       python main.py
    5. Accede a la documentación:
       http://localhost:8000/docs
    
    📚 Documentación: Ver README.md
    🏗️  Arquitectura: Ver ARQUITECTURA.md
    """)

if __name__ == "__main__":
    main()

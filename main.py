"""
Script de entrada para ejecutar la aplicación FastAPI.

Se utiliza con: python main.py
O con uvicorn: uvicorn main:app --reload
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )

"""
Script de entrada para ejecutar la aplicación FastAPI.

Se utiliza con: python main.py
O con uvicorn: uvicorn main:app --reload
"""

import uvicorn
from app.config import settings
import os

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )

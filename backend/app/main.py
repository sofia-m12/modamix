from fastapi import FastAPI
from app.api.routes import health, imports, searches
app = FastAPI(title="ModaMix API", version="0.1.0")
app.include_router(health.router)
app.include_router(imports.router, prefix="/api")
app.include_router(searches.router, prefix="/api")

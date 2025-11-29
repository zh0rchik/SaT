from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routes import (
    troops_routes, branches_routes, medexams_routes, work_mode_routes,
    recruitment_offices_router, recruitments_router, auth_routes
)

app = FastAPI()

# API маршруты
app.include_router(auth_routes.router)
app.include_router(branches_routes.router)
app.include_router(troops_routes.router)
app.include_router(medexams_routes.router)
app.include_router(recruitment_offices_router.router)
app.include_router(work_mode_routes.router)
app.include_router(recruitments_router.router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Путь к собранному фронтенду
frontend_path = Path(__file__).parent / "frontend" / "dist"

# Раздаём весь фронтенд как статику по корню
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

# Инициализация БД
@app.on_event("startup")
async def startup_event():
    await init_db()

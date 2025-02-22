from fastapi import FastAPI
from app.database import init_db
from app.routes import (troops_routes, branches_routes, medexams_routes,
                        recruitment_offices_router, recruitments_router)
from fastapi.staticfiles import StaticFiles

# Создаем экземпляр FastAPI
app = FastAPI()
app.include_router(branches_routes.router)
app.include_router(troops_routes.router)
app.include_router(medexams_routes.router)
app.include_router(recruitment_offices_router.router)
app.include_router(recruitments_router.router)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Инициализация базы данных при запуске приложения
@app.on_event("startup")
async def startup():
    await init_db()

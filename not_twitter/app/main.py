"""Основные энпоинты приложения."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from not_twitter.app.config_data.users_config import users_data
from not_twitter.app.database import crud_operations, database
from not_twitter.app.endpoints import followings, likes, medias, tweets, user_profiles

app = FastAPI()
app.include_router(followings.router)
app.include_router(likes.router)
app.include_router(medias.router)
app.include_router(tweets.router)
app.include_router(user_profiles.router)
app.mount('/', StaticFiles(directory='static', html=True))


@app.on_event("startup")
async def startup():
    """Первоначальная настройка перед запуском приложения."""
    await database.init_db()
    await crud_operations.fill_db(users_data)


@app.on_event("shutdown")
async def shutdown():
    """Завершение работы приложения."""
    await database.shutdown_db()

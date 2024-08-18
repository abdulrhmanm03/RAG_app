from fastapi import APIRouter, Depends

from src.utils.config import Settings, get_settings

base_router = APIRouter()


@base_router.get("/")
async def helloworld(app_settings: Settings = Depends(get_settings)):
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION
    return {
        "app_name": app_name,
        "app_version": app_version,
    }

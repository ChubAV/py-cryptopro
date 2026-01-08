from contextlib import asynccontextmanager
from contextvars import ContextVar
from injector import Injector
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from logging import Logger


from .endpoints_api import api_router
from .endpoints_html import html_router

from .containers import ApplicationContainer
from .config import Settings, init_settings
from .services import (
    import_all_secretkeys,
    import_all_certificate,
    set_license_crypto_pro,
)
from .middleware import APIKeyMiddleware, UUIDMiddleware

request_id: ContextVar[str] = ContextVar("request_id", default="")


class FastAPICryptoPro(FastAPI):
    """Класс FastAPI с настройками"""

    def __init__(self, container: Injector, lifespan) -> None:
        self.container = container
        settings = container.get(Settings)
        super(FastAPICryptoPro, self).__init__(
            title=settings.app_name, lifespan=lifespan, debug=settings.debug
        )
        self.mount("/static", StaticFiles(directory=settings.static_dir), name="static")


@asynccontextmanager
async def lifespan(app: FastAPICryptoPro):
    """Настройки экземпляра приложения при запуске"""
    logger = app.container.get(Logger)
    settings = app.container.get(Settings)

    logger.debug("starting application")

    import_all_certificate(settings.import_certificates_dir)
    import_all_secretkeys(settings.import_secretkeys_dir, settings.secretkeys_dir)

    if settings.license_crypto_pro is not None:
        set_license_crypto_pro(settings.license_crypto_pro)

    yield

    logger.debug("stoping application")


def create_app():
    """конструктор экземпляра приложения"""
    application = FastAPICryptoPro(
        Injector([init_settings, ApplicationContainer()]), lifespan=lifespan
    )
    settings = application.container.get(Settings)

    application.add_middleware(UUIDMiddleware, request_id=request_id)

    if settings.api_key is not None:
        application.add_middleware(APIKeyMiddleware, api_key=settings.api_key)

    """ Подключение роутеров """
    application.include_router(api_router)  # api роутер

    if settings.debug:
        application.include_router(html_router)  # html роутер

    return application


app = create_app()

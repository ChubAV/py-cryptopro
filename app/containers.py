from injector import Module, singleton, provider
from logging import Logger
from fastapi.templating import Jinja2Templates


from .loggers import create_app_logger
from .config import Settings


class ApplicationContainer(Module):
    @singleton
    @provider
    def provide_app_logger(self, settings: Settings) -> Logger:
        return create_app_logger(settings.debug, settings.log_dir)

    @singleton
    @provider
    def provide_templates(self, settings: Settings) -> Jinja2Templates:
        return Jinja2Templates(directory=settings.templates_dir)

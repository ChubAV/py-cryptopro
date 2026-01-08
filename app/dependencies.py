from logging import Logger
import re
from pathlib import Path
from typing import Annotated, Callable
from fastapi import Request, Depends
from .config import Settings
from fastapi.templating import Jinja2Templates


from .constants import ResultStatus
from .schemas import ResponseSchema, ErrorSchema, ResponseListDataSchema
from .utils import crypto_pro_description_error


def get_settings(request: Request) -> Settings:
    return request.app.container.get(Settings)


def get_import_certificates_dir(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Path:
    return settings.import_certificates_dir


def get_templates(request: Request) -> Jinja2Templates:
    return request.app.container.get(Jinja2Templates)


def get_menu(settings: Annotated[Settings, Depends(get_settings)]):
    return settings.html_menu


def get_context(settings: Annotated[Settings, Depends(get_settings)]):
    return {
        "menu": settings.html_menu,
        "backend_url": settings.backend_url,
        "api_key": settings.api_key,
    }


class ResponseWrapperBase:
    def __init__(self, func: Callable):
        self.func = func

    def wrap_ok(self, data, *args, **kwargs):
        if isinstance(data, list):
            try:
                if isinstance(kwargs.get("offset"), int):
                    offset = kwargs.get("offset")
                elif isinstance(args[1], int):
                    offset = args[1]
                else:
                    offset = 0
            except Exception:
                offset = 0

            result = ResponseSchema(
                result=ResultStatus.success,
                details=ResponseListDataSchema(
                    data=data,
                    offset=offset,  # type: ignore
                    count=len(data),
                ),
            )
        else:
            result = ResponseSchema(result=ResultStatus.success, details=data)
        return result

    def wrap_error(self, e, *args, **kwargs):
        pattern_error_code = r"0x[0-9A-Za-z]{8}"
        result_search_error_code = re.search(pattern_error_code, str(e))
        if result_search_error_code is not None:
            description = crypto_pro_description_error(
                result_search_error_code[0], str(e)
            )
            return ResponseSchema(
                result=ResultStatus.error,
                details=ErrorSchema(
                    code=result_search_error_code[0], description=description
                ),
            )
        else:
            return ResponseSchema(
                result=ResultStatus.error,
                details=ErrorSchema(code="Без кода", description=str(e)),
            )

    def format_params_for_log(self, *args, **kwargs):
        if len(args) > 0:
            args_for_log = "; ".join([f"[{n}]->{v}" for n, v in enumerate(args)])
        else:
            args_for_log = "no args params"

        if len(kwargs) > 0:
            kwargs_for_log = "; ".join([f"[{k}]->{v}" for k, v in kwargs.items()])
        else:
            kwargs_for_log = "no kwargs params"
        return args_for_log, kwargs_for_log


class ResponseWrapper(ResponseWrapperBase):
    def __call__(self, request: Request) -> Callable:
        from .main import request_id

        logger = request.app.container.get(Logger)

        def innerfunc(*args, **kwargs):
            try:
                params_for_log = self.format_params_for_log(*args, **kwargs)
                id = request_id.get()

                logger.debug(
                    f"ID {id}. Call function -> {self.func.__name__} args params: {params_for_log[0]} and kwargs params: {params_for_log[1]}"
                )
                data = self.func(*args, **kwargs)
                logger.debug(f"ID {id}. Result function -> OK")

                return self.wrap_ok(data, *args, **kwargs)
            except Exception as e:
                logger.error(f"ID {id}. Error {e}")
                return self.wrap_error(e, *args, **kwargs)

        return innerfunc


class ResponseWrapperAsync(ResponseWrapperBase):
    def __call__(self, request: Request) -> Callable:
        from .main import request_id

        logger = request.app.container.get(Logger)

        async def innerfunc(*args, **kwargs):
            try:
                params_for_log = self.format_params_for_log(*args, **kwargs)
                id = request_id.get()

                logger.debug(
                    f"ID {id}. Call function -> {self.func.__name__} args params: {params_for_log[0]} and kwargs params: {params_for_log[1]}"
                )
                data = await self.func(*args, **kwargs)
                logger.debug(f"ID {id}. Result function -> OK")
                return self.wrap_ok(data, *args, **kwargs)
            except Exception as e:
                logger.error(f"ID {id}. Error {e}")
                return self.wrap_error(e, *args, **kwargs)

        return innerfunc

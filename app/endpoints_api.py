from typing import Annotated
import io
from fastapi import APIRouter, Form, UploadFile, File, Query, Depends
from fastapi.responses import StreamingResponse
from pathlib import Path
from .services import (
    get_system_info,
    get_hash,
    get_certificates_from_store,
    save_certificate_in_folder,
    import_certificate_from_file,
    find_certificate_by_thumbprint,
    get_object_certificate_by_thumbprint,
    set_license_crypto_pro,
    verify,
    verify_xml,
    sign as sing_service,
    sign_xml,
)
from .schemas import (
    ResponseSchema,
    SystemInfoSchema,
    HashedDataSchema,
    CertificateSchema,
    ResponseListDataSchema,
    SingSchema,
    ErrorSchema,
)

from .constants import ResultStatus, AlgorithmHash, StoreName
from .dependencies import (
    get_import_certificates_dir,
    ResponseWrapper,
    ResponseWrapperAsync,
)
from .utils import convert_to_io

api_router = APIRouter(prefix="/api")


@api_router.get(
    "/systeminfo/",
    response_model=ResponseSchema[SystemInfoSchema | ErrorSchema],
    summary="Информация о системе",
    description="Информация о системе - Версия КриптоПро, версия SDK, верия pycades, версия Python, Версия ОС",
)
def system_info(
    service=Depends(ResponseWrapper(get_system_info)),
) -> ResponseSchema[SystemInfoSchema | ErrorSchema]:
    result = service()
    return result


@api_router.post(
    "/set_license/",
    response_model=ResponseSchema[bool | ErrorSchema],
    summary="Установка лицензии КриптоПро",
    description="Установка лицензии КриптоПро",
)
def set_license(
    license: str, service=Depends(ResponseWrapper(set_license_crypto_pro))
) -> ResponseSchema[bool | ErrorSchema]:
    result = service(license)
    return result


@api_router.post(
    "/hash/txt/",
    response_model=ResponseSchema[HashedDataSchema | ErrorSchema],
    summary="Хэш строки",
    description="Хэш строки - получить хэш строки",
)
def get_hash_txt(
    text: str = Form(...),
    algorithm: AlgorithmHash = Form(
        default=AlgorithmHash.CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256,
        description="Алгоритм хэширования",
    ),
    service=Depends(ResponseWrapper(get_hash)),
) -> ResponseSchema[HashedDataSchema | ErrorSchema]:
    result = service(text, algorithm)
    return result


@api_router.post(
    "/hash/file/",
    response_model=ResponseSchema[HashedDataSchema | ErrorSchema],
    summary="Хэш файла",
    description="Хэш файла - получить хэш файла",
)
async def get_hash_file(
    file: UploadFile = File(default=..., description="Файл данных"),
    algorithm: AlgorithmHash = Query(
        default=AlgorithmHash.CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256,
        description="Алгоритм хэширования",
    ),
    service=Depends(ResponseWrapper(get_hash)),
) -> ResponseSchema[HashedDataSchema | ErrorSchema]:
    data = await file.read()
    result = service(data, algorithm)
    return result


@api_router.get(
    "/certificates/",
    response_model=ResponseSchema[ResponseListDataSchema | ErrorSchema],
    summary="Получить список сертификатов",
    description="Получить список сертификатов установленных в системе",
)
def get_certificates(
    store: StoreName = StoreName.CAPICOM_ROOT_ALL,
    offset: int = 0,
    limit: int = 10,
    service=Depends(ResponseWrapper(get_certificates_from_store)),
) -> ResponseSchema[ResponseListDataSchema[CertificateSchema] | ErrorSchema]:
    result = service(store, offset, limit)
    return result


@api_router.post(
    "/certificates/",
    response_model=ResponseSchema[bool | ErrorSchema],
    summary="Импорт сертификата в хранилище",
    description="Импорт сертификата в хранилище",
)
async def import_certificates(
    import_certificates_dir: Annotated[Path, Depends(get_import_certificates_dir)],
    file: UploadFile = File(default=..., description="Файл сертификата"),
    store: StoreName = Query(
        default=StoreName.CAPICOM_MY_STORE, description="Хранилище"
    ),
    service_save=Depends(ResponseWrapperAsync(save_certificate_in_folder)),
    service_import=Depends(ResponseWrapper(import_certificate_from_file)),
) -> ResponseSchema[bool | ErrorSchema]:
    data: bytes = await file.read()

    result_save = await service_save(
        data, import_certificates_dir, file.filename, store
    )

    if result_save.result == ResultStatus.error:
        return result_save

    result_import = service_import(result_save.details, store)

    return result_import


@api_router.get(
    "/certificates/{thumbprint}/",
    response_model=ResponseSchema[CertificateSchema | ErrorSchema | None],
    summary="Получить серитифика по thumbprint(отпечаток)",
    description="Получить серитифика по thumbprint(отпечаток)",
)
async def get_certificate(
    thumbprint: str,
    service=Depends(ResponseWrapper(find_certificate_by_thumbprint)),
) -> ResponseSchema[CertificateSchema | ErrorSchema | None]:
    result = service(thumbprint)
    return result


################################################################


@api_router.post(
    "/sign/s2s/",
    response_model=ResponseSchema[str | ErrorSchema],
    summary="Создать ЭЦП - строка -> строка",
    description="Создание электронной цифровой подписи. Входные данные: строка данных, Выходные данные -> строка подписи",
)
async def sign_s2s(
    data: str = Form(..., description="Данные"),
    thumbprint: str = Form(..., description="Отпечаток сертификата"),
    service_cert=Depends(ResponseWrapper(get_object_certificate_by_thumbprint)),
    service_sign=Depends(ResponseWrapper(sing_service)),
) -> ResponseSchema[str | ErrorSchema]:
    """
    Создание подписи
    строка данных + строка подписи
    """
    cert_result = service_cert(thumbprint, "All")

    if cert_result.result == ResultStatus.error:
        return cert_result

    result = service_sign(data, cert_result.details, detached=True, binary=False)

    return result


################################################################


@api_router.post(
    "/sign/s/",
    response_model=ResponseSchema[str | ErrorSchema],
    summary="Создать ЭЦП - строка с пописью внутри",
    description="Создание электронной цифровой подписи. Входные данные: строка данных, Выходные данные -> строка с подписью внутри",
)
async def sign_s(
    data: str = Form(..., description="Данные"),
    thumbprint: str = Form(..., description="Отпечаток сертификата"),
    service_cert=Depends(ResponseWrapper(get_object_certificate_by_thumbprint)),
    service_sign=Depends(ResponseWrapper(sing_service)),
) -> ResponseSchema[str | ErrorSchema]:
    """
    Создание подписи
    строка данных -> строка c подписью внутри
    """

    cert_result = service_cert(thumbprint, "All")
    if cert_result.result == ResultStatus.error:
        return cert_result

    result_sign = service_sign(data, cert_result.details, detached=False)
    if result_sign.result == ResultStatus.error:
        return result_sign

    if not isinstance(result_sign.details, str):
        raise

    return result_sign


################################################################


@api_router.post(
    "/sign/f2f/",
    # response_model=ResponseSchema[SingSchema|None],
    summary="Создать ЭЦП - файл -> файл",
    description="Создание электронной цифровой подписи. Входные данные: файл данных, Выходные данные -> файл подписи",
)
async def sign_f2f(
    file: UploadFile = File(default=..., description="Файл данных"),
    thumbprint: str = Form(..., description="Отпечаток сертификата"),
    service_cert=Depends(ResponseWrapper(get_object_certificate_by_thumbprint)),
    service_sign=Depends(ResponseWrapper(sing_service)),
) -> StreamingResponse:
    """
    Создание подписи
    файл + файл подписи
    """

    cert_result = service_cert(thumbprint, "All")
    if cert_result.result == ResultStatus.error:
        return cert_result

    data = await file.read()

    result_sign = service_sign(data, cert_result.details, detached=True, binary=True)

    if result_sign.result == ResultStatus.error:
        return result_sign

    headers = {
        "Content-Disposition": "attachment; filename=sign.sig",
        "Content-Type": "application/octet-stream",
    }

    sign_file = convert_to_io(result_sign.details)

    return StreamingResponse(
        sign_file, headers=headers, media_type="application/octet-stream"
    )


################################################################
@api_router.post(
    "/sign/f2s/",
    response_model=ResponseSchema[str | ErrorSchema],
    summary="Создать ЭЦП - файл -> строка",
    description="Создание электронной цифровой подписи. Входные данные: файл данных, Выходные данные -> строка подписи",
)
async def sign_f2s(
    file: UploadFile = File(default=..., description="Файл данных"),
    thumbprint: str = Form(..., description="Отпечаток сертификата"),
    service_cert=Depends(ResponseWrapper(get_object_certificate_by_thumbprint)),
    service_sign=Depends(ResponseWrapper(sing_service)),
) -> ResponseSchema[str | ErrorSchema]:
    """
    Создание подписи
    файл + строка подписи
    """
    cert_result = service_cert(thumbprint, "All")
    if cert_result.result == ResultStatus.error:
        return cert_result

    data = await file.read()

    result_sign = service_sign(data, cert_result.details, detached=True, binary=False)

    if result_sign.result == ResultStatus.error:
        return result_sign

    if not isinstance(result_sign.details, str):
        raise

    return result_sign


################################################################


@api_router.post(
    "/sign/f/",
    # response_model=ResponseSchema[SingSchema|None],
    summary="Создать ЭЦП - файл с подписью внутри",
    description="Создание электронной цифровой подписи. Входные данные: файл данных, Выходные данные ->файл с подписью внутри",
)
async def sign_f(
    file: UploadFile = File(default=..., description="Файл данных"),
    thumbprint: str = Form(..., description="Отпечаток сертификата"),
    service_cert=Depends(ResponseWrapper(get_object_certificate_by_thumbprint)),
    service_sign=Depends(ResponseWrapper(sing_service)),
) -> StreamingResponse:
    """
    Создание подписи
    файл -> файл с подписью внутри
    """
    cert_result = service_cert(thumbprint, "All")
    if cert_result.result == ResultStatus.error:
        return cert_result

    data = await file.read()

    result_sign = service_sign(data, cert_result.details, detached=False, binary=True)
    if result_sign.result == ResultStatus.error:
        return result_sign

    headers = {
        "Content-Disposition": "attachment; filename=sign.sig",
        "Content-Type": "application/octet-stream",
    }

    sign_file = convert_to_io(result_sign.details)

    return StreamingResponse(
        sign_file, headers=headers, media_type="application/octet-stream"
    )


################################################################


@api_router.post(
    "/sign/xml2f/",
    # response_model=ResponseSchema[SingSchema|None],
    summary="Создать ЭЦП - xml файл",
    description="Создание электронной цифровой подписи. Входные данные: xml файл данных, Выходные данные -> xml файл с подписью внутри",
)
async def sign_xml2f(
    file: UploadFile = File(default=..., description="Файл данных"),
    thumbprint: str = Form(..., description="Отпечаток сертификата"),
    service_cert=Depends(ResponseWrapper(get_object_certificate_by_thumbprint)),
    service_sign=Depends(ResponseWrapper(sign_xml)),
) -> StreamingResponse:
    """
    Создание подписи
    файл -> файл с подписью внутри
    """
    # cert = get_object_certificate_by_thumbprint(thumbprint, 'All')
    cert_result = service_cert(thumbprint, "All")
    if cert_result.result == ResultStatus.error:
        return cert_result

    data = await file.read()
    data = data.decode("utf-8")

    result_sign = service_sign(data, cert_result.details)
    if result_sign.result == ResultStatus.error:
        return result_sign

    sign_file = io.StringIO(result_sign.details)

    headers = {
        "Content-Disposition": "attachment; filename=sign.xml",
        "Content-Type": "application/octet-stream",
    }

    return StreamingResponse(
        sign_file, headers=headers, media_type="application/octet-stream"
    )




################################################################
@api_router.post(
    "/sign/hash2s/",
    response_model=ResponseSchema[str | ErrorSchema],
    summary="Создать ЭЦП - на основе хэша",
    description="Создание электронной цифровой подписи. Входные данные: хэш данных, Выходные данные -> строка подписи",
)
async def sign_hash2s(
    hash: str = Form(..., description="Хэш"),
    thumbprint: str = Form(..., description="Отпечаток сертификата"),
    service_cert=Depends(ResponseWrapper(get_object_certificate_by_thumbprint)),
    service_sign=Depends(ResponseWrapper(sing_service)),
):
    """
    Создание подписи
    хэш -> строка c подписью внутри
    """

    cert_result = service_cert(thumbprint, "All")
    if cert_result.result == ResultStatus.error:
        return cert_result

    result_sign = service_sign(hash, cert_result.details, is_hash=True, binary=False)
    if result_sign.result == ResultStatus.error:
        return result_sign

    if not isinstance(result_sign.details, str):
        raise

    return result_sign



################################################################
@api_router.post(
    "/sign/hash2f/",
    # response_model=ResponseSchema[str | ErrorSchema],
    summary="Создать ЭЦП - на основе хэша",
    description="Создание электронной цифровой подписи. Входные данные: хэш данных, Выходные данные -> файл подписи",
)
async def sign_hash2f(
    hash: str = Form(..., description="Хэш"),
    thumbprint: str = Form(..., description="Отпечаток сертификата"),
    service_cert=Depends(ResponseWrapper(get_object_certificate_by_thumbprint)),
    service_sign=Depends(ResponseWrapper(sing_service)),
) -> StreamingResponse:
    """
    Создание подписи
    хэш -> файл c подписью
    """

    cert_result = service_cert(thumbprint, "All")
    if cert_result.result == ResultStatus.error:
        return cert_result

    result_sign = service_sign(hash, cert_result.details, is_hash=True, binary=True)
    if result_sign.result == ResultStatus.error:
        return result_sign


    headers = {
        "Content-Disposition": "attachment; filename=sign.sig",
        "Content-Type": "application/octet-stream",
    }

    sign_file = convert_to_io(result_sign.details)

    return StreamingResponse(
        sign_file, headers=headers, media_type="application/octet-stream"
    )

################################################################

@api_router.post(
    "/verify/f2f/",
    response_model=ResponseSchema[SingSchema | ErrorSchema],
    summary="Проверка ЭЦП - файл + файл",
    description="Проверка электронной цифровой подписи. Входные данные: файл данных + файл подписи",
)
async def f2f(
    file: UploadFile = File(default=..., description="Файл данных"),
    sign: UploadFile = File(default=..., description="Файл подписи"),
    service=Depends(ResponseWrapper(verify)),
) -> ResponseSchema[SingSchema | ErrorSchema]:
    """
    Проверка подписи
    файл + файл подписи
    """
    data = await file.read()
    sdata = await sign.read()
    result = service(data, sdata)
    return result


################################################################


@api_router.post(
    "/verify/f2s/",
    response_model=ResponseSchema[SingSchema | ErrorSchema],
    summary="Проверка ЭЦП - файл + строка",
    description="Проверка электронной цифровой подписи. Входные данные: файл данных + строка подписи",
)
async def f2s(
    file: UploadFile = File(default=..., description="Файл данных"),
    sign: str = Form(default=..., description="Файл подписи"),
    service=Depends(ResponseWrapper(verify)),
) -> ResponseSchema[SingSchema | ErrorSchema]:
    """
    Проверка подписи
    файл + строка подписи
    """
    data = await file.read()
    result = service(data, sign)
    return result


################################################################


@api_router.post(
    "/verify/f/",
    response_model=ResponseSchema[SingSchema | ErrorSchema],
    summary="Проверка ЭЦП - файл",
    description="Проверка электронной цифровой подписи. Входные данные: файл данных",
)
async def f(
    file: UploadFile = File(default=..., description="Файл данных"),
    service=Depends(ResponseWrapper(verify)),
) -> ResponseSchema[SingSchema | ErrorSchema]:
    """
    Проверка подписи
    файл
    """
    data = await file.read()
    result = service(data, None)
    return result


################################################################


@api_router.post(
    "/verify/s2s/",
    response_model=ResponseSchema[SingSchema | ErrorSchema],
    summary="Проверка ЭЦП - строка + строка",
    description="Проверка электронной цифровой подписи. Входные данные: строка данных + строка подписи",
)
async def s2s(
    data: str = Form(default=..., description="Данные"),
    sign: str = Form(default=..., description="Подпись"),
    service=Depends(ResponseWrapper(verify)),
) -> ResponseSchema[SingSchema | ErrorSchema]:
    """
    Проверка подписи
    строка данных + строка подписи
    """
    result = service(data, sign)
    return result


################################################################
@api_router.post(
    "/verify/s/",
    response_model=ResponseSchema[SingSchema | ErrorSchema],
    summary="Проверка ЭЦП - строка",
    description="Проверка электронной цифровой подписи. Входные данные: строка данных ",
)
async def s(
    data: str = Form(default=..., description="Данные"),
    service=Depends(ResponseWrapper(verify)),
) -> ResponseSchema[SingSchema | ErrorSchema]:
    """
    Проверка подписи
    строка данных
    """
    result = service(data, None)
    return result


################################################################


@api_router.post(
    "/verify/xml2f/",
    response_model=ResponseSchema[SingSchema | ErrorSchema],
    summary="Проверка ЭЦП - xml файл",
    description="Проверка электронной цифровой подписи. Входные данные: xml файл данных",
)
async def xml2f(
    file: UploadFile = File(default=..., description="Файл данных"),
    service=Depends(ResponseWrapper(verify_xml)),
) -> ResponseSchema[SingSchema | ErrorSchema]:
    """
    Проверка подписи
    XML файл
    """
    data = await file.read()
    data = data.decode("utf-8")
    result = service(data)
    return result

################################################################

@api_router.post(
    "/verify/hash2s/",
    response_model=ResponseSchema[SingSchema | ErrorSchema],
    summary="Проверка ЭЦП - хэш + строка",
    description="Проверка электронной цифровой подписи. Входные данные: хэш данных + строка подписи",
)
async def hash2s(
    hash: str = Form(default=..., description="Хэш"),
    sign: str = Form(default=..., description="Подпись"),
    service=Depends(ResponseWrapper(verify)),
):
    """
    Проверка подписи
    хэш + строка подписи
    """
    result = service(hash, sign, is_hash=True)
    return result


################################################################

@api_router.post(
    "/verify/hash2f/",
    response_model=ResponseSchema[SingSchema | ErrorSchema],
    summary="Проверка ЭЦП - хэш + файл",
    description="Проверка электронной цифровой подписи. Входные данные: хэш данных + файл подписи",
)
async def hash2f(
    hash: str = Form(default=..., description="Хэш"),
    sign: UploadFile = File(default=..., description="Файл подписи"),
    service=Depends(ResponseWrapper(verify)),
) -> ResponseSchema[SingSchema | ErrorSchema]:
    """
    Проверка подписи
    хэш + файл подписи
    """
    data = await sign.read()
    result = service(hash, data, is_hash=True)
    return result


################################################################
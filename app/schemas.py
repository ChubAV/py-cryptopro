from typing import TypeVar, Generic, Self, Any

import re
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    ValidationInfo,
    model_validator,
    EmailStr,
)
from datetime import datetime
from .constants import ResultStatus, StoreName

DetailsT = TypeVar("DetailsT")


class ErrorSchema(BaseModel):
    code: str = Field(title="Код ошибки")
    description: str = Field(title="Описание ошибки")


class SystemInfoSchema(BaseModel):
    """Информация о системе"""

    csp_version: str = Field(title="Версия Крипто-Про")
    sdk_version: str = Field(title="Версия SDK Крипто-Про")
    pycades_version: str = Field(title="Версия pycades")
    python_version: str = Field(title="Версия Python")
    platform_version: str = Field(title="Версия ОС")
    license_crypto_pro: str | None = Field(title="Лицензия КриптоПро", default=None)


class HashedDataSchema(BaseModel):
    """информация о  хэше"""

    hash: str = Field(title="Хэш")
    algorithm_code: int = Field(title="Код алгоритма хеширования")
    algorithm_name: str = Field(title="Наименование алгоритма хеширования")
    source: str = Field(title="Источник хэша (строка или файл)")


class SubjectSchema(BaseModel):
    CN: str = Field(
        title="CommonName -> наименование субъекта (владельца) сертификата, для личности это ФИО"
    )
    SN: str | None = Field(title="SurName -> Фамилия", default=None)
    G: str | None = Field(title="GivenName -> Имя и отчество", default=None)
    T: str | None = Field(
        title="Title -> должность владельца сертификата в указанной (O) организации",
        default=None,
    )
    O: str | None = Field(
        title="OrganizationName -> наименование организации владельца сертификата",
        default=None,
    )  # noqa: E741
    C: str = Field(
        title="CountryName -> наименование страны, содержит двухбуквенный код страны латинскими буквами: Россия = RU"
    )
    S: str | None = Field(
        title="StateOrProvinceName -> егион (область, республика) страны", default=None
    )
    L: str | None = Field(
        title="LocalityName ->  город или населенный пункт владельца (или организации владельца) сертификата",
        default=None,
    )
    STREET: str | None = Field(title="Адрес", default=None)
    E: EmailStr | None = Field(title="Email -> адрес электронной почты", default=None)
    INN: str | None = Field(title="INN -> ИНН владельца сертификата", default=None)
    SNILS: str | None = Field(
        title="SNILS -> СНИЛС владельца сертификата", default=None
    )
    INN_ORG: str | None = Field(
        title="INN -> ИНН Организации владельца сертификата", default=None
    )
    OGRN: str | None = Field(
        title="OGRN -> ОГРН Организации владельца сертификата", default=None
    )
    OGRIP: str | None = Field(
        title="OGRIP -> ОГРИП  владельца сертификата", default=None
    )
    OU: str | None = Field(
        title="OrganizationalUnitName -> наименование подразделения организации",
        default=None,
    )


class CertificateSchema(BaseModel):
    """Сертификат"""

    subject_name: str
    subject: SubjectSchema | None = None
    issuer_name: str
    issuer: SubjectSchema | None = None
    thumbprint: str
    serial_number: str
    valid_from_date: datetime
    valid_to_date: datetime
    version: str
    has_private_key: bool = False
    store: StoreName
    # certificate: Optional[str] = None

    @classmethod
    def parsing_data_certificate(cls, data: str) -> SubjectSchema:
        rex = r"(?:ИНН ЮЛ|СНИЛС|ОГРН|ИНН|C|S|L|STREET|O|CN|T|G|SN|E|ОГРНИП|OU){1}=.*?(?=, ИНН ЮЛ=|, СНИЛС=|, ОГРН=|, ИНН=|, C=|, S=|, L=|, STREET=|, O=|, CN=|, T=|, G=|, SN=|, E=|, ОГРНИП=|, OU=|$)"

        matches = re.findall(rex, data)
        payload = {}
        for m in matches:
            k, v = m.split("=")
            payload[k.strip()] = v.strip()

        payload["INN"] = payload.get("ИНН", None)
        payload["SNILS"] = payload.get("СНИЛС", None)
        payload["INN_ORG"] = payload.get("ИНН ЮЛ", None)
        payload["OGRN"] = payload.get("ОГРН", None)
        payload["OGRIP"] = payload.get("ОГРНИП", None)

        if payload["INN_ORG"] is None:
            payload["INN_ORG"] = payload.get("ИНН", None)

        return SubjectSchema(**payload)

    @field_validator("valid_from_date", "valid_to_date", mode="before")
    @classmethod
    def normalize_date(cls, v: str | datetime, info: ValidationInfo) -> datetime:
        if isinstance(v, datetime):
            return v
        return datetime.strptime(v, "%d.%m.%Y %H:%M:%S")

    @model_validator(mode="before")
    @classmethod
    def x(cls, data: Any) -> Any:
        if data.get("subject") is None:
            data["subject"] = cls.parsing_data_certificate(data.get("subject_name", ""))

        if data.get("issuer") is None:
            data["issuer"] = cls.parsing_data_certificate(data.get("issuer_name", ""))

        return data


class ResponseListDataSchema(BaseModel, Generic[DetailsT]):
    offset: int
    count: int
    data: list[DetailsT]


class ResponseSchema(BaseModel, Generic[DetailsT]):
    """Ответ сервера по api"""

    result: ResultStatus  # статус
    details: DetailsT  # результат обрработка ввиде данных


class SingSchema(BaseModel):
    """Данные о подписи"""

    singer: CertificateSchema
    date_sign: datetime | None

    @field_validator("date_sign", mode="before")
    @classmethod
    def normalize_date(cls, v: str | datetime, info: ValidationInfo) -> datetime:
        if v is None or isinstance(v, datetime):
            return v
        return datetime.strptime(v, "%d.%m.%Y %H:%M:%S")

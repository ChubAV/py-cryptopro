from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
from injector import singleton


def get_basedir() -> Path:
    """функциия возвращает путь к корневой директории"""
    return Path(__file__).parent.parent


def get_import_certificates_dir() -> Path:
    """функция возвращает путь к директории для импорта сертификатов"""
    base_dir = get_basedir()
    return Path(base_dir, "certificates")


def get_import_secretkeys_dir() -> Path:
    """функция возвращает путь к директории для импорта секретных ключей"""
    base_dir = get_basedir()
    return Path(base_dir, "secretkeys")


def get_secretkeys_dir() -> Path:
    """функция возвращает путь к директории для секретных ключей"""
    return Path("/var/opt/cprocsp/keys/root/")


def get_log_dir() -> Path:
    """функция возвращает путь к директории для логов"""
    base_dir = get_basedir()
    return Path(base_dir, "logs")


def get_static_dir() -> Path:
    """функция возвращает путь к директории для статических файлов"""
    base_dir = get_basedir()
    return Path(base_dir, "app", "static")


def get_templates_dir() -> Path:
    """функция возвращает путь к директории для шаблонов"""
    base_dir = get_basedir()
    return Path(base_dir, "app", "templates")


def get_html_menu() -> list:
    """функция возвращает список меню для html страниц"""
    menu = [
        {
            "name": "Главная",
            "slag": "home",
            "template": "home",
            "href": "/",
            "submenu": [],
        },
        {
            "name": "Плагин",
            "slag": "cadesplugin",
            "template": "cadesplugin",
            "href": "/cadesplugin/",
            "submenu": [],
        },
        {
            "name": "О сервере",
            "slag": "about",
            "template": "about",
            "href": "/about/",
            "submenu": [],
        },
        {
            "name": "Хеш",
            "slag": "hash",
            "template": "hash",
            "href": "/hash/",
            "submenu": [],
        },
        {
            "name": "Сетрификаты",
            "slag": "certs",
            "template": "certs",
            "href": "/certs/",
            "submenu": [
                {
                    "name": "Список серт-ов на сервере",
                    "slag": "certificates",
                    "template": "certificates",
                    "href": "/certificates/",
                    "submenu": [],
                },
                {
                    "name": "Данные сертификата",
                    "slag": "certificate",
                    "template": "certificate",
                    "href": "/certificate/",
                    "submenu": [],
                },
                {
                    "name": "Импортировать сертификат",
                    "slag": "certs_import",
                    "template": "certs_import",
                    "href": "/certs_import/",
                    "submenu": [],
                },
            ],
        },
        {
            "name": "Проверка подписи",
            "slag": "verify",
            "template": "verify",
            "href": "/verify/",
            "submenu": [
                {
                    "name": "Простой текст",
                    "slag": "verifytxt",
                    "template": "verifytxt",
                    "href": "/verifytxt/",
                    "submenu": [],
                },
                {
                    "name": "Файл",
                    "slag": "verifyfile",
                    "template": "verifyfile",
                    "href": "/verifyfile/",
                    "submenu": [],
                },
                {
                    "name": "XML",
                    "slag": "verifyxml",
                    "template": "verifyxml",
                    "href": "/verifyxml/",
                    "submenu": [],
                },
            ],
        },
    ]
    return menu


class Settings(BaseSettings):
    """Класс для настроек приложения"""

    app_name: str = Field(
        default="Микросервис КриптоПро", description="Название приложения"
    )
    base_dir: Path = Field(
        default_factory=get_basedir, description="Базовая директория приложения"
    )
    import_certificates_dir: Path = Field(
        default_factory=get_import_certificates_dir,
        description="Директория для импорта сертификатов",
    )
    import_secretkeys_dir: Path = Field(
        default_factory=get_import_secretkeys_dir,
        description="Директория для импорта секретных ключей",
    )
    secretkeys_dir: Path = Field(
        default_factory=get_secretkeys_dir,
        description="Директория для хранения секретных ключей",
    )
    log_dir: Path = Field(
        default_factory=get_log_dir, description="Директория для логов"
    )
    static_dir: Path = Field(
        default_factory=get_static_dir, description="Директория для статических файлов"
    )
    templates_dir: Path = Field(
        default_factory=get_templates_dir, description="Директория для шаблонов"
    )
    backend_url: str = Field(
        default="http://localhost:8080", description="URL микросервиса"
    )
    license_crypto_pro: str | None = Field(
        default=None, description="Лицензия КриптоПро"
    )
    html_menu: list = Field(
        default_factory=get_html_menu, description="Меню для html страниц"
    )
    debug: bool = Field(default=True, description="Вкл/Выкл. режима отладки")
    api_key: str | None = Field(
        default=None, description="Ключ для API, если не указан, то доступ открыт всем"
    )


def init_settings(binder):
    """Конструктор настроек"""
    path_to_env = Path(get_basedir(), ".env")
    if path_to_env.exists():
        settings = Settings(
            _env_file=path_to_env.absolute(), _env_file_encoding="utf-8"
        )  # type: ignore
    else:
        settings = Settings()
    binder.bind(Settings, to=settings, scope=singleton)

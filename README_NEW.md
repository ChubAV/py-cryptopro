## Микросервис для работы с КриптоПро в Docker

### 1. Общая информация

- **Название проекта**: Микросервис для работы с КриптоПро в Docker
- **Краткое описание**: Сервис предоставляет HTTP API для вычисления хэшей, создания и проверки электронных подписей (включая XML), а также работы с сертификатами КриптоПро (чтение, поиск, импорт). Предназначен для интеграции с внутренними сервисами и автоматизации операций ЭЦП.
- **Основные технологии**:
  - **Язык**: Python 3.12
  - **Веб-фреймворк**: FastAPI
  - **DI**: injector
  - **Шаблоны**: Jinja2 (DEV-страницы в режиме debug)
  - **Статические файлы**: встроенный StaticFiles
  - **Криптография**: pycades (обертка над КриптоПро CSP), утилиты КриптоПро (`cpconfig`, `certmgr`, `csptest`)
  - **Тесты**: pytest, httpx (dev)
  - **Управление зависимостями**: uv
  - **Контейнеризация**: Docker, docker-compose


### 2. Архитектура проекта

- **Слои и зависимости**:
  - `app/main.py`: создание `FastAPI` приложения, настройка lifespan, подключение роутеров, мидлвари (`UUIDMiddleware`, `APIKeyMiddleware`). DI через `injector`.
  - `app/endpoints_api.py`: REST API (префикс `/api`) — системная информация, хэширование, работа с сертификатами, подписание, проверка (в том числе XML).
  - `app/endpoints_html.py`: DEV-страницы (рендеринг шаблонов) подключаются только при `settings.debug=True`.
  - `app/services.py`: бизнес-логика и интеграция с КриптоПро/pycades и утилитами CLI.
  - `app/schemas.py`: Pydantic-схемы запросов/ответов (v2).
  - `app/constants.py`: перечисления статусов/алгоритмов/имен хранилищ.
  - `app/dependencies.py`: DI-обертки, респонс-врапперы, шаблоны, контекст.
  - `app/config.py`: конфигурация и Settings, чтение `.env`, директории.
  - `app/containers.py`: провайдеры `Logger`, `Jinja2Templates`.
  - `app/middleware.py`: мидлвари `APIKeyMiddleware` (заголовок `X-API-Key`), `UUIDMiddleware` (request id).
  - `app/static`, `app/templates`: статика и шаблоны DEV.

- **Хранение данных / База данных**: отсутствует. Сервис работает без БД. Состояние в файловой системе (сертификаты/ключи) в смонтированных директориях.

- **Работа с сертификатами и ключами**:
  - Сертификаты импортируются утилитой `certmgr` в системные хранилища КриптоПро.
  - Закрытые ключи копируются в `/var/opt/cprocsp/keys/root/` (по умолчанию) и «активируются» через `csptest -absorb`.
  - pycades используется для получения сведений о сертификатах, подписи/проверки, XML-подписей.

- **Интеграции с внешними сервисами**: нет. Интеграция с установленным в контейнере/системе КриптоПро CSP и его CLI.


### 3. Установка и запуск

#### 3.1 Системные требования

- Docker (Linux/Windows/macOS). Сборка базируется на `ubuntu:latest` и включает установку КриптоПро CSP и сборку `pycades`.
- Для локального запуска без Docker требуется установленный КриптоПро CSP и корректная сборка/установка `pycades` под вашу платформу. Проект ориентирован на работу в контейнере.

#### 3.2 Зависимости (uv)

- В проекте используется `uv` для управления зависимостями (см. `pyproject.toml`). В контейнере `uv` устанавливается автоматически. При локальном использовании:

```bash
# Установка uv (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Установка зависимостей
uv lock
uv sync --frozen
```

#### 3.3 Переменные окружения

Поддерживаются переменные (см. `app/config.py:Settings`). Используйте `.env` в корне проекта или `env_file` в docker-compose:

- `app_name` — название приложения (строка)
- `backend_url` — базовый URL сервиса (строка, по умолчанию `http://localhost:8080`)
- `license_crypto_pro` — строка лицензии КриптоПро (опционально)
- `debug` — включение DEV-страниц и debug режима (`true`/`false`)
- `api_key` — API-ключ для защиты эндпоинтов (если задан, заголовок `X-API-Key` обязателен)

Директории (автоматически вычисляются, можно переопределять через `.env` при необходимости):
- `import_certificates_dir` — каталог для импорта сертификатов (по умолчанию `<repo>/certificates`)
- `import_secretkeys_dir` — каталог для импорта секретных ключей (по умолчанию `<repo>/secretkeys`)
- `secretkeys_dir` — каталог хранения секретных ключей (по умолчанию `/var/opt/cprocsp/keys/root/`)
- `log_dir`, `static_dir`, `templates_dir`

#### 3.4 Локальный запуск (без Docker)

Требуется установленный КриптоПро и `pycades.so` совместимый с вашей системой. Для разработки можно использовать имеющийся `pycades.so` из проекта, но корректность зависит от вашей ОС.

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

Документация будет доступна на `/docs` (Swagger) и `/redoc`.

#### 3.5 Сборка и запуск в Docker

1) Подготовьте дистрибутив КриптоПро для вашей архитектуры и положите в `./cryptopro-dist/` (см. `Dockerfile`).
2) Соберите образ:

```bash
docker build --tag py-crypto .
```

3) Запустите контейнер напрямую:

```bash
docker run -d \
  -p 8080:8080 \
  -v "$(pwd)/app:/application/app" \
  -v "$(pwd)/tests:/application/tests" \
  -v "$(pwd)/certificates:/application/certificates" \
  -v "$(pwd)/secretkeys:/application/secretkeys" \
  -v "$(pwd)/logs:/application/logs" \
  --env-file .env \
  --name py-crypto \
  py-crypto
```

или через docker-compose:

```bash
docker compose up -d
```

Замечания по каталогам:
- `certificates` должен содержать подкаталоги: `my`, `ca`, `root`; файлы сертификатов в формате X.509 Base64 (`.cer`).
- `secretkeys` — ZIP-архивы с папкой ключа внутри (без пароля). После копирования выполняется «поглощение» ключей `csptest -absorb`.


### 4. API документация

Префикс всех API-эндпоинтов: `/api`.

- **Авторизация**: если задан `api_key`, добавляйте заголовок `X-API-Key: <значение>` ко всем запросам.
- **Ответы**: унифицированы схемой `ResponseSchema`, где
  - `result`: `success | error | processing`
  - `details`: полезная нагрузка (данные или ошибка)

Ниже перечислены эндпоинты. Для краткости примеры приведены в `curl`. Все поля форм, где указано `Form(...)`, отправляются как `multipart/form-data` или `application/x-www-form-urlencoded` в зависимости от наличия файлов.

#### 4.1 Системная информация

- **GET** `/api/systeminfo/`
  - **Назначение**: сведения о версиях CSP/SDK/pycades/Python/OS и лицензии
  - **Параметры**: нет
  - **Ответ**: `ResponseSchema[SystemInfoSchema | ErrorSchema]`
  - Пример:
    ```bash
    curl -s http://localhost:8080/api/systeminfo/
    ```

#### 4.2 Установка лицензии КриптоПро

- **POST** `/api/set_license/`
  - **Назначение**: установить лицензию CSP через `cpconfig`
  - **Тело**: `license: string` (form/query)
  - **Ответ**: `ResponseSchema[bool | ErrorSchema]`
  - Пример:
    ```bash
    curl -s -X POST "http://localhost:8080/api/set_license/?license=XXXX-XXXX-XXXX-XXXX"
    ```

#### 4.3 Хэширование

- **POST** `/api/hash/txt/`
  - **Назначение**: вычислить хэш строки
  - **Тело (form)**: `text: str`, `algorithm: AlgorithmHash` (опционально)
  - **Ответ**: `ResponseSchema[HashedDataSchema | ErrorSchema]`
  - Пример:
    ```bash
    curl -s -X POST http://localhost:8080/api/hash/txt/ \
      -F text="hello"
    ```

- **POST** `/api/hash/file/`
  - **Назначение**: вычислить хэш файла
  - **Тело (form-data)**: `file: UploadFile`, `algorithm: AlgorithmHash` (query)
  - **Ответ**: `ResponseSchema[HashedDataSchema | ErrorSchema]`
  - Пример:
    ```bash
    curl -s -X POST http://localhost:8080/api/hash/file/ \
      -F file=@./tests/files/test1.pdf
    ```

#### 4.4 Сертификаты

- **GET** `/api/certificates/`
  - **Назначение**: список сертификатов в хранилищах
  - **Параметры (query)**: `store: StoreName=All | My | Ca | Root`, `offset: int`, `limit: int`
  - **Ответ**: `ResponseSchema[ResponseListDataSchema[CertificateSchema] | ErrorSchema]`
  - Пример:
    ```bash
    curl -s "http://localhost:8080/api/certificates/?store=All&offset=0&limit=10"
    ```

- **POST** `/api/certificates/`
  - **Назначение**: импорт сертификата в системное хранилище CSP
  - **Тело (form-data)**: `file: UploadFile`, `store: StoreName=My|Ca|Root`
  - **Ответ**: `ResponseSchema[bool | ErrorSchema]`
  - Пример:
    ```bash
    curl -s -X POST http://localhost:8080/api/certificates/ \
      -F file=@./certificates/my/example.cer \
      -F store=My
    ```

- **GET** `/api/certificates/{thumbprint}/`
  - **Назначение**: получить сведения о сертификате по thumbprint
  - **Ответ**: `ResponseSchema[CertificateSchema | ErrorSchema | None]`
  - Пример:
    ```bash
    curl -s http://localhost:8080/api/certificates/ABCDEF1234567890/
    ```

#### 4.5 Подписание (CAdES/XAdES)

- **POST** `/api/sign/s2s/`
  - **Назначение**: строка -> строка подписи (отсоединенная)
  - **Тело (form)**: `data: str`, `thumbprint: str`
  - **Ответ**: `ResponseSchema[str | ErrorSchema]`

- **POST** `/api/sign/s/`
  - **Назначение**: строка -> строка с подписью внутри (присоединенная)
  - **Тело (form)**: `data: str`, `thumbprint: str`
  - **Ответ**: `ResponseSchema[str | ErrorSchema]`

- **POST** `/api/sign/f2f/`
  - **Назначение**: файл -> файл подписи (отсоединенная)
  - **Тело (form-data)**: `file: UploadFile`, `thumbprint: str`
  - **Ответ**: поток файла `application/octet-stream` (имя `sign.sig`) или ошибка

- **POST** `/api/sign/f2s/`
  - **Назначение**: файл -> строка подписи (отсоединенная)
  - **Тело (form-data)**: `file: UploadFile`, `thumbprint: str`
  - **Ответ**: `ResponseSchema[str | ErrorSchema]`

- **POST** `/api/sign/f/`
  - **Назначение**: файл -> файл с подписью внутри (присоединенная)
  - **Тело (form-data)**: `file: UploadFile`, `thumbprint: str`
  - **Ответ**: поток файла `application/octet-stream`

- **POST** `/api/sign/xml2f/`
  - **Назначение**: XML файл -> XML с подписью (XAdES-BES, enveloped)
  - **Тело (form-data)**: `file: UploadFile`, `thumbprint: str`
  - **Ответ**: поток файла XML (`sign.xml`)

- **POST** `/api/sign/hash2s/`
  - **Назначение**: хэш -> строка подписи
  - **Тело (form)**: `hash: str`, `thumbprint: str`
  - **Ответ**: `ResponseSchema[str | ErrorSchema]`

- **POST** `/api/sign/hash2f/`
  - **Назначение**: хэш -> файл подписи
  - **Тело (form)**: `hash: str`, `thumbprint: str`
  - **Ответ**: поток файла `sign.sig`

Замечания:
- Поле `thumbprint` — отпечаток сертификата из хранилища пользователя/компьютера CSP.
- Для файловых операций данные кодируются/декодируются в Base64 внутри сервиса.

#### 4.6 Проверка подписи

- **POST** `/api/verify/f2f/`
  - **Назначение**: файл данных + файл подписи
  - **Тело (form-data)**: `file: UploadFile`, `sign: UploadFile`
  - **Ответ**: `ResponseSchema[SingSchema | ErrorSchema]`

- **POST** `/api/verify/f2s/`
  - **Назначение**: файл данных + строка подписи
  - **Тело (form-data)**: `file: UploadFile`, `sign: str`
  - **Ответ**: `ResponseSchema[SingSchema | ErrorSchema]`

- **POST** `/api/verify/f/`
  - **Назначение**: файл с подписью внутри
  - **Тело (form-data)**: `file: UploadFile`
  - **Ответ**: `ResponseSchema[SingSchema | ErrorSchema]`

- **POST** `/api/verify/s2s/`
  - **Назначение**: строка данных + строка подписи
  - **Тело (form)**: `data: str`, `sign: str`
  - **Ответ**: `ResponseSchema[SingSchema | ErrorSchema]`

- **POST** `/api/verify/s/`
  - **Назначение**: строка с подписью внутри
  - **Тело (form)**: `data: str`
  - **Ответ**: `ResponseSchema[SingSchema | ErrorSchema]`

- **POST** `/api/verify/xml2f/`
  - **Назначение**: проверить XML подпись (XAdES) в файле
  - **Тело (form-data)**: `file: UploadFile`
  - **Ответ**: `ResponseSchema[SingSchema | ErrorSchema]`

- **POST** `/api/verify/hash2s/`
  - **Назначение**: хэш + строка подписи
  - **Тело (form)**: `hash: str`, `sign: str`
  - **Ответ**: `ResponseSchema[SingSchema | ErrorSchema]`

- **POST** `/api/verify/hash2f/`
  - **Назначение**: хэш + файл подписи
  - **Тело (form-data)**: `hash: str`, `sign: UploadFile`
  - **Ответ**: `ResponseSchema[SingSchema | ErrorSchema]`

Схема `SingSchema` содержит сведения о подписанте и времени подписания (если доступно).


#### 4.7 Схемы ответов (модели)

- Общая оболочка ответа: `ResponseSchema[T]`
  - Поля:
    - `result`: строка, одно из `success | error | processing`
    - `details`: полезная нагрузка типа `T` или `ErrorSchema`
  - Пример (успех):
    ```json
    {
      "result": "success",
      "details": { "hash": "BASE64...", "algorithm_code": 101, "algorithm_name": "CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256", "source": "text" }
    }
    ```
  - Пример (ошибка):
    ```json
    {
      "result": "error",
      "details": { "code": "0x800B0109", "description": "...описание ошибки..." }
    }
    ```

- `ErrorSchema`
  - Поля:
    - `code`: строка кода ошибки (например, `0x800B0109` или `Без кода`)
    - `description`: человекочитаемое описание
  - Пример:
    ```json
    { "code": "0x800B0109", "description": "A certificate chain processed, but terminated in a root certificate which is not trusted by the trust provider." }
    ```

- `SystemInfoSchema`
  - Поля: `csp_version`, `sdk_version`, `pycades_version`, `python_version`, `platform_version`, `license_crypto_pro` (nullable)
  - Пример:
    ```json
    {
      "csp_version": "5.0.12345",
      "sdk_version": "2.0.0",
      "pycades_version": "0.1.0",
      "python_version": "3.12.6",
      "platform_version": "Linux-6.8.0-aarch64-with-glibc2.38",
      "license_crypto_pro": "SERIAL XXXXX-XXXXX-..."
    }
    ```

- `HashedDataSchema`
  - Поля: `hash` (Base64 строки/файла), `algorithm_code` (int), `algorithm_name` (строка), `source` (`text | file`)
  - Пример:
    ```json
    {
      "hash": "MII...",
      "algorithm_code": 101,
      "algorithm_name": "CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256",
      "source": "file"
    }
    ```

- `SubjectSchema` (входит в `CertificateSchema`)
  - Поля (все строки, часть может быть `null`): `CN`, `SN`, `G`, `T`, `O`, `C`, `S`, `L`, `STREET`, `E`, `INN`, `SNILS`, `INN_ORG`, `OGRN`, `OGRIP`, `OU`
  - Пример:
    ```json
    {
      "CN": "Иванов Иван Иванович",
      "SN": "Иванов",
      "G": "Иван Иванович",
      "T": null,
      "O": "ООО Ромашка",
      "C": "RU",
      "S": "Москва",
      "L": "Москва",
      "STREET": "ул. Пушкина, д. 1",
      "E": "user@example.org",
      "INN": "7701234567",
      "SNILS": "112-233-445 95",
      "INN_ORG": "7701234567",
      "OGRN": "1027700132195",
      "OGRIP": null,
      "OU": "ИТ"
    }
    ```

- `CertificateSchema`
  - Поля: `subject_name` (строка DN), `subject` (`SubjectSchema | null`), `issuer_name` (строка DN), `issuer` (`SubjectSchema | null`), `thumbprint`, `serial_number`, `valid_from_date` (ISO 8601), `valid_to_date` (ISO 8601), `version` (строка), `has_private_key` (bool), `store` (`My|Ca|Root|All`)
  - Пример:
    ```json
    {
      "subject_name": "CN=Иванов Иван, O=ООО Ромашка, C=RU, ...",
      "subject": { "CN": "Иванов Иван", "C": "RU", "INN": "7701234567" },
      "issuer_name": "CN=УЦ ..., C=RU, ...",
      "issuer": { "CN": "УЦ ...", "C": "RU" },
      "thumbprint": "ABCDEF0123456789ABCDEF0123456789ABCDEF01",
      "serial_number": "0123456789ABCDEF",
      "valid_from_date": "2024-01-01T00:00:00",
      "valid_to_date": "2025-01-01T00:00:00",
      "version": "3",
      "has_private_key": true,
      "store": "My"
    }
    ```

- `ResponseListDataSchema[T]`
  - Поля: `offset` (int), `count` (int), `data` (массив `T`)
  - Пример для списка сертификатов:
    ```json
    {
      "offset": 0,
      "count": 2,
      "data": [
        { "thumbprint": "...1", "subject_name": "...", "issuer_name": "...", "serial_number": "...", "valid_from_date": "2024-01-01T00:00:00", "valid_to_date": "2025-01-01T00:00:00", "version": "3", "has_private_key": false, "store": "Root" },
        { "thumbprint": "...2", "subject_name": "...", "issuer_name": "...", "serial_number": "...", "valid_from_date": "2024-01-01T00:00:00", "valid_to_date": "2025-01-01T00:00:00", "version": "3", "has_private_key": true, "store": "My" }
      ]
    }
    ```

- `SingSchema`
  - Поля: `singer` (`CertificateSchema`), `date_sign` (ISO 8601 или `null`)
  - Пример:
    ```json
    {
      "singer": {
        "thumbprint": "ABCDEF0123456789ABCDEF0123456789ABCDEF01",
        "subject_name": "CN=Иванов Иван, O=ООО Ромашка, C=RU",
        "issuer_name": "CN=УЦ ..., C=RU",
        "serial_number": "0123456789ABCDEF",
        "valid_from_date": "2024-01-01T00:00:00",
        "valid_to_date": "2025-01-01T00:00:00",
        "version": "3",
        "has_private_key": true,
        "store": "All",
        "subject": { "CN": "Иванов Иван", "C": "RU" },
        "issuer": { "CN": "УЦ ...", "C": "RU" }
      },
      "date_sign": "2024-09-01T10:22:33"
    }
    ```

- Потоковые ответы (скачивание файлов)
  - Эндпоинты: `/api/sign/f2f/`, `/api/sign/f/`, `/api/sign/xml2f/`, `/api/sign/hash2f/`
  - Тип: `application/octet-stream`
  - Заголовки: `Content-Disposition: attachment; filename=sign.sig` (или `sign.xml` для XML)

### 5. Дополнительно

- **Безопасность**: включите `api_key`, чтобы защитить эндпоинты. Клиент обязан отправлять заголовок `X-API-Key`.
- **Логи**: складываются в `logs/` (см. `.env` и `Settings.log_dir`).
- **DEV-страницы**: при `debug=true` активны HTML-роуты (`/`, `/hash/`, `/verifytxt/`, `/verifyfile/`, `/verifyxml/`, `/certificates/`, `/certificate/`, `/certs_import/`, `/signtxt/`, `/signfile/`, `/about/`, `/cadesplugin/`).
- **Тесты**: см. `tests/`. Для успешных e2e-тестов требуется корректная установка ключей/сертификатов и актуальные `thumbprint`.

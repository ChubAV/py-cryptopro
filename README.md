## Микросервис для работы с КриптоПро в Docker

### Основные библиотеки
- python 3.12
- [pycades](https://github.com/CryptoPro/pycades) - библиотека для работы с КриптоПро через python(нужна сборка библиотеки)
- fastapi - фреймворк для создания API

### Задачи, которые решает микросервис
- Создание хэша для простого текста или файла
- Создание/Проверка ЭЦП для простого текста или файла
- Создание/Проверка ЭЦП для XML файла
- Создание/Проверка ЭЦП для хэша строки или файла

### Сборка Docker образа
- Скачать с официального сайта дистрибутив [КриптоПро](https://www.cryptopro.ru/products/csp/downloads) в соответствии со своей платформой (нужно залогиниться)
- Скопировать файлы в папку cryptopro-dist
- Запустить сборку командой `docker build --tag py-crypto .`

### Проблемы при сборке
Для сборки расширения **pycades** необходимы файлы из пакета **python3-dev**. Путь к ним указан в файле **CMakeLists.txt**.
У меня в системе они находились в папке **/usr/include/python3.12**, а в файле **CMakeLists.txt** указан путь **/usr/include/python3.11**.
Чтобы не менять файл, я сделал символическую ссылку `ln -s /usr/include/python3.12 /usr/include/python3.11`

### Запуск контейнера

`docker run -d -p 8080:8080 py-crypto -v ./certificates:/application/certificates -v ./secretkeys:/application/secretkeys -v ./logs:/application/logs`

Для импорта сертификатов и закрытых ключей в директории **certificates** и **secretkeys** монтируем соответствующие директории.

Каталог **certificates** должен содержать три каталога:
- **my** - для сертификатов пользователей
- **ca** - для сертификатов удостоверяющих центров
- **root** - для корневых сертификатов

Внутри каждого каталога могут лежать файлы сертификатов в формате X.509 Base64 с расширением **.cer**

В каталог **secretkeys** копируются файлы закрытых ключей в виде ZIP-архивов. Внутри архива должна быть папка с ключом.
Архив должен иметь следующую структуру:
```
└── le-09650.000 - каталог с файлами закрытого ключа
    ├── header.key
    ├── masks2.key
    ├── masks.key
    ├── name.key
    ├── primary2.key
    └── primary.key
```

Ключ должен быть без пароля.
С паролем я не стал заморачиваться, так как скорее всего это будут обезличенные ключи, с помощью которых будут взаимодействовать различные сервисы, а не конкретный пользователь.

В Docker можно пробросить следующие переменные окружения:
- **app_name** - название приложения
- **license_crypto_pro** - лицензия КриптоПро
- **debug** - режим отладки
- **api_key** - ключ для API

### Работа с контейнером
Точки доступа к API можно посмотреть в файле **app/endpoints_api.py**, все они с подробным описанием.
Для подписания убедитесь, что в директорию **secretkeys** были смонтированы файлы закрытых ключей, напомню, что ключи должны быть без пароля.
Для проверки подписи нужно монтировать в директорию **certificates** только сертификаты корневых и промежуточных удостоверяющих центров. Личные сертификаты можно не монтировать, по крайней мере, мне они не понадобились.
Если нужно защитить точки доступа, нужно в переменную окружения добавить **api_key**, тогда все запросы к API будут проходить проверку на наличие ключа в заголовке запроса (**X-API-KEY**).

### Тестирование
Для ручного тестирования хотел написать HTML-страницу, но пока не доделал.

Для тестирования с помощью pytest нужно добавить закрытый ключ в контейнер и настроить тесты в conftest.py, пример там есть. thumbprint указанный в conftest.py, это thumbprint сертификата.

### Аналоги и альтернативы
https://github.com/devind-team/CryptoPro-pycades?tab=readme-ov-file
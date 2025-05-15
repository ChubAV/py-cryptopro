FROM ubuntu:latest

ENV TZ=Europe/Moscow
ENV LANG=C.UTF-8
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DOCKER=true

RUN apt update &&  apt upgrade -y && \
    apt install cmake build-essential libboost-all-dev python3-dev python3-pip curl ca-certificates vim apt-utils git wget unzip -y

# Установка криптопровайдера
WORKDIR /dist
COPY ./cryptopro-dist/linux-arm64_deb.tgz /dist/linux-arm64_deb.tgz
RUN tar xvf linux-arm64_deb.tgz
RUN linux-arm64_deb/install.sh
RUN apt install /dist/linux-arm64_deb/lsb-cprocsp-devel_*.deb /dist/linux-arm64_deb/cprocsp-pki-cades*.deb
ENV PATH="$PATH:/root/.local/bin:/opt/cprocsp/bin/aarch64:/opt/cprocsp/sbin/aarch64"

# Сборка библиотеки для работы с криптопровайдером
RUN ln -s /usr/include/python3.12 /usr/include/python3.11
RUN git clone https://github.com/CryptoPro/pycades.git
RUN cd pycades && \
    patch < ./arm64_support.patch && mkdir build && cd build && \
    cmake .. && make -j4 && cp pycades.so /usr/lib/python3.12/pycades.so

# Создание директорий для приложения, сертификатов и секретных ключей
RUN     mkdir -p /application && \
        mkdir -p /application/certificates/ca && \
        mkdir -p /application/certificates/my && \
        mkdir -p /application/certificates/root && \
        mkdir -p /application/secretkeys && \
        mkdir -p /application/logs
# скачивание и установка сертификатов Минцифры
RUN cd /application/certificates/root && \
    wget https://gu-st.ru/content/lending/russian_trusted_root_ca_pem.crt

RUN cd /application/certificates/ca && \
    wget https://gu-st.ru/content/lending/russian_trusted_sub_ca_pem.zip && \
    unzip russian_trusted_sub_ca_pem.zip && \
    rm russian_trusted_sub_ca_pem.zip

WORKDIR /application/
COPY    pyproject.toml /application/pyproject.toml
COPY    ./app /application/app
# COPY    ./.env/ /application/.env

# Установка uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Установка зависимостей
RUN uv lock &&uv sync --frozen

# Удаление временных файлов
RUN apt remove cmake build-essential libboost-all-dev python3-dev curl vim git apt-utils wget unzip -y \
    && rm -r /dist \
    && rm -rf /var/lib/apt/lists/*


CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
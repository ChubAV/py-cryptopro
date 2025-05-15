from enum import StrEnum, IntEnum


class ResultStatus(StrEnum):
    """Результат обработки запроса/задания"""

    success = "success"  # успешно
    error = "error"  # ошибка
    processing = "processing"  # в работе еще обрабатывается


class AlgorithmHash(IntEnum):
    """Алгоритмы хеширования"""

    CADESCOM_HASH_ALGORITHM_SHA1 = 0  # Алгоритм SHA1.
    CADESCOM_HASH_ALGORITHM_MD2 = 1  # Алгоритм MD2.
    CADESCOM_HASH_ALGORITHM_MD4 = 2  # Алгоритм MD4.
    CADESCOM_HASH_ALGORITHM_MD5 = 3  # 	Алгоритм MD5.
    CADESCOM_HASH_ALGORITHM_SHA_256 = 4  # Алгоритм SHA1 с длиной ключа 256 бит.
    CADESCOM_HASH_ALGORITHM_SHA_384 = 5  # Алгоритм SHA1 с длиной ключа 384 бита.
    CADESCOM_HASH_ALGORITHM_SHA_512 = 6  # Алгоритм SHA1 с длиной ключа 512 бит.
    CADESCOM_HASH_ALGORITHM_CP_GOST_3411 = 100  # 	Алгоритм ГОСТ Р 34.11-94.
    CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256 = 101  # Алгоритм ГОСТ Р 34.11-2012.
    CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_512 = 102  # Алгоритм ГОСТ Р 34.11-2012.
    CADESCOM_HASH_ALGORITHM_CP_GOST_3411_HMAC = 110  # Алгоритм ГОСТ Р 34.11-94 HMAC.
    CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256_HMAC = (
        111  # Алгоритм ГОСТ Р 34.11-2012 HMAC.
    )
    CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_512_HMAC = (
        112  # Алгоритм ГОСТ Р 34.11-2012 HMAC.
    )


class StoreName(StrEnum):
    """Имена хранилищ сертификатов"""

    CAPICOM_MY_STORE = "My"
    CAPICOM_CA_STORE = "Ca"
    CAPICOM_ROOT_STORE = "Root"
    CAPICOM_ROOT_ALL = "All"

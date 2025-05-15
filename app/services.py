from typing import Any
import sys
import platform
import aiofiles
from pathlib import Path
import subprocess
import re
import pycades
from .schemas import SystemInfoSchema, HashedDataSchema, CertificateSchema, SingSchema
from .utils import data_to_base64, text_to_base64, unzip_all_files_in_folder
from .constants import AlgorithmHash, StoreName


def get_license_crypto_pro() -> str:
    """
    Получение информации о лицензии криптопровайдера
    """
    process = subprocess.Popen(
        ["cpconfig", "-license", "-view"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    stderr = stderr.decode("utf-8")
    stdout = stdout.decode("utf-8")

    if stderr:
        return "НЕТ ДАННЫХ"

    return stdout.replace("\n", " ").strip()


def set_license_crypto_pro(license: str) -> bool:
    """
    Установка лицензии криптопровайдера
    """
    process = subprocess.Popen(
        ["cpconfig", "-license", "-set", license],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    stderr = stderr.decode("utf-8")
    stdout = stdout.decode("utf-8")

    if stderr:
        return False

    return True


def get_system_info() -> SystemInfoSchema:
    """Получить информацию о системе"""
    about = pycades.About()
    license_crypto_pro = get_license_crypto_pro()
    system_info = SystemInfoSchema(
        csp_version=about.CSPVersion().toString(),
        sdk_version=about.Version,
        pycades_version=pycades.ModuleVersion(),
        python_version="{}.{}.{}".format(
            sys.version_info.major, sys.version_info.minor, sys.version_info.micro
        ),
        platform_version=platform.platform(),
        license_crypto_pro=license_crypto_pro,
    )
    return system_info


def wrapper_hash_object(
    data: str | bytes,
    algorithm: AlgorithmHash = AlgorithmHash.CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256,
    not_data: bool = False,
) -> Any:
    """
    Оборачивает уже вычисленный хэш в объект pycades.HashedData
    ил Вычисление хэша для cтроки или набора байт
    возвращает объект pycades.HashedData
    """
    if isinstance(data, bytes):
        sBase64 = data_to_base64(data)
    else:
        sBase64 = data

    hashedData = pycades.HashedData()
    hashedData.Algorithm = algorithm

    if isinstance(data, bytes):
        hashedData.DataEncoding = pycades.CADESCOM_BASE64_TO_BINARY
        hashedData.Hash(sBase64)
    elif isinstance(data, str) and not not_data:
        hashedData.Hash(sBase64)
    else:
        hashedData.SetHashValue(data)

    return hashedData


def get_hash(
    data: str | bytes,
    algorithm: AlgorithmHash = AlgorithmHash.CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256,
) -> HashedDataSchema:
    """
    Вычисление хэша для cтроки или набора байт
    вызывает wrapper_hash_object и преобразует результат (pycades.HashedData) в HashedDataSchema
    """
    cp_hashed_data = wrapper_hash_object(data, algorithm)
    result = HashedDataSchema(
        hash=cp_hashed_data.Value,
        algorithm_code=cp_hashed_data.Algorithm,
        algorithm_name=AlgorithmHash(cp_hashed_data.Algorithm).name,
        source="text" if isinstance(data, str) else "file",
    )
    return result


def get_certificate_from_base64(data: bytes) -> CertificateSchema:
    """
    Выдает информацию о сертификате
    выходные данные - сертификат в формате base64
    """
    cert = pycades.Certificate()
    cert.Import(data)
    result = CertificateSchema(
        subject_name=cert.SubjectName,
        issuer_name=cert.IssuerName,
        thumbprint=cert.Thumbprint,
        serial_number=cert.SerialNumber,
        valid_from_date=cert.ValidFromDate,
        valid_to_date=cert.ValidToDate,
        version=str(cert.Version),
        store=StoreName("All"),
    )
    return result


def get_certificates_from_store(
    store_name: StoreName, offset: int = 0, limit: int = 10
) -> list[CertificateSchema]:
    store = pycades.Store()
    in_stores: list[StoreName] = []
    results: list[CertificateSchema] = []

    if store_name == StoreName.CAPICOM_ROOT_ALL:
        in_stores = [s for s in StoreName if s.value != StoreName.CAPICOM_ROOT_ALL]
    else:
        in_stores = [
            store_name,
        ]

    for s in in_stores:
        store.Open(
            pycades.CAPICOM_CURRENT_USER_STORE,
            s,
            pycades.CAPICOM_STORE_OPEN_MAXIMUM_ALLOWED,
        )
        certs = store.Certificates

        for i in range(1, certs.Count + 1):
            cert = certs.Item(i)
            results.append(
                CertificateSchema(
                    subject_name=cert.SubjectName,
                    issuer_name=cert.IssuerName,
                    thumbprint=cert.Thumbprint,
                    serial_number=cert.SerialNumber,
                    valid_from_date=cert.ValidFromDate,
                    valid_to_date=cert.ValidToDate,
                    version=str(cert.Version),
                    store=s,
                    has_private_key=cert.HasPrivateKey(),
                )
            )
        store.Close()

    return results[offset : offset + limit]


async def save_certificate_in_folder(
    data: bytes,
    path_to_folder: Path,
    original_file_name: str | None = None,
    store: StoreName = StoreName.CAPICOM_MY_STORE,
) -> Path:
    cert: CertificateSchema = get_certificate_from_base64(data)

    file_name = f"{cert.thumbprint}.cer"
    if isinstance(original_file_name, str) and original_file_name.split(".")[-1]:
        file_name = f"{cert.thumbprint}.{original_file_name.split('.')[-1]}"

    if store == StoreName.CAPICOM_ROOT_STORE:
        sub_folder = "root"
    elif store == StoreName.CAPICOM_CA_STORE:
        sub_folder = "ca"
    else:
        sub_folder = "my"

    full_path_to_file = path_to_folder.joinpath(sub_folder).joinpath(file_name)
    if not full_path_to_file.exists():
        async with aiofiles.open(full_path_to_file, mode="wb") as f:
            await f.write(data)

    return full_path_to_file


def cli_refresh_crypto_pro():
    process = subprocess.Popen(
        ["csptest", "-absorb", "-certs", "-autoprov"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    stderr = stderr.decode("utf-8")
    stdout = stdout.decode("utf-8")

    if stderr:
        return False

    pattern_result = r"ErrorCode:\s+0x\d{8}"
    result = re.search(pattern_result, stdout)

    if result is not None and "0x00000000" in result[0]:
        return True
    else:
        return False


def import_certificate_from_file(
    path_to_file: Path, store: StoreName = StoreName.CAPICOM_MY_STORE
):
    if store == StoreName.CAPICOM_ROOT_STORE:
        store_str = "uRoot"
    elif store == StoreName.CAPICOM_CA_STORE:
        store_str = "uCa"
    else:
        store_str = "uMy"

    process = subprocess.Popen(
        ["certmgr", "-inst", "-file", path_to_file, "-all", "-store", store_str],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    stderr = stderr.decode("utf-8")
    stdout = stdout.decode("utf-8")

    if stderr:
        return False

    pattern_result = r"ErrorCode:\s+0x\d{8}"
    result = re.search(pattern_result, stdout)

    if result is not None and "0x00000000" in result[0]:
        return cli_refresh_crypto_pro()
    else:
        return False


def import_all_certificate(dir_in: Path):
    subdirs = ["my", "ca", "root"]
    extensions = ["*.cer", "*.crt"]
    for subdir in subdirs:
        for ext in extensions:
            for f in Path(dir_in, subdir).rglob(ext):
                import_certificate_from_file(
                    f, StoreName(subdir[:1].upper() + subdir[1:])
                )


def import_all_secretkeys(dir_in: Path, dir_out: Path):
    unzip_all_files_in_folder(dir_in, dir_out)
    return cli_refresh_crypto_pro()


def get_object_certificate_by_thumbprint(thumbprint: str, name_store: str):
    try:
        store = pycades.Store()

        if "All".lower() in name_store.lower():
            store.Open(pycades.CAPICOM_CURRENT_USER_STORE)
        else:
            store.Open(
                pycades.CAPICOM_CURRENT_USER_STORE,
                name_store,
                pycades.CAPICOM_STORE_OPEN_MAXIMUM_ALLOWED,
            )

        certs = store.Certificates
        cert = certs.Find(0, thumbprint).Item(
            1
        )  # думаю если сертификат не найдет будет ошибка
        return cert
    except Exception as e:
        print(f"{e}")
    finally:
        store.Close()

    return None


def find_certificate_by_thumbprint(thumbprint: str) -> CertificateSchema | None:
    name_stores = ["My", "Ca", "Root"]
    result = None

    for name_store in name_stores:
        cert_object = get_object_certificate_by_thumbprint(thumbprint, name_store)
        if cert_object is not None:
            result = CertificateSchema(
                subject_name=cert_object.SubjectName,
                issuer_name=cert_object.IssuerName,
                thumbprint=cert_object.Thumbprint,
                serial_number=cert_object.SerialNumber,
                valid_from_date=cert_object.ValidFromDate,
                valid_to_date=cert_object.ValidToDate,
                version=str(cert_object.Version),
                store=StoreName(name_store),
                has_private_key=cert_object.HasPrivateKey(),
            )
            break

    return result


def parse_sing(signed_data) -> SingSchema:
    signers = signed_data.Signers
    signer1 = signers.Item(1)
    cert1 = signer1.Certificate
    try:
        date_sign1 = signer1.SigningTime
    except Exception as e:
        print(e)
        date_sign1 = None

    cert_schema = CertificateSchema(
        subject_name=cert1.SubjectName,
        issuer_name=cert1.IssuerName,
        thumbprint=cert1.Thumbprint,
        serial_number=cert1.SerialNumber,
        valid_from_date=cert1.ValidFromDate,
        valid_to_date=cert1.ValidToDate,
        version=str(cert1.Version),
        store=StoreName("All"),
        has_private_key=cert1.HasPrivateKey(),
    )
    sing_schema = SingSchema(singer=cert_schema, date_sign=date_sign1)
    return sing_schema


def verify_hash(hash, sign):
    """
    Проверка подписи для хэша
    """
    signedData = pycades.SignedData()
    signedData.VerifyHash(hash, sign, pycades.CADESCOM_CADES_BES)
    return signedData


def verify_data(data, sign):
    """
    Проверка подписи для данных
    если подпись есть то она отсоединенная
    если подпись None значит она внутри пакета с данными
    """
    signedData = pycades.SignedData()
    if sign is not None:
        signedData.ContentEncoding = pycades.CADESCOM_BASE64_TO_BINARY
        signedData.Content = data
        signedData.VerifyCades(sign, pycades.CADESCOM_CADES_BES, 1)
    else:
        signedData.VerifyCades(data, pycades.CADESCOM_CADES_BES, 0)

    return signedData


def verify(data: bytes | str, sign: bytes | str | None, is_hash: bool = False):
    """
    Диспетчер между различныйми способами проверки подписи
    переключается в зависимости от типа входных данных
    """

    match (data, sign, is_hash):
        case bytes(data), bytes(sign), _:
            data = wrapper_hash_object(data)
            sign = data_to_base64(sign)
            signed_data = verify_hash(data, sign)
        case bytes(data), str(sign), _:
            data = wrapper_hash_object(data)
            signed_data = verify_hash(data, sign)
        case str(data), str(sign), False:
            data = text_to_base64(data)
            signed_data = verify_data(data, sign)
        case str(data), str(sign), True:
            data = wrapper_hash_object(data, not_data=True)
            signed_data = verify_hash(data, sign)
        case str(data), bytes(sign), True:
            data = wrapper_hash_object(data, not_data=True)
            sign = data_to_base64(sign)
            signed_data = verify_hash(data, sign)
        case bytes(data), None, _:
            data = data_to_base64(data)
            signed_data = verify_data(data, None)
        case str(data), None, _:
            signed_data = verify_data(data, None)
        case _:
            return None

    sing_schema = parse_sing(signed_data)
    return sing_schema


def verify_xml(data: str):
    signedXML = pycades.SignedXML()
    signedXML.Content = ""
    signedXML.Verify(data)
    sing_schema = parse_sing(signedXML)

    return sing_schema


def wrapper_signer(cert):
    signer = pycades.Signer()
    signer.Certificate = cert
    signer.CheckCertificate = True
    return signer


def sign_hash(
    data: bytes, signer, is_hash: bool = False, encoding_type=0
) -> str | bytes:
    """
    encoding_type
    0 - Данные сохраняются в виде строки в кодировке Base64. (CAPICOM_ENCODE_BASE64)
    1 - Данные сохраняются в виде чистой двоичной последовательности. CAPICOM_ENCODE_BINARY
    """
    hashedData = wrapper_hash_object(data, not_data=is_hash)
    signedData = pycades.SignedData()
    signature = signedData.SignHash(
        hashedData, signer, pycades.CADESCOM_CADES_BES, encoding_type
    )
    return signature


def sign_cades(
    data: bytes | str, signer, detached: bool = True, encoding_type: int = 0
) -> str | bytes:
    signedData = pycades.SignedData()

    if isinstance(data, bytes):
        signedData.Content = data_to_base64(data)
    elif isinstance(data, str) and detached:
        signedData.ContentEncoding = pycades.CADESCOM_BASE64_TO_BINARY
        signedData.Content = text_to_base64(data)
    else:
        signedData.Content = data

    signature = signedData.SignCades(
        signer, pycades.CADESCOM_CADES_BES, detached, encoding_type
    )
    return signature


def sign(
    data: bytes | str,
    cert,
    detached: bool = True,
    binary: bool = False,
    is_hash: bool = False,
) -> str | bytes | None:
    """
    Диспетчер между различныйми способами проверки подписи
    переключается в зависимости от типа входных данных
    """
    signer = wrapper_signer(cert)

    match (data, detached, binary, is_hash):
        case bytes(data), True, _, _:
            return sign_hash(data, signer, is_hash=False, encoding_type=binary)
        case bytes(data), False, _, _:
            return sign_cades(data, signer, detached=detached, encoding_type=binary)
        case str(data), _, _, False:
            return sign_cades(data, signer, detached=detached, encoding_type=binary)
        case str(data), _, _, True:
            return sign_hash(data, signer, is_hash=True, encoding_type=binary)
        case _:
            return None


def sign_xml(data: str, cert):
    signer = wrapper_signer(cert)

    signedXML = pycades.SignedXML()
    signedXML.Content = data
    signedXML.SignatureType = (
        pycades.CADESCOM_XML_SIGNATURE_TYPE_ENVELOPED | pycades.CADESCOM_XADES_BES
    )
    signature = signedXML.Sign(signer)

    return signature

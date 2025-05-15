import base64
import io
from zipfile import ZipFile
from pathlib import Path

################################################################


def data_to_base64(data: bytes) -> str:
    """
    Преобразование байтов в строку base64
    """
    return base64.b64encode(data).decode("utf-8")


################################################################


def text_to_base64(text: str) -> str:
    """
    Преобразование текста в строку base64
    """
    return data_to_base64(text.encode("utf-8"))


################################################################
def unzip_file_in_folder(zfile: Path, dir_out: Path) -> Path:
    """
    распаковка одного zip файла в директорию цель
    """
    with ZipFile(zfile.absolute(), "r") as zObject:
        zObject.extractall(path=dir_out.absolute())
    return Path(dir_out.absolute(), zfile.stem)


################################################################


def unzip_all_files_in_folder(dir_in: Path, dir_out: Path):
    """
    распаковка всех zip файлов из заданной директории
    в директорию цель
    """
    results = []
    for f in dir_in.rglob("*.zip"):
        results.append(unzip_file_in_folder(f, dir_out))
    return results


################################################################


def crypto_pro_description_error(code: str, description: str) -> str:
    match code.lower():
        case "0x800b0101":
            result = f"Электронная подпись верна, но срок действия одного из сертификатов цепочки истек или еще не наступил. {description}"
        case "0x80091007":
            result = f"Электронная подпись неверна. {description}"
        case "0x8007065b":
            result = f"Истекшая лицензия КриптоПро CSP. {description}"
        case "0x8009100e":
            result = f"Электронная подпись неверна. {description}"
        case "0x80090006":
            result = f"Электронная подпись неверна. {description}"
        case _:
            result = description
    return result


################################################################


def convert_to_io(data: bytes | str) -> io.BytesIO | io.StringIO:
    match data:
        case bytes():
            return io.BytesIO(data)
        case str():
            return io.StringIO(data)
        case _:
            raise


################################################################

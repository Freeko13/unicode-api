import os
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import is_zipfile, ZipFile

from app.core.result import Result
from app.core.util import download_file

UNICODE_ORG_ROOT = "https://www.unicode.org/Public"
UCDXML_FOLDER = "ucdxml"
ALL_CHARS_ZIP = "ucd.all.flat.zip"


def get_xml_unicode_database(version: str) -> Result[Path]:
    if os.environ.get("ENV") != "PROD":
        return Result.Ok(Path("/Users/aaronluna/Downloads/ucd.all.flat.xml"))
    return download_xml_unicode_database(version)


def download_xml_unicode_database(version: str) -> Result[Path]:
    with TemporaryDirectory() as tmpdir:
        download_result = download_unicode_xml_zip(version, tmpdir)
        if download_result.failure:
            return download_result
        xml_zip = download_result.value
        extract_result = extract_unicode_xml_from_zip(xml_zip, tmpdir)
        if extract_result.failure:
            return extract_result
        xml_file = extract_result.value
    return Result.Ok(xml_file)


def get_local_xml_unicode_database() -> Result[Path]:
    return Result.Ok(Path("/Users/aaronluna/Downloads/ucd.all.flat.xml"))


def download_unicode_xml_zip(version: str, local_folder: str) -> Result:
    url = get_all_chars_zip_url(version)
    local_folder = Path(local_folder)
    result = download_file(url, local_folder)
    if result.failure:
        return result
    xml_zip = result.value
    if not is_zipfile(xml_zip):
        return Result.Fail("Unicode XML Data file is not a valid .zip file!")
    return Result.Ok(xml_zip)


def get_all_chars_zip_url(version: str) -> str:
    return f"{UNICODE_ORG_ROOT}/{version}/{UCDXML_FOLDER}/{ALL_CHARS_ZIP}"


def extract_unicode_xml_from_zip(xml_zip: Path, local_folder: str) -> Result:
    with ZipFile(xml_zip, mode="r") as zip:
        zip.extractall(path=local_folder)
        extracted_xml_files = list(Path(local_folder).glob("*.xml"))
        if not extracted_xml_files:
            return Result.Fail(f"Error occurred extracting XML file from {xml_zip.name}!")
        if len(extracted_xml_files) != 1:
            error = f"{len(extracted_xml_files)} XML files were extracted from {xml_zip.name}, expected only 1:\n"
            for i, file in enumerate(extracted_xml_files, start=1):
                error += f"\tFile #{i}: {file.name}"
            return Result.Fail(error)
        xml_file = extracted_xml_files[0]
        return Result.Ok(xml_file)

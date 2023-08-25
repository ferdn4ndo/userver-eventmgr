import hashlib
import magic
import math
import os
import shutil
import tempfile
import time
from django.core.files.uploadedfile import InMemoryUploadedFile


def size_to_bytes(b: float = 0, kb: float = 0, mb: float = 0, gb: float = 0) -> int:
    size_in_bytes = b

    if kb is not None:
        size_in_bytes += 1024 * kb
    if mb is not None:
        size_in_bytes += math.pow(1024, 2) * mb
    if gb is not None:
        size_in_bytes += math.pow(1024, 3) * gb

    return round(size_in_bytes)


def get_mime_type(file_or_path) -> str:
    return magic.from_file(file_or_path, mime=True)


def check_if_media(file_path) -> bool:
    mime_type = get_mime_type(file_path)

    if mime_type is None:
        return False

    mime_start = mime_type.split('/')[0]
    return mime_start == 'video' or mime_start == 'image'


def generate_file_hash(filepath: str):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_random_file_temp_path() -> str:
    file_path = os.path.join(tempfile.gettempdir(), "{:.8f}.tmp".format(time.time()))
    while os.path.isfile(file_path):
        file_path = os.path.join(tempfile.gettempdir(), "{:.8f}.tmp".format(time.time()))
    return file_path


def save_from_memory(memory_file: InMemoryUploadedFile) -> str:
    local_filename = get_random_file_temp_path()
    with open(local_filename, 'wb') as file:
        shutil.copyfileobj(memory_file, file)
    return local_filename

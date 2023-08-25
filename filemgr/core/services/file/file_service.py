import hashlib
import os
import shutil
import tempfile
import time
from django.core.files.uploadedfile import InMemoryUploadedFile


class FileService:
    filepath: str

    def __init__(self, filepath: str = "") -> None:
        if filepath == "":
            filepath = self.get_random_file_temp_path()

        self.filepath = filepath

    def get_random_file_temp_path() -> str:
        file_path = os.path.join(tempfile.gettempdir(), "{:.8f}.tmp".format(time.time()))
        while os.path.isfile(file_path):
            file_path = os.path.join(tempfile.gettempdir(), "{:.8f}.tmp".format(time.time()))

        return file_path

    def get_file_hash(self) -> str:
        sha256_hash = hashlib.sha256()
        with open(self.filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def save_from_memory(self, memory_file: InMemoryUploadedFile) -> str:
        with open(self.filepath, 'wb') as file:
            shutil.copyfileobj(memory_file, file)

        return self.filepath

    @staticmethod
    def get_name_from_path(filepath: str) -> str:
        """
        Retrieves a name from a given path (ex: "/path/to/file_name.txt" will return "file_name")
        """
        filename = os.path.basename(filepath)

        return os.path.splitext(filename)[0]

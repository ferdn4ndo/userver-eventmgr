from rawkit.options import WhiteBalance
from rawkit.raw import Raw


class PhotoRawService:
    file_path: str

    def __init__(self, file_path: str):
        self.file_path = file_path

    def render_photo_from_cr2_raw_file(self, dest_filename):
        with Raw(filename=self.file_path) as raw:
            raw.options.white_balance = WhiteBalance(camera=False, auto=True)
            raw.save(filename=dest_filename)
        return True

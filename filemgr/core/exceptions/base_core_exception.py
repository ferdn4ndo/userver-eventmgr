class BaseCoreException(Exception):
    detail: str

    def __init__(self, details: str = ""):
        self.detail = details

    def __str__(self):
        return str(self.detail)

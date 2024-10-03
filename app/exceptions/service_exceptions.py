from app.exceptions.http_base_exceptions import NotFoundException, ConflictException

class ResourceNotFoundException(NotFoundException):
    def __init__(self, detail: str = "Requested resource was not found") -> None:
        super().__init__(detail)

class ResourceNotAddedException(ConflictException):
    def __init__(self, detail: str = "Creating new resource failed") -> None:
        super().__init__(detail)

class ResourceNotDeletedException(ConflictException):
    def __init__(self, detail: str = "Deleting resource failed") -> None:
        super().__init__(detail)

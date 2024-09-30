from app.exceptions.http_base_exceptions import NotFoundException

class ResourceNotFoundException(NotFoundException):
    def __init__(self) -> None:
        super().__init__("Requested resource was not found")

class ResourceNotAddedException(NotFoundException):
    def __init__(self) -> None:
        super().__init__("Creating new resource failed")

class ResourceNotDeletedException(NotFoundException):
    def __init__(self) -> None:
        super().__init__("Deleting resource failed")

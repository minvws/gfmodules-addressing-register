from app.exceptions.http_base_exceptions import NotFoundException, ConflictException


class AddressNotFoundException(NotFoundException):
    def __init__(self) -> None:
        super().__init__("Requested address is not found")


class UnsuccessfulAddException(ConflictException):
    def __init__(self) -> None:
        super().__init__("Creating new addresses failed")


class UnsuccessfulDeleteOperationException(ConflictException):
    def __init__(self) -> None:
        super().__init__("Deleting address failed")

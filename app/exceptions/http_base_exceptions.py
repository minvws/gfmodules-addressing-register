from fastapi.exceptions import HTTPException

# Reference can be found https://www.rfc-editor.org/rfc/rfc9110.html#status.409


class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Not found"):
        super().__init__(status_code=404, detail=detail)


class ConflictException(HTTPException):
    def __init__(self, detail: str = "Conflict Occurred"):
        super().__init__(status_code=409, detail=detail)

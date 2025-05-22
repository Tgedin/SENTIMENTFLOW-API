from fastapi import HTTPException

class CustomException(HTTPException):
    """
    Base class for custom exceptions in the application.
    Allows specifying a status code and detail message.
    """
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

# Example of more specific custom exceptions (can be expanded later)

class NotFoundException(CustomException):
    """Exception for resources not found (404)."""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)

class BadRequestException(CustomException):
    """Exception for bad requests (400)."""
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=400, detail=detail)

class UnauthorizedException(CustomException):
    """Exception for unauthorized access (401)."""
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=401, detail=detail)

class ForbiddenException(CustomException):
    """Exception for forbidden access (403)."""
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=403, detail=detail)

class UnprocessableEntityException(CustomException):
    """Exception for unprocessable entities (422), e.g., validation errors."""
    def __init__(self, detail: str = "Unprocessable entity"):
        super().__init__(status_code=422, detail=detail)

class InternalServerErrorException(CustomException):
    """Exception for internal server errors (500)."""
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(status_code=500, detail=detail)

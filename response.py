STATUS_CODE = {
    "OK": 200,
    "CREATED": 201,
    "ACCEPTED": 202,
    "NO_CONTENT": 204,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "INTERNAL_SERVER_ERROR": 500,
    "SERVICE_UNAVAILABLE": 503
}

class Response:
    def __init__(self, status_code: int, message: str, data=None):
        self.status_code = status_code
        self.message = message
        self.data = data

    def to_dict(self):
        return {
            "status_code": self.status_code,
            "message": self.message,
            "data": self.data
        }

    def __str__(self):
        return f"Response(status_code={self.status_code}, message='{self.message}')"
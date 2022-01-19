class ApiError(Exception):
    def __init__(self, message, http_error_code=500):
        self.http_error_code = http_error_code
        self.message = message
        super().__init__(message)

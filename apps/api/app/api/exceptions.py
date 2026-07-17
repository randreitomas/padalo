class DomainError(Exception):
    """Base exception for expected service-layer failures."""

    status_code = 400

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class NotFoundError(DomainError):
    status_code = 404


class ConflictError(DomainError):
    status_code = 409


class LedgerInvariantError(DomainError):
    status_code = 422


class DomainValidationError(DomainError):
    status_code = 422

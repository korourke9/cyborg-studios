class AppError(Exception):
    """Application failure with a user-visible message.

    Raise this (or a subclass) for expected failures. Unhandled infrastructure
    faults should be wrapped as AppError when they cross into application code
    so the API can always show ``message`` in an error banner.
    """

    def __init__(self, message: str) -> None:
        cleaned = message.strip()
        if not cleaned:
            raise ValueError("AppError requires a non-empty human-readable message")
        self.message = cleaned
        super().__init__(cleaned)


class NotFoundError(AppError):
    """The requested resource does not exist."""

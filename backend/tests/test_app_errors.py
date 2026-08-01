from gamebuilder.orchestration.application.errors import AppError


def test_app_error_requires_message() -> None:
    try:
        AppError("   ")
        raised = False
    except ValueError:
        raised = True
    assert raised


def test_app_error_exposes_message() -> None:
    error = AppError("  Something went wrong.  ")
    assert error.message == "Something went wrong."
    assert str(error) == "Something went wrong."

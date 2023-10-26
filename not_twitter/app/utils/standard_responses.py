"""Набор готовых стандартных JSONRespone."""
from fastapi import status
from fastapi.responses import JSONResponse


def get_not_found_response(message: str) -> JSONResponse:
    """Получить готовый ответ для статуса 404.

    Args:
        message (str): Желаемое сообщение об ошибке.

    Returns:
        Готовый JSONResponse
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "result": False,
            "error_type": "Not found error",
            "error_message": message,
        },
    )


def get_forbidden_response(message: str) -> JSONResponse:
    """Получить готовый ответ для статуса 403.

    Args:
        message (str): Желаемое сообщение об ошибке.

    Returns:
        Готовый JSONResponse
    """
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "result": False,
            "error_type": "Forbidden operation error",
            "error_message": message,
        },
    )


def get_success_response() -> JSONResponse:
    """Получить готовый простой ответ для статуса 200.

    Returns:
        Готовый JSONResponse
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": True},
    )

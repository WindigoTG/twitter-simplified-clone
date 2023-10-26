"""Проверка api-key и получение связанного с ним пользователя."""
from typing import Optional, Tuple

from fastapi import status
from fastapi.responses import JSONResponse

from not_twitter.app.database import crud_operations
from not_twitter.app.database.models import User


async def check_api_key(
    api_key: str,
) -> Tuple[Optional[User], Optional[JSONResponse]]:
    """Проверка api-key и получение связанного с ним пользователя.

    Возвращает кортеж из пользователя, если найден и JSONResponse
    с сообщением об ошибке,  если пользователь не найден.

    Args:
        api_key (str): api-key пользователя.

    Returns:
        Tuple[Optional[User], Optional[JSONResponse]]
    """
    user = await crud_operations.get_user_by_api_key(api_key)
    if user:
        error_response = None
    else:
        message = "Api-key for existing user is required"
        error_response = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "result": False,
                "error_type": "Authentication error",
                "error_message": message,
            },
        )

    return user, error_response

"""Эндпоинты для получения профилей пользователей."""
from fastapi import APIRouter, Header, Path, status
from typing_extensions import Annotated

from not_twitter.app.database import crud_operations
from not_twitter.app.utils import schemas, standard_responses
from not_twitter.app.utils.api_key_ckecker import check_api_key
from not_twitter.app.utils.endpoint_tags import Tags

router = APIRouter()


@router.get(
    "/api/users/me",
    summary="Получение информации о профиле текущего пользователя",
    response_model=schemas.ProfileResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": schemas.FailResponse}},
    status_code=status.HTTP_200_OK,
    tags=[Tags.users],
)
async def get_self_profile(
    api_key: Annotated[str, Header()],
):
    """Эндпоинт для получения профиля пользователя.

    Args:
        api_key (str): Api-key пользователя.

    Returns:
        Ответ с профилем пользователя или сообщением об ошибке.
    """
    user = await crud_operations.get_user_by_api_key(api_key)
    if user:
        return {"result": True, "user": user}

    message = "No user registered to api-key {api_key}".format(
        api_key=api_key,
    )
    return standard_responses.get_not_found_response(message)


@router.get(
    "/api/users/{user_id}",
    summary="Получение информации о профиле пользователя по ID",
    response_model=schemas.ProfileResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": schemas.FailResponse}},
    status_code=status.HTTP_200_OK,
    tags=[Tags.users],
)
async def get_user_profile(
    api_key: Annotated[str, Header()],
    user_id: Annotated[int, Path(description="ID пользователя")],
):
    """Эндпоинт для получения профиля пользователя по ID.

    Args:
        api_key (str): Api-key пользователя.
        user_id (int): ID пользователя.

    Returns:
        Ответ с профилем пользователя или сообщением об ошибке.
    """
    _, error_response = await check_api_key(api_key)

    if error_response:
        return error_response

    user = await crud_operations.get_user_by_id(user_id)
    if user:
        return {"result": True, "user": user}

    message = "No user with ID {user_id}".format(
        user_id=user_id,
    )
    return standard_responses.get_not_found_response(message)

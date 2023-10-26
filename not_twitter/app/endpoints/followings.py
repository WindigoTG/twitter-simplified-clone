"""Эндпоинты для подписки и отписки."""
from fastapi import APIRouter, Header, Path, status
from typing_extensions import Annotated

from not_twitter.app.database import crud_operations
from not_twitter.app.utils import schemas, standard_responses
from not_twitter.app.utils.api_key_ckecker import check_api_key
from not_twitter.app.utils.endpoint_tags import Tags

router = APIRouter()


# Косяк во фронтенде: вместо метода POST вызывается DELETE для подписки
@router.delete(
    "/api/users/{user_id}/follow",
    response_model=schemas.Response,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": schemas.FailResponse},
        status.HTTP_403_FORBIDDEN: {"model": schemas.FailResponse},
        status.HTTP_404_NOT_FOUND: {"model": schemas.FailResponse},
    },
    summary="Подписка на пользователя по ID",
    tags=[Tags.users],
)
async def follow_user(
    api_key: Annotated[str, Header()],
    user_id: Annotated[int, Path(description="ID пользователя для подписки")],
):
    """Эндпоинт подписки на пользователя.

    Args:
        api_key (str): Api-key пользователя.
        user_id (int): ID пользователя.

    Returns:
        Ответ с сообщением об успехе или ошибке.
    """
    follower, error_response = await check_api_key(api_key)

    if error_response:
        return error_response

    followed = await crud_operations.get_user_by_id(user_id)

    if not followed:
        message = "User with id {user_id} does not exist".format(
            user_id=user_id,
        )
        return standard_responses.get_not_found_response(message)

    if follower.id == followed.id:
        message = "Can not follow yourself"
        return standard_responses.get_forbidden_response(message)

    await crud_operations.add_following(followed, follower)
    return standard_responses.get_success_response()


@router.delete(
    # Косяк во фронтенде: вместо пути users используется tweets для отписки
    "/api/tweets/{user_id}/follow",
    summary="Отписка от пользователя по ID",
    tags=[Tags.users],
)
async def unfollow_user(
    user_id: Annotated[int, Path(description="ID пользователя для отписки")],
    api_key: Annotated[str, Header()],
):
    """Эндпоинт отписки от пользователя.

    Args:
        api_key (str): Api-key пользователя.
        user_id (int): ID пользователя.

    Returns:
        Ответ с сообщением об успехе или ошибке.
    """
    follower, error_response = await check_api_key(api_key)

    if error_response:
        return error_response

    followed = await crud_operations.get_user_by_id(user_id)

    if not followed:
        message = "User with id {user_id} does not exist".format(
            user_id=user_id,
        )
        return standard_responses.get_not_found_response(message)

    if follower.id == followed.id:
        message = "Can not unfollow yourself"
        return standard_responses.get_forbidden_response(message)

    await crud_operations.remove_following(followed, follower)
    return standard_responses.get_success_response()

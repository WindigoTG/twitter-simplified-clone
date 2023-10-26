"""Эндпоинты для добавления и удаления лайков."""

from fastapi import APIRouter, Header, Path, status
from typing_extensions import Annotated

from not_twitter.app.database import crud_operations
from not_twitter.app.utils import schemas, standard_responses
from not_twitter.app.utils.api_key_ckecker import check_api_key
from not_twitter.app.utils.endpoint_tags import Tags

router = APIRouter()


@router.post(
    "/api/tweets/{tweet_id}/likes",
    response_model=schemas.Response,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": schemas.FailResponse},
        status.HTTP_403_FORBIDDEN: {"model": schemas.FailResponse},
        status.HTTP_404_NOT_FOUND: {"model": schemas.FailResponse},
    },
    summary="Поставить лайк на твит",
    tags=[Tags.tweets],
)
async def like_tweet(
    api_key: Annotated[str, Header()],
    tweet_id: Annotated[int, Path(description="ID твита для лайка")],
):
    """Эндпоинт для добавления лайка на твит.

    Args:
        api_key (str): Api-key пользователя.
        tweet_id: ID твита.

    Returns:
        Ответ с сообщением об успехе или ошибке.
    """
    user, error_response = await check_api_key(api_key)

    if error_response:
        return error_response

    tweet = await crud_operations.get_tweet_by_id(tweet_id)

    if not tweet:
        message = "Tweet with id {tweet_id} does not exist".format(
            tweet_id=tweet_id,
        )
        return standard_responses.get_not_found_response(message)

    if user.id == tweet.author_id:
        message = "Can not like self own tweets"
        return standard_responses.get_forbidden_response(message)

    await crud_operations.add_like_by_user_to_tweet(user, tweet)
    return standard_responses.get_success_response()


@router.delete(
    "/api/tweets/{tweet_id}/likes",
    response_model=schemas.Response,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": schemas.FailResponse},
        status.HTTP_403_FORBIDDEN: {"model": schemas.FailResponse},
        status.HTTP_404_NOT_FOUND: {"model": schemas.FailResponse},
    },
    summary="Убрать лайк с твита",
    tags=[Tags.tweets],
)
async def remove_like(
    tweet_id: Annotated[int, Path(description="ID твита для удаления лайка")],
    api_key: Annotated[str, Header()],
):
    """Эндпоинт для удаления лайка с твита.

    Args:
        api_key (str): Api-key пользователя.
        tweet_id: ID твита.

    Returns:
        Ответ с сообщением об успехе или ошибке.
    """
    user, error_response = await check_api_key(api_key)

    if error_response:
        return error_response

    tweet = await crud_operations.get_tweet_by_id(tweet_id)

    if not tweet:
        message = "Tweet with id {tweet_id} does not exist".format(
            tweet_id=tweet_id,
        )
        return standard_responses.get_not_found_response(message)

    if user.id == tweet.author_id:
        message = "Can not remove likes from self own tweets"
        return standard_responses.get_forbidden_response(message)

    await crud_operations.delete_like_by_user_from_tweet(user, tweet)
    return standard_responses.get_success_response()

"""Эндпоинты для создания, получения и удаления твитов."""
from typing import List

from fastapi import Body, APIRouter, Header, Path, status
from typing_extensions import Annotated

from not_twitter.app.database import crud_operations
from not_twitter.app.utils import schemas, standard_responses
from not_twitter.app.utils.api_key_ckecker import check_api_key
from not_twitter.app.utils.endpoint_tags import Tags

router = APIRouter()


@router.get(
    "/api/tweets",
    summary="Получение твитов для ленты пользователя",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TweetsResponse,
    tags=[Tags.tweets],
)
async def get_tweets(
    api_key: Annotated[str, Header()],
):
    """Эндпоинт для получения списка твитов.

    Args:
        api_key (str): Api-key пользователя.

    Returns:
        Ответ со списком твитов.
    """
    _, error_response = await check_api_key(api_key)

    if error_response:
        return error_response

    tweets = await crud_operations.get_all_tweets()
    return {"result": True, "tweets": tweets}


@router.post(
    "/api/tweets",
    summary="Создание нового твита",
    responses={status.HTTP_401_UNAUTHORIZED: {"model": schemas.FailResponse}},
    response_model=schemas.TweetCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    tags=[Tags.tweets],
)
async def post_tweet(
    api_key: Annotated[str, Header()],
    tweet_data: Annotated[str, Body()],
    tweet_media_ids: Annotated[List[int], Body()] = None,
):
    """Эндпоинт для создания нового твита.

    Args:
        api_key (str): Api-key пользователя.
        tweet_data (str): Содержимое твита.
        tweet_media_ids (List[int]): Список ID медиа твита.

    Returns:
        Ответ с ID созданного твита или сообщение об ошибке.
    """
    user, error_response = await check_api_key(api_key)

    if error_response:
        return error_response

    tweet_id = await crud_operations.create_tweet(
        user,
        tweet_data,
        tweet_media_ids,
    )
    return {"result": True, "tweet_id": tweet_id}


@router.delete(
    "/api/tweets/{tweet_id}",
    response_model=schemas.Response,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": schemas.FailResponse},
        status.HTTP_403_FORBIDDEN: {"model": schemas.FailResponse},
        status.HTTP_404_NOT_FOUND: {"model": schemas.FailResponse},
    },
    summary="Удаление твита",
    tags=[Tags.tweets],
)
async def delete_tweet(
    api_key: Annotated[str, Header()],
    tweet_id: Annotated[int, Path(description="ID удаляемого твита")],
):
    """Эндпоинт для удаления твита.

    Args:
        api_key (str): Api-key пользователя.
        tweet_id (int): ID удаляемого твита.

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

    if user.id != tweet.author_id:
        message = "Api-key for tweet's author must be provided to delete tweet"
        return standard_responses.get_forbidden_response(message)

    await crud_operations.delete_given_tweet(tweet)
    return standard_responses.get_success_response()

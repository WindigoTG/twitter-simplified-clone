"""Эндпоинты для загрузки и получения медиа."""
import io

from fastapi import APIRouter, File, Header, Path, UploadFile, status
from fastapi.responses import StreamingResponse
from typing_extensions import Annotated

from not_twitter.app.database import crud_operations
from not_twitter.app.utils import schemas, standard_responses
from not_twitter.app.utils.api_key_ckecker import check_api_key
from not_twitter.app.utils.endpoint_tags import Tags

router = APIRouter()


@router.post(
    "/api/medias",
    responses={status.HTTP_401_UNAUTHORIZED: {"model": schemas.FailResponse}},
    response_model=schemas.MediaUploadedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Загрузка файлов из твита в БД",
    tags=[Tags.media],
)
async def upload_media(
    api_key: Annotated[str, Header()],
    file: Annotated[UploadFile, File()],
):
    """Эндпоинт для загрузки медиа.

    Args:
        api_key (str): Api-key пользователя.
        file (UploadFile): Загружаемый медиа файл.

    Returns:
        Ответ с ID загруженного медиа.
    """
    user, error_response = await check_api_key(api_key)

    if error_response:
        return error_response

    media_id = await crud_operations.add_media(file.file.read())
    return {"result": True, "media_id": media_id}


@router.get(
    "/api/medias/{media_id}",
    responses={status.HTTP_404_NOT_FOUND: {"model": schemas.FailResponse}},
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение файлов из твита из БД",
    tags=[Tags.media],
)
async def download_media(
    media_id: Annotated[int, Path()],
):
    """Получение медиа для твита.

    Args:
        media_id (int): ID медиа.

    Returns:
        Запрошенное медиа или сообщение об ошибке.
    """
    media = await crud_operations.get_media_by_id(media_id)
    if media:
        return StreamingResponse(io.BytesIO(media.media_data))

    message = "No media with ID {media_id}".format(
        media_id=media_id,
    )
    return standard_responses.get_not_found_response(message)

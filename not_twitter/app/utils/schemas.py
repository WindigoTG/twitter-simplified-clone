"""Pydantic схемы для верификации данных."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class BaseUser(BaseModel):
    """Базовая модель пользователя."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class UserProfile(BaseUser):
    """Модель профиля пользователя."""

    model_config = ConfigDict(from_attributes=True)

    followers: List[BaseUser]
    following: List[BaseUser]


class Response(BaseModel):
    """Модель базового ответа."""

    result: bool


class ProfileResponse(Response):
    """Модель ответа с профилем пользователя."""

    model_config = ConfigDict(from_attributes=True)

    user: UserProfile


class FailResponse(Response):
    """Модель неудачного ответа."""

    error_type: str
    error_message: str


class Like(BaseModel):
    """Модель лайка."""

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str


class Tweet(BaseModel):
    """Модель твита."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    attachments: Optional[List[str]]
    author: BaseUser
    likes: List[Like]


class TweetsResponse(Response):
    """Модель ответа со списком твитов."""

    tweets: List[Tweet]


class TweetCreatedResponse(Response):
    """Модель ответа при успешном создании твита."""

    tweet_id: int


class MediaUploadedResponse(Response):
    """Модель ответа при успешной загрузке медиа."""

    media_id: int

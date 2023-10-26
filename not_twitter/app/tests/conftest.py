"""Фикстуры для тестирования приложения."""

import os  # noqa

POSTGRES_USER = "testnottwitter"  # noqa
POSTGRES_PASSWORD = "testd3f1n1t3lyjustacl0n3"  # noqa
POSTGRES_DB = "test_not_twitter_db"  # noqa
POSTGRES_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@127.0.0.1:5432/{POSTGRES_DB}"  # noqa

os.environ["POSTGRES_URL"] = POSTGRES_URL  # noqa

import asyncio
from typing import Dict, List

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from not_twitter.app.database.database import Base
from not_twitter.app.database import models
from not_twitter.app.main import app

pytest_plugins = ("pytest_asyncio",)

engine = create_async_engine(POSTGRES_URL, echo=True)
async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session.

    Yields:
        loop: event loop.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def client():
    """Тестовый клиент FastAPI.

    Yields:
        client (TestClient): тестовый клиент FastAPI.
    """
    with TestClient(app) as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def session():
    """Сессия для работы с тестовой БД.

    Yields:
        session (AsyncSession): Сессия для работы с БД.
    """
    # global async_session
    async with async_session() as session:
        yield session


async def delete_entries(session: AsyncSession, entries: List[Base]) -> None:
    for entry in entries:
        await session.delete(entry)
    await session.commit()


@pytest_asyncio.fixture(scope="function")
async def api_keys(session: AsyncSession):
    """Создание api-keys и связанных с ними пользователей.

    Args:
        session (AsyncSession): сессия для работы с БД.

    Yields:
        test_api_keys (List[ApiKeyToUser]): Список тестовых api-key.
    """
    test_users = [
        models.User(name="Test_User_1"),
        models.User(name="Test_User_2"),
    ]
    session.add_all(test_users)
    await session.commit()

    test_api_keys = [
        models.ApiKeyToUser(api_key="test_key_1", user_id=test_users[0].id),
        models.ApiKeyToUser(api_key="test_key_2", user_id=test_users[1].id),
    ]

    session.add_all(test_api_keys)
    await session.commit()

    yield test_api_keys

    await delete_entries(session, test_users)


@pytest_asyncio.fixture(scope="function")
async def tweets_and_api_keys(
    session: AsyncSession,
    api_keys: List[models.ApiKeyToUser],
):
    """Создание api-keys, связанных с ними пользователей и их твитов.

    Args:
        session (AsyncSession): сессия для работы с БД.
        api_keys (List[ApiKeyToUser]): Список тестовых api-key.

    Yields:
        test_tweets_and_api_keys (Dict[str, List[base]])
    """
    test_tweets = [
        models.Tweet(content="test_tweet_1", author_id=api_keys[0].user_id),
        models.Tweet(content="test_tweet_2", author_id=api_keys[1].user_id),
    ]

    session.add_all(test_tweets)
    await session.commit()

    test_tweets_and_api_keys = {
        "api_keys": api_keys,
        "tweets": test_tweets,
    }

    yield test_tweets_and_api_keys


@pytest_asyncio.fixture(scope="function")
async def liked_tweets_and_api_keys(
    session: AsyncSession,
    tweets_and_api_keys: Dict[str, List[models.Base]],
):
    """Создание api-keys, связанных с ними пользователей и их твитов и лайков.

    Args:
        session (AsyncSession): сессия для работы с БД.
        tweets_and_api_keys (Dict[str, List[base]]): api-keys и твиты.

    Yields:
        liked_test_tweets_and_api_keys (Dict[str, List[base]])
    """
    api_keys = tweets_and_api_keys["api_keys"]
    tweets = tweets_and_api_keys["tweets"]
    test_likes = [
        models.Like(
            tweet_id=tweets[0].id,
            user_id=api_keys[1].user_id,
            name="",
        ),
        models.Like(
            tweet_id=tweets[1].id,
            user_id=api_keys[0].user_id,
            name="",
        ),
    ]

    session.add_all(test_likes)
    await session.commit()

    yield tweets_and_api_keys


@pytest_asyncio.fixture(scope="function")
async def followed_users_api_keys(
    session: AsyncSession,
    api_keys: List[models.ApiKeyToUser],
):
    """Создание api-keys, связанных с ними пользователей и подписок.

    Args:
        session (AsyncSession): сессия для работы с БД.
        api_keys (List[ApiKeyToUser]): Список тестовых api-key.

    Yields:
        followed_users_api_keys (List[ApiKeyToUser]): Список тестовых api-key.
    """
    test_followings = [
        models.Following(
            follower_id=api_keys[0].user_id,
            followed_id=api_keys[1].user_id,
        ),
        models.Following(
            follower_id=api_keys[1].user_id,
            followed_id=api_keys[0].user_id,
        ),
    ]

    session.add_all(test_followings)
    await session.commit()

    yield api_keys


@pytest_asyncio.fixture(scope="function")
async def media(session: AsyncSession):
    """Создание api-keys, связанных с ними пользователей и подписок.

    Args:
        session (AsyncSession): сессия для работы с БД.

    Yields:
        test_media(Media): тестовое медиа.
    """
    test_media = models.Media(media_data=b"test_media")
    session.add(test_media)
    await session.commit()

    yield test_media

    await delete_entries(session, [test_media])

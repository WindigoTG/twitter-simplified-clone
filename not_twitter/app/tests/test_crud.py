"""Тестирование CRUD операций с базой данных."""
import pytest
from sqlalchemy import select

from not_twitter.app.database import crud_operations, models

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_get_user_by_api_key(api_keys):
    """Тестирование функции get_user_by_api_key.

    Args:
        api_keys (List[ApiKeyToUser]): Список тестовых api-key.
    """
    api_key = api_keys[0].api_key
    result = await crud_operations.get_user_by_api_key(api_key)
    assert isinstance(result, models.User)


@pytest.mark.asyncio
async def test_get_user_by_id(api_keys):
    """Тестирование функции get_user_by_id.

    Args:
        api_keys (List[ApiKeyToUser]): Список тестовых api-key.

    """
    user_id = api_keys[0].user_id
    result = await crud_operations.get_user_by_id(user_id)
    assert isinstance(result, models.User)
    assert result.id == user_id


@pytest.mark.asyncio
async def test_create_tweet(session, api_keys):
    """Тестирование функции create_tweet.

    Args:
        session (AsyncSession): сессия для работы с БД.
        api_keys (List[ApiKeyToUser]): Список тестовых api-key.
    """
    all_tweets = await session.execute(select(models.Tweet))
    all_tweets = all_tweets.scalars().all()
    count_before = len(all_tweets) if all_tweets else 0

    user = models.User(id=api_keys[0].user_id, name="user")
    content = "content"
    result = await crud_operations.create_tweet(user, content, [])

    all_tweets = await session.execute(select(models.Tweet))
    all_tweets = all_tweets.scalars().all()
    count_after = len(all_tweets) if all_tweets else 0

    assert isinstance(result, int)
    query = select(models.Tweet).where(models.Tweet.id == result)
    tweet = await session.execute(query)
    assert isinstance(tweet.scalar(), models.Tweet)
    assert count_after - count_before == 1


@pytest.mark.asyncio
async def test_get_tweets_by_author_id(tweets_and_api_keys):
    """Тестирование функции get_tweets_by_author_id.

    Args:
        tweets_and_api_keys (Dict[str, List[base]]): тестовые твиты и api-keys.
    """
    author_id = tweets_and_api_keys["api_keys"][0].user_id
    result = await crud_operations.get_tweets_by_author_id(author_id)
    assert isinstance(result, list)
    assert isinstance(result[0], models.Tweet)


@pytest.mark.asyncio
async def test_get_tweet_by_id(tweets_and_api_keys):
    """Тестирование функции get_tweet_by_id.

    Args:
        tweets_and_api_keys (Dict[str, List[base]]): тестовые твиты и api-keys.
    """
    test_tweet = tweets_and_api_keys["tweets"][0]
    result = await crud_operations.get_tweet_by_id(test_tweet.id)
    assert isinstance(result, models.Tweet)
    assert result.id == test_tweet.id
    assert result.content == test_tweet.content


@pytest.mark.asyncio
async def test_get_all_tweets(tweets_and_api_keys):
    """Тестирование функции get_all_tweets.

    Args:
        tweets_and_api_keys (Dict[str, List[base]]): тестовые твиты и api-keys.
    """
    tweets = tweets_and_api_keys["tweets"]
    result = await crud_operations.get_all_tweets()
    assert isinstance(result, list)
    assert isinstance(result[0], models.Tweet)
    assert len(result) == len(tweets)


@pytest.mark.asyncio
async def test_add_like_by_user_to_tweet(session, tweets_and_api_keys):
    """Тестирование функции add_like_by_user_to_tweet.

    Args:
        session (AsyncSession): сессия для работы с БД.
        tweets_and_api_keys (Dict[str, List[base]]): тестовые твиты и api-keys.
    """
    tweet = tweets_and_api_keys["tweets"][0]
    api_keys = tweets_and_api_keys["api_keys"]
    user = await crud_operations.get_user_by_id(api_keys[1].user_id)

    query = select(models.Like).where(models.Like.tweet_id == tweet.id)
    likes = await session.execute(query)
    likes = likes.scalars().all()
    count_before = len(likes) if likes else 0

    await crud_operations.add_like_by_user_to_tweet(user, tweet)

    query = select(models.Like).where(models.Like.tweet_id == tweet.id)
    likes = await session.execute(query)
    likes = likes.scalars().all()
    count_after = len(likes) if likes else 0

    assert count_after - count_before == 1

    query = select(models.Like).where(
        (models.Like.tweet_id == tweet.id and models.Like.user_id == user.id),
    )
    like = await session.execute(query)
    assert isinstance(like.scalar(), models.Like)


@pytest.mark.asyncio
async def test_delete_like_by_user_from_tweet(
    session,
    liked_tweets_and_api_keys,
):
    """Тестирование функции delete_like_by_user_from_tweet.

    Args:
        session (AsyncSession): сессия для работы с БД.
        liked_tweets_and_api_keys (Dict[str, List[base]]): твиты и api-keys.
    """
    tweet = liked_tweets_and_api_keys["tweets"][0]
    api_keys = liked_tweets_and_api_keys["api_keys"]
    user = await crud_operations.get_user_by_id(api_keys[1].user_id)

    query = select(models.Like).where(models.Like.tweet_id == tweet.id)
    likes = await session.execute(query)
    likes = likes.scalars().all()
    count_before = len(likes) if likes else 0

    await crud_operations.delete_like_by_user_from_tweet(user, tweet)

    query = select(models.Like).where(models.Like.tweet_id == tweet.id)
    likes = await session.execute(query)
    likes = likes.scalars().all()
    count_after = len(likes) if likes else 0

    assert count_before - count_after == 1

    query = select(models.Like).where(
        (models.Like.tweet_id == tweet.id and models.Like.user_id == user.id),
    )
    like = await session.execute(query)
    assert like.scalar() is None


@pytest.mark.asyncio
async def test_delete_given_tweet(session, tweets_and_api_keys):
    """Тестирование функции test_delete_given_tweet.

    Args:
        session (AsyncSession): сессия для работы с БД.
        tweets_and_api_keys (Dict[str, List[base]]): тестовые твиты и api-keys.
    """
    tweet = tweets_and_api_keys["tweets"][0]
    test_tweet_id = tweet.id

    all_tweets = await session.execute(select(models.Tweet))
    all_tweets = all_tweets.scalars().all()
    count_before = len(all_tweets) if all_tweets else 0

    await crud_operations.delete_given_tweet(tweet)

    all_tweets = await session.execute(select(models.Tweet))
    all_tweets = all_tweets.scalars().all()
    count_after = len(all_tweets) if all_tweets else 0

    query = select(models.Tweet).where(models.Tweet.id == test_tweet_id)
    tweet = await session.execute(query)
    assert not tweet.scalar()
    assert count_before - count_after == 1


@pytest.mark.asyncio
async def test_add_following(session, api_keys):
    """Тестирование функции add_following.

    Args:
        session (AsyncSession): сессия для работы с БД.
        api_keys (List[ApiKeyToUser]): Список тестовых api-key.
    """
    followed = await crud_operations.get_user_by_id(api_keys[0].user_id)
    follower = await crud_operations.get_user_by_id(api_keys[1].user_id)

    followings = await session.execute(select(models.Following))
    followings = followings.scalars().all()
    count_before = len(followings) if followings else 0

    await crud_operations.add_following(followed, follower)

    followings = await session.execute(select(models.Following))
    followings = followings.scalars().all()
    count_after = len(followings) if followings else 0

    assert count_after - count_before == 1


@pytest.mark.asyncio
async def test_remove_following(session, followed_users_api_keys):
    """Тестирование функции remove_following.

    Args:
        session (AsyncSession): сессия для работы с БД.
        followed_users_api_keys (List[ApiKeyToUser]): Список тестовых api-key.
    """
    followed = await crud_operations.get_user_by_id(
        followed_users_api_keys[0].user_id,
    )
    follower = await crud_operations.get_user_by_id(
        followed_users_api_keys[1].user_id,
    )

    followings = await session.execute(select(models.Following))
    followings = followings.scalars().all()
    count_before = len(followings) if followings else 0

    await crud_operations.remove_following(followed, follower)

    followings = await session.execute(select(models.Following))
    followings = followings.scalars().all()
    count_after = len(followings) if followings else 0

    assert count_before - count_after == 1


@pytest.mark.asyncio
async def test_add_media(session):
    """Тестирование функции add_media.

    Args:
        session (AsyncSession): сессия для работы с БД.
    """
    test_bytes: bytes = b"test_bytes"

    medias = await session.execute(select(models.Media))
    medias = medias.scalars().all()
    count_before = len(medias) if medias else 0

    test_media_id = await crud_operations.add_media(test_bytes)

    medias = await session.execute(select(models.Media))
    medias = medias.scalars().all()
    count_after = len(medias) if medias else 0

    assert isinstance(test_media_id, int)
    assert count_after - count_before == 1


@pytest.mark.asyncio
async def test_get_media(media):
    """Тестирование функции get_media.

    Args:
        media (Media): тестовое медиа.
    """
    result = await crud_operations.get_media_by_id(media.id)

    assert isinstance(result, models.Media)
    assert result.media_data == media.media_data

"""CRUD операции с базой данных."""
from typing import Dict, List, Optional

from sqlalchemy import delete, desc
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from not_twitter.app.database.database import async_session
from not_twitter.app.database.models import (
    ApiKeyToUser,
    Following,
    Like,
    Media,
    Tweet,
    User,
)

MEDIA_URL = "api/medias/"


async def fill_db(users_data: Dict[str, str]) -> None:
    """Создание пользователей и Api-key в базе данных.

    Args:
        users_data (Dict[str, str]): Словарь 'api_key': 'имя_пользователя'.
    """
    async with async_session() as session:
        query = await session.execute(select(ApiKeyToUser.api_key))
        api_keys = query.scalars()
        users_to_add = []
        keys_to_add = []
        for key in users_data.keys():
            if key not in api_keys:
                users_to_add.append(User(name=users_data[key]))
                keys_to_add.append(ApiKeyToUser(api_key=key))

        if not users_to_add:
            return

        session.add_all(users_to_add)
        await session.commit()

        for idx in range(len(users_to_add)):
            keys_to_add[idx].user_id = users_to_add[idx].id
        session.add_all(keys_to_add)
        await session.commit()
        await session.close()


async def get_user_by_api_key(api_key: str) -> Optional[User]:
    """Получение пользователя из БД по его api-key.

    Args:
        api_key (str): Api-key пользователя.

    Returns:
        User: Объект пользователя или None.
    """
    async with async_session() as session:
        async with session.begin():
            query = await session.execute(
                select(ApiKeyToUser)
                .where(ApiKeyToUser.api_key == api_key)
                .options(
                    selectinload(ApiKeyToUser.user).subqueryload(User.following),
                    selectinload(ApiKeyToUser.user).subqueryload(User.followers),
                )
            )
            key_to_user = query.scalar()
            if key_to_user:
                return key_to_user.user
            return None


async def get_user_by_id(user_id: int) -> Optional[User]:
    """Получение пользователя из БД по его ID.

    Args:
        user_id (int): ID пользователя.

    Returns:
        User: Объект пользователя или None.
    """
    async with async_session() as session:
        async with session.begin():
            query = await session.execute(
                select(User)
                .where(User.id == user_id)
                .options(
                    selectinload(User.following),
                    selectinload(User.followers),
                )
            )
            return query.scalar()


async def create_tweet(user: User, content: str, media_ids: List[int]) -> int:
    """Создание твита в БД за авторством пользователя.

    Args:
        user (User): Объект автора твита.
        content (str): Содержимое твита.
        media_ids (List[int]): Автор твита.

    Returns:
        int: ID созданного твита.
    """
    async with async_session() as session:
        new_tweet = Tweet(
            content=content,
            author_id=user.id,
            attachments=[MEDIA_URL + str(media_id) for media_id in media_ids],
        )
        session.add(new_tweet)
        await session.commit()
        if media_ids:
            query = await session.execute(
                select(Media).filter(Media.id.in_(media_ids)),
            )
            medias = query.scalars()
            for media in medias:
                media.tweet_id = new_tweet.id
            await session.commit()
        await session.close()
        return new_tweet.id


async def get_tweets_by_author_id(author_id: int) -> Optional[List[Tweet]]:
    """Получение списка твитов из БД по ID автора.

    Args:
        author_id (int): ID автора твитов.

    Returns:
        List[Tweet]: Список объектов твитов.
    """
    async with async_session() as session:
        async with session.begin():
            query = await session.execute(
                select(Tweet)
                .where(Tweet.author_id == author_id)
                .order_by(desc(Tweet.id))
                .options(selectinload(Tweet.likes)),
            )
            return query.scalars().all()


async def get_tweet_by_id(tweet_id: int) -> Optional[Tweet]:
    """Получение твита из БД по его ID.

    Args:
        tweet_id (int): ID твита.

    Returns:
        Tweet: Объект твита или None.
    """
    async with async_session() as session:
        async with session.begin():
            query = await session.execute(
                select(Tweet)
                .where(Tweet.id == tweet_id)
                .options(
                    selectinload(Tweet.likes),
                )
            )
            return query.scalar()


async def get_all_tweets() -> Optional[List[Tweet]]:
    """Получение списка всех твитов из БД.

    Returns:
        List[Tweet]: Список объектов твитов или None.
    """
    async with async_session() as session:
        async with session.begin():
            query = await session.execute(
                select(Tweet)
                .order_by(desc(Tweet.id))
                .options(
                    selectinload(Tweet.likes),
                )
            )
            return query.scalars().all()


async def delete_tweet_by_id(tweet_id: int) -> None:
    """Удаление твита из БД по его ID.

    Args:
        tweet_id (int): ID твита.
    """
    async with async_session() as session:
        async with session.begin():
            await session.execute(delete(Tweet).where(Tweet.id == tweet_id))
            await session.commit()


async def delete_given_tweet(tweet: Tweet) -> None:
    """Удаление твита из БД на основании его объекта.

    Args:
        tweet (Tweet): Объект твита.
    """
    await delete_tweet_by_id(tweet.id)


async def add_media(data: bytes) -> int:
    """Добавление медиа в БД.

    Args:
        data (bytes): Байтовая строка добавляемого медиа.

    Returns:
        int: ID добавленного медиа.
    """
    async with async_session() as session:
        async with session.begin():
            new_media = Media(media_data=data)
            session.add(new_media)
            await session.commit()
            return new_media.id


async def get_media_by_id(media_id: int) -> Optional[Media]:
    """Получение медиа из БД по ID.

    Args:
        media_id (int): ID медиа в БД.

    Returns:
        Media: Объект медиа или None.
    """
    async with async_session() as session:
        async with session.begin():
            query = await session.execute(
                select(Media).where(Media.id == media_id),
            )
            return query.scalar()


async def add_like_by_user_to_tweet(user: User, tweet: Tweet) -> None:
    """Создание записи о лайке твита в БД.

    Args:
        user (User): Объект пользователя, поставившего лайк.
        tweet (Tweet): Объект твита, которому поставлен лайк
    """
    async with async_session() as session:
        async with session.begin():
            new_like = Like(
                tweet_id=tweet.id,
                user_id=user.id,
                name=user.name,
            )
            session.add(new_like)
            await session.commit()


async def delete_like_by_user_from_tweet(user: User, tweet: Tweet) -> None:
    """Удаление записи о лайке твита в БД.

    Args:
        user (User): Объект пользователя, поставившего лайк.
        tweet (Tweet): Объект твита, которому поставлен лайк
    """
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                delete(Like).where(
                    Like.tweet_id == tweet.id and Like.user_id == user.id,
                )
            )
            await session.commit()


async def add_following(followed: User, follower: User) -> None:
    """Создание записи о подписке одного пользователя на другого.

    Args:
        followed (User): Объект пользователя, на которого подписались.
        follower (User): Объект подписавшегося пользователя.
    """
    async with async_session() as session:
        async with session.begin():
            new_following = Following(
                followed_id=followed.id,
                follower_id=follower.id,
            )
            session.add(new_following)
            await session.commit()


async def remove_following(followed: User, follower: User) -> None:
    """Удаление записи о подписке одного пользователя на другого.

    Args:
        followed (User): Объект пользователя, на которого подписались.
        follower (User): Объект подписавшегося пользователя.
    """
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                delete(Following).where(
                    Following.followed_id == followed.id
                    and Following.follower_id == follower.id,
                )
            )
            await session.commit()

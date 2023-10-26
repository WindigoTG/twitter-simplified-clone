"""Тестирование эндпоинтов приложения."""
from typing import Dict

from fastapi import status


def get_api_key_headers(api_key: str) -> Dict[str, str]:
    """Получение готовых хэдеров с указанным api-key.

    Args:
        api_key (str): желаемый api-key.

    Returns:
        headers (Dict[str, str]): словарь хэдеров.
    """
    return {"api-key": api_key}


def test_get_users_me(client, api_keys):
    """Тестирование эндпоинта /api/users/me.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        api_keys (List[ApiKeyToUser]): Список тестовых api-key.
    """
    headers = get_api_key_headers(api_keys[0].api_key)
    response = client.get("/api/users/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    res_json = response.json()
    assert res_json.get("result")
    assert res_json.get("user") is not None


def test_get_users_me_no_auth(client):
    """Тестирование эндпоинта GET /api/users/me без аутентификации.

    Args:
        client (TestClient): тестовый клиент FastAPI.
    """
    response = client.get("/api/users/me")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_user_profile(client, api_keys):
    """Тестирование эндпоинта GET /api/users/{user_id}.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        api_keys (List[ApiKeyToUser]): Список тестовых api-key.
    """
    headers = get_api_key_headers(api_keys[0].api_key)
    response = client.get(
        "/api/users/{user_id}".format(user_id=api_keys[-1].user_id),
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    res_json = response.json()
    assert res_json.get("result")
    assert res_json.get("user") is not None


def test_get_non_existent_user_profile(client, api_keys):
    """Тестирование эндпоинта GET /api/users/{user_id}.

    Для несуществующего юзера.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        api_keys (List[ApiKeyToUser]): Список тестовых api-key.
    """
    headers = get_api_key_headers(api_keys[0].api_key)
    response = client.get("/api/users/9999", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    res_json = response.json()
    assert not res_json.get("result")


def test_post_tweet(client, api_keys):
    """Тестирование эндпоинта POST api/tweets.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        api_keys (List[ApiKeyToUser]): Список тестовых api-key.
    """
    payload = {
        "tweet_data": "test tweet",
        "tweet_media_ids": [],
    }
    headers = get_api_key_headers(api_keys[0].api_key)
    response = client.post("api/tweets", headers=headers, json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    res_json = response.json()
    assert res_json.get("result")
    assert isinstance(res_json.get("tweet_id"), int)


def test_post_tweet_without_auth(client):
    """Тестирование эндпоинта POST api/tweets без аутентификации.

    Args:
        client (TestClient): тестовый клиент FastAPI.
    """
    payload = {
        "tweet_data": "test tweet",
        "tweet_media_ids": [],
    }
    response = client.post("api/tweets", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_tweets(client, tweets_and_api_keys):
    """Тестирование эндпоинта GET api/tweets.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        tweets_and_api_keys (Dict[str, List[base]]): тестовые твиты и api-keys.
    """
    api_keys = tweets_and_api_keys["api_keys"]
    tweets = tweets_and_api_keys["tweets"]
    headers = get_api_key_headers(api_keys[0].api_key)
    response = client.get("/api/tweets", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    res_json = response.json()
    assert res_json.get("result")
    assert len(res_json.get("tweets")) == len(tweets)


def test_like_tweet(client, tweets_and_api_keys):
    """Тестирование эндпоинта POST api/tweets/{tweet_id}/likes.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        tweets_and_api_keys (Dict[str, List[base]]): тестовые твиты и api-keys.
    """
    api_keys = tweets_and_api_keys["api_keys"]
    tweets = tweets_and_api_keys["tweets"]
    headers = get_api_key_headers(api_keys[0].api_key)
    response = client.post(
        "api/tweets/{tweet_id}/likes".format(tweet_id=tweets[1].id),
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    res_json = response.json()
    assert res_json.get("result")


def test_like_self_own_tweet(client, tweets_and_api_keys):
    """Тестирование эндпоинта POST api/tweets/{tweet_id}likes.

    Для собственного твита.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        tweets_and_api_keys (Dict[str, List[base]]): тестовые твиты и api-keys.
    """
    api_keys = tweets_and_api_keys["api_keys"]
    tweets = tweets_and_api_keys["tweets"]
    headers = get_api_key_headers(api_keys[0].api_key)
    response = client.post(
        "api/tweets/{tweet_id}/likes".format(tweet_id=tweets[0].id),
        headers=headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    res_json = response.json()
    assert not res_json.get("result")


def test_like_tweet_non_existent_auth(client):
    """Тестирование эндпоинта POST api/tweets/{tweet_id}likes.

    С неверной аутентификацией.

    Args:
        client (TestClient): тестовый клиент FastAPI.
    """
    headers = get_api_key_headers("non_existent_api_key")
    response = client.post("api/tweets/2/likes", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    res_json = response.json()
    assert not res_json.get("result")


def test_like_non_existent_tweet(client, api_keys):
    """Тестирование эндпоинта POST api/tweets/{tweet_id}likes.

    Для несуществующего твита.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        api_keys (List[ApiKeyToUser]): Список тестовых api-key.
    """
    headers = get_api_key_headers(api_keys[0].api_key)
    response = client.post("api/tweets/9999/likes", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    res_json = response.json()
    assert not res_json.get("result")


def test_unlike_tweet(client, liked_tweets_and_api_keys):
    """Тестирование эндпоинта DELETE api/tweets/{tweet_id}/likes.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        liked_tweets_and_api_keys (Dict[str, List[base]]): твиты и api-keys.
    """
    api_keys = liked_tweets_and_api_keys["api_keys"]
    tweets = liked_tweets_and_api_keys["tweets"]
    headers = get_api_key_headers(api_keys[0].api_key)
    response = client.delete(
        "api/tweets/{tweet_id}/likes".format(tweet_id=tweets[-1].id),
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    res_json = response.json()
    assert res_json.get("result")


def test_unlike_self_own_tweet(client, liked_tweets_and_api_keys):
    """Тестирование эндпоинта DELETE api/tweets/{tweet_id}/likes.

    Для собственного твита.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        liked_tweets_and_api_keys (Dict[str, List[base]]): твиты и api-keys.
    """
    api_keys = liked_tweets_and_api_keys["api_keys"]
    tweets = liked_tweets_and_api_keys["tweets"]
    headers = get_api_key_headers(api_keys[0].api_key)
    response = client.delete(
        "api/tweets/{tweet_id}/likes".format(tweet_id=tweets[0].id),
        headers=headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    res_json = response.json()
    assert not res_json.get("result")


def test_unlike_tweet_non_existent_auth(client):
    """Тестирование эндпоинта DELETE api/tweets/{tweet_id}/likes.

    С неверной аутентификацией.

    Args:
        client (TestClient): тестовый клиент FastAPI.
    """
    headers = get_api_key_headers("non_existent_api_key")
    response = client.delete(
        "api/tweets/1/likes",
        headers=headers,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    res_json = response.json()
    assert not res_json.get("result")


def test_unlike_non_existent_tweet(client, api_keys):
    """Тестирование эндпоинта DELETE api/tweets/{tweet_id}/likes.

    Для несуществующего твита.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        api_keys (List[ApiKeyToUser]): Список тестовых api-key.
    """
    headers = get_api_key_headers(api_keys[0].api_key)
    response = client.delete("api/tweets/9999/likes", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    res_json = response.json()
    assert not res_json.get("result")


def test_delete_tweet_wrong_auth(client, tweets_and_api_keys):
    """Тестирование эндпоинта DELETE api/tweets/{tweet_id}.

    Для чужого твита.


    Args:
        client (TestClient): тестовый клиент FastAPI.
        tweets_and_api_keys (Dict[str, List[base]]): тестовые твиты и api-keys.
    """
    api_keys = tweets_and_api_keys["api_keys"]
    tweets = tweets_and_api_keys["tweets"]
    headers = get_api_key_headers(api_keys[0].api_key)
    response = client.delete(
        "api/tweets/{tweet_id}".format(tweet_id=tweets[1].id),
        headers=headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    res_json = response.json()
    assert not res_json.get("result")


def test_delete_tweet_non_existent_auth(client):
    """Тестирование эндпоинта DELETE api/tweets/{tweet_id}.

    С некорректной аутентификацией.

    Args:
        client (TestClient): тестовый клиент FastAPI.
    """
    headers = get_api_key_headers("non_existent_api_key")
    response = client.delete("api/tweets/1", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    res_json = response.json()
    assert not res_json.get("result")


def test_delete_non_existent_tweet(client, api_keys):
    """Тестирование эндпоинта DELETE api/tweets/{tweet_id}.

    Для несуществующего твита.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        api_keys (List[ApiKeyToUser]): Список тестовых api-key.
    """
    headers = get_api_key_headers(api_keys[0].api_key)
    response = client.delete("api/tweets/9999", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    res_json = response.json()
    assert not res_json.get("result")


def test_delete_tweet(client, tweets_and_api_keys):
    """Тестирование эндпоинта DELETE api/tweets/{tweet_id}.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        tweets_and_api_keys (Dict[str, List[base]]): тестовые твиты и api-keys.
    """
    api_keys = tweets_and_api_keys["api_keys"]
    tweets = tweets_and_api_keys["tweets"]
    headers = get_api_key_headers(api_keys[0].api_key)
    response = client.delete(
        "api/tweets/{tweet_id}".format(tweet_id=tweets[0].id),
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    res_json = response.json()
    assert res_json.get("result")


def test_follow_user(client, api_keys):
    """Тестирование эндпоинта DELETE /api/users/{user_id}/follow.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        api_keys (List[ApiKeyToUser]): Список тестовых api-key.
    """
    headers = get_api_key_headers(api_keys[0].api_key)
    response = client.delete(
        "/api/users/{user_id}/follow".format(user_id=api_keys[1].user_id),
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    res_json = response.json()
    assert res_json.get("result")


def test_follow_self(client, api_keys):
    """Тестирование эндпоинта DELETE /api/users/{user_id}/follow.

    Для самого себя.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        api_keys (List[ApiKeyToUser]): Список тестовых api-key.
    """
    headers = get_api_key_headers(api_keys[0].api_key)
    response = client.delete(
        "/api/users/{user_id}/follow".format(user_id=api_keys[0].user_id),
        headers=headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    res_json = response.json()
    assert not res_json.get("result")


def test_follow_user_without_auth(client):
    """Тестирование эндпоинта DELETE /api/users/{user_id}/follow.

    Без аутентификации.

    Args:
        client (TestClient): тестовый клиент FastAPI.
    """
    response = client.delete("/api/users/2/follow")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    res_json = response.json()
    assert not res_json.get("result")


def test_follow_user_non_existent_auth(client):
    """Тестирование эндпоинта DELETE /api/users/{user_id}/follow.

    С неверной аутентификацией.

    Args:
        client (TestClient): тестовый клиент FastAPI.
    """
    headers = get_api_key_headers("non_existent_api_key")
    response = client.delete("/api/users/2/follow", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    res_json = response.json()
    assert not res_json.get("result")


def test_follow_user_non_existent_user(client, api_keys):
    """Тестирование эндпоинта DELETE /api/users/{user_id}/follow.

    Для несуществующего пользователя.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        api_keys (List[ApiKeyToUser]): Список тестовых api-key.
    """
    headers = get_api_key_headers(api_keys[0].api_key)
    response = client.delete("/api/users/9999/follow", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    res_json = response.json()
    assert not res_json.get("result")


def test_unfollow_user(client, followed_users_api_keys):
    """Тестирование эндпоинта DELETE /api/tweets/{user_id}/follow.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        followed_users_api_keys (List[ApiKeyToUser]): Список тестовых api-key.
    """
    headers = get_api_key_headers(followed_users_api_keys[0].api_key)
    user_id = followed_users_api_keys[1].user_id
    response = client.delete(
        "/api/tweets/{user_id}/follow".format(user_id=user_id),
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    res_json = response.json()
    assert res_json.get("result")


def test_unfollow_self(client, followed_users_api_keys):
    """Тестирование эндпоинта DELETE /api/tweets/{user_id}/follow.

    Для самого себя.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        followed_users_api_keys (List[User]): тестовые api-keys.
    """
    headers = get_api_key_headers(followed_users_api_keys[0].api_key)
    user_id = followed_users_api_keys[0].user_id
    response = client.delete(
        "/api/tweets/{user_id}/follow".format(user_id=user_id),
        headers=headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    res_json = response.json()
    assert not res_json.get("result")


def test_unfollow_user_without_auth(client):
    """Тестирование эндпоинта DELETE /api/tweets/{user_id}/follow.

    Без аутентификации.

    Args:
        client (TestClient): тестовый клиент FastAPI.
    """
    response = client.delete("/api/tweets/2/follow")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    res_json = response.json()
    assert not res_json.get("result")


def test_unfollow_user_non_existent_auth(client):
    """Тестирование эндпоинта DELETE /api/tweets/{user_id}/follow.

    С некорректной аутентификацией.

    Args:
        client (TestClient): тестовый клиент FastAPI.
    """
    headers = get_api_key_headers("non_existent_api_key")
    response = client.delete("/api/tweets/2/follow", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    res_json = response.json()
    assert not res_json.get("result")


def test_unfollow_user_non_existent_user(client, followed_users_api_keys):
    """Тестирование эндпоинта DELETE /api/tweets/{user_id}/follow.

    Для несуществующего пользователя.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        followed_users_api_keys (List[User]): тестовые api-keys.
    """
    headers = get_api_key_headers(followed_users_api_keys[0].api_key)
    response = client.delete("/api/tweets/9999/follow", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    res_json = response.json()
    assert not res_json.get("result")


def test_upload_media(client, api_keys):
    """Тестирование эндпоинта POST /api/medias.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        api_keys (List[ApiKeyToUser]): Список тестовых api-key.
    """
    headers = get_api_key_headers(api_keys[0].api_key)
    test_bytes = b"test_bytes"
    files = {"file": ("filename", test_bytes, "image/jpeg")}
    response = client.post("/api/medias", headers=headers, files=files)
    assert response.status_code == status.HTTP_201_CREATED
    res_json = response.json()
    assert res_json.get("result")
    assert isinstance(res_json.get("media_id"), int)


def test_get_media(client, media):
    """Тестирование эндпоинта GET /api/medias{media_id}.

    Args:
        client (TestClient): тестовый клиент FastAPI.
        media (Media): тестовое медиа.
    """

    response = client.get(
        "/api/medias/{media_id}".format(media_id=media.id),
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.content == media.media_data

"""ORM модели для базы данных."""
from sqlalchemy import ARRAY, Column, ForeignKey, Integer, LargeBinary, Sequence, String
from sqlalchemy.orm import relationship

from not_twitter.app.database.database import Base


class Following(Base):
    """Представление подписки одного пользователя на другого."""

    __tablename__ = "followings"
    followed_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    follower_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )


class User(Base):
    """Представление пользователя."""

    __tablename__ = "users"
    id = Column(
        Integer,
        Sequence("user_id_seq"),
        primary_key=True,
    )
    name = Column(
        String(50),
        nullable=False,
    )

    following = relationship(
        "User",
        secondary="followings",
        primaryjoin=id == Following.follower_id,
        secondaryjoin=id == Following.followed_id,
        backref="followers",
        lazy="selectin",
    )

    api_key = relationship(
        "ApiKeyToUser",
        back_populates="user",
        lazy="noload",
        cascade="all, delete-orphan",
    )
    tweets = relationship(
        "Tweet",
        back_populates="author",
        lazy="joined",
        cascade="all, delete-orphan",
    )


class ApiKeyToUser(Base):
    """Представление связи пользователя и Api-key."""

    __tablename__ = "users_by_keys"
    api_key = Column(
        String(100),
        primary_key=True,
        index=True,
        nullable=False,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    user = relationship(
        "User",
        back_populates="api_key",
        lazy="selectin",
    )


class Tweet(Base):
    """Представление твита."""

    __tablename__ = "tweets"
    id = Column(
        Integer,
        Sequence("tweet_id_seq"),
        primary_key=True,
    )
    content = Column(
        String,
        nullable=False,
    )
    author_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    author = relationship(
        "User",
        back_populates="tweets",
        lazy="selectin",
        passive_deletes=True,
    )
    likes = relationship(
        "Like",
        back_populates="tweet",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    attachments = Column(
        ARRAY(String),
        nullable=True,
    )


class Like(Base):
    """Представление лайка."""

    __tablename__ = "likes"
    tweet_id = Column(
        Integer,
        ForeignKey("tweets.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    name = Column(
        String,
        nullable=False,
    )
    tweet = relationship(
        "Tweet",
        back_populates="likes",
        passive_deletes=True,
    )


class Media(Base):
    """Представление медиа из твита."""

    __tablename__ = "medias"
    id = Column(
        Integer,
        Sequence("media_id_seq"),
        primary_key=True,
    )
    media_data = Column(
        LargeBinary,
        nullable=False,
    )
    tweet_id = Column(
        Integer,
        ForeignKey("tweets.id", ondelete="CASCADE"),
    )

import uuid
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, String, Integer, Boolean,
    DateTime, ForeignKey, Enum as SAEnum, Text
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
from pydantic_settings import BaseSettings
import enum


class Settings(BaseSettings):
    database_url: str
    secret_key: str = "dev-secret"
    apns_team_id: str = ""
    apns_key_id: str = ""
    apns_auth_key: str = ""
    apns_bundle_id: str = "com.yourname.instagramtracker"
    environment: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ChangeType(str, enum.Enum):
    new_follower = "new_follower"
    lost_follower = "lost_follower"
    new_following = "new_following"
    lost_following = "lost_following"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tracked_accounts = relationship("TrackedAccount", back_populates="user")


class TrackedAccount(Base):
    __tablename__ = "tracked_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    instagram_username = Column(String, nullable=False)
    check_interval_minutes = Column(Integer, default=360)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="tracked_accounts")
    snapshots = relationship("AccountSnapshot", back_populates="tracked_account", order_by="AccountSnapshot.snapshotted_at.desc()")
    changes = relationship("FollowerChange", back_populates="tracked_account")
    notifications = relationship("NotificationLog", back_populates="tracked_account")


class AccountSnapshot(Base):
    __tablename__ = "account_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tracked_account_id = Column(UUID(as_uuid=True), ForeignKey("tracked_accounts.id"), nullable=False)
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    is_private = Column(Boolean, default=False)
    full_name = Column(String, nullable=True)
    biography = Column(Text, nullable=True)
    external_url = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    profile_pic_url = Column(String, nullable=True)
    snapshotted_at = Column(DateTime, default=datetime.utcnow)

    tracked_account = relationship("TrackedAccount", back_populates="snapshots")


class FollowerChange(Base):
    __tablename__ = "follower_changes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tracked_account_id = Column(UUID(as_uuid=True), ForeignKey("tracked_accounts.id"), nullable=False)
    change_type = Column(SAEnum(ChangeType), nullable=False)
    username = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    profile_pic_url = Column(String, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow)

    tracked_account = relationship("TrackedAccount", back_populates="changes")


class NotificationLog(Base):
    __tablename__ = "notifications_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tracked_account_id = Column(UUID(as_uuid=True), ForeignKey("tracked_accounts.id"), nullable=False)
    notification_type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    was_delivered = Column(Boolean, default=False)

    tracked_account = relationship("TrackedAccount", back_populates="notifications")


def create_tables():
    Base.metadata.create_all(bind=engine)

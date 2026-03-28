from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class ChangeType(str, Enum):
    new_follower = "new_follower"
    lost_follower = "lost_follower"
    new_following = "new_following"
    lost_following = "lost_following"


# ── User ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    device_token: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    device_token: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Device ────────────────────────────────────────────────────────────────────

class DeviceRegister(BaseModel):
    user_id: str
    device_token: str


# ── Tracked Account ───────────────────────────────────────────────────────────

class TrackedAccountCreate(BaseModel):
    instagram_username: str
    check_interval_minutes: int = Field(default=360, ge=5, le=1440)
    user_id: str


class TrackedAccountUpdate(BaseModel):
    check_interval_minutes: Optional[int] = Field(default=None, ge=5, le=1440)
    is_active: Optional[bool] = None


class TrackedAccountResponse(BaseModel):
    id: str
    user_id: str
    instagram_username: str
    check_interval_minutes: int
    is_active: bool
    created_at: datetime
    latest_snapshot: Optional["AccountSnapshotResponse"] = None

    class Config:
        from_attributes = True


# ── Account Snapshot ──────────────────────────────────────────────────────────

class AccountSnapshotResponse(BaseModel):
    id: str
    tracked_account_id: str
    followers_count: int
    following_count: int
    posts_count: int
    is_private: bool
    full_name: Optional[str]
    biography: Optional[str]
    external_url: Optional[str]
    is_verified: bool
    profile_pic_url: Optional[str]
    snapshotted_at: datetime

    class Config:
        from_attributes = True


TrackedAccountResponse.model_rebuild()


# ── Follower Change ───────────────────────────────────────────────────────────

class FollowerChangeResponse(BaseModel):
    id: str
    tracked_account_id: str
    change_type: ChangeType
    username: str
    full_name: Optional[str]
    profile_pic_url: Optional[str]
    detected_at: datetime

    class Config:
        from_attributes = True


# ── Notification Log ──────────────────────────────────────────────────────────

class NotificationLogResponse(BaseModel):
    id: str
    tracked_account_id: str
    notification_type: str
    message: str
    sent_at: datetime
    was_delivered: bool

    class Config:
        from_attributes = True


# ── History ───────────────────────────────────────────────────────────────────

class HistoryEntry(BaseModel):
    notification: NotificationLogResponse
    account_username: str


# ── Paginated Response ────────────────────────────────────────────────────────

class PaginatedHistory(BaseModel):
    items: List[HistoryEntry]
    total: int
    page: int
    per_page: int
    has_more: bool

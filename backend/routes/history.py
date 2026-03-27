import uuid
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session

from database import get_db, TrackedAccount, NotificationLog, User
from models import NotificationLogResponse, HistoryEntry, PaginatedHistory

router = APIRouter(prefix="/api/history", tags=["history"])


def _get_or_create_user(user_id: str, db: Session) -> User:
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz user_id formatı")
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        user = User(id=uid)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.get("", response_model=PaginatedHistory)
def get_all_history(
    x_user_id: str = Header(..., alias="X-User-ID"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    user = _get_or_create_user(x_user_id, db)

    # Kullanıcıya ait tüm hesapların ID'leri
    account_ids = [
        a.id for a in db.query(TrackedAccount).filter(
            TrackedAccount.user_id == user.id
        ).all()
    ]
    if not account_ids:
        return PaginatedHistory(items=[], total=0, page=page, per_page=per_page, has_more=False)

    total = (
        db.query(NotificationLog)
        .filter(NotificationLog.tracked_account_id.in_(account_ids))
        .count()
    )

    logs = (
        db.query(NotificationLog)
        .filter(NotificationLog.tracked_account_id.in_(account_ids))
        .order_by(NotificationLog.sent_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    # account_id → username map
    accounts = db.query(TrackedAccount).filter(
        TrackedAccount.id.in_(account_ids)
    ).all()
    username_map = {str(a.id): a.instagram_username for a in accounts}

    items = [
        HistoryEntry(
            notification=NotificationLogResponse(
                id=str(log.id),
                tracked_account_id=str(log.tracked_account_id),
                notification_type=log.notification_type,
                message=log.message,
                sent_at=log.sent_at,
                was_delivered=log.was_delivered,
            ),
            account_username=username_map.get(str(log.tracked_account_id), ""),
        )
        for log in logs
    ]

    return PaginatedHistory(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        has_more=(page * per_page) < total,
    )


@router.get("/{account_id}", response_model=PaginatedHistory)
def get_account_history(
    account_id: str,
    x_user_id: str = Header(..., alias="X-User-ID"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    user = _get_or_create_user(x_user_id, db)
    try:
        aid = uuid.UUID(account_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz account_id")

    account = db.query(TrackedAccount).filter(
        TrackedAccount.id == aid,
        TrackedAccount.user_id == user.id,
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Hesap bulunamadı")

    total = (
        db.query(NotificationLog)
        .filter(NotificationLog.tracked_account_id == aid)
        .count()
    )

    logs = (
        db.query(NotificationLog)
        .filter(NotificationLog.tracked_account_id == aid)
        .order_by(NotificationLog.sent_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    items = [
        HistoryEntry(
            notification=NotificationLogResponse(
                id=str(log.id),
                tracked_account_id=str(log.tracked_account_id),
                notification_type=log.notification_type,
                message=log.message,
                sent_at=log.sent_at,
                was_delivered=log.was_delivered,
            ),
            account_username=account.instagram_username,
        )
        for log in logs
    ]

    return PaginatedHistory(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        has_more=(page * per_page) < total,
    )

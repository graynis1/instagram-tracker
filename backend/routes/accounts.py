import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db, TrackedAccount, User, AccountSnapshot
from models import (
    TrackedAccountCreate, TrackedAccountUpdate,
    TrackedAccountResponse, AccountSnapshotResponse
)
from scheduler import get_scheduler

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


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


def _serialize_account(acc: TrackedAccount) -> TrackedAccountResponse:
    latest = None
    if acc.snapshots:
        s = acc.snapshots[0]
        latest = AccountSnapshotResponse(
            id=str(s.id),
            tracked_account_id=str(s.tracked_account_id),
            followers_count=s.followers_count,
            following_count=s.following_count,
            posts_count=s.posts_count,
            is_private=s.is_private,
            full_name=s.full_name,
            biography=s.biography,
            external_url=s.external_url,
            is_verified=s.is_verified,
            profile_pic_url=s.profile_pic_url,
            snapshotted_at=s.snapshotted_at,
        )
    return TrackedAccountResponse(
        id=str(acc.id),
        user_id=str(acc.user_id),
        instagram_username=acc.instagram_username,
        check_interval_minutes=acc.check_interval_minutes,
        is_active=acc.is_active,
        created_at=acc.created_at,
        latest_snapshot=latest,
    )


@router.get("", response_model=list[TrackedAccountResponse])
def list_accounts(
    x_user_id: str = Header(..., alias="X-User-ID"),
    db: Session = Depends(get_db),
):
    user = _get_or_create_user(x_user_id, db)
    accounts = (
        db.query(TrackedAccount)
        .filter(TrackedAccount.user_id == user.id)
        .order_by(TrackedAccount.created_at.desc())
        .all()
    )
    return [_serialize_account(a) for a in accounts]


@router.post("", response_model=TrackedAccountResponse, status_code=201)
def add_account(
    body: TrackedAccountCreate,
    x_user_id: str = Header(..., alias="X-User-ID"),
    db: Session = Depends(get_db),
):
    user = _get_or_create_user(x_user_id, db)

    # Aynı kullanıcı aynı hesabı tekrar ekleyemesin
    existing = db.query(TrackedAccount).filter(
        TrackedAccount.user_id == user.id,
        TrackedAccount.instagram_username == body.instagram_username.lower().strip(),
        TrackedAccount.is_active == True,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Bu hesap zaten takip listende")

    account = TrackedAccount(
        user_id=user.id,
        instagram_username=body.instagram_username.lower().strip(),
        check_interval_minutes=body.check_interval_minutes,
    )
    db.add(account)
    db.commit()
    db.refresh(account)

    # Scheduler'a ekle
    get_scheduler().add_job(str(account.id), account.check_interval_minutes)

    # İlk snapshot'ı arka planda al
    import threading
    t = threading.Thread(
        target=get_scheduler().check_account_now,
        args=(str(account.id),),
        daemon=True,
    )
    t.start()

    return _serialize_account(account)


@router.delete("/{account_id}", status_code=204)
def delete_account(
    account_id: str,
    x_user_id: str = Header(..., alias="X-User-ID"),
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

    get_scheduler().remove_job(account_id)
    account.is_active = False
    db.commit()


@router.patch("/{account_id}", response_model=TrackedAccountResponse)
def update_account(
    account_id: str,
    body: TrackedAccountUpdate,
    x_user_id: str = Header(..., alias="X-User-ID"),
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

    if body.check_interval_minutes is not None:
        account.check_interval_minutes = body.check_interval_minutes
        get_scheduler().add_job(account_id, body.check_interval_minutes)

    if body.is_active is not None:
        account.is_active = body.is_active
        if body.is_active:
            get_scheduler().add_job(account_id, account.check_interval_minutes)
        else:
            get_scheduler().remove_job(account_id)

    db.commit()
    db.refresh(account)
    return _serialize_account(account)


@router.get("/{account_id}/snapshot", response_model=AccountSnapshotResponse)
def get_snapshot(
    account_id: str,
    x_user_id: str = Header(..., alias="X-User-ID"),
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

    snapshot = (
        db.query(AccountSnapshot)
        .filter(AccountSnapshot.tracked_account_id == aid)
        .order_by(AccountSnapshot.snapshotted_at.desc())
        .first()
    )
    if not snapshot:
        raise HTTPException(status_code=404, detail="Henüz snapshot yok")

    return AccountSnapshotResponse(
        id=str(snapshot.id),
        tracked_account_id=str(snapshot.tracked_account_id),
        followers_count=snapshot.followers_count,
        following_count=snapshot.following_count,
        posts_count=snapshot.posts_count,
        is_private=snapshot.is_private,
        full_name=snapshot.full_name,
        biography=snapshot.biography,
        external_url=snapshot.external_url,
        is_verified=snapshot.is_verified,
        profile_pic_url=snapshot.profile_pic_url,
        snapshotted_at=snapshot.snapshotted_at,
    )


@router.post("/{account_id}/check-now", status_code=200)
def check_now(
    account_id: str,
    x_user_id: str = Header(..., alias="X-User-ID"),
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

    # Senkron çalıştır — sonucu ve hatayı doğrudan döndür
    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(get_scheduler().check_account_now, account_id)
        try:
            result = future.result(timeout=60)
        except FuturesTimeout:
            return {"ok": False, "error": "timeout", "details": "60 saniye içinde tamamlanamadı"}
        except Exception as e:
            return {"ok": False, "error": "exception", "details": str(e)}

    return result

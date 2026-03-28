import logging
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio

from database import SessionLocal, TrackedAccount, AccountSnapshot, FollowerChange
from scraper import InstagramScraper
from notifications import NotificationService

logger = logging.getLogger(__name__)

# Her hesap için son kontrol zamanı — aynı hesabı interval'den önce yeniden tarama
_last_checked: dict[str, datetime] = {}
# Her hesap için ayarlı interval (dakika) — rate limit hesabında kullanılır
_account_intervals: dict[str, int] = {}

scraper = InstagramScraper()
notifier = NotificationService()


def _can_check(account_id: str) -> bool:
    last = _last_checked.get(account_id)
    if last is None:
        return True
    interval_minutes = _account_intervals.get(account_id, 360)
    # En az 4 dakika, en fazla interval süresi kadar bekle
    cooldown = max(4, interval_minutes - 1)
    return datetime.utcnow() - last >= timedelta(minutes=cooldown)


def check_account(tracked_account_id: str):
    """Bir hesabı kontrol et, değişiklikleri kaydet ve bildirim gönder."""
    if not _can_check(tracked_account_id):
        logger.debug(f"Hesap {tracked_account_id} henüz 30 dakika geçmedi, atlanıyor")
        return

    _last_checked[tracked_account_id] = datetime.utcnow()
    db = SessionLocal()

    try:
        account = db.query(TrackedAccount).filter(
            TrackedAccount.id == tracked_account_id,
            TrackedAccount.is_active == True
        ).first()

        if not account:
            logger.warning(f"Hesap {tracked_account_id} bulunamadı veya pasif")
            return

        username = account.instagram_username
        logger.info(f"@{username} kontrol ediliyor...")

        # Profil istatistiklerini al
        stats = scraper.get_profile_stats(username)
        if "error" in stats:
            logger.warning(f"@{username} scrape hatası: {stats}")
            return

        # Önceki snapshot
        old_snapshot: Optional[AccountSnapshot] = (
            db.query(AccountSnapshot)
            .filter(AccountSnapshot.tracked_account_id == tracked_account_id)
            .order_by(AccountSnapshot.snapshotted_at.desc())
            .first()
        )

        # Yeni snapshot oluştur
        new_snapshot = AccountSnapshot(
            tracked_account_id=tracked_account_id,
            followers_count=stats["followers_count"],
            following_count=stats["following_count"],
            posts_count=stats["posts_count"],
            is_private=stats["is_private"],
            full_name=stats.get("full_name", ""),
            biography=stats.get("biography", ""),
            external_url=stats.get("external_url", ""),
            is_verified=stats.get("is_verified", False),
            profile_pic_url=stats.get("profile_pic_url", ""),
        )
        db.add(new_snapshot)
        db.flush()

        follower_changes = []

        # Herkese açık hesaplarda takipçi/takip listesi karşılaştırması
        if not stats["is_private"] and old_snapshot:
            _detect_follower_changes(
                db, account, old_snapshot, username, follower_changes
            )

        db.commit()

        # Bildirimleri gönder (async çalıştır)
        # Account'u user ilişkisiyle taze çek
        account_with_user = db.query(TrackedAccount).filter(
            TrackedAccount.id == tracked_account_id
        ).first()

        if account_with_user:
            asyncio.run(notifier.notify_changes(
                account_with_user,
                old_snapshot,
                new_snapshot,
                follower_changes,
            ))

        logger.info(f"@{username} kontrol tamamlandı")

    except Exception as e:
        db.rollback()
        logger.error(f"check_account hatası {tracked_account_id}: {e}", exc_info=True)
    finally:
        db.close()


def _detect_follower_changes(db, account, old_snapshot, username: str, changes_out: list):
    """Takipçi ve takip listelerindeki değişiklikleri tespit et."""
    try:
        # Eski kayıtlı takipçiler
        old_followers_db = db.query(FollowerChange).filter(
            FollowerChange.tracked_account_id == account.id,
            FollowerChange.change_type.in_(["new_follower"]),
        ).all()
        old_follower_set = {c.username for c in old_followers_db}

        # Yeni takipçi listesini al
        current_followers = scraper.get_followers_list(username)
        if not current_followers:
            return

        current_follower_set = {f["username"] for f in current_followers}
        follower_map = {f["username"]: f for f in current_followers}

        # Yeni takipçiler
        new_followers = current_follower_set - old_follower_set
        for uname in list(new_followers)[:50]:  # max 50
            f = follower_map.get(uname, {})
            change = FollowerChange(
                tracked_account_id=account.id,
                change_type="new_follower",
                username=uname,
                full_name=f.get("full_name", ""),
                profile_pic_url=f.get("profile_pic_url", ""),
            )
            db.add(change)
            changes_out.append({
                "change_type": "new_follower",
                "username": uname,
                "full_name": f.get("full_name", ""),
            })

        # Kaybedilen takipçiler
        lost_followers = old_follower_set - current_follower_set
        for uname in list(lost_followers)[:50]:
            change = FollowerChange(
                tracked_account_id=account.id,
                change_type="lost_follower",
                username=uname,
                full_name="",
                profile_pic_url="",
            )
            db.add(change)

        # Takip listesi
        old_following_db = db.query(FollowerChange).filter(
            FollowerChange.tracked_account_id == account.id,
            FollowerChange.change_type.in_(["new_following"]),
        ).all()
        old_following_set = {c.username for c in old_following_db}

        current_following = scraper.get_following_list(username)
        if not current_following:
            return

        current_following_set = {f["username"] for f in current_following}
        following_map = {f["username"]: f for f in current_following}

        new_following = current_following_set - old_following_set
        for uname in list(new_following)[:50]:
            f = following_map.get(uname, {})
            change = FollowerChange(
                tracked_account_id=account.id,
                change_type="new_following",
                username=uname,
                full_name=f.get("full_name", ""),
                profile_pic_url=f.get("profile_pic_url", ""),
            )
            db.add(change)
            changes_out.append({
                "change_type": "new_following",
                "username": uname,
                "full_name": f.get("full_name", ""),
            })

        lost_following = old_following_set - current_following_set
        for uname in list(lost_following)[:50]:
            change = FollowerChange(
                tracked_account_id=account.id,
                change_type="lost_following",
                username=uname,
                full_name="",
                profile_pic_url="",
            )
            db.add(change)

    except Exception as e:
        logger.error(f"Takipçi değişim tespiti hatası {username}: {e}")


class AccountScheduler:
    def __init__(self):
        self._scheduler = BackgroundScheduler(
            job_defaults={"coalesce": True, "max_instances": 1, "misfire_grace_time": 300}
        )

    def start(self):
        """Tüm aktif hesaplar için job ekle ve scheduler'ı başlat."""
        db = SessionLocal()
        try:
            accounts = db.query(TrackedAccount).filter(
                TrackedAccount.is_active == True
            ).all()
            for acc in accounts:
                self._add_job_internal(str(acc.id), acc.check_interval_minutes)
            logger.info(f"{len(accounts)} hesap için scheduler başlatıldı")
        finally:
            db.close()

        self._scheduler.start()

    def stop(self):
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)

    def _add_job_internal(self, tracked_account_id: str, interval_minutes: int):
        _account_intervals[tracked_account_id] = interval_minutes
        job_id = f"account_{tracked_account_id}"
        if self._scheduler.get_job(job_id):
            self._scheduler.remove_job(job_id)
        self._scheduler.add_job(
            func=check_account,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id=job_id,
            args=[tracked_account_id],
            replace_existing=True,
        )
        logger.debug(f"Job eklendi: {job_id}, her {interval_minutes} dakikada bir")

    def add_job(self, tracked_account_id: str, interval_minutes: int):
        self._add_job_internal(tracked_account_id, interval_minutes)

    def remove_job(self, tracked_account_id: str):
        job_id = f"account_{tracked_account_id}"
        if self._scheduler.get_job(job_id):
            self._scheduler.remove_job(job_id)
            logger.debug(f"Job kaldırıldı: {job_id}")

    def check_account_now(self, tracked_account_id: str):
        """Manuel anlık kontrol — rate limit bypass."""
        _last_checked.pop(tracked_account_id, None)
        check_account(tracked_account_id)


_scheduler_instance: Optional[AccountScheduler] = None


def get_scheduler() -> AccountScheduler:
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = AccountScheduler()
    return _scheduler_instance

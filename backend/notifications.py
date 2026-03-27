import time
import json
import logging
import httpx
from datetime import datetime, timezone
from typing import Optional
from database import settings, SessionLocal, NotificationLog, TrackedAccount, AccountSnapshot

logger = logging.getLogger(__name__)

APNS_HOST_PROD = "https://api.push.apple.com"
APNS_HOST_DEV  = "https://api.sandbox.push.apple.com"


def _format_count(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


class NotificationService:
    def __init__(self):
        self._token_cache: Optional[str] = None
        self._token_exp: float = 0.0

    def _get_apns_host(self) -> str:
        return APNS_HOST_PROD if settings.environment == "production" else APNS_HOST_DEV

    def _build_jwt(self) -> str:
        """APNs için JWT token oluşturur (ES256)."""
        from jose import jwt as jose_jwt
        now = int(time.time())
        if self._token_cache and self._token_exp > now + 60:
            return self._token_cache

        payload = {
            "iss": settings.apns_team_id,
            "iat": now,
        }
        key = settings.apns_auth_key.replace("\\n", "\n")
        token = jose_jwt.encode(
            payload,
            key,
            algorithm="ES256",
            headers={"kid": settings.apns_key_id},
        )
        self._token_cache = token
        self._token_exp = now + 3600
        return token

    async def send_push(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[dict] = None,
    ) -> bool:
        if not device_token or not settings.apns_team_id:
            logger.debug("APNs yapılandırılmamış, bildirim atlandı")
            return False

        payload = {
            "aps": {
                "alert": {"title": title, "body": body},
                "sound": "default",
                "badge": 1,
            }
        }
        if data:
            payload.update(data)

        host = self._get_apns_host()
        url = f"{host}/3/device/{device_token}"
        headers = {
            "authorization": f"bearer {self._build_jwt()}",
            "apns-topic": settings.apns_bundle_id,
            "apns-push-type": "alert",
            "apns-priority": "10",
            "content-type": "application/json",
        }

        try:
            async with httpx.AsyncClient(http2=True, timeout=10) as client:
                resp = await client.post(url, headers=headers, content=json.dumps(payload))
            if resp.status_code == 200:
                return True
            logger.warning(f"APNs hata {resp.status_code}: {resp.text}")
            return False
        except Exception as e:
            logger.error(f"APNs isteği başarısız: {e}")
            return False

    async def notify_changes(
        self,
        tracked_account,
        old_snapshot: Optional[AccountSnapshot],
        new_snapshot: AccountSnapshot,
        follower_changes: list,
    ):
        if not tracked_account.user or not tracked_account.user.device_token:
            return

        device_token = tracked_account.user.device_token
        username = tracked_account.instagram_username
        messages = []

        if old_snapshot:
            # ── Takipçi değişimi ────────────────────────────────────────
            diff_followers = new_snapshot.followers_count - old_snapshot.followers_count
            if diff_followers > 0:
                old_f = _format_count(old_snapshot.followers_count)
                new_f = _format_count(new_snapshot.followers_count)
                messages.append((
                    "follower_gain",
                    f"📈 @{username} {diff_followers} yeni takipçi kazandı ({old_f} → {new_f})",
                ))
            elif diff_followers < 0:
                messages.append((
                    "follower_loss",
                    f"📉 @{username} {abs(diff_followers)} takipçi kaybetti",
                ))

            # ── Takip değişimi ───────────────────────────────────────────
            diff_following = new_snapshot.following_count - old_snapshot.following_count
            if diff_following > 0:
                messages.append((
                    "following_gain",
                    f"➕ @{username} {diff_following} yeni hesabı takip etmeye başladı",
                ))
            elif diff_following < 0:
                messages.append((
                    "following_loss",
                    f"➖ @{username} {abs(diff_following)} hesabı takipten çıkardı",
                ))

            # ── Gönderi değişimi ─────────────────────────────────────────
            diff_posts = new_snapshot.posts_count - old_snapshot.posts_count
            if diff_posts > 0:
                messages.append((
                    "new_post",
                    f"📸 @{username} yeni gönderi paylaştı (toplam: {new_snapshot.posts_count})",
                ))

            # ── Gizlilik değişimi ────────────────────────────────────────
            if not old_snapshot.is_private and new_snapshot.is_private:
                messages.append(("went_private", f"🔒 @{username} hesabını gizledi"))
            elif old_snapshot.is_private and not new_snapshot.is_private:
                messages.append(("went_public", f"🔓 @{username} hesabını herkese açtı"))

            # ── Biyografi değişimi ───────────────────────────────────────
            if old_snapshot.biography != new_snapshot.biography:
                messages.append(("bio_change", f"✏️ @{username} biyografisini değiştirdi"))

        # ── Bireysel takipçi değişiklikleri ──────────────────────────────
        for change in follower_changes:
            if change["change_type"] == "new_following":
                messages.append((
                    "new_following_person",
                    f"👤 @{username}, @{change['username']} kişisini takip etmeye başladı",
                ))

        # ── Bildirimleri gönder ve kaydet ─────────────────────────────────
        db = SessionLocal()
        try:
            for notif_type, msg in messages:
                delivered = await self.send_push(
                    device_token=device_token,
                    title="Instagram Takip",
                    body=msg,
                    data={"account_id": str(tracked_account.id), "type": notif_type},
                )
                log = NotificationLog(
                    tracked_account_id=tracked_account.id,
                    notification_type=notif_type,
                    message=msg,
                    was_delivered=delivered,
                )
                db.add(log)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Bildirim kaydedilirken hata: {e}")
        finally:
            db.close()

import time
import random
import logging
from typing import Optional
import instaloader

logger = logging.getLogger(__name__)

# Son istek zamanlarını takip et
_last_request_time: float = 0.0


def _rate_limit_wait():
    global _last_request_time
    elapsed = time.time() - _last_request_time
    wait = random.uniform(3, 8)
    if elapsed < wait:
        time.sleep(wait - elapsed)
    _last_request_time = time.time()


class InstagramScraper:
    def __init__(self):
        self._loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            quiet=True,
        )

    def _new_loader(self) -> instaloader.Instaloader:
        return instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            quiet=True,
        )

    def get_profile_stats(self, username: str) -> dict:
        """
        Profil istatistiklerini döndürür.
        Hata durumunda {"error": "..."} döner, exception fırlatmaz.
        """
        _rate_limit_wait()
        try:
            loader = self._new_loader()
            profile = instaloader.Profile.from_username(loader.context, username)
            return {
                "followers_count": profile.followers,
                "following_count": profile.followees,
                "posts_count": profile.mediacount,
                "is_private": profile.is_private,
                "full_name": profile.full_name or "",
                "biography": profile.biography or "",
                "external_url": profile.external_url or "",
                "is_verified": profile.is_verified,
                "profile_pic_url": profile.profile_pic_url or "",
            }
        except instaloader.exceptions.ProfileNotExistsException:
            logger.warning(f"Profil bulunamadı: {username}")
            return {"error": "profile_not_found", "username": username}
        except instaloader.exceptions.ConnectionException as e:
            msg = str(e).lower()
            if "429" in msg or "rate" in msg or "too many" in msg:
                logger.warning(f"Rate limit hit for {username}, 30 dakika bekleniyor")
                time.sleep(1800)
                return {"error": "rate_limited", "username": username}
            logger.error(f"Bağlantı hatası {username}: {e}")
            return {"error": "connection_error", "details": str(e)}
        except Exception as e:
            logger.error(f"Beklenmedik hata {username}: {e}")
            return {"error": "unknown_error", "details": str(e)}

    def get_followers_list(self, username: str) -> list[dict]:
        """
        Takipçi listesini döndürür.
        Private hesapta veya hata durumunda boş liste döner.
        """
        _rate_limit_wait()
        try:
            loader = self._new_loader()
            profile = instaloader.Profile.from_username(loader.context, username)
            if profile.is_private:
                return []
            result = []
            for follower in profile.get_followers():
                _rate_limit_wait()
                result.append({
                    "username": follower.username,
                    "full_name": follower.full_name or "",
                    "profile_pic_url": follower.profile_pic_url or "",
                })
            return result
        except instaloader.exceptions.LoginRequiredException:
            logger.info(f"{username} takipçi listesi için login gerekiyor")
            return []
        except instaloader.exceptions.ConnectionException as e:
            msg = str(e).lower()
            if "429" in msg or "rate" in msg or "too many" in msg:
                logger.warning(f"Rate limit (followers) {username}")
                time.sleep(1800)
            return []
        except Exception as e:
            logger.error(f"Takipçi listesi hatası {username}: {e}")
            return []

    def get_following_list(self, username: str) -> list[dict]:
        """
        Takip edilen listesini döndürür.
        Private hesapta veya hata durumunda boş liste döner.
        """
        _rate_limit_wait()
        try:
            loader = self._new_loader()
            profile = instaloader.Profile.from_username(loader.context, username)
            if profile.is_private:
                return []
            result = []
            for followee in profile.get_followees():
                _rate_limit_wait()
                result.append({
                    "username": followee.username,
                    "full_name": followee.full_name or "",
                    "profile_pic_url": followee.profile_pic_url or "",
                })
            return result
        except instaloader.exceptions.LoginRequiredException:
            logger.info(f"{username} takip listesi için login gerekiyor")
            return []
        except instaloader.exceptions.ConnectionException as e:
            msg = str(e).lower()
            if "429" in msg or "rate" in msg or "too many" in msg:
                logger.warning(f"Rate limit (following) {username}")
                time.sleep(1800)
            return []
        except Exception as e:
            logger.error(f"Takip listesi hatası {username}: {e}")
            return []

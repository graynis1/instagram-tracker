import httpx
import logging
import random
import time

logger = logging.getLogger(__name__)

_last_request_time: float = 0.0


def _rate_limit_wait():
    global _last_request_time
    elapsed = time.time() - _last_request_time
    wait = random.uniform(1, 3)
    if elapsed < wait:
        time.sleep(wait - elapsed)
    _last_request_time = time.time()


class InstagramScraper:
    _HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.0 Mobile/15E148 Safari/604.1"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "X-IG-App-ID": "936619743392459",
        "Connection": "keep-alive",
    }

    def get_profile_stats(self, username: str) -> dict:
        _rate_limit_wait()
        url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
        try:
            with httpx.Client(timeout=12.0, follow_redirects=True) as client:
                r = client.get(url, headers=self._HEADERS)

            if r.status_code == 404:
                return {"error": "profile_not_found", "details": f"@{username} profili bulunamadı"}
            if r.status_code == 429:
                return {"error": "rate_limited", "details": "Instagram istek limiti aşıldı, lütfen bekleyin"}
            if r.status_code in (401, 403):
                return {
                    "error": "blocked",
                    "details": "Instagram bu sunucudan gelen istekleri reddetti (401/403)",
                }
            if r.status_code != 200:
                return {"error": "http_error", "details": f"Instagram HTTP {r.status_code}"}

            data = r.json()
            user = data.get("data", {}).get("user")
            if not user:
                return {"error": "user_not_found", "details": f"@{username} JSON'da bulunamadı"}

            return {
                "followers_count": user.get("edge_followed_by", {}).get("count", 0),
                "following_count": user.get("edge_follow", {}).get("count", 0),
                "posts_count": user.get("edge_owner_to_timeline_media", {}).get("count", 0),
                "is_private": user.get("is_private", False),
                "full_name": user.get("full_name", ""),
                "biography": user.get("biography", ""),
                "external_url": user.get("external_url", "") or "",
                "is_verified": user.get("is_verified", False),
                "profile_pic_url": (
                    user.get("profile_pic_url_hd")
                    or user.get("profile_pic_url")
                    or ""
                ),
            }
        except httpx.TimeoutException:
            return {"error": "timeout", "details": "Instagram yanıt vermedi (12 sn zaman aşımı)"}
        except httpx.ConnectError as e:
            return {"error": "connection_error", "details": f"Bağlantı kurulamadı: {e}"}
        except Exception as e:
            logger.error(f"Scraper hatası @{username}: {e}", exc_info=True)
            return {"error": "unknown_error", "details": str(e)}

    def get_followers_list(self, username: str) -> list[dict]:
        # Login gerektirdiğinden devre dışı
        return []

    def get_following_list(self, username: str) -> list[dict]:
        # Login gerektirdiğinden devre dışı
        return []

import httpx
import json
import logging
import random
import re
import time

logger = logging.getLogger(__name__)

_last_request_time: float = 0.0


def _rate_limit_wait():
    global _last_request_time
    elapsed = time.time() - _last_request_time
    wait = random.uniform(1, 2)
    if elapsed < wait:
        time.sleep(wait - elapsed)
    _last_request_time = time.time()


class InstagramScraper:
    _BROWSER_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }
    _API_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "X-IG-App-ID": "936619743392459",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Referer": "https://www.instagram.com/",
        "Origin": "https://www.instagram.com",
    }

    def get_profile_stats(self, username: str) -> dict:
        _rate_limit_wait()
        try:
            with httpx.Client(timeout=12.0, follow_redirects=True) as client:
                # Adım 1: Ana sayfadan session cookie al (CSRF token vb.)
                try:
                    client.get("https://www.instagram.com/", headers=self._BROWSER_HEADERS)
                    logger.debug(f"Session cookie alındı: {dict(client.cookies)}")
                except Exception as e:
                    logger.debug(f"Ana sayfa isteği başarısız: {e}")

                # Adım 2: Web profile info API'si
                csrf = client.cookies.get("csrftoken", "")
                api_headers = dict(self._API_HEADERS)
                if csrf:
                    api_headers["X-CSRFToken"] = csrf

                r = client.get(
                    f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}",
                    headers=api_headers,
                )
                logger.info(f"API yanıtı @{username}: HTTP {r.status_code}")

                if r.status_code == 200:
                    data = r.json()
                    user = data.get("data", {}).get("user")
                    if user:
                        return self._parse_user(user)
                    return {"error": "user_not_found", "details": f"@{username} JSON'da bulunamadı"}

                if r.status_code == 404:
                    return {"error": "profile_not_found", "details": f"@{username} profili bulunamadı"}

                # Adım 3: Fallback — HTML'den JSON-LD ile çek
                logger.info(f"API {r.status_code}, HTML scrape deneniyor @{username}")
                return self._scrape_html(client, username)

        except httpx.TimeoutException:
            return {"error": "timeout", "details": "Instagram yanıt vermedi (12 sn zaman aşımı)"}
        except httpx.ConnectError as e:
            return {"error": "connection_error", "details": f"Bağlantı kurulamadı: {e}"}
        except Exception as e:
            logger.error(f"Scraper hatası @{username}: {e}", exc_info=True)
            return {"error": "unknown_error", "details": str(e)}

    def _parse_user(self, user: dict) -> dict:
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

    def _scrape_html(self, client: httpx.Client, username: str) -> dict:
        """HTML sayfasından JSON-LD ile temel profil verisi çeker."""
        try:
            r = client.get(
                f"https://www.instagram.com/{username}/",
                headers=self._BROWSER_HEADERS,
            )
        except Exception as e:
            return {"error": "connection_error", "details": str(e)}

        if r.status_code == 404:
            return {"error": "profile_not_found", "details": f"@{username} bulunamadı"}
        if r.status_code != 200:
            return {"error": "http_error", "details": f"HTML scrape HTTP {r.status_code}"}

        html = r.text

        # Login duvarı tespiti
        if "Log in to Instagram" in html or "LoginAndSignupPage" in html or "login" in r.url.path:
            return {
                "error": "login_required",
                "details": "Instagram bu sunucu IP'sinden profil görüntülenmesini engelliyor",
            }

        # Gizli hesap tespiti
        is_private = "This Account is Private" in html or "Bu hesap gizlidir" in html

        # JSON-LD'den veri çıkar
        match = re.search(
            r'<script type="application/ld\+json"[^>]*>(.*?)</script>',
            html, re.DOTALL,
        )
        if match:
            try:
                ld = json.loads(match.group(1))
                entity = ld.get("mainEntity") or ld
                followers, following = 0, 0
                for stat in entity.get("interactionStatistic", []):
                    itype = stat.get("interactionType", "")
                    count = int(stat.get("userInteractionCount", 0))
                    if "FollowAction" in itype:
                        followers = count
                    elif "BefriendAction" in itype:
                        following = count
                image = entity.get("image", "")
                return {
                    "followers_count": followers,
                    "following_count": following,
                    "posts_count": 0,
                    "is_private": is_private,
                    "full_name": entity.get("name", ""),
                    "biography": entity.get("description", ""),
                    "external_url": "",
                    "is_verified": False,
                    "profile_pic_url": image if isinstance(image, str) else "",
                }
            except Exception as e:
                logger.debug(f"JSON-LD parse hatası: {e}")

        return {
            "error": "blocked",
            "details": (
                "Instagram bu sunucu IP'sinden veri alınmasını engelliyor. "
                "Render sunucuları Instagram tarafından kısıtlanmış olabilir."
            ),
        }

    def get_followers_list(self, username: str) -> list[dict]:
        # Login gerektirdiğinden devre dışı
        return []

    def get_following_list(self, username: str) -> list[dict]:
        # Login gerektirdiğinden devre dışı
        return []

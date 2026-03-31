import httpx
import json
import logging
import os
import random
import re
import time

logger = logging.getLogger(__name__)

_last_request_time: float = 0.0

# Cloudflare Worker proxy URL — ayarlanmışsa direkt Instagram yerine buraya istek gönderir
# Render ortam değişkeni: INSTAGRAM_PROXY_URL
PROXY_URL = os.getenv("INSTAGRAM_PROXY_URL", "").rstrip("/")


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
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
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
        if PROXY_URL:
            return self._fetch_via_proxy(username)
        return self._fetch_direct(username)

    # ── Proxy yolu (Cloudflare Worker) ──────────────────────────────────────

    def _fetch_via_proxy(self, username: str) -> dict:
        try:
            with httpx.Client(timeout=12.0) as client:
                r = client.get(f"{PROXY_URL}?username={username}")
                logger.info(f"Proxy yanıtı @{username}: HTTP {r.status_code}")

                if r.status_code == 200:
                    data = r.json()
                    user = data.get("data", {}).get("user")
                    if user:
                        return self._parse_user(user)
                    return {"error": "user_not_found", "details": f"@{username} bulunamadı"}
                if r.status_code == 404:
                    return {"error": "profile_not_found", "details": f"@{username} bulunamadı"}
                return {"error": "proxy_error", "details": f"Proxy HTTP {r.status_code}: {r.text[:200]}"}
        except httpx.TimeoutException:
            return {"error": "timeout", "details": "Proxy yanıt vermedi (12 sn)"}
        except Exception as e:
            logger.error(f"Proxy hatası @{username}: {e}", exc_info=True)
            return {"error": "proxy_error", "details": str(e)}

    # ── Direkt yol (sunucu IP'si engelliyse çalışmaz) ───────────────────────

    def _fetch_direct(self, username: str) -> dict:
        try:
            with httpx.Client(timeout=12.0, follow_redirects=True) as client:
                # Adım 1: Session cookie al
                try:
                    client.get("https://www.instagram.com/", headers=self._BROWSER_HEADERS)
                except Exception:
                    pass

                # Adım 2: Web profile info API
                csrf = client.cookies.get("csrftoken", "")
                headers = dict(self._API_HEADERS)
                if csrf:
                    headers["X-CSRFToken"] = csrf

                r = client.get(
                    f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}",
                    headers=headers,
                )
                logger.info(f"Direkt API @{username}: HTTP {r.status_code}")

                if r.status_code == 200:
                    data = r.json()
                    user = data.get("data", {}).get("user")
                    if user:
                        return self._parse_user(user)
                    return {"error": "user_not_found", "details": f"@{username} bulunamadı"}
                if r.status_code == 404:
                    return {"error": "profile_not_found", "details": f"@{username} bulunamadı"}

                # Adım 3: HTML fallback
                logger.info(f"API {r.status_code}, HTML scrape deneniyor @{username}")
                return self._scrape_html(client, username)

        except httpx.TimeoutException:
            return {"error": "timeout", "details": "Instagram yanıt vermedi (12 sn)"}
        except httpx.ConnectError as e:
            return {"error": "connection_error", "details": str(e)}
        except Exception as e:
            logger.error(f"Scraper hatası @{username}: {e}", exc_info=True)
            return {"error": "unknown_error", "details": str(e)}

    def _scrape_html(self, client: httpx.Client, username: str) -> dict:
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
            return {"error": "http_error", "details": f"HTML HTTP {r.status_code}"}

        html = r.text
        if "Log in to Instagram" in html or "LoginAndSignupPage" in html:
            return {
                "error": "blocked",
                "details": (
                    "Instagram bu sunucu IP'sini engelliyor. "
                    "Render'da INSTAGRAM_PROXY_URL ortam değişkeni ayarlanmalı. "
                    "SETUP.md dosyasındaki adımları izle."
                ),
            }

        is_private = "This Account is Private" in html
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
            except Exception:
                pass

        return {
            "error": "blocked",
            "details": (
                "Instagram bu sunucu IP'sini engelliyor. "
                "INSTAGRAM_PROXY_URL ortam değişkeni ayarla. "
                "SETUP.md dosyasındaki adımları izle."
            ),
        }

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

    def get_followers_list(self, username: str) -> list[dict]:
        return []

    def get_following_list(self, username: str) -> list[dict]:
        return []

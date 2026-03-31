/**
 * Instagram Proxy — Cloudflare Worker
 *
 * Kurulum:
 *  1. https://dash.cloudflare.com adresine git, ücretsiz hesap aç
 *  2. Workers & Pages > Create > Worker
 *  3. Bu dosyanın içeriğini yapıştır, Deploy et
 *  4. Worker URL'ini kopyala (örn. https://instagram-proxy.your-name.workers.dev)
 *  5. Render dashboard > instagram-tracker-api > Environment Variables
 *     INSTAGRAM_PROXY_URL = <worker URL>
 *  6. Render'da Manual Deploy tetikle
 */

export default {
  async fetch(request) {
    // CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, OPTIONS",
          "Access-Control-Allow-Headers": "*",
        },
      });
    }

    const url = new URL(request.url);
    const username = url.searchParams.get("username");

    if (!username) {
      return json({ error: "username parametresi gerekli" }, 400);
    }

    // Güvenlik: sadece geçerli Instagram username karakterleri
    if (!/^[a-zA-Z0-9._]{1,30}$/.test(username)) {
      return json({ error: "Geçersiz username" }, 400);
    }

    try {
      const igUrl = `https://i.instagram.com/api/v1/users/web_profile_info/?username=${encodeURIComponent(username)}`;

      const igResp = await fetch(igUrl, {
        headers: {
          "User-Agent":
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
          Accept: "*/*",
          "Accept-Language": "en-US,en;q=0.9",
          "X-IG-App-ID": "936619743392459",
          "X-Requested-With": "XMLHttpRequest",
          "Sec-Fetch-Dest": "empty",
          "Sec-Fetch-Mode": "cors",
          "Sec-Fetch-Site": "same-site",
          Referer: "https://www.instagram.com/",
          Origin: "https://www.instagram.com",
        },
      });

      const body = await igResp.text();

      return new Response(body, {
        status: igResp.status,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          "Cache-Control": "no-store",
        },
      });
    } catch (e) {
      return json({ error: "fetch_failed", details: e.message }, 500);
    }
  },
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
  });
}

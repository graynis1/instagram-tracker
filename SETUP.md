# Kurulum Kılavuzu

## Backend (Render.com)

### 1. GitHub'a Push Et
```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/kullanici/instagram-tracker.git
git push -u origin main
```

### 2. Render.com'da Servis Oluştur
1. render.com → "New Web Service"
2. GitHub repo'yu bağla
3. `render.yaml` otomatik algılanır, ayarları onaylar
4. PostgreSQL veritabanı otomatik oluşturulur

### 3. APNs Yapılandırması
1. developer.apple.com → Certificates, Identifiers & Profiles
2. Keys → "+" → Apple Push Notifications service (APNs) seç
3. .p8 dosyasını indir (yalnızca bir kez indirilebilir!)
4. Render dashboard → Environment Variables:
   - `APNS_TEAM_ID`: Developer hesabındaki Team ID (10 haneli)
   - `APNS_KEY_ID`: Oluşturduğun key'in ID'si
   - `APNS_AUTH_KEY`: .p8 dosyasının içeriği (tüm satırlar dahil)
   - `APNS_BUNDLE_ID`: com.yourname.instagramtracker

### 4. Servis URL'ini Al
Render dashboard → Web Service → URL'yi kopyala
Örnek: `https://instagram-tracker-api.onrender.com`

---

## iOS App (Xcode)

### 1. Proje Oluştur
1. Xcode → File → New Project
2. iOS → App → SwiftUI, Bundle ID: `com.yourname.instagramtracker`
3. iOS 17.0 Deployment Target
4. Tüm .swift dosyalarını projeye ekle

### 2. Push Notification Capability
1. Project → Target → Signing & Capabilities
2. "+ Capability" → Push Notifications
3. Background Modes → Remote notifications ✓

### 3. API URL'ini Güncelle
`APIService.swift` → `baseURL` satırını Render URL'inle değiştir:
```swift
private let baseURL = "https://instagram-tracker-api.onrender.com"
```

### 4. Test Et
- Push bildirim simulator'da çalışmaz, gerçek cihaz gerekir
- Xcode → Window → Devices and Simulators → cihazını seç
- Run (⌘R)

---

## Sorun Giderme

### Backend başlamıyor
- Render logs'u kontrol et
- `DATABASE_URL` env var set edilmiş mi?
- `alembic upgrade head` başarıyla çalıştı mı?

### Push bildirim gelmiyor
- Device token Render'a ulaşıyor mu? (`/api/devices/register` endpoint)
- APNs env vars doğru mu?
- Production vs Sandbox: `ENVIRONMENT=production` ise gerçek APNs, değilse sandbox

### Instagram rate limit
- Scraper 30 dakika bekler ve tekrar dener
- Logs'ta "rate_limited" mesajını gör
- Check interval'i 6+ saat olarak bırak

---

## Mimari Özeti

```
iOS App ──HTTPS──► FastAPI (Render)
                       │
                  APScheduler (periyodik kontrol)
                       │
              Instaloader (anonim scrape)
                       │
                  PostgreSQL (veriler)
                       │
              APNs ──► iPhone bildirimi
```

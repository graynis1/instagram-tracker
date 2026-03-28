import Foundation

enum APIError: Error, LocalizedError {
    case invalidURL
    case httpError(Int, String)
    case decodingError(Error)
    case networkError(Error)
    case unknown

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Geçersiz URL"
        case .httpError(let code, let msg): return "Sunucu hatası \(code): \(msg)"
        case .decodingError(let e): return "Veri çözümleme hatası: \(e.localizedDescription)"
        case .networkError(let e): return "Ağ hatası: \(e.localizedDescription)"
        case .unknown: return "Bilinmeyen hata"
        }
    }
}

actor APIService {
    static let shared = APIService()

    private let baseURL = "https://instagram-tracker-api.onrender.com"

    private var userID: String {
        if let id = UserDefaults.standard.string(forKey: "USER_ID") { return id }
        let new = UUID().uuidString
        UserDefaults.standard.set(new, forKey: "USER_ID")
        return new
    }

    private let decoder: JSONDecoder = {
        let d = JSONDecoder()
        d.dateDecodingStrategy = .custom { decoder in
            let container = try decoder.singleValueContainer()
            let str = try container.decode(String.self)
            let formatters = [
                "yyyy-MM-dd'T'HH:mm:ss.SSSSSS",
                "yyyy-MM-dd'T'HH:mm:ss",
                "yyyy-MM-dd'T'HH:mm:ssZ",
                "yyyy-MM-dd'T'HH:mm:ss.SSSSSSZ",
            ]
            let f = DateFormatter()
            f.locale = Locale(identifier: "en_US_POSIX")
            for fmt in formatters {
                f.dateFormat = fmt
                if let date = f.date(from: str) { return date }
            }
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Tarih ayrıştırılamadı: \(str)"
            )
        }
        return d
    }()

    private func request<T: Decodable>(
        path: String,
        method: String = "GET",
        body: Data? = nil
    ) async throws -> T {
        guard let url = URL(string: baseURL + path) else { throw APIError.invalidURL }

        var req = URLRequest(url: url)
        req.httpMethod = method
        req.setValue(userID, forHTTPHeaderField: "X-User-ID")
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if let body { req.httpBody = body }

        do {
            let (data, response) = try await URLSession.shared.data(for: req)
            guard let http = response as? HTTPURLResponse else { throw APIError.unknown }
            if !(200...299).contains(http.statusCode) {
                let msg = String(data: data, encoding: .utf8) ?? "Bilinmeyen hata"
                throw APIError.httpError(http.statusCode, msg)
            }
            do {
                return try decoder.decode(T.self, from: data)
            } catch {
                throw APIError.decodingError(error)
            }
        } catch let e as APIError {
            throw e
        } catch {
            throw APIError.networkError(error)
        }
    }

    private func requestVoid(
        path: String,
        method: String = "DELETE",
        body: Data? = nil
    ) async throws {
        guard let url = URL(string: baseURL + path) else { throw APIError.invalidURL }

        var req = URLRequest(url: url)
        req.httpMethod = method
        req.setValue(userID, forHTTPHeaderField: "X-User-ID")
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if let body { req.httpBody = body }

        do {
            let (data, response) = try await URLSession.shared.data(for: req)
            guard let http = response as? HTTPURLResponse else { throw APIError.unknown }
            if !(200...299).contains(http.statusCode) {
                let msg = String(data: data, encoding: .utf8) ?? "Bilinmeyen hata"
                throw APIError.httpError(http.statusCode, msg)
            }
        } catch let e as APIError {
            throw e
        } catch {
            throw APIError.networkError(error)
        }
    }

    // MARK: - Device

    func registerDevice(deviceToken: String) async throws {
        let body = try JSONSerialization.data(withJSONObject: [
            "user_id": userID,
            "device_token": deviceToken,
        ])
        let _: [String: String] = try await request(path: "/api/devices/register", method: "POST", body: body)
    }

    // MARK: - Accounts

    func getAccounts() async throws -> [TrackedAccount] {
        return try await request(path: "/api/accounts")
    }

    func addAccount(username: String, intervalMinutes: Int) async throws -> TrackedAccount {
        let body = try JSONSerialization.data(withJSONObject: [
            "instagram_username": username,
            "check_interval_minutes": intervalMinutes,
            "user_id": userID,
        ])
        return try await request(path: "/api/accounts", method: "POST", body: body)
    }

    func deleteAccount(id: String) async throws {
        try await requestVoid(path: "/api/accounts/\(id)", method: "DELETE")
    }

    func updateAccount(id: String, intervalHours: Int? = nil, isActive: Bool? = nil) async throws -> TrackedAccount {
        var dict: [String: Any] = [:]
        if let h = intervalHours { dict["check_interval_hours"] = h }
        if let a = isActive { dict["is_active"] = a }
        let body = try JSONSerialization.data(withJSONObject: dict)
        return try await request(path: "/api/accounts/\(id)", method: "PATCH", body: body)
    }

    func getSnapshot(accountId: String) async throws -> AccountSnapshot {
        return try await request(path: "/api/accounts/\(accountId)/snapshot")
    }

    func checkNow(accountId: String) async throws {
        try await requestVoid(path: "/api/accounts/\(accountId)/check-now", method: "POST")
    }

    // MARK: - History

    func getHistory(accountId: String? = nil, page: Int = 1) async throws -> PaginatedHistory {
        if let id = accountId {
            return try await request(path: "/api/history/\(id)?page=\(page)")
        }
        return try await request(path: "/api/history?page=\(page)")
    }
}

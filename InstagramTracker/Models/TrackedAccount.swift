import Foundation

struct TrackedAccount: Identifiable, Codable {
    let id: String
    let userId: String
    let instagramUsername: String
    var checkIntervalHours: Int
    var isActive: Bool
    let createdAt: Date
    var latestSnapshot: AccountSnapshot?

    enum CodingKeys: String, CodingKey {
        case id
        case userId = "user_id"
        case instagramUsername = "instagram_username"
        case checkIntervalHours = "check_interval_hours"
        case isActive = "is_active"
        case createdAt = "created_at"
        case latestSnapshot = "latest_snapshot"
    }
}

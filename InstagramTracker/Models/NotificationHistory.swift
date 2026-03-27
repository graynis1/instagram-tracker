import Foundation

struct NotificationLog: Identifiable, Codable {
    let id: String
    let trackedAccountId: String
    let notificationType: String
    let message: String
    let sentAt: Date
    let wasDelivered: Bool

    enum CodingKeys: String, CodingKey {
        case id
        case trackedAccountId = "tracked_account_id"
        case notificationType = "notification_type"
        case message
        case sentAt = "sent_at"
        case wasDelivered = "was_delivered"
    }
}

struct HistoryEntry: Identifiable, Codable {
    var id: String { notification.id }
    let notification: NotificationLog
    let accountUsername: String

    enum CodingKeys: String, CodingKey {
        case notification
        case accountUsername = "account_username"
    }
}

struct PaginatedHistory: Codable {
    let items: [HistoryEntry]
    let total: Int
    let page: Int
    let perPage: Int
    let hasMore: Bool

    enum CodingKeys: String, CodingKey {
        case items, total, page
        case perPage = "per_page"
        case hasMore = "has_more"
    }
}

import Foundation

struct AccountSnapshot: Identifiable, Codable {
    let id: String
    let trackedAccountId: String
    let followersCount: Int
    let followingCount: Int
    let postsCount: Int
    let isPrivate: Bool
    let fullName: String?
    let biography: String?
    let externalUrl: String?
    let isVerified: Bool
    let profilePicUrl: String?
    let snapshottedAt: Date

    enum CodingKeys: String, CodingKey {
        case id
        case trackedAccountId = "tracked_account_id"
        case followersCount = "followers_count"
        case followingCount = "following_count"
        case postsCount = "posts_count"
        case isPrivate = "is_private"
        case fullName = "full_name"
        case biography
        case externalUrl = "external_url"
        case isVerified = "is_verified"
        case profilePicUrl = "profile_pic_url"
        case snapshottedAt = "snapshotted_at"
    }
}

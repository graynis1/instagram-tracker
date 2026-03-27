import Foundation

enum ChangeType: String, Codable {
    case newFollower = "new_follower"
    case lostFollower = "lost_follower"
    case newFollowing = "new_following"
    case lostFollowing = "lost_following"
}

struct FollowerChange: Identifiable, Codable {
    let id: String
    let trackedAccountId: String
    let changeType: ChangeType
    let username: String
    let fullName: String?
    let profilePicUrl: String?
    let detectedAt: Date

    enum CodingKeys: String, CodingKey {
        case id
        case trackedAccountId = "tracked_account_id"
        case changeType = "change_type"
        case username
        case fullName = "full_name"
        case profilePicUrl = "profile_pic_url"
        case detectedAt = "detected_at"
    }
}

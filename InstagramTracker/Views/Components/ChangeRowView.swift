import SwiftUI

struct ChangeRowView: View {
    let entry: HistoryEntry

    private var emoji: String {
        switch entry.notification.notificationType {
        case "follower_gain":    return "📈"
        case "follower_loss":    return "📉"
        case "following_gain":   return "➕"
        case "following_loss":   return "➖"
        case "new_post":         return "📸"
        case "went_private":     return "🔒"
        case "went_public":      return "🔓"
        case "bio_change":       return "✏️"
        case "new_following_person": return "👤"
        default:                 return "🔔"
        }
    }

    private var bgColor: Color {
        switch entry.notification.notificationType {
        case "follower_gain", "following_gain", "new_post": return .bgGreen
        case "follower_loss", "following_loss", "went_private": return .bgRed
        default: return .bgPurpleTint
        }
    }

    var body: some View {
        HStack(spacing: 12) {
            ZStack {
                Circle()
                    .fill(bgColor)
                    .frame(width: 36, height: 36)
                Text(emoji)
                    .font(.system(size: 16))
            }
            VStack(alignment: .leading, spacing: 3) {
                Text("@\(entry.accountUsername)")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.textPrimary)
                Text(entry.notification.message)
                    .font(.system(size: 12))
                    .foregroundColor(.textSecondary)
                    .lineLimit(2)
            }
            Spacer()
            Text(entry.notification.sentAt.relativeString)
                .font(.system(size: 9))
                .foregroundColor(.textTertiary)
        }
        .padding(.vertical, 6)
    }
}

private extension Date {
    var relativeString: String {
        let diff = Date().timeIntervalSince(self)
        if diff < 60 { return "şimdi" }
        if diff < 3600 { return "\(Int(diff/60))dk" }
        if diff < 86400 { return "\(Int(diff/3600))sa" }
        if diff < 604800 { return "\(Int(diff/86400))g" }
        let f = DateFormatter()
        f.dateFormat = "d MMM"
        f.locale = Locale(identifier: "tr_TR")
        return f.string(from: self)
    }
}

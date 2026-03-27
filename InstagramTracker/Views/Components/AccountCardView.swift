import SwiftUI

struct AccountCardView: View {
    let account: TrackedAccount

    private var latestFollowers: Int {
        account.latestSnapshot?.followersCount ?? 0
    }
    private var latestFollowing: Int {
        account.latestSnapshot?.followingCount ?? 0
    }
    private var latestPosts: Int {
        account.latestSnapshot?.postsCount ?? 0
    }

    private func formatCount(_ n: Int) -> String {
        if n >= 1_000_000 { return String(format: "%.1fM", Double(n) / 1_000_000) }
        if n >= 1_000 { return String(format: "%.1fK", Double(n) / 1_000) }
        return "\(n)"
    }

    private var timeAgo: String {
        guard let snap = account.latestSnapshot else { return "henüz kontrol edilmedi" }
        let diff = Date().timeIntervalSince(snap.snapshottedAt)
        if diff < 60 { return "az önce" }
        if diff < 3600 { return "\(Int(diff/60)) dk önce" }
        if diff < 86400 { return "\(Int(diff/3600)) sa önce" }
        return "\(Int(diff/86400)) gün önce"
    }

    var body: some View {
        VStack(spacing: 0) {
            // Üst satır
            HStack(spacing: 10) {
                GradientAvatarView(
                    username: account.instagramUsername,
                    fullName: account.latestSnapshot?.fullName,
                    size: 38
                )
                VStack(alignment: .leading, spacing: 2) {
                    HStack(spacing: 4) {
                        Text("@\(account.instagramUsername)")
                            .font(.system(size: 14, weight: .semibold))
                            .foregroundColor(.textPrimary)
                        if account.latestSnapshot?.isVerified == true {
                            Image(systemName: "checkmark.seal.fill")
                                .font(.system(size: 11))
                                .foregroundColor(.brandPurple)
                        }
                    }
                    Text(timeAgo)
                        .font(.system(size: 10))
                        .foregroundColor(.textTertiary)
                }
                Spacer()
                if account.isActive {
                    Text("Aktif")
                        .pillStyle(bg: .bgGreen, text: .statusGreen)
                } else {
                    Text("Pasif")
                        .pillStyle(bg: Color(hex: "F3F4F6"), text: .textSecondary)
                }
            }
            .padding(.horizontal, 14)
            .padding(.top, 14)
            .padding(.bottom, 10)

            Divider()
                .background(Color.black.opacity(0.05))
                .padding(.horizontal, 14)

            // Alt istatistik satırı
            HStack(spacing: 0) {
                statBox(value: formatCount(latestFollowers), label: "TAKİPÇİ")
                Divider().frame(height: 30).background(Color.black.opacity(0.05))
                statBox(value: formatCount(latestFollowing), label: "TAKİP")
                Divider().frame(height: 30).background(Color.black.opacity(0.05))
                statBox(value: formatCount(latestPosts), label: "GÖNDERI")
            }
            .padding(.vertical, 10)
        }
        .cardStyle()
    }

    private func statBox(value: String, label: String) -> some View {
        VStack(spacing: 2) {
            Text(value)
                .font(.system(size: 15, weight: .bold))
                .foregroundColor(.textPrimary)
            Text(label)
                .font(.system(size: 9, weight: .semibold))
                .foregroundColor(.textSecondary)
                .tracking(0.3)
        }
        .frame(maxWidth: .infinity)
    }
}

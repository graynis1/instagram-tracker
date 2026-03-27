import SwiftUI

struct HistoryView: View {
    @StateObject private var vm = NotificationsViewModel()

    private func emoji(for type: String) -> String {
        switch type {
        case "follower_gain":        return "📈"
        case "follower_loss":        return "📉"
        case "following_gain":       return "➕"
        case "following_loss":       return "➖"
        case "new_post":             return "📸"
        case "went_private":         return "🔒"
        case "went_public":          return "🔓"
        case "bio_change":           return "✏️"
        case "new_following_person": return "👤"
        default:                     return "🔔"
        }
    }

    private func bgColor(for type: String) -> Color {
        switch type {
        case "follower_gain", "following_gain", "new_post", "went_public": return .bgGreen
        case "follower_loss", "following_loss", "went_private": return .bgRed
        default: return .bgPurpleTint
        }
    }

    private func timeAgo(_ date: Date) -> String {
        let diff = Date().timeIntervalSince(date)
        if diff < 60 { return "şimdi" }
        if diff < 3600 { return "\(Int(diff/60)) dk" }
        if diff < 86400 { return "\(Int(diff/3600)) sa" }
        return "\(Int(diff/86400)) gün"
    }

    var body: some View {
        NavigationStack {
            ZStack {
                Color.bgPage.ignoresSafeArea()

                if vm.isLoading && vm.entries.isEmpty {
                    ProgressView().tint(.brandPurple)
                } else if vm.entries.isEmpty {
                    EmptyStateView(
                        icon: "bell",
                        title: "Henüz bildirim yok",
                        description: "Takip ettiğin hesaplarda değişiklik olduğunda burada görünecek"
                    )
                } else {
                    ScrollView {
                        VStack(spacing: 0) {
                            // Alt başlık
                            HStack {
                                Text("Bugün \(vm.todayCount) yeni bildirim")
                                    .font(.system(size: 13))
                                    .foregroundColor(.textSecondary)
                                Spacer()
                            }
                            .padding(.horizontal, 16)
                            .padding(.bottom, 12)

                            LazyVStack(spacing: 8) {
                                ForEach(vm.entries) { entry in
                                    notificationCard(entry: entry)
                                        .onAppear {
                                            if entry.id == vm.entries.last?.id {
                                                Task { await vm.loadMore() }
                                            }
                                        }
                                }
                            }
                            .padding(.horizontal, 12)
                        }
                        .padding(.top, 4)
                    }
                    .refreshable {
                        await vm.loadHistory()
                    }
                }
            }
            .navigationTitle("Bildirimler")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Temizle") {
                        vm.clearHistory()
                    }
                    .font(.system(size: 14))
                    .foregroundColor(.brandPurple)
                }
            }
        }
        .task {
            await vm.loadHistory()
        }
    }

    private func notificationCard(entry: HistoryEntry) -> some View {
        HStack(spacing: 0) {
            // Sol kenarda dikey gradient çizgi
            Rectangle()
                .fill(LinearGradient.brand)
                .frame(width: 3)
                .cornerRadius(2)

            HStack(spacing: 12) {
                ZStack {
                    Circle()
                        .fill(bgColor(for: entry.notification.notificationType))
                        .frame(width: 36, height: 36)
                    Text(emoji(for: entry.notification.notificationType))
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
                Text(timeAgo(entry.notification.sentAt))
                    .font(.system(size: 9))
                    .foregroundColor(.textTertiary)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 12)
        }
        .background(Color.bgCard)
        .cornerRadius(16)
        .shadow(color: .black.opacity(0.05), radius: 6, x: 0, y: 2)
    }
}

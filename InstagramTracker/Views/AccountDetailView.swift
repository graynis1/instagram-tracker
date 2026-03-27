import SwiftUI
import Charts

struct AccountDetailView: View {
    let account: TrackedAccount
    @StateObject private var vm: AccountDetailViewModel

    init(account: TrackedAccount) {
        self.account = account
        _vm = StateObject(wrappedValue: AccountDetailViewModel(account: account))
    }

    private func formatCount(_ n: Int) -> String {
        if n >= 1_000_000 { return String(format: "%.1fM", Double(n) / 1_000_000) }
        if n >= 1_000 { return String(format: "%.1fK", Double(n) / 1_000) }
        return "\(n)"
    }

    var body: some View {
        ZStack {
            Color.bgPage.ignoresSafeArea()

            ScrollView {
                VStack(spacing: 14) {
                    // 1. Profil kartı
                    profileCard

                    // 2. 3'lü stat grid
                    if let snap = vm.snapshot {
                        HStack(spacing: 10) {
                            StatCardView(
                                label: "Takipçi",
                                value: formatCount(snap.followersCount),
                                change: nil
                            )
                            StatCardView(
                                label: "Takip",
                                value: formatCount(snap.followingCount),
                                change: nil
                            )
                            StatCardView(
                                label: "Gönderi",
                                value: formatCount(snap.postsCount),
                                change: nil
                            )
                        }
                    }

                    // 3. Takipçi grafiği (Chart)
                    if let snap = vm.snapshot {
                        followerChart(snap: snap)
                    }

                    // 4. Son değişiklikler
                    if !vm.history.isEmpty {
                        recentChanges
                    }

                    if vm.isLoading {
                        ProgressView()
                            .tint(.brandPurple)
                            .padding()
                    }
                }
                .padding(14)
            }
            .refreshable {
                await vm.loadDetail()
            }
        }
        .navigationTitle("@\(account.instagramUsername)")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button {
                    Task { await vm.checkNow() }
                } label: {
                    if vm.isCheckingNow {
                        ProgressView().tint(.brandPurple)
                    } else {
                        Image(systemName: "arrow.clockwise")
                            .foregroundStyle(LinearGradient.brand)
                    }
                }
                .disabled(vm.isCheckingNow)
            }
        }
        .task {
            await vm.loadDetail()
        }
    }

    private var profileCard: some View {
        HStack(spacing: 14) {
            GradientAvatarView(
                username: account.instagramUsername,
                fullName: vm.snapshot?.fullName,
                size: 56
            )
            VStack(alignment: .leading, spacing: 4) {
                HStack(spacing: 4) {
                    if let name = vm.snapshot?.fullName, !name.isEmpty {
                        Text(name)
                            .font(.system(size: 15, weight: .semibold))
                            .foregroundColor(.textPrimary)
                    }
                    if vm.snapshot?.isVerified == true {
                        Image(systemName: "checkmark.seal.fill")
                            .font(.system(size: 13))
                            .foregroundColor(.brandPurple)
                    }
                }
                Text("@\(account.instagramUsername)")
                    .font(.system(size: 13))
                    .foregroundColor(.brandPurple)
                if let bio = vm.snapshot?.biography, !bio.isEmpty {
                    Text(bio)
                        .font(.system(size: 12))
                        .foregroundColor(.textSecondary)
                        .lineLimit(3)
                }
                HStack(spacing: 4) {
                    if vm.snapshot?.isPrivate == true {
                        Image(systemName: "lock.fill")
                            .font(.system(size: 9))
                            .foregroundColor(.textTertiary)
                        Text("Gizli Hesap")
                            .font(.system(size: 10))
                            .foregroundColor(.textTertiary)
                    } else {
                        Image(systemName: "globe")
                            .font(.system(size: 9))
                            .foregroundColor(.textTertiary)
                        Text("Herkese Açık")
                            .font(.system(size: 10))
                            .foregroundColor(.textTertiary)
                    }
                }
            }
            Spacer()
        }
        .padding(16)
        .cardStyle()
    }

    private func followerChart(snap: AccountSnapshot) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("TAKİPÇİ GELİŞİMİ")
                .font(.system(size: 11, weight: .semibold))
                .foregroundColor(.textSecondary)
                .tracking(0.5)

            Chart {
                LineMark(
                    x: .value("Tarih", snap.snapshottedAt),
                    y: .value("Takipçi", snap.followersCount)
                )
                .foregroundStyle(LinearGradient.brand)
                .lineStyle(StrokeStyle(lineWidth: 2.5))

                AreaMark(
                    x: .value("Tarih", snap.snapshottedAt),
                    y: .value("Takipçi", snap.followersCount)
                )
                .foregroundStyle(
                    LinearGradient(
                        colors: [Color.brandPurple.opacity(0.2), Color.brandPurple.opacity(0)],
                        startPoint: .top, endPoint: .bottom
                    )
                )

                PointMark(
                    x: .value("Tarih", snap.snapshottedAt),
                    y: .value("Takipçi", snap.followersCount)
                )
                .foregroundStyle(Color.brandPurple)
                .symbolSize(50)
            }
            .frame(height: 140)
            .chartYAxis {
                AxisMarks(position: .leading)
            }
        }
        .padding(16)
        .cardStyle()
    }

    private var recentChanges: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("SON DEĞİŞİKLİKLER")
                .font(.system(size: 11, weight: .semibold))
                .foregroundColor(.textSecondary)
                .tracking(0.5)

            VStack(spacing: 0) {
                ForEach(vm.history.prefix(5)) { entry in
                    ChangeRowView(entry: entry)
                    if entry.id != vm.history.prefix(5).last?.id {
                        Divider().padding(.leading, 48)
                    }
                }
            }
            .padding(.horizontal, 12)
            .cardStyle()
        }
    }
}

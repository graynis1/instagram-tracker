import SwiftUI

struct SettingsView: View {
    @AppStorage("defaultIntervalMinutes") private var defaultInterval = 360
    @AppStorage("notifyFollowerChange") private var notifyFollowerChange = true
    @AppStorage("notifyFollowingChange") private var notifyFollowingChange = true
    @AppStorage("notifyNewPost") private var notifyNewPost = true
    @AppStorage("notifyPrivacyChange") private var notifyPrivacyChange = true
    @AppStorage("notifyBioChange") private var notifyBioChange = false

    @State private var showDeleteAlert = false

    private let intervals      = [5,      15,      30,      60,       180,      360,      720]
    private let intervalLabels = ["5 Dk", "15 Dk", "30 Dk", "1 Saat", "3 Saat", "6 Saat", "12 Saat"]

    var body: some View {
        NavigationStack {
            ZStack {
                Color.bgPage.ignoresSafeArea()

                ScrollView {
                    VStack(spacing: 24) {
                        // Varsayılan kontrol sıklığı
                        VStack(alignment: .leading, spacing: 10) {
                            sectionLabel("VARSAYILAN KONTROL SIKLIĞI")
                            let columns = [GridItem(.flexible()), GridItem(.flexible())]
                            LazyVGrid(columns: columns, spacing: 8) {
                                ForEach(Array(intervals.enumerated()), id: \.offset) { idx, interval in
                                    intervalCard(interval: interval, label: intervalLabels[idx])
                                }
                            }
                        }

                        // Bildirim tercihleri
                        VStack(alignment: .leading, spacing: 10) {
                            sectionLabel("BİLDİRİM TERCİHLERİ")
                            VStack(spacing: 0) {
                                toggleRow(label: "Takipçi değişimi", binding: $notifyFollowerChange)
                                settingsDivider
                                toggleRow(label: "Takip değişimi", binding: $notifyFollowingChange)
                                settingsDivider
                                toggleRow(label: "Yeni gönderi", binding: $notifyNewPost)
                                settingsDivider
                                toggleRow(label: "Gizlilik değişimi", binding: $notifyPrivacyChange)
                                settingsDivider
                                toggleRow(label: "Biyografi değişimi", binding: $notifyBioChange)
                            }
                            .cardStyle()
                        }

                        // Hesap
                        VStack(alignment: .leading, spacing: 10) {
                            sectionLabel("HESAP")
                            VStack(spacing: 0) {
                                HStack {
                                    Text("Kullanıcı ID")
                                        .font(.system(size: 14))
                                        .foregroundColor(.textPrimary)
                                    Spacer()
                                    Text(UserDefaults.standard.string(forKey: "USER_ID")?.prefix(8).description ?? "-")
                                        .font(.system(size: 12, design: .monospaced))
                                        .foregroundColor(.textTertiary)
                                }
                                .padding(.horizontal, 14)
                                .padding(.vertical, 14)

                                settingsDivider

                                Button {
                                    showDeleteAlert = true
                                } label: {
                                    HStack {
                                        Text("Tüm verileri sil")
                                            .font(.system(size: 14))
                                            .foregroundColor(.statusRed)
                                        Spacer()
                                        Image(systemName: "trash")
                                            .font(.system(size: 13))
                                            .foregroundColor(.statusRed)
                                    }
                                    .padding(.horizontal, 14)
                                    .padding(.vertical, 14)
                                }
                            }
                            .cardStyle()
                        }

                        // Versiyon
                        Text("v1.0.0 · Instagram Tracker")
                            .font(.system(size: 12))
                            .foregroundColor(.textTertiary)
                            .frame(maxWidth: .infinity, alignment: .center)
                            .padding(.top, 8)
                            .padding(.bottom, 24)
                    }
                    .padding(16)
                }
            }
            .navigationTitle("Ayarlar")
            .navigationBarTitleDisplayMode(.large)
            .alert("Tüm Verileri Sil", isPresented: $showDeleteAlert) {
                Button("Sil", role: .destructive) {
                    UserDefaults.standard.removeObject(forKey: "USER_ID")
                    UserDefaults.standard.removeObject(forKey: "defaultIntervalHours")
                }
                Button("İptal", role: .cancel) {}
            } message: {
                Text("Tüm takip listesi ve geçmiş veriler silinecek. Bu işlem geri alınamaz.")
            }
        }
    }

    private func sectionLabel(_ text: String) -> some View {
        Text(text)
            .font(.system(size: 11, weight: .semibold))
            .foregroundColor(.textSecondary)
            .tracking(0.5)
    }

    private var settingsDivider: some View {
        Divider()
            .background(Color.black.opacity(0.05))
            .padding(.leading, 14)
    }

    private func intervalCard(interval: Int, label: String) -> some View {
        let isSelected = defaultInterval == interval
        return Button {
            withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                defaultInterval = interval
            }
        } label: {
            Text(label)
                .font(.system(size: 13, weight: isSelected ? .bold : .medium))
                .foregroundColor(isSelected ? .brandPurple : .textSecondary)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(isSelected ? Color.bgPurpleTint : Color.bgCard)
                .cornerRadius(12)
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(isSelected ? Color.brandPurple : Color.clear, lineWidth: 1.5)
                )
        }
        .buttonStyle(.plain)
    }

    private func toggleRow(label: String, binding: Binding<Bool>) -> some View {
        Toggle(isOn: binding) {
            Text(label)
                .font(.system(size: 14))
                .foregroundColor(.textPrimary)
        }
        .toggleStyle(BrandToggleStyle())
        .padding(.horizontal, 14)
        .padding(.vertical, 12)
    }
}

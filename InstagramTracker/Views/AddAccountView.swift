import SwiftUI

struct AddAccountView: View {
    @ObservedObject var vm: AccountsViewModel
    @Environment(\.dismiss) private var dismiss

    @State private var username = ""
    @State private var selectedInterval = 6
    @State private var notifyFollowerChange = true
    @State private var notifyFollowingChange = true
    @State private var notifyNewPost = true
    @State private var notifyPrivacyChange = true
    @State private var notifyBioChange = false
    @State private var isLoading = false
    @State private var errorMessage: String?

    private let intervals = [1, 2, 3, 6, 12]
    private let intervalLabels = ["1 Saat", "2 Saat", "3 Saat", "6 Saat", "12 Saat"]

    var body: some View {
        NavigationStack {
            ZStack(alignment: .bottom) {
                Color.bgPage.ignoresSafeArea()

                ScrollView {
                    VStack(spacing: 20) {
                        // Hata banner
                        if let err = errorMessage {
                            HStack(spacing: 8) {
                                Image(systemName: "exclamationmark.circle.fill")
                                    .foregroundColor(.statusRed)
                                Text(err)
                                    .font(.system(size: 13))
                                    .foregroundColor(.statusRed)
                                Spacer()
                                Button { withAnimation { errorMessage = nil } } label: {
                                    Image(systemName: "xmark")
                                        .font(.system(size: 11, weight: .bold))
                                        .foregroundColor(.statusRed)
                                }
                            }
                            .padding(12)
                            .background(Color.bgRed)
                            .cornerRadius(12)
                            .transition(.move(edge: .top).combined(with: .opacity))
                        }

                        // Kullanıcı adı
                        VStack(alignment: .leading, spacing: 8) {
                            Text("KULLANICI ADI")
                                .font(.system(size: 11, weight: .semibold))
                                .foregroundColor(.textSecondary)
                                .tracking(0.5)

                            HStack(spacing: 10) {
                                ZStack {
                                    Circle()
                                        .fill(LinearGradient.brand)
                                        .frame(width: 32, height: 32)
                                    Text("@")
                                        .font(.system(size: 14, weight: .bold))
                                        .foregroundColor(.white)
                                }
                                TextField("instagram_kullanici_adi", text: $username)
                                    .font(.system(size: 15))
                                    .foregroundColor(.textPrimary)
                                    .autocapitalization(.none)
                                    .autocorrectionDisabled()
                                    .keyboardType(.twitter)
                            }
                            .padding(14)
                            .cardStyle()
                        }

                        // Kontrol sıklığı
                        VStack(alignment: .leading, spacing: 8) {
                            Text("KONTROL SIKLIĞI")
                                .font(.system(size: 11, weight: .semibold))
                                .foregroundColor(.textSecondary)
                                .tracking(0.5)

                            let columns = [GridItem(.flexible()), GridItem(.flexible())]
                            LazyVGrid(columns: columns, spacing: 8) {
                                ForEach(Array(intervals.enumerated()), id: \.offset) { idx, interval in
                                    intervalCard(interval: interval, label: intervalLabels[idx])
                                }
                            }
                        }

                        // Bildirim tercihleri
                        VStack(alignment: .leading, spacing: 8) {
                            Text("BİLDİRİMLER")
                                .font(.system(size: 11, weight: .semibold))
                                .foregroundColor(.textSecondary)
                                .tracking(0.5)

                            VStack(spacing: 0) {
                                toggleRow(label: "Takipçi değişimi", binding: $notifyFollowerChange)
                                Divider().padding(.leading, 14)
                                toggleRow(label: "Takip değişimi", binding: $notifyFollowingChange)
                                Divider().padding(.leading, 14)
                                toggleRow(label: "Yeni gönderi", binding: $notifyNewPost)
                                Divider().padding(.leading, 14)
                                toggleRow(label: "Gizlilik değişimi", binding: $notifyPrivacyChange)
                                Divider().padding(.leading, 14)
                                toggleRow(label: "Biyografi değişimi", binding: $notifyBioChange)
                            }
                            .cardStyle()
                        }

                        Spacer(minLength: 90)
                    }
                    .padding(16)
                    .animation(.spring(response: 0.3, dampingFraction: 0.7), value: errorMessage)
                }

                // Alt buton
                VStack {
                    GradientButton("Takibe Başla", isLoading: isLoading) {
                        await addAccount()
                    }
                    .padding(.horizontal, 16)
                    .padding(.bottom, 24)
                }
                .background(
                    LinearGradient(
                        colors: [Color.bgPage.opacity(0), Color.bgPage],
                        startPoint: .top, endPoint: .bottom
                    )
                    .frame(height: 100)
                )
            }
            .navigationTitle("Hesap Ekle")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("İptal") { dismiss() }
                        .foregroundColor(.brandPurple)
                }
            }
        }
        .presentationDetents([.large])
    }

    private func intervalCard(interval: Int, label: String) -> some View {
        let isSelected = selectedInterval == interval
        return Button {
            withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                selectedInterval = interval
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

    private func addAccount() async {
        let trimmed = username.trimmingCharacters(in: .whitespacesAndNewlines)
            .replacingOccurrences(of: "@", with: "")
        guard !trimmed.isEmpty else {
            withAnimation { errorMessage = "Lütfen bir kullanıcı adı gir" }
            return
        }
        isLoading = true
        errorMessage = nil
        do {
            _ = try await vm.addAccount(username: trimmed, intervalHours: selectedInterval)
            dismiss()
        } catch {
            withAnimation { errorMessage = error.localizedDescription }
        }
        isLoading = false
    }
}

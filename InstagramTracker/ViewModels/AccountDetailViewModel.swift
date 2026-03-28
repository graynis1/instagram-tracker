import Foundation
import SwiftUI

@MainActor
class AccountDetailViewModel: ObservableObject {
    @Published var snapshot: AccountSnapshot?
    @Published var history: [HistoryEntry] = []
    @Published var isLoading = false
    @Published var isCheckingNow = false
    @Published var error: String?

    let account: TrackedAccount

    init(account: TrackedAccount) {
        self.account = account
        // Varsa mevcut snapshot'ı kullan
        self.snapshot = account.latestSnapshot
    }

    func loadDetail() async {
        isLoading = true
        error = nil
        async let snapshotTask: AccountSnapshot? = {
            do { return try await APIService.shared.getSnapshot(accountId: account.id) }
            catch { return nil }
        }()
        async let historyTask: PaginatedHistory? = {
            do { return try await APIService.shared.getHistory(accountId: account.id) }
            catch { return nil }
        }()

        let (snap, hist) = await (snapshotTask, historyTask)
        if let snap { snapshot = snap }
        if let hist { history = hist.items }
        isLoading = false
    }

    func checkNow() async {
        isCheckingNow = true
        let prevTime = snapshot?.snapshottedAt
        do {
            try await APIService.shared.checkNow(accountId: account.id)
            // Yeni snapshot gelene kadar polling (max 40 saniye, 2s aralık)
            for _ in 0..<20 {
                try? await Task.sleep(nanoseconds: 2_000_000_000)
                if let newSnap = try? await APIService.shared.getSnapshot(accountId: account.id) {
                    if newSnap.snapshottedAt != prevTime {
                        snapshot = newSnap
                        // Geçmişi de arka planda güncelle
                        if let hist = try? await APIService.shared.getHistory(accountId: account.id) {
                            history = hist.items
                        }
                        break
                    }
                }
            }
        } catch {
            self.error = error.localizedDescription
        }
        isCheckingNow = false
    }

    // Takipçi grafiği için son 7 snapshot
    var followerChartData: [(Date, Int)] {
        // history'den takipçi sayılarını türetemiyoruz, snapshot tek nokta
        // Gerçek uygulamada multiple snapshot query gerekir
        // Şimdilik mevcut snapshot'ı göster
        guard let s = snapshot else { return [] }
        return [(s.snapshottedAt, s.followersCount)]
    }
}

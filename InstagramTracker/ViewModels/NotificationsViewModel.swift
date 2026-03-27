import Foundation
import SwiftUI

@MainActor
class NotificationsViewModel: ObservableObject {
    @Published var entries: [HistoryEntry] = []
    @Published var isLoading = false
    @Published var hasMore = false
    @Published var error: String?

    private var currentPage = 1

    func loadHistory() async {
        isLoading = true
        error = nil
        currentPage = 1
        do {
            let result = try await APIService.shared.getHistory(page: currentPage)
            entries = result.items
            hasMore = result.hasMore
        } catch {
            self.error = error.localizedDescription
        }
        isLoading = false
    }

    func loadMore() async {
        guard hasMore, !isLoading else { return }
        currentPage += 1
        do {
            let result = try await APIService.shared.getHistory(page: currentPage)
            entries.append(contentsOf: result.items)
            hasMore = result.hasMore
        } catch {
            self.error = error.localizedDescription
        }
    }

    func clearHistory() {
        entries = []
    }

    var todayCount: Int {
        let calendar = Calendar.current
        return entries.filter {
            calendar.isDateInToday($0.notification.sentAt)
        }.count
    }
}

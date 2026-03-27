import Foundation
import SwiftUI

@MainActor
class AccountsViewModel: ObservableObject {
    @Published var accounts: [TrackedAccount] = []
    @Published var isLoading = false
    @Published var error: String?

    func loadAccounts() async {
        isLoading = true
        error = nil
        do {
            accounts = try await APIService.shared.getAccounts()
        } catch {
            self.error = error.localizedDescription
        }
        isLoading = false
    }

    func addAccount(username: String, intervalHours: Int) async throws -> TrackedAccount {
        let account = try await APIService.shared.addAccount(username: username, intervalHours: intervalHours)
        accounts.insert(account, at: 0)
        return account
    }

    func deleteAccount(id: String) async {
        do {
            try await APIService.shared.deleteAccount(id: id)
            accounts.removeAll { $0.id == id }
        } catch {
            self.error = error.localizedDescription
        }
    }

    func deleteAccounts(at offsets: IndexSet) {
        let toDelete = offsets.map { accounts[$0] }
        Task {
            for acc in toDelete {
                await deleteAccount(id: acc.id)
            }
        }
    }
}

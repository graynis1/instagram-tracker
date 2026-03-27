import SwiftUI

struct AccountsListView: View {
    @StateObject private var vm = AccountsViewModel()
    @State private var showAddSheet = false

    var body: some View {
        NavigationStack {
            ZStack {
                Color.bgPage.ignoresSafeArea()

                if vm.isLoading && vm.accounts.isEmpty {
                    ProgressView()
                        .tint(.brandPurple)
                } else if vm.accounts.isEmpty {
                    EmptyStateView(
                        icon: "person.2",
                        title: "Henüz hesap eklenmedi",
                        description: "Takip etmek istediğin hesabı eklemek için + butonuna dokun"
                    )
                } else {
                    ScrollView {
                        LazyVStack(spacing: 10) {
                            ForEach(vm.accounts) { account in
                                NavigationLink(destination: AccountDetailView(account: account)) {
                                    AccountCardView(account: account)
                                        .contentShape(Rectangle())
                                }
                                .buttonStyle(.plain)
                                .swipeActions(edge: .trailing, allowsFullSwipe: true) {
                                    Button(role: .destructive) {
                                        Task { await vm.deleteAccount(id: account.id) }
                                    } label: {
                                        Label("Sil", systemImage: "trash")
                                    }
                                }
                            }
                        }
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                    }
                    .refreshable {
                        await vm.loadAccounts()
                    }
                }
            }
            .navigationTitle("Takip Listesi")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        showAddSheet = true
                    } label: {
                        ZStack {
                            Circle()
                                .fill(LinearGradient.brand)
                                .frame(width: 34, height: 34)
                            Image(systemName: "plus")
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(.white)
                        }
                    }
                }
            }
            .sheet(isPresented: $showAddSheet) {
                AddAccountView(vm: vm)
            }
        }
        .task {
            await vm.loadAccounts()
        }
    }
}

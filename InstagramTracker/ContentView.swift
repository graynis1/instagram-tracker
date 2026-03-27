import SwiftUI

struct ContentView: View {
    @State private var selectedTab = 0

    var body: some View {
        ZStack(alignment: .bottom) {
            Group {
                switch selectedTab {
                case 0: AccountsListView()
                case 1: HistoryView()
                case 2: SettingsView()
                default: AccountsListView()
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)

            CustomTabBar(selectedTab: $selectedTab)
        }
        .ignoresSafeArea(edges: .bottom)
    }
}

struct CustomTabBar: View {
    @Binding var selectedTab: Int

    private struct TabItem {
        let icon: String
        let activeIcon: String
        let label: String
    }

    private let items: [TabItem] = [
        .init(icon: "person.2",        activeIcon: "person.2.fill",        label: "Takip"),
        .init(icon: "bell",            activeIcon: "bell.fill",            label: "Bildirimler"),
        .init(icon: "gearshape",       activeIcon: "gearshape.fill",       label: "Ayarlar"),
    ]

    var body: some View {
        HStack(spacing: 0) {
            ForEach(Array(items.enumerated()), id: \.offset) { idx, item in
                Button {
                    withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                        selectedTab = idx
                    }
                } label: {
                    VStack(spacing: 4) {
                        ZStack {
                            if selectedTab == idx {
                                Circle()
                                    .fill(LinearGradient.brand.opacity(0.15))
                                    .frame(width: 36, height: 36)
                            }
                            Image(systemName: selectedTab == idx ? item.activeIcon : item.icon)
                                .font(.system(size: 20, weight: selectedTab == idx ? .semibold : .regular))
                                .foregroundStyle(
                                    selectedTab == idx
                                        ? AnyShapeStyle(LinearGradient.brand)
                                        : AnyShapeStyle(Color.textTertiary)
                                )
                        }
                        Text(item.label)
                            .font(.system(size: 10, weight: selectedTab == idx ? .semibold : .regular))
                            .foregroundColor(selectedTab == idx ? .brandPurple : .textTertiary)
                    }
                    .frame(maxWidth: .infinity)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.top, 10)
        .padding(.bottom, 28)
        .background(
            Color.bgCard
                .shadow(color: .black.opacity(0.08), radius: 12, x: 0, y: -4)
        )
    }
}

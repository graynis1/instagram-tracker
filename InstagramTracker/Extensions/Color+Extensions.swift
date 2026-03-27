import SwiftUI

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let r = Double((int >> 16) & 0xFF) / 255
        let g = Double((int >> 8)  & 0xFF) / 255
        let b = Double(int         & 0xFF) / 255
        self.init(red: r, green: g, blue: b)
    }

    static let brandPurple   = Color(hex: "A78BFA")
    static let brandPink     = Color(hex: "F472B6")
    static let bgPage        = Color(hex: "F7F8FC")
    static let bgCard        = Color(hex: "FFFFFF")
    static let bgPurpleTint  = Color(hex: "FAF5FF")
    static let bgPinkTint    = Color(hex: "FDF2F8")
    static let textPrimary   = Color(hex: "1C1C1E")
    static let textSecondary = Color(hex: "8E8E93")
    static let textTertiary  = Color(hex: "C7C7CC")
    static let statusGreen   = Color(hex: "15803D")
    static let bgGreen       = Color(hex: "F0FDF4")
    static let statusRed     = Color(hex: "BE123C")
    static let bgRed         = Color(hex: "FFF1F2")
}

extension LinearGradient {
    static let brand = LinearGradient(
        colors: [Color.brandPurple, Color.brandPink],
        startPoint: .topLeading, endPoint: .bottomTrailing
    )
    static let avatarA = LinearGradient(
        colors: [Color(hex: "A78BFA"), Color(hex: "7C3AED")],
        startPoint: .topLeading, endPoint: .bottomTrailing
    )
    static let avatarB = LinearGradient(
        colors: [Color(hex: "F472B6"), Color(hex: "BE185D")],
        startPoint: .topLeading, endPoint: .bottomTrailing
    )
    static let avatarC = LinearGradient(
        colors: [Color(hex: "67E8F9"), Color(hex: "2563EB")],
        startPoint: .topLeading, endPoint: .bottomTrailing
    )
    static let avatarD = LinearGradient(
        colors: [Color(hex: "A78BFA"), Color(hex: "F472B6")],
        startPoint: .topLeading, endPoint: .bottomTrailing
    )

    static func avatar(for username: String) -> LinearGradient {
        let all: [LinearGradient] = [.avatarA, .avatarB, .avatarC, .avatarD]
        return all[abs(username.hashValue) % all.count]
    }
}

// MARK: - Card Style

struct CardStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .background(Color.bgCard)
            .cornerRadius(20)
            .shadow(color: .black.opacity(0.06), radius: 8, x: 0, y: 2)
            .overlay(
                RoundedRectangle(cornerRadius: 20)
                    .stroke(Color.black.opacity(0.04), lineWidth: 0.5)
            )
    }
}

extension View {
    func cardStyle() -> some View { modifier(CardStyle()) }
}

// MARK: - Pill / Badge

extension View {
    func pillStyle(bg: Color, text: Color) -> some View {
        self
            .font(.system(size: 9, weight: .semibold))
            .padding(.vertical, 3)
            .padding(.horizontal, 9)
            .background(bg)
            .foregroundColor(text)
            .cornerRadius(20)
    }
}

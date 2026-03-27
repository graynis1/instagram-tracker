import SwiftUI

struct GradientAvatarView: View {
    let username: String
    let fullName: String?
    let size: CGFloat

    init(username: String, fullName: String? = nil, size: CGFloat = 38) {
        self.username = username
        self.fullName = fullName
        self.size = size
    }

    private var initials: String {
        if let name = fullName, !name.isEmpty {
            let parts = name.split(separator: " ")
            if parts.count >= 2 {
                return String(parts[0].prefix(1) + parts[1].prefix(1)).uppercased()
            }
            return String(name.prefix(2)).uppercased()
        }
        return String(username.prefix(2)).uppercased()
    }

    var body: some View {
        ZStack {
            Circle()
                .fill(LinearGradient.avatar(for: username))
                .frame(width: size, height: size)
            Text(initials)
                .font(.system(size: size * 0.35, weight: .bold))
                .foregroundColor(.white)
        }
    }
}

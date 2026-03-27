import SwiftUI

struct GradientButton: View {
    let title: String
    let isLoading: Bool
    let action: () async -> Void

    init(_ title: String, isLoading: Bool = false, action: @escaping () async -> Void) {
        self.title = title
        self.isLoading = isLoading
        self.action = action
    }

    var body: some View {
        Button {
            Task { await action() }
        } label: {
            ZStack {
                if isLoading {
                    ProgressView()
                        .tint(.white)
                } else {
                    Text(title)
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(.white)
                }
            }
            .frame(maxWidth: .infinity)
            .frame(height: 54)
            .background(LinearGradient.brand)
            .cornerRadius(16)
        }
        .disabled(isLoading)
    }
}

import SwiftUI

struct BrandToggleStyle: ToggleStyle {
    func makeBody(configuration: Configuration) -> some View {
        HStack {
            configuration.label
            Spacer()
            ZStack(alignment: configuration.isOn ? .trailing : .leading) {
                Capsule()
                    .fill(
                        configuration.isOn
                            ? AnyShapeStyle(LinearGradient.brand)
                            : AnyShapeStyle(Color(hex: "E5E5EA"))
                    )
                    .frame(width: 50, height: 30)
                Circle()
                    .fill(.white)
                    .frame(width: 24, height: 24)
                    .padding(3)
                    .shadow(color: .black.opacity(0.15), radius: 2, x: 0, y: 1)
            }
            .animation(.spring(response: 0.3, dampingFraction: 0.7), value: configuration.isOn)
            .onTapGesture { configuration.isOn.toggle() }
        }
    }
}

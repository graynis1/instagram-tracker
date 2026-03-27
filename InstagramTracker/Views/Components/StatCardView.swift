import SwiftUI

struct StatCardView: View {
    let label: String
    let value: String
    let change: Int?

    var body: some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.system(size: 20, weight: .bold))
                .foregroundColor(.textPrimary)
                .minimumScaleFactor(0.7)
                .lineLimit(1)
            Text(label.uppercased())
                .font(.system(size: 9, weight: .semibold))
                .foregroundColor(.textSecondary)
                .tracking(0.5)
            if let change, change != 0 {
                let isPositive = change > 0
                Text("\(isPositive ? "+" : "")\(change)")
                    .pillStyle(
                        bg: isPositive ? .bgGreen : .bgRed,
                        text: isPositive ? .statusGreen : .statusRed
                    )
            }
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 12)
        .background(Color.bgPage)
        .cornerRadius(10)
    }
}

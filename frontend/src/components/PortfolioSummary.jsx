import { useState, useEffect } from "react";

const CATEGORY_COLORS = {
  "Large Cap": "var(--color-primary-light)",
  "Flexi Cap": "var(--color-accent-lime)",
  "Mid Cap": "#fbbf24",
  "Small Cap": "var(--color-accent-orange)",
  "Balanced Advantage": "var(--color-text-main)",
  "Sectoral - Technology": "#38bdf8",
  "Debt - Gilt": "var(--color-text-muted)",
};

export default function PortfolioSummary() {
  const [portfolio, setPortfolio] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/portfolio")
      .then((r) => r.json())
      .then(setPortfolio)
      .catch(() => {});
  }, []);

  if (!portfolio) return (
    <div style={{ textAlign: "center", padding: 60, color: "var(--color-text-muted)", fontFamily: "var(--font-body)" }}>Loading portfolio...</div>
  );

  const totalInvested = portfolio.portfolio.reduce((s, f) => s + f.invested_amount, 0);
  const totalCurrent = portfolio.portfolio.reduce((s, f) => s + f.current_value, 0);
  const totalReturn = ((totalCurrent - totalInvested) / totalInvested) * 100;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      {/* Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
        {[
          { label: "Total Invested", value: `₹${(totalInvested / 100000).toFixed(1)}L`, color: "var(--color-text-muted)" },
          { label: "Current Value", value: `₹${(totalCurrent / 100000).toFixed(1)}L`, color: "var(--color-accent-lime)" },
          { label: "Total Returns", value: `+${totalReturn.toFixed(1)}%`, color: "var(--color-accent-lime)" },
          { label: "Total Funds", value: portfolio.portfolio.length, color: "var(--color-primary-light)" },
        ].map((stat, i) => (
          <div key={i} className="rs-card">
            <div className="rs-card-body">
              <div style={{ fontSize: 12, color: "var(--color-text-muted)", marginBottom: 8, fontFamily: "var(--font-heading)", letterSpacing: "0.05em" }}>{stat.label}</div>
              <div style={{ fontSize: 24, fontWeight: 700, color: stat.color }}>{stat.value}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Investor profile */}
      <div className="rs-card">
        <div className="rs-card-header">
          <div style={{ fontSize: 12, color: "var(--color-text-muted)", fontWeight: 700, letterSpacing: "0.05em", fontFamily: "var(--font-heading)" }}>
            INVESTOR PROFILE
          </div>
        </div>
        <div className="rs-card-body">
          <div style={{ display: "flex", gap: 40, flexWrap: "wrap" }}>
            {[
              { label: "Age", value: `${portfolio.age} years` },
              { label: "Risk Profile", value: portfolio.risk_profile },
              { label: "Goals", value: portfolio.goals.join(", ") },
              { label: "Horizon", value: `${portfolio.investment_horizon_years} years` },
            ].map((item, i) => (
              <div key={i}>
                <div style={{ fontSize: 12, color: "var(--color-text-muted)", marginBottom: 4 }}>{item.label}</div>
                <div style={{ fontSize: 15, fontWeight: 600, color: "var(--color-text-main)", textTransform: "capitalize" }}>{item.value}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Fund list */}
      <div className="rs-card">
        <div className="rs-card-header">
          <div style={{ fontSize: 12, color: "var(--color-text-muted)", fontWeight: 700, letterSpacing: "0.05em", fontFamily: "var(--font-heading)" }}>
            HOLDINGS
          </div>
        </div>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ backgroundColor: "var(--color-bg-input)" }}>
              {["Fund", "Category", "Allocation", "Invested", "Current", "Return"].map((h) => (
                <th key={h} style={{ padding: "14px 24px", textAlign: "left", fontSize: 12, color: "var(--color-text-muted)", fontWeight: 700, fontFamily: "var(--font-heading)" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {portfolio.portfolio.map((fund, i) => {
              const ret = ((fund.current_value - fund.invested_amount) / fund.invested_amount) * 100;
              const catColor = CATEGORY_COLORS[fund.category] || "var(--color-text-muted)";
              return (
                <tr key={i} style={{ borderTop: "1px solid var(--color-border)" }}>
                  <td style={{ padding: "16px 24px", fontSize: 14, fontWeight: 600, color: "var(--color-text-main)" }}>{fund.fund_name}</td>
                  <td style={{ padding: "16px 24px" }}>
                    <span style={{
                      fontSize: 11, padding: "4px 10px", borderRadius: 6,
                      backgroundColor: "var(--color-bg-input)", color: catColor, fontWeight: 700,
                      border: `1px solid ${catColor}44`
                    }}>
                      {fund.category}
                    </span>
                  </td>
                  <td style={{ padding: "16px 24px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                      <div style={{ width: 80, height: 6, backgroundColor: "var(--color-bg-input)", borderRadius: 3, overflow: "hidden" }}>
                        <div style={{ width: `${fund.allocation_percent * (80 / 25)}px`, maxWidth: "100%", height: "100%", backgroundColor: catColor, borderRadius: 3 }} />
                      </div>
                      <span style={{ fontSize: 13, color: "var(--color-text-muted)", fontWeight: 600 }}>{fund.allocation_percent}%</span>
                    </div>
                  </td>
                  <td style={{ padding: "16px 24px", fontSize: 13, color: "var(--color-text-muted)" }}>₹{(fund.invested_amount / 1000).toFixed(0)}K</td>
                  <td style={{ padding: "16px 24px", fontSize: 13, color: "var(--color-text-main)", fontWeight: 600 }}>₹{(fund.current_value / 1000).toFixed(0)}K</td>
                  <td style={{ padding: "16px 24px", fontSize: 13, fontWeight: 700, color: ret >= 0 ? "var(--color-accent-lime)" : "var(--color-accent-orange)" }}>
                    {ret > 0 ? "+" : ""}{ret.toFixed(1)}%
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

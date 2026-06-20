function ConfidenceDial({ score }) {
  const pct = Math.round(score * 100);
  const color = pct >= 75 ? "var(--color-accent-lime)" : pct >= 55 ? "#fbbf24" : "var(--color-accent-orange)";
  const label = pct >= 75 ? "High Confidence" : pct >= 55 ? "Moderate Confidence" : "Low Confidence";

  // SVG arc
  const r = 54;
  const circumference = Math.PI * r;
  const offset = circumference * (1 - pct / 100);

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
      <svg width={140} height={80} viewBox="0 0 140 80">
        {/* Track */}
        <path
          d="M 14 70 A 56 56 0 0 1 126 70"
          fill="none" stroke="var(--color-bg-input)" strokeWidth={10} strokeLinecap="round"
        />
        {/* Progress */}
        <path
          d="M 14 70 A 56 56 0 0 1 126 70"
          fill="none" stroke={color} strokeWidth={10} strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 1.5s ease" }}
        />
        <text x="70" y="65" textAnchor="middle" fill={color} fontSize={24} fontWeight={700} fontFamily="var(--font-heading)">{pct}%</text>
      </svg>
      <span style={{ fontSize: 13, color, fontWeight: 700, fontFamily: "var(--font-heading)" }}>{label}</span>
    </div>
  );
}

export default function FinalVerdict({ result }) {
  if (!result) return null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      {/* Top row: confidence + recommendation */}
      <div style={{ display: "grid", gridTemplateColumns: "240px 1fr", gap: 20 }}>
        {/* Confidence */}
        <div className="rs-card">
          <div className="rs-card-body" style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12, height: "100%", justifyContent: "center" }}>
            <div style={{ fontSize: 12, color: "var(--color-text-muted)", fontWeight: 700, letterSpacing: "0.05em", fontFamily: "var(--font-heading)" }}>CONFIDENCE</div>
            <ConfidenceDial score={result.confidence_score} />
          </div>
        </div>

        {/* Final recommendation */}
        <div className="rs-card" style={{ borderLeft: "6px solid var(--color-accent-lime)" }}>
          <div className="rs-card-body">
            <div style={{ fontSize: 12, color: "var(--color-text-muted)", fontWeight: 700, letterSpacing: "0.05em", marginBottom: 16, fontFamily: "var(--font-heading)" }}>
              FINAL RECOMMENDATION
            </div>
            <p style={{ fontSize: 16, lineHeight: 1.7, color: "var(--color-text-main)", margin: 0, fontWeight: 400 }}>
              {result.final_recommendation}
            </p>
          </div>
        </div>
      </div>

      {/* Action items */}
      {result.action_items?.length > 0 && (
        <div className="rs-card">
          <div className="rs-card-body">
            <div style={{ fontSize: 12, color: "var(--color-text-muted)", fontWeight: 700, letterSpacing: "0.05em", marginBottom: 16, fontFamily: "var(--font-heading)" }}>
              ACTION ITEMS
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {result.action_items.map((item, i) => (
                <div key={i} style={{ display: "flex", gap: 16, alignItems: "flex-start" }}>
                  <div style={{
                    minWidth: 28, height: 28, borderRadius: "50%", backgroundColor: "var(--color-primary-light)",
                    display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, color: "#fff", fontWeight: 700
                  }}>
                    {i + 1}
                  </div>
                  <span style={{ fontSize: 14, color: "var(--color-text-main)", lineHeight: 1.6, marginTop: 2 }}>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Agreements & Disagreements */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        <div className="rs-card" style={{ borderTop: "4px solid var(--color-accent-lime)" }}>
          <div className="rs-card-body">
            <div style={{ fontSize: 12, color: "var(--color-accent-lime)", fontWeight: 700, letterSpacing: "0.05em", marginBottom: 16, fontFamily: "var(--font-heading)" }}>
              ✓ COMMITTEE AGREEMENTS
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {result.agreements?.map((a, i) => (
                <div key={i} style={{ fontSize: 13, color: "var(--color-text-main)", lineHeight: 1.6, paddingLeft: 16, borderLeft: "3px solid var(--color-accent-lime-muted)" }}>
                  {a}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="rs-card" style={{ borderTop: "4px solid var(--color-accent-orange)" }}>
          <div className="rs-card-body">
            <div style={{ fontSize: 12, color: "var(--color-accent-orange)", fontWeight: 700, letterSpacing: "0.05em", marginBottom: 16, fontFamily: "var(--font-heading)" }}>
              ✗ COMMITTEE DISAGREEMENTS
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {result.disagreements?.map((d, i) => (
                <div key={i} style={{ fontSize: 13, color: "var(--color-text-main)", lineHeight: 1.6, paddingLeft: 16, borderLeft: "3px solid rgba(251, 146, 60, 0.2)" }}>
                  {d}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Risk warnings */}
      {result.risk_warnings?.length > 0 && (
        <div className="rs-card" style={{ borderLeft: "4px solid #ef4444" }}>
          <div className="rs-card-body">
            <div style={{ fontSize: 12, color: "#ef4444", fontWeight: 700, letterSpacing: "0.05em", marginBottom: 16, fontFamily: "var(--font-heading)" }}>
              ⚠ RISK WARNINGS
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {result.risk_warnings.map((w, i) => (
                <div key={i} style={{ fontSize: 13, color: "#fca5a5", lineHeight: 1.6, display: "flex", gap: 12 }}>
                  <span style={{ color: "#ef4444" }}>•</span><span>{w}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Evidence */}
      {result.evidence?.length > 0 && (
        <div className="rs-card">
          <div className="rs-card-body">
            <div style={{ fontSize: 12, color: "var(--color-text-muted)", fontWeight: 700, letterSpacing: "0.05em", marginBottom: 16, fontFamily: "var(--font-heading)" }}>
              EVIDENCE BASE
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
              {result.evidence.map((e, i) => (
                <span key={i} style={{
                  fontSize: 12, padding: "6px 14px", borderRadius: 8,
                  backgroundColor: "var(--color-bg-input)", color: "var(--color-text-muted)", border: "1px solid var(--color-border)"
                }}>
                  {e}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

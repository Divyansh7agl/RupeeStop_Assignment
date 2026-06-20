const ADVISOR_CONFIG = {
  conservative: {
    label: "Conservative Advisor",
    icon: "🛡️",
    color: "var(--color-text-main)",
    bg: "var(--color-bg-surface)",
    border: "var(--color-border)",
    desc: "Capital Preservation Focus"
  },
  growth: {
    label: "Growth Advisor",
    icon: "🚀",
    color: "var(--color-text-main)",
    bg: "var(--color-bg-surface)",
    border: "var(--color-border)",
    desc: "Long-term Returns Focus"
  },
  cost_efficiency: {
    label: "Cost & Efficiency Advisor",
    icon: "📊",
    color: "var(--color-text-main)",
    bg: "var(--color-bg-surface)",
    border: "var(--color-border)",
    desc: "Portfolio Simplicity Focus"
  },
  devils_advocate: {
    label: "Devil's Advocate",
    icon: "😈",
    color: "var(--color-text-main)",
    bg: "var(--color-bg-surface)",
    border: "var(--color-border)",
    desc: "Challenge & Risk Focus"
  },
};

const STANCE_COLORS = {
  BUY: "var(--color-accent-lime)",
  HOLD: "var(--color-text-main)",
  SELL: "var(--color-accent-orange)",
  RESTRUCTURE: "var(--color-primary-light)",
  CAUTION: "#fbbf24",
};

function ConfidenceBar({ value }) {
  const pct = Math.round(value * 100);
  const color = pct >= 75 ? "var(--color-accent-lime)" : pct >= 50 ? "#fbbf24" : "var(--color-accent-orange)";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <div style={{ flex: 1, height: 6, background: "var(--color-bg-input)", borderRadius: 3, overflow: "hidden" }}>
        <div style={{
          width: `${pct}%`, height: "100%",
          backgroundColor: color, borderRadius: 3,
          transition: "width 1s ease"
        }} />
      </div>
      <span style={{ fontSize: 13, color, fontWeight: 700, minWidth: 36, fontFamily: "var(--font-heading)" }}>{pct}%</span>
    </div>
  );
}

function AdvisorCard({ type, opinion }) {
  const config = ADVISOR_CONFIG[type];

  return (
    <div className="rs-card" style={{
      borderTop: `4px solid ${config.color === 'var(--color-text-main)' ? 'var(--color-primary-light)' : config.color}`
    }}>
      <div className="rs-card-body">
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span style={{ fontSize: 26, background: "var(--color-bg-input)", padding: 8, borderRadius: 8 }}>{config.icon}</span>
            <div>
              <div style={{ fontWeight: 700, fontSize: 15, color: config.color, fontFamily: "var(--font-heading)" }}>{config.label}</div>
              <div style={{ fontSize: 12, color: "var(--color-text-muted)" }}>{config.desc}</div>
            </div>
          </div>
          {opinion?.stance && (
            <span style={{
              fontSize: 12, fontWeight: 700, padding: "6px 14px", borderRadius: 20,
              backgroundColor: "var(--color-bg-input)",
              color: STANCE_COLORS[opinion.stance] || "var(--color-text-main)",
              border: `1px solid ${STANCE_COLORS[opinion.stance] || "var(--color-border)"}`
            }}>
              {opinion.stance}
            </span>
          )}
        </div>

        {opinion ? (
          <>
            {/* Confidence */}
            <div style={{ marginBottom: 18 }}>
              <div style={{ fontSize: 11, color: "var(--color-text-muted)", marginBottom: 8, fontWeight: 700, letterSpacing: "0.05em" }}>CONFIDENCE</div>
              <ConfidenceBar value={opinion.confidence} />
            </div>

            {/* Reasoning */}
            <div style={{ marginBottom: 18 }}>
              <div style={{ fontSize: 11, color: "var(--color-text-muted)", marginBottom: 8, fontWeight: 700, letterSpacing: "0.05em" }}>ANALYSIS</div>
              <p style={{ fontSize: 14, lineHeight: 1.6, color: "var(--color-text-main)", margin: 0 }}>
                {opinion.reasoning}
              </p>
            </div>

            {/* Key Points */}
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 11, color: "var(--color-text-muted)", marginBottom: 10, fontWeight: 700, letterSpacing: "0.05em" }}>KEY POINTS</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {opinion.key_points?.map((point, i) => (
                  <div key={i} style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
                    <span style={{ color: "var(--color-accent-lime)", fontSize: 14, marginTop: 1, flexShrink: 0 }}>▸</span>
                    <span style={{ fontSize: 13, color: "var(--color-text-main)", lineHeight: 1.5 }}>{point}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Evidence */}
            {opinion.evidence_used?.length > 0 && (
              <div>
                <div style={{ fontSize: 11, color: "var(--color-text-muted)", marginBottom: 8, fontWeight: 700, letterSpacing: "0.05em" }}>EVIDENCE USED</div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {opinion.evidence_used.map((e, i) => (
                    <span key={i} style={{
                      fontSize: 11, padding: "4px 10px", borderRadius: 6,
                      backgroundColor: "var(--color-bg-input)", color: "var(--color-text-muted)", border: "1px solid var(--color-border)"
                    }}>
                      {e.length > 40 ? e.slice(0, 37) + "..." : e}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : (
          <div style={{ textAlign: "center", padding: "40px 0", color: "var(--color-text-muted)" }}>
            Awaiting analysis...
          </div>
        )}
      </div>
    </div>
  );
}

export default function CommitteeOpinions({ opinions }) {
  return (
    <div>
      <div style={{ fontSize: 13, color: "var(--color-text-muted)", fontWeight: 700, marginBottom: 20, letterSpacing: "0.05em", fontFamily: "var(--font-heading)" }}>
        COMMITTEE DEBATE — {Object.keys(opinions).length} ADVISORS
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 20 }}>
        {Object.entries(opinions).map(([type, opinion]) => (
          <AdvisorCard key={type} type={type} opinion={opinion} />
        ))}
      </div>
    </div>
  );
}

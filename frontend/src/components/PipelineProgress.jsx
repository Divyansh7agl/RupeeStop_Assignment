const STEP_ICONS = {
  load_profile: "👤",
  planner: "🧠",
  tool_execution: "🔧",
  specialists_parallel: "⚡",
  devils_advocate: "😈",
  consensus: "⚖️",
  pipeline_complete: "✅",
};

const STEP_COLORS = {
  pending: "var(--color-text-muted)",
  running: "var(--color-accent-lime)",
  completed: "var(--color-primary-light)",
  failed: "#ef4444",
};

export default function PipelineProgress({ steps, isRunning }) {
  return (
    <div className="rs-card">
      <div className="rs-card-body">
        <div style={{ fontSize: 12, color: "var(--color-text-muted)", fontWeight: 700, marginBottom: 20, letterSpacing: "0.05em", fontFamily: "var(--font-heading)" }}>
          PIPELINE EXECUTION
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 0, overflowX: "auto", paddingBottom: 4 }}>
          {steps.map((step, i) => (
            <div key={step.id} style={{ display: "flex", alignItems: "center", flex: i < steps.length - 1 ? 1 : 0 }}>
              {/* Step node */}
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", minWidth: 90 }}>
                <div style={{
                  width: 46, height: 46, borderRadius: "50%",
                  backgroundColor: step.status === "completed" ? "var(--color-bg-base)"
                    : step.status === "running" ? "var(--color-bg-surface-hover)"
                    : "var(--color-bg-input)",
                  border: `2px solid ${STEP_COLORS[step.status] || "var(--color-border)"}`,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 20, position: "relative",
                  boxShadow: step.status === "running" ? `0 0 16px ${STEP_COLORS.running}33` : "none",
                  transition: "all 0.3s"
                }}>
                  {step.status === "running" ? (
                    <span style={{ animation: "spin 1.5s linear infinite", display: "inline-block" }}>⟳</span>
                  ) : STEP_ICONS[step.id]}
                </div>
                <div style={{
                  fontSize: 11, marginTop: 8, textAlign: "center",
                  color: step.status === "completed" ? "var(--color-text-main)"
                    : step.status === "running" ? "var(--color-accent-lime)"
                    : "var(--color-text-muted)",
                  fontWeight: step.status !== "pending" ? 600 : 400,
                  maxWidth: 80, lineHeight: 1.3
                }}>
                  {step.label}
                </div>
                {step.status === "running" && step.details && (
                  <div style={{ fontSize: 10, color: "var(--color-text-muted)", textAlign: "center", maxWidth: 90, marginTop: 4 }}>
                    {step.details.slice(0, 35)}...
                  </div>
                )}
              </div>

              {/* Connector line */}
              {i < steps.length - 1 && (
                <div style={{
                  flex: 1, height: 2, minWidth: 16,
                  background: step.status === "completed"
                    ? "linear-gradient(90deg, var(--color-primary-light), var(--color-accent-lime))"
                    : "var(--color-border)",
                  transition: "background 0.5s",
                  marginBottom: 28
                }} />
              )}
            </div>
          ))}
        </div>
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}

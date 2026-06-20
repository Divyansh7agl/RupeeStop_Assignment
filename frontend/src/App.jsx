import { useState, useRef } from "react";
import PipelineProgress from "./components/PipelineProgress";
import CommitteeOpinions from "./components/CommitteeOpinions";
import FinalVerdict from "./components/FinalVerdict";
import PortfolioSummary from "./components/PortfolioSummary";

const SAMPLE_QUESTIONS = [
  "Should I redeem my small cap fund given current market volatility?",
  "Am I over-diversified with 8 funds in my portfolio?",
  "Is my portfolio allocation consistent with my age and moderate risk profile?",
  "Why might my portfolio be more volatile than expected?",
  "Should I consolidate my two large cap funds into one?",
];

const API_BASE = "http://localhost:8000";

export default function App() {
  const [question, setQuestion] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [pipelineSteps, setPipelineSteps] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("committee");
  const [provider, setProvider] = useState("gemini");
  const abortRef = useRef(null);

  const runAnalysis = async () => {
    if (!question.trim()) return;
    setIsRunning(true);
    setResult(null);
    setError(null);
    setPipelineSteps([]);

    const STEPS = [
      { id: "load_profile", label: "Loading Portfolio" },
      { id: "planner", label: "Planner Agent" },
      { id: "tool_execution", label: "Running Tools" },
      { id: "specialists_parallel", label: "Specialist Advisors" },
      { id: "devils_advocate", label: "Devil's Advocate" },
      { id: "consensus", label: "Consensus Agent" },
      { id: "pipeline_complete", label: "Complete" },
    ];

    setPipelineSteps(STEPS.map((s) => ({ ...s, status: "pending", details: "" })));

    try {
      const res = await fetch(`${API_BASE}/analyze/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, use_sample_data: true, provider }),
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      abortRef.current = reader;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        const lines = text.split("\n").filter((l) => l.startsWith("data: "));

        for (const line of lines) {
          try {
            const event = JSON.parse(line.slice(6));

            if (event.type === "step_update") {
              setPipelineSteps((prev) =>
                prev.map((s) =>
                  s.id === event.step
                    ? { ...s, status: event.status, details: event.message }
                    : s
                )
              );
            } else if (event.type === "final_result") {
              setResult(event.data);
              setActiveTab("committee");
            } else if (event.type === "error") {
              setError(event.message);
            }
          } catch {}
        }
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="app-container" style={{ minHeight: "100vh", paddingBottom: "60px" }}>
      {/* Header */}
      <header style={{ 
        borderBottom: "1px solid var(--color-border)", 
        padding: "20px 40px", 
        display: "flex", 
        alignItems: "center", 
        gap: 16,
        backgroundColor: "var(--color-bg-surface)"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{
            width: 40, height: 40, borderRadius: 8,
            backgroundColor: "var(--color-accent-lime)",
            color: "var(--color-bg-base)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 20, fontWeight: "bold"
          }}>
            ₹
          </div>
          <div>
            <div style={{ fontWeight: 800, fontSize: 18, fontFamily: "var(--font-heading)", letterSpacing: "-0.5px" }}>Rupeestop</div>
            <div style={{ fontSize: 12, color: "var(--color-text-muted)", fontFamily: "var(--font-body)" }}>Investment Committee AI</div>
          </div>
        </div>
        <div style={{ marginLeft: "auto", display: "flex", gap: 16, alignItems: "center" }}>
          <label style={{ display: "flex", alignItems: "center", gap: 6, cursor: "pointer", fontSize: 12, fontWeight: 700, color: provider === "gemini" ? "var(--color-text-main)" : "var(--color-text-muted)" }}>
            <input type="radio" value="gemini" checked={provider === "gemini"} onChange={(e) => setProvider(e.target.value)} style={{ accentColor: "var(--color-primary-light)" }} />
            Gemini 2.0 Flash
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: 6, cursor: "pointer", fontSize: 12, fontWeight: 700, color: provider === "groq" ? "var(--color-accent-lime)" : "var(--color-text-muted)" }}>
            <input type="radio" value="groq" checked={provider === "groq"} onChange={(e) => setProvider(e.target.value)} style={{ accentColor: "var(--color-accent-lime)" }} />
            Groq (Llama-3.3-70b)
          </label>
        </div>
      </header>

      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "40px 24px" }}>
        {/* Query Input */}
        <div style={{ marginBottom: 40 }}>
          <div style={{ 
            fontSize: 14, 
            color: "var(--color-text-muted)", 
            marginBottom: 12, 
            fontWeight: 700,
            fontFamily: "var(--font-heading)",
            textTransform: "uppercase",
            letterSpacing: "1px"
          }}>
            Ask The Committee
          </div>
          <div style={{ display: "flex", gap: 16 }}>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g. Should I redeem my small cap fund? Am I over-diversified?"
              rows={2}
              style={{
                flex: 1, 
                backgroundColor: "var(--color-bg-input)", 
                border: "1px solid var(--color-border)",
                borderRadius: 8, 
                padding: "16px 20px", 
                color: "var(--color-text-main)",
                fontSize: 15, 
                resize: "none", 
                outline: "none",
                fontFamily: "var(--font-body)", 
                lineHeight: 1.5,
                transition: "border-color 0.2s"
              }}
              onFocus={(e) => e.target.style.borderColor = "var(--color-border-active)"}
              onBlur={(e) => e.target.style.borderColor = "var(--color-border)"}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); runAnalysis(); } }}
            />
            <button
              className="rs-btn-primary"
              onClick={runAnalysis}
              disabled={isRunning || !question.trim()}
              style={{ minWidth: 140, fontSize: 16 }}
            >
              {isRunning ? "Analyzing..." : "Analyze →"}
            </button>
          </div>

          {/* Sample questions */}
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 16 }}>
            {SAMPLE_QUESTIONS.map((q, i) => (
              <button
                key={i}
                className="rs-btn-outline"
                onClick={() => setQuestion(q)}
                style={{ fontSize: 12 }}
              >
                {q.length > 65 ? q.slice(0, 62) + "..." : q}
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="rs-card" style={{ borderLeft: "4px solid #ef4444", padding: "16px 20px", marginBottom: 32, color: "#fca5a5" }}>
            ⚠️ {error}
          </div>
        )}

        {/* Pipeline Progress */}
        {pipelineSteps.length > 0 && (
          <div style={{ marginBottom: 40 }}>
            <PipelineProgress steps={pipelineSteps} isRunning={isRunning} />
          </div>
        )}

        {/* Results */}
        {result && (
          <div>
            {/* Tabs */}
            <div className="rs-tabs">
              {[
                { id: "committee", label: "Committee Opinions" },
                { id: "verdict", label: "Final Verdict" },
                { id: "portfolio", label: "Portfolio Analysis" },
              ].map((tab) => (
                <button
                  key={tab.id}
                  className={`rs-tab ${activeTab === tab.id ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            <div style={{ marginTop: 24 }}>
              {activeTab === "committee" && <CommitteeOpinions opinions={result.committee_opinions} />}
              {activeTab === "verdict" && <FinalVerdict result={result} />}
              {activeTab === "portfolio" && <PortfolioSummary />}
            </div>
          </div>
        )}

        {!result && !isRunning && pipelineSteps.length === 0 && (
          <div style={{ textAlign: "center", padding: "100px 0", color: "var(--color-text-muted)" }}>
            <div style={{ fontSize: 56, marginBottom: 24, opacity: 0.8 }}>₹</div>
            <div style={{ fontSize: 24, fontWeight: 700, fontFamily: "var(--font-heading)", marginBottom: 12, color: "var(--color-text-main)" }}>
              Investment Committee Ready
            </div>
            <div style={{ fontSize: 16, fontFamily: "var(--font-body)", maxWidth: 500, margin: "0 auto" }}>
              4 AI advisors will debate your question, analyze market data, and reach a consensus recommendation.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

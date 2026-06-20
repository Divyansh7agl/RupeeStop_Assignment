"""
Investment Committee Agents.
Each agent has a distinct persona, system prompt, and reasoning focus.
All run in parallel via asyncio.gather for real multi-agent orchestration.
"""

import json
import time
import asyncio
import structlog
from typing import Dict, Any

from models.schemas import AdvisorOpinion, InvestorProfile
from agents.llm_client import LLMClient

logger = structlog.get_logger(__name__)


# ─────────────────────────────────────────────
# BASE AGENT
# ─────────────────────────────────────────────

class BaseAgent:
    def __init__(self, llm: LLMClient, name: str):
        self.llm = llm
        self.name = name

    def _build_context(self, question: str, tool_outputs: Dict[str, Any], profile: InvestorProfile) -> str:
        return f"""
INVESTOR PROFILE:
- Age: {profile.age} years
- Risk Profile: {profile.risk_profile}
- Goals: {', '.join(profile.goals)}
- Investment Horizon: {profile.investment_horizon_years} years

QUESTION FROM INVESTOR:
{question}

TOOL DATA GATHERED:
{json.dumps(tool_outputs, indent=2, default=str)}

Based on the above data, provide your expert opinion.
"""

    async def analyze(self, question: str, tool_outputs: Dict[str, Any], profile: InvestorProfile, provider: str = "gemini") -> AdvisorOpinion:
        raise NotImplementedError


# ─────────────────────────────────────────────
# AGENT 1: Conservative Advisor
# ─────────────────────────────────────────────

class ConservativeAdvisor(BaseAgent):
    SYSTEM_PROMPT = """You are a Conservative Investment Advisor on an investment committee.
Your primary focus: CAPITAL PRESERVATION above all else.

Your philosophy:
- Protect the downside before chasing the upside
- Diversification is the only free lunch in investing
- Volatility is the enemy of compounding
- Debt allocation matters, especially as investors approach goals

When analyzing portfolios, you always prioritize:
1. Maximum drawdown risk
2. Debt/equity balance appropriate to age
3. Concentration risk (single fund or sector overexposure)
4. Downside scenarios — what happens in a bear market?

You must respond in this EXACT JSON format:
{
  "advisor": "Conservative Advisor",
  "stance": "<one of: BUY / HOLD / SELL / RESTRUCTURE / CAUTION>",
  "confidence": <float between 0.0 and 1.0>,
  "reasoning": "<2-3 sentences explaining your core concern or approval>",
  "key_points": ["<point 1>", "<point 2>", "<point 3>"],
  "evidence_used": ["<tool or data point you relied on>", ...]
}

Be specific. Reference actual numbers from the tool data. No generic advice."""

    def __init__(self, llm: LLMClient):
        super().__init__(llm, "Conservative Advisor")

    async def analyze(self, question: str, tool_outputs: Dict, profile: InvestorProfile, provider: str = "gemini") -> AdvisorOpinion:
        start = time.time()
        logger.info("agent.conservative.start")

        context = self._build_context(question, tool_outputs, profile)
        result = await self.llm.complete_json(self.SYSTEM_PROMPT, context, temperature=0.25, provider=provider)

        logger.info("agent.conservative.complete", duration_ms=round((time.time() - start) * 1000, 2))
        return AdvisorOpinion(**result)


# ─────────────────────────────────────────────
# AGENT 2: Growth Advisor
# ─────────────────────────────────────────────

class GrowthAdvisor(BaseAgent):
    SYSTEM_PROMPT = """You are a Growth-Oriented Investment Advisor on an investment committee.
Your primary focus: MAXIMIZING LONG-TERM WEALTH CREATION.

Your philosophy:
- Time in the market beats timing the market
- Volatility is not risk — permanent capital loss is risk
- Young investors should embrace higher equity allocation
- Mid and small caps create generational wealth over 15-20 year horizons
- Inflation is the silent killer — real returns matter

When analyzing portfolios, you prioritize:
1. Long-term CAGR potential vs benchmark
2. Whether equity allocation is bold enough for the horizon
3. Alpha generation — are the funds beating their benchmarks?
4. Missed opportunities — what upside is the investor leaving on the table?

You must respond in this EXACT JSON format:
{
  "advisor": "Growth Advisor",
  "stance": "<one of: BUY / HOLD / SELL / RESTRUCTURE / CAUTION>",
  "confidence": <float between 0.0 and 1.0>,
  "reasoning": "<2-3 sentences explaining your growth thesis or concern>",
  "key_points": ["<point 1>", "<point 2>", "<point 3>"],
  "evidence_used": ["<tool or data point you relied on>", ...]
}

Be bold. Reference CAGR numbers, alpha, benchmark comparisons from the data."""

    def __init__(self, llm: LLMClient):
        super().__init__(llm, "Growth Advisor")

    async def analyze(self, question: str, tool_outputs: Dict, profile: InvestorProfile, provider: str = "gemini") -> AdvisorOpinion:
        start = time.time()
        logger.info("agent.growth.start")

        context = self._build_context(question, tool_outputs, profile)
        result = await self.llm.complete_json(self.SYSTEM_PROMPT, context, temperature=0.35, provider=provider)

        logger.info("agent.growth.complete", duration_ms=round((time.time() - start) * 1000, 2))
        return AdvisorOpinion(**result)


# ─────────────────────────────────────────────
# AGENT 3: Cost & Efficiency Advisor
# ─────────────────────────────────────────────

class CostEfficiencyAdvisor(BaseAgent):
    SYSTEM_PROMPT = """You are a Cost & Efficiency Advisor on an investment committee.
Your primary focus: PORTFOLIO SIMPLICITY, LOW COST, ZERO OVERLAP.

Your philosophy:
- Every basis point of expense ratio compounds against the investor
- Owning 2 large cap funds = paying twice for the same stocks
- More funds = more complexity, not more diversification
- A 3-fund portfolio can beat a 10-fund portfolio after costs
- Overlap analysis reveals hidden concentration that allocation percentages hide

When analyzing portfolios, you scrutinize:
1. Expense ratios — are they paying too much for active management?
2. Fund overlap — which funds hold the same underlying stocks?
3. Number of funds — is this portfolio unnecessarily complex?
4. Direct vs regular plans (cost efficiency)
5. Are there funds serving the same purpose?

You must respond in this EXACT JSON format:
{
  "advisor": "Cost & Efficiency Advisor",
  "stance": "<one of: BUY / HOLD / SELL / RESTRUCTURE / CAUTION>",
  "confidence": <float between 0.0 and 1.0>,
  "reasoning": "<2-3 sentences about cost inefficiencies or portfolio bloat>",
  "key_points": ["<point 1>", "<point 2>", "<point 3>"],
  "evidence_used": ["<tool or data point you relied on>", ...]
}

Be specific about expense ratios, overlap, and fund consolidation opportunities."""

    def __init__(self, llm: LLMClient):
        super().__init__(llm, "Cost & Efficiency Advisor")

    async def analyze(self, question: str, tool_outputs: Dict, profile: InvestorProfile, provider: str = "gemini") -> AdvisorOpinion:
        start = time.time()
        logger.info("agent.cost_efficiency.start")

        context = self._build_context(question, tool_outputs, profile)
        result = await self.llm.complete_json(self.SYSTEM_PROMPT, context, temperature=0.25, provider=provider)

        logger.info("agent.cost_efficiency.complete", duration_ms=round((time.time() - start) * 1000, 2))
        return AdvisorOpinion(**result)


# ─────────────────────────────────────────────
# AGENT 4: Devil's Advocate
# ─────────────────────────────────────────────

class DevilsAdvocate(BaseAgent):
    SYSTEM_PROMPT = """You are the Devil's Advocate on an investment committee.
Your purpose: CHALLENGE EVERY ASSUMPTION. Protect the investor from overconfident advice.

You have access to all three other advisors' opinions. Your job is NOT to agree — it is to ask the hard questions they missed, expose hidden risks, and stress-test their recommendations.

Your philosophy:
- Every recommendation has a failure scenario — find it
- Past performance does NOT guarantee future results
- Market conditions can invalidate even well-reasoned advice
- Behavioural risk is real — can the investor actually hold through a 40% drawdown?
- What are the second and third-order consequences of this recommendation?

When reviewing others' opinions, challenge:
1. What assumptions are they making that could be wrong?
2. What risks have they NOT accounted for?
3. What is the bear case for their recommendation?
4. What would make this advice catastrophically fail?
5. Are there conflicts of interest or biases in the recommendations?

You must respond in this EXACT JSON format:
{
  "advisor": "Devil's Advocate",
  "stance": "<one of: BUY / HOLD / SELL / RESTRUCTURE / CAUTION>",
  "confidence": <float between 0.0 and 1.0>,
  "reasoning": "<2-3 sentences identifying the key risk or flaw in current thinking>",
  "key_points": ["<challenge 1>", "<challenge 2>", "<challenge 3>"],
  "evidence_used": ["<what you referenced to form this challenge>", ...]
}

Be contrarian. Be specific. Reference exact claims from the other advisors' opinions."""

    def __init__(self, llm: LLMClient):
        super().__init__(llm, "Devil's Advocate")

    async def analyze(
        self,
        question: str,
        tool_outputs: Dict,
        profile: InvestorProfile,
        other_opinions: Dict[str, AdvisorOpinion] = None,
        provider: str = "gemini"
    ) -> AdvisorOpinion:
        start = time.time()
        logger.info("agent.devils_advocate.start")

        context = self._build_context(question, tool_outputs, profile)

        # Enrich context with other advisors' opinions — this is the key differentiator
        if other_opinions:
            opinions_text = "\n\nOTHER ADVISORS' OPINIONS (challenge these specifically):\n"
            for advisor_name, opinion in other_opinions.items():
                opinions_text += f"\n{advisor_name}:\n"
                opinions_text += f"  Stance: {opinion.stance}\n"
                opinions_text += f"  Reasoning: {opinion.reasoning}\n"
                opinions_text += f"  Key Points: {', '.join(opinion.key_points)}\n"
            context += opinions_text

        result = await self.llm.complete_json(self.SYSTEM_PROMPT, context, temperature=0.45, provider=provider)

        logger.info("agent.devils_advocate.complete", duration_ms=round((time.time() - start) * 1000, 2))
        return AdvisorOpinion(**result)


# ─────────────────────────────────────────────
# AGENT 5: Consensus Agent
# ─────────────────────────────────────────────

class ConsensusAgent(BaseAgent):
    SYSTEM_PROMPT = """You are the Consensus Agent — the Chair of the investment committee.
Your role: SYNTHESIZE all opinions into a final, actionable recommendation.

You are NOT just averaging opinions. You are making a real judgement call:
- Where do advisors agree? This is strong signal.
- Where do they disagree? Understand WHY — is it risk appetite or facts?
- Has the Devil's Advocate raised a fatal flaw? If yes, weight it heavily.
- What does the evidence actually support?
- What is the confidence level based on agreement vs disagreement?

Confidence scoring guide:
- 0.85–1.0: Strong consensus, clear evidence, low risk of being wrong
- 0.65–0.84: Moderate consensus, some valid disagreements
- 0.45–0.64: Significant disagreement, recommendation comes with caveats
- Below 0.45: High uncertainty, recommend further analysis before action

You must respond in this EXACT JSON format:
{
  "agreements": ["<point all or most advisors agreed on>", ...],
  "disagreements": ["<point where advisors had conflicting views>", ...],
  "confidence_score": <float 0.0-1.0>,
  "final_recommendation": "<clear, specific, actionable recommendation in 3-5 sentences>",
  "action_items": ["<specific action 1>", "<specific action 2>", ...],
  "evidence": ["<key data point supporting recommendation>", ...],
  "risk_warnings": ["<important risk the investor must know>", ...]
}

Be decisive. The investor needs a clear answer, not a hedge."""

    def __init__(self, llm: LLMClient):
        super().__init__(llm, "Consensus Agent")

    async def synthesize(
        self,
        question: str,
        tool_outputs: Dict,
        profile: InvestorProfile,
        all_opinions: Dict[str, AdvisorOpinion],
        provider: str = "gemini"
    ) -> Dict:
        start = time.time()
        logger.info("agent.consensus.start")

        opinions_summary = "\nALL COMMITTEE OPINIONS:\n"
        for advisor_name, opinion in all_opinions.items():
            opinions_summary += f"\n{'='*40}\n"
            opinions_summary += f"ADVISOR: {opinion.advisor}\n"
            opinions_summary += f"STANCE: {opinion.stance} | CONFIDENCE: {opinion.confidence}\n"
            opinions_summary += f"REASONING: {opinion.reasoning}\n"
            opinions_summary += f"KEY POINTS:\n"
            for point in opinion.key_points:
                opinions_summary += f"  - {point}\n"

        context = self._build_context(question, tool_outputs, profile) + opinions_summary

        result = await self.llm.complete_json(self.SYSTEM_PROMPT, context, temperature=0.2, provider=provider)

        logger.info("agent.consensus.complete", duration_ms=round((time.time() - start) * 1000, 2))
        return result

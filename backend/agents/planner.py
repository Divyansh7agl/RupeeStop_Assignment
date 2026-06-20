"""
Planner Agent: Orchestrates the full investment committee pipeline.
- Decides which tools to call based on the user question
- Runs specialist agents in parallel
- Feeds Devil's Advocate the other opinions
- Hands everything to Consensus Agent
"""

import asyncio
import time
import structlog
from typing import Dict, Any, List, Tuple, AsyncGenerator

from models.schemas import (
    InvestorProfile, FinalRecommendation, AdvisorOpinion,
    PipelineLog, QueryRequest
)
from agents.llm_client import LLMClient
from agents.specialists import (
    ConservativeAdvisor, GrowthAdvisor,
    CostEfficiencyAdvisor, DevilsAdvocate, ConsensusAgent
)
from tools.investment_tools import (
    portfolio_analyzer, get_all_fund_metadata,
    get_portfolio_weighted_returns, get_portfolio_risk_summary,
    market_context_tool
)
from data.portfolio import SAMPLE_PORTFOLIO

logger = structlog.get_logger(__name__)


class PlannerAgent:
    """
    Orchestrates the full multi-agent pipeline.
    Yields PipelineLog events for real-time streaming to the frontend.
    """

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.conservative = ConservativeAdvisor(llm)
        self.growth = GrowthAdvisor(llm)
        self.cost_efficiency = CostEfficiencyAdvisor(llm)
        self.devils_advocate = DevilsAdvocate(llm)
        self.consensus = ConsensusAgent(llm)

    def _determine_tools_needed(self, question: str) -> List[str]:
        """
        Decide which tools are needed based on question content.
        In production this would itself be an LLM call.
        """
        question_lower = question.lower()
        tools = ["portfolio_analyzer"]  # always run

        if any(kw in question_lower for kw in ["fund", "redeem", "sell", "switch", "metadata"]):
            tools.append("fund_metadata")

        if any(kw in question_lower for kw in ["return", "perform", "cagr", "underperform", "growth"]):
            tools.append("historical_returns")

        if any(kw in question_lower for kw in ["risk", "volatile", "drawdown", "sharpe", "safe"]):
            tools.append("risk_metrics")

        if any(kw in question_lower for kw in ["market", "sector", "economy", "rbi", "interest", "current"]):
            tools.append("market_context")

        # Default: if general question, run everything
        if len(tools) <= 2:
            tools = ["portfolio_analyzer", "fund_metadata", "historical_returns", "risk_metrics"]

        return list(set(tools))

    async def run(
        self,
        request: QueryRequest
    ) -> Tuple[FinalRecommendation, List[PipelineLog]]:
        """
        Full pipeline. Returns final recommendation + full logs.
        """
        logs: List[PipelineLog] = []
        pipeline_start = time.time()

        def log(step: str, status: str, details: str = None):
            entry = PipelineLog(step=step, status=status, details=details)
            logs.append(entry)
            logger.info(f"pipeline.{step}", status=status, details=details)
            return entry

        # ── Step 1: Load investor profile ──
        log("load_profile", "running", "Loading investor profile and portfolio")
        if request.use_sample_data or request.investor_profile is None:
            from data.portfolio import SAMPLE_PORTFOLIO
            profile = InvestorProfile(**SAMPLE_PORTFOLIO)
        else:
            profile = request.investor_profile
        log("load_profile", "completed", f"Loaded {len(profile.portfolio)} funds for {profile.age}yo investor")

        # ── Step 2: Planner decides tools ──
        log("planner", "running", "Analyzing question to determine required tools")
        tools_needed = self._determine_tools_needed(request.question)
        log("planner", "completed", f"Tools selected: {', '.join(tools_needed)}")

        # ── Step 3: Run tools ──
        log("tool_execution", "running", f"Gathering evidence from {len(tools_needed)} tools")
        tool_outputs: Dict[str, Any] = {}

        if "portfolio_analyzer" in tools_needed:
            tool_outputs["portfolio_analysis"] = portfolio_analyzer(profile).model_dump()

        if "fund_metadata" in tools_needed:
            metadata = get_all_fund_metadata(profile)
            tool_outputs["fund_metadata"] = {k: v.model_dump() for k, v in metadata.items()}

        if "historical_returns" in tools_needed:
            tool_outputs["portfolio_returns"] = get_portfolio_weighted_returns(profile)

        if "risk_metrics" in tools_needed:
            tool_outputs["portfolio_risk"] = get_portfolio_risk_summary(profile)

        if "market_context" in tools_needed:
            market_query = f"Indian mutual fund market outlook 2025, {request.question[:100]}"
            market_ctx = await market_context_tool(market_query, self.llm, request.provider)
            tool_outputs["market_context"] = market_ctx.model_dump()

        log("tool_execution", "completed", f"Evidence gathered: {list(tool_outputs.keys())}")

        # ── Step 4: Parallel specialist analysis ──
        log("specialists_parallel", "running", "Conservative, Growth, Cost advisors analyzing in parallel")
        specialist_start = time.time()

        conservative_task = self.conservative.analyze(request.question, tool_outputs, profile, provider=request.provider)
        growth_task = self.growth.analyze(request.question, tool_outputs, profile, provider=request.provider)
        cost_task = self.cost_efficiency.analyze(request.question, tool_outputs, profile, provider=request.provider)

        conservative_opinion, growth_opinion, cost_opinion = await asyncio.gather(
            conservative_task, growth_task, cost_task
        )

        specialist_duration = round((time.time() - specialist_start) * 1000, 2)
        log("specialists_parallel", "completed", f"3 advisors responded in {specialist_duration}ms")

        # ── Step 5: Devil's Advocate (sees other opinions) ──
        log("devils_advocate", "running", "Devil's Advocate challenging specialist opinions")
        da_start = time.time()

        devils_opinion = await self.devils_advocate.analyze(
            request.question,
            tool_outputs,
            profile,
            other_opinions={
                "Conservative Advisor": conservative_opinion,
                "Growth Advisor": growth_opinion,
                "Cost & Efficiency Advisor": cost_opinion
            },
            provider=request.provider
        )

        log("devils_advocate", "completed", f"Challenges raised in {round((time.time()-da_start)*1000, 2)}ms")

        # ── Step 6: Consensus ──
        log("consensus", "running", "Synthesizing all opinions into final recommendation")
        consensus_start = time.time()

        all_opinions = {
            "conservative": conservative_opinion,
            "growth": growth_opinion,
            "cost_efficiency": cost_opinion,
            "devils_advocate": devils_opinion
        }

        consensus_data = await self.consensus.synthesize(
            request.question, tool_outputs, profile, all_opinions, provider=request.provider
        )

        log("consensus", "completed", f"Consensus reached in {round((time.time()-consensus_start)*1000, 2)}ms")

        # ── Step 7: Assemble final output ──
        total_duration = round((time.time() - pipeline_start) * 1000, 2)
        log("pipeline_complete", "completed", f"Full pipeline completed in {total_duration}ms")

        final = FinalRecommendation(
            committee_opinions={
                "conservative": conservative_opinion,
                "growth": growth_opinion,
                "cost_efficiency": cost_opinion,
                "devils_advocate": devils_opinion
            },
            agreements=consensus_data.get("agreements", []),
            disagreements=consensus_data.get("disagreements", []),
            confidence_score=consensus_data.get("confidence_score", 0.5),
            final_recommendation=consensus_data.get("final_recommendation", ""),
            action_items=consensus_data.get("action_items", []),
            evidence=consensus_data.get("evidence", []),
            risk_warnings=consensus_data.get("risk_warnings", [])
        )

        return final, logs

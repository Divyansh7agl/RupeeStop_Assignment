"""
Investment Committee Tools
Pure computation tools that agents call to gather evidence.
No hardcoded answers — all derived from portfolio data + metadata DBs.
"""

import math
import time
from typing import Dict, List, Optional
import structlog

from models.schemas import (
    PortfolioAnalysis, FundMetadata, HistoricalReturns,
    RiskMetrics, MarketContext, InvestorProfile
)
from data.portfolio import FUND_METADATA_DB, HISTORICAL_RETURNS_DB

logger = structlog.get_logger(__name__)

EQUITY_CATEGORIES = {"Large Cap", "Mid Cap", "Small Cap", "Flexi Cap", "ELSS", "Thematic", "Sectoral - Technology"}
DEBT_CATEGORIES = {"Debt - Gilt", "Debt - Short Duration", "Debt - Corporate Bond", "Liquid"}
HYBRID_CATEGORIES = {"Balanced Advantage", "Aggressive Hybrid", "Conservative Hybrid"}


# ─────────────────────────────────────────────
# TOOL 1: Portfolio Analyzer
# ─────────────────────────────────────────────

def portfolio_analyzer(profile: InvestorProfile) -> PortfolioAnalysis:
    """
    Analyzes portfolio allocation, overlap, diversification.
    Returns structured metrics without any LLM involvement.
    """
    start = time.time()
    logger.info("tool.portfolio_analyzer.start", funds=len(profile.portfolio))

    total_invested = sum(f.invested_amount for f in profile.portfolio)
    total_current = sum(f.current_value for f in profile.portfolio)
    total_returns_pct = ((total_current - total_invested) / total_invested) * 100

    category_allocation: Dict[str, float] = {}
    for fund in profile.portfolio:
        cat = fund.category
        category_allocation[cat] = category_allocation.get(cat, 0) + fund.allocation_percent

    equity_pct = sum(
        alloc for cat, alloc in category_allocation.items()
        if cat in EQUITY_CATEGORIES
    )
    debt_pct = sum(
        alloc for cat, alloc in category_allocation.items()
        if cat in DEBT_CATEGORIES
    )
    hybrid_pct = sum(
        alloc for cat, alloc in category_allocation.items()
        if cat in HYBRID_CATEGORIES
    )
    sectoral_pct = sum(
        alloc for cat, alloc in category_allocation.items()
        if "Sectoral" in cat or "Thematic" in cat
    )

    # Overlap: check if 2+ large cap funds exist
    large_cap_funds = [f for f in profile.portfolio if f.category == "Large Cap"]
    overlap_detected = len(large_cap_funds) >= 2

    # Diversification score: penalize for overlap, too many funds, high sectoral
    score = 10.0
    if overlap_detected:
        score -= 2.0
    if len(profile.portfolio) > 7:
        score -= 1.0
    if sectoral_pct > 15:
        score -= 1.5
    if debt_pct < 5 and profile.age > 40:
        score -= 1.0
    score = max(0, min(10, score))

    # Concentration risk
    max_single_alloc = max(f.allocation_percent for f in profile.portfolio)
    if max_single_alloc > 35:
        concentration_risk = "High"
    elif max_single_alloc > 20:
        concentration_risk = "Medium"
    else:
        concentration_risk = "Low"

    duration_ms = (time.time() - start) * 1000
    logger.info("tool.portfolio_analyzer.complete", duration_ms=round(duration_ms, 2))

    return PortfolioAnalysis(
        total_invested=total_invested,
        total_current_value=total_current,
        total_returns_percent=round(total_returns_pct, 2),
        category_allocation=category_allocation,
        equity_percent=round(equity_pct, 2),
        debt_percent=round(debt_pct, 2),
        hybrid_percent=round(hybrid_pct, 2),
        sectoral_percent=round(sectoral_pct, 2),
        number_of_funds=len(profile.portfolio),
        large_cap_overlap_detected=overlap_detected,
        diversification_score=round(score, 1),
        concentration_risk=concentration_risk
    )


# ─────────────────────────────────────────────
# TOOL 2: Fund Metadata Tool
# ─────────────────────────────────────────────

def fund_metadata_tool(fund_id: str) -> Optional[FundMetadata]:
    """
    Returns category, benchmark, expense ratio, AUM for a fund.
    """
    logger.info("tool.fund_metadata.query", fund_id=fund_id)

    data = FUND_METADATA_DB.get(fund_id)
    if not data:
        logger.warning("tool.fund_metadata.not_found", fund_id=fund_id)
        return None

    return FundMetadata(**data)


def get_all_fund_metadata(profile: InvestorProfile) -> Dict[str, FundMetadata]:
    """Batch fetch metadata for all funds in portfolio."""
    result = {}
    for fund in profile.portfolio:
        meta = fund_metadata_tool(fund.fund_id)
        if meta:
            result[fund.fund_id] = meta
    return result


# ─────────────────────────────────────────────
# TOOL 3: Historical Return Tool
# ─────────────────────────────────────────────

def historical_return_tool(fund_id: str) -> Optional[HistoricalReturns]:
    """
    Returns CAGR across timeframes, volatility, max drawdown, alpha, beta.
    """
    logger.info("tool.historical_returns.query", fund_id=fund_id)

    data = HISTORICAL_RETURNS_DB.get(fund_id)
    if not data:
        logger.warning("tool.historical_returns.not_found", fund_id=fund_id)
        return None

    return HistoricalReturns(fund_id=fund_id, **data)


def get_portfolio_weighted_returns(profile: InvestorProfile) -> Dict:
    """Compute allocation-weighted average returns for entire portfolio."""
    weighted_1y = 0
    weighted_3y = 0
    weighted_5y = 0
    weighted_vol = 0
    total_alloc = sum(f.allocation_percent for f in profile.portfolio)

    for fund in profile.portfolio:
        returns = historical_return_tool(fund.fund_id)
        if not returns:
            continue
        weight = fund.allocation_percent / total_alloc
        weighted_1y += returns.cagr_1y * weight
        weighted_3y += returns.cagr_3y * weight
        weighted_5y += returns.cagr_5y * weight
        weighted_vol += returns.volatility_annual * weight

    return {
        "portfolio_cagr_1y": round(weighted_1y, 2),
        "portfolio_cagr_3y": round(weighted_3y, 2),
        "portfolio_cagr_5y": round(weighted_5y, 2),
        "portfolio_volatility": round(weighted_vol, 2)
    }


# ─────────────────────────────────────────────
# TOOL 4: Risk Metrics Tool
# ─────────────────────────────────────────────

RISK_FREE_RATE = 7.0  # India 10Y Gsec approx


def risk_metrics_tool(fund_id: str) -> Optional[RiskMetrics]:
    """
    Computes Sharpe, Sortino, VaR from historical data.
    """
    logger.info("tool.risk_metrics.query", fund_id=fund_id)

    hist = HISTORICAL_RETURNS_DB.get(fund_id)
    if not hist:
        return None

    cagr_5y = hist["cagr_5y"]
    vol = hist["volatility_annual"]
    max_dd = hist["max_drawdown"]

    sharpe = (cagr_5y - RISK_FREE_RATE) / vol if vol > 0 else 0
    # Sortino uses downside deviation (approx as vol * 0.7 for simplicity)
    downside_dev = vol * 0.7
    sortino = (cagr_5y - RISK_FREE_RATE) / downside_dev if downside_dev > 0 else 0
    # 95% VaR approximation (normal dist): mean - 1.645 * sigma
    monthly_vol = vol / math.sqrt(12)
    monthly_return = cagr_5y / 12
    var_95 = monthly_return - 1.645 * monthly_vol

    # Rolling return approximations
    rolling_1y_avg = hist["cagr_1y"] * 0.92  # slight haircut for rolling avg
    rolling_3y_avg = hist["cagr_3y"] * 0.95

    # Risk grade
    if sharpe >= 1.0 and max_dd > -25:
        grade = "A"
    elif sharpe >= 0.7 and max_dd > -35:
        grade = "B"
    elif sharpe >= 0.4:
        grade = "C"
    else:
        grade = "D"

    return RiskMetrics(
        fund_id=fund_id,
        sharpe_ratio=round(sharpe, 3),
        sortino_ratio=round(sortino, 3),
        max_drawdown=max_dd,
        rolling_1y_return_avg=round(rolling_1y_avg, 2),
        rolling_3y_return_avg=round(rolling_3y_avg, 2),
        value_at_risk_95=round(var_95, 2),
        risk_grade=grade
    )


def get_portfolio_risk_summary(profile: InvestorProfile) -> Dict:
    """Aggregate risk metrics across portfolio."""
    grades = []
    sharpes = []
    max_dds = []

    for fund in profile.portfolio:
        metrics = risk_metrics_tool(fund.fund_id)
        if not metrics:
            continue
        grades.append(metrics.risk_grade)
        sharpes.append(metrics.sharpe_ratio)
        max_dds.append(metrics.max_drawdown)

    avg_sharpe = sum(sharpes) / len(sharpes) if sharpes else 0
    worst_drawdown = min(max_dds) if max_dds else 0
    grade_counts = {g: grades.count(g) for g in set(grades)}

    return {
        "average_sharpe": round(avg_sharpe, 3),
        "worst_drawdown_in_portfolio": worst_drawdown,
        "risk_grade_distribution": grade_counts,
        "portfolio_risk_level": (
            "High" if avg_sharpe < 0.5 or worst_drawdown < -38
            else "Moderate" if avg_sharpe < 0.9
            else "Low-Moderate"
        )
    }


# ─────────────────────────────────────────────
# TOOL 5: Market Context Tool (Gemini Search / Groq fallback)
# ─────────────────────────────────────────────

async def market_context_tool(query: str, llm_client=None, provider: str = "gemini") -> MarketContext:
    """
    Fetches live market context using Gemini's Google Search grounding.
    Falls back to Groq knowledge-based response if Gemini unavailable or groq requested.
    """
    from datetime import datetime
    logger.info("tool.market_context.start", query=query)

    if provider == "gemini" and llm_client and hasattr(llm_client, 'gemini_client'):
        try:
            result = await llm_client.search_market_context(query)
            logger.info("tool.market_context.gemini_success")
            return MarketContext(
                query=query,
                context=result,
                source="gemini_search",
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logger.warning("tool.market_context.gemini_failed", error=str(e))

    # Groq fallback or direct request
    if llm_client and hasattr(llm_client, 'groq_client'):
        try:
            result = await llm_client.groq_market_context(query)
            logger.info("tool.market_context.groq_fallback_success")
            return MarketContext(
                query=query,
                context=result,
                source="groq_knowledge",
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error("tool.market_context.groq_failed", error=str(e))

    return MarketContext(
        query=query,
        context="Market context unavailable. Analysis based on historical data only.",
        source="unavailable",
        timestamp=datetime.now().isoformat()
    )

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class RiskProfile(str, Enum):
    conservative = "conservative"
    moderate = "moderate"
    aggressive = "aggressive"


class FundHolding(BaseModel):
    fund_name: str
    fund_id: str
    category: str
    allocation_percent: float
    invested_amount: float
    current_value: float
    sip_amount: Optional[float] = 0


class InvestorProfile(BaseModel):
    age: int
    risk_profile: RiskProfile
    monthly_income: Optional[float] = None
    monthly_investment: Optional[float] = None
    goals: List[str]
    investment_horizon_years: Optional[int] = None
    portfolio: List[FundHolding]


class PortfolioAnalysis(BaseModel):
    total_invested: float
    total_current_value: float
    total_returns_percent: float
    category_allocation: Dict[str, float]
    equity_percent: float
    debt_percent: float
    hybrid_percent: float
    sectoral_percent: float
    number_of_funds: int
    large_cap_overlap_detected: bool
    diversification_score: float  # 0-10
    concentration_risk: str  # Low / Medium / High


class FundMetadata(BaseModel):
    fund_name: str
    category: str
    benchmark: str
    expense_ratio: float
    aum_cr: float
    fund_manager: str
    launch_year: int


class HistoricalReturns(BaseModel):
    fund_id: str
    cagr_1y: float
    cagr_3y: float
    cagr_5y: float
    cagr_10y: Optional[float]
    volatility_annual: float
    max_drawdown: float
    alpha: float
    beta: float


class RiskMetrics(BaseModel):
    fund_id: str
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    rolling_1y_return_avg: float
    rolling_3y_return_avg: float
    value_at_risk_95: float  # 95% VaR
    risk_grade: str  # A/B/C/D


class MarketContext(BaseModel):
    query: str
    context: str
    source: str  # "gemini_search" or "groq_knowledge"
    timestamp: str


class AdvisorOpinion(BaseModel):
    advisor: str
    stance: str  # BUY / HOLD / SELL / RESTRUCTURE / CAUTION
    confidence: float  # 0.0 - 1.0
    reasoning: str
    key_points: List[str]
    evidence_used: List[str]


class CommitteeDebate(BaseModel):
    question: str
    conservative_opinion: AdvisorOpinion
    growth_opinion: AdvisorOpinion
    cost_efficiency_opinion: AdvisorOpinion
    devils_advocate_opinion: AdvisorOpinion


class FinalRecommendation(BaseModel):
    committee_opinions: Dict[str, AdvisorOpinion]
    agreements: List[str]
    disagreements: List[str]
    confidence_score: float
    final_recommendation: str
    action_items: List[str]
    evidence: List[str]
    risk_warnings: List[str]


class QueryRequest(BaseModel):
    question: str
    investor_profile: Optional[InvestorProfile] = None
    use_sample_data: bool = True
    provider: str = "gemini"


class PipelineLog(BaseModel):
    step: str
    status: str  # running / completed / failed
    details: Optional[str] = None
    duration_ms: Optional[float] = None

"""
Pydantic Schemas for Request/Response Validation
"""

from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List

# ============================================================================
# COMPANY SCHEMAS
# ============================================================================

class CompanyBase(BaseModel):
    symbol: str = Field(..., max_length=10, description="Stock ticker symbol")
    name: str = Field(..., max_length=255, description="Company name")
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    market_cap: Optional[int] = Field(None, description="Market cap in USD")

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    market_cap: Optional[int] = None

class Company(CompanyBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True  # Updated for Pydantic v2

# ============================================================================
# ESG SCORE SCHEMAS
# ============================================================================

class ESGScoreBase(BaseModel):
    environmental_score: Optional[float] = None
    social_score: Optional[float] = None
    governance_score: Optional[float] = None
    total_esg_score: Optional[float] = None
    carbon_intensity: Optional[float] = None
    controversy_score: Optional[float] = None
    date: date

class ESGScoreResponse(ESGScoreBase):
    id: int
    company_id: int
    
    class Config:
        from_attributes = True

# ============================================================================
# FINANCIAL METRIC SCHEMAS
# ============================================================================

class FinancialMetricBase(BaseModel):
    pe_ratio: Optional[float] = None
    eps: Optional[float] = None
    revenue: Optional[int] = None
    profit_margin: Optional[float] = None
    debt_to_equity: Optional[float] = None
    date: date

class FinancialMetricResponse(FinancialMetricBase):
    id: int
    company_id: int
    
    class Config:
        from_attributes = True

# ============================================================================
# COMPANY DETAIL (with relationships)
# ============================================================================

class CompanyDetail(Company):
    esg_scores: List[ESGScoreResponse] = []
    financial_metrics: List[FinancialMetricResponse] = []
    
    class Config:
        from_attributes = True

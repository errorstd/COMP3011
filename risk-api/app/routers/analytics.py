# KPI endpoints

# app/routers/analytics.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database import get_db
from app import models
from datetime import date, timedelta

router = APIRouter(prefix="/analytics", tags=["Analytics & KPIs"])

@router.get("/portfolio/average-esg")
def get_portfolio_average_esg(
    symbols: str,  # Comma-separated: "AAPL,MSFT,GOOGL"
    db: Session = Depends(get_db)
):
    """Calculate portfolio-weighted average ESG score"""
    symbol_list = symbols.split(',')
    
    # Get latest ESG scores for each company
    scores = db.query(
        models.Company.symbol,
        models.ESGScore.total_esg_score,
        models.Company.market_cap
    ).join(models.ESGScore).filter(
        models.Company.symbol.in_(symbol_list)
    ).all()
    
    # Calculate weighted average
    total_market_cap = sum(s.market_cap for s in scores)
    weighted_score = sum(
        s.total_esg_score * (s.market_cap / total_market_cap) 
        for s in scores
    )
    
    return {
        "portfolio_symbols": symbol_list,
        "average_esg_score": round(weighted_score, 2),
        "total_market_cap": total_market_cap,
        "num_companies": len(scores)
    }

@router.get("/top-performers")
def get_top_esg_performers(
    limit: int = 10,
    sector: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get top ESG performing companies"""
    query = db.query(
        models.Company.symbol,
        models.Company.name,
        models.Company.sector,
        models.ESGScore.total_esg_score,
        models.ESGScore.environmental_score,
        models.ESGScore.social_score,
        models.ESGScore.governance_score
    ).join(models.ESGScore)
    
    if sector:
        query = query.filter(models.Company.sector == sector)
    
    results = query.order_by(
        desc(models.ESGScore.total_esg_score)
    ).limit(limit).all()
    
    return [{
        "symbol": r.symbol,
        "name": r.name,
        "sector": r.sector,
        "esg_score": r.total_esg_score,
        "environmental": r.environmental_score,
        "social": r.social_score,
        "governance": r.governance_score
    } for r in results]

@router.get("/sector-distribution")
def get_sector_esg_distribution(db: Session = Depends(get_db)):
    """Get average ESG scores by sector"""
    results = db.query(
        models.Company.sector,
        func.avg(models.ESGScore.total_esg_score).label('avg_esg'),
        func.avg(models.ESGScore.carbon_intensity).label('avg_carbon'),
        func.count(models.Company.id).label('company_count')
    ).join(models.ESGScore).group_by(
        models.Company.sector
    ).all()
    
    return [{
        "sector": r.sector,
        "average_esg_score": round(r.avg_esg, 2),
        "average_carbon_intensity": round(r.avg_carbon, 2),
        "num_companies": r.company_count
    } for r in results]

@router.get("/risk-flags")
def get_risk_flags(
    controversy_threshold: float = 5.0,
    carbon_threshold: float = 100.0,
    db: Session = Depends(get_db)
):
    """Identify companies with ESG risk flags"""
    high_risk = db.query(
        models.Company.symbol,
        models.Company.name,
        models.ESGScore.controversy_score,
        models.ESGScore.carbon_intensity,
        models.ESGScore.total_esg_score
    ).join(models.ESGScore).filter(
        (models.ESGScore.controversy_score >= controversy_threshold) |
        (models.ESGScore.carbon_intensity >= carbon_threshold)
    ).all()
    
    return [{
        "symbol": r.symbol,
        "name": r.name,
        "flags": {
            "high_controversy": r.controversy_score >= controversy_threshold,
            "high_carbon": r.carbon_intensity >= carbon_threshold
        },
        "controversy_score": r.controversy_score,
        "carbon_intensity": r.carbon_intensity,
        "esg_score": r.total_esg_score
    } for r in high_risk]

@router.get("/financial-esg-correlation")
def get_financial_esg_correlation(db: Session = Depends(get_db)):
    """Analyze correlation between financial performance and ESG scores"""
    data = db.query(
        models.Company.symbol,
        models.ESGScore.total_esg_score,
        models.FinancialMetric.pe_ratio,
        models.FinancialMetric.profit_margin,
        models.FinancialMetric.revenue
    ).join(models.ESGScore).join(models.FinancialMetric).all()
    
    # Calculate basic correlation (or use numpy/scipy)
    # For simplicity, return data for client-side analysis
    
    return [{
        "symbol": d.symbol,
        "esg_score": d.total_esg_score,
        "pe_ratio": d.pe_ratio,
        "profit_margin": d.profit_margin,
        "revenue": d.revenue
    } for d in data]

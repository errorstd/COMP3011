"""
Stock Valuation & Risk Analytics API
Version 3.0.0 - Financial Data Focus (ESG Removed)
"""

from fastapi import FastAPI, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
import csv
import io
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
from statistics import stdev, mean

from app.database import get_db
from app import models, schemas

app = FastAPI(
    title="Stock Valuation & Risk Analytics API",
    description="Professional stock analysis API with valuation metrics and risk assessment",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

def convert_numpy(value):
    """Convert numpy types to Python native types"""
    if value is None or pd.isna(value):
        return None
    if isinstance(value, (np.integer, np.floating)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.item()
    return value


# ============================================================================
# ROOT & HEALTH CHECK
# ============================================================================

@app.get("/", tags=["Health"])
def root():
    """API Health Check"""
    return {
        "message": "Stock Valuation & Risk Analytics API",
        "status": "running",
        "docs": "/docs",
        "version": "3.0.0",
        "focus": "Financial valuation and risk analysis",
        "features": [
            "Stock valuation metrics (P/E, DCF estimates)",
            "Historical price analysis",
            "Volatility & risk assessment",
            "Portfolio performance tracking",
            "Sector comparison analytics",
            "Real-time data fetching",
            "Stock search & browse by category"
        ]
    }


# ============================================================================
# COMPANY MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/companies/", tags=["Companies"])
async def create_companies(
    company: Optional[schemas.CompanyCreate] = None,
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Create single company OR bulk upload from CSV"""
    
    if file:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        try:
            contents = await file.read()
            csv_data = contents.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_data))
            
            imported = []
            errors = []
            
            for row in csv_reader:
                try:
                    existing = db.query(models.Company).filter(
                        models.Company.symbol == row['symbol'].upper()
                    ).first()
                    
                    if existing:
                        errors.append({row['symbol']: "Already exists"})
                        continue
                    
                    company_obj = models.Company(
                        symbol=row['symbol'].upper(),
                        name=row['name'],
                        sector=row.get('sector'),
                        industry=row.get('industry'),
                        market_cap=int(row.get('market_cap', 0)) if row.get('market_cap') else None
                    )
                    db.add(company_obj)
                    imported.append(row['symbol'].upper())
                    
                except Exception as e:
                    errors.append({row.get('symbol', 'Unknown'): str(e)})
            
            db.commit()
            
            return {
                "mode": "bulk_upload",
                "message": "Bulk upload completed",
                "imported_count": len(imported),
                "imported_symbols": imported,
                "error_count": len(errors),
                "errors": errors if errors else None
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")
    
    elif company:
        existing = db.query(models.Company).filter(
            models.Company.symbol == company.symbol.upper()
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"Company {company.symbol} already exists"
            )
        
        db_company = models.Company(
            symbol=company.symbol.upper(),
            name=company.name,
            sector=company.sector,
            industry=company.industry,
            market_cap=company.market_cap
        )
        
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
        
        return {
            "mode": "single_create",
            "message": f"Company {company.symbol} created successfully",
            "company": {
                "id": db_company.id,
                "symbol": db_company.symbol,
                "name": db_company.name,
                "sector": db_company.sector,
                "industry": db_company.industry,
                "market_cap": db_company.market_cap
            }
        }
    
    else:
        raise HTTPException(
            status_code=400,
            detail="Must provide either company JSON data or CSV file"
        )


@app.get("/companies/", tags=["Companies"])
def get_companies(
    symbol: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    sector: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all companies OR specific company"""
    
    if symbol:
        company = db.query(models.Company).filter(
            models.Company.symbol == symbol.upper()
        ).first()
        
        if not company:
            raise HTTPException(status_code=404, detail=f"Company {symbol} not found")
        
        latest_financial = db.query(models.FinancialMetric).filter(
            models.FinancialMetric.company_id == company.id
        ).order_by(desc(models.FinancialMetric.date)).first()
        
        prices = db.query(models.StockPrice).filter(
            models.StockPrice.company_id == company.id
        ).order_by(desc(models.StockPrice.date)).limit(30).all()
        
        price_change_30d = None
        if len(prices) >= 2:
            price_change_30d = ((prices[0].close - prices[-1].close) / prices[-1].close) * 100
        
        return {
            "mode": "single",
            "company": {
                "id": company.id,
                "symbol": company.symbol,
                "name": company.name,
                "sector": company.sector,
                "industry": company.industry,
                "market_cap": company.market_cap,
                "pe_ratio": latest_financial.pe_ratio if latest_financial else None,
                "eps": latest_financial.eps if latest_financial else None,
                "profit_margin": latest_financial.profit_margin if latest_financial else None,
                "debt_to_equity": latest_financial.debt_to_equity if latest_financial else None,
                "price_change_30d_percent": round(price_change_30d, 2) if price_change_30d else None,
                "latest_price": prices[0].close if prices else None,
                "latest_price_date": prices[0].date.isoformat() if prices else None
            }
        }
    
    query = db.query(models.Company)
    
    if sector:
        query = query.filter(models.Company.sector == sector)
    
    total = query.count()
    companies = query.offset(skip).limit(limit).all()
    
    return {
        "mode": "list",
        "total": total,
        "showing": len(companies),
        "skip": skip,
        "limit": limit,
        "filters": {"sector": sector},
        "companies": [
            {
                "id": c.id,
                "symbol": c.symbol,
                "name": c.name,
                "sector": c.sector,
                "industry": c.industry,
                "market_cap": c.market_cap
            }
            for c in companies
        ]
    }


@app.delete("/companies/", tags=["Companies"])
def delete_all_companies(
    confirm: bool = Query(False),
    db: Session = Depends(get_db)
):
    """DELETE ALL COMPANIES - CASCADE DELETE ENABLED"""
    
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Confirmation required",
                "message": "To delete all companies, add ?confirm=true to the URL",
                "warning": "This action cannot be undone!",
                "example": "DELETE /companies/?confirm=true"
            }
        )
    
    try:
        count = db.query(models.Company).count()
        
        if count == 0:
            return {
                "message": "No companies to delete",
                "deleted_count": 0
            }
        
        # ✅ FIX: Use ORM delete, not raw SQL
        # This allows CASCADE DELETE to work properly
        companies = db.query(models.Company).all()
        for company in companies:
            db.delete(company)
        
        db.commit()
        
        return {
            "message": "All companies deleted successfully",
            "deleted_count": count,
            "note": "CASCADE DELETE removed all related financial metrics and stock prices",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting companies: {str(e)}")


@app.delete("/companies/{symbol}", tags=["Companies"])
def delete_company(symbol: str, db: Session = Depends(get_db)):
    """Delete a specific company (CASCADE DELETE)"""
    
    db_company = db.query(models.Company).filter(
        models.Company.symbol == symbol.upper()
    ).first()
    
    if not db_company:
        raise HTTPException(status_code=404, detail=f"Company {symbol} not found")
    
    db.delete(db_company)
    db.commit()
    
    return {
        "message": f"Company {symbol} deleted successfully",
        "deleted_symbol": symbol.upper(),
        "note": "All related data automatically deleted via CASCADE"
    }


# ============================================================================
# STOCK SEARCH & BROWSE (NEW FEATURE)
# ============================================================================

@app.get("/browse/search", tags=["Browse & Search"])
def search_stocks(
    query: str = Query(..., description="Search term (company name or symbol)"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search stocks by company name or symbol
    
    Examples:
    - /browse/search?query=apple
    - /browse/search?query=AAPL
    - /browse/search?query=micro
    """
    
    search_term = f"%{query.upper()}%"
    
    results = db.query(models.Company).filter(
        (models.Company.symbol.like(search_term)) |
        (models.Company.name.ilike(search_term))
    ).limit(limit).all()
    
    if not results:
        raise HTTPException(
            status_code=404, 
            detail=f"No companies found matching '{query}'"
        )
    
    return {
        "search_query": query,
        "found": len(results),
        "results": [
            {
                "symbol": c.symbol,
                "name": c.name,
                "sector": c.sector,
                "industry": c.industry,
                "market_cap": c.market_cap
            }
            for c in results
        ]
    }


@app.get("/browse/categories", tags=["Browse & Search"])
def get_categories(db: Session = Depends(get_db)):
    """
    Get all available stock categories with counts
    
    Returns sectors and industries available in the database
    """
    
    sectors = db.query(
        models.Company.sector,
        func.count(models.Company.id).label('count')
    ).group_by(models.Company.sector).all()
    
    industries = db.query(
        models.Company.industry,
        func.count(models.Company.id).label('count')
    ).group_by(models.Company.industry).limit(50).all()
    
    return {
        "total_sectors": len(sectors),
        "total_industries": len(industries),
        "sectors": [
            {"name": s.sector, "company_count": s.count}
            for s in sectors if s.sector
        ],
        "industries": [
            {"name": i.industry, "company_count": i.count}
            for i in industries if i.industry
        ]
    }


@app.get("/browse/new-stocks", tags=["Browse & Search"])
def get_new_stocks(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get recently added stocks (sorted by newest price data)
    
    Useful for discovering newly imported companies
    """
    
    results = db.query(
        models.Company.symbol,
        models.Company.name,
        models.Company.sector,
        models.Company.market_cap,
        func.max(models.StockPrice.date).label('latest_date')
    ).join(models.StockPrice).group_by(
        models.Company.id
    ).order_by(
        desc('latest_date')
    ).limit(limit).all()
    
    return {
        "description": "Recently added stocks",
        "found": len(results),
        "stocks": [
            {
                "symbol": r.symbol,
                "name": r.name,
                "sector": r.sector,
                "market_cap": r.market_cap,
                "latest_data_date": r.latest_date.isoformat()
            }
            for r in results
        ]
    }


@app.get("/browse/tech-stocks", tags=["Browse & Search"])
def get_tech_stocks(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all Technology sector stocks"""
    
    stocks = db.query(models.Company).filter(
        models.Company.sector == "Technology"
    ).limit(limit).all()
    
    return {
        "category": "Technology Stocks",
        "found": len(stocks),
        "stocks": [
            {
                "symbol": s.symbol,
                "name": s.name,
                "industry": s.industry,
                "market_cap": s.market_cap
            }
            for s in stocks
        ]
    }


@app.get("/browse/green-energy", tags=["Browse & Search"])
def get_green_energy_stocks(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get green/renewable energy related stocks"""
    
    # Search for energy sector + renewable/solar/wind keywords
    stocks = db.query(models.Company).filter(
        (models.Company.sector == "Energy") |
        (models.Company.industry.ilike("%renewable%")) |
        (models.Company.industry.ilike("%solar%")) |
        (models.Company.industry.ilike("%wind%")) |
        (models.Company.name.ilike("%solar%")) |
        (models.Company.name.ilike("%wind%"))
    ).limit(limit).all()
    
    return {
        "category": "Green Energy & Renewables",
        "found": len(stocks),
        "stocks": [
            {
                "symbol": s.symbol,
                "name": s.name,
                "sector": s.sector,
                "industry": s.industry,
                "market_cap": s.market_cap
            }
            for s in stocks
        ]
    }


# ============================================================================
# VALUATION ANALYTICS
# ============================================================================

@app.get("/analytics/valuation/undervalued", tags=["Valuation"])
def get_undervalued_stocks(
    limit: int = Query(10, ge=1, le=50),
    sector: Optional[str] = None,
    max_pe: float = Query(15.0, description="Maximum P/E ratio threshold"),
    db: Session = Depends(get_db)
):
    """
    Find potentially undervalued stocks based on P/E ratio
    
    Criteria:
    - Low P/E ratio (below threshold)
    - Positive earnings (EPS > 0)
    - Sorted by P/E ratio (lowest first)
    """
    
    query = db.query(
        models.Company.symbol,
        models.Company.name,
        models.Company.sector,
        models.Company.market_cap,
        models.FinancialMetric.pe_ratio,
        models.FinancialMetric.eps,
        models.FinancialMetric.profit_margin
    ).join(models.FinancialMetric).filter(
        models.FinancialMetric.pe_ratio.isnot(None),
        models.FinancialMetric.pe_ratio > 0,
        models.FinancialMetric.pe_ratio <= max_pe,
        models.FinancialMetric.eps > 0
    )
    
    if sector:
        query = query.filter(models.Company.sector == sector)
    
    results = query.order_by(models.FinancialMetric.pe_ratio).limit(limit).all()
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No undervalued stocks found with P/E < {max_pe}"
        )
    
    return {
        "criteria": {
            "max_pe_ratio": max_pe,
            "sector": sector,
            "limit": limit
        },
        "found": len(results),
        "undervalued_stocks": [
            {
                "rank": idx + 1,
                "symbol": r.symbol,
                "name": r.name,
                "sector": r.sector,
                "market_cap": r.market_cap,
                "pe_ratio": round(r.pe_ratio, 2),
                "eps": round(r.eps, 2) if r.eps else None,
                "profit_margin": round(r.profit_margin * 100, 2) if r.profit_margin else None,
                "valuation_score": "Strong" if r.pe_ratio < 10 else "Moderate"
            }
            for idx, r in enumerate(results)
        ]
    }


@app.get("/analytics/valuation/overvalued", tags=["Valuation"])
def get_overvalued_stocks(
    limit: int = Query(10, ge=1, le=50),
    sector: Optional[str] = None,
    min_pe: float = Query(30.0, description="Minimum P/E ratio threshold"),
    db: Session = Depends(get_db)
):
    """
    Find potentially overvalued stocks based on P/E ratio
    
    Criteria:
    - High P/E ratio (above threshold)
    - Sorted by P/E ratio (highest first)
    """
    
    query = db.query(
        models.Company.symbol,
        models.Company.name,
        models.Company.sector,
        models.Company.market_cap,
        models.FinancialMetric.pe_ratio,
        models.FinancialMetric.eps,
        models.FinancialMetric.profit_margin
    ).join(models.FinancialMetric).filter(
        models.FinancialMetric.pe_ratio.isnot(None),
        models.FinancialMetric.pe_ratio >= min_pe
    )
    
    if sector:
        query = query.filter(models.Company.sector == sector)
    
    results = query.order_by(desc(models.FinancialMetric.pe_ratio)).limit(limit).all()
    
    return {
        "criteria": {
            "min_pe_ratio": min_pe,
            "sector": sector,
            "limit": limit
        },
        "found": len(results),
        "overvalued_stocks": [
            {
                "rank": idx + 1,
                "symbol": r.symbol,
                "name": r.name,
                "sector": r.sector,
                "market_cap": r.market_cap,
                "pe_ratio": round(r.pe_ratio, 2),
                "eps": round(r.eps, 2) if r.eps else None,
                "profit_margin": round(r.profit_margin * 100, 2) if r.profit_margin else None,
                "risk_level": "High" if r.pe_ratio > 50 else "Moderate"
            }
            for idx, r in enumerate(results)
        ]
    }


# ============================================================================
# RISK ASSESSMENT
# ============================================================================

@app.get("/analytics/risk/volatility/{symbol}", tags=["Risk Assessment"])
def get_stock_volatility(symbol: str, db: Session = Depends(get_db)):
    """
    Calculate price volatility (standard deviation) for a stock
    
    Metrics:
    - 30-day volatility
    - 90-day volatility
    - Price range
    - Risk classification
    """
    
    symbol = symbol.upper()
    
    company = db.query(models.Company).filter(
        models.Company.symbol == symbol
    ).first()
    
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {symbol} not found")
    
    prices = db.query(models.StockPrice).filter(
        models.StockPrice.company_id == company.id
    ).order_by(desc(models.StockPrice.date)).limit(90).all()
    
    if len(prices) < 30:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient price data for {symbol} (need 30+ days)"
        )
    
    close_prices = [p.close for p in reversed(prices)]
    returns = [
        ((close_prices[i] - close_prices[i-1]) / close_prices[i-1]) * 100
        for i in range(1, len(close_prices))
    ]
    
    volatility_30d = stdev(returns[:30]) if len(returns) >= 30 else None
    volatility_90d = stdev(returns) if len(returns) >= 90 else None
    
    price_range = max(close_prices) - min(close_prices)
    price_range_percent = (price_range / min(close_prices)) * 100
    
    if volatility_30d:
        if volatility_30d < 2:
            risk_level = "Low"
        elif volatility_30d < 4:
            risk_level = "Moderate"
        else:
            risk_level = "High"
    else:
        risk_level = "Unknown"
    
    return {
        "symbol": symbol,
        "name": company.name,
        "analysis_period": {
            "days_analyzed": len(prices),
            "start_date": prices[-1].date.isoformat(),
            "end_date": prices[0].date.isoformat()
        },
        "volatility": {
            "30_day_volatility_percent": round(volatility_30d, 2) if volatility_30d else None,
            "90_day_volatility_percent": round(volatility_90d, 2) if volatility_90d else None,
            "risk_level": risk_level
        },
        "price_metrics": {
            "current_price": round(prices[0].close, 2),
            "period_high": round(max(close_prices), 2),
            "period_low": round(min(close_prices), 2),
            "price_range": round(price_range, 2),
            "price_range_percent": round(price_range_percent, 2)
        }
    }


@app.get("/analytics/risk/high-risk", tags=["Risk Assessment"])
def get_high_risk_stocks(
    limit: int = Query(10, ge=1, le=50),
    min_volatility: float = Query(4.0, description="Minimum volatility threshold %"),
    db: Session = Depends(get_db)
):
    """
    Identify high-risk stocks based on price volatility
    
    Analyzes 30-day price movements to calculate risk scores
    """
    
    companies = db.query(models.Company).all()
    
    risk_stocks = []
    
    for company in companies:
        prices = db.query(models.StockPrice).filter(
            models.StockPrice.company_id == company.id
        ).order_by(desc(models.StockPrice.date)).limit(30).all()
        
        if len(prices) < 30:
            continue
        
        close_prices = [p.close for p in reversed(prices)]
        returns = [
            ((close_prices[i] - close_prices[i-1]) / close_prices[i-1]) * 100
            for i in range(1, len(close_prices))
        ]
        
        volatility = stdev(returns)
        
        if volatility >= min_volatility:
            risk_stocks.append({
                "symbol": company.symbol,
                "name": company.name,
                "sector": company.sector,
                "volatility_30d": round(volatility, 2),
                "current_price": round(prices[0].close, 2),
                "price_change_30d": round(
                    ((prices[0].close - prices[-1].close) / prices[-1].close) * 100, 2
                )
            })
    
    risk_stocks.sort(key=lambda x: x['volatility_30d'], reverse=True)
    risk_stocks = risk_stocks[:limit]
    
    if not risk_stocks:
        raise HTTPException(
            status_code=404,
            detail=f"No high-risk stocks found with volatility >= {min_volatility}%"
        )
    
    return {
        "criteria": {
            "min_volatility_percent": min_volatility,
            "limit": limit
        },
        "found": len(risk_stocks),
        "high_risk_stocks": risk_stocks
    }


# ============================================================================
# PORTFOLIO ANALYTICS
# ============================================================================

@app.get("/analytics/portfolio/performance", tags=["Portfolio"])
def get_portfolio_performance(
    symbols: str = Query(..., description="Comma-separated symbols"),
    db: Session = Depends(get_db)
):
    """
    Analyze portfolio performance metrics
    
    Supports formats:
    - AAPL,MSFT,GOOGL
    - AAPL, MSFT, GOOGL
    """
    
    symbols_clean = symbols.strip().replace(' ', '').replace(',', ',')
    symbol_list = [s.strip().upper() for s in symbols_clean.split(',') if s.strip()]
    
    if not symbol_list:
        raise HTTPException(status_code=400, detail="No valid symbols provided")
    
    portfolio_data = []
    total_market_cap = 0
    
    for symbol in symbol_list:
        company = db.query(models.Company).filter(
            models.Company.symbol == symbol
        ).first()
        
        if not company:
            continue
        
        financial = db.query(models.FinancialMetric).filter(
            models.FinancialMetric.company_id == company.id
        ).order_by(desc(models.FinancialMetric.date)).first()
        
        prices = db.query(models.StockPrice).filter(
            models.StockPrice.company_id == company.id
        ).order_by(desc(models.StockPrice.date)).limit(30).all()
        
        if not prices:
            continue
        
        price_change = ((prices[0].close - prices[-1].close) / prices[-1].close) * 100 if len(prices) >= 2 else 0
        
        portfolio_data.append({
            "symbol": symbol,
            "name": company.name,
            "sector": company.sector,
            "market_cap": company.market_cap,
            "current_price": round(prices[0].close, 2),
            "price_change_30d": round(price_change, 2),
            "pe_ratio": round(financial.pe_ratio, 2) if financial and financial.pe_ratio else None,
            "eps": round(financial.eps, 2) if financial and financial.eps else None
        })
        
        if company.market_cap:
            total_market_cap += company.market_cap
    
    if not portfolio_data:
        raise HTTPException(
            status_code=404,
            detail="No data found for provided symbols"
        )
    
    weighted_return = sum(
        (p['price_change_30d'] or 0) * (p['market_cap'] / total_market_cap)
        for p in portfolio_data if p['market_cap']
    )
    
    return {
        "portfolio_symbols": symbol_list,
        "found_companies": len(portfolio_data),
        "total_market_cap": total_market_cap,
        "weighted_avg_return_30d": round(weighted_return, 2),
        "companies": portfolio_data
    }


# ============================================================================
# SECTOR ANALYTICS
# ============================================================================

@app.get("/analytics/sectors/comparison", tags=["Sector Analysis"])
def get_sector_comparison(db: Session = Depends(get_db)):
    """Compare average financial metrics across sectors"""
    
    results = db.query(
        models.Company.sector,
        func.avg(models.FinancialMetric.pe_ratio).label('avg_pe'),
        func.avg(models.FinancialMetric.eps).label('avg_eps'),
        func.avg(models.FinancialMetric.profit_margin).label('avg_margin'),
        func.count(models.Company.id).label('company_count')
    ).join(models.FinancialMetric).group_by(models.Company.sector).all()
    
    if not results:
        raise HTTPException(status_code=404, detail="No financial data available")
    
    sectors = [
        {
            "sector": r.sector,
            "avg_pe_ratio": round(r.avg_pe, 2) if r.avg_pe else None,
            "avg_eps": round(r.avg_eps, 2) if r.avg_eps else None,
            "avg_profit_margin": round(r.avg_margin * 100, 2) if r.avg_margin else None,
            "company_count": r.company_count
        }
        for r in results
    ]
    
    return {
        "total_sectors": len(results),
        "sectors": sectors
    }


@app.get("/sectors/", tags=["Sectors"])
def get_sectors(db: Session = Depends(get_db)):
    """Get list of all available sectors"""
    
    sector_counts = db.query(
        models.Company.sector,
        func.count(models.Company.id).label('count')
    ).group_by(models.Company.sector).all()
    
    return {
        "total_sectors": len(sector_counts),
        "sectors": [
            {"name": sc.sector, "company_count": sc.count}
            for sc in sector_counts if sc.sector
        ]
    }

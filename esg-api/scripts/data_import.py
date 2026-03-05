"""
Data import script using FREE Yahoo Finance ESG data
No API keys required!
"""

import yesg
import yfinance as yf
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from app.database import SessionLocal, engine
from app.models import Company, ESGScore, FinancialMetric, StockPrice
import time

# List of companies across different sectors (50 companies)
COMPANIES = {
    'Technology': ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'TSLA', 'AMD', 'INTC', 'CRM', 'ORCL'],
    'Finance': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SCHW', 'USB'],
    'Healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'ABT', 'MRK', 'LLY', 'BMY', 'AMGN'],
    'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HAL'],
    'Consumer': ['AMZN', 'WMT', 'HD', 'PG', 'KO', 'PEP', 'COST', 'NKE', 'MCD', 'SBUX']
}

def import_company_data(symbol: str, sector: str, db: Session):
    """Import company basic information"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Check if company already exists
        existing = db.query(Company).filter(Company.symbol == symbol).first()
        if existing:
            print(f"  ⏭️  {symbol} already exists, skipping...")
            return existing
        
        # Create company record
        company = Company(
            symbol=symbol,
            name=info.get('longName', symbol),
            sector=sector,
            industry=info.get('industry', 'Unknown'),
            market_cap=info.get('marketCap', 0)
        )
        
        db.add(company)
        db.commit()
        db.refresh(company)
        
        print(f"  ✅ Imported {symbol} - {company.name}")
        return company
        
    except Exception as e:
        print(f"  ❌ Error importing {symbol}: {e}")
        return None

def import_esg_data(symbol: str, company_id: int, db: Session):
    """Import ESG scores from Yahoo Finance (FREE!)"""
    try:
        # Get ESG data using yesg library
        esg_data = yesg.get_esg_full(symbol)
        
        if esg_data is None or esg_data.empty:
            print(f"    ⚠️  No ESG data available for {symbol}")
            return
        
        # Extract ESG scores
        total_score = esg_data.get('Total-Score', [None])[0]
        env_score = esg_data.get('E-Score', [None])[0]
        social_score = esg_data.get('S-Score', [None])[0]
        gov_score = esg_data.get('G-Score', [None])[0]
        
        # Get controversy score if available
        controversy = esg_data.get('Highest Controversy', [0])[0]
        
        # Check if ESG data already exists
        existing = db.query(ESGScore).filter(
            ESGScore.company_id == company_id,
            ESGScore.date == date.today()
        ).first()
        
        if existing:
            print(f"    ⏭️  ESG data for {symbol} already exists")
            return
        
        # Create ESG score record
        esg_score = ESGScore(
            company_id=company_id,
            environmental_score=float(env_score) if env_score else None,
            social_score=float(social_score) if social_score else None,
            governance_score=float(gov_score) if gov_score else None,
            total_esg_score=float(total_score) if total_score else None,
            carbon_intensity=None,  # Not available in free tier
            controversy_score=float(controversy) if controversy else 0.0,
            date=date.today()
        )
        
        db.add(esg_score)
        db.commit()
        
        print(f"    ✅ ESG scores imported for {symbol}")
        
    except Exception as e:
        print(f"    ❌ Error importing ESG for {symbol}: {e}")

def import_financial_data(symbol: str, company_id: int, db: Session):
    """Import financial metrics from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Check if financial data already exists
        existing = db.query(FinancialMetric).filter(
            FinancialMetric.company_id == company_id,
            FinancialMetric.date == date.today()
        ).first()
        
        if existing:
            print(f"    ⏭️  Financial data for {symbol} already exists")
            return
        
        # Create financial metrics record
        financial = FinancialMetric(
            company_id=company_id,
            pe_ratio=info.get('trailingPE'),
            eps=info.get('trailingEps'),
            revenue=info.get('totalRevenue'),
            profit_margin=info.get('profitMargins'),
            debt_to_equity=info.get('debtToEquity'),
            date=date.today()
        )
        
        db.add(financial)
        db.commit()
        
        print(f"    ✅ Financial data imported for {symbol}")
        
    except Exception as e:
        print(f"    ❌ Error importing financials for {symbol}: {e}")

def import_stock_prices(symbol: str, company_id: int, db: Session):
    """Import recent stock price data"""
    try:
        ticker = yf.Ticker(symbol)
        
        # Get last 30 days of price data
        hist = ticker.history(period="1mo")
        
        if hist.empty:
            print(f"    ⚠️  No price data for {symbol}")
            return
        
        # Import each day's data
        for index, row in hist.iterrows():
            price_date = index.date()
            
            # Check if already exists
            existing = db.query(StockPrice).filter(
                StockPrice.company_id == company_id,
                StockPrice.date == price_date
            ).first()
            
            if existing:
                continue
            
            stock_price = StockPrice(
                company_id=company_id,
                date=price_date,
                open=row['Open'],
                close=row['Close'],
                volume=int(row['Volume'])
            )
            
            db.add(stock_price)
        
        db.commit()
        print(f"    ✅ Stock prices imported for {symbol}")
        
    except Exception as e:
        print(f"    ❌ Error importing prices for {symbol}: {e}")

def run_full_import():
    """Run complete data import"""
    db = SessionLocal()
    
    print("\n" + "="*60)
    print("🚀 Starting ESG Data Import (FREE Yahoo Finance Data)")
    print("="*60 + "\n")
    
    total_companies = sum(len(symbols) for symbols in COMPANIES.values())
    current = 0
    
    for sector, symbols in COMPANIES.items():
        print(f"\n📊 Importing {sector} sector...")
        
        for symbol in symbols:
            current += 1
            print(f"\n[{current}/{total_companies}] Processing {symbol}...")
            
            # Import company info
            company = import_company_data(symbol, sector, db)
            
            if company:
                # Import ESG scores (FREE!)
                import_esg_data(symbol, company.id, db)
                
                # Import financial metrics
                import_financial_data(symbol, company.id, db)
                
                # Import stock prices
                import_stock_prices(symbol, company.id, db)
            
            # Sleep to avoid rate limiting
            time.sleep(1)
    
    db.close()
    
    print("\n" + "="*60)
    print("✅ Data import completed!")
    print("="*60)
    print(f"\nImported data for {total_companies} companies across 5 sectors")

if __name__ == "__main__":
    run_full_import()

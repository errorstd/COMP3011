"""
Analytics Logic Tests
Tests financial calculation accuracy
"""

import sys
import os

# ✅ FIX: Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import numpy as np
from statistics import stdev
from app.database import SessionLocal
from app.models import Company, FinancialMetric, StockPrice
from datetime import date, timedelta


def test_volatility_calculation():
    """Test volatility calculation formula"""
    # Sample price data
    prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 110]
    
    # Calculate returns
    returns = [
        ((prices[i] - prices[i-1]) / prices[i-1]) * 100
        for i in range(1, len(prices))
    ]
    
    # Calculate volatility
    volatility = stdev(returns)
    
    # Volatility should be positive
    assert volatility > 0
    # Volatility should be reasonable for this data (between 0-10%)
    assert 0 < volatility < 10
    
    print(f"✅ Volatility calculation test passed (volatility: {volatility:.2f}%)")


def test_pe_ratio_classification():
    """Test P/E ratio classification logic"""
    
    def classify_pe(pe_ratio):
        if pe_ratio < 10:
            return "Undervalued"
        elif pe_ratio > 30:
            return "Overvalued"
        else:
            return "Fairly Valued"
    
    assert classify_pe(8.5) == "Undervalued"
    assert classify_pe(15.0) == "Fairly Valued"
    assert classify_pe(45.0) == "Overvalued"
    
    print("✅ P/E ratio classification test passed")


def test_risk_level_classification():
    """Test risk level classification based on volatility"""
    
    def classify_risk(volatility):
        if volatility < 2:
            return "Low"
        elif volatility < 4:
            return "Moderate"
        else:
            return "High"
    
    assert classify_risk(1.5) == "Low"
    assert classify_risk(3.0) == "Moderate"
    assert classify_risk(5.5) == "High"
    
    print("✅ Risk level classification test passed")


def test_price_change_calculation():
    """Test price change percentage calculation"""
    old_price = 100.0
    new_price = 110.0
    
    price_change = ((new_price - old_price) / old_price) * 100
    
    assert price_change == 10.0
    print("✅ Price change calculation test passed")


def test_weighted_portfolio_return():
    """Test weighted average portfolio return calculation"""
    
    # Portfolio with 3 stocks
    portfolio = [
        {"market_cap": 100000000, "return": 5.0},   # 5% return
        {"market_cap": 200000000, "return": 10.0},  # 10% return
        {"market_cap": 100000000, "return": -2.0}   # -2% return
    ]
    
    total_market_cap = sum(p["market_cap"] for p in portfolio)
    
    weighted_return = sum(
        (p["return"] * p["market_cap"] / total_market_cap)
        for p in portfolio
    )
    
    # Expected: (5*100 + 10*200 + -2*100) / 400 = 5.75%
    expected = 5.75
    assert abs(weighted_return - expected) < 0.01
    
    print(f"✅ Weighted portfolio return test passed (return: {weighted_return:.2f}%)")


def test_numpy_conversion():
    """Test numpy type conversion for JSON serialization"""
    
    def convert_numpy(value):
        if value is None:
            return None
        if isinstance(value, (np.integer, np.floating)):
            return float(value)
        return value
    
    # Test various numpy types
    assert convert_numpy(np.int64(42)) == 42.0
    assert convert_numpy(np.float64(3.14)) == 3.14
    assert convert_numpy(None) is None
    assert convert_numpy(100) == 100
    
    print("✅ Numpy conversion test passed")


def test_database_query_logic():
    """Test database query returns expected structure"""
    db = SessionLocal()
    
    try:
        # Test that query returns list
        companies = db.query(Company).limit(5).all()
        assert isinstance(companies, list)
        
        # Test that each company has required attributes
        if len(companies) > 0:
            company = companies[0]
            assert hasattr(company, 'symbol')
            assert hasattr(company, 'name')
            assert hasattr(company, 'sector')
        
        print(f"✅ Database query logic test passed ({len(companies)} companies found)")
        
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 Running Analytics Logic Tests")
    print("="*70 + "\n")
    
    test_volatility_calculation()
    test_pe_ratio_classification()
    test_risk_level_classification()
    test_price_change_calculation()
    test_weighted_portfolio_return()
    test_numpy_conversion()
    test_database_query_logic()
    
    print("\n" + "="*70)
    print("✅ All analytics tests passed!")
    print("="*70)

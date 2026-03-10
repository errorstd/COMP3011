"""
API Endpoint Tests
Tests REST API functionality using FastAPI TestClient
"""

import sys
import os

# ✅ FIX: Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import Company, FinancialMetric, StockPrice

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint health check"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "Stock Valuation & Risk Analytics API" in data["message"]
    print("✅ Root endpoint test passed")


def test_get_companies_empty():
    """Test getting companies when database might be empty"""
    response = client.get("/companies/")
    assert response.status_code == 200
    data = response.json()
    assert "companies" in data
    assert isinstance(data["companies"], list)
    print(f"✅ Get companies test passed (found {len(data['companies'])} companies)")


def test_get_specific_company():
    """Test getting a specific company by symbol"""
    # First, get list of companies
    response = client.get("/companies/")
    data = response.json()
    
    if len(data["companies"]) > 0:
        symbol = data["companies"][0]["symbol"]
        
        # Test getting specific company
        response = client.get(f"/companies/?symbol={symbol}")
        assert response.status_code == 200
        company_data = response.json()
        assert company_data["mode"] == "single"
        assert company_data["company"]["symbol"] == symbol
        print(f"✅ Get specific company test passed ({symbol})")
    else:
        print("⏭️  Skipping specific company test (no companies in DB)")


def test_get_nonexistent_company():
    """Test getting a company that doesn't exist"""
    response = client.get("/companies/?symbol=NONEXISTENT999")
    assert response.status_code == 404
    print("✅ Nonexistent company test passed (404 returned correctly)")


def test_get_sectors():
    """Test getting all sectors"""
    response = client.get("/sectors/")
    assert response.status_code == 200
    data = response.json()
    assert "sectors" in data
    assert isinstance(data["sectors"], list)
    print(f"✅ Get sectors test passed (found {data['total_sectors']} sectors)")


def test_get_categories():
    """Test browse categories endpoint"""
    response = client.get("/browse/categories")
    assert response.status_code == 200
    data = response.json()
    assert "sectors" in data
    assert "industries" in data
    print("✅ Get categories test passed")


def test_search_stocks():
    """Test stock search functionality"""
    # Get a company to search for
    response = client.get("/companies/")
    data = response.json()
    
    if len(data["companies"]) > 0:
        # Search by partial symbol
        symbol = data["companies"][0]["symbol"]
        search_term = symbol[:3]  # First 3 letters
        
        response = client.get(f"/browse/search?query={search_term}")
        # Should be 200 or 404 (both acceptable if no matches)
        assert response.status_code in [200, 404]
        print(f"✅ Search stocks test passed (searched for '{search_term}')")
    else:
        print("⏭️  Skipping search test (no companies in DB)")


def test_undervalued_stocks():
    """Test undervalued stocks endpoint"""
    response = client.get("/analytics/valuation/undervalued?limit=5&max_pe=15")
    # Should be 200 or 404 (acceptable if no undervalued stocks)
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert "undervalued_stocks" in data
        print(f"✅ Undervalued stocks test passed (found {data['found']})")
    else:
        print("⏭️  No undervalued stocks found (acceptable)")


def test_overvalued_stocks():
    """Test overvalued stocks endpoint"""
    response = client.get("/analytics/valuation/overvalued?limit=5&min_pe=30")
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert "overvalued_stocks" in data
        print(f"✅ Overvalued stocks test passed (found {data['found']})")
    else:
        print("⏭️  No overvalued stocks found (acceptable)")


def test_sector_comparison():
    """Test sector comparison analytics"""
    response = client.get("/analytics/sectors/comparison")
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert "sectors" in data
        print(f"✅ Sector comparison test passed ({data['total_sectors']} sectors)")
    else:
        print("⏭️  No financial data for sector comparison (acceptable)")


def test_volatility_endpoint():
    """Test volatility calculation endpoint"""
    # Get a company with data
    response = client.get("/companies/")
    data = response.json()
    
    if len(data["companies"]) > 0:
        symbol = data["companies"][0]["symbol"]
        
        response = client.get(f"/analytics/risk/volatility/{symbol}")
        # Could be 200, 404, or 400 (insufficient data)
        assert response.status_code in [200, 400, 404]
        
        if response.status_code == 200:
            volatility_data = response.json()
            assert "volatility" in volatility_data
            print(f"✅ Volatility test passed ({symbol})")
        else:
            print(f"⏭️  Volatility test skipped ({symbol} - insufficient data)")
    else:
        print("⏭️  Skipping volatility test (no companies in DB)")


def test_invalid_endpoints():
    """Test that invalid endpoints return 404"""
    response = client.get("/invalid/endpoint/that/does/not/exist")
    assert response.status_code == 404
    print("✅ Invalid endpoint test passed (404 returned)")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 Running API Endpoint Tests")
    print("="*70 + "\n")
    
    test_root_endpoint()
    test_get_companies_empty()
    test_get_specific_company()
    test_get_nonexistent_company()
    test_get_sectors()
    test_get_categories()
    test_search_stocks()
    test_undervalued_stocks()
    test_overvalued_stocks()
    test_sector_comparison()
    test_volatility_endpoint()
    test_invalid_endpoints()
    
    print("\n" + "="*70)
    print("✅ All API tests completed!")
    print("="*70)

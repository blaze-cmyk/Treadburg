"""
SEC route for fetching financial data
"""

from fastapi import APIRouter, HTTPException
from services.sec_client import sec_client
from services.sec_parser import extract_financials

router = APIRouter()


@router.get("/financials/{ticker}")
async def get_financials(ticker: str):
    """
    Get financial data for a ticker from SEC EDGAR
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
        
    Returns:
        Structured financial data
    """
    # Fetch company facts from SEC
    company_facts = await sec_client.get_company_facts(ticker.upper())
    
    if not company_facts:
        raise HTTPException(status_code=404, detail=f"Financial data not found for ticker: {ticker}")
    
    # Parse and extract financials
    financials = extract_financials(company_facts)
    
    return financials

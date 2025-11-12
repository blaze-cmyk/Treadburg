#!/usr/bin/env python3
"""
Test the enhanced financial analysis capabilities
"""

import requests
import json

def test_financial_queries():
    """Test various financial analysis queries"""
    print("🧪 TESTING FINANCIAL ANALYSIS CAPABILITIES")
    print("=" * 60)
    
    test_queries = [
        # Price requests
        "tell me the current price of BTCUSDT",
        "tell me the current price of AAPL", 
        "current price of NVDA",
        
        # SEC filings
        "SEC 10-Q latest for NFLX: revenue, subs adds, margin, guidance",
        "Latest SEC filing for AAPL with revenue breakdown",
        
        # Comparative analysis
        "Compare AAPL vs MSFT: last close, EV/S, EV/EBITDA, P/E, FCF margin",
        "NVDA vs AMD vs AVGO revenue growth and valuation metrics",
        "SPY vs QQQ vs DIA returns and risk over 1Y",
        
        # Market structure
        "BTC vs ETH last 90d: return, realized vol, correlation",
        "TSLA vs NVDA options positioning and gamma walls",
        
        # Deep research
        "Deep research: NVDA latest 10-K guidance and margin trajectory",
        "Top 20 US tickers by market cap reporting next 7 days"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: '{query}'")
        
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ],
            "model": "gpt-4o",
            "temperature": 0.1,
            "enable_functions": True
        }
        
        try:
            response = requests.post(
                'http://localhost:8080/api/tradeberg/enhanced-chat',
                json=payload,
                timeout=90
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Success: {result.get('success')}")
                print(f"   Function: {result.get('function_called')}")
                
                response_text = result.get('response', '')
                if response_text:
                    print(f"   Length: {len(response_text)} chars")
                    
                    # Check for financial analysis features
                    if "FINANCIAL ANALYSIS" in response_text:
                        print("   ✅ FINANCIAL ANALYSIS FORMAT")
                    elif "PRICE DATA" in response_text:
                        print("   ✅ PRICE DATA FORMAT")
                    elif "CRYPTO ANALYSIS" in response_text:
                        print("   ✅ CRYPTO ANALYSIS FORMAT")
                    else:
                        print("   ⚠️ BASIC FORMAT")
                    
                    # Check for key features
                    features = []
                    if "SEC" in response_text or "10-K" in response_text or "10-Q" in response_text:
                        features.append("SEC_FILINGS")
                    if "P/E" in response_text or "EV/S" in response_text or "valuation" in response_text.lower():
                        features.append("VALUATION")
                    if "$" in response_text or "price" in response_text.lower():
                        features.append("PRICING")
                    if "table" in response_text.lower() or "|" in response_text:
                        features.append("TABLES")
                    if "http" in response_text.lower() or "url" in response_text.lower():
                        features.append("CITATIONS")
                    
                    if features:
                        print(f"   📊 Features: {', '.join(features)}")
                    
                    print(f"   Preview: {response_text[:150]}...")
                else:
                    print("   ❌ EMPTY RESPONSE")
            else:
                print(f"   ❌ ERROR: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)[:100]}...")

if __name__ == "__main__":
    print("🔍 FINANCIAL ANALYSIS CAPABILITY TEST")
    print("=" * 70)
    
    test_financial_queries()
    
    print("\n" + "=" * 70)
    print("📋 TEST COMPLETE")
    print("✅ Look for:")
    print("   - FINANCIAL ANALYSIS / PRICE DATA / CRYPTO ANALYSIS headers")
    print("   - SEC filing information and URLs")
    print("   - Valuation metrics (P/E, EV/S, etc.)")
    print("   - Real-time pricing data")
    print("   - Comparative tables")
    print("   - Source citations")
    print("\n🎯 Your system should now handle all financial queries!")

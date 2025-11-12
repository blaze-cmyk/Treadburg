"""
Test script to verify Binance data flows through TradeBerg chat
Tests the complete flow: Frontend → Backend → Binance → AI → Response
"""

import sys
import os
import json
import requests
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_chat_endpoint():
    """Test the main chat endpoint that users interact with"""
    print("=" * 70)
    print("TESTING TRADEBERG CHAT → BINANCE DATA FLOW")
    print("=" * 70)
    
    # Test endpoint
    url = "http://localhost:8080/api/chat/completions"
    
    # Test message asking about BTC
    test_message = "What's the current price of BTC?"
    
    print(f"\n📤 Sending test message: '{test_message}'")
    print(f"📍 Endpoint: {url}")
    
    payload = {
        "model": "tradeberg",
        "messages": [
            {"role": "user", "content": test_message}
        ],
        "stream": False
    }
    
    try:
        print("\n🔄 Making request to chat endpoint...")
        response = requests.post(
            url,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Chat endpoint responded successfully!")
            
            try:
                data = response.json()
                
                # Check if response contains Binance data indicators
                response_text = ""
                if "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    if "message" in choice:
                        response_text = choice["message"].get("content", "")
                    elif "text" in choice:
                        response_text = choice.get("text", "")
                
                print(f"\n📊 Response received ({len(response_text)} characters)")
                
                # Check for Binance data indicators
                indicators = {
                    "price_mentioned": any(x in response_text.lower() for x in ["$", "price", "btc"]),
                    "has_numbers": any(char.isdigit() for char in response_text),
                    "has_tradeberg": "TRADEBERG" in response_text,
                    "has_market_data": any(x in response_text.lower() for x in ["volume", "change", "high", "low"]),
                    "has_charts": "```json:chart:" in response_text
                }
                
                print("\n🔍 Binance Data Indicators:")
                for indicator, present in indicators.items():
                    status = "✅" if present else "❌"
                    print(f"   {status} {indicator.replace('_', ' ').title()}: {present}")
                
                # Show sample of response
                print(f"\n📝 Response Preview (first 500 chars):")
                print("-" * 70)
                print(response_text[:500])
                if len(response_text) > 500:
                    print("...")
                print("-" * 70)
                
                # Overall assessment
                if all(indicators.values()):
                    print("\n🎉 SUCCESS: Binance data is flowing through TradeBerg chat!")
                elif indicators["has_tradeberg"] and indicators["price_mentioned"]:
                    print("\n✅ PARTIAL: TradeBerg is responding with price data")
                else:
                    print("\n⚠️ WARNING: Response may not contain Binance data")
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON response: {e}")
                print(f"Raw response: {response.text[:500]}")
                
        else:
            print(f"❌ Chat endpoint returned error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server")
        print("   Make sure the server is running on http://localhost:8080")
        print("   Start it with: python -m uvicorn main:app --reload --port 8080")
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out (>30s)")
    except Exception as e:
        print(f"❌ ERROR: {e}")


def test_realtime_data_endpoint():
    """Test the direct Binance data endpoint"""
    print("\n" + "=" * 70)
    print("TESTING DIRECT BINANCE DATA ENDPOINT")
    print("=" * 70)
    
    url = "http://localhost:8080/api/tradeberg/realtime-data/BTC"
    
    print(f"\n📍 Endpoint: {url}")
    
    try:
        print("🔄 Fetching real-time BTC data...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success") and "data" in data:
                market_data = data["data"]
                
                print("✅ Real-time data endpoint working!")
                print(f"\n📊 Live Binance Data:")
                print(f"   Symbol: {market_data.get('symbol', 'N/A')}")
                print(f"   Price: ${market_data.get('price', {}).get('current', 0):,.2f}")
                print(f"   24h Change: {market_data.get('price', {}).get('change_24h', 0):.2f}%")
                print(f"   24h Volume: ${market_data.get('price', {}).get('quote_volume_24h', 0)/1e9:.2f}B")
                print(f"   Buy Pressure: {market_data.get('volume_metrics', {}).get('buy_pressure', 0):.1f}%")
                print(f"   Liquidity: {market_data.get('liquidity', {}).get('liquidity_level', 'N/A')}")
                
                return True
            else:
                print("❌ Unexpected response format")
                return False
        else:
            print(f"❌ Endpoint returned error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_symbol_detection():
    """Test if symbol detection is working"""
    print("\n" + "=" * 70)
    print("TESTING SYMBOL DETECTION")
    print("=" * 70)
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    
    try:
        from open_webui.utils.realtime_data_injector import extract_symbols
        
        test_cases = [
            "What's the price of BTC?",
            "Compare ETH and SOL",
            "Analyze BTCUSDT chart",
            "How is Bitcoin doing?",
            "Show me Ethereum price"
        ]
        
        print("\n🔍 Testing symbol extraction:")
        all_passed = True
        
        for test in test_cases:
            symbols = extract_symbols(test)
            status = "✅" if symbols else "❌"
            print(f"   {status} '{test}' → {symbols}")
            if not symbols and any(x in test.lower() for x in ["btc", "eth", "sol", "bitcoin", "ethereum"]):
                all_passed = False
        
        if all_passed:
            print("\n✅ Symbol detection working correctly!")
        else:
            print("\n⚠️ Some symbols not detected")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")


def main():
    print("\n🚀 TRADEBERG CHAT → BINANCE DATA FLOW TEST")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Symbol detection
    test_symbol_detection()
    
    # Test 2: Direct Binance endpoint
    binance_working = test_realtime_data_endpoint()
    
    # Test 3: Main chat endpoint
    test_chat_endpoint()
    
    print("\n" + "=" * 70)
    print("✅ TEST SUITE COMPLETE")
    print("=" * 70)
    
    print("\n📋 SUMMARY:")
    print("   1. Symbol Detection: Tests if BTC/ETH/SOL are detected in messages")
    print("   2. Binance Endpoint: Tests if real-time data is fetched from Binance")
    print("   3. Chat Flow: Tests if Binance data flows through chat responses")
    
    print("\n🔗 INTEGRATION FLOW:")
    print("   User Message → Symbol Detection → Binance API → Data Injection → AI Response")
    
    print("\n💡 WHAT TO LOOK FOR:")
    print("   ✅ TRADEBERG prefix in responses")
    print("   ✅ Real-time price data ($XX,XXX.XX)")
    print("   ✅ Market metrics (volume, change%, buy pressure)")
    print("   ✅ Visual charts (```json:chart:candlestick```)")
    
    if binance_working:
        print("\n🎉 Binance is connected and data is flowing!")
    else:
        print("\n⚠️ Check if server is running: python -m uvicorn main:app --reload --port 8080")


if __name__ == "__main__":
    main()

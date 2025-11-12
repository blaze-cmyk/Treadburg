"""
Test Binance Integration in TradeBerg Chat
Verifies that pricing data comes from Binance API
"""

import requests
import json
import time

def test_binance_integration():
    """Test if Binance data appears in chat responses"""
    
    print("=" * 70)
    print("🧪 TESTING BINANCE INTEGRATION IN CHAT")
    print("=" * 70)
    
    # Test endpoint
    url = "http://localhost:8080/api/tradeberg/enforced/chat/completions"
    
    test_cases = [
        {
            "name": "BTC Price Query",
            "message": "What is the current price of BTC?",
            "expected_symbol": "BTC"
        },
        {
            "name": "ETH Price Query",
            "message": "Tell me the price of Ethereum",
            "expected_symbol": "ETH"
        },
        {
            "name": "SOL Analysis",
            "message": "Analyze SOL price action",
            "expected_symbol": "SOL"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─' * 70}")
        print(f"Test {i}/{len(test_cases)}: {test['name']}")
        print(f"{'─' * 70}")
        print(f"📤 Query: '{test['message']}'")
        print(f"🎯 Expected Symbol: {test['expected_symbol']}")
        
        payload = {
            "model": "tradeberg",
            "messages": [
                {"role": "user", "content": test["message"]}
            ],
            "stream": False
        }
        
        try:
            print("\n⏳ Sending request...")
            start_time = time.time()
            
            response = requests.post(
                url,
                json=payload,
                timeout=60
            )
            
            elapsed = time.time() - start_time
            print(f"⏱️  Response time: {elapsed:.2f}s")
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract response text
                response_text = ""
                if "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    if "message" in choice:
                        response_text = choice["message"].get("content", "")
                
                print(f"\n✅ Response received ({len(response_text)} characters)")
                
                # Check for Binance indicators
                binance_indicators = {
                    "has_price": "$" in response_text and any(char.isdigit() for char in response_text),
                    "has_binance_badge": "Binance API" in response_text or "Live Data" in response_text,
                    "has_symbol": test['expected_symbol'] in response_text.upper(),
                    "has_24h_change": "24h" in response_text or "change" in response_text.lower(),
                    "has_volume": "volume" in response_text.lower(),
                    "has_tradeberg": "TRADEBERG" in response_text
                }
                
                print("\n🔍 Binance Data Indicators:")
                for indicator, present in binance_indicators.items():
                    status = "✅" if present else "❌"
                    print(f"   {status} {indicator.replace('_', ' ').title()}: {present}")
                
                # Show response preview
                print(f"\n📝 Response Preview:")
                print("─" * 70)
                preview_lines = response_text.split('\n')[:15]  # First 15 lines
                for line in preview_lines:
                    print(line[:70])  # Truncate long lines
                if len(response_text.split('\n')) > 15:
                    print("...")
                print("─" * 70)
                
                # Overall assessment
                if binance_indicators["has_binance_badge"]:
                    print("\n🎉 SUCCESS: Binance data is being used!")
                elif binance_indicators["has_price"] and binance_indicators["has_symbol"]:
                    print("\n✅ PARTIAL: Response has price data (check if from Binance)")
                else:
                    print("\n⚠️ WARNING: May not be using Binance data")
                
            else:
                print(f"\n❌ Error: HTTP {response.status_code}")
                print(f"Response: {response.text[:500]}")
                
        except requests.exceptions.ConnectionError:
            print("\n❌ ERROR: Cannot connect to server")
            print("   Start server: python -m uvicorn main:app --reload --port 8080")
            break
        except requests.exceptions.Timeout:
            print("\n❌ ERROR: Request timeout (>60s)")
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
        
        # Wait between tests
        if i < len(test_cases):
            print("\n⏸️  Waiting 2 seconds before next test...")
            time.time()


def test_direct_binance():
    """Quick test of direct Binance endpoint"""
    print("\n" + "=" * 70)
    print("🔧 TESTING DIRECT BINANCE ENDPOINT")
    print("=" * 70)
    
    url = "http://localhost:8080/api/tradeberg/realtime-data/BTC"
    
    try:
        print(f"\n📍 Endpoint: {url}")
        print("⏳ Fetching...")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                market_data = data["data"]
                print(f"\n✅ Binance API Working!")
                print(f"   Price: ${market_data['price']['current']:,.2f}")
                print(f"   24h Change: {market_data['price']['change_24h']:+.2f}%")
                return True
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("\n🚀 BINANCE CHAT INTEGRATION TEST")
    print(f"⏰ Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # First, verify Binance endpoint works
    binance_working = test_direct_binance()
    
    if not binance_working:
        print("\n⚠️ WARNING: Direct Binance endpoint not working")
        print("   Chat integration test may fail")
    
    # Test chat integration
    test_binance_integration()
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)
    
    print("\n📋 WHAT TO LOOK FOR:")
    print("   ✅ '🔴 Live Data: Prices from Binance API' badge")
    print("   ✅ Exact prices with $ symbol")
    print("   ✅ 24h change percentages")
    print("   ✅ Volume data")
    print("   ✅ TRADEBERG prefix")
    
    print("\n💡 VERIFICATION:")
    print("   If you see the Binance badge → Integration working!")
    print("   If no badge → Check server logs for errors")


if __name__ == "__main__":
    main()

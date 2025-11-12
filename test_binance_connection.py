"""
Test script to verify Binance API connectivity and data fetching
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from open_webui.utils.realtime_data_aggregator import (
    BinanceAPI, 
    get_realtime_market_data,
    get_comparison_data
)

def test_binance_api():
    """Test Binance API directly"""
    print("=" * 60)
    print("TESTING BINANCE API CONNECTION")
    print("=" * 60)
    
    binance = BinanceAPI()
    
    # Test 1: Get current price
    print("\n📊 Test 1: Fetching BTC current price...")
    try:
        price_data = binance.get_current_price("BTCUSDT")
        if price_data:
            print(f"✅ SUCCESS: BTC Price = ${float(price_data['price']):,.2f}")
        else:
            print("❌ FAILED: No price data returned")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 2: Get 24h ticker
    print("\n📈 Test 2: Fetching 24h ticker data...")
    try:
        ticker = binance.get_24h_ticker("BTCUSDT")
        if ticker:
            print(f"✅ SUCCESS:")
            print(f"   - High: ${float(ticker['highPrice']):,.2f}")
            print(f"   - Low: ${float(ticker['lowPrice']):,.2f}")
            print(f"   - Change: {float(ticker['priceChangePercent']):.2f}%")
            print(f"   - Volume: {float(ticker['volume']):,.2f} BTC")
        else:
            print("❌ FAILED: No ticker data returned")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 3: Get klines (candlestick data)
    print("\n🕯️ Test 3: Fetching candlestick data...")
    try:
        klines = binance.get_klines("BTCUSDT", interval="1h", limit=5)
        if klines:
            print(f"✅ SUCCESS: Retrieved {len(klines)} candles")
            print(f"   Latest candle close: ${float(klines[-1][4]):,.2f}")
        else:
            print("❌ FAILED: No kline data returned")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 4: Get order book
    print("\n📖 Test 4: Fetching order book...")
    try:
        order_book = binance.get_order_book("BTCUSDT", limit=10)
        if order_book and 'bids' in order_book and 'asks' in order_book:
            print(f"✅ SUCCESS:")
            print(f"   - Bids: {len(order_book['bids'])} levels")
            print(f"   - Asks: {len(order_book['asks'])} levels")
            if order_book['bids'] and order_book['asks']:
                print(f"   - Best Bid: ${float(order_book['bids'][0][0]):,.2f}")
                print(f"   - Best Ask: ${float(order_book['asks'][0][0]):,.2f}")
        else:
            print("❌ FAILED: No order book data returned")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 5: Get recent trades
    print("\n💱 Test 5: Fetching recent trades...")
    try:
        trades = binance.get_recent_trades("BTCUSDT", limit=5)
        if trades:
            print(f"✅ SUCCESS: Retrieved {len(trades)} recent trades")
            print(f"   Latest trade: ${float(trades[-1]['price']):,.2f} @ {float(trades[-1]['qty']):.4f} BTC")
        else:
            print("❌ FAILED: No trade data returned")
    except Exception as e:
        print(f"❌ ERROR: {e}")


def test_comprehensive_data():
    """Test comprehensive data aggregation"""
    print("\n" + "=" * 60)
    print("TESTING COMPREHENSIVE DATA AGGREGATION")
    print("=" * 60)
    
    print("\n🔄 Fetching comprehensive market data for BTC...")
    try:
        data = get_realtime_market_data("BTC")
        if data:
            print(f"✅ SUCCESS: Comprehensive data retrieved")
            print(f"\n📊 Summary:")
            print(f"   Symbol: {data['symbol']}")
            print(f"   Price: ${data['price']['current']:,.2f}")
            print(f"   24h Change: {data['price']['change_24h']:.2f}%")
            print(f"   24h Volume: ${data['price']['quote_volume_24h']/1e9:.2f}B")
            print(f"   Buy Pressure: {data['volume_metrics']['buy_pressure']:.1f}%")
            print(f"   Liquidity Level: {data['liquidity']['liquidity_level']}")
            print(f"   Candlesticks: {len(data['candlestick_data'])} candles")
        else:
            print("❌ FAILED: No comprehensive data returned")
    except Exception as e:
        print(f"❌ ERROR: {e}")


def test_comparison_data():
    """Test comparison data for multiple symbols"""
    print("\n" + "=" * 60)
    print("TESTING MULTI-SYMBOL COMPARISON")
    print("=" * 60)
    
    symbols = ["BTC", "ETH", "SOL"]
    print(f"\n🔄 Fetching comparison data for {', '.join(symbols)}...")
    try:
        data = get_comparison_data(symbols)
        if data:
            print(f"✅ SUCCESS: Retrieved data for {len(data)} symbols")
            print(f"\n📊 Comparison:")
            for item in data:
                print(f"   {item['symbol']}: ${item['price']:,.2f} ({item['change_24h']:+.2f}%) - Buy Pressure: {item['buy_pressure']:.1f}%")
        else:
            print("❌ FAILED: No comparison data returned")
    except Exception as e:
        print(f"❌ ERROR: {e}")


def main():
    print("\n🚀 BINANCE CONNECTIVITY TEST")
    print("Testing if Binance API is correctly configured and data is coming through...\n")
    
    # Run all tests
    test_binance_api()
    test_comprehensive_data()
    test_comparison_data()
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETE")
    print("=" * 60)
    print("\nIf all tests passed, Binance is correctly configured!")
    print("If any tests failed, check:")
    print("  1. Internet connection")
    print("  2. Binance API availability")
    print("  3. API keys (if using authenticated endpoints)")
    print("  4. Rate limits")


if __name__ == "__main__":
    main()

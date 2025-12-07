import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.market_data_service import market_data_service

async def test():
    print("=== TESTING MARKET DATA SERVICE ===")
    
    # 1. Test Crypto (BTC/USDT)
    print("\n1. Testing Crypto (BTC/USDT)...")
    btc_price = await market_data_service.get_price("BTC/USDT")
    print(f"BTC Price: {btc_price}")
    
    btc_book = await market_data_service.get_order_book("BTC/USDT")
    if btc_book:
        print(f"BTC Order Book: {len(btc_book['bids'])} bids, {len(btc_book['asks'])} asks")
        print(f"Top Bid: {btc_book['bids'][0]}")
        print(f"Top Ask: {btc_book['asks'][0]}")
    else:
        print("Failed to get BTC order book")

    # 2. Test Stock (TSLA)
    print("\n2. Testing Stock (TSLA)...")
    tsla_price = await market_data_service.get_price("TSLA")
    print(f"TSLA Price: {tsla_price}")
    
    if tsla_price:
        tsla_book = await market_data_service.get_order_book("TSLA")
        print(f"TSLA Book: {tsla_book}")
    else:
        print("TSLA Price unavailable (likely missing Alpaca keys)")

    # 3. Test Snapshot
    print("\n3. Testing Snapshot (ETH)...")
    snapshot = await market_data_service.get_market_snapshot("ETH")
    print(snapshot)

    await market_data_service.close()

if __name__ == "__main__":
    asyncio.run(test())

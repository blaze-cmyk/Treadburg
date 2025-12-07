#!/bin/bash
# Simple curl-based smoke test for on-demand ingestion

echo "🧪 TradeBerg On-Demand Ingestion Curl Test"
echo "=========================================="

TICKERS=("TSLA" "F" "AAPL" "MSFT" "NVDA")

for ticker in "${TICKERS[@]}"; do
  echo ""
  echo "--- Testing $ticker ---"
  
  START=$(date +%s)
  
  RESPONSE=$(curl -s -X POST \
    "http://localhost:8080/api/chat/test-curl/stream" \
    -H "Content-Type: application/json" \
    -d "{\"userPrompt\":\"What is ${ticker} revenue for 2024?\",\"chatId\":\"test-curl\"}")
  
  END=$(date +%s)
  DURATION=$((END - START))
  
  # Extract first 150 chars
  PREVIEW=$(echo "$RESPONSE" | head -c 150)
  
  echo "⏱  Latency: ${DURATION}s"
  echo "📄 Preview: $PREVIEW..."
  
done

echo ""
echo "=========================================="
echo "✅ Test complete. Check backend logs for:"
echo "   🔥 No data for <ticker>, triggering on-demand ingestion..."
echo "   ✅ Retry successful, found <n> chunks"

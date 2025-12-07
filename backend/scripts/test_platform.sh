#!/bin/bash

BASE_URL="http://localhost:8080"

echo "🧪 Starting Full Platform Test..."

# 1. Health Check
echo -e "\n1️⃣  Testing Health Check..."
HEALTH=$(curl -s "$BASE_URL/health")
echo "   Response: $HEALTH"
if [[ "$HEALTH" == *"healthy"* ]]; then
    echo "   ✅ Health Check Passed"
else
    echo "   ❌ Health Check Failed"
    exit 1
fi

# 2. Create Chat
echo -e "\n2️⃣  Creating New Chat..."
CHAT_RES=$(curl -s -X POST "$BASE_URL/api/chat/create" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test Chat"}')
echo "   Response: $CHAT_RES"

# Extract Chat ID (simple grep/sed since we might not have jq)
CHAT_ID=$(echo $CHAT_RES | grep -o '"chatId":"[^"]*' | cut -d'"' -f4)

if [ -z "$CHAT_ID" ]; then
    echo "   ❌ Failed to extract Chat ID"
    exit 1
else
    echo "   ✅ Chat Created. ID: $CHAT_ID"
fi

# 3. Test Fundamental Agent (Streaming)
echo -e "\n3️⃣  Testing Fundamental Agent (Stream)..."
echo "   Query: 'What is Apple revenue?'"
# We use -N for no buffer to see stream, but here we just want to capture output
FUND_RES=$(curl -s -N -X POST "$BASE_URL/api/chat/$CHAT_ID/stream" \
  -H "Content-Type: application/json" \
  -d '{"userPrompt": "What is Apple revenue?"}')

# Check for some expected content (keywords)
if [[ "$FUND_RES" == *"Apple"* ]] || [[ "$FUND_RES" == *"revenue"* ]]; then
    echo "   ✅ Fundamental Agent Responded"
    echo "   Sample Output: ${FUND_RES:0:100}..."
else
    echo "   ❌ Fundamental Agent Failed"
    echo "   Output: $FUND_RES"
fi

# 4. Test Market Agent (Streaming)
echo -e "\n4️⃣  Testing Market Agent (Stream)..."
echo "   Query: 'Analyze AAPL chart structure'"
MARKET_RES=$(curl -s -N -X POST "$BASE_URL/api/chat/$CHAT_ID/stream" \
  -H "Content-Type: application/json" \
  -d '{"userPrompt": "Analyze AAPL chart structure"}')

if [[ "$MARKET_RES" == *"structure"* ]] || [[ "$MARKET_RES" == *"liquidity"* ]]; then
    echo "   ✅ Market Agent Responded"
    echo "   Sample Output: ${MARKET_RES:0:100}..."
else
    echo "   ❌ Market Agent Failed"
    echo "   Output: $MARKET_RES"
fi

echo -e "\n✅ Platform Test Complete."

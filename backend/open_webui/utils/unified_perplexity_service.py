"""
Unified Perplexity Service for TradeBerg
- Handles text queries with Perplexity API (real-time financial data, citations, related questions)
- Handles image analysis with OpenAI Vision API
- Smart routing based on content type
- Clean, production-ready implementation
"""

import os
import json
import base64
import time
import re
import asyncio
from typing import Dict, List, Any, Optional, Tuple
import httpx
from datetime import datetime
from open_webui.utils import logger

log = logger.logger

class UnifiedPerplexityService:
    """Unified service for handling both text and image analysis"""
    
    def __init__(self):
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.perplexity_base_url = "https://api.perplexity.ai"
        self.openai_base_url = "https://api.openai.com/v1"
        
        # Financial domain whitelist for Perplexity
        self.financial_domains = [
            "bloomberg.com",
            "reuters.com",
            "finance.yahoo.com",
            "marketwatch.com",
            "coindesk.com",
            "cointelegraph.com",
            "forbes.com/crypto",
            "cnbc.com",
            "wsj.com",
            "ft.com"
        ]
    
    def _is_image_query(self, image_data: Optional[str]) -> bool:
        """Check if query contains image data"""
        return image_data is not None and len(image_data) > 0
    
    def _detect_query_intent(self, user_message: str) -> Dict[str, Any]:
        """Detect query intent and extract relevant information"""
        message_lower = user_message.lower()
        
        intents = []
        symbols = []
        
        # Intent detection
        if any(kw in message_lower for kw in ["chart", "analyze", "technical", "pattern", "trend", "screenshot"]):
            intents.append("chart_analysis")
        
        if any(kw in message_lower for kw in ["news", "sentiment", "market", "update", "latest"]):
            intents.append("market_news")
        
        if any(kw in message_lower for kw in ["price", "current", "value", "quote"]):
            intents.append("price_check")
        
        if any(kw in message_lower for kw in ["trade", "position", "entry", "exit", "strategy"]):
            intents.append("trading_strategy")
        
        # Symbol extraction
        symbol_keywords = {
            "BTC": ["btc", "bitcoin"],
            "ETH": ["eth", "ethereum"],
            "SOL": ["sol", "solana"],
            "BNB": ["bnb", "binance"],
            "XRP": ["xrp", "ripple"],
            "ADA": ["ada", "cardano"],
            "DOGE": ["doge", "dogecoin"],
            "MATIC": ["matic", "polygon"],
            "DOT": ["dot", "polkadot"],
            "LINK": ["link", "chainlink"]
        }
        
        for symbol, keywords in symbol_keywords.items():
            if any(kw in message_lower for kw in keywords):
                symbols.append(symbol)
        
        return {
            "intents": intents if intents else ["general_query"],
            "symbols": symbols,
            "original_message": user_message
        }
    
    def _enhance_user_query(self, user_message: str, intent_data: Dict[str, Any]) -> str:
        """Enhance user query for better Perplexity responses"""
        symbols = intent_data.get("symbols", [])
        intents = intent_data.get("intents", [])
        
        # Add context to make responses more structured
        enhancements = []
        
        if "price_check" in intents:
            enhancements.append("Include current price, 24h change, and volume.")
        
        if "market_news" in intents:
            enhancements.append("Provide latest news with source citations.")
        
        if "chart_analysis" in intents or "trading_strategy" in intents:
            enhancements.append("Include support/resistance levels and entry/exit recommendations.")
        
        if symbols:
            enhancements.append(f"Focus on: {', '.join(symbols)}")
        
        # Combine original query with enhancements
        if enhancements:
            enhanced = f"{user_message}\n\nPlease include: {' '.join(enhancements)} Use tables and clear formatting."
            return enhanced
        
        return user_message
    
    def _create_trading_system_prompt(self) -> str:
        """Create Perplexity-style trading system prompt with proactive analysis"""
        return """You are TRADEBERG, a professional trading AI assistant with CREATIVE INTELLIGENCE.

🎯 CORE PRINCIPLE: Be PROACTIVE, not reactive. Always provide comprehensive analysis even if not explicitly requested.

MANDATORY RESPONSE FORMAT (ALWAYS USE):

1. **📊 Price Card** (ALWAYS FIRST):
```
**[Asset Name]**
**$[Current Price]** | [Change %] [↑/↓] | 24h Vol: $[Volume]
Last updated: [Time]
```

2. **📈 Market Overview** (2-3 sentences):
Current market conditions, trend direction, and key context

3. **📋 Key Metrics Table** (ALWAYS INCLUDE):
| Metric | Value | Status | Change |
|--------|-------|--------|--------|
| 24h High | $X | - | +X% |
| 24h Low | $X | - | -X% |
| Support | $X | 🟢 Strong | - |
| Resistance | $X | 🔴 Key Level | - |
| Market Cap | $X | - | Rank #X |
| Volume | $X | 📊 High/Low | +X% |

4. **📰 Latest News** (3-5 bullets, ALWAYS):
- [Breaking news with impact] [1]
- [Market-moving events] [2]
- [Institutional activity] [3]

5. **🔍 Technical Analysis** (ALWAYS PROVIDE):
Create a comparison table:
| Indicator | Value | Signal | Interpretation |
|-----------|-------|--------|----------------|
| RSI (14) | X | Neutral/Bullish/Bearish | Explanation |
| MACD | X | Bullish/Bearish | Crossover status |
| Moving Avg | X | Above/Below | Trend confirmation |
| Volume | X | High/Low | Strength indicator |

6. **💡 Smart Insights** (ALWAYS INCLUDE):
- **Trend**: Current direction with confidence level
- **Momentum**: Strength of current move
- **Key Levels**: Critical support/resistance
- **Risk Assessment**: Current market risk level

7. **🎯 Trading Context** (BE CREATIVE):
- **Scenario Analysis**: What could happen next
- **Catalysts**: What to watch for
- **Timeframe**: Short/medium/long-term outlook

CREATIVE RULES (MANDATORY):
✅ ALWAYS show tables (even for simple questions)
✅ ALWAYS provide technical analysis (even if not asked)
✅ ALWAYS include news context (search for latest)
✅ ALWAYS give trading insights (be helpful)
✅ ALWAYS use comparison tables when relevant
✅ ALWAYS provide scenario analysis
✅ Use emojis liberally: 📊 📈 📉 💰 🔴 🟢 ⚠️ 🎯 💡 🔍
✅ Format ALL numbers: $102,193.63 (with commas)
✅ Show changes: -1.05% ↓ or +2.34% ↑
✅ Include source citations: [1], [2], [3]

EXAMPLE CREATIVE RESPONSES:

User: "what is btc rate?"
You: [Price card] + [Metrics table] + [News] + [Technical analysis table] + [Trend analysis] + [Key levels] + [What to watch]

User: "tell me about ethereum"
You: [Price card] + [ETH vs BTC comparison table] + [Network metrics table] + [News] + [Technical analysis] + [Upcoming catalysts] + [Risk/reward]

User: "market update"
You: [Top 5 coins table] + [Market sentiment table] + [Sector performance table] + [News] + [Key movers analysis] + [Market outlook]

BE PROACTIVE: If user asks a simple question, give them a comprehensive answer with:
- Price data
- Comparison tables
- Technical analysis
- News context
- Trading insights
- Risk assessment

NEVER give short answers. ALWAYS be comprehensive and creative with data presentation."""
    
    async def process_text_query(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        model: str = "sonar-pro"
    ) -> Dict[str, Any]:
        """Process text query using Perplexity API with financial data"""
        
        if not self.perplexity_api_key:
            log.error("Perplexity API key not configured")
            return {
                "success": False,
                "error": "Perplexity API key not configured"
            }
        
        try:
            log.info(f"📊 Processing text query with Perplexity: '{user_message[:50]}...'")
            
            # Detect intent and enhance prompt
            intent_data = self._detect_query_intent(user_message)
            
            # Enhance user message for better responses
            enhanced_message = self._enhance_user_query(user_message, intent_data)
            
            # Build messages array
            messages = [
                {
                    "role": "system",
                    "content": self._create_trading_system_prompt()
                }
            ]
            
            # Add conversation history if available
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Last 10 messages for context
            
            # Add enhanced user message
            messages.append({
                "role": "user",
                "content": enhanced_message
            })
            
            # Call Perplexity API
            async with httpx.AsyncClient(timeout=120.0) as client:
                start_time = time.time()
                
                response = await client.post(
                    f"{self.perplexity_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.perplexity_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": 0.2,
                        "max_tokens": 2000,
                        "return_citations": True,
                        "return_related_questions": True
                        # Note: search_domain_filter removed - causes API timeouts
                        # "search_recency_filter": "day",
                        # "search_domain_filter": self.financial_domains
                    }
                )
                
                processing_time = time.time() - start_time
                
                if response.status_code == 429:
                    log.warning(f"⚠️ Perplexity API rate limit hit - waiting 2 seconds")
                    await asyncio.sleep(2)
                    return {
                        "success": False,
                        "error": "Rate limit reached. Please try again in a moment."
                    }
                elif response.status_code != 200:
                    log.error(f"Perplexity API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"Perplexity API error: {response.status_code}"
                    }
                
                result = response.json()
                
                # Extract response data
                message_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                citations = result.get("citations", [])
                usage = result.get("usage", {})
                
                # Extract related questions (Perplexity may return them differently)
                related_questions = []
                try:
                    # Try to extract from response metadata
                    related_questions = result.get("related_questions", [])
                except:
                    pass
                
                log.info(f"✅ Perplexity response received: {len(message_content)} chars, {len(citations)} citations")
                
                return {
                    "success": True,
                    "response": message_content,
                    "citations": citations,
                    "related_questions": related_questions[:5],  # Top 5 related questions
                    "model": model,
                    "tokens_used": usage.get("total_tokens", 0),
                    "processing_time": processing_time,
                    "intent_detected": intent_data["intents"],
                    "symbols_detected": intent_data["symbols"],
                    "timestamp": datetime.now().isoformat()
                }
                
        except httpx.TimeoutException:
            log.error("Perplexity API timeout")
            return {
                "success": False,
                "error": "Request timeout - Perplexity API took too long to respond"
            }
        except Exception as e:
            log.exception(f"Error in Perplexity text query: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_image_query(
        self,
        user_message: str,
        image_data: str,
        model: str = "gpt-4o"
    ) -> Dict[str, Any]:
        """Process image query using OpenAI Vision API"""
        
        if not self.openai_api_key:
            log.error("OpenAI API key not configured")
            return {
                "success": False,
                "error": "OpenAI API key not configured"
            }
        
        try:
            log.info(f"🖼️  Processing image query with OpenAI Vision: '{user_message[:50]}...'")
            
            # Build institutional trading prompt for vision analysis
            vision_system_prompt = """You are TRADEBERG - an institutional trading terminal analyzing charts with expert precision.

Provide comprehensive chart analysis with:
1. **Liquidity Map**: Key support/resistance levels, liquidity pools, stop clusters
2. **Market Structure**: Trend analysis, consolidation zones, breakout patterns
3. **Entry/Exit Levels**: Specific price points with R:R ratios
4. **Risk Assessment**: Invalidation levels, probability scenarios
5. **Institutional Context**: Market maker behavior, absorption zones, sweep levels

Use professional execution language. Be specific with price levels. No retail TA jargon."""
            
            # Prepare image URL
            image_url = f"data:image/png;base64,{image_data}"
            
            # Call OpenAI Vision API
            async with httpx.AsyncClient(timeout=60.0) as client:
                start_time = time.time()
                
                response = await client.post(
                    f"{self.openai_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {
                                "role": "system",
                                "content": vision_system_prompt
                            },
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": user_message
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": image_url,
                                            "detail": "high"
                                        }
                                    }
                                ]
                            }
                        ],
                        "max_tokens": 2000,
                        "temperature": 0.1
                    }
                )
                
                processing_time = time.time() - start_time
                
                if response.status_code != 200:
                    log.error(f"OpenAI Vision API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"OpenAI Vision API error: {response.status_code}"
                    }
                
                result = response.json()
                
                # Extract response data
                message_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                usage = result.get("usage", {})
                
                log.info(f"✅ OpenAI Vision response received: {len(message_content)} chars")
                
                return {
                    "success": True,
                    "response": message_content,
                    "model": model,
                    "tokens_used": usage.get("total_tokens", 0),
                    "processing_time": processing_time,
                    "method": "openai_vision",
                    "timestamp": datetime.now().isoformat()
                }
                
        except httpx.TimeoutException:
            log.error("OpenAI Vision API timeout")
            return {
                "success": False,
                "error": "Request timeout - OpenAI Vision API took too long to respond"
            }
        except Exception as e:
            log.exception(f"Error in OpenAI Vision query: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_unified_query(
        self,
        user_message: str,
        image_data: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Unified query processor - intelligently routes between Vision and Perplexity
        - Images: Use OpenAI Vision for chart analysis
        - Text: Use Perplexity for financial data with citations
        """
        
        log.info(f"🎯 Unified query processing | Image: {bool(image_data)} | Message: '{user_message[:50]}...'")
        
        # Route to appropriate service
        if self._is_image_query(image_data):
            # Use OpenAI Vision for image analysis
            result = await self.process_image_query(
                user_message=user_message,
                image_data=image_data
            )
            result["service_used"] = "openai_vision"
        else:
            # Use Perplexity for text-based financial queries
            result = await self.process_text_query(
                user_message=user_message,
                conversation_history=conversation_history
            )
            result["service_used"] = "perplexity_api"
        
        # Add session tracking
        if session_id:
            result["session_id"] = session_id
        
        return result


# Singleton instance
_unified_service = None

def get_unified_service() -> UnifiedPerplexityService:
    """Get singleton instance of unified service"""
    global _unified_service
    if _unified_service is None:
        _unified_service = UnifiedPerplexityService()
    return _unified_service

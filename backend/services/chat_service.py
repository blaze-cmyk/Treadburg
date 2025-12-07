"""
Chat service for handling AI responses - GEMINI API
"""
import sys
import os
import logging
from typing import List, Dict, AsyncGenerator
import asyncio
import re

# Configure logging first
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from services.gemini_service import gemini_service
    GEMINI_AVAILABLE = True
    print("✅ Gemini service loaded successfully")
    logger.info("✅ Gemini service loaded successfully")
except ImportError as e:
    GEMINI_AVAILABLE = False
    print(f"❌ Gemini service import failed: {e}")
    logger.error(f"❌ Gemini service import failed: {e}")
except Exception as e:
    GEMINI_AVAILABLE = False
    print(f"❌ Gemini service error: {e}")
    logger.error(f"❌ Gemini service error: {e}")

from config import settings
from services.sec_client import sec_client
from services.sec_parser import extract_financials

# Ticker mapping for common company names
COMPANY_TO_TICKER = {
    'tesla': 'TSLA',
    'apple': 'AAPL',
    'microsoft': 'MSFT',
    'amazon': 'AMZN',
    'google': 'GOOGL',
    'alphabet': 'GOOGL',
    'meta': 'META',
    'facebook': 'META',
    'nvidia': 'NVDA',
    'ford': 'F',
    'gm': 'GM',
    'general motors': 'GM',
}

class ChatService:
    """Service for handling chat interactions - Uses Gemini API"""
    
    def __init__(self):
        self.gemini_available = GEMINI_AVAILABLE
        if not self.gemini_available:
            logger.error("❌ ChatService initialized without Gemini - service will not work")
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")
        if not api_key:
            logger.error("❌ GEMINI_API_KEY or API_KEY not configured")

    def _extract_tickers(self, message: str) -> List[str]:
        """
        Extract ticker symbols from user message
        """
        tickers = set()
        lower_message = message.lower()
        
        # Check for company names
        for company, ticker in COMPANY_TO_TICKER.items():
            if company in lower_message:
                tickers.add(ticker)
        
        # Check for explicit ticker symbols (e.g., TSLA, $AAPL)
        ticker_pattern = r'\b([A-Z]{1,5})\b|\$([A-Z]{1,5})\b'
        matches = re.findall(ticker_pattern, message)
        for match in matches:
            ticker = match[0] or match[1]
            if ticker and 1 <= len(ticker) <= 5:
                tickers.add(ticker)
        
        return list(tickers)
    
    def _detect_mode(self, prompt: str) -> str:
        """
        Very simple intent router to choose between general chat and full analysis.

        - Greetings / very short prompts / pure concept questions -> 'general'
        - Everything else defaults to 'analysis' (full TradeBerg behavior).
        """
        text = (prompt or "").strip().lower()
        if not text:
            return "general"

        # Short greetings
        if text in {"hi", "hey", "hello", "yo", "gm", "gn"}:
            return "general"

        # Simple educational questions
        if text.startswith("explain ") or text.startswith("what is "):
            # If no clear ticker / symbol markers, treat as general
            if "@" not in text and "$" not in text:
                return "general"

        return "analysis"
    
    async def stream_response(
        self,
        user_prompt: str,
        conversation_history: List[Dict] = None,
        attachments: List[Dict] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream AI response using Perplexity API."""
        prompt = user_prompt or ""

        # Decide mode up-front (general vs analysis)
        mode = self._detect_mode(prompt)
        
        # Extract image data from attachments if present
        image_data = None
        if attachments:
            for att in attachments:
                if isinstance(att, dict) and att.get("type") == "image" and att.get("data"):
                    data = att["data"]
                    # Data URL "data:image/png;base64,AAAA..." -> take base64 part
                    if isinstance(data, str) and "," in data:
                        data = data.split(",", 1)[1]
                    image_data = data
                    # If we have an image, force chart mode
                    mode = "chart"
                    logger.info("📸 Image detected! Switching to CHART mode.")
                    break
        
        logger.info(f"🚀 Stream Response Mode: {mode}, Attachments: {len(attachments) if attachments else 0}")
        
        # Debug output for user
        if image_data:
            yield f"[DEBUG: Image detected, size: {len(image_data)} chars]\n\n"
        else:
            yield "[DEBUG: No image detected]\n\n"

        # Extract tickers from the message
        tickers = self._extract_tickers(user_prompt)
        
        # If tickers are found, force analysis mode (unless it's already chart mode)
        if tickers and mode == "general":
            mode = "analysis"
            logger.info(f"🔄 Upgraded mode to ANALYSIS due to tickers: {tickers}")
            
        enhanced_prompt = user_prompt
        
        # Fetch SEC data for detected tickers (ONLY if not in chart mode)
        if tickers and mode != "chart":
            logger.info(f"📊 Detected tickers: {', '.join(tickers)}")
            sec_context = "\n\n--- SEC DATA ---\n"
            
            # Create tasks for all tickers to run in parallel
            tasks = [sec_client.get_company_facts(ticker) for ticker in tickers]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, ticker in enumerate(tickers):
                result = results[i]
                
                # Handle exceptions or successful results
                if isinstance(result, Exception):
                    logger.error(f"Error fetching SEC data for {ticker}: {result}")
                    continue
                    
                company_facts = result
                if company_facts:
                    try:
                        financials = extract_financials(company_facts)
                        sec_context += f"\nSEC DATA FOR {ticker}:\n"
                        sec_context += f"Company: {financials.get('name', 'Unknown')}\n"
                        
                        # Add revenue data
                        revenues = financials.get('revenues', [])[:5]
                        if revenues:
                            sec_context += f"Latest Revenue (Financials): {revenues}\n"
                        
                        # Add net income data
                        net_income = financials.get('netIncome', [])[:5]
                        if net_income:
                            sec_context += f"Latest Net Income (Financials): {net_income}\n"
                    except Exception as e:
                        logger.error(f"Error parsing SEC data for {ticker}: {e}")
            
            sec_context += "--- END SEC DATA ---\n"
            
            # Only append if we actually got data
            if "SEC DATA FOR" in sec_context:
                enhanced_prompt += sec_context
                logger.info(f"✅ Injected SEC data for tickers: {tickers}")
        
        # Check if Gemini is available
        if not self.gemini_available:
            logger.error("❌ Gemini service not available")
            fallback = "⚠️ Trading analysis service is currently unavailable. Please check backend configuration."
            for word in fallback.split():
                yield word + " "
                await asyncio.sleep(0.02)
            return
        
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")
        if not api_key:
            logger.error("❌ GEMINI_API_KEY not configured")
            fallback = "⚠️ API key not configured. Please add GEMINI_API_KEY to backend/.env file."
            for word in fallback.split():
                yield word + " "
                await asyncio.sleep(0.02)
            return
        
        # Use Gemini API for every prompt
        try:
            logger.info("🔵 Using Gemini API for trading analysis")
            
            # Stream from Gemini with enhanced prompt (includes SEC data)
            async for chunk in gemini_service.stream(
                prompt=enhanced_prompt,
                mode=mode,
                chart_image=image_data,
                metadata=None,
            ):
                yield chunk
                
            logger.info("✅ Gemini API call successful")
            return
                
        except Exception as e:
            logger.error(f"❌ Gemini service exception: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            error_msg = f"⚠️ Error connecting to trading analysis service. Please try again."
            for word in error_msg.split():
                yield word + " "
                await asyncio.sleep(0.02)
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Generate fallback response when AI service is unavailable"""
        prompt_lower = prompt.lower()
        
        if any(term in prompt_lower for term in ['price', '@', 'stock', 'crypto']):
            return f"""## Market Analysis for: {prompt}

I can help you with real-time market data and analysis. Here's what I can provide:

**Price Information:**
- Current market prices for stocks and cryptocurrencies
- Historical price data and trends
- Price alerts and notifications

**Technical Analysis:**
- Support and resistance levels
- Trend analysis and momentum indicators
- Volume analysis and market structure

**Trading Insights:**
- Entry and exit recommendations
- Risk assessment and position sizing
- Market sentiment analysis

**Note:** This is a demo response. Connect your API keys in the backend configuration to enable real-time data.

Would you like me to analyze a specific symbol? Use @SYMBOL format (e.g., @AAPL, @BTC)."""
        
        elif any(term in prompt_lower for term in ['chart', 'technical', 'indicator']):
            return f"""## Technical Analysis

I can help you with comprehensive technical analysis:

**Chart Patterns:**
- Support and resistance zones
- Trend lines and channels
- Chart patterns (head & shoulders, triangles, etc.)

**Technical Indicators:**
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Moving Averages

**Market Structure:**
- Liquidity zones
- Order flow analysis
- Institutional footprints

**Note:** This is a demo response. Enable API keys for real-time chart analysis."""
        
        else:
            return f"""## TradeBerg Trading Assistant

You asked: "{prompt}"

I'm your AI trading assistant! I can help you with:

1. **Real-time Market Data** - Stock and crypto prices
2. **Technical Analysis** - Charts, indicators, and patterns
3. **Trading Strategies** - Entry/exit points and risk management
4. **Portfolio Analysis** - Track and optimize your positions
5. **Market Insights** - News, sentiment, and trends

**Try asking:**
- "What's the price of @AAPL?"
- "Analyze @BTC technical indicators"
- "Show me trading history"
- "Explain RSI indicator"

**Note:** This is a demo response. Configure your API keys in the backend to enable full functionality."""

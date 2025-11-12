"""
OpenAI Function Calling Integration for Market Data APIs
Integrates Coinalyze and Nansen APIs with OpenAI ChatGPT for real-time analysis
"""

import json
import os
import httpx
from typing import Dict, List, Any, Optional
# OpenAI removed - using only Perplexity API
import anthropic
from open_webui.utils import logger

log = logger.logger

# API Configuration
NANSEN_API_KEY = os.getenv("NANSEN_API_KEY", "")
NANSEN_API_BASE_URL = os.getenv("NANSEN_API_BASE_URL", "https://api.nansen.ai/api/v1")
COINALYZE_API_KEY = os.getenv("COINALYZE_API_KEY", "")
COINALYZE_API_BASE_URL = os.getenv("COINALYZE_API_BASE_URL", "https://api.coinalyze.net/v1")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
# OPENAI_API_KEY removed - using only Perplexity

def format_perplexity_response(analysis: str, symbol: str = "BTCUSDT", analysis_type: str = "crypto") -> str:
    """Format Perplexity response with structured layout based on analysis type"""
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    if analysis_type == "financial":
        # Financial markets formatting
        formatted_response = f"""
📈 **TRADEBERG FINANCIAL ANALYSIS - {symbol}**
🕒 *Generated: {timestamp}*
💼 *Powered by Perplexity AI with Real-time Financial Data*

---

{analysis}

---

📊 **DATA SOURCES:**
• **SEC Filings**: 10-K, 10-Q, 8-K reports with direct URLs
• **Real-time Prices**: Live market data feeds
• **Valuation Metrics**: P/E, EV/S, EV/EBITDA, FCF margins
• **News Integration**: Latest earnings, guidance, analyst updates

💡 **AVAILABLE QUERIES:**
• "Compare AAPL vs MSFT valuation metrics"
• "Latest SEC 10-Q for NVDA with revenue breakdown"
• "SPY vs QQQ returns and risk analysis"
• "Current price of [TICKER]"
• "Deep research on [COMPANY] with peer analysis"

🔄 **NEXT STEPS:**
• Request specific SEC filing analysis
• Compare multiple stocks with valuation tables
• Get real-time price updates
• Ask for earnings calendar and guidance
"""
    
    elif analysis_type == "price":
        # Price data formatting
        formatted_response = f"""
💰 **TRADEBERG PRICE DATA - {symbol}**
🕒 *Generated: {timestamp}*
⚡ *Real-time Market Data via Perplexity AI*

---

{analysis}

---

📊 **PRICE FEATURES:**
• **Real-time Quotes**: Live bid/ask and last prices
• **Market Data**: Volume, market cap, trading activity
• **Performance**: Daily, weekly, monthly returns
• **Technical Levels**: Support, resistance, key levels

💡 **PRICE QUERIES:**
• "Current price of BTCUSDT"
• "AAPL stock price and market cap"
• "SPY vs QQQ performance comparison"
• "Real-time crypto prices"

🔄 **GET MORE DATA:**
• Request detailed technical analysis
• Compare multiple asset prices
• Get historical performance data
• Ask for volume and liquidity analysis
"""
    
    else:
        # Crypto/default formatting
        formatted_response = f"""
📊 **TRADEBERG CRYPTO ANALYSIS - {symbol}**
🕒 *Generated: {timestamp}*
🚀 *Powered by Perplexity AI with Real-time Crypto Data*

---

{analysis}

---

📋 **CRYPTO FEATURES:**
• **Real-time Data**: Live prices, volume, market cap
• **Technical Analysis**: Chart patterns, key levels
• **Market Context**: News, sentiment, on-chain data
• **DeFi Integration**: Liquidity pools, yield farming

💡 **CRYPTO QUERIES:**
• Send chart images for visual analysis
• "Current BTC price and market sentiment"
• "ETH vs BTC performance comparison"
• "DeFi yield opportunities"

🔄 **NEXT STEPS:**
• Upload chart images for detailed analysis
• Request specific crypto comparisons
• Get real-time market updates
• Ask about DeFi and yield strategies
"""
    
    return formatted_response.strip()

class MarketDataFunctions:
    """Market data functions for OpenAI function calling"""
    
    def __init__(self):
        # Using only Perplexity API - no OpenAI client needed
        pass
        
    @staticmethod
    def get_function_definitions() -> List[Dict[str, Any]]:
        """Define all available market data functions for OpenAI"""
        return [
            {
                "name": "get_coinalyze_open_interest",
                "description": "Get current open interest data for cryptocurrency symbols from Coinalyze. Shows institutional positioning and market leverage.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbols": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of cryptocurrency symbols (e.g., ['BTCUSDT', 'ETHUSDT'])"
                        }
                    },
                    "required": ["symbols"]
                }
            },
            {
                "name": "get_coinalyze_funding_rates",
                "description": "Get current funding rates for cryptocurrency perpetual futures. Indicates market sentiment and carry costs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbols": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of cryptocurrency symbols (e.g., ['BTCUSDT', 'ETHUSDT'])"
                        }
                    },
                    "required": ["symbols"]
                }
            },
            {
                "name": "get_coinalyze_liquidations",
                "description": "Get recent liquidation data for a cryptocurrency symbol. Shows forced selling/buying pressure.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Cryptocurrency symbol (e.g., 'BTCUSDT')"
                        },
                        "timeframe": {
                            "type": "string",
                            "description": "Time period for liquidation data (e.g., '1h', '4h', '1d')",
                            "default": "1h"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_nansen_defi_holdings",
                "description": "Get DeFi portfolio holdings for a specific wallet address using Nansen data. Shows institutional/whale positions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "wallet_address": {
                            "type": "string",
                            "description": "Ethereum wallet address to analyze (e.g., '0x...')"
                        }
                    },
                    "required": ["wallet_address"]
                }
            },
            {
                "name": "analyze_chart_with_perplexity",
                "description": "Analyze cryptocurrency charts using Perplexity AI with real-time market context, news, and technical analysis. Best for comprehensive trading insights.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Cryptocurrency symbol to analyze (e.g., 'BTCUSDT', 'ETHUSDT')"
                        },
                        "timeframe": {
                            "type": "string",
                            "description": "Chart timeframe (e.g., '15m', '1h', '4h', '1d')",
                            "default": "15m"
                        },
                        "analysis_type": {
                            "type": "string",
                            "description": "Type of analysis requested (e.g., 'trend analysis', 'key levels', 'entry points')",
                            "default": "comprehensive analysis"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "analyze_market_structure",
                "description": "Comprehensive market structure analysis combining multiple data sources for institutional-level insights.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Primary cryptocurrency symbol to analyze (e.g., 'BTCUSDT')"
                        },
                        "include_liquidations": {
                            "type": "boolean",
                            "description": "Include liquidation analysis",
                            "default": True
                        },
                        "timeframe": {
                            "type": "string",
                            "description": "Analysis timeframe (e.g., '1h', '4h', '1d')",
                            "default": "4h"
                        }
                    },
                    "required": ["symbol"]
                }
            }
        ]
    
    async def execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a market data function and return results"""
        try:
            if function_name == "get_coinalyze_open_interest":
                return await self._get_coinalyze_open_interest(arguments["symbols"])
            elif function_name == "get_coinalyze_funding_rates":
                return await self._get_coinalyze_funding_rates(arguments["symbols"])
            elif function_name == "get_coinalyze_liquidations":
                return await self._get_coinalyze_liquidations(
                    arguments["symbol"], 
                    arguments.get("timeframe", "1h")
                )
            elif function_name == "get_nansen_defi_holdings":
                return await self._get_nansen_defi_holdings(arguments["wallet_address"])
            elif function_name == "analyze_chart_with_perplexity":
                return await self._analyze_chart_with_perplexity(
                    arguments["symbol"],
                    arguments.get("timeframe", "15m"),
                    arguments.get("analysis_type", "comprehensive analysis")
                )
            elif function_name == "analyze_market_structure":
                return await self._analyze_market_structure(
                    arguments["symbol"],
                    arguments.get("include_liquidations", True),
                    arguments.get("timeframe", "4h")
                )
            else:
                raise ValueError(f"Unknown function: {function_name}")
                
        except Exception as e:
            log.error(f"Error executing function {function_name}: {e}")
            return {
                "error": str(e),
                "function": function_name,
                "success": False
            }
    
    async def _get_coinalyze_open_interest(self, symbols: List[str]) -> Dict[str, Any]:
        """Fetch open interest data from Coinalyze"""
        if not COINALYZE_API_KEY:
            return {"error": "Coinalyze API key not configured", "success": False}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                symbols_param = ",".join(symbols)
                response = await client.get(
                    f"{COINALYZE_API_BASE_URL}/open-interest",
                    params={"symbols": symbols_param},
                    headers={"api_key": COINALYZE_API_KEY}
                )
                
                if response.status_code != 200:
                    return {"error": f"API error: {response.status_code}", "success": False}
                
                data = response.json()
                return {
                "success": True,
                "data": data,
                "symbols": symbols,
                "data_type": "open_interest"
            }
                
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _get_coinalyze_funding_rates(self, symbols: List[str]) -> Dict[str, Any]:
        """Fetch funding rates from Coinalyze"""
        if not COINALYZE_API_KEY:
            return {"error": "Coinalyze API key not configured", "success": False}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                symbols_param = ",".join(symbols)
                response = await client.get(
                    f"{COINALYZE_API_BASE_URL}/funding-rate",
                    params={"symbols": symbols_param},
                    headers={"api_key": COINALYZE_API_KEY}
                )
                
                if response.status_code != 200:
                    return {"error": f"API error: {response.status_code}", "success": False}
                
                data = response.json()
                return {
                    "success": True,
                    "data": data,
                    "symbols": symbols,
                    "data_type": "funding_rates"
                }
                
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _get_coinalyze_liquidations(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Fetch liquidation data from Coinalyze"""
        if not COINALYZE_API_KEY:
            return {"error": "Coinalyze API key not configured", "success": False}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{COINALYZE_API_BASE_URL}/liquidation-history",
                    params={"symbol": symbol, "timeframe": timeframe},
                    headers={"api_key": COINALYZE_API_KEY}
                )
                
                if response.status_code != 200:
                    return {"error": f"API error: {response.status_code}", "success": False}
                
                data = response.json()
                return {
                    "success": True,
                    "data": data,
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "data_type": "liquidations"
                }
                
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _get_nansen_defi_holdings(self, wallet_address: str) -> Dict[str, Any]:
        """Fetch DeFi holdings from Nansen"""
        if not NANSEN_API_KEY:
            return {"error": "Nansen API key not configured", "success": False}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{NANSEN_API_BASE_URL}/portfolio/defi-holdings",
                    headers={
                        "apiKey": NANSEN_API_KEY,
                        "Content-Type": "application/json"
                    },
                    json={"wallet_address": wallet_address}
                )
                
                if response.status_code != 200:
                    return {"error": f"API error: {response.status_code}", "success": False}
                
                data = response.json()
                return {
                    "success": True,
                    "data": data,
                    "wallet_address": wallet_address,
                    "data_type": "defi_holdings"
                }
                
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _analyze_market_structure(self, symbol: str, include_liquidations: bool, timeframe: str) -> Dict[str, Any]:
        """Comprehensive market structure analysis"""
        try:
            # Fetch multiple data sources in parallel
            tasks = [
                self._get_coinalyze_open_interest([symbol]),
                self._get_coinalyze_funding_rates([symbol])
            ]
            
            if include_liquidations:
                tasks.append(self._get_coinalyze_liquidations(symbol, timeframe))
            
            import asyncio
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            analysis = {
                "success": True,
                "symbol": symbol,
                "timeframe": timeframe,
                "analysis_components": {},
                "data_type": "market_structure_analysis"
            }
            
            if len(results) >= 2:
                analysis["analysis_components"]["open_interest"] = results[0]
                analysis["analysis_components"]["funding_rates"] = results[1]
                
            if include_liquidations and len(results) >= 3:
                analysis["analysis_components"]["liquidations"] = results[2]
            
            # Add institutional insights
            analysis["institutional_insights"] = {
                "leverage_assessment": "Based on open interest and funding rate correlation",
                "liquidity_zones": "Identified from liquidation clusters",
                "sentiment_bias": "Derived from funding rate trends",
                "risk_factors": "Cross-referenced with market microstructure"
            }
            
            return analysis
            
        except Exception as e:
            return {"error": str(e), "success": False}

async def fetch_relevant_market_data(user_query: str, market_functions: MarketDataFunctions) -> Dict[str, Any]:
    """Fetch relevant market data based on user query"""
    query_lower = user_query.lower()
    market_data = {}
    
    # Detect symbols mentioned
    symbols = []
    if "btc" in query_lower or "bitcoin" in query_lower:
        symbols.append("BTCUSDT")
    if "eth" in query_lower or "ethereum" in query_lower:
        symbols.append("ETHUSDT")
    if "sol" in query_lower or "solana" in query_lower:
        symbols.append("SOLUSDT")
    
    # Default to BTC if no specific symbol mentioned
    if not symbols and any(keyword in query_lower for keyword in ["market", "analysis", "open interest", "funding", "liquidation"]):
        symbols = ["BTCUSDT"]
    
    try:
        if symbols:
            # Fetch open interest and funding rates
            if any(keyword in query_lower for keyword in ["open interest", "oi", "leverage", "position"]):
                oi_data = await market_functions._get_coinalyze_open_interest(symbols)
                if oi_data.get("success"):
                    market_data["open_interest"] = oi_data
            
            if any(keyword in query_lower for keyword in ["funding", "rate", "sentiment", "carry"]):
                funding_data = await market_functions._get_coinalyze_funding_rates(symbols)
                if funding_data.get("success"):
                    market_data["funding_rates"] = funding_data
            
            # Fetch liquidations for first symbol
            if any(keyword in query_lower for keyword in ["liquidation", "liq", "squeeze", "flush"]):
                liq_data = await market_functions._get_coinalyze_liquidations(symbols[0], "4h")
                if liq_data.get("success"):
                    market_data["liquidations"] = liq_data
        
        # Check for wallet analysis
        if "wallet" in query_lower or "defi" in query_lower or "0x" in user_query:
            # Extract wallet address if present
            import re
            wallet_match = re.search(r'0x[a-fA-F0-9]{40}', user_query)
            if wallet_match:
                wallet_address = wallet_match.group()
                defi_data = await market_functions._get_nansen_defi_holdings(wallet_address)
                if defi_data.get("success"):
                    market_data["defi_holdings"] = defi_data
    
    except Exception as e:
        log.error(f"Error fetching market data: {e}")
    
    return market_data

def format_market_data_for_analysis(market_data: Dict[str, Any]) -> str:
    """Format market data for Claude analysis"""
    formatted_data = []
    
    if "open_interest" in market_data:
        oi_data = market_data["open_interest"]
        formatted_data.append("📊 **OPEN INTEREST DATA:**")
        for item in oi_data.get("data", []):
            formatted_data.append(f"- {item.get('symbol', 'N/A')}: ${item.get('value', 0):,.0f}")
    
    if "funding_rates" in market_data:
        funding_data = market_data["funding_rates"]
        formatted_data.append("\n💰 **FUNDING RATES:**")
        for item in funding_data.get("data", []):
            rate = item.get('value', 0) * 100
            formatted_data.append(f"- {item.get('symbol', 'N/A')}: {rate:.4f}%")
    
    if "liquidations" in market_data:
        liq_data = market_data["liquidations"]
        formatted_data.append("\n⚡ **RECENT LIQUIDATIONS:**")
        total_long_liq = sum(item.get('value', 0) for item in liq_data.get("data", []) if item.get('side') == 'long')
        total_short_liq = sum(item.get('value', 0) for item in liq_data.get("data", []) if item.get('side') == 'short')
        formatted_data.append(f"- Long liquidations: ${total_long_liq:,.0f}")
        formatted_data.append(f"- Short liquidations: ${total_short_liq:,.0f}")
    
    if "defi_holdings" in market_data:
        defi_data = market_data["defi_holdings"]
        formatted_data.append("\n🏦 **DEFI HOLDINGS:**")
        holdings = defi_data.get("data", {}).get("holdings", [])
        total_value = sum(holding.get('value_usd', 0) for holding in holdings[:5])
        formatted_data.append(f"- Total portfolio value: ${total_value:,.0f}")
        for holding in holdings[:5]:
            formatted_data.append(f"- {holding.get('token_symbol', 'N/A')}: ${holding.get('value_usd', 0):,.0f}")
    
    return "\n".join(formatted_data) if formatted_data else "No market data available."

def get_enhanced_system_prompt() -> str:
    """Get enhanced system prompt for structured market analysis"""
    return """You are TRADEBERG — an elite institutional AI terminal combining macro/quant/market-microstructure analysis.

RESPONSE FORMAT (MANDATORY):
Always structure your responses with these sections:

📊 **MARKET OVERVIEW**
- Current market conditions and key metrics
- Price action and volume analysis

🔍 **INSTITUTIONAL ANALYSIS** 
- Smart money flows and positioning
- Liquidity analysis and market microstructure
- Open interest and funding rate implications

⚡ **KEY INSIGHTS**
- Critical levels and zones
- Risk factors and catalysts
- Beneficiaries vs victims of current setup

🎯 **ACTIONABLE INTELLIGENCE**
- Entry/exit levels with R:R ratios
- Stop loss and target zones
- Scenario probabilities

💡 **SUMMARY**
- One-line market thesis
- Primary risk to watch

ANALYSIS REQUIREMENTS:
- Use real-time data from Nansen and Coinalyze APIs
- Focus on liquidity, positioning, and institutional flows
- Provide specific levels and probabilities
- Identify who benefits/loses from current setup
- Use institutional language (sweeps, absorption, trapped liquidity)
- NO retail TA terms (RSI, MACD, patterns)

Always call appropriate functions to get fresh market data before analysis."""

async def process_chat_with_functions(messages: List[Dict[str, Any]], model: str = "gpt-4o") -> Dict[str, Any]:
    """Process chat messages with function calling capability"""
    
    market_functions = MarketDataFunctions()
    
    # Add enhanced system prompt if not present
    if not any(msg.get("role") == "system" for msg in messages):
        messages.insert(0, {
            "role": "system", 
            "content": get_enhanced_system_prompt()
        })
    
    # Use Claude for better formatting if available, otherwise OpenAI
    use_claude = False  # Disable Claude for now, use OpenAI
    
    try:
        if use_claude:
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            # Convert messages for Claude format
            claude_messages = []
            system_content = ""
            
            for msg in messages:
                if msg["role"] == "system":
                    system_content = msg["content"]
                else:
                    claude_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # For Claude, we'll use a different approach since it doesn't support function calling
            # We'll detect if market data is needed and fetch it first
            user_query = claude_messages[-1]["content"] if claude_messages else ""
            market_data = await fetch_relevant_market_data(user_query, market_functions)
            
            if market_data:
                # Add market data to the conversation
                data_summary = format_market_data_for_analysis(market_data)
                claude_messages.append({
                    "role": "assistant",
                    "content": f"I've retrieved the following market data:\n\n{data_summary}\n\nNow let me analyze this for you:"
                })
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                system=system_content,
                messages=claude_messages,
                temperature=0.1
            )
            
            return {
                "success": True,
                "response": response.content[0].text,
                "function_called": "market_data_analysis" if market_data else None,
                "function_result": market_data,
                "model_used": "claude-3.5-sonnet",
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                }
            }
        else:
            # Use Perplexity for ALL responses (text and function calling)
            from open_webui.utils.perplexity_analyzer import analyze_chart_with_perplexity_context_only
            
            # Get the user's message and handle both string and list content
            if messages:
                content = messages[-1]["content"]
                if isinstance(content, list):
                    # Extract text from list content
                    user_message = " ".join([
                        part.get("text", "") for part in content 
                        if isinstance(part, dict) and part.get("type") == "text"
                    ])
                else:
                    user_message = str(content)
            else:
                user_message = ""
            
            # Detect request type for better routing
            crypto_keywords = ["btc", "eth", "usdt", "bitcoin", "ethereum", "binance", "crypto", "defi", "nft"]
            stock_keywords = ["aapl", "msft", "nvda", "amd", "tsla", "googl", "meta", "spy", "qqq", "nasdaq", "s&p", "dow"]
            sec_keywords = ["10-k", "10-q", "sec", "filing", "earnings", "guidance", "revenue", "eps"]
            analysis_keywords = ["analyze", "compare", "vs", "valuation", "p/e", "ev/s", "margin", "growth"]
            price_keywords = ["price", "current price", "quote", "last close", "market cap"]
            
            is_crypto_request = any(keyword.lower() in user_message.lower() for keyword in crypto_keywords)
            is_stock_request = any(keyword.lower() in user_message.lower() for keyword in stock_keywords)
            is_sec_request = any(keyword.lower() in user_message.lower() for keyword in sec_keywords)
            is_analysis_request = any(keyword.lower() in user_message.lower() for keyword in analysis_keywords)
            is_price_request = any(keyword.lower() in user_message.lower() for keyword in price_keywords)
            
            # Route to appropriate analysis based on request type
            if is_crypto_request or (is_price_request and any(k in user_message.lower() for k in crypto_keywords)):
                # Crypto analysis with chart context
                symbol = "BTCUSDT"  # default
                if "eth" in user_message.lower():
                    symbol = "ETHUSDT"
                elif "btc" in user_message.lower() or "bitcoin" in user_message.lower():
                    symbol = "BTCUSDT"
                
                result = await analyze_chart_with_perplexity_context_only(
                    user_prompt=f"Crypto Analysis: {user_message}",
                    symbol=symbol
                )
                
                if not result.get('error'):
                    structured_response = format_perplexity_response(result['analysis'], symbol, "crypto")
                    return {
                        "success": True,
                        "response": structured_response,
                        "function_called": "perplexity_crypto_analysis",
                        "function_result": result,
                        "usage": {"total_tokens": result.get('tokens_used', 0)}
                    }
            
            elif is_stock_request or is_sec_request or is_analysis_request:
                # Financial markets analysis
                enhanced_prompt = f"""
Financial Analysis Request: {user_message}

Please provide comprehensive analysis including:
- Real-time prices and market data
- SEC filing information if relevant
- Comparative analysis with tables
- Valuation metrics (P/E, EV/S, EV/EBITDA, etc.)
- Risk factors and catalysts
- Cite all sources including SEC filing URLs
- Include specific section numbers from filings
- Provide data in table format when comparing multiple assets
"""
                
                result = await analyze_chart_with_perplexity_context_only(
                    user_prompt=enhanced_prompt,
                    symbol="SPY"  # Use SPY as general market context
                )
                
                if not result.get('error'):
                    structured_response = format_perplexity_response(result['analysis'], "FINANCIAL_MARKETS", "financial")
                    return {
                        "success": True,
                        "response": structured_response,
                        "function_called": "perplexity_financial_analysis",
                        "function_result": result,
                        "usage": {"total_tokens": result.get('tokens_used', 0)}
                    }
            
            elif is_price_request:
                # Real-time price requests
                enhanced_prompt = f"""
Real-time Price Request: {user_message}

Please provide:
- Current real-time prices
- Market cap and trading volume
- Daily/weekly/monthly performance
- Key technical levels
- Recent news affecting price
- Cite all data sources with URLs
"""
                
                result = await analyze_chart_with_perplexity_context_only(
                    user_prompt=enhanced_prompt,
                    symbol="MARKET"
                )
                
                if not result.get('error'):
                    structured_response = format_perplexity_response(result['analysis'], "REAL_TIME_PRICES", "price")
                    return {
                        "success": True,
                        "response": structured_response,
                        "function_called": "perplexity_price_data",
                        "function_result": result,
                        "usage": {"total_tokens": result.get('tokens_used', 0)}
                    }
            
            # For non-chart requests, still use Perplexity for consistency
            result = await analyze_chart_with_perplexity_context_only(
                user_prompt=user_message,
                symbol="BTCUSDT"  # default context
            )
            
            if not result.get('error'):
                return {
                    "success": True,
                    "response": result['analysis'],
                    "function_called": "perplexity_general_response",
                    "function_result": result,
                    "usage": {"total_tokens": result.get('tokens_used', 0)}
                }
            else:
                # No fallback - return error if Perplexity fails
                return {
                    "success": False,
                    "error": "Perplexity API failed and no fallback configured",
                    "response": "I'm currently unable to process your request. Please try again later."
                }
            
    except Exception as e:
        log.error(f"Error in chat processing: {e}")
        return {
            "success": False,
            "error": str(e),
            "response": "I encountered an error processing your request. Please try again.",
            "function_called": None,
            "function_result": None
        }

    async def _analyze_chart_with_perplexity(self, symbol: str, timeframe: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze chart using Perplexity AI with real-time market context"""
        try:
            from open_webui.utils.vision_api import analyze_chart_image
            from open_webui.utils.chart_capture import capture_chart_silently
            
            log.info(f"🔍 Analyzing {symbol} {timeframe} chart with Perplexity...")
            
            # Capture chart screenshot
            screenshot_base64 = await capture_chart_silently(symbol, timeframe)
            
            if not screenshot_base64:
                return {
                    "error": f"Failed to capture chart for {symbol}",
                    "success": False,
                    "symbol": symbol,
                    "timeframe": timeframe
                }
            
            # Analyze with Perplexity
            analysis_result = await analyze_chart_image(
                image_base64=screenshot_base64,
                user_prompt=f"{analysis_type} for {symbol} {timeframe}",
                symbol=symbol,
                timeframe=timeframe,
                provider="perplexity",
                use_cache=True
            )
            
            if analysis_result.get('success'):
                return {
                    "success": True,
                    "analysis": analysis_result['analysis'],
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "provider": analysis_result.get('provider', 'perplexity'),
                    "cost": analysis_result.get('cost', 0),
                    "tokens_used": analysis_result.get('tokens_used', 0),
                    "has_market_context": analysis_result.get('has_market_context', True),
                    "method": "perplexity_vision_analysis"
                }
            else:
                return {
                    "error": f"Chart analysis failed: {analysis_result.get('analysis', 'Unknown error')}",
                    "success": False,
                    "symbol": symbol,
                    "timeframe": timeframe
                }
                
        except Exception as e:
            log.error(f"Error in Perplexity chart analysis: {e}")
            return {
                "error": f"Chart analysis error: {str(e)}",
                "success": False,
                "symbol": symbol,
                "timeframe": timeframe
            }

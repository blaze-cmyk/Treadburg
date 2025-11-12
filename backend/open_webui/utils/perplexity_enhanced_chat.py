"""
Enhanced Perplexity API Integration for TradeBerg
Implements complete strategy with prompt enhancement, vision support, and structured outputs
"""

import json
import re
import base64
import time
from typing import Dict, List, Any, Optional, Tuple
import httpx
from open_webui.utils import logger

log = logger.logger

class QueryTypeDetector:
    """Detects query intent and extracts relevant information"""
    
    @staticmethod
    def detect_query_type(user_input: str) -> Dict[str, Any]:
        """Analyze user input to determine intent and extract symbols/timeframes"""
        query_lower = user_input.lower()
        
        # Query type detection
        query_types = []
        
        if any(keyword in query_lower for keyword in ["chart", "analyze", "technical", "pattern", "trend"]):
            query_types.append("chart_analysis")
        
        if any(keyword in query_lower for keyword in ["position", "portfolio", "holdings", "balance"]):
            query_types.append("position_check")
        
        if any(keyword in query_lower for keyword in ["news", "sentiment", "events", "announcement"]):
            query_types.append("market_research")
        
        if any(keyword in query_lower for keyword in ["price", "quote", "current", "value"]):
            query_types.append("price_check")
        
        # Default to comprehensive if unclear
        if not query_types:
            query_types.append("comprehensive_research")
        
        # Extract symbols
        symbols = []
        symbol_patterns = {
            "BTCUSDT": ["btc", "bitcoin"],
            "ETHUSDT": ["eth", "ethereum"],
            "SOLUSDT": ["sol", "solana"],
            "ADAUSDT": ["ada", "cardano"],
            "DOTUSDT": ["dot", "polkadot"],
            "LINKUSDT": ["link", "chainlink"],
            "AVAXUSDT": ["avax", "avalanche"],
            "MATICUSDT": ["matic", "polygon"],
        }
        
        for symbol, keywords in symbol_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                symbols.append(symbol)
        
        # Extract timeframe
        timeframe = "15m"  # default
        timeframe_patterns = {
            "1m": ["1m", "1 minute", "one minute"],
            "5m": ["5m", "5 minute", "five minute"],
            "15m": ["15m", "15 minute", "fifteen minute"],
            "1h": ["1h", "1 hour", "one hour", "hourly"],
            "4h": ["4h", "4 hour", "four hour"],
            "1d": ["1d", "daily", "day", "1 day"],
            "1w": ["1w", "weekly", "week", "1 week"]
        }
        
        for tf, patterns in timeframe_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                timeframe = tf
                break
        
        return {
            "query_types": query_types,
            "symbols": symbols if symbols else ["BTCUSDT"],
            "timeframe": timeframe,
            "original_query": user_input
        }

class PromptEnhancer:
    """Enhances user queries with professional analytical prompts"""
    
    @staticmethod
    def get_enhancement_template(query_type: str) -> str:
        """Get enhancement template for specific query type"""
        
        templates = {
            "chart_analysis": """
Analyze the provided chart/market data with institutional-level technical analysis. Provide:

1) **Technical Analysis Table** (trend, support, resistance, key levels, momentum indicators)
2) **Market Context** with real-time data and recent news citations
3) **Trade Setup** (entry/exit/stop-loss levels in table format with R:R ratios)
4) **Risk Assessment** with probability scenarios
5) **Related Questions** for follow-up analysis

Format all comparative data in markdown tables. Include risk levels and confidence scores. Cite all sources.
""",
            
            "position_check": """
Provide comprehensive portfolio analysis including:

1) **Position Overview Table** (holdings, values, allocations, P&L)
2) **Risk Metrics** (VaR, correlation analysis, concentration risk)
3) **Performance Analysis** with benchmark comparisons in table format
4) **Rebalancing Recommendations** with specific actions
5) **Market Impact Assessment** of current positions

Use markdown tables for all numerical data. Include risk assessments and confidence scores.
""",
            
            "market_research": """
Conduct comprehensive market research with:

1) **Market Sentiment Analysis** with data sources and sentiment scores
2) **News Impact Table** (events, impact level, affected assets, timeframes)
3) **Institutional Flow Analysis** (smart money movements, positioning changes)
4) **Catalyst Calendar** with upcoming events and expected impact
5) **Cross-Asset Correlations** in table format

Cite all news sources with URLs. Format data in structured tables with risk assessments.
""",
            
            "price_check": """
Provide real-time price analysis including:

1) **Current Price Table** (last, bid, ask, volume, market cap, change %)
2) **Technical Levels** (support, resistance, pivot points) in table format
3) **Volume Analysis** with institutional flow indicators
4) **Price Action Context** with recent catalysts and news
5) **Short-term Outlook** with probability scenarios

Include all data in structured markdown tables. Cite real-time data sources.
""",
            
            "comprehensive_research": """
Provide comprehensive market analysis covering:

1) **Market Overview Table** (key metrics, performance, volatility)
2) **Technical Analysis** with chart patterns and key levels
3) **Fundamental Context** with recent developments and catalysts
4) **Institutional Positioning** (flows, sentiment, positioning changes)
5) **Risk/Reward Assessment** with scenario analysis and probabilities

Format all data in markdown tables. Include citations and confidence scores for all claims.
"""
        }
        
        return templates.get(query_type, templates["comprehensive_research"])
    
    @staticmethod
    def enhance_prompt(query_info: Dict[str, Any]) -> str:
        """Transform user query into professional analytical prompt"""
        
        primary_type = query_info["query_types"][0]
        symbols = query_info["symbols"]
        timeframe = query_info["timeframe"]
        original = query_info["original_query"]
        
        # Get base template
        template = PromptEnhancer.get_enhancement_template(primary_type)
        
        # Add context-specific instructions
        context_additions = []
        
        if len(symbols) > 1:
            context_additions.append(f"Compare analysis across symbols: {', '.join(symbols)}")
        
        context_additions.append(f"Focus on {timeframe} timeframe analysis")
        context_additions.append("Use institutional language (sweeps, absorption, trapped liquidity)")
        context_additions.append("NO retail TA terms (RSI, MACD, Fibonacci, patterns)")
        context_additions.append("Include specific entry/exit levels with R:R ratios")
        
        # Construct enhanced prompt
        enhanced_prompt = f"""
MARKET ANALYSIS REQUEST for {', '.join(symbols)} on {timeframe} timeframe:

Original Query: "{original}"

{template}

ADDITIONAL REQUIREMENTS:
{chr(10).join(f'- {req}' for req in context_additions)}

RESPONSE FORMAT REQUIREMENTS:
- Use markdown tables for all comparative data
- Include risk levels (Low/Medium/High) for all recommendations
- Provide confidence scores (0-100%) for key insights
- Cite all sources with URLs where possible
- Include "Related Questions" section with 3-5 follow-up suggestions
- Structure response with clear headers and sections
"""
        
        return enhanced_prompt.strip()

class PerplexityAPIClient:
    """Enhanced Perplexity API client with vision and structured output support"""
    
    def __init__(self, api_key: str = "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"):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        
    async def analyze_with_context(
        self, 
        enhanced_prompt: str, 
        conversation_history: List[Dict[str, Any]] = None,
        image_data: Optional[str] = None,
        model: str = "sonar-pro"
    ) -> Dict[str, Any]:
        """
        Unified Perplexity API call with vision + text support
        """
        
        try:
            # Build messages array
            messages = []
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Keep last 10 messages
            
            # Prepare user message content
            user_content = []
            
            # Add text content
            user_content.append({
                "type": "text",
                "text": enhanced_prompt
            })
            
            # Add image if provided
            if image_data:
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_data}"
                    }
                })
            
            # Add user message
            messages.append({
                "role": "user",
                "content": user_content if len(user_content) > 1 else enhanced_prompt
            })
            
            # API request payload
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": 4000,
                "temperature": 0.2,
                "return_citations": True,
                "return_related_questions": True,
                "return_images": True
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code} - {response.text}"
                    }
                
                result = response.json()
                
                # Extract response components
                main_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                citations = result.get("citations", [])
                related_questions = result.get("related_questions", [])
                images = result.get("images", [])
                usage = result.get("usage", {})
                
                return {
                    "success": True,
                    "content": main_content,
                    "citations": citations,
                    "related_questions": related_questions,
                    "images": images,
                    "usage": usage,
                    "model": model
                }
                
        except Exception as e:
            log.error(f"Perplexity API error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

class ResponseFormatter:
    """Formats Perplexity responses with structured output enforcement"""
    
    @staticmethod
    def format_structured_response(
        content: str,
        citations: List[Dict[str, Any]],
        related_questions: List[str],
        images: List[Dict[str, Any]] = None
    ) -> str:
        """Format response with enforced structure and enhanced presentation"""
        
        # Clean and structure the main content
        structured_content = ResponseFormatter._structure_content(content)
        
        # Add citations section
        if citations:
            citations_section = ResponseFormatter._format_citations(citations)
            structured_content += f"\n\n{citations_section}"
        
        # Add related questions
        if related_questions:
            questions_section = ResponseFormatter._format_related_questions(related_questions)
            structured_content += f"\n\n{questions_section}"
        
        # Add images section if available
        if images:
            images_section = ResponseFormatter._format_images(images)
            structured_content += f"\n\n{images_section}"
        
        return structured_content
    
    @staticmethod
    def _structure_content(content: str) -> str:
        """Ensure content follows structured format"""
        
        # If content already has good structure, return as-is
        if "##" in content or "**" in content:
            return content
        
        # Otherwise, add basic structure
        lines = content.split('\n')
        structured_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Convert numbered lists to markdown
            if re.match(r'^\d+\.', line):
                structured_lines.append(f"### {line}")
            # Convert bullet points
            elif line.startswith('-') or line.startswith('•'):
                structured_lines.append(f"- **{line[1:].strip()}**")
            else:
                structured_lines.append(line)
        
        return '\n'.join(structured_lines)
    
    @staticmethod
    def _format_citations(citations: List[Dict[str, Any]]) -> str:
        """Format citations section"""
        
        citations_text = "## 📚 Sources & Citations\n\n"
        
        for i, citation in enumerate(citations[:10], 1):  # Limit to 10 citations
            if isinstance(citation, dict):
                title = citation.get("title", "Source")
                url = citation.get("url", "#")
            else:
                title = str(citation)
                url = "#"
            citations_text += f"{i}. **[{title}]({url})**\n"
        
        return citations_text
    
    @staticmethod
    def _format_related_questions(questions: List[str]) -> str:
        """Format related questions as clickable suggestions"""
        
        questions_text = "## 💡 Related Questions\n\n"
        questions_text += "*Click any question to explore further:*\n\n"
        
        for question in questions[:5]:  # Limit to 5 questions
            questions_text += f"- 🔍 **{question}**\n"
        
        return questions_text
    
    @staticmethod
    def _format_images(images: List[Dict[str, Any]]) -> str:
        """Format external images section"""
        
        images_text = "## 📊 Additional Charts & Visuals\n\n"
        
        for i, image in enumerate(images[:3], 1):  # Limit to 3 images
            if isinstance(image, dict):
                url = image.get("url", "")
                title = image.get("title", f"Chart {i}")
            else:
                url = str(image) if image else ""
                title = f"Chart {i}"
            if url:
                images_text += f"![{title}]({url})\n\n"
        
        return images_text

class ConversationManager:
    """Manages conversation history and context"""
    
    def __init__(self):
        self.conversations = {}  # session_id -> messages
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add message to conversation history"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
        
        # Keep only last 20 messages
        if len(self.conversations[session_id]) > 20:
            self.conversations[session_id] = self.conversations[session_id][-20:]
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for session"""
        return self.conversations.get(session_id, [])
    
    def clear_conversation(self, session_id: str):
        """Clear conversation history"""
        if session_id in self.conversations:
            del self.conversations[session_id]

# Global instances
conversation_manager = ConversationManager()
perplexity_client = PerplexityAPIClient()

async def process_enhanced_chat(
    user_message: str,
    session_id: str = "default",
    image_data: Optional[str] = None,
    model: str = "sonar-pro"
) -> Dict[str, Any]:
    """
    Main function to process chat with complete enhancement strategy
    """
    
    try:
        # Step 1: Query Type Detection
        query_info = QueryTypeDetector.detect_query_type(user_message)
        log.info(f"Detected query types: {query_info['query_types']}")
        
        # Step 2: Prompt Enhancement
        enhanced_prompt = PromptEnhancer.enhance_prompt(query_info)
        log.info(f"Enhanced prompt length: {len(enhanced_prompt)} chars")
        
        # Step 3: Get conversation history
        conversation_history = conversation_manager.get_conversation_history(session_id)
        
        # Step 4: Perplexity API call with all features
        result = await perplexity_client.analyze_with_context(
            enhanced_prompt=enhanced_prompt,
            conversation_history=conversation_history,
            image_data=image_data,
            model=model
        )
        
        # Handle both dict and string responses
        if isinstance(result, str):
            # If result is a string, treat it as the content
            formatted_response = ResponseFormatter.format_structured_response(
                content=result,
                citations=[],
                related_questions=[],
                images=[]
            )
            result = {
                "success": True,
                "content": result,
                "citations": [],
                "related_questions": [],
                "images": [],
                "usage": {},
                "model": model
            }
        elif isinstance(result, dict):
            if not result.get("success", True):  # Default to True if success key is missing
                return result
            
            # Step 5: Format structured response
            formatted_response = ResponseFormatter.format_structured_response(
                content=result.get("content", ""),
                citations=result.get("citations", []),
                related_questions=result.get("related_questions", []),
                images=result.get("images", [])
            )
        else:
            # Handle unexpected response format
            return {
                "success": False,
                "error": f"Unexpected response format: {type(result)}",
                "response": "I apologize, but I received an unexpected response format. Please try again."
            }
        
        # Step 6: Update conversation history
        conversation_manager.add_message(session_id, "user", user_message)
        conversation_manager.add_message(session_id, "assistant", formatted_response)
        
        return {
            "success": True,
            "response": formatted_response,
            "query_info": query_info,
            "citations": result.get("citations", []) if isinstance(result, dict) else [],
            "related_questions": result.get("related_questions", []) if isinstance(result, dict) else [],
            "images": result.get("images", []) if isinstance(result, dict) else [],
            "usage": result.get("usage", {}) if isinstance(result, dict) else {},
            "model": result.get("model", model) if isinstance(result, dict) else model
        }
        
    except Exception as e:
        log.error(f"Enhanced chat processing error: {e}")
        return {
            "success": False,
            "error": str(e),
            "response": "I apologize, but I'm currently unable to process your request. Please try again."
        }

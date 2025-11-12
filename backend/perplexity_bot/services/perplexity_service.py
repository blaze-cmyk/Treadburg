"""
Perplexity API service for trading analysis
"""
import httpx
import logging
import time
from typing import Dict, List, Optional, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config

logger = logging.getLogger(__name__)

class PerplexityService:
    """Service for interacting with Perplexity API"""
    
    def __init__(self):
        self.api_key = config.PERPLEXITY_API_KEY
        self.base_url = config.PERPLEXITY_BASE_URL
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def enhance_prompt(self, message: str, has_image: bool = False) -> str:
        """Enhance user prompt for better trading analysis"""
        
        # Detect query type
        message_lower = message.lower()
        
        if any(term in message_lower for term in ['chart', 'analyze', 'technical', 'price action']):
            query_type = "chart_analysis"
        elif any(term in message_lower for term in ['position', 'trade', 'entry', 'exit']):
            query_type = "position_check"
        elif any(term in message_lower for term in ['market', 'news', 'sentiment']):
            query_type = "market_research"
        else:
            query_type = "price_check"
        
        # Enhanced prompts based on query type
        prompt_templates = {
            "chart_analysis": f"""
As an institutional trading analyst, provide a comprehensive technical analysis for: {message}

Focus on:
1. **Liquidity Analysis**: Identify key liquidity pools, potential sweeps, and absorption zones
2. **Market Structure**: Current trend, support/resistance levels, and structural breaks
3. **Volume Profile**: Volume distribution, high-volume nodes, and volume-price relationships
4. **Institutional Footprints**: Signs of smart money activity, order flow imbalances
5. **Risk Assessment**: Probability scenarios with entry/exit levels and risk-reward ratios

Avoid retail indicators (RSI, MACD, Fibonacci). Use institutional terminology.
Provide specific price levels and actionable insights.
""",
            "position_check": f"""
As a risk management specialist, analyze this trading position: {message}

Provide:
1. **Position Assessment**: Current market context and position validity
2. **Risk Analysis**: Potential scenarios and probability weightings
3. **Management Strategy**: Entry refinement, stop-loss placement, profit targets
4. **Market Conditions**: How current conditions affect this position
5. **Actionable Recommendations**: Specific actions with reasoning

Include specific price levels and risk-reward calculations.
""",
            "market_research": f"""
As a market research analyst, provide comprehensive market intelligence for: {message}

Cover:
1. **Market Overview**: Current sentiment, key drivers, and market dynamics
2. **Institutional Activity**: Smart money flows, large transactions, and positioning
3. **Fundamental Factors**: Economic events, news impact, and market catalysts
4. **Technical Context**: Key levels, trend analysis, and momentum indicators
5. **Forward Outlook**: Scenarios, probabilities, and key levels to watch

Provide actionable intelligence with specific timeframes and price targets.
""",
            "price_check": f"""
As a market analyst, provide current market analysis for: {message}

Include:
1. **Current Price Action**: Real-time analysis and immediate context
2. **Key Levels**: Support, resistance, and critical price zones
3. **Market Sentiment**: Current positioning and sentiment indicators
4. **Short-term Outlook**: Immediate scenarios and probability assessments
5. **Trading Opportunities**: Potential setups with specific levels

Focus on actionable information with clear price targets and timeframes.
"""
        }
        
        enhanced_prompt = prompt_templates.get(query_type, prompt_templates["price_check"])
        
        if has_image:
            enhanced_prompt += "\n\nAnalyze the provided chart image in conjunction with this request."
        
        return enhanced_prompt
    
    async def call_perplexity_api(
        self, 
        messages: List[Dict], 
        model: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> Dict:
        """Make API call to Perplexity"""
        
        if not self.api_key:
            raise ValueError("Perplexity API key not configured")
        
        model = model or config.DEFAULT_MODEL
        temperature = temperature if temperature is not None else config.TEMPERATURE
        max_tokens = max_tokens or config.MAX_TOKENS
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "return_citations": True,
            "return_related_questions": True,
            "return_images": False
        }
        
        try:
            logger.info(f"Calling Perplexity API with model: {model}")
            start_time = time.time()
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code != 200:
                logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
                raise httpx.HTTPStatusError(
                    f"API request failed with status {response.status_code}",
                    request=response.request,
                    response=response
                )
            
            result = response.json()
            result["processing_time"] = processing_time
            
            logger.info(f"Perplexity API call successful in {processing_time:.2f}s")
            return result
            
        except httpx.TimeoutException:
            logger.error("Perplexity API timeout")
            raise
        except Exception as e:
            logger.error(f"Perplexity API call failed: {str(e)}")
            raise
    
    def parse_response(self, api_response: Dict) -> Tuple[str, List[Dict], List[str], int]:
        """Parse Perplexity API response"""
        
        try:
            # Extract main content
            choices = api_response.get("choices", [])
            if not choices:
                raise ValueError("No choices in API response")
            
            message_content = choices[0].get("message", {}).get("content", "")
            
            # Extract citations
            citations = []
            if "citations" in api_response:
                for citation in api_response["citations"]:
                    citations.append({
                        "title": citation.get("title", ""),
                        "url": citation.get("url", ""),
                        "snippet": citation.get("snippet", "")
                    })
            
            # Extract related questions
            related_questions = api_response.get("related_questions", [])
            
            # Extract token usage
            usage = api_response.get("usage", {})
            tokens_used = usage.get("total_tokens", 0)
            
            return message_content, citations, related_questions, tokens_used
            
        except Exception as e:
            logger.error(f"Error parsing Perplexity response: {str(e)}")
            raise ValueError(f"Failed to parse API response: {str(e)}")
    
    async def process_message(
        self, 
        message: str, 
        image_data: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> Dict:
        """Main orchestrator function for processing messages"""
        
        try:
            # Enhance the prompt
            enhanced_prompt = await self.enhance_prompt(message, bool(image_data))
            
            # Build messages array
            messages = []
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend([
                    {"role": msg["role"], "content": msg["content"]} 
                    for msg in conversation_history[-10:]  # Keep last 10 messages
                ])
            
            # Add current message
            current_message = {"role": "user", "content": enhanced_prompt}
            
            # Add image if provided
            if image_data:
                current_message["content"] = [
                    {"type": "text", "text": enhanced_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ]
            
            messages.append(current_message)
            
            # Call Perplexity API
            api_response = await self.call_perplexity_api(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Parse response
            content, citations, related_questions, tokens_used = self.parse_response(api_response)
            
            return {
                "success": True,
                "message": content,
                "citations": citations,
                "related_questions": related_questions,
                "model_used": model or config.DEFAULT_MODEL,
                "tokens_used": tokens_used,
                "processing_time": api_response.get("processing_time", 0),
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "success": False,
                "message": "I apologize, but I encountered an error processing your request. Please try again.",
                "citations": [],
                "related_questions": [],
                "model_used": model or config.DEFAULT_MODEL,
                "tokens_used": 0,
                "processing_time": 0,
                "error": str(e)
            }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Global service instance
perplexity_service = PerplexityService()

"""
Perplexity API integration for TradeBerg
Integrated directly into the main backend
"""
import httpx
import logging
import os
import base64
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger(__name__)

class PerplexityIntegration:
    """Integrated Perplexity service for trading analysis"""
    
    def __init__(self):
        self.api_key = os.getenv('PERPLEXITY_API_KEY', '')
        self.base_url = "https://api.perplexity.ai"
        self.model = "sonar-pro"
        
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

Provide actionable insights with specific price levels and timeframes.
""",
            "position_check": f"""
As a professional trading advisor, analyze this position/trade inquiry: {message}

Provide:
1. **Position Assessment**: Current market conditions and position viability
2. **Risk Management**: Stop-loss levels, position sizing, and risk-reward analysis
3. **Market Context**: Relevant market factors affecting this position
4. **Action Plan**: Specific recommendations with entry/exit strategies
5. **Timeline**: Expected timeframes for position development

Include specific price targets and risk parameters.
""",
            "market_research": f"""
As a market research analyst, provide comprehensive market intelligence for: {message}

Cover:
1. **Market Overview**: Current market sentiment and key drivers
2. **Fundamental Analysis**: Economic factors, news, and market-moving events
3. **Institutional Activity**: Large player movements and market positioning
4. **Correlation Analysis**: Cross-asset relationships and sector impacts
5. **Forward Outlook**: Potential scenarios and probability assessments

Provide data-driven insights with supporting evidence.
""",
            "price_check": f"""
As a cryptocurrency/trading analyst, provide detailed price analysis for: {message}

Include:
1. **Current Price Action**: Recent price movements and key levels
2. **Technical Indicators**: RSI, MACD, moving averages, and momentum signals
3. **Support/Resistance**: Key price levels and breakout/breakdown scenarios
4. **Volume Analysis**: Trading volume trends and volume-price relationships
5. **Price Targets**: Short-term and medium-term price projections

Provide specific price levels and probability assessments.
"""
        }
        
        return prompt_templates.get(query_type, f"Provide a comprehensive trading analysis for: {message}")
    
    async def send_message(self, message: str, image_data: Optional[str] = None, 
                          conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Send message to Perplexity API with enhanced prompts"""
        
        if not self.api_key:
            return {
                "success": False,
                "error": "Perplexity API key not configured",
                "message": "Please configure PERPLEXITY_API_KEY environment variable"
            }
        
        try:
            # Enhance the prompt
            enhanced_prompt = await self.enhance_prompt(message, bool(image_data))
            
            # Prepare messages for API
            messages = []
            
            # Add conversation history (last 5 messages for context)
            if conversation_history:
                for msg in conversation_history[-5:]:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            # Prepare current message
            current_message = {"role": "user", "content": enhanced_prompt}
            
            # Add image if provided
            if image_data:
                current_message["content"] = [
                    {"type": "text", "text": enhanced_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ]
            
            messages.append(current_message)
            
            # API request payload
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 4000,
                "temperature": 0.2,
                "return_citations": True,
                "return_related_questions": True,
                "return_images": False
            }
            
            # Make API request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract response content
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    # Extract citations and related questions
                    citations = data.get("citations", [])
                    related_questions = data.get("related_questions", [])
                    
                    return {
                        "success": True,
                        "message": content,
                        "citations": citations,
                        "related_questions": related_questions,
                        "model_used": self.model
                    }
                else:
                    logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API request failed with status {response.status_code}",
                        "message": "Failed to get response from Perplexity API"
                    }
                    
        except Exception as e:
            logger.error(f"Perplexity integration error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "An error occurred while processing your request"
            }
    
    async def close(self):
        """Cleanup method"""
        pass

# Global instance
perplexity_service = PerplexityIntegration()

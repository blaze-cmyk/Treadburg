"""
Perplexity API service for trading analysis
"""
import httpx
import logging
import time
from typing import Dict, List, Optional, Tuple
import sys
import os
import json

# Get the config from perplexity_bot directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Import config directly using importlib to avoid conflicts
import importlib.util
config_path = os.path.join(parent_dir, 'config.py')
spec = importlib.util.spec_from_file_location("perplexity_config", config_path)
config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_module)
config = config_module.config

logger = logging.getLogger(__name__)

class PerplexityService:
    """Service for interacting with Perplexity API"""
    
    def __init__(self):
        self.api_key = config.PERPLEXITY_API_KEY
        self.base_url = config.PERPLEXITY_BASE_URL
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def enhance_prompt(
        self,
        message: str,
        has_image: bool = False,
        context: Optional[Dict] = None,
    ) -> str:
        """
        Lightly wrap the user message with optional structured context.

        We do NOT try to be clever here anymore – the main behavior is controlled
        by the system prompt. This function just appends JSON context so the
        model can ground its analysis in real data.
        """
        parts: list[str] = [message.strip()]

        if context:
            try:
                context_json = json.dumps(context, default=str)
            except Exception:
                context_json = str(context)

            parts.append(
                "\n\nCONTEXT_JSON (for your analysis, do NOT invent missing fields):\n"
            )
            parts.append(context_json)

        if has_image:
            parts.append(
                "\n\nThe user also attached a chart image. Use it alongside the context."
            )

        return "".join(parts)
    
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
                error_text = response.text
                logger.error(f"Perplexity API error: {response.status_code} - {error_text}")
                raise httpx.HTTPStatusError(
                    f"API request failed with status {response.status_code}: {error_text}",
                    request=response.request,
                    response=response
                )
            
            # Parse JSON response
            try:
                result = response.json()
            except Exception as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response text: {response.text[:500]}")
                raise ValueError(f"Invalid JSON response from Perplexity API: {e}")
            
            result["processing_time"] = processing_time
            
            logger.info(f"Perplexity API call successful in {processing_time:.2f}s")
            logger.debug(f"Response keys: {result.keys()}")
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
            # Validate response is a dict
            if not isinstance(api_response, dict):
                logger.error(f"API response is not a dict: {type(api_response)}")
                raise ValueError(f"Invalid API response type: {type(api_response)}")
            
            # Extract main content
            choices = api_response.get("choices", [])
            if not choices:
                logger.error(f"No choices in API response: {api_response}")
                raise ValueError("No choices in API response")
            
            message_content = choices[0].get("message", {}).get("content", "")
            
            # Extract citations
            citations = []
            if "citations" in api_response:
                for citation in api_response["citations"]:
                    # Handle both string URLs and dict citations
                    if isinstance(citation, str):
                        citations.append({
                            "title": "Source",
                            "url": citation,
                            "snippet": ""
                        })
                    elif isinstance(citation, dict):
                        citations.append({
                            "title": citation.get("title", "Source"),
                            "url": citation.get("url", ""),
                            "snippet": citation.get("snippet", "")
                        })
                    else:
                        logger.warning(f"Unknown citation format: {type(citation)}")
            
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
        max_tokens: int = None,
        mode: str = "analysis",
        context: Optional[Dict] = None,
    ) -> Dict:
        """Main orchestrator function for processing messages"""
        try:
            # Enhance the user prompt with optional context
            enhanced_prompt = await self.enhance_prompt(
                message, bool(image_data), context=context
            )

            # Build messages array with system + mode prompts
            messages: List[Dict] = []

            # Core TradeBerg system prompt (full doctrine + structure)
            tradeberg_system = """
You are TradeBerg, a root-market reasoning engine.

Your role:
- Analyze stocks, crypto, and other liquid assets using fundamentals, liquidity, market microstructure, positioning, and behavior.
- Read price charts only as maps of liquidity and positioning.
- Explain where setups exist, where stop-losses likely sit, and how far a move can structurally run — without giving direct trading instructions or investment advice.
- Combine institutional research discipline (filings, data, citations) with hedge-fund style market structure analysis.
- You are not a signal bot. You are not a retail TA tool. You are an explanation engine for how the game is really played.

Knowledge boundaries and data discipline:
- Only present facts that are supported by:
  - official filings (10-K, 10-Q, 8-K, prospectuses, S-1, earnings releases)
  - company investor relations material
  - recognized financial data providers or APIs
  - on-chain or market microstructure data from reliable sources
- If data is unavailable, say it clearly. Do not guess or assume.
- Every important number must include a source indication, e.g.:
  - "Revenue was 6.9 billion in 2023 (source: FY 2023 10-K)."
  - "BTC trades at 96,234 (source: Binance API, real-time snapshot)."
- Never fabricate numbers, events, or data. If you are not sure, say you are not sure.

Core market doctrine:
- Trading is a zero-sum to negative-sum game after fees, slippage, and funding.
- Price is a function of liquidity, not patterns. It moves to where orders are:
  - stop-loss clusters
  - liquidation levels
  - option hedging bands
  - forced rebalancing and margin calls
- You interpret charts as maps of where liquidity and trapped players are, not as patterns that "predict".
- Retail behavior is fragmented; institutional behavior is concentrated.
- Indicators and patterns (RSI, MACD, moving averages, wedges, SMC, ICT, FVG, etc.) are crowd-belief systems that create liquidity, not edges.

What you actually do on each query (when doing full analysis):
- Detect catalysts and events (earnings, M&A, financing, treasury moves, regulatory shocks).
- Perform a fundamental reality check (revenue, margins, cash, dilution, debt, runway, viability).
- Map microstructure and liquidity (obvious highs/lows, round numbers, trapped flows, likely liquidation bands).
- Model behavioral positioning (what retail believes vs. how professionals can harvest their stops).
- Identify structural setup zones and invalidation in neutral language (no direct trade instructions).
- Map scenarios instead of predictions: conditional paths for how squeezes, liquidations, and catalysts can play out.

Limits and compliance:
- Do not give direct investment advice or portfolio allocations.
- Do not use certainty language ("will go up", "guaranteed").
- Do not encourage leverage, gambling, or illegal behavior.
- You may call structures "scammy" or "non-viable" based on fundamentals, but you do not defame individuals.

Default analysis output template (when in full analysis mode):
## Thesis
## Mechanics and liquidity
## Fundamental context
## Positioning and asymmetry
## Structural setup zones and invalidation
## Scenario map (non-advisory)
## Data sources

Communication style:
- Tone: sell-side quant plus buy-side macro, blunt and analytical.
- No hype, no emoji, no motivational talk.
- Avoid retail TA jargon except when describing what retail believes.
- Be compact but complete.
"""

            messages.append({"role": "system", "content": tradeberg_system})

            # Mode-specific behavior on top of the core doctrine
            mode = (mode or "analysis").lower()
            if mode == "general":
                mode_instructions = """
Mode: general conversational / educational.

- Keep answers short and clean.
- For greetings, reply in 1–2 sentences, briefly stating what you can do.
- For simple concept questions (e.g. "what is P/E?"), answer in 3–6 sentences with ONE clear numeric example.
- Do NOT use the full markdown analysis template in this mode.
- Do NOT include capability marketing paragraphs or long lists of what you "can do".
- Only mention vision or tools if the user explicitly asks how you work.
"""
            elif mode == "chart":
                mode_instructions = """
Mode: chart-focused analysis.

- Assume the user has provided a chart image or explicit chart context.
- Always produce a clean markdown report using these exact sections:
  ## Thesis
  ## Mechanics and liquidity
  ## Structural zones and invalidation
  ## Scenario map (non-advisory)
  ## Data sources
- Focus primarily on liquidity, trapped flows, structural zones, and invalidation on that chart.
- Keep each section tight and readable: short paragraphs and bullet lists, no walls of text.
- Put any citations or source-style mentions ONLY in the "## Data sources" section as a bulleted list.
"""
            else:
                mode_instructions = """
Mode: full market/asset analysis.

- Always produce a clean markdown report using these exact sections:
  ## Thesis
  ## Mechanics and liquidity
  ## Fundamental context
  ## Positioning and asymmetry
  ## Structural setup zones and invalidation
  ## Scenario map (non-advisory)
  ## Data sources
- Use short paragraphs and bullet lists; avoid long unbroken blocks of text.
- If some data is unavailable in context, explicitly say so in the relevant section instead of guessing.
- Put any citations or URLs ONLY in the "## Data sources" section as a bulleted list.
"""

            messages.append({"role": "system", "content": mode_instructions})
            
            # Add conversation history if provided (ensure alternating user/assistant)
            if conversation_history:
                # Filter and ensure proper alternation
                for msg in conversation_history[-10:]:  # Keep last 10 messages
                    # Handle both dict and object types
                    if isinstance(msg, dict):
                        role = msg.get("role")
                        content = msg.get("content")
                    elif hasattr(msg, 'role') and hasattr(msg, 'content'):
                        role = msg.role
                        content = msg.content
                    else:
                        logger.warning(f"Skipping invalid message format: {type(msg)}")
                        continue
                    
                    # Only add user and assistant messages
                    if role in ["user", "assistant"] and content:
                        # Ensure alternation: don't add consecutive messages from same role
                        if not messages or messages[-1]["role"] != role:
                            messages.append({"role": role, "content": content})
                        else:
                            logger.debug(f"Skipping consecutive {role} message to maintain alternation")
            
            # Ensure the last message in history is from assistant if we're adding a user message
            # This prevents user-user alternation
            if messages and messages[-1]["role"] == "user":
                logger.warning("Last history message is 'user', removing to prevent alternation error")
                messages.pop()
            
            # Add current message
            current_message: Dict = {"role": "user", "content": enhanced_prompt}
            
            # Add image if provided
            if image_data:
                current_message["content"] = [
                    {"type": "text", "text": enhanced_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ]
            
            messages.append(current_message)
            
            # Debug: Log the messages being sent
            logger.info(f"Sending {len(messages)} messages to Perplexity API")
            for i, msg in enumerate(messages):
                logger.debug(f"Message {i}: role={msg.get('role')}, content_length={len(str(msg.get('content', '')))}")
            
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
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
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

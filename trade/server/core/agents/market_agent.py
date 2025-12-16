import asyncio
from typing import Dict, Any
from core.intent_router import IntentObject
from services.market_data_service import market_data_service
from services.gemini_service import gemini_service
from core.output_engine import output_engine
from core.constants import TRADEBERG_GENERAL_IDENTITY


class MarketAgent:
    SYSTEM_PROMPT = TRADEBERG_GENERAL_IDENTITY

    def __init__(self):
        from services.chart_parser import chart_parser
        self.chart_parser = chart_parser
    
    async def run(self, intent: IntentObject) -> Dict[str, Any]:
        ticker = intent.tickers[0] if intent.tickers else "UNKNOWN"
        
        # 1. Parallel Data Gathering (Async)
        # We gather chart analysis and market data concurrently
        tasks = []
        
        # Task A: Chart Parsing (if chart exists)
        vision_json = {}
        if intent.has_chart and intent.meta.get('files'):
            # Assuming file bytes are passed correctly
            tasks.append(self.chart_parser.parse(intent.meta['files'][0]))
        else:
            tasks.append(asyncio.sleep(0)) # No-op
            
        # Task B: Live Market Data
        tasks.append(market_data_service.get_snapshot(ticker))
        
        # Task C: Historical Data (for chart rendering)
        tasks.append(market_data_service.get_historical_data(ticker, limit=100))
        
        # Execute all
        results = await asyncio.gather(*tasks)
        
        vision_result = results[0] if isinstance(results[0], dict) else {}
        market_data = results[1]
        historical_data = results[2]
        
        # 2. Context Building
        context = self._build_context(
            user_query=intent.text,
            vision_data=vision_result,
            market_data=market_data
        )
        
        # 3. LLM Reasoning
        # Enable search if we lack specific data or just want broader context
        # For now, let's enable it if we don't have a chart, to get news/sentiment
        # BUT: If intent.meta['disable_search'] is True (from Trade Page), force it OFF.
        disable_search = intent.meta.get('disable_search', False)
        search_flag = (not intent.has_chart) and (not disable_search)
        
        response_text, grounding_metadata = await gemini_service.generate_content(
            prompt=f"{self.SYSTEM_PROMPT}\n\n{context}",
            use_search_grounding=search_flag, # ✅ Enable Google Search for broader context
            system_instruction=self.SYSTEM_PROMPT
        )
        
        # 4. Output Formatting & Visuals
        # Embed chart if available
        if historical_data:
            import json
            chart_json = {
                "type": "line",
                "title": f"{ticker} Price Action",
                "unit": "USD",
                "series": ["Price"],
                "data": [
                    {"label": str(d["timestamp"]), "values": [d["close"]]} for d in historical_data
                ]
            }
            chart_block = f"```json-chart\n{json.dumps(chart_json)}\n```\n\n"
            response_text = chart_block + response_text
            
        formatted = output_engine.format_market_response(
            raw_text=response_text,
            market_data=market_data
        )
        
        if grounding_metadata:
            formatted['grounding_metadata'] = grounding_metadata
            
        return formatted

    def _build_context(self, user_query: str, vision_data: Dict, market_data: Dict) -> str:
        """
        Constructs the context for the LLM based on structured inputs.
        """
        # Format Vision Data
        vision_str = "NO CHART PROVIDED"
        if vision_data:
            vision_str = f"""
            CHART STRUCTURE (Vision Analysis):
            - Timeframe: {vision_data.get('timeframe', 'Unknown')}
            - Trend: {vision_data.get('trend', 'Unknown')}
            - Key Highs: {vision_data.get('high_levels', [])}
            - Key Lows: {vision_data.get('low_levels', [])}
            - Liquidity Zones: {vision_data.get('liquidity_zones', [])}
            - Patterns: {vision_data.get('patterns', [])}
            """
            
        # Format Market Data
        market_str = f"""
        LIVE MARKET DATA ({market_data.get('symbol', 'Unknown')}):
        - Price: {market_data.get('price', 'N/A')}
        - Volume: {market_data.get('volume', 'N/A')}
        - 24h Change: {market_data.get('change_24h', 'N/A')}%
        - Source: {market_data.get('source', 'Unknown')}
        """
        if 'raw_grounding_text' in market_data:
            market_str += f"\nAdditional Context: {market_data['raw_grounding_text']}"
            
        return f"""
        USER QUERY: {user_query}
        
        {vision_str}
        
        {market_str}
        """

market_agent = MarketAgent()

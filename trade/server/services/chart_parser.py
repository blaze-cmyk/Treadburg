import json
from typing import Dict, Any, Optional
from services.gemini_service import gemini_service

class ChartParser:
    """
    The 'Eyes' of the Market Agent.
    Uses Vision models to extract structured technical levels from chart images.
    """
    
    async def parse(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Analyzes a chart image and returns structured JSON.
        """
        prompt = """
        Analyze this financial chart. 
        Extract the following structure in strict JSON format:
        {
            "timeframe": "e.g. 4H, 1D, 15m",
            "trend": "bullish/bearish/neutral",
            "high_levels": [price1, price2],
            "low_levels": [price1, price2],
            "liquidity_zones": [
                {"price_range": "start-end", "type": "supply/demand"}
            ],
            "patterns": ["e.g. double top, bull flag"]
        }
        Do not include markdown formatting. Just the JSON.
        """
        
        try:
            response_text = await gemini_service.analyze_image(
                image=image_bytes,
                prompt=prompt
            )
            
            # Clean and parse JSON
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_text)
            
        except Exception as e:
            print(f"ChartParser Error: {e}")
            return {
                "error": str(e),
                "trend": "unknown",
                "high_levels": [],
                "low_levels": []
            }

chart_parser = ChartParser()

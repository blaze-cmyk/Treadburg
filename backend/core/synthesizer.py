import asyncio
from typing import Dict, Any
from core.intent_router import IntentObject
from core.agents.fundamental_agent import FundamentalAgent
from core.agents.market_agent import MarketAgent
from services.gemini_service import gemini_service

class MultiAgentSynthesizer:
    """
    Orchestrates the Fundamental and Market agents in parallel.
    Merges their outputs into a single coherent narrative.
    """
    
    SYSTEM_PROMPT = """
    You are TRADEBERG — the Unified Analyst.
    
    Your purpose:
    Combine two structured analyses:
    1. A company-focused fundamentals report
    2. A market-structure and liquidity assessment
    
    ## Goal
    Summarize key alignments or contradictions.
    - Are fundamentals and price action telling the same story?
    - Are traders positioned with or against fundamentals?
    
    ## Output Style
    ## Unified View – [Asset]
    ### Fundamentals Summary
    ### Market Structure Summary
    ### Cross-Context Take (Your Synthesis)
    """

    def __init__(self):
        self.fund_agent = FundamentalAgent()
        self.market_agent = MarketAgent()

    async def run(self, intent: IntentObject) -> Dict[str, Any]:
        # 1. Run Agents in Parallel (Async)
        # This cuts latency by ~50%
        fund_task = asyncio.create_task(self.fund_agent.run(intent))
        market_task = asyncio.create_task(self.market_agent.run(intent))
        
        fund_result, market_result = await asyncio.gather(fund_task, market_task)
        
        # 2. Synthesize Narrative
        # We feed both outputs to the LLM to write the "Cross-Context Take"
        synthesis_context = f"""
        FUNDAMENTAL ANALYSIS:
        {fund_result['markdown']}
        
        MARKET STRUCTURE ANALYSIS:
        {market_result['markdown']}
        """
        
        unified_narrative = await gemini_service.generate_content(
            prompt=f"{self.SYSTEM_PROMPT}\n\n{synthesis_context}"
        )
        
        # 3. Merge Objects
        # Combine charts, tables, and citations from both
        return {
            "markdown": unified_narrative,
            "charts": (fund_result.get("charts", []) + market_result.get("charts", [])),
            "tables": fund_result.get("tables", []),
            "overlay": market_result.get("overlay", {}),
            "citations": list(set(fund_result.get("citations", []) + market_result.get("citations", [])))
        }

synthesizer = MultiAgentSynthesizer()

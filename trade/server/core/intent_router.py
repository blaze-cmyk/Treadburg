import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

class IntentType(str, Enum):
    CHART_REASONING = "CHART_REASONING"
    FUNDAMENTAL_ANALYSIS = "FUNDAMENTAL_ANALYSIS"
    MIXED_CONTEXT = "MIXED_CONTEXT"
    GENERAL_SMALLTALK = "GENERAL_SMALLTALK"

@dataclass
class IntentObject:
    intent: IntentType
    tickers: List[str] = field(default_factory=list)
    has_chart: bool = False
    text: str = ""
    scores: Dict[str, int] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)

class IntentRouter:
    """
    Deterministic router for TradeBerg V2.
    Classifies user requests into:
    - CHART_REASONING (Visual/Technical)
    - FUNDAMENTAL_ANALYSIS (Financials/Text)
    - MIXED_CONTEXT (Both)
    - GENERAL_SMALLTALK (Conversational)
    """

    # ---------- 1.  Hard overrides ----------
    # ARR / margin / distribution / cost / deal / impact  -> Fundamental only
    FUND_FORCE_WORDS = {
        "revenue","earnings","margin","cash","balance","profit","income","expense",
        "ebit","ebitda","operating","distribution","deal","agreement","contract",
        "impact","cost","expenses","guidance","forecast","valuation","sales",
        "percentage","split","atlas","legacy","arr","annual recurring revenue",
        "acv","customers","retention","growth","subscription","gross","net",
        "fundamental","financial","product","segment","geography","business unit",
        "partnership","supply","demand","pricing","inventory","pepsi","distribution deal",
        "10-k", "10-q", "filing", "sec", "dividend", "yoy", "qoq", "fiscal", "quarter", "annual",
        "ceo", "cfo", "cto", "executive", "management", "founder", "leadership"
    }

    MARKET_FORCE_WORDS = {
        "chart","liquidity","stop","sweep","setup","pattern","technical","level",
        "support","resistance","trend","breakout","break","bearish","bullish",
        "price","volume","volatility","candlestick","rsi","macd","moving average",
        "zone","supply zone","demand zone","orderbook","positioning","crowded",
        "squeeze","short","long","flow","market structure","liquidity map",
        "wick", "candle", "entry", "stop loss", "tp", "target", "action"
    }
    
    MIXED_PHRASING = {
        "fundamentals and chart", "company outlook vs stock trend", "earnings vs price action",
        "revenue vs price", "valuation and momentum", "financials and breakout", "macro and technicals",
        "reason for stock move", "why stock up", "why stock down", "why falling", "why ripping", "why pumped",
        "what drives it", "trade idea reasoning", "analysis full picture", "complete overview",
        "technical and fundamental", "chart reaction to earnings", "after earnings move"
    }

    def __init__(self):
        # Regex for potential tickers (1-5 uppercase letters)
        self.ticker_pattern = re.compile(r'\b[A-Z]{1,5}\b')

    def route(self, text: str, has_chart: bool = False, files: List[Any] = None) -> IntentObject:
        """
        Main routing method.
        """
        normalized_text = text.lower()
        
        # 1. Extract Entities
        tickers = self._extract_tickers(text)
        
        # Boost chart intent if image is present
        if has_chart or (files and len(files) > 0):
            has_chart = True

        # 2. Calculate Scores
        fund_score = self._calculate_score(normalized_text, self.FUND_FORCE_WORDS)
        market_score = self._calculate_score(normalized_text, self.MARKET_FORCE_WORDS)
        mixed_score = self._calculate_score(normalized_text, self.MIXED_PHRASING)

        # 3. Decision Matrix
        intent = self._classify(normalized_text, has_chart, chart_score=market_score, fund_score=fund_score, mixed_score=mixed_score, has_ticker=len(tickers) > 0)

        return IntentObject(
            intent=intent,
            tickers=tickers,
            has_chart=has_chart,
            text=text,
            scores={"chart": market_score, "fund": fund_score, "mixed": mixed_score}
        )

    def _extract_tickers(self, text: str) -> List[str]:
        """
        Extracts ticker symbols from text using TickerResolver.
        """
        from services.ticker_resolver import TickerResolver
        
        valid_tickers = []
        
        # 1. Try to resolve company names first (e.g. "Datadog" -> "DDOG")
        resolved_ticker = TickerResolver.resolve_symbol(text)
        if resolved_ticker:
            valid_tickers.append(resolved_ticker)
            
        # 2. Extract potential tickers via regex
        matches = self.ticker_pattern.findall(text)
        
        # 3. Validate regex matches
        for match in matches:
            if TickerResolver.validate_ticker(match):
                valid_tickers.append(match)
                
        return list(set(valid_tickers)) # Deduplicate

    def _calculate_score(self, text: str, keywords: set) -> int:
        """
        Counts occurrences of keywords in text.
        """
        score = 0
        for word in keywords:
            if word in text:
                score += 1
        return score

    def _classify(self, text: str, has_chart: bool, chart_score: int, fund_score: int, mixed_score: int, has_ticker: bool) -> IntentType:
        """
        Applies the robust decision matrix rules.
        """
        
        # 1. Hard overrides based on explicit mixed phrasing
        if mixed_score > 0:
            return IntentType.MIXED_CONTEXT
            
        # 2. Hard overrides based on image presence (unless strong fundamental keywords exist)
        # If user uploads a chart but asks about "gross margin", we want mixed or fundamental, not just chart.
        if has_chart:
            if fund_score > 0:
                return IntentType.MIXED_CONTEXT
            return IntentType.CHART_REASONING

        # 3. Strong Fundamental Signal
        # If any strong fundamental keyword is present, prefer fundamental
        # This fixes "impact", "deal", "margin" queries
        if fund_score > 0 and chart_score == 0:
            return IntentType.FUNDAMENTAL_ANALYSIS

        # 4. Strong Market Signal
        if chart_score > 0 and fund_score == 0:
            return IntentType.CHART_REASONING

        # 5. Mixed Signal (Keywords from both)
        if fund_score > 0 and chart_score > 0:
            return IntentType.MIXED_CONTEXT
            
        # 6. Ticker Only Fallback
        # If we found a ticker but no keywords, default to Chart/Price Analysis (Market Agent)
        if has_ticker:
            return IntentType.CHART_REASONING

        # 7. Default / Smalltalk
        return IntentType.GENERAL_SMALLTALK

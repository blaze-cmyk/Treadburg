"""
Intent Detection for Chart Analysis
Detects if user prompt requires chart analysis and screenshot capture
"""

import re
from typing import Dict, Any, List


def requires_chart_analysis(user_message: str) -> bool:
    """
    Detects if user prompt requires chart analysis.
    This determines if we need to take a screenshot silently.
    
    Args:
        user_message: The user's message text
        
    Returns:
        True if chart analysis is needed, False otherwise
    """
    if not user_message:
        return False
        
    message = user_message.lower()
    
    # Keywords that indicate chart analysis is needed
    # These keywords trigger automatic screenshot capture
    analysis_keywords = [
        'analyze', 'analysis', 'trend', 'trending',
        'support', 'resistance', 'breakout', 'breakdown',
        'buy', 'sell', 'entry', 'exit', 'signal',
        'pattern', 'chart', 'technical', 'indicator',
        'rsi', 'macd', 'moving average', 'volume',
        'bullish', 'bearish', 'reversal', 'continuation',
        'fibonacci', 'pivot', 'target', 'stop loss',
        'risk', 'reward', 'setup', 'trade', 'ta',
        'liquidity', 'sweep', 'absorption', 'imbalance',
        'trapped', 'unwind', 'compression', 'deleveraging',
        'level', 'levels', 'key level', 'key levels',
        'setup', 'play', 'trade idea', 'trade setup'
    ]
    
    # Check if any keyword exists in message
    needs_analysis = any(keyword in message for keyword in analysis_keywords)
    
    # Also check for question patterns about price action
    question_patterns = [
        'what do you see',
        'what\'s happening',
        'should i',
        'can i',
        'is it good',
        'looks like',
        'think about',
        'what about',
        'how is',
        'tell me about'
    ]
    
    has_question_pattern = any(pattern in message for pattern in question_patterns)
    
    # Check for symbol mentions (e.g., $BTC, BTCUSDT)
    symbol_pattern = r'\$?[A-Z]{2,10}(?:USDT|USD|BTC|ETH)?'
    has_symbol = bool(re.search(symbol_pattern, user_message, re.IGNORECASE))
    
    # Check for timeframe mentions
    timeframe_pattern = r'\b(1m|5m|15m|30m|1h|4h|1d|1w|1M)\b'
    has_timeframe = bool(re.search(timeframe_pattern, message))
    
    return needs_analysis or has_question_pattern or (has_symbol and has_timeframe)


def extract_symbol_from_message(user_message: str, default: str = "BTCUSDT") -> str:
    """
    Extracts trading symbol from user message.
    
    Args:
        user_message: The user's message text
        default: Default symbol if none found
        
    Returns:
        Extracted symbol (e.g., "BTCUSDT")
    """
    if not user_message:
        return default
    
    # Pattern for $SYMBOL or SYMBOLUSDT format
    patterns = [
        r'\$([A-Z]{2,10})(?:USDT|USD|BTC|ETH)?',
        r'\b([A-Z]{2,10})(?:USDT|USD|BTC|ETH)\b',
        r'\b([A-Z]{2,10})\b(?=\s*(?:chart|analysis|trend|setup))',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, user_message, re.IGNORECASE)
        if match:
            symbol = match.group(1).upper()
            # Normalize to USDT if not specified
            if not any(symbol.endswith(suffix) for suffix in ['USDT', 'USD', 'BTC', 'ETH']):
                symbol = f"{symbol}USDT"
            return symbol
    
    return default


def extract_timeframe_from_message(user_message: str, default: str = "15m") -> str:
    """
    Extracts timeframe from user message.
    
    Args:
        user_message: The user's message text
        default: Default timeframe if none found
        
    Returns:
        Extracted timeframe (e.g., "15m", "1h", "1d")
    """
    if not user_message:
        return default
    
    message = user_message.lower()
    
    # Direct patterns
    direct_pattern = r'\b(1m|5m|15m|30m|1h|4h|1d|1w|1M)\b'
    match = re.search(direct_pattern, message)
    if match:
        return match.group(1)
    
    # Minutes patterns
    minutes_match = re.search(r'\b(\d{1,2})\s*(?:m|min|mins|minute|minutes)\b', message)
    if minutes_match:
        return f"{minutes_match.group(1)}m"
    
    # Hours patterns
    hours_match = re.search(r'\b(\d{1,2})\s*(?:h|hr|hrs|hour|hours)\b', message)
    if hours_match:
        return f"{hours_match.group(1)}h"
    
    # Days patterns
    days_match = re.search(r'\b(\d{1,2})\s*(?:d|day|days)\b', message)
    if days_match:
        return f"{days_match.group(1)}d"
    
    return default


def should_remove_auto_attached_image(messages: List[Dict[str, Any]]) -> bool:
    """
    Determines if we should remove an auto-attached image from messages.
    This is used when we're doing silent backend screenshot capture.
    
    Args:
        messages: List of message dicts
        
    Returns:
        True if we should remove auto-attached images
    """
    if not messages:
        return False
    
    # Get last user message
    last_user_msg = None
    for msg in reversed(messages):
        if msg.get("role") == "user":
            last_user_msg = msg
            break
    
    if not last_user_msg:
        return False
    
    # Check if message requires chart analysis
    content = last_user_msg.get("content", "")
    if isinstance(content, str):
        return requires_chart_analysis(content)
    elif isinstance(content, list):
        # Check text parts
        text_parts = [part.get("text", "") for part in content if part.get("type") == "text"]
        combined_text = " ".join(text_parts)
        return requires_chart_analysis(combined_text)
    
    return False


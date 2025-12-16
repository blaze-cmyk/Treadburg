"""
Response formatter for beautiful, structured AI outputs
"""
import re
from typing import Dict, List

class ResponseFormatter:
    """Format AI responses with tables, charts, and structured sections"""
    
    @staticmethod
    def format_trading_analysis(content: str, citations: List[Dict] = None, related_questions: List[str] = None) -> str:
        """
        Format trading analysis with beautiful, human-readable structure
        """
        # Clean up the content first
        content = ResponseFormatter._clean_content(content)
        
        # Parse into structured sections
        sections = ResponseFormatter._parse_into_sections(content)
        
        # Build formatted output
        formatted = ""
        
        # Add title based on content
        if any(keyword in content.lower() for keyword in ['btc', 'bitcoin', 'eth', 'ethereum']):
            symbol = ResponseFormatter._extract_symbol(content)
            formatted += f"# 📊 {symbol} Analysis\n\n"
        else:
            formatted += "# 📊 Market Analysis\n\n"
        
        # Add executive summary if content is long
        if len(content) > 500:
            summary = ResponseFormatter._create_summary(content)
            formatted += f"## Executive Summary\n\n{summary}\n\n---\n\n"
        
        # Add price information prominently
        price_info = ResponseFormatter._extract_price_info(content)
        if price_info:
            formatted += price_info + "\n\n"
        
        # Add main sections
        for section_title, section_content in sections.items():
            if section_content:
                formatted += f"## {section_title}\n\n{section_content}\n\n"
        
        # Add key levels table
        levels_table = ResponseFormatter._create_levels_table(content)
        if levels_table:
            formatted += levels_table + "\n\n"
        
        # Add market sentiment visualization
        sentiment = ResponseFormatter._create_sentiment_section(content)
        if sentiment:
            formatted += sentiment + "\n\n"
        
        # Add citations in clean format
        if citations and len(citations) > 0:
            formatted += "## 📚 Data Sources\n\n"
            for i, citation in enumerate(citations[:5], 1):
                title = citation.get('title', 'Source')
                url = citation.get('url', '#')
                formatted += f"{i}. [{title}]({url})\n"
            formatted += "\n"
        
        # Add related questions
        if related_questions and len(related_questions) > 0:
            formatted += "## 💡 Related Questions\n\n"
            for question in related_questions[:3]:
                formatted += f"• {question}\n"
            formatted += "\n"
        
        # Add footer
        formatted += "---\n\n"
        formatted += "*Analysis powered by TradeBerg • Real-time market data*\n"
        
        return formatted
    
    @staticmethod
    def _clean_content(content: str) -> str:
        """Clean up raw content"""
        # Remove excessive newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        # Remove leading/trailing whitespace
        content = content.strip()
        return content
    
    @staticmethod
    def _extract_symbol(content: str) -> str:
        """Extract trading symbol from content"""
        symbols = {
            'btc': 'Bitcoin (BTC)',
            'bitcoin': 'Bitcoin (BTC)',
            'eth': 'Ethereum (ETH)',
            'ethereum': 'Ethereum (ETH)',
            'sol': 'Solana (SOL)',
            'bnb': 'Binance Coin (BNB)',
        }
        
        content_lower = content.lower()
        for key, value in symbols.items():
            if key in content_lower:
                return value
        
        return "Market"
    
    @staticmethod
    def _create_summary(content: str) -> str:
        """Create a concise executive summary"""
        # Take first 2-3 sentences
        sentences = re.split(r'[.!?]+', content)
        summary_sentences = [s.strip() for s in sentences[:3] if s.strip()]
        return ' '.join(summary_sentences) + '.'
    
    @staticmethod
    def _extract_price_info(content: str) -> str:
        """Extract and format price information"""
        # Look for price patterns
        price_pattern = r'\$[\d,]+(?:\.\d{2})?'
        prices = re.findall(price_pattern, content)
        
        if not prices:
            return ""
        
        # Find context around first price
        first_price = prices[0]
        price_index = content.find(first_price)
        context_start = max(0, price_index - 100)
        context_end = min(len(content), price_index + 200)
        context = content[context_start:context_end]
        
        # Check for change indicators
        change_pattern = r'([+-]?\d+\.?\d*%)'
        changes = re.findall(change_pattern, context)
        
        output = f"## 💰 Current Price\n\n**{first_price}**"
        
        if changes:
            change = changes[0]
            if change.startswith('+') or not change.startswith('-'):
                output += f" 🟢 {change}"
            else:
                output += f" 🔴 {change}"
        
        return output
    
    @staticmethod
    def _parse_into_sections(content: str) -> Dict[str, str]:
        """Parse content into logical sections"""
        sections = {
            "📈 Market Overview": "",
            "🎯 Key Insights": "",
            "⚖️ Risk Analysis": "",
            "🔮 Outlook": ""
        }
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Distribute paragraphs to sections based on keywords
        overview_keywords = ['trading', 'price', 'market', 'currently', 'recent']
        insight_keywords = ['key', 'important', 'notable', 'significant', 'level']
        risk_keywords = ['risk', 'caution', 'warning', 'volatile', 'uncertain']
        outlook_keywords = ['outlook', 'expect', 'forecast', 'future', 'ahead', 'likely']
        
        for para in paragraphs:
            para_lower = para.lower()
            
            if any(kw in para_lower for kw in outlook_keywords):
                sections["🔮 Outlook"] += para + "\n\n"
            elif any(kw in para_lower for kw in risk_keywords):
                sections["⚖️ Risk Analysis"] += para + "\n\n"
            elif any(kw in para_lower for kw in insight_keywords):
                sections["🎯 Key Insights"] += para + "\n\n"
            elif any(kw in para_lower for kw in overview_keywords):
                sections["📈 Market Overview"] += para + "\n\n"
            else:
                # Default to overview
                if not sections["📈 Market Overview"]:
                    sections["📈 Market Overview"] += para + "\n\n"
                else:
                    sections["🎯 Key Insights"] += para + "\n\n"
        
        # Clean up empty sections
        return {k: v.strip() for k, v in sections.items() if v.strip()}
    
    @staticmethod
    def _create_sections(content: str) -> str:
        """Break content into structured sections"""
        sections = {
            "Market Overview": ["overview", "trading", "market", "currently"],
            "Technical Analysis": ["support", "resistance", "level", "technical", "indicator"],
            "Key Insights": ["key", "important", "notable", "significant"],
            "Outlook": ["outlook", "forecast", "expect", "scenario", "probability"]
        }
        
        result = ""
        
        # Split content into sentences
        sentences = re.split(r'[.!?]+', content)
        
        for section_name, keywords in sections.items():
            section_content = []
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in keywords):
                    section_content.append(sentence.strip())
            
            if section_content:
                result += f"## 📈 {section_name}\n\n"
                for sentence in section_content[:3]:  # Limit to 3 sentences per section
                    if sentence:
                        result += f"- {sentence}.\n"
                result += "\n"
        
        return result
    
    @staticmethod
    def _create_levels_table(content: str) -> str:
        """Create a table for support and resistance levels"""
        # Extract price levels
        prices = re.findall(r'\$[\d,]+(?:\.\d{2})?', content)
        if len(prices) < 2:
            return ""
        
        table = "\n## 🎯 Key Price Levels\n\n"
        table += "| Level Type | Price | Status |\n"
        table += "|------------|-------|--------|\n"
        
        # Identify support and resistance
        support_keywords = ['support', 'low', 'floor', 'bottom']
        resistance_keywords = ['resistance', 'high', 'ceiling', 'top']
        
        content_lower = content.lower()
        
        for price in prices[:4]:  # Show top 4 levels
            level_type = "Key Level"
            status = "Active"
            
            # Find context around this price
            price_index = content.find(price)
            if price_index != -1:
                context = content[max(0, price_index-50):price_index+50].lower()
                if any(kw in context for kw in support_keywords):
                    level_type = "🟢 Support"
                elif any(kw in context for kw in resistance_keywords):
                    level_type = "🔴 Resistance"
            
            table += f"| {level_type} | **{price}** | {status} |\n"
        
        table += "\n"
        return table
    
    @staticmethod
    def _create_sentiment_section(content: str) -> str:
        """Create a visual sentiment indicator"""
        content_lower = content.lower()
        
        # Count sentiment indicators
        bullish_words = ['bullish', 'rally', 'uptrend', 'positive', 'strong', 'momentum']
        bearish_words = ['bearish', 'decline', 'downtrend', 'negative', 'weak', 'correction']
        neutral_words = ['consolidat', 'sideways', 'neutral', 'cautious', 'uncertain']
        
        bullish_count = sum(1 for word in bullish_words if word in content_lower)
        bearish_count = sum(1 for word in bearish_words if word in content_lower)
        neutral_count = sum(1 for word in neutral_words if word in content_lower)
        
        total = bullish_count + bearish_count + neutral_count
        if total == 0:
            return ""
        
        sentiment = "\n## 📊 Market Sentiment\n\n"
        sentiment += "```\n"
        
        # Create visual bar
        if bullish_count > bearish_count and bullish_count > neutral_count:
            sentiment += "🟢 BULLISH   " + "█" * min(bullish_count * 3, 20) + "\n"
            sentiment += "🟡 NEUTRAL   " + "░" * min(neutral_count * 3, 10) + "\n"
            sentiment += "🔴 BEARISH   " + "░" * min(bearish_count * 3, 10) + "\n"
        elif bearish_count > bullish_count and bearish_count > neutral_count:
            sentiment += "🟢 BULLISH   " + "░" * min(bullish_count * 3, 10) + "\n"
            sentiment += "🟡 NEUTRAL   " + "░" * min(neutral_count * 3, 10) + "\n"
            sentiment += "🔴 BEARISH   " + "█" * min(bearish_count * 3, 20) + "\n"
        else:
            sentiment += "🟢 BULLISH   " + "░" * min(bullish_count * 3, 10) + "\n"
            sentiment += "🟡 NEUTRAL   " + "█" * min(neutral_count * 3, 20) + "\n"
            sentiment += "🔴 BEARISH   " + "░" * min(bearish_count * 3, 10) + "\n"
        
        sentiment += "```\n\n"
        return sentiment
    
    @staticmethod
    def format_quick_response(content: str) -> str:
        """Format quick responses with minimal structure"""
        formatted = f"💬 **Quick Answer**\n\n{content}\n"
        return formatted

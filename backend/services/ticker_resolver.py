
import re

class TickerResolver:
    """
    Resolves company names to tickers and validates symbols.
    """
    
    # Simple static map for common companies
    # In a real production system, this would be a database or external API lookup
    NAME_TO_TICKER = {
        "datadog": "DDOG",
        "microsoft": "MSFT",
        "apple": "AAPL",
        "google": "GOOGL",
        "alphabet": "GOOGL",
        "amazon": "AMZN",
        "meta": "META",
        "facebook": "META",
        "tesla": "TSLA",
        "nvidia": "NVDA",
        "netflix": "NFLX",
        "salesforce": "CRM",
        "adobe": "ADBE",
        "oracle": "ORCL",
        "amd": "AMD",
        "intel": "INTC",
        "cava": "CAVA",
        "elf": "ELF",
        "celh": "CELH",
        "duolingo": "DUOL",
        "bill.com": "BILL",
        "sofi": "SOFI",
        "palantir": "PLTR",
        "snowflake": "SNOW",
        "uber": "UBER",
        "airbnb": "ABNB",
        "coinbase": "COIN",
        "shopify": "SHOP",
        "spotify": "SPOT",
        "square": "SQ",
        "block": "SQ",
        "paypal": "PYPL",
        "crowdstrike": "CRWD",
        "zscaler": "ZS",
        "cloudflare": "NET",
        "mongodb": "MDB",
        "servicenow": "NOW",
        "workday": "WDAY",
        "atlassian": "TEAM",
        "hubspot": "HUBS",
        "twilio": "TWLO",
        "okta": "OKTA",
        "zoom": "ZM",
        "docu": "DOCU",
        "roku": "ROKU",
        "pinterest": "PINS",
        "snap": "SNAP",
        "twitter": "TWTR", # Delisted but good for legacy checks
        "x": "TWTR",
        "reddit": "RDDT",
        "robinhood": "HOOD",
        "affirm": "AFRM",
        "upstart": "UPST",
        "opendoor": "OPEN",
        "doorDash": "DASH",
        "instacart": "CART",
        "arm": "ARM",
        "klaviyo": "KVYO",
        "birkenstock": "BIRK",
    }

    @staticmethod
    def resolve_symbol(text: str) -> str | None:
        """
        Attempts to resolve a company name or symbol from text to a valid ticker.
        """
        text_lower = text.lower()
        
        # 1. Direct lookup in name map
        for name, ticker in TickerResolver.NAME_TO_TICKER.items():
            # Check for exact word match to avoid partial matches (e.g. "target" matching "target corp")
            # Using regex word boundaries
            if re.search(r'\b' + re.escape(name) + r'\b', text_lower):
                return ticker
                
        # 2. Check if the text itself looks like a ticker (3-5 uppercase letters)
        # This is a fallback and should be validated against a real list if possible
        # For now, we rely on the IntentRouter's extraction logic, but this helper
        # can be used to validate specific tokens.
        
        return None

    @staticmethod
    def validate_ticker(ticker: str) -> bool:
        """
        Validates if a string looks like a valid ticker and isn't a common false positive.
        """
        if not ticker:
            return False
            
        ticker = ticker.upper()
        
        # Common false positives that look like tickers
        FALSE_POSITIVES = {
            "ARR", "CEO", "CFO", "CTO", "COO", "FYI", "TBD", "N/A", "USA", "UK", "EU", 
            "GDP", "CPI", "PPI", "FOMC", "SEC", "IRS", "FBI", "CIA", "NASA", "NATO", 
            "UN", "WHO", "CDC", "FDA", "EPA", "FCC", "FTC", "DOJ", "DOD", "DOE", "DOT",
            "ROI", "ROE", "ROA", "EBITDA", "EPS", "PE", "PEG", "PS", "PB", "NAV", "AUM",
            "CAGR", "YOY", "QOQ", "MOM", "YTD", "LTM", "TTM", "FY", "Q1", "Q2", "Q3", "Q4",
            "AI", "ML", "LLM", "RAG", "API", "SDK", "GUI", "UI", "UX", "CSS", "HTML", "JS",
            "SQL", "AWS", "GCP", "AZURE", "SAAS", "PAAS", "IAAS", "B2B", "B2C", "D2C",
            "IPO", "SPAC", "ETF", "REIT", "ADR", "OTC", "NYSE", "NASDAQ", "AMEX", "CBOE"
        }
        
        if ticker in FALSE_POSITIVES:
            return False
            
        return True
